#!/usr/bin/env python3
"""What each registered design can resolve (no model calls, no new data).

For a two-arm design with n sessions per arm, acceptance rates p and p+d, and
a two-sided Fisher exact test at alpha=0.05, enumerate the exact sampling
distribution over (k1, k2) and report:

  mde[n] = smallest d in percentage points with power >= 0.80.

Baseline p is the least favourable (maximum-variance) p=0.5, so the reported
mde is the *best case*: every other baseline resolves less.  Reporting the
best case is the conservative choice for a limitation---a design cannot be
claimed to resolve more than this.

Also reports, for each observed null/descriptive claim, the exact
Clopper-Pearson interval on the observed rate, so the text can state the
effect the data still admits instead of asserting absence.

Outputs RESOLUTION.json (machine-read by the paper verifier) and
RESOLUTION.md.
"""
import json
from pathlib import Path

import numpy as np
from scipy.stats import binom, fisher_exact

HERE = Path(__file__).resolve().parent
ALPHA = 0.05
POWER = 0.80
NS = (4, 8, 10, 16, 32, 64)
STEPS = [d for d in np.arange(0.0, 1.0001, 0.01)]


def reject_matrix(n, p1, p2):
    """P(reject) for Fisher two-sided over all (k1, k2)."""
    ks = np.arange(n + 1)
    w1 = binom.pmf(ks, n, p1)
    w2 = binom.pmf(ks, n, p2)
    power = 0.0
    for i, k1 in enumerate(ks):
        if w1[i] == 0.0:
            continue
        for j, k2 in enumerate(ks):
            if w2[j] == 0.0:
                continue
            _, p = fisher_exact([[int(k1), n - int(k1)], [int(k2), n - int(k2)]],
                                alternative="two-sided")
            if p < ALPHA:
                power += w1[i] * w2[j]
    return power


def mde(n, p=0.5):
    for d in STEPS:
        if p + d > 1.0:
            break
        if reject_matrix(n, p, p + d) >= POWER:
            return round(float(d), 2)
    return None


def cp_interval(k, n, alpha=ALPHA):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return round(lo, 3), round(hi, 3)


def approx_n_for(target, p=0.5, power=POWER, alpha=ALPHA):
    """Standard normal approximation, PER-ARM n: pooled variance under the
    z_alpha term, unpooled under the power term. No continuity correction
    (an earlier revision multiplied the whole expression by 2, which yields
    the TWO-ARM TOTAL -- 181 at target=0.20 -- and was mislabelled per-arm
    and as continuity-corrected; fixed 2026-11-06).  Quantiles use
    statistics.NormalDist (identical to scipy.stats.norm.ppf; keeps this
    function scipy-free)."""
    from statistics import NormalDist
    nd = NormalDist()
    z_a = nd.inv_cdf(1 - alpha / 2)
    z_b = nd.inv_cdf(power)
    p2 = p + target
    var = p * (1 - p) + p2 * (1 - p2)
    pbar = (p + p2) / 2
    return int(np.ceil((z_a * np.sqrt(2 * pbar * (1 - pbar))
                        + z_b * np.sqrt(var)) ** 2 / target ** 2))


def main():
    rows = []
    for n in NS:
        print(f"n={n} ...", flush=True)
        rows.append({"n_per_arm": n, "mde_pp_at_p05_80power": mde(n),
                     "max_power_at_p2_1": round(reject_matrix(n, 0.5, 1.0), 3)})

    # Designs whose claims are null or descriptive, with their observed counts.
    observed = [
        {"claim": "H2 wrapper extension (accepted)",
         "n_per_arm": 10, "k": [5, 7],
         "note": "registered direction reversal; null by design"},
        {"claim": "H2 frozen pairs (accepted)",
         "n_per_arm": 4, "k": [2, 3], "note": "registered n>=4 pairs"},
        {"claim": "P010L2 withheld arm (accepted)",
         "n_per_arm": 8, "k": [0, 8], "note": "informative: at the floor"},
    ]
    for rec in observed:
        rec_mde = mde(rec["n_per_arm"])
        rec["mde_pp"] = None if rec_mde is None else rec_mde * 100
        rec["mde_none"] = rec_mde is None
        rec["ci"] = [cp_interval(rec["k"][0], rec["n_per_arm"]),
                     cp_interval(rec["k"][1], rec["n_per_arm"])]

    # n required to resolve a 20-point and a 10-point difference at 80% power.
    # The exact enumeration is feasible only for modest n, so the required
    # per-arm n is reported by the standard (pooled-variance) normal
    # approximation; the exact table above is the load-bearing one.
    required = {f"{int(t * 100)}pp": approx_n_for(t) for t in (0.20, 0.10)}

    # Paired (exact McNemar) resolution floor: with b one-directional
    # discordant pairs and no ties, two-sided p = 2 * 0.5**b, so the first b
    # that clears alpha is 6; b=5 gives 0.0625.
    paired_floor = next(b for b in range(1, 40) if 2 * 0.5 ** b < ALPHA)
    paired = {"min_one_way_discordant_p05": paired_floor,
              "p_at_floor": 2 * 0.5 ** paired_floor,
              "p_at_floor_minus_one": 2 * 0.5 ** (paired_floor - 1),
              "observed": {"P010P": 5, "P010L2": 8, "P010L3": 8,
                           "P010N16": 10}}

    out = {"alpha": ALPHA, "power": POWER, "baseline_p": 0.5,
           "paired_exact": paired,
           "method": "exact enumeration, two-sided Fisher, maximum-variance "
                     "baseline (best case)",
           "table": rows, "observed": observed,
           "n_required": required,
           "n_required_method": "standard normal approximation (pooled "
                                "variance), per-arm n; no continuity "
                                "correction; exact enumeration for these n is "
                                "out of scope of this offline script",
           "caveat": "MDE is the best case; at any baseline away from 0.5 the "
                     "same n resolves less. Used to state what a design cannot "
                     "resolve, never to convert a null into a positive."}
    (HERE / "RESOLUTION.json").write_text(json.dumps(out, indent=2,
                                                     sort_keys=True) + "\n")
    lines = ["# Design resolution (exact, no model calls)", "",
             f"Two-sided Fisher, alpha={ALPHA}, power={POWER}, baseline p=0.5 "
             "(best case).", "",
             "| n per arm | max power (at p2=1.0) | smallest detectable diff (pp) |",
             "|---:|---:|---:|"]
    for r in rows:
        cells = ("none (no d resolves at this n)"
                 if r['mde_pp_at_p05_80power'] is None
                 else int(r['mde_pp_at_p05_80power'] * 100))
        lines.append(f"| {r['n_per_arm']} | {r['max_power_at_p2_1']:.2f} | {cells} |")
    lines += ["", f"n required to resolve 20pp: {required.get('20pp')}, "
                  f"10pp: {required.get('10pp')}.", "",
              "| observed claim | k/n per arm | MDE (pp) | 95% CI |", "|---|---|---:|---|"]
    for rec in observed:
        mde_cell = "none" if rec['mde_pp'] is None else f"{rec['mde_pp']:.0f}"
        lines.append(f"| {rec['claim']} | {rec['k'][0]}/{rec['n_per_arm']} vs "
                     f"{rec['k'][1]}/{rec['n_per_arm']} | {mde_cell} | "
                     f"[{rec['ci'][0][0]}, {rec['ci'][0][1]}] vs "
                     f"[{rec['ci'][1][0]}, {rec['ci'][1][1]}] |")
    (HERE / "RESOLUTION.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
