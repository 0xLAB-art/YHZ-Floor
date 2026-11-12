#!/usr/bin/env python3
"""P022 vs P024 — drop distribution across arms and across cohorts.

P022 and P024 each run the SAME 24 CSPRNG instances on two label arms, so
within a cohort the arms are instance-paired and McNemar's exact test is the
right test. Across cohorts the seed draws differ, so P022-vs-P024 comparisons
are unpaired and use a Newcombe interval on the drop-rate difference plus
Fisher's exact test.

Writes COMPARISON_P022_P024.md / .json. With --allow-missing it writes whatever
exists (P024 may not have started) and marks the missing parts as pending.
"""
import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("_cmp", HERE / "compare_p021_p023.py")
_cmp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cmp)
wilson, newcombe = _cmp.wilson, _cmp.newcombe
fisher_2x2, pval = _cmp.fisher_2x2, _cmp.pval
pct, ci = _cmp.pct, _cmp.ci
TERM, TRANSPORT, MODEL_LEVEL, CELLS = _cmp.TERM, _cmp.TRANSPORT, _cmp.MODEL_LEVEL, _cmp.CELLS

_b = importlib.util.spec_from_file_location(
    "_p011b", HERE / "info_contract_label3_n32_20261101" / "analyze_p011.py")
_p011 = importlib.util.module_from_spec(_b)
_b.loader.exec_module(_p011)
binomial = _p011.exact_binomial_two_sided

ARMS = {
    "P022a": HERE / "info_contract_aesgcm_p022a_20261102",
    "P022b": HERE / "info_contract_aesgcm_p022b_20261102",
    "P024a": HERE / "info_contract_aesgcm_p024a_20261103",
    "P024b": HERE / "info_contract_aesgcm_p024b_20261103",
}
COHORTS = {"P022": ("P022a", "P022b"), "P024": ("P024a", "P024b")}


