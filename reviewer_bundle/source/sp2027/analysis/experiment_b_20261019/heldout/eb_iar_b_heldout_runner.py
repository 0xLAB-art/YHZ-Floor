#!/usr/bin/env python3
"""Held-out runner for IAR-B (single blind pass).

Re-verifies the IAR-B freeze, re-points the frozen evaluation harness at the
held-out case tree, and executes exactly one blind pass over the 58 held-out
cases (determinism double-run included). Records the results path + sha256.

No retuning: this wrapper never edits the frozen harness or the held-out set.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BASE))

import eb_iar_b_heldout as G  # noqa: E402  (freeze helper + generator constants)
import eb_runner as R  # noqa: E402  (frozen evaluation harness)


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    G.verify_freeze()

    R.CASES = BASE / "iar_b_heldout" / "cases" / "dev"
    R.PRIV = BASE / "iar_b_heldout" / "private" / "dev"
    R.LABELS = BASE / "iar_b_heldout" / "labels" / "heldout_labels.json"
    R.TRUST = BASE / "iar_b_heldout" / "trust" / "heldout_run_keys.json"
    R.RUNS = BASE / "iar_b_heldout" / "runs"
    # Broaden the measured V3-sig attack set to include the held-out H10
    # (reference replay) family; gate thresholds are unchanged.
    R.FP_FAMILIES_V3SIG = set(R.FP_FAMILIES_V3SIG) | {"H10"}

    R.RUNS.mkdir(parents=True, exist_ok=True)
    before = {p.name for p in R.RUNS.iterdir() if p.is_dir()}

    rc = R.main()

    after = [p for p in R.RUNS.iterdir() if p.is_dir() and p.name not in before]
    after.sort(key=lambda p: p.stat().st_mtime)
    results = [p / "results.json" for p in after if (p / "results.json").exists()]
    if not results:
        print(json.dumps({"error": "no results.json produced", "rc": rc}, sort_keys=True))
        return 1
    out = results[-1]
    print(json.dumps({
        "heldout_results": str(out),
        "sha256": sha_file(out),
        "return_code": rc,
        "new_run_dirs": [p.name for p in after],
    }, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
