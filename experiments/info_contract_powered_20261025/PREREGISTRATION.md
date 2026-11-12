# PREREGISTRATION — P010P: powered same-label replication of the information-contract 2×2

**Namespace:** `sp2027/research_execution/info_contract_powered_20261025/`
**Date:** 2026-10-25 · Written before any provider call under this protocol.
**Motivation:** the 2026-10-25 five-referee panel (REVIEW_PANEL_20261025.md in
the paper directory) converged on one statistical requirement: the RQ2
interaction claim ("the cell collapses only under the
named-with-unstated-premise conjunction") is asserted at n=4 per cell with
paired discordance 4/0 (two-sided p=0.125) and no powered interaction test.
This cohort supplies the powered test.

## 1. Design (frozen)

- **Protocol:** P010's frozen runner, imported byte-for-byte
  (`run_info_contract_2x2_chacha20.py`, SHA-256 `a08eab6f…83ee198`, asserted
  at launch) and driven by a wrapper that changes ONLY the output namespace,
  the protocol label, the seed list, and the Latin-square rotation applied
  modulo 4. Prompts, cell slots, fixture, oracle, policy, feedback strings,
  max_tokens=1400, temperature provider-default, and turn flow are the frozen
  module's own code, unchanged. Wrapper resume rule: seed granularity
  (disclosed in the wrapper docstring; duplicate (seed, cell) rows from a
  partial-seed rerun are resolved in analysis by keeping the earliest row and
  flagging later ones as instrument duplicates — recorded, never deleted).
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−) — identical slots.
- **Seeds:** 101–108 (8 fresh seeds; verified unused by the standard search
  over preregistrations/results under sp2027/). Two balanced Latin squares
  (rotation index = seed index mod 4).
- **Sessions:** 4 cells × 8 seeds = 32 sessions; ≤2 turns; one provider call
  per turn.
- **Model label:** `claude-sonnet-4-6-free` (the only label the provider
  exposes — probed 2026-10-25, `/v1/models` returns exactly one entry; the
  second-label replication requested by the panel remains registered future
  work and is NOT executed here).
- **RC4 fixture:** NOT re-run. The P011 RC4 cohort was saturated (16/16
  first-turn), so additional RC4 sessions cannot detect an effect; spending
  sessions there adds no information. Recorded as a design decision, not an
  omission.

## 2. Primary and secondary analyses (frozen before any call)

- **Primary (the panel's requirement):** paired C1-vs-C4 discordance on the 8
  shared seeds, exact binomial two-sided. At n=8 the test can actually reach
  conventional significance under the P010 effect shape (8-vs-0 discordance →
  two-sided p = 2·(1/2)⁸ = 0.0078). Reported with the full discordance count,
  not a threshold verdict.
- **Secondary (all descriptive, prespecified):** per-cell acceptance with
  submissions/turns; premise marginal (C1+C3 vs C2+C4) and naming marginal
  (C1+C4 vs C2+C3), Fisher exact one- and two-sided; interaction reading
  stated as the cell-pattern description with the paired test carrying the
  inferential weight; submissions cost of C2 vs C1.
- **Falsifiers (prespecified, mirroring P010's at n=8):**
  - F1: C4 succeeds about as often as C1 (honest null replicates) → verdict
    by paired discordance ≤ 2 of 8.
  - F2: C3 fails while C1 succeeds → naming gates when premise stated.
  - F3: C2 succeeds → derive frame sustains success without the premise.
- **Cross-cohort comparison with P010:** side-by-side descriptive table only;
  a combined-cohort exact test is preregistered as a SECONDARY descriptive
  statistic (Mantel-Haenszel-free simple pooled Fisher, labeled
  cross-cohort-descriptive, no capability-rate claim); no averaging of
  rates.

## 3. Discipline

AUTH_SMOKE health probe (16 tokens, non-evidence) precedes the first
experiment call and is logged in `HEALTH.json`. Provider failures are
terminal per session (PROVIDER_UNAVAILABLE et al.), never retried; if most
consecutive sessions fail on the provider, the launch stops with status
halted. Cost ceiling $5 estimated. Every call's tokens/cost appended to
`sp2027/research_execution/BUDGET_LEDGER.jsonl`. Git: freeze commit before
the first experiment call; namespace-restricted commits. Never pooled with
P010/P011/H1/V4 or any cohort except the prespecified secondary
cross-cohort descriptive test above.
