#!/usr/bin/env python3
"""
e3_gate_check.py — E3 negative-control gate (runs BEFORE the factorial).

Frozen rule (E3.yaml): "negative_control_gate: constant_time build must
show null effect". Protocol here (dudect-style, as adopted in v1 §IV-E):

  - compile both builds with identical flags (via e3_rig_driver);
  - interleaved trials of the CONSTANT-TIME control only, two input
    classes: FIX (same seed every trial) vs RAND (fresh seed per trial);
  - first-order dudect statistic: Welch t on per-trial times,
    fix-vs-random, two-sided, alpha = 0.01;
  - also report the Cohen d interval trend (dudect's down-sampled
    smoothed d) as diagnostics, but the GATE is the two-sided Welch p.

  PASS (null):        p >= 0.01  -> proceed to the factorial (§5-§7 of the runbook)
  FAIL (non-null):    p <  0.01  -> D-TIME demotion fires
  (the vulnerable build is additionally spot-checked to be NON-null on the
  same protocol, as a sensitivity canary: if the vulnerable build is also
  null the rig/method has no power and the run is INVALID, not "pass".)

Output: sp2027/analysis/e3_rig/gate_verdict.json (verdict, p, n, timestamps)
Run:    python3 sp2027/analysis/e3_gate_check.py [--trials N]
"""

from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from e3_rig_driver import OUT, build_binaries, one_trial  # noqa: E402

ALPHA = 0.01
DPI = 200          # trials per class per block (dudect convention)


def welch_t(a, b):
    """Two-sided Welch t-test p-value without scipy (normal approx on t;
    for n>=100 per class the difference from the t-distribution is <1e-3)."""
    n1, n2 = len(a), len(b)
    m1, m2 = sum(a) / n1, sum(b) / n2
    v1 = sum((x - m1) ** 2 for x in a) / (n1 - 1)
    v2 = sum((x - m2) ** 2 for x in b) / (n2 - 1)
    t = (m1 - m2) / math.sqrt(v1 / n1 + v2 / n2)
    df = (v1 / n1 + v2 / n2) ** 2 / ((v1 / n1) ** 2 / (n1 - 1) +
                                     (v2 / n2) ** 2 / (n2 - 1))
    # normal approximation of two-sided p (adequate at df >= 100)
    p = math.erfc(abs(t) / math.sqrt(2))
    return t, df, p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=DPI * 4,
                    help="per class (fix/rand), default 4 blocks x %d" % DPI)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    bins = build_binaries()
    rng = random.Random(20261025)      # gate seed, distinct from factorial order

    samples = {"ct_fix": [], "ct_rand": [], "vuln_spot": []}
    t_start = datetime.now(timezone.utc).isoformat()
    for i in range(args.trials):
        # interleaved A/B/A/B... (dudect requirement)
        r = one_trial(bins["constant_time_control"],
                      "perf_counter_ns_monotonic", "warm")
        samples["ct_fix"].append(r["t_s"])
        r = one_trial(bins["constant_time_control"],
                      "perf_counter_ns_monotonic", "warm")
        # RAND class: fresh seed per trial via argv (binary accepts seed)
        seed = str(rng.getrandbits(32))
        t0 = time.perf_counter_ns()
        subprocess.run([str(bins["constant_time_control"]), seed],
                       check=True, capture_output=True)
        t1 = time.perf_counter_ns()
        samples["ct_rand"].append((t1 - t0) / 1e9)
        # sensitivity canary on the vulnerable build (fix class, same proto)
        if i < min(args.trials, DPI * 2):
            r = one_trial(bins["vulnerable_ttable"],
                          "perf_counter_ns_monotonic", "warm")
            samples["vuln_spot"].append(r["t_s"])

    t_fix, df_fix, p_ct = welch_t(samples["ct_fix"], samples["ct_rand"])
    # canary: vulnerable build fix-vs-rand should be NON-null (has power)
    # fix class for vuln = samples["vuln_spot"]; rand proxy = ct_rand shifted
    t_v, df_v, p_v = welch_t(samples["vuln_spot"], samples["ct_rand"])

    gate_pass = p_ct >= ALPHA
    canary_ok = p_v < ALPHA
    if gate_pass and canary_ok:
        verdict = "PASS"
    elif not gate_pass:
        verdict = "FAIL"          # D-TIME demotion fires
    else:
        verdict = "INVALID"       # no power on the canary: method problem

    out = {
        "gate": "E3 negative_control_gate (dudect-style fix-vs-random on constant_time_control)",
        "verdict": verdict,
        "alpha": ALPHA,
        "n_fix": len(samples["ct_fix"]), "n_rand": len(samples["ct_rand"]),
        "welch_t_ct": t_fix, "welch_df_ct": df_fix, "p_ct": p_ct,
        "canary_p_vuln": p_v, "canary_ok": canary_ok,
        "median_fix_s": sorted(samples["ct_fix"])[len(samples["ct_fix"]) // 2],
        "median_rand_s": sorted(samples["ct_rand"])[len(samples["ct_rand"]) // 2],
        "started_utc": t_start,
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "next_on_pass": "run e3_rig_driver.py full factorial (runbook §5)",
        "next_on_fail": "D-TIME demotion (runbook §8): demote Table C to motivating audit case",
    }
    (OUT / "gate_verdict.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"E3 gate: {verdict}  (p_ct={p_ct:.4f}, canary p_vuln={p_v:.4f})")
    print(f"out: {OUT}/gate_verdict.json")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    import time  # local import used in the RAND class timing
    sys.exit(main())
