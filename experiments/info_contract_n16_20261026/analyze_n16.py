#!/usr/bin/env python3
"""P010N16 leak scan + analysis (frozen protocol, see PREREGISTRATION.md).

1) Leak scan: for seeds 121-136 compute fixture truth with the SAME
   derivation as run_code_feedback_chacha20.instance, then scan every
   prompt file (and every text-readable artifact) for the truth hex.
   Prompts must contain zero hits.
2) Analysis: EARLIEST row per (seed, cell) (later rows = instrument
   duplicates, recorded never deleted); per-cell acceptance; paired
   C1-vs-C4 discordance exact binomial two-sided; premise/naming marginals
   Fisher exact; F1-F3 falsifier verdicts; cross-cohort descriptive table;
   token/cost totals from raw provider responses.
"""
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

from scipy.stats import fisher_exact

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
sys.path.insert(0, str(SRC))
from run_code_feedback_chacha20 import instance  # noqa: E402

SEEDS = list(range(121, 137))
CELLS = ("C1", "C2", "C3", "C4")
PROTOCOL = "P010N16-INFO-CONTRACT-2X2-CHACHA20-N16-v1"


def truth_hex(seed):
    _, truth = instance(seed)
    # truth is the recovered-plaintext bytes held by the oracle
    if isinstance(truth, bytes):
        return truth.hex()
    return truth


def leak_scan():
    secrets = {}
    for s in SEEDS:
        t = truth_hex(seed=s)
        vals = set()
        if isinstance(t, dict):
            for v in t.values():
                if isinstance(v, str):
                    vals.add(v)
        elif isinstance(t, str):
            vals.add(t)
        for v in list(vals):
            if len(v) >= 16:
                secrets[v.lower()] = s
                secrets[v.upper()] = s
                spaced = " ".join(v[i:i + 2] for i in range(0, len(v), 2))
                secrets[spaced] = s
    prompt_hits = []
    prompt_files = sorted((HERE / "prompts").glob("*.txt"))
    for pf in prompt_files:
        text = pf.read_text(errors="replace")
        for sec, s in secrets.items():
            if sec and sec in text:
                prompt_hits.append({"file": pf.name, "seed": s})
    other_hits = []
    for pattern in ("*.json", "*.jsonl"):
        for jf in sorted(HERE.glob(pattern)):
            if jf.name in ("LEAK_SCAN.json",):
                continue
            text = jf.read_text(errors="replace")
            for sec, s in secrets.items():
                if sec and sec in text:
                    other_hits.append({"file": jf.name, "seed": s})
    result = {
        "schema": "infoc-n16-leakscan/1",
        "protocol": PROTOCOL,
        "seeds": SEEDS,
        "prompt_files": len(prompt_files),
        "prompt_hits": len(prompt_hits),
        "prompt_hit_detail": prompt_hits[:10],
        "other_json_hits": len(other_hits),
        "other_json_hit_detail": other_hits[:10],
        "verdict": "PASS" if not prompt_hits else "FAIL",
        "note": "execution_captures excluded by design (accepted-program stdout may echo the recovered plaintext)",
    }
    (HERE / "LEAK_SCAN.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    return result


def load_earliest():
    rows = {}
    dups = []
    for line in (HERE / "results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        key = (r["seed"], r["cell"])
        if key in rows:
            dups.append(key)
        else:
            rows[key] = r
    return rows, dups


def binom_two_sided(k, n):
    # exact two-sided (symmetric p=0.5): 2 * P(X <= min(k, n-k)), capped at 1
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2**n
    return min(1.0, 2 * tail)


def main():
    leak = leak_scan()
    rows, dups = load_earliest()
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

    # primary: paired C1-vs-C4 discordance on shared seeds
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
    # exact two-sided sign test on the discordant pairs (p = 0.5)
    p_primary = binom_two_sided(c4_wins, discordant) if discordant else 1.0

    # marginals
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

    # falsifiers
    f1 = "FALSE" if discordant > 4 and c1_wins > c4_wins else ("OPEN" if discordant > 4 else "INCONCLUSIVE(discordance<=4)")
    f2 = "TRUE (naming gates)" if acc["C3"] < acc["C1"] else "FALSE (C3 == C1)"
    f3 = "TRUE (derive frame sustains)" if acc["C2"] >= 12 else f"FALSE (C2 {acc['C2']}/16 far below C1)"

    # cost totals from raw responses
    in_toks = out_toks = 0
    for rf in sorted((HERE / "raw_provider_responses").glob("*.json")):
        try:
            body = json.loads(rf.read_text())
        except ValueError:
            continue
        u = body.get("usage") or {}
        in_toks += int(u.get("input_tokens") or 0)
        out_toks += int(u.get("output_tokens") or 0)

    analysis = {
        "schema": "infoc-n16-analysis/1",
        "protocol": PROTOCOL,
        "unique_sessions": len(rows),
        "instrument_duplicates": [list(k) for k in dups],
        "per_cell": {c: {"sessions": sum(1 for k in rows if k[1] == c),
                         "accepted": acc[c], "submissions": subs[c], "turns": turns[c]}
                     for c in CELLS},
        "primary_paired_C1_vs_C4": {
            "c1_wins": c1_wins, "c4_wins": c4_wins, "ties": ties,
            "discordant": discordant, "exact_binomial_two_sided_p": round(p_primary, 6)},
        "premise_marginal": {"B+ (C1+C3)": f"{b_plus}/{n_plus}", "B- (C2+C4)": f"{b_minus}/{n_minus}",
                             "fisher_two_sided_p": float(f"{p_premise:.6g}")},
        "naming_marginal": {"A+ (C1+C4)": f"{a_plus}/{n_ap}", "A- (C2+C3)": f"{a_minus}/{n_am}",
                            "fisher_two_sided_p": float(f"{p_naming:.6g}")},
        "falsifiers": {"F1_honest_null": f1, "F2_naming_gates": f2, "F3_derive_frame": f3},
        "usage": {"input_tokens": in_toks, "output_tokens": out_toks,
                  "calls": len(list((HERE / "raw_provider_responses").glob("*.json"))),
                  "estimated_accounting_cost_usd": round((in_toks * 3 + out_toks * 15) / 1e6, 6)},
        "leak_scan_verdict": leak["verdict"],
        "cross_cohort_descriptive": {
            "P010 n=4": {"C1": "4/4", "C2": "4/4", "C3": "4/4", "C4": "0/4"},
            "P010P n=8": {"C1": "8/8", "C2": "0/8", "C3": "8/8", "C4": "3/8"},
            "P010L2 n=8": {"C1": "8/8", "C2": "0/8", "C3": "8/8", "C4": "0/8"},
            "driftcheck n=4 (post-hoc)": {"C1": "4/4", "C2": "2/4", "C3": "4/4", "C4": "2/4"},
            "P010N16 n=16": {c: f"{acc[c]}/16" for c in CELLS},
            "note": "descriptive only — never pooled as a rate",
        },
    }
    (HERE / "analysis.json").write_text(json.dumps(analysis, indent=1, sort_keys=True) + "\n")
    print(json.dumps(analysis, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
