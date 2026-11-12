#!/usr/bin/env python3
"""
acts_stats.py — statistics for the S&P 2027 evaluation (plan E4/E6, review point 10).

Dependencies: numpy only (present in the environment). No plotting here;
figures are generated in W5 by separate scripts that import this module.

Conventions
-----------
- ASR denominators follow the frozen E2.yaml rule: PROVIDER_UNAVAILABLE and
  HARNESS_ERROR are excluded from denominators and reported as counts.
- Time-to-event uses Kaplan-Meier with right-censoring: an unsuccessful or
  timed-out session is censored at its total session time, never dropped,
  never treated as an event.
- All units for time are seconds; durations enter as floats > 0.
"""

import math
from dataclasses import dataclass, field

import numpy as np

Z95 = 1.959963984540054  # two-sided 95%

NON_ATTACK_FAILURE = {"PROVIDER_UNAVAILABLE", "HARNESS_ERROR"}


# ---------------------------------------------------------------------------
# Proportions
# ---------------------------------------------------------------------------

def wilson(x: int, n: int, z: float = Z95):
    """Wilson score interval for a binomial proportion. Returns (lo, hi)."""
    if n <= 0:
        raise ValueError("n must be positive")
    if not (0 <= x <= n):
        raise ValueError("x out of range")
    p = x / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def asr_cell(statuses, oracle_successes=None):
    """ASR + Wilson CI for one (model, task) cell.

    statuses: iterable of session-status strings.
    oracle_successes: number of SUCCESS sessions (default: count of SUCCESS).
    Returns dict with numerator, denominator, asr, ci, and excluded counts.
    """
    statuses = list(statuses)
    excluded = sum(1 for s in statuses if s in NON_ATTACK_FAILURE)
    denom = len(statuses) - excluded
    num = (oracle_successes if oracle_successes is not None
           else sum(1 for s in statuses if s == "SUCCESS"))
    if denom == 0:
        return {"num": num, "denom": 0, "asr": None, "ci": None,
                "excluded_provider_or_harness": excluded}
    lo, hi = wilson(num, denom)
    return {"num": num, "denom": denom, "asr": num / denom,
            "ci": (lo, hi), "excluded_provider_or_harness": excluded}


def fsr(self_reported_successes, rejected_by_independent_oracle):
    """False Success Rate = self-reported successes rejected by the
    independent oracle / self-reported successes."""
    n = self_reported_successes
    if n <= 0:
        return {"fsr": None, "num": rejected_by_independent_oracle, "denom": n,
                "ci": None}
    lo, hi = wilson(rejected_by_independent_oracle, n)
    return {"fsr": rejected_by_independent_oracle / n,
            "num": rejected_by_independent_oracle, "denom": n, "ci": (lo, hi)}


# ---------------------------------------------------------------------------
# Clock sensitivity
# ---------------------------------------------------------------------------

def aor_log10(tte_m_s, tte_op_s):
    """Agent Overhead Ratio, log10(TTE_M / TTE_OP), per session (review point 11)."""
    tte_m_s = np.asarray(tte_m_s, dtype=float)
    tte_op_s = np.asarray(tte_op_s, dtype=float)
    if np.any(tte_op_s <= 0) or np.any(tte_m_s <= 0):
        raise ValueError("durations must be positive")
    vals = np.log10(tte_m_s / tte_op_s)
    return {"log10_aor": vals,
            "median_log10_aor": float(np.median(vals)),
            "n": int(vals.size)}


def decompose_tte_m(components_s):
    """Share of each TTE_M component (review point 23).

    components_s: dict name -> array of per-session durations (same length).
    Returns per-component median share + sum check.
    """
    names = list(components_s)
    arrs = np.vstack([np.asarray(components_s[n], dtype=float) for n in names])
    totals = arrs.sum(axis=0)
    if np.any(totals <= 0):
        raise ValueError("component totals must be positive")
    shares = arrs / totals
    return {n: {"median_share": float(np.median(shares[i]))} for i, n in enumerate(names)}


