#!/usr/bin/env python3
"""P010L3 analysis — third-label information-contract 2x2.

Reads this namespace's own results.jsonl (earliest row per (seed, cell),
instrument duplicates flagged), asserts the frozen session count, and emits
ANALYSIS.json with the same statistics the paper reports for the earlier
cohorts: per-cell acceptances, premise and naming marginals (exact Fisher), the
seed-paired C1-versus-C4 discordance (exact binomial), and a seed-stratified
Cochran-Mantel-Haenszel test. No pooling with any other cohort.
"""

import json
import pathlib
from collections import Counter, defaultdict

from scipy.stats import binomtest, fisher_exact

HERE = pathlib.Path(__file__).resolve().parent
CELLS = ("C1", "C2", "C3", "C4")
SEEDS = tuple(range(201, 209))


def cmh(strata):
    """Cochran-Mantel-Haenszel statistic, 1 df, uncorrected.

    Each stratum is the 2x2 [[accepted_stated, rejected_stated],
    [accepted_withheld, rejected_withheld]] for one seed. The uncorrected form
    is what the earlier cohorts report (P010L2 reads chi2=24.0, p=9.6e-7), so
    the same statistic is used here for comparability; the continuity-corrected
    variant is not reported.
    """
    num = var_sum = 0.0
    strata_used = 0
    for a, b, c, d in strata:
        n = a + b + c + d
        if n < 2:
            continue
        num += a - (a + b) * (a + c) / n
        var_sum += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
        strata_used += 1
    if var_sum == 0:
        return {"chi2": None, "p": None, "strata": strata_used,
                "note": "degenerate variance — no discordance in any stratum"}
    chi2 = num * num / var_sum
    from scipy.stats import chi2 as chi2_dist
    return {"chi2": round(chi2, 2), "p": float(chi2_dist.sf(chi2, 1)),
            "strata": strata_used, "observed_minus_expected": round(num, 3),
            "continuity_correction": False}


def main():
    rows, seen, duplicates = [], set(), []
    for line in (HERE / "results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        key = (r["seed"], r["cell"])
        if key in seen:
            duplicates.append(key)          # instrument duplicate, never deleted
            continue
        seen.add(key)
        rows.append(r)

    cells = {c: [r for r in rows if r["cell"] == c] for c in CELLS}
    accepted = {c: sum(1 for r in cells[c] if r["status"] == "SUCCESS") for c in CELLS}
    submissions = {c: sum(r["submissions"] for r in cells[c]) for c in CELLS}
    turns = {c: sum(r["turns"] for r in cells[c]) for c in CELLS}
    n_per_cell = {c: len(cells[c]) for c in CELLS}

    # premise marginal: stated = C1 + C3, withheld = C2 + C4
    stated = accepted["C1"] + accepted["C3"]
    withheld = accepted["C2"] + accepted["C4"]
    n_stated = n_per_cell["C1"] + n_per_cell["C3"]
    n_withheld = n_per_cell["C2"] + n_per_cell["C4"]
    fisher2 = fisher_exact([[stated, n_stated - stated],
                            [withheld, n_withheld - withheld]], alternative="two-sided")
    fisher1 = fisher_exact([[stated, n_stated - stated],
                            [withheld, n_withheld - withheld]], alternative="greater")
    # naming marginal: named = C1 + C4, withheld = C2 + C3
    named = accepted["C1"] + accepted["C4"]
    unnamed = accepted["C2"] + accepted["C3"]
    n_named = n_per_cell["C1"] + n_per_cell["C4"]
    n_unnamed = n_per_cell["C2"] + n_per_cell["C3"]
    naming2 = fisher_exact([[named, n_named - named],
                            [unnamed, n_unnamed - unnamed]], alternative="two-sided")

    # seed-paired C1 vs C4 discordance
    c1 = {(r["seed"]): r["status"] == "SUCCESS" for r in cells["C1"]}
    c4 = {(r["seed"]): r["status"] == "SUCCESS" for r in cells["C4"]}
    seeds = sorted(set(c1) & set(c4))
    only_c1 = sum(1 for s in seeds if c1[s] and not c4[s])
    only_c4 = sum(1 for s in seeds if c4[s] and not c1[s])
    ties = len(seeds) - only_c1 - only_c4
    paired = binomtest(only_c1, only_c1 + only_c4, 0.5, alternative="two-sided") \
        if only_c1 + only_c4 else None

    # seed-stratified CMH on the premise marginal (stated vs withheld within seed)
    strata = []
    for s in sorted({r["seed"] for r in rows}):
        def pick(cell):
            got = [r for r in cells[cell] if r["seed"] == s]
            return (got[0]["status"] == "SUCCESS") if got else None
        vals = {c: pick(c) for c in CELLS}
        if any(v is None for v in vals.values()):
            continue
        acc_stated = sum(1 for c in ("C1", "C3") if vals[c])
        rej_stated = 2 - acc_stated
        acc_withheld = sum(1 for c in ("C2", "C4") if vals[c])
        rej_withheld = 2 - acc_withheld
        strata.append((acc_stated, rej_stated, acc_withheld, rej_withheld))
    cmh_res = cmh(strata)

    first_turn = {c: sum(1 for r in cells[c]
                         if r["status"] == "SUCCESS" and r["turns"] == 1)
                  for c in CELLS}
    out = {
        "protocol": rows[0]["protocol"] if rows else None,
        "sessions": len(rows),
        "expected_sessions": 32,
        "instrument_duplicates": duplicates,
        "n_per_cell": n_per_cell,
        "accepted": accepted,
        "accepted_first_turn": first_turn,
        "submissions": submissions,
        "turns": turns,
        "status_counts": dict(Counter(r["status"] for r in rows)),
        "provider_failures": sum(r["provider_failures"] for r in rows),
        "premise_marginal": {"stated": stated, "n_stated": n_stated,
                             "withheld": withheld, "n_withheld": n_withheld,
                             "fisher_one_sided_p": float(fisher1.pvalue),
                             "fisher_two_sided_p": float(fisher2.pvalue),
                             "odds_ratio": None if fisher2.statistic == float("inf")
                             else float(fisher2.statistic)},
        "naming_marginal": {"named": named, "n_named": n_named,
                            "unnamed": unnamed, "n_unnamed": n_unnamed,
                            "fisher_two_sided_p": float(naming2.pvalue)},
        "paired_c1_vs_c4": {"seeds": seeds, "only_c1": only_c1,
                            "only_c4": only_c4, "ties": ties,
                            "binom_two_sided_p": None if paired is None
                            else float(paired.pvalue)},
        "premise_cmh": cmh_res,
        "complete": len(rows) == 32 and all(n_per_cell[c] == 8 for c in CELLS),
        "pooling": "none — this cohort stands alone; cross-label counts are descriptive",
    }
    (HERE / "ANALYSIS.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
