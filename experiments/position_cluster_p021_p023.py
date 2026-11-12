#!/usr/bin/env python3
"""Is the drop pattern clustered in execution order?

P021's transport failures were bursty; P023's repair should remove that
structure. This script tests the drop indicator for serial dependence and
positional clustering, for P021 (complete) and P023 (complete or partial):

1. **Runs test** (Wald-Wolfowitz) over execution order, normal approximation
   plus a 10,000-shuffle permutation p (fixed seed) — fewer runs than chance
   means clustering.
2. **Lag-1 autocorrelation** of the drop indicator.
3. **Longest run of consecutive drops**, against the permutation null.
4. **Execution blocks** (4 equal contiguous blocks): drop rate per block with
   Wilson 95% CIs and a chi-square (or permutation) test.
5. **Rotation phase** (0-3, position within each instance's rotation): tests
   whether the first-executed cell of an instance is dropped more often.
6. **Per-cell positional runs test** over instance index 0..N-1.
7. Full position × cell matrices to CSV.

Execution order is the order rows appear in `results.jsonl` (the runner appends
as sessions finish), so it is the real temporal order, not a reconstruction.

Usage: position_cluster_p021_p023.py [--allow-partial]
"""
import argparse
import json
import math
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
COHORTS = {
    "P021": HERE / "info_contract_aesgcm_random_p021_20261102",
    "P023": HERE / "info_contract_aesgcm_random_p023_20261103",
}
CELLS = ("C1", "C2", "C3", "C4")
TERM = {"HTTP_ERROR", "TIMEOUT", "EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
        "MALFORMED_PROVIDER_JSON", "PROVIDER_UNAVAILABLE", "CREDENTIAL_MISSING",
        "CREDENTIAL_EMPTY"}
TRANSPORT = {"HTTP_ERROR", "TIMEOUT", "PROVIDER_UNAVAILABLE", "MALFORMED_PROVIDER_JSON",
             "CREDENTIAL_MISSING", "CREDENTIAL_EMPTY"}
MODEL_LEVEL = {"EMPTY_RESPONSE", "INCOMPLETE_RESPONSE"}
PERM_N = 10000
PERM_SEED = 20261103


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def runs_stat(seq):
    if not seq:
        return None
    runs, prev = 1, seq[0]
    for x in seq[1:]:
        if x != prev:
            runs += 1
            prev = x
    n1, n0 = sum(seq), len(seq) - sum(seq)
    n = n1 + n0
    if n1 == 0 or n0 == 0:
        return {"runs": runs, "n1": n1, "n0": n0, "expected": None,
                "z": None, "p_normal": None}
    exp = 1 + 2 * n1 * n0 / n
    var = 2 * n1 * n0 * (2 * n1 * n0 - n) / (n * n * (n - 1))
    z = (runs - exp) / math.sqrt(var)
    p = math.erfc(abs(z) / math.sqrt(2))
    return {"runs": runs, "n1": n1, "n0": n0, "expected": round(exp, 2),
            "z": round(z, 3), "p_normal": p}


def permutation_runs(seq, observed, rng):
    low = high = 0
    s = list(seq)
    n = len(s)
    if not any(s) or all(s):
        return None, None
    for _ in range(PERM_N):
        rng.shuffle(s)
        r, prev = 1, s[0]
        for x in s[1:]:
            if x != prev:
                r += 1
                prev = x
        if r <= observed:
            low += 1
        if r >= observed:
            high += 1
    p_low = (low + 1) / (PERM_N + 1)
    p_high = (high + 1) / (PERM_N + 1)
    return p_low, min(1.0, 2 * min(p_low, p_high))


def longest_run(seq):
    best = cur = 0
    for x in seq:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return best


def lag1(seq):
    n = len(seq)
    if n < 3:
        return None
    m = sum(seq) / n
    num = sum((seq[i] - m) * (seq[i + 1] - m) for i in range(n - 1))
    den = sum((x - m) ** 2 for x in seq)
    return None if den == 0 else num / den


def chi2_sf(x, df):
    try:
        from scipy.stats import chi2
        return float(chi2.sf(x, df))
    except Exception:
        return None


