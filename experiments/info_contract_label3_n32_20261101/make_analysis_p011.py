#!/usr/bin/env python3
"""Emit ANALYSIS.json for P011-INFO-CONTRACT-2X2-CHACHA20-LABEL3-N32-v1.

Read-only over results.jsonl. Rules are identical to analyze_p011.py, which was
frozen before the cohort completed: earliest row per (seed, cell); terminal
provider-failure rows are counted, never retried, never imputed, and never
converted into oracle outcomes; no pooling with any other cohort.

This file only serialises those rules to JSON. It does not re-derive them.
"""
import json
from collections import defaultdict
from pathlib import Path

from analyze_p011 import exact_binomial_two_sided, fisher_2x2

HERE = Path(__file__).resolve().parent
TERM = {"HTTP_ERROR", "TIMEOUT", "EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
        "MALFORMED_PROVIDER_JSON", "PROVIDER_UNAVAILABLE", "CREDENTIAL_MISSING"}

CELLS = ("C1", "C2", "C3", "C4")


def main():
    best, dups = {}, []
    for line in (HERE / "results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        key = (rec["seed"], rec["cell"])
        if key in best:
            dups.append(rec["run_id"])
        else:
            best[key] = rec

    verdict, drops = {}, defaultdict(list)
    for key, rec in best.items():
        if rec["status"] in TERM:
            verdict[key] = "PROVIDER_DROP"
            drops[key[1]].append(key[0])
        else:
            verdict[key] = 1 if rec.get("oracle_verdict") == "accepted" else 0

    seeds = sorted({k[0] for k in best})
    accepted = {c: sum(1 for k, v in verdict.items() if k[1] == c and v == 1) for c in CELLS}
    evaluable = {c: sum(1 for k, v in verdict.items() if k[1] == c and isinstance(v, int)) for c in CELLS}

    pairs = [(verdict[(s, "C1")], verdict[(s, "C4")]) for s in seeds
             if isinstance(verdict.get((s, "C1")), int) and isinstance(verdict.get((s, "C4")), int)]
    b10 = sum(1 for a, c in pairs if a == 1 and c == 0)
    b01 = sum(1 for a, c in pairs if a == 0 and c == 1)
    p_paired = exact_binomial_two_sided(min(b10, b01), b10 + b01) if (b10 + b01) else None

    stated = accepted["C1"] + accepted["C3"]
    withheld = accepted["C2"] + accepted["C4"]
    stated_ev = evaluable["C1"] + evaluable["C3"]
    withheld_ev = evaluable["C2"] + evaluable["C4"]
    p_premise = fisher_2x2(stated, withheld, stated_ev - stated, withheld_ev - withheld)

    out = {
        "protocol": "P011-INFO-CONTRACT-2X2-CHACHA20-LABEL3-N32-v1",
        "preregistered": True,
        "confirmatory": False,
        "namespace": HERE.name,
        "seeds": {"first": seeds[0], "last": seeds[-1], "count": len(seeds)},
        "sessions_recorded": len(best),
        "per_cell": {c: {"accepted": accepted[c], "evaluable": evaluable[c],
                         "provider_drops": len(drops[c]),
                         "drop_seeds": sorted(drops[c])} for c in CELLS},
        "paired_primary": {"test": "exact binomial two-sided, C1 vs C4 on shared seeds",
                           "discordant_c1_only": b10, "discordant_c4_only": b01,
                           "evaluable_pairs": len(pairs), "p_two_sided": p_paired},
        "premise_marginal": {"stated": stated, "stated_evaluable": stated_ev,
                             "withheld": withheld, "withheld_evaluable": withheld_ev,
                             "test": "Fisher exact two-sided", "p_two_sided": p_premise},
        "provider_dropout": {"terminal_rows": sum(len(v) for v in drops.values()),
                             "share_of_registered": round(sum(len(v) for v in drops.values()) / (4 * len(seeds)), 4)},
        "instrument_duplicate_rows": {"count": len(dups), "run_ids": dups},
        "interpretation": (
            "Registered scale-up of P010L3 from n=8 to n=32 per cell on the same "
            "frozen methodology. Mechanism identification only: not a capability "
            "rate estimate, not pooled with any other cohort. The stated arm is "
            "not deterministic at this size (C1 27/32, C3 30/32); the paired "
            "contrast and the premise marginal stand on their own population."
        ),
        "corrections": [
            "Fisher p printed by analyze_p011.py as 0 is floating-point underflow; "
            "recorded here as the returned value with that caveat, not as an exact p."
        ],
    }
    (HERE / "ANALYSIS.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out["per_cell"], indent=1, sort_keys=True))
    print("paired:", b10, "/", b01, "p=", p_paired, "| premise p=", p_premise)


if __name__ == "__main__":
    main()
