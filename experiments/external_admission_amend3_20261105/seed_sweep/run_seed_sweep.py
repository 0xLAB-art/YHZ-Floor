#!/usr/bin/env python3
"""Seed-range sweep — Amendment 3 (DRAFT 2026-11-05).

The pre-freeze sweep required by the preregistration: every cohort label in
`PREREGISTRATION*.md` and every `results.jsonl` seed field must be disjoint
from the grid's seed range.  Field-level check; no model call, $0.

The first draft proposed 101–104.  The sweep (recorded here) rejected that
range: 101/102 are used by `info_contract_powered_20261025` (seeds 101–108)
and the P010-family preregs list 101–118 as spent.  The replacement range is
417–420, verified free at field level in this run.
"""

import glob
import json
import os
import re
from pathlib import Path

REPO = Path("/mnt/nvme5/ACTS-Attack")
BASE = REPO / "sp2027"
OUT = Path(__file__).resolve().parent / "SEED_SWEEP.json"
CANDIDATE = list(range(417, 421))
SELF_NAMESPACE = "research_execution/external_admission_amend3_20261105/"


def scan():
    used = {}
    for pattern in ("research_execution/**/results.jsonl",
                    "research_execution/**/PREREGISTRATION*.md",
                    "research_execution/**/*.jsonl"):
        for path in glob.glob(str(BASE / pattern), recursive=True):
            rel = os.path.relpath(path, BASE)
            # the amendment-3 namespace is the reservation being checked, not a
            # cohort: its own draft/seed-sweep must not count as prior usage.
            if rel.startswith(SELF_NAMESPACE):
                continue
            try:
                text = open(path, errors="ignore").read()
            except OSError:
                continue
            if path.endswith(".jsonl"):
                for line in text.splitlines():
                    match = re.search(r'"seed"\s*:\s*(\d+)', line)
                    if match:
                        value = int(match.group(1))
                        if 0 <= value < 100000:
                            used.setdefault(value, rel)
            else:
                for line in text.splitlines():
                    if "seed" not in line.lower():
                        continue
                    for a, b in re.findall(r"(\d{1,5})\s*[–\-]\s*(\d{1,5})", line):
                        a, b = int(a), int(b)
                        if 0 < a < 100000 and 0 < b < 100000 and b - a < 2000:
                            for value in range(a, b + 1):
                                used.setdefault(value, rel)
                    for token in re.findall(r"\b(\d{2,5})\b", line):
                        value = int(token)
                        if 0 < value < 100000:
                            used.setdefault(value, rel)
    return used


def main():
    used = scan()
    conflicts = {value: used[value] for value in CANDIDATE if value in used}
    # show the rejected first draft too
    draft_conflicts = {value: used[value] for value in range(101, 105)}
    free_runs = []
    run = []
    for value in range(300, 1000):
        if value in used:
            if len(run) >= 4:
                free_runs.append([run[0], run[-1]])
            run = []
        else:
            run.append(value)
    if len(run) >= 4:
        free_runs.append([run[0], run[-1]])

    payload = {
        "schema": "external-admission-amend3-seed-sweep/1-draft",
        "date": "2026-11-05",
        "method": (
            "field-level scan of every research_execution/**/results.jsonl "
            "seed field and every PREREGISTRATION*.md numeric seed "
            "range/label; the prereg reservation list is also checked"),
        "draft_range_rejected": {
            "range": [101, 104],
            "in_use_sources": draft_conflicts,
            "reason": ("101–104 are already spent (info_contract_powered "
                       "101–108; P010-family preregs list 101–118)"),
        },
        "candidate_range": CANDIDATE,
        "candidate_range_free": not conflicts,
        "candidate_conflicts": conflicts,
        "free_4_runs_300_999": free_runs[:20],
        "sources_checked": [
            "research_execution/**/results.jsonl",
            "research_execution/**/*.jsonl (seed field)",
            "research_execution/**/PREREGISTRATION*.md",
        ],
        "excluded_from_sweep": SELF_NAMESPACE + " (the reservation itself, not a cohort)",
        "boundary": (
            "Sweep record only; it registers nothing until the freeze commit. "
            "The grid's seed labels carry no per-seed randomness."),
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps({
        "candidate": CANDIDATE,
        "free": payload["candidate_range_free"],
        "draft_101_104_used": bool(draft_conflicts),
        "draft_conflict_sources": draft_conflicts,
        "out": str(OUT),
    }, indent=2))
    return 0 if not conflicts else 1


if __name__ == "__main__":
    raise SystemExit(main())