def load(path):
    rows, order = {}, []
    for line in (path / "results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        key = (rec["seed"], rec["cell"])
        if key in rows:
            continue
        rows[key] = rec
        order.append(key)
    launch = json.loads((path / "_LAUNCH.json").read_text())
    return rows, order, launch


def analyse(name, path):
    rows, order, launch = load(path)
    seq = [1 if rows[k]["status"] in TERM else 0 for k in order]
    n = len(seq)
    k = sum(seq)
    rng = random.Random(PERM_SEED)
    stat = runs_stat(seq)
    p_low, p_perm = (None, None) if stat["n1"] in (0, n) else permutation_runs(seq, stat["runs"], rng)

    blocks = []
    if n >= 8:
        size = n // 4
        for b in range(4):
            lo = b * size
            hi = n if b == 3 else (b + 1) * size
            kk, nn = sum(seq[lo:hi]), hi - lo
            blocks.append({"block": b + 1, "from": lo, "to": hi - 1,
                           "drops": kk, "sessions": nn,
                           "rate": kk / nn if nn else None,
                           "wilson": wilson(kk, nn)})
    block_test = None
    if blocks:
        exp = [b["sessions"] * k / n for b in blocks]
        obs = [b["drops"] for b in blocks]
        x2 = sum((o - e) ** 2 / e for o, e in zip(obs, exp) if e > 0)
        block_test = {"chi2": round(x2, 3), "df": 3, "p": chi2_sf(x2, 3)}

    # rotation phase: position within the instance's rotation (0-3)
    phase = {}
    for i, key in enumerate(order):
        phase.setdefault(i % 4, []).append(1 if rows[key]["status"] in TERM else 0)
    phase_rates = {p: {"drops": sum(v), "sessions": len(v),
                       "rate": sum(v) / len(v) if v else None,
                       "wilson": wilson(sum(v), len(v))}
                   for p, v in sorted(phase.items())}

    # per-cell positional runs test
    per_cell = {}
    exec_pos = {key: i for i, key in enumerate(order)}
    for c in CELLS:
        keys = sorted((k for k in rows if k[1] == c), key=lambda k: exec_pos[k])

        def _subset(sel):
            st = runs_stat([1 if rows[k]["status"] in sel else 0 for k in keys])
            return {"n": st["n1"] if st else 0,
                    "runs": st["runs"] if st else None,
                    "expected_runs": st["expected"] if st else None,
                    "p_normal": st["p_normal"] if st else None}

        seq_c = [1 if rows[k]["status"] in TERM else 0 for k in keys]
        st = runs_stat(seq_c)
        per_cell[c] = {"sessions": len(seq_c), "drops": sum(seq_c),
                       "runs": st["runs"] if st else None,
                       "expected_runs": st["expected"] if st else None,
                       "p_normal": st["p_normal"] if st else None,
                       "transport": _subset(TRANSPORT),
                       "model": _subset(MODEL_LEVEL)}

    matrix = {}
    for i, (seed, cell) in enumerate(order):
        matrix.setdefault(i % max(1, len(launch["seeds"])), {})[cell] = rows[(seed, cell)]["status"]

    return {"cohort": name, "protocol": launch["protocol"], "sessions": n,
            "registered": int(launch.get("sessions_registered", n)),
            "drops": k, "drop_rate": k / n if n else None,
            "runs": stat, "p_permutation": p_perm, "p_low": p_low,
            "lag1": lag1(seq), "longest_drop_run": longest_run(seq),
            "blocks": blocks, "block_test": block_test,
            "phase": phase_rates, "per_cell": per_cell,
            "execution_sequence_sha": __import__("hashlib").sha256(
                "".join(str(x) for x in seq).encode()).hexdigest()}


def fmt_p(p):
    if p is None:
        return "—"
    return f"{p:.2e}" if p < 1e-3 else f"{p:.4f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-partial", action="store_true")
    args = ap.parse_args()
    out = {}
    for name, path in COHORTS.items():
        out[name] = analyse(name, path)
    p023 = out["P023"]
    partial = p023["sessions"] < p023["registered"]
    if partial and not args.allow_partial:
        raise SystemExit(f"P023 incomplete: {p023['sessions']}/{p023['registered']}")

    L = ["# Does the drop pattern cluster in execution order?\n"]
    L.append(f"Execution order = order rows appear in `results.jsonl` (append order). "
             f"Permutation null: 10,000 shuffles, seed {PERM_SEED}. "
             f"A **low** runs p means fewer runs than chance, i.e. clustering.\n")
    if partial:
        L.append(f"> **PARTIAL: P023 has {p023['sessions']}/{p023['registered']} sessions.** "
                 f"Only P021's row is interpretable.\n")
    L.append("| cohort | sessions | drops | runs | expected runs | runs p (normal) | runs p (permutation) "
             "| lag-1 | longest drop run |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for name, r in out.items():
        st = r["runs"]
        L.append(f"| {name} | {r['sessions']} | {r['drops']} ({100 * r['drop_rate']:.1f}%) "
                 f"| {st['runs']} | {st['expected']} | {fmt_p(st['p_normal'])} "
                 f"| {fmt_p(r['p_permutation'])} | "
                 f"{'—' if r['lag1'] is None else f'{r[chr(108)+chr(97)+chr(103)+chr(49)]:.3f}'} "
                 f"| {r['longest_drop_run']} |")
    L.append("")
    L.append("## Execution blocks (4 contiguous quarters)\n")
    L.append("| cohort | block | sessions | drops | rate (95% Wilson) |")
    L.append("|---|---|---|---|---|")
    for name, r in out.items():
        for b in r["blocks"]:
            L.append(f"| {name} | Q{b['block']} ({b['from']}–{b['to']}) | {b['sessions']} "
                     f"| {b['drops']} | {100 * b['rate']:.1f}% "
                     f"[{100 * b['wilson'][0]:.1f}, {100 * b['wilson'][1]:.1f}] |")
        bt = r["block_test"]
        if bt:
            L.append(f"| {name} | — | — | — | chi2={bt['chi2']}, df={bt['df']}, p={fmt_p(bt['p'])} |")
    L.append("")
    L.append("## Rotation phase (position within each instance's 4-cell rotation)\n")
    L.append("| cohort | phase | sessions | drops | rate (95% Wilson) |")
    L.append("|---|---|---|---|---|")
    for name, r in out.items():
        for ph, v in r["phase"].items():
            L.append(f"| {name} | {ph} | {v['sessions']} | {v['drops']} | "
                     f"{100 * v['rate']:.1f}% [{100 * v['wilson'][0]:.1f}, {100 * v['wilson'][1]:.1f}] |")
    L.append("")
    L.append("## Per-cell positional runs test\n")
    L.append("| cohort | cell | sessions | any-drop runs p | transport drops | transport runs p "
             "| model drops | model runs p |")
    L.append("|---|---|---|---|---|---|---|---|")
    for name, r in out.items():
        for c in CELLS:
            v = r["per_cell"][c]
            L.append(f"| {name} | {c} | {v['sessions']} | {fmt_p(v['p_normal'])} "
                     f"| {v['transport']['n']} | {fmt_p(v['transport']['p_normal'])} "
                     f"| {v['model']['n']} | {fmt_p(v['model']['p_normal'])} |")
    L.append("")

    r21, r23 = out["P021"], out["P023"]
    L.append("## Reading\n")
    L.append(f"- P021: {r21['drops']}/{r21['sessions']} drops, {r21['runs']['runs']} runs vs "
             f"{r21['runs']['expected']} expected; runs p={fmt_p(r21['runs']['p_normal'])} "
             f"(permutation {fmt_p(r21['p_permutation'])}), lag-1 {r21['lag1']:.3f}."
             if r21["lag1"] is not None else
             f"- P021: {r21['drops']}/{r21['sessions']} drops; runs p={fmt_p(r21['runs']['p_normal'])}.")
    L.append(f"- P023: {r23['drops']}/{r23['sessions']} drops, {r23['runs']['runs']} runs vs "
             f"{r23['runs']['expected']} expected; runs p={fmt_p(r23['runs']['p_normal'])} "
             f"(permutation {fmt_p(r23['p_permutation'])}).")
    L.append("- Read the **transport** column for provider bursts and the **model** column for "
             "condition-driven textless completions. The any-drop column mixes both and is "
             "misleading when a cell is near-saturated.")
    for nm, r in out.items():
        tp = [c for c in CELLS if r["per_cell"][c]["transport"]["p_normal"] is not None
              and r["per_cell"][c]["transport"]["p_normal"] < 0.05]
        mp = [c for c in CELLS if r["per_cell"][c]["model"]["p_normal"] is not None
              and r["per_cell"][c]["model"]["p_normal"] < 0.05]
        L.append(f"- {nm}: transport clustering at p<0.05 in "
                 f"{', '.join(tp) if tp else 'no cell'}; model-level clustering in "
                 f"{', '.join(mp) if mp else 'no cell'}.")
    for name, r in out.items():
        sat = [c for c in CELLS
               if r["per_cell"][c]["sessions"] >= 20
               and r["per_cell"][c]["drops"] >= 0.80 * r["per_cell"][c]["sessions"]]
        if sat:
            L.append(f"- {name}: cell(s) {', '.join(sat)} are near-saturated "
                     f"(>=80% drops). The any-drop runs test is uninformative there — with "
                     f"almost no zeros, any clumping of the few evaluable sessions looks like "
                     f"clustering. Read the transport and model-level columns instead.")
    if partial:
        L.append("- **P023 row is partial and must not be quoted.**")
    L.append("")

    (HERE / "POSITION_CLUSTER_P021_P023.md").write_text("\n".join(L) + "\n")
    (HERE / "POSITION_CLUSTER_P021_P023.json").write_text(
        json.dumps({"partial": partial, "cohorts": out}, indent=2, sort_keys=True) + "\n")

    for name, path in COHORTS.items():
        rows, order, _ = load(path)
        with (HERE / f"POSITION_MATRIX_{name}.csv").open("w") as fh:
            fh.write("exec_index,cell,status,drop\n")
            for i, key in enumerate(order):
                rec = rows[key]
                fh.write(f"{i},{key[1]},{rec['status']},{int(rec['status'] in TERM)}\n")

    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
