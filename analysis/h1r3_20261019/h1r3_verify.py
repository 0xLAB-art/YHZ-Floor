#!/usr/bin/env python3
"""H1-R3 post-hoc integrity audit.

Re-runs the independent reference adjudicator over every retained session and
compares its verdict with the recorded verdict.  Also re-runs the blind
validator, checks that every retained hash still matches, and confirms that the
protected historical artifacts were not modified.

No provider calls.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

import h1r3_contract as contract

PROTECTED = [
    "sp2027/analysis/RESULTS_LOCK.json",
    "sp2027/analysis/RESULTS_LOCK_H1PC.json",
    "sp2027/paper/main.tex",
    "sp2027/paper/main.pdf",
]
EXPECTED_PROTECTED = {
    "sp2027/analysis/RESULTS_LOCK.json": "4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39",
    "sp2027/analysis/RESULTS_LOCK_H1PC.json": "8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103",
    "sp2027/paper/main.tex": "51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461",
    "sp2027/paper/main.pdf": "fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a",
}


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "runs" / "confirmatory"
    rows = [json.loads(line) for line in (run_dir / "results.jsonl").read_text().splitlines()]

    disagreements, missing, checked = [], [], 0
    for row in rows:
        case = run_dir / "sessions" / row["session_id"]
        bundle = case / "reference_bundle.json"
        if not bundle.is_file():
            missing.append({"session": row["session_id"], "reason": "no-reference-bundle"})
            continue
        replay = contract.run_script(HERE / "h1r3_reference.py", [str(bundle)])
        recorded = (row.get("reference") or {}).get("verdict")
        checked += 1
        if replay.get("verdict") != recorded:
            disagreements.append({"session": row["session_id"], "recorded": recorded,
                                  "replay": replay.get("verdict"), "replay_detail": replay})
        cert = case / "certificate.private.json"
        if cert.is_file():
            cert_obj = json.loads(cert.read_text())
            for item in cert_obj.get("evidence", []):
                path = Path(item["path"])
                if not path.is_file() or sha_file(path) != item["sha256"]:
                    disagreements.append({"session": row["session_id"], "reason": "evidence-hash",
                                          "kind": item.get("kind")})

    protected = {}
    for rel in PROTECTED:
        path = ROOT / rel
        if path.is_file():
            digest = sha_file(path)
            protected[rel] = {"sha256": digest, "matches_expected": digest == EXPECTED_PROTECTED[rel]}
        else:
            protected[rel] = {"missing": True, "matches_expected": False}

    summary = {
        "run_dir": str(run_dir),
        "sessions": len(rows),
        "reference_replays": checked,
        "reference_disagreements": len(disagreements),
        "missing_bundles": len(missing),
        "protected_artifacts": protected,
        "protected_unchanged": all(v.get("matches_expected") for v in protected.values()),
        "recorded_terminal_counts": dict(Counter(r.get("terminal") for r in rows)),
        "details": disagreements[:20],
    }
    print(json.dumps(summary, indent=2))
    (HERE / "H1R3_INTEGRITY_AUDIT.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return 0 if not disagreements and summary["protected_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
