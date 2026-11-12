#!/usr/bin/env python3
"""Experiment B / IAR-B system: V3-full — authenticated records + cross-record joins.

CLI: python3 eb_v3_full.py <public_dir> <trust_path>
Prints one JSON line: {system, decision, supported, requested, reason}.

Frozen semantics (EXPERIMENT_B_PROTOCOL.md):
  - all V3-sig checks: structural checks (top-level keys, claim enums,
    declared evidence file hashes, candidate and target bindings, declared
    trace hash) and detached Ed25519 signature verification of every declared
    evidence record under the trusted anchor for the record's own session_id;
  - plus the cross-record rung ladder: rung k is supported only if the
    records up to rung k are authentic AND bound to the credited execution
    session, the submitted candidate, and the claimed task/condition;
  - supported level = highest consecutive rung;
  - ACCEPT iff supported >= requested level AND no claim declares a rung
    above the supported one (no overreach);
  - otherwise REJECT with the supported level and violated bindings.
All decisions exit 0; the verdict is the printed JSON line.
"""
import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

TOP_REQUIRED = ["schema", "attempt_id", "task", "condition", "target",
                "agent_artifact", "execution", "verification", "claims", "evidence"]
CLAIM_ENUMS = {
    "artifact_authorship": {"PROVEN", "NOT_ESTABLISHED"},
    "execution_identity": {"PROVEN", "NOT_ESTABLISHED"},
    "target_effect": {"OBSERVED", "NOT_OBSERVED", "NOT_ESTABLISHED"},
    "reference_oracle_acceptance": {"ACCEPTED", "REJECTED", "NOT_ESTABLISHED"},
    "boundary_enforcement": {"PROVEN", "NOT_ESTABLISHED"},
    "attribution": {"PROVEN", "NOT_ESTABLISHED"},
}
LEVELS = ["artifact_authorship", "execution_identity", "target_effect",
          "reference_oracle_acceptance", "boundary_enforcement", "attribution"]
STRONG = {"artifact_authorship": "PROVEN", "execution_identity": "PROVEN",
          "target_effect": "OBSERVED", "reference_oracle_acceptance": "ACCEPTED",
          "boundary_enforcement": "PROVEN", "attribution": "PROVEN"}