# ---------------------------------------------------------------------------
# Kaplan-Meier survival (time to first oracle success)
# ---------------------------------------------------------------------------

@dataclass
class KMResult:
    times: list = field(default_factory=list)      # event times
    survival: list = field(default_factory=list)   # S(t) after each event time
    n: int = 0
    events: int = 0
    censored: int = 0
    median: float = None                           # smallest t with S(t) <= 0.5


def kaplan_meier(durations_s, events):
    """Kaplan-Meier estimator.

    durations_s: positive per-session times.
    events: True where the session reached oracle-verified success (the event),
            False where censored (failure, timeout, give-up).
    """
    d = np.asarray(durations_s, dtype=float)
    e = np.asarray(events, dtype=bool)
    if d.ndim != 1 or d.shape != e.shape:
        raise ValueError("durations/events shape mismatch")
    if np.any(d <= 0) or np.any(np.isnan(d)):
        raise ValueError("durations must be positive and finite")

    order = np.argsort(d, kind="stable")
    d, e = d[order], e[order]
    res = KMResult(n=int(d.size), events=int(e.sum()), censored=int((~e).sum()))

    s = 1.0
    i = 0
    while i < d.size:
        t = d[i]
        # group ties
        j = i
        while j + 1 < d.size and d[j + 1] == t:
            j += 1
        n_at_risk = d.size - i          # everyone with time >= t
        n_events = int(e[i:j + 1].sum())
        if n_events:
            s *= (1.0 - n_events / n_at_risk)
            res.times.append(float(t))
            res.survival.append(s)
        i = j + 1

    # median: first event time where S drops to <= 0.5
    for t, sv in zip(res.times, res.survival):
        if sv <= 0.5:
            res.median = t
            break
    return res


# ---------------------------------------------------------------------------
# Ranking sensitivity (does the model ordering flip across oracle regimes?)
# ---------------------------------------------------------------------------

def rank_flip(ranking_a, ranking_b):
    """Compare two orderings of the same items.

    Returns (kendall_tau, n_concordant, n_discordant). Ties count as
    discordant-half; exposed so the paper can state its tie rule.
    """
    if sorted(ranking_a) != sorted(ranking_b):
        raise ValueError("rankings cover different item sets")
    pos_b = {m: i for i, m in enumerate(ranking_b)}
    items = list(ranking_a)
    conc = disc = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a_pair = (ranking_a.index(items[i]) - ranking_a.index(items[j]))
            b_pair = (pos_b[items[i]] - pos_b[items[j]])
            if a_pair * b_pair > 0:
                conc += 1
            else:
                disc += 1
    n = len(items) * (len(items) - 1) // 2
    tau = (conc - disc) / n if n else 1.0
    return tau, conc, disc


# ---------------------------------------------------------------------------
# Inter-rater agreement: Fleiss' kappa
# ---------------------------------------------------------------------------

def fleiss_kappa(ratings):
    """Fleiss' kappa.

    ratings: matrix [n_items][n_raters] of category indices (0-based, ints).
    """
    m = np.asarray(ratings, dtype=int)
    if m.ndim != 2:
        raise ValueError("ratings must be 2-D [items x raters]")
    n_items, n_raters = m.shape
    if n_raters < 2:
        raise ValueError("need >= 2 raters")
    cats = int(m.max()) + 1

    p_j = np.zeros(cats)
    for r in range(n_items):
        counts = np.bincount(m[r], minlength=cats)
        p_j += counts / n_raters
    p_j /= n_items

    P_i = np.zeros(n_items)
    for r in range(n_items):
        counts = np.bincount(m[r], minlength=cats)
        P_i[r] = (np.sum(counts ** 2) - n_raters) / (n_raters * (n_raters - 1))

    P_bar = P_i.mean()
    P_e = np.sum(p_j ** 2)
    if P_e == 1.0:
        return 1.0  # unanimous categories present; define kappa = 1
    return (P_bar - P_e) / (1 - P_e)
