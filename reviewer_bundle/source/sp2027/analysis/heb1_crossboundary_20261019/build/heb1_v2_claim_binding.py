#!/usr/bin/env python3
"""V2 claim-binding validator: structure + hashes + cross-artifact identity joins.

Blind public-input validation. Decision rule (frozen):
  EMIT level 6 iff every join J1-J9 holds, every claim-consistency check holds,
  and the evidence-tier chain reaches level 6; otherwise
  REJECT claim-overreach supported=<k> (with violations list when non-empty).
No cryptographic recomputation; no private inputs; no labels.

Frozen spec: ../HEB1_EXPERIMENT_PROTOCOL_20261019.md
Usage: python3 heb1_v2_claim_binding.py <public_dir>
Prints one line of JSON to stdout.
"""
import hashlib
import json
import sys
from pathlib import Path

VER = "heb1-reference-v1"
TOP_REQUIRED = ["schema", "attempt_id", "task", "condition", "target",
                "agent_artifact", "execution", "verification", "claims", "evidence"]
REQUIRED_KINDS = ["agent_artifact", "execution_trace", "target_effect",
                  "reference_acceptance", "boundary", "verifier_metadata"]
CLAIM_ENUMS = {
    "artifact_authorship": {"PROVEN", "NOT_ESTABLISHED"},
    "execution_identity": {"PROVEN", "NOT_ESTABLISHED"},
    "target_effect": {"OBSERVED", "NOT_OBSERVED", "NOT_ESTABLISHED"},
    "reference_oracle_acceptance": {"ACCEPTED", "REJECTED", "NOT_ESTABLISHED"},
    "boundary_enforcement": {"PROVEN", "NOT_ESTABLISHED"},
    "attribution": {"PROVEN", "NOT_ESTABLISHED"},
}


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def g(d, *keys):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def eq_all(*vals) -> bool:
    return all(v is not None for v in vals) and len(set(vals)) == 1


