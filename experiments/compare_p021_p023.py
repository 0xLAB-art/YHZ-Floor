#!/usr/bin/env python3
"""Row-by-row comparison of P021 (original) and P023 (transport-repaired re-run).

Both cohorts use the same design, the same frozen runner, the same cells,
rotations and analysis, but DIFFERENT CSPRNG seed draws. The comparison is
therefore per cell and per positional index — it is NOT an instance-paired test
and no paired p-value is reported. The only paired quantity is the positional
matrix written to CSV, labelled as such.

Outputs:
  COMPARISON_P021_P023.md            the table + reading
  COMPARISON_P021_P023.json          machine-readable numbers
  COMPARISON_P021_P023_by_position.csv

Usage: compare_p021_p023.py [--allow-partial]
"""
import argparse
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
P021 = HERE / "info_contract_aesgcm_random_p021_20261102"
P023 = HERE / "info_contract_aesgcm_random_p023_20261103"
CELLS = ("C1", "C2", "C3", "C4")
TERM = {"HTTP_ERROR", "TIMEOUT", "EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
        "MALFORMED_PROVIDER_JSON", "PROVIDER_UNAVAILABLE", "CREDENTIAL_MISSING",
        "CREDENTIAL_EMPTY"}
TRANSPORT = {"HTTP_ERROR", "TIMEOUT", "PROVIDER_UNAVAILABLE", "MALFORMED_PROVIDER_JSON",
             "CREDENTIAL_MISSING", "CREDENTIAL_EMPTY"}
MODEL_LEVEL = {"EMPTY_RESPONSE", "INCOMPLETE_RESPONSE"}

_spec = importlib.util.spec_from_file_location(
    "_p011_stats", HERE / "info_contract_label3_n32_20261101" / "analyze_p011.py")
_p011 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p011)
fisher_2x2 = _p011.fisher_2x2


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def newcombe(k2, n2, k1, n1):
    """Newcombe hybrid score interval for p2 - p1 (method 10)."""
    if not n1 or not n2:
        return None
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    diff = p2 - p1
    lo = diff - math.sqrt((p2 - l2) ** 2 + (u1 - p1) ** 2)
    hi = diff + math.sqrt((u2 - p2) ** 2 + (p1 - l1) ** 2)
    return (max(-1.0, lo), min(1.0, hi))


