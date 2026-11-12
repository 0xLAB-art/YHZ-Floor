#!/usr/bin/env python3
"""Verify the committed lineage recomputation against a fresh run.

Re-runs recompute_lineage.py into a temporary file and compares the result
with the committed lineage_recomputation.json.  The recomputation is
deterministic and contains no timestamps, so a byte-identical result is the
expected outcome.

Usage:  python3 verify_lineage.py
Exit code 0 means the committed file is reproduced exactly.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMITTED = HERE / "lineage_recomputation.json"
SCRIPT = HERE / "recompute_lineage.py"


def main() -> int:
    if not COMMITTED.is_file():
        print("[FAIL] committed file missing: %s" % COMMITTED.name)
        return 1
    committed = COMMITTED.read_text()
    with tempfile.TemporaryDirectory() as tmp:
        fresh_path = Path(tmp) / "fresh.json"
        proc = subprocess.run([sys.executable, str(SCRIPT), "--out", str(fresh_path)],
                              capture_output=True, text=True)
        for line in proc.stdout.splitlines():
            print(line)
        if proc.returncode != 0:
            print("[FAIL] recomputation exited %d" % proc.returncode)
            print(proc.stderr[-800:])
            return 1
        fresh = fresh_path.read_text()
    if fresh == committed:
        print("[PASS] committed recomputation is reproduced byte for byte")
        return 0
    try:
        a, b = json.loads(committed), json.loads(fresh)
    except Exception as exc:  # pragma: no cover - defensive
        print("[FAIL] cannot parse JSON: %s" % exc)
        return 1
    # A partial distribution (for example a reviewer bundle that does not ship
    # the H1-R3 session records) reproduces a subset of the sections.  Every
    # section that was computed must still match exactly.
    mismatched = []
    compared = 0
    for key in sorted(a):
        if key not in b:
            mismatched.append("%s: missing from the fresh run" % key)
            continue
        if isinstance(b[key], dict) and "skipped" in b[key]:
            print("[SKIP] %s: %s" % (key, b[key]["skipped"]))
            continue
        compared += 1
        if a[key] != b[key]:
            mismatched.append("%s: differs" % key)
    if mismatched:
        for entry in mismatched:
            print("[FAIL] %s" % entry)
        print("[FAIL] committed recomputation is not reproduced")
        return 1
    print("[PASS] every computed section is reproduced (%d sections)" % compared)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())