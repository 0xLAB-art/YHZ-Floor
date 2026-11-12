#!/usr/bin/env python3
"""Build a compact failure dossier from a retained H1-R3 run.

For every non-success primary session, emit the terminal stage, the reference
detail, the runtime error class, and the program lines most likely to explain
the failure.  Used for the manual mechanism attribution in the final report.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

KEY_PATTERNS = [
    r"\bd\s*=", r"\bk\s*=", r"modinv|pow\(.*-1", r"fromhex|b64decode|base64",
    r"plaintext|keystream", r"print\(", r"assert",
]


def source_excerpt(path: Path, limit: int = 14) -> list[str]:
    if not path.is_file():
        return []
    lines = path.read_text().splitlines()
    hits = []
    for idx, line in enumerate(lines, start=1):
        if any(re.search(p, line) for p in KEY_PATTERNS):
            hits.append(f"{idx:4d}: {line.strip()[:160]}")
        if len(hits) >= limit:
            break
    return hits


def main() -> int:
    run_dir = Path(sys.argv[1])
    rows = [json.loads(line) for line in (run_dir / "results.jsonl").read_text().splitlines()]
    dossier = []
    for row in rows:
        if row.get("kind") != "primary" or row.get("terminal") == "SUCCESS":
            continue
        case = run_dir / "sessions" / row["session_id"]
        ref = row.get("reference") or {}
        dossier.append({
            "session_id": row["session_id"], "family": row["family"], "level": row["level"],
            "seed": row["seed"], "arm": row["arm"], "terminal": row["terminal"],
            "execution_status": row.get("execution_status"),
            "schema_errors": row.get("output_schema_errors"),
            "qualification_violations": (row.get("qualification") or {}).get("violations"),
            "reference_detail": ref.get("detail"),
            "public_sufficiency_confirmed": ref.get("public_sufficiency_confirmed"),
            "certificate_integrity": ref.get("certificate_integrity"),
            "stderr_tail": (row.get("stderr_tail") or "")[:600],
            "generalization": row.get("generalization", {}).get("success"),
            "source_chars": row.get("source_chars"),
            "source_excerpt": source_excerpt(case / "candidate.py"),
        })
    summary = {
        "run_dir": str(run_dir),
        "failures": len(dossier),
        "by_stage": dict(Counter(d["terminal"] for d in dossier)),
        "by_arm": dict(Counter(d["arm"] for d in dossier)),
        "by_family_stage": dict(Counter(f"{d['family'][:3]}|{d['terminal']}" for d in dossier)),
        "by_level": dict(Counter(d["level"] for d in dossier)),
        "public_sufficiency_confirmed_all": all(d["public_sufficiency_confirmed"] for d in dossier) if dossier else None,
        "certificate_integrity_all": all(d["certificate_integrity"] for d in dossier) if dossier else None,
    }
    out = {"summary": summary, "dossier": dossier}
    (HERE / "H1R3_FAILURE_DOSSIER.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
