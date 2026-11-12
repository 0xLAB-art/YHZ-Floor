#!/usr/bin/env python3
"""P011-L3-N32 analysis — frozen before cohort completion (registered in PREREGISTRATION.md).

Resume rule (P010L3 pattern): analysis keeps the EARLIEST row per (seed, cell).
Terminal provider-failure rows (HTTP_ERROR / TIMEOUT / EMPTY_RESPONSE /
INCOMPLETE_RESPONSE / MALFORMED_PROVIDER_JSON) are counted, never retried,
never imputed, and never converted into oracle outcomes.
Primary test (registered): paired C1-vs-C4 discordance on shared seeds,
exact binomial two-sided, with the pre-specified discordance floor rule
applied against our own interest. Secondary descriptives: premise marginal,
naming marginal, per-seed counts, provider-dropout counts.
No pooled inference across cohorts; P011 stands on its own population.
"""
import json
import math
from math import comb
from math import lgamma
from collections import defaultdict
from pathlib import Path

try:
    from scipy.stats import fisher_exact, binom_test
except Exception:
    fisher_exact = None
    binom_test = None

HERE = Path(__file__).resolve().parent
TERM = {"HTTP_ERROR", "TIMEOUT", "EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
        "MALFORMED_PROVIDER_JSON", "PROVIDER_UNAVAILABLE", "CREDENTIAL_MISSING"}


def load():
    earliest = defaultdict(list)
    for line in (HERE / "results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        key = (rec["seed"], rec["cell"])
        earliest.setdefault(key if False else rec["seed"], []).append(rec)
    # keep earliest per (seed, cell) by file order
    best = {}
    dups = []
    for line in (HERE / "results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        k = (rec["seed"], rec["cell"])
        if k in best:
            dups.append(rec["run_id"])
        else:
            best[k] = rec
    return best, dups


def fisher_2x2(a, b, c, d):
    if fisher_exact is not None:
        return fisher_exact([[a, b], [c, d]], "two-sided")[1]
    n = a + b + c + d
    r1, r2, c1 = a + b, c + d, a + c
    lo, hi = max(0, c1 - r2), min(c1, r1)
    probs = {x: (comb(r1, x) * comb(r2, c1 - x) / comb(n if n else 1, c1))
             for x in range(lo, hi + 1)}
    denom = sum(probs.values())
    # Observed top-left cell is `a`; the table is [[a, b], [c, d]]. Using `c`
    # here returned 0.0 for every degenerate table (e.g. 4/4 vs 4/4, or
    # 28/28 vs 0/10), which invalidated Fisher p-values in P014/P016 reports.
    p_obs = probs.get(a, 0.0)
    tail = sum(v for v in probs.values() if v <= p_obs * (1 + 1e-9))
    return min(1.0, tail / denom if denom else 1.0)


def exact_binomial_two_sided(k, n, p=0.5):
    tail = sum(comb(n, i)*p**i*(1-p)**(n-i)
               for i in range(n+1) if comb(n, i)*p**i*(1-p)**(n-i)
               <= comb(n, k)*p**k*(1-p)**(n-k)*(1+1e-9))
    return min(1.0, tail)


def main():
    best, dups = load()
    accepted = {k: (rec["status"] == "SUCCESS" and rec.get("oracle_verdict") == "accepted")
                for k, rec in best.items() if rec["status"] != "SUCCESS" or True}
    verdict = {}
    drops = defaultdict(list)
    for k, rec in best.items():
        if rec["status"] in TERM:
            drops[k[1]].append(rec["seed"])
            verdict[k] = "PROVIDER_DROP"
        else:
            verdict[k] = 1 if (rec.get("oracle_verdict") == "accepted") else 0
    seeds = sorted({k[0] for k in best})
    cells = sorted({k[1] for k in best})
    marginal = {c: sum(1 for k, v in verdict.items() if k[1] == c and v == 1)
                for c in cells}
    print(f"=== P011-L3-N32 ({len(seeds)} seeds x {len(cells)} cells recorded) ===")
    print("accepts per cell (first-row basis):", marginal)
    print("provider-drop terminal rows by cell:", {c: sorted(s) for c, s in drops.items()})
    if dups:
        print(f"instrument-duplicate rows (flagged, never deleted): {len(dups)}: {dups[:4]} ...")
    # paired discordance on shared seeds (both C1 and C4 evaluable)
    disc = [(verdict[(s, "C1")], verdict[(s, "C4")])
            for s in seeds if (s, "C1") in verdict and (s, "C4") in verdict
            and isinstance(verdict[(s, "C1")], int) and isinstance(verdict[(s, "C4")], int)]
    b10 = sum(1 for a, c in disc if a == 1 and c == 0)
    b01 = sum(1 for a, c in disc if a == 0 and c == 1)
    if b10 + b01:
        p = exact_binomial_two_sided(min(b10, b01), b10 + b01)
        print(f"paired C1-vs-C4 discordance: {b10}/{b01} (n={len(disc)}), exact two-sided p={p:.6g}")
    m = fisher_2x2(marginal.get("C1", 0), len(seeds)-marginal.get("C1", 0)-len(drops.get('C1', [])),
                   marginal.get("C2", 0), len(seeds)-marginal.get("C2", 0)-len(drops.get('C2', [])))
    print(f"premise marginal C1+C3 (stated) vs C2+C4 (withheld) — full grid below at completion")
    stated = marginal.get("C1", 0)+marginal.get("C3", 0)
    withheld = marginal.get("C2", 0)+marginal.get("C4", 0)
    stated_evaluable = 2*len(seeds) - len(drops.get('C1', [])) - len(drops.get('C3', []))
    withheld_evaluable = 2*len(seeds) - len(drops.get('C2', [])) - len(drops.get('C4', []))
    pm = fisher_2x2(stated, withheld, stated_evaluable-stated, withheld_evaluable-withheld)
    print(f"premise marginal {stated}/{stated_evaluable} vs {withheld}/{withheld_evaluable}, Fisher two-sided p={pm:.6g}")


if __name__ == "__main__":
    main()
