#!/usr/bin/env python3
"""Experiment B / IAR-B system: V3-sig — authenticated records, no cross-record joins.

CLI: python3 eb_v3_sig.py <public_dir> <trust_path>
Prints one JSON line: {system, decision, supported, requested, reason}.

Frozen semantics (EXPERIMENT_B_PROTOCOL.md):
  - structural checks in the spirit of the hash-integrity baseline: top-level
    keys, claim enums, declared evidence file hashes, candidate and target
    bindings, declared trace hash;
  - every declared evidence record must carry a detached Ed25519 signature
    that verifies under the trusted anchor for the record's own session_id;
  - NO cross-record semantic joins (that is V3-full's job);
  - supported level = declared ladder level from `claims`;
  - ACCEPT iff supported >= requested level from request.claimed.claim_level.
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
    print(json.dumps({"system": "v3-sig", "decision": decision,
                      "supported": supported, "requested": requested,
                      "reason": reason}, sort_keys=True))
    return 0


def main():
    if len(sys.argv) != 3:
        return out("REJECT", None, None, "usage: eb_v3_sig.py <public_dir> <trust_path>")
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
        if len(set(kinds)) != len(kinds):
            return out("REJECT", None, None, "duplicate-evidence-kind")
        cand = pub / "candidate.json"
        if not cand.exists():
            return out("REJECT", None, None, "missing-candidate")
        if sha_file(cand) != cert["agent_artifact"].get("sha256"):
            return out("REJECT", None, None, "candidate-agent-binding")
        tgt = pub / "target.json"
        if not tgt.exists():
            return out("REJECT", None, None, "missing-target")
        if sha_file(tgt) != cert["target"].get("artifact_sha256"):
            return out("REJECT", None, None, "target-binding")
        if "execution_trace" in kinds and cert.get("execution", {}).get("trace_hash"):
            if sha_file(pub / "evidence/execution_trace.json") != cert["execution"]["trace_hash"]:
                return out("REJECT", None, None, "trace-hash-binding")
        supported = 0
        for name in LEVELS:
            if claims.get(name) == STRONG[name]:
                supported += 1
            else:
                break
        lvl_name = (req.get("claimed") or {}).get("claim_level")
        if lvl_name not in LEVELS:
            return out("REJECT", supported, None, "bad-claim-level")
        requested = LEVELS.index(lvl_name) + 1
    except Exception as exc:  # noqa: BLE001 - report malformed input as REJECT
        return out("REJECT", None, None, f"malformed:{type(exc).__name__}")
    if supported >= requested:
        return out("ACCEPT", supported, requested, "signed-evidence-consistent")
    return out("REJECT", supported, requested, f"claim-overreach supported={supported}")


if __name__ == "__main__":
    sys.exit(main())
