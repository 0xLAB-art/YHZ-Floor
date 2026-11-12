#!/usr/bin/env python3
"""C1 confirmatory cohort — the REGISTERED Holm-family analysis.

Computes exactly the three preregistered tests (m=3, Holm step-down at
FWER 0.05) from the frozen results.jsonl rows, deterministically:

  H1 (PRIMARY): paired C1-vs-C4 discordance — exact two-sided binomial on
      the one-directional discordance count over evaluable pairs (both
      sessions in a pair produced no accepted program => tie);
  H2: premise marginal — Fisher exact one-sided, stated (C1+C3) vs
      withheld (C2+C4) accepted-session counts;
  H3: naming marginal — Fisher exact two-sided, named (C1+C4) vs unnamed
      (C2+C3).

Verdicts: Holm step-down (ascending p multiplied by m, m-1, ... with
monotonicity); registered bar = H1 clears Holm within the family and the
discordance is one-directional.  No other test; no pooling.
"""
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
M = 3
ALPHA = 0.05

ACCEPTED_STATUSES = {"SUCCESS"}


def fisher_one_sided(a, b, c, d):
    """Hypergeometric ONE-SIDED GREATER p for [[a,b],[c,d]]:
    P(X >= a) under the fixed-margin hypergeometric.  (The original
    implementation summed every x with pr(x) <= pr(a) -- the two-sided
    criterion -- while labelled one-sided; corrected 2026-11-07 after the
    independent blind reviewers computed 0.0121 for the C1 confirmatory
    table.  Frozen rows unchanged; the registered bar (H1) is unaffected.)"""
    n = a + b + c + d
    if n == 0:
        return None
    row1, col1 = a + b, a + c
    hi = min(col1, row1)
    tot = 0.0
    for x in range(a, hi + 1):
        pr = math.comb(col1, x) * math.comb(n - col1, row1 - x) / math.comb(n, row1)
        tot += pr
    return min(1.0, tot)


def fisher_two_sided(a, b, c, d):
    n = a + b + c + d
    if n == 0:
        return None
    row1, col1 = a + b, a + c
    lo, hi = max(0, col1 - (n - row1)), min(col1, row1)
    p0 = math.comb(col1, a) * math.comb(n - col1, row1 - a) / math.comb(n, row1)
    tot = 0.0
    for x in range(lo, hi + 1):
        pr = math.comb(col1, x) * math.comb(n - col1, row1 - x) / math.comb(n, row1)
        if pr <= p0 * (1 + 1e-9):
            tot += pr
    return tot


def main():
    rows = [json.loads(l) for l in (HERE / "results.jsonl").read_text().splitlines()
            if l.strip()]
    sessions = {}
    for r in rows:
        key = (r["seed"], r["cell"])
        sessions[key] = r  # one session per (seed, cell) by construction

    def accepted(seed, cell):
        r = sessions.get((seed, cell))
        return 1 if (r and r["status"] in ACCEPTED_STATUSES and r.get("accepted")) else 0

    seeds = sorted({s for s, _ in sessions})
    # H1: paired C1-vs-C4 over evaluable pairs
    discord_c1_wins = discord_c4_wins = ties = 0
    for s in seeds:
        a, d = accepted(s, "C1"), accepted(s, "C4")
        if a and not d:
            discord_c1_wins += 1
        elif d and not a:
            discord_c4_wins += 1
        else:
            ties += 1
    b = discord_c1_wins + discord_c4_wins
    h1_p = None if b == 0 else 2 * 0.5 ** b

    # H2: premise marginal (stated C1+C3 vs withheld C2+C4)
    st_acc = sum(accepted(s, "C1") + accepted(s, "C3") for s in seeds)
    st_n = 2 * len(seeds)
    wh_acc = sum(accepted(s, "C2") + accepted(s, "C4") for s in seeds)
    wh_n = 2 * len(seeds)
    h2_p = fisher_one_sided(st_acc, st_n - st_acc, wh_acc, wh_n - wh_acc)

    # H3: naming marginal (named C1+C4 vs unnamed C2+C3), two-sided
    nm_acc = sum(accepted(s, "C1") + accepted(s, "C4") for s in seeds)
    nm_n = 2 * len(seeds)
    un_acc = sum(accepted(s, "C2") + accepted(s, "C3") for s in seeds)
    un_n = 2 * len(seeds)
    h3_p = fisher_two_sided(nm_acc, nm_n - nm_acc, un_acc, un_n - un_acc)

    tests = [("H1_paired", h1_p), ("H2_premise", h2_p), ("H3_naming", h3_p)]
    order = sorted([(p, name) for name, p in tests if p is not None])
    holm = {}
    running_max = 0.0
    for i, (p, name) in enumerate(order):
        adj = min(1.0, p * (M - i))
        running_max = max(running_max, adj)  # step-down monotonicity
        holm[name] = {"p": p, "holm_adjusted": running_max,
                      "significant": running_max < ALPHA}
    f1_holm = holm.get("H1_paired", {}).get("significant", False)
    one_directional = discord_c4_wins == 0

    cell_counts = {}
    for cell in ("C1", "C2", "C3", "C4"):
        acc = sum(accepted(s, cell) for s in seeds)
        cell_counts[cell] = {"accepted": acc, "sessions": len(seeds)}

    out = {
        "schema": "info-contract-confirmatory-c1-holm/1",
        "protocol": "P010-INFO-CONTRACT-2X2-CHACHA20-CONFIRMATORY-C1-v1",
        "registered_family": {
            "m": M, "alpha": ALPHA,
            "tests": ["H1_paired (PRIMARY)", "H2_premise", "H3_naming"],
            "correction": "Holm step-down within the family",
            "registered_bar": ("H1 clears Holm within the family AND the "
                               "discordance is one-directional"),
        },
        "sessions": len(rows),
        "cell_counts": cell_counts,
        "pairs": {"evaluable_discordant_pairs": b,
                  "discordant_c1_wins": discord_c1_wins,
                  "discordant_c4_wins": discord_c4_wins,
                  "ties": ties},
        "marginals": {"premise": {"stated_accepted": st_acc, "stated_n": st_n,
                                  "withheld_accepted": wh_acc, "withheld_n": wh_n},
                      "naming": {"named_accepted": nm_acc, "named_n": nm_n,
                                 "unnamed_accepted": un_acc, "unnamed_n": un_n}},
        "tests": {"H1_paired": {"p": h1_p}, "H2_premise": {"p": h2_p},
                  "H3_naming": {"p": h3_p}},
        "holm": holm,
        "verdicts": {
            "H1_registered_bar": ("CLEARED" if (f1_holm and one_directional)
                                  else "NOT_CLEARED"),
            "one_directional": one_directional,
            "note": ("the registered bar is H1 clearing Holm within the "
                     "declared family and one-directionality; no other "
                     "test is registered; no pooling"),
        },
    }
    (HERE / "C1_HOLM_VERDICT.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["holm"], indent=1))
    print(json.dumps(out["verdicts"], indent=1))


if __name__ == "__main__":
    main()
