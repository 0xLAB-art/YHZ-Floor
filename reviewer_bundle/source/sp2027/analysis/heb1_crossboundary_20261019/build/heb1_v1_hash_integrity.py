#!/usr/bin/env python3
"""V1 baseline: structure + hash integrity only.

Blind public-input baseline. Reads ONLY the public case directory.
Decision rule: structural keys present, claim values in enum, every declared
evidence hash matches its file, candidate file hash matches
cert.agent_artifact.sha256, target file hash matches cert.target.artifact_sha256
-> trust the declared level and emit min(6, declared). Else REJECT.
No identity joins, no condition/target/session binding, no crypto.

Usage: python3 heb1_v1_hash_integrity.py <public_dir>
Prints one line of JSON to stdout.
"""
import hashlib
import json
import sys
from pathlib import Path

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


def declared_level(claims: dict) -> int:
    steps = [
        claims.get("artifact_authorship") == "PROVEN",
        claims.get("execution_identity") == "PROVEN",
        claims.get("target_effect") == "OBSERVED",
        claims.get("reference_oracle_acceptance") == "ACCEPTED",
        claims.get("boundary_enforcement") == "PROVEN",
        claims.get("attribution") == "PROVEN",
    ]
    lvl = 0
    for i, ok in enumerate(steps, 1):
        if ok:
            lvl = i
        else:
            break
    return lvl


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"system": "V1", "decision": "REJECT", "level": 0,
                          "reason": "usage: heb1_v1_hash_integrity.py <public_dir>"}))
        return 2
    pub = Path(sys.argv[1])
    out = {"system": "V1", "decision": "REJECT", "level": 0, "reason": ""}

    def reject(reason: str) -> int:
        out["reason"] = reason
        print(json.dumps(out, sort_keys=True))
        return 0

    try:
        cert = json.loads((pub / "certificate.json").read_text())
        json.loads((pub / "request.json").read_text())
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
    for item in cert["evidence"]:
        fp = pub / item.get("path", "")
        if not fp.is_file():
            return reject("missing-evidence-file:" + str(item.get("kind")))
        if sha_file(fp) != item.get("sha256"):
            return reject("hash-mismatch:" + str(item.get("kind")))
    cand = pub / "candidate.json"
    if not cand.is_file():
        return reject("missing-candidate")
    if sha_file(cand) != cert.get("agent_artifact", {}).get("sha256"):
        return reject("candidate-agent-binding")
    tgt = pub / "target.json"
    if not tgt.is_file():
        return reject("missing-target")
    if sha_file(tgt) != cert.get("target", {}).get("artifact_sha256"):
        return reject("target-binding")

    lvl = declared_level(claims)
    if lvl >= 1:
        out.update({"decision": "EMIT", "level": min(6, lvl),
                    "reason": "structure+hashes consistent; declared level trusted"})
    else:
        out["reason"] = "structure+hashes consistent but no established declared level"
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
