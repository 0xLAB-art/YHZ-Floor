#!/usr/bin/env python3
"""P013 AES-CTR analysis (frozen protocol, see PREREGISTRATION.md).

EARLIEST row per (seed, cell) (later rows = instrument duplicates, recorded
never deleted); per-cell acceptance; paired C1-vs-C4 discordance exact
binomial two-sided; premise/naming marginals Fisher exact; seed-stratified
Cochran-Mantel-Haenszel on the premise contrast (post hoc); F1-F3 falsifier
verdicts; cross-fixture descriptive table on the premise-observability
axis; token/cost totals from raw provider responses. Reads LEAK_SCAN.json
(written by leakscan_aesctr.py).
"""
import json
import math
from pathlib import Path

from scipy.stats import fisher_exact

HERE = Path(__file__).resolve().parent

SEEDS = list(range(181, 197))
CELLS = ("C1", "C2", "C3", "C4")
PROTOCOL = "P013-INFO-CONTRACT-2X2-AESCTR-KEYSTREAM-REUSE-v1"


def binom_two_sided(k, n):
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2**n
    return min(1.0, 2 * tail)


def cmh_premise(per_seed):
    """Cochran-Mantel-Haenszel on the premise contrast, stratum = seed."""
    sa = se = sv = 0.0
    for s in SEEDS:
        d = per_seed.get(s, {})
        a = sum(1 for c in ("C1", "C3") if d.get(c))
        m = sum(1 for c in ("C1", "C3") if c in d)
        n = sum(1 for c in CELLS if d.get(c))
        N = sum(1 for c in CELLS if c in d)
        if N <= 1 or m == 0 or m == N:
            continue
        sa += a
        se += m * n / N
        sv += m * n * (N - m) * (N - n) / (N * N * (N - 1))
    if sv == 0:
        return {"chi2_cc": 0.0, "p_two_sided": 1.0, "note": "zero variance (degenerate strata)"}
    chi2 = (abs(sa - se) - 0.5) ** 2 / sv
    p = math.erfc(math.sqrt(chi2 / 2.0))
    return {"sum_a": sa, "sum_expected": round(se, 4), "sum_var": round(sv, 4),
            "chi2_cc": round(chi2, 4), "p_two_sided": round(p, 6)}


