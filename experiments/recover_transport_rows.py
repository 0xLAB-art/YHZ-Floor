#!/usr/bin/env python3
"""Clean-then-resume recovery: drop transport-failed rows from a cohort's
results.jsonl files (root + shard level) so the cohort's own resume logic
re-runs exactly those pairs. Valid outcomes (SUCCESS, ORACLE_FAIL,
EMPTY_RESPONSE=floor-exhausted) are kept. Dropped rows are archived in
dropped_transport_rows.jsonl next to the file they came from."""
import json, shutil, sys
from pathlib import Path

BAD = {"HTTP_ERROR", "MALFORMED_PROVIDER_JSON", "NO_SUBMISSION", "TIMEOUT",
       "INCOMPLETE_RESPONSE", "PROVIDER_UNAVAILABLE"}

def clean_file(p: Path):
    if not p.exists():
        return 0
    keep, drop = [], []
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            keep.append(line); continue
        (drop if r.get("status") in BAD else keep).append(line)
    if drop:
        shutil.copy2(p, p.with_suffix(".jsonl.pre_recovery"))
        p.write_text("\n".join(keep) + ("\n" if keep else ""))
        with (p.parent / "dropped_transport_rows.jsonl").open("a") as f:
            f.write("\n".join(drop) + "\n")
    return len(drop)

def main(ns_name):
    ns = Path(ns_name)
    if not ns.is_absolute():
        ns = Path(__file__).resolve().parent / ns_name
    total = 0
    for p in [ns / "results.jsonl"] + list(ns.glob("shard_*/results.jsonl")):
        total += clean_file(p)
    print(f"{ns.name}: dropped {total} transport rows; ready to resume")

if __name__ == "__main__":
    main(sys.argv[1])