def load(path):
    if not (path / "results.jsonl").exists():
        return None
    launch = json.loads((path / "_LAUNCH.json").read_text())
    rows = {}
    for line in (path / "results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        rows.setdefault((rec["seed"], rec["cell"]), rec)
    fails = Counter()
    events = path / "events.jsonl"
    if events.exists():
        for line in events.read_text().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if e["kind"] == "provider_failure":
                fails[(e["cell"], e["category"])] += 1
    per_cell = {}
    for c in CELLS:
        rs = [r for (s, cc), r in rows.items() if cc == c]
        drops = [r for r in rs if r["status"] in TERM]
        tr = [r for r in drops if r["status"] in TRANSPORT]
        mo = [r for r in drops if r["status"] in MODEL_LEVEL]
        acc = sum(1 for r in rs if r.get("oracle_verdict") == "accepted")
        n, nd = len(rs), len(drops)
        per_cell[c] = {"sessions": n, "drops": nd, "transport": len(tr),
                       "model": len(mo), "evaluable": n - nd, "accepted": acc,
                       "drop_rate": (nd / n) if n else None,
                       "drop_wilson": wilson(nd, n),
                       "transport_rate": (len(tr) / n) if n else None,
                       "model_rate": (len(mo) / n) if n else None,
                       "acc_rate": (acc / (n - nd)) if (n - nd) else None,
                       "acc_wilson": wilson(acc, n - nd),
                       "drop_statuses": dict(Counter(r["status"] for r in drops))}
    total = {k: sum(v[k] for v in per_cell.values())
             for k in ("sessions", "drops", "transport", "model", "evaluable", "accepted")}
    total["drop_rate"] = total["drops"] / total["sessions"] if total["sessions"] else None
    total["transport_rate"] = total["transport"] / total["sessions"] if total["sessions"] else None
    total["model_rate"] = total["model"] / total["sessions"] if total["sessions"] else None
    total["acc_rate"] = total["accepted"] / total["evaluable"] if total["evaluable"] else None
    total["drop_wilson"] = wilson(total["drops"], total["sessions"])
    return {"launch": launch, "rows": rows, "per_cell": per_cell,
            "total": total, "fails": fails, "protocol": launch["protocol"],
            "label": launch.get("model_label"), "floor": launch.get("token_floor"),
            "seeds": list(launch.get("seeds", []))}


def paired(arms, cell):
    a, b = arms
    seeds = sorted({s for (s, c) in a["rows"] if c == cell}
                   & {s for (s, c) in b["rows"] if c == cell})
    both = only_a = only_b = neither = 0
    for s in seeds:
        va = a["rows"][(s, cell)].get("oracle_verdict") == "accepted"
        vb = b["rows"][(s, cell)].get("oracle_verdict") == "accepted"
        if va and vb:
            both += 1
        elif va:
            only_a += 1
        elif vb:
            only_b += 1
        else:
            neither += 1
    n10, n01 = only_a, only_b
    p = binomial(min(n10, n01), n10 + n01) if (n10 + n01) else None
    return {"pairs": len(seeds), "both": both, "only_a": only_a, "only_b": only_b,
            "neither": neither, "mcnemar_p": p}


def delta(x, y):
    """y - x on drops/sessions, with Newcombe and Fisher."""
    if not x or not y or not x["sessions"] or not y["sessions"]:
        return None
    d = y["drop_rate"] - x["drop_rate"]
    return {"delta": d,
            "newcombe": newcombe(y["drops"], y["sessions"], x["drops"], x["sessions"]),
            "fisher_p": fisher_2x2(y["drops"], x["drops"],
                                   y["sessions"] - y["drops"], x["sessions"] - x["drops"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-missing", action="store_true")
    args = ap.parse_args()
    data = {k: load(v) for k, v in ARMS.items()}
    missing = [k for k, v in data.items() if v is None]
    if missing and not args.allow_missing:
        raise SystemExit(f"missing results: {missing}")

    L = ["# P022 vs P024 — drop distribution across arms\n"]
    for arm in ("P022a", "P022b", "P024a", "P024b"):
        d = data[arm]
        if d:
            L.append(f"- **{arm}** `{d['protocol']}` — {d['label']}, floor {d['floor']}, "
                     f"{d['total']['sessions']}/96 sessions, seeds `{str(d['launch'].get('seeds_registered_sha256'))[:12]}…`")
        else:
            L.append(f"- **{arm}** — not collected yet")
    if missing:
        L.append(f"\n> **PENDING: {', '.join(missing)}.** Sections that need them are marked pending.\n")
    L.append("")

    L.append("## Descriptive — every arm, every cell\n")
    L.append("| arm | cell | sessions | transport drops | model-level drops | evaluable | accepted "
             "| drop rate (95% Wilson) | accepted/evaluable |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for arm in ("P022a", "P022b", "P024a", "P024b"):
        d = data[arm]
        if not d:
            continue
        for c in CELLS:
            v = d["per_cell"][c]
            L.append(f"| {arm} | {c} | {v['sessions']} | {v['transport']} | {v['model']} "
                     f"| {v['evaluable']} | {v['accepted']} | {pct(v['drop_rate'])} "
                     f"{ci(v['drop_wilson'])} | {pct(v['acc_rate'])} |")
        t = d["total"]
        L.append(f"| {arm} | **total** | {t['sessions']} | {t['transport']} | {t['model']} "
                 f"| {t['evaluable']} | {t['accepted']} | {pct(t['drop_rate'])} "
                 f"{ci(t['drop_wilson'])} | {pct(t['acc_rate'])} |")
    L.append("")

    L.append("## Within-cohort arm comparison (same instances, McNemar exact)\n")
    L.append("| cohort | cell | pairs | both accept | a only | b only | neither | McNemar p |")
    L.append("|---|---|---|---|---|---|---|---|")
    paired_out = {}
    for coh, (aa, bb) in COHORTS.items():
        if not (data[aa] and data[bb]):
            L.append(f"| {coh} | — | — | — | — | — | — | pending |")
            continue
        for c in CELLS + ("total",):
            if c == "total":
                vals = [paired((data[aa], data[bb]), x) for x in CELLS]
                agg = {k: sum(v[k] for v in vals) for k in ("pairs", "both", "only_a", "only_b", "neither")}
                n10, n01 = agg["only_a"], agg["only_b"]
                agg["mcnemar_p"] = binomial(min(n10, n01), n10 + n01) if (n10 + n01) else None
                p = agg
            else:
                p = paired((data[aa], data[bb]), c)
                paired_out[f"{coh}:{c}"] = p
            L.append(f"| {coh} | {c} | {p['pairs']} | {p['both']} | {p['only_a']} "
                     f"| {p['only_b']} | {p['neither']} | {pval(p['mcnemar_p'])} |")
    L.append("")

    L.append("## Across cohorts, same arm (unpaired, different seed draws)\n")
    L.append("| arm | cell | P022 drops/sessions | P024 drops/sessions | Δ drop rate (95% Newcombe) | Fisher p |")
    L.append("|---|---|---|---|---|---|")
    cross = {}
    for stem in ("a", "b"):
        p22, p24 = data[f"P022{stem}"], data[f"P024{stem}"]
        if not p24:
            L.append(f"| {stem} | — | — | pending | — | — |")
            continue
        for c in CELLS + ("total",):
            x = p22["total"] if c == "total" else p22["per_cell"][c]
            y = p24["total"] if c == "total" else p24["per_cell"][c]
            dd = delta(x, y)
            cross[f"{stem}:{c}"] = dd
            L.append(f"| {stem} | {c} | {x['drops']}/{x['sessions']} ({pct(x['drop_rate'])}) "
                     f"| {y['drops']}/{y['sessions']} ({pct(y['drop_rate'])}) "
                     f"| {pct(dd['delta'])} {ci(dd['newcombe'])} | {pval(dd['fisher_p'])} |")
    L.append("")

    L.append("## Transport-only drops, arm by arm\n")
    L.append("| arm | transport drops | sessions | rate | model-level drops | rate |")
    L.append("|---|---|---|---|---|---|")
    for arm in ("P022a", "P022b", "P024a", "P024b"):
        d = data[arm]
        if d:
            t = d["total"]
            L.append(f"| {arm} | {t['transport']} | {t['sessions']} | {pct(t['transport_rate'])} "
                     f"| {t['model']} | {pct(t['model_rate'])} |")
    L.append("")

    L.append("## Provider-failure attempts by category\n")
    cats = sorted({k[1] for d in data.values() if d for k in d["fails"]})
    if cats:
        L.append("| category | " + " | ".join(a for a in ARMS) + " |")
        L.append("|---" * (len(ARMS) + 1) + "|")
        for cat in cats:
            row = [str(sum(v for (c, k), v in (data[a]["fails"] if data[a] else Counter()).items() if k == cat))
                   for a in ARMS]
            L.append(f"| {cat} | " + " | ".join(row) + " |")
        L.append("")

    L.append("## Reading\n")
    for arm in ("P022a", "P022b", "P024a", "P024b"):
        d = data[arm]
        if not d:
            continue
        t = d["total"]
        L.append(f"- {arm}: {t['drops']}/{t['sessions']} drops ({pct(t['drop_rate'])}), "
                 f"transport {t['transport']}, model-level {t['model']}, "
                 f"evaluable {t['evaluable']}.")
    for coh in COHORTS:
        if f"{coh}:total" in paired_out:
            p = paired_out[f"{coh}:total"]
            L.append(f"- {coh} arm agreement: both accept {p['both']}, a-only {p['only_a']}, "
                     f"b-only {p['only_b']}, neither {p['neither']} (McNemar p={pval(p['mcnemar_p'])}).")
    if data.get("P024b"):
        b = data["P024b"]["per_cell"]
        L.append(f"- P024b withheld cells: C2 evaluable {b['C2']['evaluable']}, "
                 f"C4 evaluable {b['C4']['evaluable']} (P022b had 0 and 0).")
    else:
        L.append("- P024 not collected yet; arm-b withheld evaluability is the quantity to watch.")
    if missing:
        L.append("- **Pending sections are not results.**")
    L.append("")

    (HERE / "COMPARISON_P022_P024.md").write_text("\n".join(L) + "\n")
    def _clean(v):
        if not v:
            return None
        out = {kk: vv for kk, vv in v.items() if kk not in ("rows", "fails")}
        out["fails"] = {f"{c}:{cat}": n for (c, cat), n in v["fails"].items()}
        return out

    (HERE / "COMPARISON_P022_P024.json").write_text(json.dumps(
        {"missing": missing,
         "arms": {k: _clean(v) for k, v in data.items()},
         "paired": paired_out, "cross_cohort": cross},
        indent=2, sort_keys=True, default=str) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
