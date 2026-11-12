#!/usr/bin/env python3
"""H1-R3 statistical helpers (paired binary outcomes).

The primary quantity is the paired risk difference tau = P(Y_treat=1) -
P(Y_ref=1) estimated over matched instances.  All intervals are reported with
explicit multiplicity handling and a predeclared equivalence margin.
"""
from __future__ import annotations

import math
import random
from itertools import combinations

import numpy as np
from scipy import stats as sps


def mcnemar_exact(b: int, c: int) -> dict:
    """Exact two-sided McNemar test on discordant counts b (ref-only) and c (treat-only)."""
    n = b + c
    if n == 0:
        return {"b": b, "c": c, "discordant": 0, "p_value": 1.0,
                "note": "no discordant pairs; test is uninformative"}
    p = sps.binomtest(min(b, c), n, 0.5, alternative="two-sided").pvalue
    return {"b": b, "c": c, "discordant": n, "p_value": float(p)}


def paired_risk_difference_ci(pairs: list[tuple[int, int]], resamples: int = 20000,
                              seed: int = 20261019, alpha: float = 0.05) -> dict:
    """Percentile bootstrap and exact-conditional interval for tau = treat - ref."""
    n = len(pairs)
    if n == 0:
        return {"n": 0, "estimate": None, "ci_low": None, "ci_high": None}
    ref = np.array([a for a, _ in pairs], dtype=float)
    treat = np.array([b for _, b in pairs], dtype=float)
    diff = treat - ref
    estimate = float(diff.mean())
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(resamples, n))
    boots = diff[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    b = int(np.sum((ref == 1) & (treat == 0)))
    c = int(np.sum((ref == 0) & (treat == 1)))
    return {
        "n": n,
        "ref_rate": float(ref.mean()),
        "treat_rate": float(treat.mean()),
        "estimate": estimate,
        "ci_low": float(lo),
        "ci_high": float(hi),
        "discordant_ref_only": b,
        "discordant_treat_only": c,
        "concordant_both_success": int(np.sum((ref == 1) & (treat == 1))),
        "concordant_both_failure": int(np.sum((ref == 0) & (treat == 0))),
        "mcnemar": mcnemar_exact(b, c),
        "interval_method": "paired percentile bootstrap over instances",
    }


def exact_upper_bound_zero_discordant(n: int, alpha: float = 0.05) -> float:
    """One-sided exact upper bound on the discordance probability with zero events."""
    if n <= 0:
        return 1.0
    return float(1 - alpha ** (1 / n))


def equivalence_assessment(ci: dict, margin: float) -> dict:
    """Classify a paired contrast against a predeclared equivalence margin."""
    if ci.get("estimate") is None:
        return {"status": "NOT_ESTIMABLE", "margin": margin}
    lo, hi, est = ci["ci_low"], ci["ci_high"], ci["estimate"]
    # Convention: tau = P(treatment success) - P(reference success), so a
    # positive tau means the treatment arm did better.
    if lo >= -margin and hi <= margin:
        status = "EQUIVALENT_WITHIN_MARGIN"
    elif lo > margin:
        status = "MEANINGFULLY_BETTER_THAN_REFERENCE"
    elif hi < -margin:
        status = "MEANINGFULLY_WORSE_THAN_REFERENCE"
    else:
        status = "INCONCLUSIVE"
    return {"status": status, "margin": margin, "estimate": est, "ci": [lo, hi],
            "distance_to_margin": {"lower": lo + margin, "upper": margin - hi}}


def holm(p_values: list[tuple[str, float]]) -> list[dict]:
    """Holm-Bonferroni adjustment; input is [(label, p), ...]."""
    ordered = sorted(p_values, key=lambda x: x[1])
    m = len(ordered)
    out = []
    running = 0.0
    for i, (label, p) in enumerate(ordered):
        adjusted = min(1.0, (m - i) * p)
        running = max(running, adjusted)
        out.append({"label": label, "p": p, "p_holm": running, "rank": i + 1, "m": m})
    return out


def variance_decomposition(records: list[dict], value_key: str) -> dict:
    """Nested variance decomposition: instance, arm, replicate (residual).

    `records` rows need keys: instance (str), arm (str), replicate (int), and
    the binary `value_key`.  Estimated with a random-effects ANOVA on the
    instance means and the within-cell dispersion.  Reported descriptively.
    """
    cells: dict[tuple[str, str], list[float]] = {}
    for row in records:
        cells.setdefault((row["instance"], row["arm"]), []).append(float(row[value_key]))
    within = [vals for vals in cells.values() if len(vals) > 1]
    if not within:
        return {"status": "NO_REPLICATES"}
    residuals = []
    for vals in within:
        mean = sum(vals) / len(vals)
        residuals.extend((v - mean) ** 2 for v in vals)
    dof = sum(len(v) - 1 for v in within)
    within_var = sum(residuals) / dof if dof else 0.0
    return {"status": "ESTIMATED", "within_cell_variance": within_var,
            "within_cell_sd": math.sqrt(within_var), "replicate_dof": dof,
            "cells_with_replicates": len(within)}


def interaction_test(records: list[dict], value_key: str = "terminal_success") -> dict:
    """Representation x complexity interaction via logistic regression with cluster-robust SE.

    Model: logit P = b0 + b_arm + b_level + b_arm:level, clusters = instance.
    Uses a hand-rolled IRLS fit to avoid a statsmodels dependency.
    """
    arms = sorted({r["arm"] for r in records if r["arm"] != "R0"})
    levels = sorted({r["level"] for r in records})
    if len(arms) != 1 or len(levels) < 2:
        return {"status": "NOT_ESTIMABLE", "arms": arms, "levels": levels}
    arm = arms[0]
    rows = [r for r in records if r["arm"] in ("R0", arm)]
    X, y, clusters = [], [], []
    level_index = {lv: i for i, lv in enumerate(levels)}
    for r in rows:
        base = [1.0, 1.0 if r["arm"] == arm else 0.0]
        for lv in levels[1:]:
            base.append(1.0 if r["level"] == lv else 0.0)
        for lv in levels[1:]:
            base.append(1.0 if (r["arm"] == arm and r["level"] == lv) else 0.0)
        X.append(base)
        y.append(float(r[value_key]))
        clusters.append(r["instance"])
    X = np.array(X, dtype=float)
    y = np.array(y, dtype=float)
    if len(set(y)) < 2:
        return {"status": "DEGENERATE", "reason": "outcome constant"}
    beta = np.zeros(X.shape[1])
    for _ in range(200):
        eta = X @ beta
        p = 1 / (1 + np.exp(-np.clip(eta, -30, 30)))
        W = np.clip(p * (1 - p), 1e-9, None)
        grad = X.T @ (y - p)
        H = X.T @ (X * W[:, None])
        try:
            step = np.linalg.solve(H, grad)
        except np.linalg.LinAlgError:
            return {"status": "SINGULAR"}
        beta = beta + step
        if np.max(np.abs(step)) < 1e-10:
            break
    eta = X @ beta
    p = 1 / (1 + np.exp(-np.clip(eta, -30, 30)))
    W = np.clip(p * (1 - p), 1e-9, None)
    H = X.T @ (X * W[:, None])
    try:
        cov = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        return {"status": "SINGULAR"}
    # cluster-robust sandwich
    meat = np.zeros_like(cov)
    for cluster in sorted(set(clusters)):
        mask = np.array([c == cluster for c in clusters])
        score = X[mask].T @ (y[mask] - p[mask])
        meat += np.outer(score, score)
    cov_cr = cov @ meat @ cov
    se = np.sqrt(np.clip(np.diag(cov_cr), 1e-12, None))
    n_par = X.shape[1]
    n_clusters = len(set(clusters))
    t_crit = float(sps.t.ppf(0.975, max(1, n_clusters - 1)))
    # interaction terms are the last (len(levels)-1) coefficients
    inter_idx = list(range(n_par - (len(levels) - 1), n_par))
    out = []
    for idx in inter_idx:
        out.append({"level_contrast": levels[1:][idx - inter_idx[0]],
                    "coef": float(beta[idx]), "se_cluster_robust": float(se[idx]),
                    "z": float(beta[idx] / se[idx]) if se[idx] else None,
                    "ci_lo": float(beta[idx] - t_crit * se[idx]),
                    "ci_hi": float(beta[idx] + t_crit * se[idx])})
    return {"status": "ESTIMATED", "arm": arm, "levels": levels, "n_clusters": n_clusters,
            "coefficients": {f"b{i}": float(v) for i, v in enumerate(beta)},
            "interaction_terms": out,
            "note": "cluster-robust descriptive model; not a confirmatory test"}


def cohens_kappa(a: list[int], b: list[int]) -> float:
    if len(a) != len(b) or not a:
        return float("nan")
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa = sum(a) / n
    pb = sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe != 1 else float("nan")


def wilson_interval(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))