def load(d):
    best = {}
    for line in (d / "results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        best.setdefault((rec["seed"], rec["cell"]), rec)
    launch = json.loads((d / "_LAUNCH.json").read_text())
    fails = Counter()
    for line in (d / "events.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e["kind"] == "provider_failure":
            fails[(e["cell"], e["category"])] += 1
    order = {s: i for i, s in enumerate(launch["seeds"])}
    per_cell = {}
    for c in CELLS:
        rows = [r for (s, cc), r in best.items() if cc == c]
        drops = [r for r in rows if r["status"] in TERM]
        transport = [r for r in drops if r["status"] in TRANSPORT]
        model = [r for r in drops if r["status"] in MODEL_LEVEL]
        acc = sum(1 for r in rows if r.get("oracle_verdict") == "accepted")
        n, nd = len(rows), len(drops)
        per_cell[c] = {
            "sessions": n,
            "drops": nd,
            "transport_drops": len(transport),
            "model_drops": len(model),
            "evaluable": n - nd,
            "accepted": acc,
            "drop_rate": (nd / n) if n else None,
            "drop_wilson": wilson(nd, n),
            "acc_rate": (acc / (n - nd)) if (n - nd) else None,
            "acc_wilson": wilson(acc, n - nd),
            "drop_statuses": dict(Counter(r["status"] for r in drops)),
        }
    return {"launch": launch, "rows": best, "order": order,
            "per_cell": per_cell, "fails": fails}


def overall(per_cell):
    n = sum(v["sessions"] for v in per_cell.values())
    nd = sum(v["drops"] for v in per_cell.values())
    tr = sum(v["transport_drops"] for v in per_cell.values())
    mo = sum(v["model_drops"] for v in per_cell.values())
    acc = sum(v["accepted"] for v in per_cell.values())
    ev = n - nd
    return {"sessions": n, "drops": nd, "transport_drops": tr, "model_drops": mo,
            "evaluable": ev, "accepted": acc,
            "drop_rate": (nd / n) if n else None, "drop_wilson": wilson(nd, n),
            "acc_rate": (acc / ev) if ev else None}


def pct(x):
    return "—" if x is None else f"{100 * x:.1f}%"


def ci(t):
    return "—" if t is None else f"[{100 * t[0]:.1f}, {100 * t[1]:.1f}]"


def pval(p):
    if p is None:
        return "—"
    return f"{p:.2e}" if p < 1e-3 else f"{p:.4f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-partial", action="store_true")
    args = ap.parse_args()

    a, b = load(P021), load(P023)
    n_reg = int(b["launch"]["sessions_registered"])
    partial = len(b["rows"]) < n_reg
    if partial and not args.allow_partial:
        raise SystemExit(f"P023 incomplete: {len(b['rows'])}/{n_reg} sessions")
    oa, ob = overall(a["per_cell"]), overall(b["per_cell"])

    lines = []
    lines.append("# P021 vs P023 — drop-rate comparison\n")
    lines.append(f"- **P021** `{a['launch']['protocol']}` — label `{a['launch']['model_label']}`, "
                 f"{oa['sessions']} sessions, seeds `{str(a['launch'].get('seeds_registered_sha256'))[:12]}…`")
    lines.append(f"- **P023** `{b['launch']['protocol']}` — label `{b['launch']['model_label']}`, "
                 f"{ob['sessions']}/{n_reg} sessions, seeds `{str(b['launch'].get('seeds_registered_sha256'))[:12]}…`")
    lines.append("- Same runner, cells, rotations, floor and analyzer. **Different seed draws**, so "
                 "this is a per-cell comparison, not an instance-paired test.")
    if partial:
        lines.append(f"\n> **PARTIAL: {ob['sessions']} of {n_reg} sessions. Not a result.** "
                     "The table is regenerated when P023 finishes.\n")
    lines.append("")

    for title, cohort, ov in (("P021 (original transport)", a, oa),
                              ("P023 (repaired transport)", b, ob)):
        lines.append(f"## {title}\n")
        lines.append("| cell | sessions | transport drops | model-level drops | evaluable | accepted "
                     "| drop rate (95% Wilson) | accepted/evaluable (95% Wilson) |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for c in CELLS:
            v = cohort["per_cell"][c]
            lines.append(f"| {c} | {v['sessions']} | {v['transport_drops']} | {v['model_drops']} "
                         f"| {v['evaluable']} | {v['accepted']} | {pct(v['drop_rate'])} "
                         f"{ci(v['drop_wilson'])} | {pct(v['acc_rate'])} {ci(v['acc_wilson'])} |")
        lines.append(f"| **total** | {ov['sessions']} | {ov['transport_drops']} | {ov['model_drops']} "
                     f"| {ov['evaluable']} | {ov['accepted']} | {pct(ov['drop_rate'])} "
                     f"{ci(ov['drop_wilson'])} | {pct(ov['acc_rate'])} |")
        lines.append("")

    lines.append("## Drop-rate difference (P023 − P021)\n")
    lines.append("| cell | P021 drops/sessions | P023 drops/sessions | Δ (95% Newcombe) | Fisher two-sided |")
    lines.append("|---|---|---|---|---|")
    deltas = {}
    for c in CELLS + ("total",):
        if c == "total":
            na, nda, nb, ndb = oa["sessions"], oa["drops"], ob["sessions"], ob["drops"]
        else:
            na, nda = a["per_cell"][c]["sessions"], a["per_cell"][c]["drops"]
            nb, ndb = b["per_cell"][c]["sessions"], b["per_cell"][c]["drops"]
        d = None if not na or not nb else (ndb / nb) - (nda / na)
        ci_d = newcombe(ndb, nb, nda, na)
        p = (fisher_2x2(ndb, nda, nb - ndb, na - nda)
             if na > 0 and nb > 0 else None)
        deltas[c] = {"p021": [nda, na], "p023": [ndb, nb], "delta": d,
                     "newcombe": ci_d, "fisher_p": p}
        lines.append(f"| {c} | {nda}/{na} ({pct(na and nda / na)}) | {ndb}/{nb} ({pct(nb and ndb / nb)}) "
                     f"| {pct(d)} {ci(ci_d)} | {pval(p)} |")
    lines.append("")

    lines.append("## Provider-failure attempts by category\n")
    lines.append("Attempts, not sessions: the repaired transport retries before a session is lost.\n")
    cats = sorted({k[1] for k in list(a["fails"]) + list(b["fails"])})
    if cats:
        lines.append("| category | P021 attempts | P023 attempts |")
        lines.append("|---|---|---|")
        for cat in cats:
            ca = sum(v for (c, k), v in a["fails"].items() if k == cat)
            cb = sum(v for (c, k), v in b["fails"].items() if k == cat)
            lines.append(f"| {cat} | {ca} | {cb} |")
        lines.append("")

    tr_a, tr_b = oa["transport_drops"], ob["transport_drops"]
    lines.append("## Reading\n")
    lines.append(f"- P021 lost **{oa['drops']}/{oa['sessions']}** sessions "
                 f"({pct(oa['drop_rate'])}); **{tr_a}** of those were transport-level.")
    lines.append(f"- P023 has lost **{ob['drops']}/{ob['sessions']}** so far "
                 f"({pct(ob['drop_rate'])}); **{tr_b}** transport-level.")
    lines.append(f"- Transport drop rate: P021 {pct(tr_a / oa['sessions'] if oa['sessions'] else None)} "
                 f"→ P023 {pct(tr_b / ob['sessions'] if ob['sessions'] else None)}. "
                 f"Δ {pct((tr_b / ob['sessions'] if ob['sessions'] else 0) - (tr_a / oa['sessions'] if oa['sessions'] else 0))} "
                 f"({ci(newcombe(tr_b, ob['sessions'], tr_a, oa['sessions']))}).")
    lines.append(f"- Model-level drops (textless/truncated completions) are unaffected by the repair "
                 f"by design: P021 {oa['model_drops']}, P023 {ob['model_drops']}.")
    if partial:
        lines.append("- **Partial sample.** Do not quote these rates; wait for the regenerated table.")
    lines.append("")

    (HERE / "COMPARISON_P021_P023.md").write_text("\n".join(lines) + "\n")

    payload = {"partial": partial, "p023_sessions": ob["sessions"],
               "p023_registered": n_reg, "p021": oa, "p023": ob,
               "per_cell": {"p021": a["per_cell"], "p023": b["per_cell"]},
               "deltas": deltas,
               "failure_attempts": {
                   "p021": {f"{c}:{k}": v for (c, k), v in a["fails"].items()},
                   "p023": {f"{c}:{k}": v for (c, k), v in b["fails"].items()}}}
    (HERE / "COMPARISON_P021_P023.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")

    with (HERE / "COMPARISON_P021_P023_by_position.csv").open("w") as fh:
        fh.write("position,cell,p021_status,p023_status\n")
        by_pos_b = defaultdict(dict)
        for (seed, cell), r in b["rows"].items():
            by_pos_b[bidx(seed, b)][cell] = r["status"]
        for pos in range(max(len(a["order"]), len(b["order"]))):
            for c in CELLS:
                sa = status_at(a, pos, c)
                sb = by_pos_b.get(pos, {}).get(c)
                fh.write(f"{pos},{c},{sa or ''},{sb or ''}\n")

    print("\n".join(lines))
    print(f"[written] {HERE / 'COMPARISON_P021_P023.md'}")
    return 0


def bidx(seed, cohort):
    return cohort["order"][seed]


def status_at(cohort, pos, cell):
    for (seed, c), r in cohort["rows"].items():
        if c == cell and cohort["order"][seed] == pos:
            return r["status"]
    return None


if __name__ == "__main__":
    sys.exit(main())