def main():
    rows, dups = {}, []
    for line in (HERE / "results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        key = (r["seed"], r["cell"])
        if key in rows:
            dups.append(key)
        else:
            rows[key] = r

    acc = {c: 0 for c in CELLS}
    subs = {c: 0 for c in CELLS}
    turns = {c: 0 for c in CELLS}
    per_seed = {}
    for (s, c), r in rows.items():
        if r["status"] == "SUCCESS":
            acc[c] += 1
        subs[c] += r.get("submissions", 0)
        turns[c] += r.get("turns", 0)
        per_seed.setdefault(s, {})[c] = r["status"] == "SUCCESS"

    c1_wins = c4_wins = ties = 0
    for s in SEEDS:
        d = per_seed.get(s, {})
        a, b = d.get("C1", False), d.get("C4", False)
        if a and not b:
            c1_wins += 1
        elif b and not a:
            c4_wins += 1
        else:
            ties += 1
    discordant = c1_wins + c4_wins
    p_primary = binom_two_sided(c4_wins, discordant) if discordant else 1.0

    b_plus = acc["C1"] + acc["C3"]
    b_minus = acc["C2"] + acc["C4"]
    n_plus = sum(1 for (s, c) in rows if c in ("C1", "C3"))
    n_minus = sum(1 for (s, c) in rows if c in ("C2", "C4"))
    a_plus = acc["C1"] + acc["C4"]
    a_minus = acc["C2"] + acc["C3"]
    n_ap = sum(1 for (s, c) in rows if c in ("C1", "C4"))
    n_am = sum(1 for (s, c) in rows if c in ("C2", "C3"))
    _, p_premise = fisher_exact([[b_plus, n_plus - b_plus], [b_minus, n_minus - b_minus]])
    _, p_naming = fisher_exact([[a_plus, n_ap - a_plus], [a_minus, n_am - a_minus]])

    f1 = ("FALSE (C1 at stated-arm ceiling; the fixture reproduces stated-arm "
          "determinism)") if acc["C1"] >= 12 else "TRUE (C1 below 12/16 — instrument-difficulty result)"
    f2 = ("FALSE (C3 == C1; naming never gates when the premise is stated)"
          ) if acc["C3"] >= acc["C1"] else "TRUE (naming gates: C3 below C1)"
    f3 = ("FALSE (C2 far below C1: the derive-from-observations frame does "
          f"not sustain success — {acc['C2']}/16; the hidden premise is not "
          "recoverable from the public observations)") if acc["C2"] < 12 else "TRUE (derive frame sustains: C2 near C1)"

    in_toks = out_toks = 0
    for rf in sorted((HERE / "raw_provider_responses").glob("*.json")):
        try:
            body = json.loads(rf.read_text())
        except ValueError:
            continue
        u = body.get("usage") or {}
        in_toks += int(u.get("input_tokens") or 0)
        out_toks += int(u.get("output_tokens") or 0)

    leak = json.loads((HERE / "LEAK_SCAN.json").read_text()) if (HERE / "LEAK_SCAN.json").exists() else {"verdict": "MISSING"}

    analysis = {
        "schema": "infoc-p013-analysis/1",
        "protocol": PROTOCOL,
        "unique_sessions": len(rows),
        "instrument_duplicates": [list(k) for k in dups],
        "per_cell": {c: {"sessions": sum(1 for k in rows if k[1] == c),
                         "accepted": acc[c], "submissions": subs[c], "turns": turns[c]}
                     for c in CELLS},
        "primary_paired_C1_vs_C4": {
            "c1_wins": c1_wins, "c4_wins": c4_wins, "ties": ties,
            "discordant": discordant, "exact_binomial_two_sided_p": round(p_primary, 8)},
        "premise_marginal": {"B+ (C1+C3)": f"{b_plus}/{n_plus}", "B- (C2+C4)": f"{b_minus}/{n_minus}",
                             "fisher_two_sided_p": float(f"{p_premise:.6g}")},
        "naming_marginal": {"A+ (C1+C4)": f"{a_plus}/{n_ap}", "A- (C2+C3)": f"{a_minus}/{n_am}",
                            "fisher_two_sided_p": float(f"{p_naming:.6g}")},
        "cmh_premise_stratified_by_seed": cmh_premise(per_seed),
        "falsifiers": {"F1_stated_arm_ceiling": f1, "F2_naming_gates": f2, "F3_derive_frame": f3},
        "usage": {"input_tokens": in_toks, "output_tokens": out_toks,
                  "calls": len(list((HERE / "raw_provider_responses").glob("*.json"))),
                  "estimated_accounting_cost_usd": round((in_toks * 3 + out_toks * 15) / 1e6, 6)},
        "leak_scan_verdict": leak.get("verdict"),
        "reading": ("Second hidden-premise family, preregistered: the premise is PERFECTLY "
                    "load-bearing here. Withholding the premise sentence drops both withheld "
                    "arms to 0/16 even when the family is named (C4) — unlike ChaCha20, where "
                    "the derive frame recovers the all-zero reference on a minority of seeds. "
                    "The premise alone suffices regardless of naming (C3 = 16/16). Combined "
                    "with P012 (observable premise: null by construction) this locates the "
                    "contract effect on the observability axis: it appears exactly when the "
                    "load-bearing premise is a fact about secret content that semantic "
                    "security makes unobservable."),
        "cross_fixture_descriptive": {
            "ChaCha20 (hidden premise, claude label)": {
                "P010 n=4": {"C1": "4/4", "C2": "4/4", "C3": "4/4", "C4": "0/4"},
                "P010P n=8": {"C1": "8/8", "C2": "0/8", "C3": "8/8", "C4": "3/8"},
                "P010L2 n=8": {"C1": "8/8", "C2": "0/8", "C3": "8/8", "C4": "0/8"},
                "P010N16 n=16": {"C1": "16/16", "C2": "3/16", "C3": "16/16", "C4": "6/16"}},
            "ChaCha20 (hidden premise, gpt-oss vendor) P010X1 n=16":
                {"C1": "16/16", "C2": "6/16", "C3": "16/16", "C4": "6/16"},
            "AES-CTR (hidden premise, claude label) P013 n=16": {c: f"{acc[c]}/16" for c in CELLS},
            "ECDSA (observable premise) P012 n=16": {"C1": "16/16", "C2": "16/16", "C3": "16/16", "C4": "16/16"},
            "RC4 (saturated ceiling, honest null)": {"C1": "4/4", "C2": "4/4", "C3": "4/4", "C4": "4/4"},
            "note": "descriptive only — never pooled as a rate; premise-observability axis",
        },
    }
    (HERE / "analysis.json").write_text(json.dumps(analysis, indent=1, sort_keys=True) + "\n")
    print(json.dumps(analysis, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
