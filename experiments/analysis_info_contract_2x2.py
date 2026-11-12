#!/usr/bin/env python3
"""P010-INFO-CONTRACT-2X2-CHACHA20-v1 analysis.

Reads info_contract_2x2_20261018/{results.jsonl,events.jsonl,summary.json}
and writes ANALYSIS.json + prints human-readable tables.

Descriptive exact statistics only (no alpha-level claims):
- Fisher exact one-sided hypergeometric for R marginal (R+ vs R-) and N marginal (N+ vs N-).
- Paired discordance counts by seed (McNemar-style descriptive).
"""
import json
import sys
from itertools import combinations
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "info_contract_2x2_20261018"

CELL_DESC = {
    "C1": "N+ R+ (named, zero-reference premise)   [historical default]",
    "C2": "N- R- (unnamed, no premise)               [historical blind + neutral sentence]",
    "C3": "N- R+ (unnamed, premise present)",
    "C4": "N+ R- (named, premise withheld)",
}
R_PLUS = ["C1", "C3"]
R_MINUS = ["C2", "C4"]
N_PLUS = ["C1", "C4"]
N_MINUS = ["C2", "C3"]


def rows(path):
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def fisher_one_sided(a_c, a_t, b_c, b_t):
    """P(X >= a_c) where group1 has a_t total, group2 b_t total, draws = a_c + b_c."""
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
    """Exact binomial two-sided p for discordant pairs b vs c (p=0.5 each)."""
    if b + c == 0:
        return None
    n = b + c
    probs = [comb(n, k) * 0.5 ** n for k in range(n + 1)]
    obs = probs[b]
    return min(1.0, sum(p for p in probs if p <= obs * (1 + 1e-9)))


def main():
    res = rows(OUT / "results.jsonl")
    events = rows(OUT / "events.jsonl")
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

    # marginals
    def accepted(cells):
        got = [r for r in res if r["cell"] in cells]
        return sum(r.get("status") == "SUCCESS" for r in got), len(got)

    rp_a, rp_t = accepted(R_PLUS)
    rm_a, rm_t = accepted(R_MINUS)
    np_a, np_t = accepted(N_PLUS)
    nm_a, nm_t = accepted(N_MINUS)
    print(f"\n== marginals ==")
    print(f"R+ (C1,C3): {rp_a}/{rp_t}; R- (C2,C4): {rm_a}/{rm_t}")
    print(f"N+ (C1,C4): {np_a}/{np_t}; N- (C2,C3): {nm_a}/{nm_t}")

    fp_r1 = fisher_one_sided(rp_a, rp_t, rm_a, rm_t)
    fp_r2 = fisher_two_sided(rp_a, rp_t, rm_a, rm_t)
    fp_n1 = fisher_one_sided(np_a, np_t, nm_a, nm_t)
    fp_n2 = fisher_two_sided(np_a, np_t, nm_a, nm_t)
    print(f"R marginal Fisher one-sided p={fp_r1:.4f} two-sided p={fp_r2:.4f}" if fp_r1 is not None else "R marginal: insufficient data")
    print(f"N marginal Fisher one-sided p={fp_n1:.4f} two-sided p={fp_n2:.4f}" if fp_n1 is not None else "N marginal: insufficient data")

    # paired discordance (R+ vs R-, within seed: compare C1 vs C4 and C3 vs C2)
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
    b, c = disc["C1> C4"], disc["C4> C1"]
    pb = binom_two_sided(b, c)
    print(f"C1 vs C4 discordant b={b} c={c}; exact binomial two-sided p={pb}")

    # failure stages per cell from events
    print("\n== rejected-verdict failure stages (events) ==")
    stage_by_cell = {}
    for e in events:
        if e.get("kind") == "oracle_verdict" and e.get("verdict") == "rejected":
            stage_by_cell.setdefault(e.get("cell"), []).append(e.get("failure_stage"))
    for c in ("C1", "C2", "C3", "C4"):
        print(f"{c}: {stage_by_cell.get(c, [])}")

    # falsifier verdicts (computed on available data)
    c1_acc = sum(r.get("status") == "SUCCESS" for r in by_cell["C1"])
    c2_acc = sum(r.get("status") == "SUCCESS" for r in by_cell["C2"])
    c3_acc = sum(r.get("status") == "SUCCESS" for r in by_cell["C3"])
    c4_acc = sum(r.get("status") == "SUCCESS" for r in by_cell["C4"])
    fals = {
        "F1_C4_approximates_C1": (c4_acc == c1_acc),
        "F2_C3_fails_while_C1_succeeds": (c3_acc < len(by_cell["C3"]) and c1_acc > 0),
        "F3_C2_succeeds_premise_not_necessary": (c2_acc > 0),
        "observed": {"C1": c1_acc, "C2": c2_acc, "C3": c3_acc, "C4": c4_acc},
    }
    print("\n== falsifier checks ==")
    for k, v in fals.items():
        print(f"{k}: {v}")

    analysis = {
        "protocol": "P010-INFO-CONTRACT-2X2-CHACHA20-v1",
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
        "notes": [
            "Descriptive exact statistics only; n=16 detects only large effects (prespecified).",
            "Mechanism identification for one model/fixture/contract; no capability-rate claim.",
            "Not pooled with H1 V2, V4, historical, or post-freeze cohorts.",
        ],
    }
    (OUT / "ANALYSIS.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {OUT / 'ANALYSIS.json'}")


if __name__ == "__main__":
    sys.exit(main())
