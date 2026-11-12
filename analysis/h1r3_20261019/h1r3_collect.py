#!/usr/bin/env python3
"""Rebuild `results.jsonl` (and a run summary) from retained per-session records.

The runner writes each `session_result.json` immediately, so an interrupted run
can be reconstructed without losing or reordering observations.  This script
never deletes or rewrites a session directory.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    run_dir = Path(sys.argv[1])
    sessions = sorted((run_dir / "sessions").glob("*/session_result.json"))
    rows = []
    for path in sessions:
        rows.append(json.loads(path.read_text()))
    rows.sort(key=lambda r: r.get("ordinal", 0))
    with (run_dir / "results.jsonl").open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    summary = {
        "sessions": len(rows),
        "terminal_counts": dict(Counter(r.get("terminal") for r in rows)),
        "usage_totals": {
            "input_tokens": sum((r.get("usage") or {}).get("input_tokens", 0) for r in rows),
            "output_tokens": sum((r.get("usage") or {}).get("output_tokens", 0) for r in rows),
        },
        "source": "reconstructed-from-session-records",
    }
    (run_dir / "run_summary_reconstructed.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
