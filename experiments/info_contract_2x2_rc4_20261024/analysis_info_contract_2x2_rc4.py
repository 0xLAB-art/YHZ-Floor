#!/usr/bin/env python3
"""P011-INFO-CONTRACT-2X2-RC4-v1 analysis.

Structural mirror of analysis_info_contract_2x2.py (P010). Reads
{results.jsonl, events.jsonl} in this namespace and writes ANALYSIS.json.

Descriptive exact statistics only (no alpha-level claims):
- Fisher exact one-sided/two-sided hypergeometric for the reference-premise
  marginal (R+ = C1,C3 vs R- = C2,C4) and the naming marginal (N+ = C1,C4 vs
  N- = C2,C3).
- Paired discordance by seed (McNemar-style descriptive) with exact binomial
  two-sided p for C1 vs C4.
- Falsifier verdicts F1-F3 as prespecified for the RC4 extension.

Never pools with P010; P010 numbers are only read (read-only) to print the
side-by-side comparison rows.
"""
import json
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
P010_DIR = HERE.parents[0] / "info_contract_2x2_20261018"

CELL_DESC = {
    "C1": "A+ B+ (named RC4 keystream-reuse instance, all-zero reference value stated)   [P010 default mirror]",
    "C2": "A- B- (naming withheld + derive-from-observations frame, reference content unstated)",
    "C3": "A- B+ (naming withheld, all-zero reference value stated)",
    "C4": "A+ B- (named RC4 keystream-reuse instance, reference content unstated)",
}
R_PLUS = ["C1", "C3"]
R_MINUS = ["C2", "C4"]
N_PLUS = ["C1", "C4"]
N_MINUS = ["C2", "C3"]


def rows(path):
    out = []
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def fisher_one_sided(a_c, a_t, b_c, b_t):
    n = a_c + b_c
    total = a_t + b_t
    if total == 0 or n == 0:
        return None
    denom = comb(total, n)
    p = 0
    for k in range(a_c, min(a_t, n) + 1):
        if n - k <= b_t and k <= a_t:
            p += comb(a_t, k) * comb(b_t, n - k)
    return p / denom


def fisher_two_sided(a_c, a_t, b_c, b_t):
    n = a_c + b_c
    total = a_t + b_t
    if total == 0 or n == 0:
        return None
    denom = comb(total, n)
    probs = []
    for k in range(max(0, n - b_t), min(a_t, n) + 1):
        probs.append((comb(a_t, k) * comb(b_t, n - k) / denom, k))
    obs = sum(pr for pr, k in probs if k == a_c)
    return sum(pr for pr, k in probs if pr <= obs * (1 + 1e-9))


def binom_two_sided(b, c):
    if b + c == 0:
        return None
    n = b + c
    probs = [comb(n, k) * 0.5 ** n for k in range(n + 1)]
    obs = probs[b]
    return min(1.0, sum(p for p in probs if p <= obs * (1 + 1e-9)))


