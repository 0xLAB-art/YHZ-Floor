# AMENDMENT — H2-CBC-PAIRS-EXT-20261024-v1

## A1 — Fisher exact denominator defect (post-hoc, post-outcomes; recorded 2026-10-24T07:35:58Z)

**Cause.** The Fisher exact implementation inherited the frozen cohort runner's denominator `comb(2n, n)`. Fisher's exact test conditions on the successes margin; the correct denominator is `comb(2n, total_successes)`. Discovered during report verification by an independent fraction-arithmetic cross-check against `scipy.stats.fisher_exact`: the defective two-sided value equals the correct one scaled by `comb(2n,T)/comb(2n,n)` — the numerator selection (pmf mass ≤ observed) was already correct.

**Lineage disclosure.** The same defect is present in the frozen cohort `H2-CBC-AGENCY-20261023-v1`: its REPORT.md §3 publishes the one-sided 4v4 p-value as 6/70 = 0.0857; the correct value is 6/28 = 0.214286 (scipy-verified). The frozen namespace is read-only and was NOT modified; the correction is recorded here and in this namespace's REPORT.md.

**Fix.** `_pmf`/`fisher_one_sided`/`fisher_two_sided` denominators → `comb(2n, T)`; aggregation extracted from `main()` into `aggregate()` so `summary.json` is regenerable without touching `run_info.json`, recorded sessions, or the ledger. Re-aggregation performed with the resume path not exercised at all (no session loop, zero provider calls).

**Impact.** None on session outcomes, terminal states, acceptance counts, error classes, query counts, tokens, cost, or the gate. Corrected statistics (scipy cross-check exact to machine precision):

- Extension 10v10 (A 5/10 vs B 7/10): one-sided (A>B) 115275/125970 = **0.915099**; two-sided **0.649917** (was 0.6239 / 0.4431 under the defective denominator).
- Combined descriptive 14v14 (A 9/14 vs B 9/14): one-sided **0.652708**; two-sided **1.0** (was 0.2135 / 0.3271).
- Frozen 4v4, corrected for reference: 6/28 = **0.214286** (published: 6/70 = 0.0857).

**Falsifier verdicts UNCHANGED.** F-primary rule = (corrected two-sided p ≥ 0.05 AND arm A turn-2 submissions = 0): 0.6499 ≥ 0.05 holds but turn-2 submissions = 3 → F-primary FALSE. F-secondary (no test) and F3 (no violation) unaffected.

**Runner sha256:** before `ac16e49841d85fe4a92247f5b2fcc3582a1a3e67ff14bae8fbae291d3e0f50f6` → after `d702512a5e79e3846e8bf76b33954ac0e5a71789640e01313157e1c0c0bcebc6`. `FREEZE.json` carries this amendment; every other frozen file hash is the freeze-commit value, re-verified at report time.