def level_chain(ev, cmp_sha, cert, joins_failed) -> int:
    trace, effect = ev.get("execution_trace"), ev.get("target_effect")
    ref, boundary = ev.get("reference_acceptance"), ev.get("boundary")
    agent = ev.get("agent_artifact")
    sess = g(cert, "execution", "session_id")
    l1 = agent is not None and g(agent, "artifact_sha256") == cmp_sha
    l2 = (l1 and trace is not None
          and g(trace, "candidate_sha256") == cmp_sha
          and g(trace, "session_id") == sess)
    l3 = l2 and effect is not None and g(effect, "status") == "OBSERVED"
    l4 = (l3 and ref is not None and g(ref, "accepted") is True
          and g(ref, "artifact_sha256") == cmp_sha)
    l5 = l4 and boundary is not None and g(boundary, "enforced") is True
    l6 = l5 and not joins_failed
    lvl = 0
    for i, ok in enumerate([l1, l2, l3, l4, l5, l6], 1):
        if ok:
            lvl = i
        else:
            break
    return lvl


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"system": "V2", "decision": "REJECT", "level": 0,
                          "reason": "usage: heb1_v2_claim_binding.py <public_dir>"}))
        return 2
    pub = Path(sys.argv[1])
    out = {"system": "V2", "decision": "REJECT", "level": 0, "reason": ""}

    def reject(reason: str) -> int:
        out["reason"] = reason
        print(json.dumps(out, sort_keys=True))
        return 0

    try:
        cert = json.loads((pub / "certificate.json").read_text())
        request = json.loads((pub / "request.json").read_text())
    except Exception as e:
        return reject("malformed-input:" + type(e).__name__)

    for k in TOP_REQUIRED:
        if k not in cert:
            return reject("missing-key:" + k)
    claims = cert.get("claims", {})
    for field, allowed in CLAIM_ENUMS.items():
        if claims.get(field) not in allowed:
            return reject("bad-claim-enum:" + field)
    if not isinstance(cert.get("evidence"), list) or not cert["evidence"]:
        return reject("bad-evidence-list")
    present = {}
    for item in cert["evidence"]:
        fp = pub / item.get("path", "")
        if not fp.is_file():
            return reject("missing-evidence-file:" + str(item.get("kind")))
        if sha_file(fp) != item.get("sha256"):
            return reject("hash-mismatch:" + str(item.get("kind")))
        if item.get("kind") in present:
            return reject("duplicate-evidence-kind:" + str(item.get("kind")))
        try:
            present[item.get("kind")] = json.loads(fp.read_text())
        except Exception:
            return reject("malformed-evidence:" + str(item.get("kind")))
    cand = pub / "candidate.json"
    if not cand.is_file():
        return reject("missing-candidate")
    sha_cand = sha_file(cand)
    if sha_cand != g(cert, "agent_artifact", "sha256"):
        return reject("candidate-agent-binding")
    tgt = pub / "target.json"
    if not tgt.is_file():
        return reject("missing-target")
    if sha_file(tgt) != g(cert, "target", "artifact_sha256"):
        return reject("target-binding")
    for k in REQUIRED_KINDS:
        if k not in present:
            return reject("missing-evidence:" + k)

    ev = present
    req = request.get("claimed", {}) or {}
    joins = {
        "J1": eq_all(g(ev, "execution_trace", "candidate_sha256"), sha_cand),
        "J2": eq_all(g(ev, "execution_trace", "session_id"),
                     g(cert, "execution", "session_id"),
                     g(ev, "target_effect", "session_id")),
        "J3": eq_all(g(ev, "execution_trace", "base_instance_id"),
                     g(cert, "task", "base_instance_id"),
                     g(req, "base_instance_id")),
        "J4": eq_all(g(req, "condition_id"), g(cert, "condition", "id"),
                     g(ev, "execution_trace", "condition_id")),
        "J5": eq_all(g(req, "target_hashes", "artifact_sha256"),
                     g(cert, "target", "artifact_sha256")),
        "J6": eq_all(g(req, "run_id"), g(cert, "execution", "session_id")),
        "J7": (eq_all(g(ev, "reference_acceptance", "artifact_sha256"),
                      g(cert, "agent_artifact", "sha256"), sha_cand)
               and eq_all(g(ev, "reference_acceptance", "session_id"),
                          g(cert, "execution", "session_id"))),
        "J8": g(ev, "boundary", "enforced") is True,
        "J9": eq_all(g(ev, "verifier_metadata", "verifier_version"),
                     g(cert, "verification", "verifier_version"), VER),
    }
    joins_failed = sorted(k for k, v in joins.items() if not v)
    lvl = level_chain(ev, sha_cand, cert, joins_failed)

    mism = []
    if claims.get("artifact_authorship") == "PROVEN":
        if g(ev, "agent_artifact", "artifact_sha256") != sha_cand:
            mism.append("artifact_authorship")
    if claims.get("execution_identity") == "PROVEN":
        if g(ev, "execution_trace", "candidate_sha256") != sha_cand:
            mism.append("execution_identity")
    te = claims.get("target_effect")
    if te in ("OBSERVED", "NOT_OBSERVED"):
        if g(ev, "target_effect", "status") != te:
            mism.append("target_effect")
    ro = claims.get("reference_oracle_acceptance")
    if ro == "ACCEPTED":
        if not (g(ev, "reference_acceptance", "accepted") is True
                and g(ev, "reference_acceptance", "artifact_sha256") == sha_cand):
            mism.append("reference_oracle_acceptance")
    elif ro == "REJECTED":
        if g(ev, "reference_acceptance", "accepted") is not False:
            mism.append("reference_oracle_acceptance")
    if claims.get("boundary_enforcement") == "PROVEN":
        if g(ev, "boundary", "enforced") is not True:
            mism.append("boundary_enforcement")
    if claims.get("attribution") == "PROVEN":
        if lvl < 6:
            mism.append("attribution")

    violations = joins_failed + sorted(mism)
    if not violations and lvl == 6:
        out.update({"decision": "EMIT", "level": 6,
                    "reason": "all identity, condition, target, and claim bindings consistent"})
    else:
        reason = "claim-overreach supported=%d" % lvl
        if violations:
            reason += "; violations=" + ",".join(violations)
        out["reason"] = reason
        out["level"] = lvl
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
