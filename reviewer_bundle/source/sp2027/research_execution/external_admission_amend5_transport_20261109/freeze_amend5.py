#!/usr/bin/env python3
"""Amendment-5 freeze: builds FREEZE.json (the frozen-input manifest).

FREEZE.json lists SHA-256 for every registered input of
PHASE2-EXTERNAL-ADMISSION-AMEND5-TRANSPORT-v1 (prereg §9). The runner
re-verifies every hash at live start and refuses any mismatch. The
namespace-restricted git commit containing this manifest is the
registration act; FREEZE_COMMIT.txt records that commit's hash and live
mode refuses to run until the marker exists.

Offline: zero model calls, zero network. Requires the FINAL
COMPLETENESS_CENSUS_AMEND5.json (prereg D1: the census completes via the
resume script BEFORE anything is frozen) and refuses to freeze a manifest
whose census registers no PASS combination.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.name
OUT = HERE / "FREEZE.json"

TOP_FILES = [
    "PREREGISTRATION_AMEND5_TRANSPORT.md",
    "run_amend5_sessions.py",
    "responses_client.py",
    "completeness_census_amend5.py",
    "completeness_census_resume.py",
    "COMPLETENESS_CENSUS_AMEND5.json",
    "compat_gate_amend5.py",
    "COMPAT_GATE_AMEND5.json",
    "PROMPT_HASHES.json",
    "seed_sweep_AMEND5_SEED_SWEEP.json",
]


def sha_abs(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    census_path = HERE / "COMPLETENESS_CENSUS_AMEND5.json"
    if not census_path.is_file():
        sys.exit("COMPLETENESS_CENSUS_AMEND5.json missing — the census "
                 "completes via completeness_census_resume.py BEFORE the "
                 "freeze (prereg D1)")
    census = json.loads(census_path.read_text())
    if not census.get("pass_combinations"):
        sys.exit("census registers no PASS combination — nothing to freeze")

    manifest = json.loads((HERE / "PROMPT_HASHES.json").read_text())

    files = {}
    for name in TOP_FILES:
        p = HERE / name
        if not p.is_file():
            sys.exit(f"freeze input missing: {name}")
        files[name] = {"path": f"{NS}/{name}", "sha256": sha_abs(p)}

    for e in manifest["instantiated_prompts"]:
        rel = e["path"]
        p = HERE / rel
        if not p.is_file():
            sys.exit(f"prompt missing: {rel}")
        files[f"prompt:{e['task_id']}:{e['representation']}"] = {
            "path": f"{NS}/{rel}", "sha256": sha_abs(p)}

    for task, arts in sorted(manifest["artifacts"].items()):
        for a in arts:
            rel = f"fixtures/tasks/{task}/{a['name']}"
            p = HERE / rel
            if not p.is_file():
                sys.exit(f"artifact missing: {rel}")
            files[f"artifact:{task}:{a['name']}"] = {
                "path": f"{NS}/{rel}", "sha256": sha_abs(p)}

    for rel in ("oracle/answers.json",
                "census_nyu/criterion5_outcomes.json"):
        p = HERE / rel
        if not p.is_file():
            sys.exit(f"input missing: {rel}")
        files[rel] = {"path": f"{NS}/{rel}", "sha256": sha_abs(p)}

    freeze = {
        "schema": "external-admission-amend5-freeze/1",
        "protocol": "PHASE2-EXTERNAL-ADMISSION-AMEND5-TRANSPORT-v1",
        "namespace": NS,
        "generated_date": time.strftime("%Y-%m-%d"),
        "status": "FROZEN",
        "files": files,
        "census_summary": {
            "pass_combinations": len(census["pass_combinations"]),
            "grid_sessions_expected": len(census["pass_combinations"]) * 4,
        },
        "boundary": (
            "the namespace-restricted git commit containing FREEZE.json is "
            "the registration act; FREEZE_COMMIT.txt records that commit's "
            "hash and the live runner refuses to start without it; any "
            "post-freeze change lands in the prereg §10 deviation ledger"),
    }
    OUT.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"files": len(files),
                      "pass_combinations":
                          len(census["pass_combinations"]),
                      "grid_sessions_expected":
                          len(census["pass_combinations"]) * 4,
                      "written": str(OUT)}, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
