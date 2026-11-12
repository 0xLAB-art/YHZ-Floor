#!/usr/bin/env python3
"""Build the Amendment-3 oracle answer file (DRAFT 2026-11-05).

ORACLE TRUTH MATERIAL — used for offline verification only; never prompt
content, never transcript content.  Mirrors the Phase-2 oracle schema
(external_admission_20261024/oracle/answers.json).

The answers are the pinned NYU CTF Bench `challenge.json` `flag` values for
the seven criterion-5-eligible tasks; the run log that derives them is
census_nyu/reference_solvers/reference_solve_run.jsonl.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "answers.json"
RUN_LOG = ROOT / "census_nyu" / "reference_solvers" / "reference_solve_run.jsonl"
OUTCOMES = ROOT / "census_nyu" / "criterion5_outcomes.json"
PIN = Path("/tmp/opencode/nyu_pin")


def main():
    outcomes = json.loads(OUTCOMES.read_text(encoding="utf-8"))
    eligible = set(outcomes["grid_membership"])
    runs = {}
    for line in RUN_LOG.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        runs[row["task_id"]] = row
    answers, sources = {}, {}
    for task_id in sorted(eligible):
        run = runs[task_id]
        if run["verdict"] != "MATCH":
            raise SystemExit(f"task not verified: {task_id}")
        path = PIN / run["path_in_pin"] / "challenge.json"
        pinned = json.loads(path.read_text(encoding="utf-8"))["flag"]
        if pinned != run["answer"]:
            raise SystemExit(f"answer drift: {task_id}")
        answers[task_id] = pinned
        sources[task_id] = {
            "path_in_pin": run["path_in_pin"],
            "answer_sha256": hashlib.sha256(pinned.encode()).hexdigest(),
            "reference_solve_verdict": run["verdict"],
        }
    payload = {
        "schema": "external-admission-oracle-answers/1",
        "namespace": "external_admission_amend3_20261105",
        "classification": (
            "ORACLE TRUTH MATERIAL — used for offline verification only; "
            "NEVER prompt content, NEVER transcript content"),
        "source": (
            "pinned NYU CTF Bench challenge.json flag fields; our oracle "
            "compares submitted.strip() == pinned answer exactly (the Phase-2 "
            "metadata-answer semantics)"),
        "verification": (
            "every answer reproduced byte-exactly by the offline stdlib-only "
            "reference solve; see census_nyu/reference_solvers/"
            "reference_solve_run.jsonl"),
        "answers": answers,
        "sources": sources,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps({"tasks": len(answers), "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