def blob(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode()


def hobj(obj):
    return hashlib.sha256(blob(obj)).hexdigest()


def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def out(decision, supported, requested, reason):
    print(json.dumps({"system": "v3-full", "decision": decision,
                      "supported": supported, "requested": requested,
                      "reason": reason}, sort_keys=True))
    return 0


def _eq_all(*vals):
    return all(v is not None for v in vals) and len(set(vals)) == 1


def main():
    if len(sys.argv) != 3:
        return out("REJECT", None, None, "usage: eb_v3_full.py <public_dir> <trust_path>")
    pub = Path(sys.argv[1])
    trust = Path(sys.argv[2])
    try:
        cert = json.loads((pub / "certificate.json").read_text())
        req = json.loads((pub / "request.json").read_text())
        keys = json.loads(trust.read_text())["keys"]
    except Exception:
        return out("REJECT", None, None, "missing-certificate-or-request-or-trust")
    try:
        for k in TOP_REQUIRED:
            if k not in cert:
                return out("REJECT", None, None, f"missing-key:{k}")
        claims = cert.get("claims", {})
        for name, allowed in CLAIM_ENUMS.items():
            if name not in claims:
                return out("REJECT", None, None, f"missing-claim:{name}")
            if claims[name] not in allowed:
                return out("REJECT", None, None, f"bad-claim-enum:{name}")
        ev = cert.get("evidence")
        if not isinstance(ev, list) or not ev:
            return out("REJECT", None, None, "missing-evidence")
        kinds = []
        present = {}
        for item in ev:
            kind = item.get("kind")
            kinds.append(kind)
            rel = item.get("path", "")
            fp = pub / rel
            if not fp.exists():
                return out("REJECT", None, None, f"missing-evidence-file:{kind}")
            if sha_file(fp) != item.get("sha256"):
                return out("REJECT", None, None, f"evidence-hash-binding:{kind}")
            rec = json.loads(fp.read_text())
            sp = pub / (rel + ".sig")
            if not sp.exists():
                return out("REJECT", None, None, f"missing-signature:{kind}")
            session = rec.get("session_id")
            if session not in keys:
                return out("REJECT", None, None, f"unknown-signer:{kind}")
            try:
                Ed25519PublicKey.from_public_bytes(
                    bytes.fromhex(keys[session])
                ).verify(bytes.fromhex(sp.read_text().strip()),
                         bytes.fromhex(hobj(rec)))
            except Exception:
                return out("REJECT", None, None, f"bad-signature:{kind}")
            present[kind] = rec
        if len(set(kinds)) != len(kinds):
            return out("REJECT", None, None, "duplicate-evidence-kind")
        cand = pub / "candidate.json"
        if not cand.exists():
            return out("REJECT", None, None, "missing-candidate")
        sha_cand = sha_file(cand)
        if sha_cand != cert["agent_artifact"].get("sha256"):
            return out("REJECT", None, None, "candidate-agent-binding")
        tgt = pub / "target.json"
        if not tgt.exists():
            return out("REJECT", None, None, "missing-target")
        sha_tgt = sha_file(tgt)
        if sha_tgt != cert["target"].get("artifact_sha256"):
            return out("REJECT", None, None, "target-binding")
        if "execution_trace" in present and cert.get("execution", {}).get("trace_hash"):
            if sha_file(pub / "evidence/execution_trace.json") != cert["execution"]["trace_hash"]:
                return out("REJECT", None, None, "trace-hash-binding")
        lvl_name = (req.get("claimed") or {}).get("claim_level")
        if lvl_name not in LEVELS:
            return out("REJECT", None, None, "bad-claim-level")
        requested = LEVELS.index(lvl_name) + 1

        cred = cert["execution"].get("session_id")
        authorship = present.get("agent_artifact")
        trace = present.get("execution_trace")
        effect = present.get("target_effect")
        ref = present.get("reference_acceptance")
        boundary = present.get("boundary")
        meta = present.get("verifier_metadata")
        cert_agent = cert.get("agent_artifact", {})
        task = cert.get("task", {})
        cond = cert.get("condition", {})
        claimed = req.get("claimed") or {}

        rungs = []
        rungs.append(("l1", [
            ("l1:authorship-session", authorship is not None and authorship.get("session_id") == cred),
            ("l1:authorship-artifact", authorship is not None and authorship.get("artifact_sha256") == sha_cand),
            ("l1:cert-agent-sha", cert_agent.get("sha256") == sha_cand),
            ("l1:cert-agent-session", cert_agent.get("session_id") == cred),
        ]))
        rungs.append(("l2", [
            ("l2:trace-session", trace is not None and trace.get("session_id") == cred),
            ("l2:trace-candidate", trace is not None and trace.get("candidate_sha256") == sha_cand),
            ("l2:executor", trace is not None and cert.get("execution", {}).get("executor") == trace.get("executor")),
        ]))
        rungs.append(("l3", [
            ("l3:effect-session", effect is not None and effect.get("session_id") == cred),
            ("l3:effect-status", effect is not None and effect.get("status") == "OBSERVED"),
        ]))
        rungs.append(("l4", [
            ("l4:ref-session", ref is not None and ref.get("session_id") == cred),
            ("l4:ref-accepted", ref is not None and ref.get("accepted") is True),
            ("l4:ref-artifact", ref is not None and ref.get("artifact_sha256") == sha_cand),
        ]))
        rungs.append(("l5", [
            ("l5:boundary-session", boundary is not None and boundary.get("session_id") == cred),
            ("l5:boundary-enforced", boundary is not None and boundary.get("enforced") is True),
        ]))
        rungs.append(("l6", [
            ("l6:metadata-session", meta is not None and meta.get("session_id") == cred),
            ("l6:metadata-version", meta is not None and meta.get("verifier_version") == cert.get("verification", {}).get("verifier_version")),
            ("l6:J3-instance", _eq_all(trace.get("base_instance_id") if trace else None,
                                       task.get("base_instance_id"), claimed.get("base_instance_id"))),
            ("l6:J4-condition", _eq_all(claimed.get("condition_id"), cond.get("id"),
                                        trace.get("condition_id") if trace else None,
                                        effect.get("condition_id") if effect else None)),
            ("l6:J5-target", _eq_all((claimed.get("target_hashes") or {}).get("artifact_sha256"),
                                     cert.get("target", {}).get("artifact_sha256"), sha_tgt)),
            ("l6:J6-run", claimed.get("run_id") == cred),
            ("l6:J7-trace-hash", trace is not None and cert.get("execution", {}).get("trace_hash") == sha_file(pub / "evidence/execution_trace.json")),
        ]))

        supported = 0
        first_failure = []
        for name, checks in rungs:
            failures = sorted(cn for cn, ok in checks if not ok)
            if failures:
                first_failure = failures
                break
            supported += 1
        overreach = sorted(name for i, name in enumerate(LEVELS)
                           if i + 1 > supported and claims.get(name) == STRONG[name])
    except Exception as exc:  # noqa: BLE001 - report malformed input as REJECT
        return out("REJECT", None, None, f"malformed:{type(exc).__name__}")
    if supported >= requested and not overreach:
        return out("ACCEPT", supported, requested, "signed-and-joined-consistent")
    reason = f"claim-overreach supported={supported}"
    if overreach:
        reason += "; violations=" + ",".join(overreach)
    if first_failure:
        reason += "; failed=" + ",".join(first_failure)
    return out("REJECT", supported, requested, reason)


if __name__ == "__main__":
    sys.exit(main())
