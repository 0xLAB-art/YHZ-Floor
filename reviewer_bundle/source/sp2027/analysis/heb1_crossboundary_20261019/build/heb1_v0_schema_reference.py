#!/usr/bin/env python3
"""V0 baseline: schema + declared-reference acceptance only.

Blind public-input baseline. Reads ONLY the public case directory.
Decision rule: if the certificate validates against the HEB-1 JSON Schema,
trust the declared claims and emit the declared level; else REJECT.
No hash checks, no joins, no crypto. This is the naive contract-checking
baseline the HEB-1 study compares against.

Usage: python3 heb1_v0_schema_reference.py <public_dir>
Prints one line of JSON to stdout.
"""
import json
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent / "heb1_certificate_schema.json"


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


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"system": "V0", "decision": "REJECT", "level": 0,
                          "reason": "usage: heb1_v0_schema_reference.py <public_dir>"}))
        return 2
    pub = Path(sys.argv[1])
    out = {"system": "V0", "decision": "REJECT", "level": 0, "reason": ""}
    try:
        cert = json.loads((pub / "certificate.json").read_text())
        json.loads((pub / "request.json").read_text())
        import jsonschema
        schema = json.loads(SCHEMA_PATH.read_text())
        jsonschema.validate(cert, schema)
    except Exception as e:
        out["reason"] = "schema-invalid:" + type(e).__name__
        print(json.dumps(out, sort_keys=True))
        return 0
    lvl = declared_level(cert.get("claims", {}))
    if lvl >= 1:
        out.update({"decision": "EMIT", "level": lvl,
                    "reason": "schema-valid; declared level trusted without integrity or binding checks"})
    else:
        out["reason"] = "schema-valid but no established declared level"
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
