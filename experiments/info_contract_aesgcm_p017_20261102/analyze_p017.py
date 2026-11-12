#!/usr/bin/env python3
"""P017 analysis — frozen before the cohort runs.

Adds an ATTRIBUTION endpoint to the P014 estimator, because that is this
cohort's purpose: was P014's withheld-arm dropout a budget artefact?

Prespecified decision rule (PREREGISTRATION.md §4, rule A1), applied as written:

  max withheld-cell dropout <= 2          -> BUDGET_EXPLAINS
  3 .. 7                                  -> PARTIAL_BUDGET
  >= 8 in either withheld cell            -> BUDGET_HYPOTHESIS_FAILS

Acceptance is reported separately and never merged into that verdict: if any
withheld session is accepted, P014's conclusion is revised rather than defended.

Keeps the P014 rules unchanged: earliest row per (seed, cell); terminal
provider-failure rows are counted, never retried, never imputed, never turned
into oracle outcomes; paired C1-vs-C4 on EVALUABLE pairs only.
"""
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TERM = {"HTTP_ERROR", "TIMEOUT", "EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
        "MALFORMED_PROVIDER_JSON", "PROVIDER_UNAVAILABLE", "CREDENTIAL_MISSING"}
CELLS = ("C1", "C2", "C3", "C4")

# frozen estimator helpers, loaded by path (same bytes as the P011/P014 cohorts)
_P011 = (HERE.parent / "info_contract_label3_n32_20261101" / "analyze_p011.py")
_spec = importlib.util.spec_from_file_location("_p011_stats", _P011)
_p011 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p011)
fisher_2x2 = _p011.fisher_2x2


def attribution(max_withheld_drops):
    if max_withheld_drops <= 2:
        return "BUDGET_EXPLAINS"
    if max_withheld_drops <= 7:
        return "PARTIAL_BUDGET"
    return "BUDGET_HYPOTHESIS_FAILS"


def main():
    if not (HERE / "results.jsonl").exists():
        print("P017: no results.jsonl in this namespace — cohort did not start or wrote nothing.")
        print("This is a null artefact, not a result: nothing was measured.")
        return
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
    acc = {c: sum(1 for k, v in verdict.items() if k[1] == c and v == 1) for c in CELLS}
    ev = {c: sum(1 for k, v in verdict.items() if k[1] == c and isinstance(v, int)) for c in CELLS}

    pairs = [(verdict[(s, "C1")], verdict[(s, "C4")]) for s in seeds
             if isinstance(verdict.get((s, "C1")), int) and isinstance(verdict.get((s, "C4")), int)]
    b10 = sum(1 for a, c in pairs if a == 1 and c == 0)
    b01 = sum(1 for a, c in pairs if a == 0 and c == 1)
    p_paired = _p011.exact_binomial_two_sided(min(b10, b01), b10 + b01) if (b10 + b01) else None

    stated, withheld = acc["C1"] + acc["C3"], acc["C2"] + acc["C4"]
    stated_ev, withheld_ev = ev["C1"] + ev["C3"], ev["C2"] + ev["C4"]
    p_premise = fisher_2x2(stated, withheld, stated_ev - stated, withheld_ev - withheld) if withheld_ev else None

    naming_a, naming_b = acc["C1"] + acc["C4"], acc["C2"] + acc["C3"]
    naming_a_ev, naming_b_ev = ev["C1"] + ev["C4"], ev["C2"] + ev["C3"]
    p_naming = fisher_2x2(naming_a, naming_b, naming_a_ev - naming_a,
                          naming_b_ev - naming_b) if naming_b_ev else None

    with_drops = {c: len(drops[c]) for c in ("C2", "C4")}
    verdict_a1 = attribution(max(with_drops.values()))
    p_attr = fisher_2x2(with_drops["C2"] + with_drops["C4"], withheld_ev,
                        len(drops["C1"]) + len(drops["C3"]), stated_ev)

    print(f"=== P017 AES-GCM @ floor 4200 ({len(seeds)} seeds x {len(CELLS)} cells) ===")
    print("accepted / evaluable:", {c: f"{acc[c]}/{ev[c]}" for c in CELLS})
    print("withheld-arm dropout (C2, C4):", with_drops)
    print(f"ATTRIBUTION RULE A1: {verdict_a1} "
          f"(thresholds: <=2 BUDGET_EXPLAINS, 3-7 PARTIAL_BUDGET, >=8 FAILS)")
    print(f"attrition stated-vs-withheld 2x2 Fisher p={p_attr}")
    print(f"paired C1-vs-C4: {b10}/{b01} over {len(pairs)} evaluable pairs, p={p_paired}")
    print(f"premise marginal {stated}/{stated_ev} vs {withheld}/{withheld_ev}, p={p_premise}")
    print(f"naming marginal {naming_a}/{naming_a_ev} vs {naming_b}/{naming_b_ev}, p={p_naming}")

    if withheld > 0:
        print("\n!! WITHHELD-ARM ACCEPTANCE PRESENT: P014 must be REVISED, not defended.")
    if any(len(drops[c]) >= 8 for c in ("C2", "C4")):
        print("\n!! F3 triggered: dropout is not budget-bound. Report as the main finding.")

    if dups:
        print(f"\ninstrument-duplicate rows (flagged, never deleted): {len(dups)}: {dups[:3]}")


if __name__ == "__main__":
    main()
