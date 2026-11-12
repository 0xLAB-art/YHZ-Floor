#!/usr/bin/env python3
"""P014 (AES-GCM nonce reuse) analysis — frozen before cohort completion,
same rules as analyze_p011.py.

Resume rule: earliest row per (seed, cell). Terminal provider-failure rows are
counted, never retried, never imputed, never converted into oracle outcomes.
Primary test (registered): paired C1-vs-C4 discordance on shared seeds, exact
binomial two-sided, reported with the EVALUABLE-pair denominator. Secondary
descriptives: premise marginal, naming marginal, per-seed counts, provider
dropout by cell. No pooled inference across cohorts; P014 stands alone.
"""
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

# The frozen statistics helpers live with the P011 cohort. Load them by path so
# this script does not depend on cwd or PYTHONPATH: the estimator must be the
# same bytes as the cohort it was frozen against, not a copy that can drift.
_P011 = (Path(__file__).resolve().parents[1]
         / "info_contract_label3_n32_20261101" / "analyze_p011.py")
_spec = importlib.util.spec_from_file_location("_p011_stats", _P011)
_p011 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p011)
exact_binomial_two_sided = _p011.exact_binomial_two_sided
fisher_2x2 = _p011.fisher_2x2

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

    stated, withheld = accepted["C1"] + accepted["C3"], accepted["C2"] + accepted["C4"]
    stated_ev, withheld_ev = evaluable["C1"] + evaluable["C3"], evaluable["C2"] + evaluable["C4"]
    p_premise = fisher_2x2(stated, withheld, stated_ev - stated, withheld_ev - withheld)

    naming_a, naming_b = accepted["C1"] + accepted["C4"], accepted["C2"] + accepted["C3"]
    naming_a_ev, naming_b_ev = evaluable["C1"] + evaluable["C4"], evaluable["C2"] + evaluable["C3"]
    p_naming = fisher_2x2(naming_a, naming_b, naming_a_ev - naming_a, naming_b_ev - naming_b)

    print(f"=== P014 AES-GCM ({len(seeds)} seeds x {len(CELLS)} cells) ===")
    print("accepted / evaluable:", {c: f"{accepted[c]}/{evaluable[c]}" for c in CELLS})
    print("provider drops:", {c: len(drops[c]) for c in CELLS})
    if dups:
        print(f"instrument-duplicate rows: {len(dups)}: {dups[:3]}")
    print(f"paired C1-vs-C4: {b10}/{b01} over {len(pairs)} evaluable pairs, p={p_paired}")
    print(f"premise marginal {stated}/{stated_ev} vs {withheld}/{withheld_ev}, p={p_premise}")
    print(f"naming marginal {naming_a}/{naming_a_ev} vs {naming_b}/{naming_b_ev}, p={p_naming}")


if __name__ == "__main__":
    main()
