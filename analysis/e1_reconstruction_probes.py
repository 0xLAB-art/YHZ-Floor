#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

BENCHMARKS = {
    "Cybench": "cybench",
    "NYU CTF Bench": "nyu_ctf_bench",
    "CVE-Bench": "cve_bench",
    "Incalmo": "incalmo",
    "AgentHarm": "agentharm",
    "WebSP-Eval": "websp_eval",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    summary = list(csv.DictReader((root / "sp2027/benchmarks/summary.csv").open()))
    freeze = list(csv.DictReader((root / "human_audit/source_freeze_20261005/SOURCE_FREEZE_20261005_v2.csv").open()))
    result = []
    for row in summary:
        if row["benchmark"] not in BENCHMARKS:
            continue
        slug = BENCHMARKS[row["benchmark"]]
        fields = root / "sp2027/benchmarks" / slug / "fields.md"
        evidence = sorted(str(p.relative_to(root)) for p in (fields.parent / "evidence").glob("*.md"))
        source_rows = [r for r in freeze if r["benchmark"] == slug]
        outcome = row["reconstruction_probe"]
        if outcome.startswith("reconstructed"):
            classification = "reconstructed"
        elif outcome.startswith("partial"):
            classification = "partial"
        elif outcome.startswith("cannot_reconstruct"):
            classification = "cannot_reconstruct"
        else:
            classification = "unresolved"
        result.append({
            "benchmark": row["benchmark"],
            "worksheet": str(fields.relative_to(root)),
            "evidence_files_present": evidence,
            "source_freeze_rows": len(source_rows),
            "source_archive_files_available": sum(
                (root / "human_audit" / r["relative_source_path"]).is_file()
                for r in source_rows
            ),
            "recorded_outcome": outcome,
            "release_result_rederivation": classification,
            "fresh_replay_performed": False,
            "integrity_verification": "manifest/source-freeze check is separate from reconstruction",
        })
    print(json.dumps({
        "schema": "e1-f9-probe-run/1.0.0",
        "mode": "read-only release evidence inspection",
        "network_or_provider_calls": 0,
        "benchmarks": result,
    }, indent=2))


if __name__ == "__main__":
    main()
