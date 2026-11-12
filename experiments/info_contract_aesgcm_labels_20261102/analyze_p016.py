#!/usr/bin/env python3
"""P016 analysis — frozen before either label completed.

Per label, never pooled:
  - per-cell accepted / evaluable / terminal drops
  - paired C1-vs-C4 discordance on evaluable pairs, exact binomial two-sided
  - premise marginal (C1+C3 vs C2+C4), Fisher two-sided
  - the prespecified classification from PREREGISTRATION.md §4:
        direction replicated   C1 >= 12/16 and C2 <= 4/16
        instrument difficulty  C1 < 12/16
        not replicated         otherwise
Then one descriptive comparison table against P014 (same fixture, same floor
2800, same route, different labels). No p-value is computed ACROSS labels and no
rate is pooled: the labels share a route, a key and an adapter, so only direction
and magnitude are compared.
"""
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
P014 = HERE.parent / "info_contract_aesgcm_20261102"
TERM = {"HTTP_ERROR", "TIMEOUT", "EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
        "MALFORMED_PROVIDER_JSON", "PROVIDER_UNAVAILABLE", "CREDENTIAL_MISSING"}
CELLS = ("C1", "C2", "C3", "C4")
REGISTERED_SEEDS = 16
LABELS = (("gpt-6.1-sol", "gpt_6_1_sol"), ("gpt-5.6-sol", "gpt_5_6_sol"))

_spec = importlib.util.spec_from_file_location(
    "_p011_stats", HERE.parent / "info_contract_label3_n32_20261101" / "analyze_p011.py")
_p011 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p011)
fisher_2x2 = _p011.fisher_2x2
binomial = _p011.exact_binomial_two_sided


def load_cells(path):
    """Earliest row per (seed, cell); terminal failures counted, never imputed."""
    best, dups = {}, 0
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        key = (rec["seed"], rec["cell"])
        if key in best:
            dups += 1
        else:
            best[key] = rec
    acc, ev, drops = defaultdict(int), defaultdict(int), defaultdict(int)
    verdict = {}
    for key, rec in best.items():
        if rec["status"] in TERM:
            drops[key[1]] += 1
            verdict[key] = "PROVIDER_DROP"
        else:
            v = 1 if rec.get("oracle_verdict") == "accepted" else 0
            verdict[key] = v
            ev[key[1]] += 1
            acc[key[1]] += v
    return {"acc": acc, "ev": ev, "drops": drops, "verdict": verdict,
            "seeds": sorted({k[0] for k in best}), "dups": dups}


def summarise(name, d):
    pairs = [(d["verdict"][(s, "C1")], d["verdict"][(s, "C4")]) for s in d["seeds"]
             if isinstance(d["verdict"].get((s, "C1")), int)
             and isinstance(d["verdict"].get((s, "C4")), int)]
    b10 = sum(1 for a, c in pairs if a == 1 and c == 0)
    b01 = sum(1 for a, c in pairs if a == 0 and c == 1)
    p_paired = binomial(min(b10, b01), b10 + b01) if (b10 + b01) else None
    stated, withheld = d["acc"]["C1"] + d["acc"]["C3"], d["acc"]["C2"] + d["acc"]["C4"]
    s_ev, w_ev = d["ev"]["C1"] + d["ev"]["C3"], d["ev"]["C2"] + d["ev"]["C4"]
    p_prem = fisher_2x2(stated, withheld, s_ev - stated, w_ev - withheld) if w_ev and s_ev else None
    # Classification uses the REGISTERED 16-seed denominator. On a cohort that
    # ended short, the absolute thresholds would mislabel a partial run as an
    # instrument failure, so a short cohort is explicitly left unclassified.
    if len(d["seeds"]) < REGISTERED_SEEDS:
        cls = f"partial cohort ({len(d['seeds'])}/{REGISTERED_SEEDS} seeds) — NOT classified"
    elif d["acc"]["C1"] < 12:
        cls = "instrument-difficulty"
    elif d["acc"]["C1"] >= 12 and d["acc"]["C2"] <= 4:
        cls = "direction replicated"
    else:
        cls = "direction NOT replicated"
    return {"b10": b10, "b01": b01, "pairs": len(pairs), "p_paired": p_paired,
            "premise": (stated, s_ev, withheld, w_ev, p_prem), "cls": cls}


def main():
    rows, summaries, missing = [], {}, []
    for label, slug in LABELS:
        path = HERE / slug / "results.jsonl"
        if not path.exists():
            missing.append(label)
            continue
        d = load_cells(path)
        summaries[label] = summarise(label, d)
        rows.append((label, d))

    if not rows:
        print("P016: no label produced results yet — nothing measured.")
        return

    for label, d in rows:
        s = summaries[label]
        print(f"=== {label} ({len(d['seeds'])} seeds recorded) ===")
        print("accepted / evaluable:",
              {c: f"{d['acc'][c]}/{d['ev'][c]}" for c in CELLS})
        print("terminal drops:", {c: d["drops"][c] for c in CELLS})
        print(f"paired C1-vs-C4: {s['b10']}/{s['b01']} over {s['pairs']} evaluable pairs, "
              f"p={s['p_paired']}")
        st, st_ev, wi, wi_ev, p = s["premise"]
        print(f"premise marginal {st}/{st_ev} vs {wi}/{wi_ev}, p={p}")
        print(f"classification: {s['cls']}")
        if d["dups"]:
            print(f"instrument-duplicate rows (flagged): {d['dups']}")
        print()

    # ---- descriptive comparison with P014; no pooled estimate, no cross-label p
    print("=== comparison vs P014 (same fixture, same floor 2800, same route) ===")
    p014_summary = P014 / "summary.json"
    if p014_summary.exists():
        p14 = json.loads(p014_summary.read_text())["per_cell"]
        header = f"{'cell':<5} {'P014 gpt-6-astra':>18} " + " ".join(f"{l:>18}" for l, _ in rows)
        print(header)
        for c in CELLS:
            line = f"{c:<5} {p14[c]['accepted']:>10}/{p14[c]['sessions']:<7}"
            for label, d in rows:
                line += f" {d['acc'][c]:>10}/{d['ev'][c]:<7}"
            print(line)
        print("\nP014 column is accepted/registered (dropout shown in REPORT_P014.md);")
        print("label columns are accepted/evaluable in this cohort.")
    else:
        print("P014 summary.json not found — comparison skipped.")

    print("\nNOT POOLED: these labels share one route, one key and one adapter;")
    print("the table supports 'direction on label X', not a provider or model-family rate.")
    if missing:
        print(f"\nlabels with no results (not started or no rows): {', '.join(missing)}")


if __name__ == "__main__":
    main()
