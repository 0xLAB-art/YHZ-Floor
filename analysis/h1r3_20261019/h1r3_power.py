#!/usr/bin/env python3
"""H1-R3 prospective power and precision analysis.

Run BEFORE the confirmatory campaign.  It fixes, on the record, the sample
size, the equivalence margin, and the achievability claims that the confirmatory
analysis will be allowed to make.

Model: N matched instances.  Each instance yields (Y_ref, Y_treat) in {0,1}.
b = P(Y_ref=1, Y_treat=0), c = P(Y_ref=0, Y_treat=1), tau = c - b.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from scipy import stats as sps

sys.path.insert(0, str(Path(__file__).resolve().parent))


def exact_mcnemar_power(n_pairs: int, p_b: float, p_c: float, alpha: float = 0.05) -> float:
    """Exact two-sided McNemar power by enumerating the discordant count."""
    p_disc = p_b + p_c
    if p_disc <= 0:
        return alpha
    n_disc = [sps.binom.pmf(k, n_pairs, p_disc) for k in range(n_pairs + 1)]
    power = 0.0
    for k in range(n_pairs + 1):
        if n_disc[k] < 1e-14:
            continue
        # conditional on k discordant pairs, b ~ Bin(k, p_b / p_disc)
        q = p_b / p_disc
        cond_power = 0.0
        for b in range(k + 1):
            p = sps.binomtest(b, k, 0.5, alternative="two-sided").pvalue if k else 1.0
            if p < alpha:
                cond_power += sps.binom.pmf(b, k, q)
        power += n_disc[k] * cond_power
    return power


def zero_discordance_bound(n_pairs: int, alpha: float = 0.05) -> float:
    """One-sided 1-alpha upper confidence bound on the discordance rate with 0 events."""
    return 1 - alpha ** (1 / n_pairs)


def interval_width(n_pairs: int, p_disc: float, tau: float = 0.0, z: float = 1.959963984540054) -> float:
    se = math.sqrt(max(p_disc - tau * tau, 1e-12) / n_pairs)
    return 2 * z * se


def main() -> int:
    scenarios = [
        {"label": "noise-only", "p_b": 0.02, "p_c": 0.02},
        {"label": "small-harm", "p_b": 0.05, "p_c": 0.01},
        {"label": "moderate-harm", "p_b": 0.10, "p_c": 0.02},
        {"label": "large-harm", "p_b": 0.20, "p_c": 0.02},
        {"label": "small-benefit", "p_b": 0.01, "p_c": 0.05},
    ]
    n_values = [24, 32, 48, 64, 96, 128]
    table = []
    for n in n_values:
        row = {"n_pairs": n, "zero_discordance_95_upper_bound": round(zero_discordance_bound(n), 4)}
        for sc in scenarios:
            tau = sc["p_c"] - sc["p_b"]
            row[sc["label"]] = {
                "tau": round(tau, 4),
                "power": round(exact_mcnemar_power(n, sc["p_b"], sc["p_c"]), 4),
                "expected_ci_halfwidth": round(interval_width(n, sc["p_b"] + sc["p_c"], tau) / 2, 4),
            }
        table.append(row)

    # Predeclared design
    margin = 0.10
    alpha = 0.05
    design = {
        "equivalence_margin": margin,
        "alpha": alpha,
        "primary_contrasts": ["R1_vs_R0", "R2_vs_R0"],
        "primary_level": "L3",
        "primary_n_per_family": 64,
        "primary_n_pooled": 128,
        "multiplicity": "Holm across the two primary contrasts, per family-stratified set",
    }
    primary = {
        "n_pooled": design["primary_n_pooled"],
        "zero_discordance_95_upper_bound": round(zero_discordance_bound(design["primary_n_pooled"]), 4),
        "power_at_moderate_harm": round(exact_mcnemar_power(design["primary_n_pooled"], 0.10, 0.02), 4),
        "power_at_small_harm": round(exact_mcnemar_power(design["primary_n_pooled"], 0.05, 0.01), 4),
        "halfwidth_at_5pct_discordance": round(interval_width(design["primary_n_pooled"], 0.05) / 2, 4),
        "halfwidth_at_10pct_discordance": round(interval_width(design["primary_n_pooled"], 0.10) / 2, 4),
    }
    per_family = {
        "n": design["primary_n_per_family"],
        "zero_discordance_95_upper_bound": round(zero_discordance_bound(design["primary_n_per_family"]), 4),
        "power_at_moderate_harm": round(exact_mcnemar_power(design["primary_n_per_family"], 0.10, 0.02), 4),
    }

    # Secondary single-arm blocks (smaller n): state what they can and cannot do.
    secondary = {}
    for n in (32, 24):
        secondary[f"n{n}"] = {
            "zero_discordance_95_upper_bound": round(zero_discordance_bound(n), 4),
            "power_at_moderate_harm": round(exact_mcnemar_power(n, 0.10, 0.02), 4),
        }

    report = {
        "analysis": "prospective power/precision for paired binary outcome",
        "design": design,
        "primary_pooled_L3": primary,
        "primary_per_family_L3": per_family,
        "secondary_blocks": secondary,
        "scenario_table": table,
        "interpretation_rules": {
            "non_inferiority": "declared only if the 95% CI upper bound for tau < margin and the point estimate is within the margin",
            "superiority_or_harm": "declared only if the 95% CI excludes 0 in the observed direction AND Holm-adjusted exact McNemar p < alpha",
            "otherwise": "INCONCLUSIVE; never reported as equivalence",
            "zero_discordance_rule": "report the exact one-sided bound on the discordance rate rather than a degenerate interval",
        },
        "known_limitations": [
            "Calibration showed ceiling performance at every tested level; the confirmatory design is therefore primarily a precision / non-inferiority design, not a powered superiority test in a non-ceiling regime.",
            "The provider exposes no sampling controls; replicate duplicates measure, but do not control, sampling variance.",
            "Single model route and single provider; no cross-model generalisation is claimed.",
            "The effect, if any, is only identified for zero-query synthetic recovery tasks at the tested observation-complexity levels.",
        ],
    }
    print(json.dumps(report, indent=2))
    if "--out" in sys.argv:
        Path(sys.argv[sys.argv.index("--out") + 1]).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
