#!/usr/bin/env python3
"""B2 baseline models: content-addressed (digest-only) vs execution-bound (digest-session) provenance verifier models.

CLI: python3 b2_prov_baselines.py <config> <public_dir> <trust_path>
  config in: digest-only | digest-session | abl-authjoin | abl-refjoin | abl-tracejoin | abl-executor
Prints one JSON line: {system, decision, supported, requested, reason}.

Frozen semantics: B2_PROTOCOL.md (sections 3-4; frozen design, recorded in the B2 freeze packet).

Faithful-model caveat (B2_PROTOCOL.md section 3): these are MODELS of design classes
(in-toto/SLSA-style digest-complete verification; RATS-style freshness/execution-identity
binding), implemented offline from the public descriptions of those design classes.
They are NOT the actual products, and no network/pip access was used.

- digest-only:   D1..D17 only (signature authenticity, declared-hash consistency,
                 cross-record digest continuity, record-content assertions;
                 NO execution-identity joins).
- digest-session: D1..D17 + S1..S6 (execution-identity binding: record.session_id == cred).
- ablations:     digest-session minus exactly one check (abl-authjoin -S1,
                 abl-refjoin -S4, abl-tracejoin -S2, abl-executor -D7).

supported = number of leading satisfied ladder levels (0..6); null on structural failure.
ACCEPT iff supported >= requested and no claim above supported declares a strong value.
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
EVIDENCE_ORDER = ["agent_artifact", "execution_trace", "target_effect",
                  "reference_acceptance", "boundary", "verifier_metadata"]

CONFIGS = ("digest-only", "digest-session", "abl-authjoin", "abl-refjoin",
           "abl-tracejoin", "abl-executor")

# per config: (disabled D-class checks, disabled S-class checks)
DISABLED = {
    "digest-only": (set(), {"S1", "S2", "S3", "S4", "S5", "S6"}),
    "digest-session": (set(), set()),
    "abl-authjoin": (set(), {"S1"}),
    "abl-refjoin": (set(), {"S4"}),
    "abl-tracejoin": (set(), {"S2"}),
    "abl-executor": ({"D7"}, set()),
}


def blob(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode()


def hobj(obj):
    return hashlib.sha256(blob(obj)).hexdigest()


def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def out(cfg, decision, supported, requested, reason):
    print(json.dumps({"system": cfg, "decision": decision,
                      "supported": supported, "requested": requested,
                      "reason": reason}, sort_keys=True))
    return 0


def _eq_all(*vals):
    return all(v is not None for v in vals) and len(set(vals)) == 1


def main():
    if len(sys.argv) != 4:
        print(json.dumps({"system": "b2-baselines", "decision": "REJECT",
                          "supported": None, "requested": None,
                          "reason": "usage: b2_prov_baselines.py <config> <public_dir> <trust_path>"},
                         sort_keys=True))
        return 0
    cfg = sys.argv[1]
    if cfg not in CONFIGS:
        print(json.dumps({"system": "b2-baselines", "decision": "REJECT",
                          "supported": None, "requested": None,
                          "reason": f"unknown-config:{cfg}"}, sort_keys=True))
        return 0
    pub = Path(sys.argv[2])
    trust = Path(sys.argv[3])
    try:
        cert = json.loads((pub / "certificate.json").read_text())
        req = json.loads((pub / "request.json").read_text())
        keys = json.loads(trust.read_text())["keys"]
    except Exception:
        return out(cfg, "REJECT", None, None, "missing-certificate-or-request-or-trust")
    try:
        # --- D1/D2/D3: structural + declared-hash + signature authenticity (global) ---
        for k in TOP_REQUIRED:
            if k not in cert:
                return out(cfg, "REJECT", None, None, f"missing-key:{k}")
        claims = cert.get("claims", {})
        for name, allowed in CLAIM_ENUMS.items():
            if name not in claims:
                return out(cfg, "REJECT", None, None, f"missing-claim:{name}")
            if claims[name] not in allowed:
                return out(cfg, "REJECT", None, None, f"bad-claim-enum:{name}")
        ev = cert.get("evidence")
        if not isinstance(ev, list) or not ev:
            return out(cfg, "REJECT", None, None, "missing-evidence")
        kinds = []
        present = {}
        for item in ev:
            kind = item.get("kind")
            kinds.append(kind)
            if kind not in EVIDENCE_ORDER:
                return out(cfg, "REJECT", None, None, f"unknown-evidence-kind:{kind}")
            rel = item.get("path", "")
            fp = pub / rel
            if not fp.exists():
                return out(cfg, "REJECT", None, None, f"missing-evidence-file:{kind}")
            if sha_file(fp) != item.get("sha256"):
                return out(cfg, "REJECT", None, None, f"evidence-hash-binding:{kind}")
            rec = json.loads(fp.read_text())
            sp = pub / (rel + ".sig")
            if not sp.exists():
                return out(cfg, "REJECT", None, None, f"missing-signature:{kind}")
            session = rec.get("session_id")
            if session not in keys:
                return out(cfg, "REJECT", None, None, f"unknown-signer:{kind}")
            try:
                Ed25519PublicKey.from_public_bytes(
                    bytes.fromhex(keys[session])
                ).verify(bytes.fromhex(sp.read_text().strip()),
                         bytes.fromhex(hobj(rec)))
            except Exception:
                return out(cfg, "REJECT", None, None, f"bad-signature:{kind}")
            present[kind] = rec
        if len(set(kinds)) != len(kinds):
            return out(cfg, "REJECT", None, None, "duplicate-evidence-kind")
        cand = pub / "candidate.json"
        if not cand.exists():
            return out(cfg, "REJECT", None, None, "missing-candidate")
        sha_cand = sha_file(cand)
        tgt = pub / "target.json"
        if not tgt.exists():
            return out(cfg, "REJECT", None, None, "missing-target")
        sha_tgt = sha_file(tgt)
        lvl_name = (req.get("claimed") or {}).get("claim_level")
        if lvl_name not in LEVELS:
            return out(cfg, "REJECT", None, None, "bad-claim-level")
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

        d_off, s_off = DISABLED[cfg]

        def keep(entries):
            return [(label, ok) for cid, label, ok in entries
                    if cid not in d_off and cid not in s_off]

        rungs = [
            ("l1", keep([
                ("D4", "l1:D4-cert-agent-sha",
                 cert_agent.get("sha256") == sha_cand),
                ("D5", "l1:D5-authorship-artifact",
                 authorship is not None and authorship.get("artifact_sha256") == sha_cand),
                ("S1", "l1:S1-authorship-session",
                 authorship is not None and authorship.get("session_id") == cred),
            ])),
            ("l2", keep([
                ("D6", "l2:D6-trace-candidate",
                 trace is not None and trace.get("candidate_sha256") == sha_cand),
                ("D7", "l2:D7-executor",
                 trace is not None and cert.get("execution", {}).get("executor") == trace.get("executor")),
                ("S2", "l2:S2-trace-session",
                 trace is not None and trace.get("session_id") == cred),
            ])),
            ("l3", keep([
                ("D8", "l3:D8-effect-status",
                 effect is not None and effect.get("status") == "OBSERVED"),
                ("S3", "l3:S3-effect-session",
                 effect is not None and effect.get("session_id") == cred),
            ])),
            ("l4", keep([
                ("D9", "l4:D9-ref-accepted",
                 ref is not None and ref.get("accepted") is True),
                ("D10", "l4:D10-ref-artifact",
                 ref is not None and ref.get("artifact_sha256") == sha_cand),
                ("S4", "l4:S4-ref-session",
                 ref is not None and ref.get("session_id") == cred),
            ])),
            ("l5", keep([
                ("D11", "l5:D11-boundary-enforced",
                 boundary is not None and boundary.get("enforced") is True),
                ("S5", "l5:S5-boundary-session",
                 boundary is not None and boundary.get("session_id") == cred),
            ])),
            ("l6", keep([
                ("D12", "l6:D12-metadata-version",
                 meta is not None and meta.get("verifier_version") == cert.get("verification", {}).get("verifier_version")),
                ("D13", "l6:D13-target",
                 _eq_all((claimed.get("target_hashes") or {}).get("artifact_sha256"),
                         cert.get("target", {}).get("artifact_sha256"), sha_tgt)),
                ("D14", "l6:D14-instance",
                 _eq_all(trace.get("base_instance_id") if trace else None,
                         task.get("base_instance_id"), claimed.get("base_instance_id"))),
                ("D15", "l6:D15-condition",
                 _eq_all(claimed.get("condition_id"), cond.get("id"),
                         trace.get("condition_id") if trace else None,
                         effect.get("condition_id") if effect else None)),
                ("D16", "l6:D16-run",
                 claimed.get("run_id") == cred),
                ("D17", "l6:D17-trace-hash",
                 trace is not None and (not cert.get("execution", {}).get("trace_hash")
                                        or cert.get("execution", {}).get("trace_hash") == hobj(trace))),
                ("S6", "l6:S6-metadata-session",
                 meta is not None and meta.get("session_id") == cred),
            ])),
        ]

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
        return out(cfg, "REJECT", None, None, f"malformed:{type(exc).__name__}")
    if supported >= requested and not overreach:
        reason = ("content-addressed-consistent" if cfg == "digest-only"
                  else "content-and-execution-consistent")
        return out(cfg, "ACCEPT", supported, requested, reason)
    reason = f"claim-overreach supported={supported}"
    if overreach:
        reason += "; violations=" + ",".join(overreach)
    if first_failure:
        reason += "; failed=" + ",".join(first_failure)
    return out(cfg, "REJECT", supported, requested, reason)


if __name__ == "__main__":
    sys.exit(main())
