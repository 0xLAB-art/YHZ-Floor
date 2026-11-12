#!/usr/bin/env python3
"""Stats for P010N16 paper integration. Validates CMH/permutation methods
against the previously reported P010+P010P combined values (chi2=21.15,
p=4.3e-6; exact permutation p=1.0e-6) before computing new ones."""
import json, math, itertools
from pathlib import Path
from scipy.stats import fisher_exact, chi2

ROOT = Path("/mnt/nvme5/ACTS-Attack/sp2027/research_execution")

def rows(ns):
    out = []
    for line in (ROOT / ns / "results.jsonl").read_text().splitlines():
        if line.strip():
            out.append(json.loads(line))
    # earliest per (seed, cell)
    seen = {}
    for r in out:
        seen.setdefault((r["seed"], r["cell"]), r)
    return list(seen.values())

def fisher(a, b, c, d):
    _, two = fisher_exact([[a, b], [c, d]])
    _, one = fisher_exact([[a, b], [c, d]], alternative="greater")
    return one, two

def cmh(strata, continuity=False):
    """strata: list of (a_success_stated, n_stated, c_success_unstated, n_unstated)"""
    num = 0.0; den = 0.0
    for a, m1, c, m2 in strata:
        n = m1 + m2; r1 = a + c; r2 = (m1 - a) + (m2 - c)
        if n <= 1 or r1 == 0 or r2 == 0:
            E = m1 * r1 / n if n else 0
            V = 0.0
        else:
            E = m1 * r1 / n
            V = m1 * m2 * r1 * r2 / (n * n * (n - 1))
        num += a - E
        den += V
    if den == 0:
        return float("nan"), float("nan")
    if continuity:
        x = max(0.0, abs(num) - 0.5) ** 2 / den
    else:
        x = num * num / den
    return x, chi2.sf(x, 1)

def perm_exact(strata, t_obs):
    """Exact permutation: within each stratum stated-successes ~ Hypergeom.
    DP over convolution of per-stratum distributions. One-sided P(T >= t_obs)."""
    dist = {0: 1.0}
    for a, m1, c, m2 in strata:
        n = m1 + m2; k = a + c
        # P(X = x) = C(k, x) C(n-k, m1-x) / C(n, m1)
        support = {}
        lo = max(0, m1 - (n - k)); hi = min(k, m1)
        for x in range(lo, hi + 1):
            if 0 <= x <= k and 0 <= m1 - x <= n - k:
                p = (math.comb(k, x) * math.comb(n - k, m1 - x)) / math.comb(n, m1)
                if p > 0:
                    support[x] = p
        new = {}
        for s0, p0 in dist.items():
            for x, px in support.items():
                new[s0 + x] = new.get(s0 + x, 0.0) + p0 * px
        dist = new
    return sum(p for s, p in dist.items() if s >= t_obs)

def strata_from(rs, seeds=None):
    out = []
    by = {}
    for r in rs:
        by.setdefault(r["seed"], {})[r["cell"]] = r["status"] == "SUCCESS"
    for s in sorted(by):
        if seeds and s not in seeds:
            continue
        d = by[s]
        stated = [d.get("C1", False), d.get("C3", False)]
        unst = [d.get("C2", False), d.get("C4", False)]
        out.append((sum(stated), len(stated), sum(unst), len(unst)))
    return out

p010 = rows("info_contract_2x2_20261018")
p010p = rows("info_contract_powered_20261025")
n16 = rows("info_contract_n16_20261026")
p010l2 = rows("info_contract_label2_20261025")

def counts(rs):
    acc = {}; subs = {}
    for r in rs:
        acc.setdefault(r["cell"], 0)
        subs.setdefault(r["cell"], 0)
        if r["status"] == "SUCCESS":
            acc[r["cell"]] += 1
        subs[r["cell"]] += r["submissions"]
    return acc, subs

acc16, subs16 = counts(n16)
print("N16 per-cell:", acc16, "subs:", subs16)

one, two = fisher(32, 0, 9, 23)
print(f"N16 premise 32/32 vs 9/32: one={one:.6g} two={two:.6g}")
one_n, two_n = fisher(22, 10, 19, 13)
print(f"N16 naming 22/32 vs 19/32: one={one_n:.6g} two={two_n:.6g}")

# paired C1 vs C4 in N16
c1w = c4w = ties = 0
by = {}
for r in n16:
    by.setdefault(r["seed"], {})[r["cell"]] = r["status"] == "SUCCESS"
for s, d in by.items():
    a, b = d.get("C1", False), d.get("C4", False)
    if a and not b: c1w += 1
    elif b and not a: c4w += 1
    else: ties += 1
disc = c1w + c4w
p_disc = min(1.0, 2 * sum(math.comb(disc, i) for i in range(0, min(c4w, c1w) + 1)) / 2**disc)
print(f"N16 paired C1-vs-C4: {c1w}/{c4w} ties={ties} disc={disc} two-sided p={p_disc:.6g}  fmt4={2*0.5**10:.4g}")

# CMH within N16 (strata = seeds)
st = strata_from(n16)
x, p = cmh(st); xc, pc = cmh(st, continuity=True)
print(f"N16 CMH: no-cc chi2={x:.4g} p={p:.4g} | cc chi2={xc:.4g} p={pc:.4g}")

# Validate old combined (P010+P010P): reported chi2=21.15 p=4.3e-6, perm p=1.0e-6
st_old = strata_from(p010) + strata_from(p010p)
x, p = cmh(st_old); xc, pc = cmh(st_old, continuity=True)
t_old = sum(a for a, _, _, _ in st_old)
print(f"OLD combined CMH: no-cc chi2={x:.4g} p={p:.4g} | cc chi2={xc:.4g} p={pc:.4g} T_obs={t_old}")
print(f"OLD combined perm exact one-sided p={perm_exact(st_old, t_old):.6g}")

# New combined (P010+P010P+N16)
st_new = st_old + st
x, p = cmh(st_new); xc, pc = cmh(st_new, continuity=True)
t_new = sum(a for a, _, _, _ in st_new)
print(f"NEW combined CMH: no-cc chi2={x:.4g} p={p:.4g} | cc chi2={xc:.4g} p={pc:.4g} T_obs={t_new}")
print(f"NEW combined perm exact one-sided p={perm_exact(st_new, t_new):.6g}")

one_c, two_c = fisher(56, 0, 16, 40)
print(f"NEW combined fisher 56/56 vs 16/56: one={one_c:.6g} two={two_c:.6g}")

# per-seed table rows for S30
print("\n--- N16 per-seed rows ---")
for s in range(121, 137):
    cells = {r["cell"]: r for r in n16 if r["seed"] == s}
    print(s, " & ".join(f"{cells[c]['status'].replace('_','\\_')} {cells[c]['submissions']}/{cells[c]['turns']}" for c in ("C1","C2","C3","C4")))

# second-label + original for cross-cohort table sanity
a1, _ = counts(p010); aL2, _ = counts(p010l2); aP, sP = counts(p010p)
print("P010:", a1, "P010P:", aP, "subs P010P:", sP, "L2:", aL2)