def main():
    res = rows(HERE / "results.jsonl")
    events = rows(HERE / "events.jsonl")
    print(f"sessions recorded: {len(res)}")
    by_cell = {c: [] for c in CELL_DESC}
    for r in res:
        by_cell[r["cell"]].append(r)

    print("\n== per-cell (planned 4 sessions each) ==")
    for c in ("C1", "C2", "C3", "C4"):
        rs = by_cell[c]
        acc = [r["seed"] for r in rs if r.get("status") == "SUCCESS"]
        print(f"{c} {CELL_DESC[c]}: sessions={len(rs)} accepted={len(acc)} seeds={acc} "
              f"submissions={sum(r.get('submissions', 0) for r in rs)} turns={sum(r.get('turns', 0) for r in rs)}")

    print("\n== paired by seed ==")
    seeds = sorted({r["seed"] for r in res})
    print("seed | C1 | C2 | C3 | C4")
    for s in seeds:
        cells = {r["cell"]: r for r in res if r["seed"] == s}
        line = f"{s:>4} |"
        for c in ("C1", "C2", "C3", "C4"):
            r = cells.get(c)
            line += " -- |" if r is None else ("  A |" if r.get("status") == "SUCCESS" else "  . |")
        print(line)

    def accepted(cells):
        got = [r for r in res if r["cell"] in cells]
        return sum(r.get("status") == "SUCCESS" for r in got), len(got)

    rp_a, rp_t = accepted(R_PLUS)
    rm_a, rm_t = accepted(R_MINUS)
    np_a, np_t = accepted(N_PLUS)
    nm_a, nm_t = accepted(N_MINUS)
    print("\n== marginals ==")
    print(f"R+ (C1,C3): {rp_a}/{rp_t}; R- (C2,C4): {rm_a}/{rm_t}")
    print(f"N+ (C1,C4): {np_a}/{np_t}; N- (C2,C3): {nm_a}/{nm_t}")

    fp_r1 = fisher_one_sided(rp_a, rp_t, rm_a, rm_t)
    fp_r2 = fisher_two_sided(rp_a, rp_t, rm_a, rm_t)
    fp_n1 = fisher_one_sided(np_a, np_t, nm_a, nm_t)
    fp_n2 = fisher_two_sided(np_a, np_t, nm_a, nm_t)
    print(f"R marginal Fisher one-sided p={fp_r1} two-sided p={fp_r2}" if fp_r1 is not None else "R marginal: insufficient data")
    print(f"N marginal Fisher one-sided p={fp_n1} two-sided p={fp_n2}" if fp_n1 is not None else "N marginal: insufficient data")

    pair_specs = [("C1", "C4"), ("C3", "C2")]
    disc = {"C1> C4": 0, "C4> C1": 0, "C3> C2": 0, "C2> C3": 0}
    for a, b in pair_specs:
        for s in seeds:
            ra = next((r for r in res if r["seed"] == s and r["cell"] == a), None)
            rb = next((r for r in res if r["seed"] == s and r["cell"] == b), None)
            if ra is None or rb is None:
                continue
            a_s = ra.get("status") == "SUCCESS"
            b_s = rb.get("status") == "SUCCESS"
            if a_s and not b_s:
                disc[f"{a}> {b}"] += 1
            if b_s and not a_s:
                disc[f"{b}> {a}"] += 1
    print("\n== paired discordance (matched seeds) ==")
    for k, v in disc.items():
        print(f"{k}: {v}")
    b_, c_ = disc["C1> C4"], disc["C4> C1"]
    pb = binom_two_sided(b_, c_)
    print(f"C1 vs C4 discordant b={b_} c={c_}; exact binomial two-sided p={pb}")

    print("\n== rejected-verdict failure stages (events) ==")
    stage_by_cell = {}
    for e in events:
        if e.get("kind") == "oracle_verdict" and e.get("verdict") == "rejected":
            stage_by_cell.setdefault(e.get("cell"), []).append(e.get("failure_stage"))
    for c in ("C1", "C2", "C3", "C4"):
        print(f"{c}: {stage_by_cell.get(c, [])}")

    c1_acc = sum(r.get("status") == "SUCCESS" for r in by_cell["C1"])
    c2_acc = sum(r.get("status") == "SUCCESS" for r in by_cell["C2"])
    c3_acc = sum(r.get("status") == "SUCCESS" for r in by_cell["C3"])
    c4_acc = sum(r.get("status") == "SUCCESS" for r in by_cell["C4"])
    c1_t, c2_t, c3_t, c4_t = (len(by_cell[c]) for c in ("C1", "C2", "C3", "C4"))
    fals = {
        # F1 firing (TRUE) = honest null: the reference premise is NOT load-bearing for RC4.
        # Operationalization (prespecified): |accepted(C4) - accepted(C1)| <= 1 on the executed
        # matched sessions (per-cell n=4; "about as often" = within one session either direction).
        "F1_C4_succeeds_about_as_often_as_C1_honest_null":
            (c1_t > 0 and c4_t > 0 and abs(c4_acc - c1_acc) <= 1),
        "F2_C3_fails_while_C1_succeeds": (c3_t > 0 and c3_acc == 0 and c1_acc > 0),
        "F3_C2_succeeds": (c2_acc > 0),
        "operationalizations": {
            "F1": "abs(accepted_C4 - accepted_C1) <= 1 with both cells executed (prespecified)",
            "F2": "accepted_C3 == 0 while accepted_C1 > 0 (executed sessions)",
            "F3": "accepted_C2 > 0 (executed sessions)",
        },
        "observed": {"C1": [c1_acc, c1_t], "C2": [c2_acc, c2_t], "C3": [c3_acc, c3_t], "C4": [c4_acc, c4_t]},
    }
    print("\n== falsifier checks ==")
    for k, v in fals.items():
        print(f"{k}: {v}")

    # read-only P010 comparison rows (never pooled; reported side by side only)
    p010 = None
    if (P010_DIR / "summary.json").exists():
        p010 = json.loads((P010_DIR / "summary.json").read_text())

    analysis = {
        "protocol": "P011-INFO-CONTRACT-2X2-RC4-v1",
        "sessions_recorded": len(res),
        "per_cell": {c: {"sessions": len(by_cell[c]),
                         "accepted": sum(r.get("status") == "SUCCESS" for r in by_cell[c]),
                         "seeds_accepted": [r["seed"] for r in by_cell[c] if r.get("status") == "SUCCESS"]}
                     for c in CELL_DESC},
        "marginals": {"R_plus": [rp_a, rp_t], "R_minus": [rm_a, rm_t],
                      "N_plus": [np_a, np_t], "N_minus": [nm_a, nm_t]},
        "fisher": {"R_one_sided": fp_r1, "R_two_sided": fp_r2, "N_one_sided": fp_n1, "N_two_sided": fp_n2},
        "paired_discordance": disc,
        "binom_C1_vs_C4_two_sided": pb,
        "failure_stages": {c: stage_by_cell.get(c, []) for c in CELL_DESC},
        "falsifiers": fals,
        "p010_summary_readonly_for_side_by_side": p010,
        "notes": [
            "Descriptive exact statistics only; n=16 detects only large effects (prespecified).",
            "Mechanism identification for one model/fixture/contract; no capability-rate claim; no alpha claim.",
            "Not pooled with P010, H1 V2, V4, historical, or post-freeze cohorts; side-by-side reporting only.",
        ],
    }
    (HERE / "ANALYSIS.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {HERE / 'ANALYSIS.json'}")


if __name__ == "__main__":
    sys.exit(main())
