# PREREGISTRATION — P010N16: per-cell n=16 increase of the information-contract 2×2

**Namespace:** `sp2027/research_execution/info_contract_n16_20261026/`
**Date:** 2026-10-26 · Written before any provider call under this protocol
(the only call made so far is the 16-token AUTH_SMOKE health probe, logged
`HEALTH.json`, `evidence: false`).

**Motivation.** `REVISION_NOTES_20261026.md` §"Still open" item 1: the
paper's information-contract headline currently rests on 5 discordant pairs
(P010P, n=8/cell) and 8 discordant pairs (P010L2, n=8/cell). The exact
paired test's floor at those sizes is disclosed but thin (p=0.0625 and
p=0.0078). This cohort doubles per-cell n on the PRIMARY label so the
registered paired test has real resolution. Item 2 of that list (an
open-weight, digest-pinned model cohort) is explicitly **declined by
decision**: this project has never executed a local/open-weight model —
every cohort in its record ran through an API provider route — so an
open-weight cohort would introduce a first-of-kind execution path rather
than close the attestation gap. The gap stays disclosed in §11 limits as
already written; no local-model work is performed here.

## 1. Design (frozen)

- **Protocol:** P010's frozen runner, imported byte-for-byte
  (`run_info_contract_2x2_chacha20.py`, SHA-256 `a08eab6f…83ee198`,
  asserted at launch) and driven by a wrapper that changes ONLY the output
  namespace, the protocol label, the seed list, and the Latin-square
  rotation applied modulo 4. Prompts, cell slots, fixture, oracle, policy,
  feedback strings, max_tokens=1400, temperature provider-default, and turn
  flow are the frozen module's own code, unchanged. Wrapper resume rule:
  seed granularity (disclosed in the wrapper docstring; duplicate
  (seed, cell) rows from a partial-seed rerun are resolved in analysis by
  keeping the earliest row and flagging later ones as instrument duplicates
  — recorded, never deleted).
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−) — identical slots.
- **Seeds:** 121–136 (16 fresh seeds; verified unused by search over
  preregistrations and results under `sp2027/`). Four balanced Latin squares
  (rotation index = seed index mod 4).
- **Sessions:** 4 cells × 16 seeds = 64 sessions; ≤2 turns; one provider
  call per turn.
- **Model label:** `claude-sonnet-4-6-free` via `https://api.apmix.ai`
  (the primary label of P010/P010P; route attested in `HEALTH.json` — the
  provider exposes exactly one label). **No open-weight/local model is
  used anywhere in this cohort** (decision above).
- **Fixtures:** ChaCha20 only. RC4 is not re-run (P011 saturated 16/16 —
  recorded design decision, as in P010P). The second label (P010L2,
  gpt-6.1-sol) is not re-run here; its n-increase, if ever executed, is
  separate registered future work.

## 2. Primary and secondary analyses (frozen before any call)

- **Primary:** paired C1-vs-C4 discordance on the 16 shared seeds, exact
  binomial two-sided. At n=16 discordance 8-vs-0 gives p=2·(1/2)⁸=0.0078,
  16-vs-0 gives p=2·(1/2)¹⁶≈3.05e-5. Reported with the full discordance
  count, not a threshold verdict.
- **Secondary (all descriptive, prespecified):** per-cell acceptance with
  submissions/turns; premise marginal (C1+C3 vs C2+C4) and naming marginal
  (C1+C4 vs C2+C3), Fisher exact one- and two-sided; interaction reading
  stated as the cell-pattern description with the paired test carrying the
  inferential weight; submissions cost of C2 vs C1.
- **Cross-cohort view (prespecified, descriptive only):** side-by-side
  table against P010 (n=4), P010P (n=8), P010L2 (n=8), drift-check (n=4,
  post-hoc rerun). A simple pooled Fisher on premise-marginal counts is
  reported ONLY as a cross-cohort-descriptive statistic (as P010P did),
  never as a capability rate and never averaged across labels.
- **Falsifiers (prespecified, mirroring prior cohorts at n=16):**
  - F1: C4 succeeds about as often as C1 (honest null replicates) → verdict
    by paired discordance ≤ 4 of 16.
  - F2: C3 fails while C1 succeeds → naming gates when premise stated.
  - F3: C2 succeeds at a rate near C1 → derive frame sustains success
    without the premise (read against P010P 0/8, P010L2 0/8).

## 3. Discipline

AUTH_SMOKE health probe (16 tokens, non-evidence) precedes the first
experiment call and is logged in `HEALTH.json`. Provider failures are
terminal per session (PROVIDER_UNAVAILABLE et al.), never retried; if most
consecutive sessions fail on the provider, the launch stops with status
halted. Cost ceiling $5 estimated (prior32-session cohort cost $0.22 on
this route; 64 sessions expected ≈ $0.5). Every call's tokens/cost appended
to `sp2027/research_execution/BUDGET_LEDGER.jsonl`. Git: freeze commit
before the first experiment call; namespace-restricted commits. Never pooled
with P010/P010P/P010L2/P011/H1/V4 or any cohort except the prespecified
cross-cohort descriptive table above. Leak scan over all prompt files before
analysis (truth must appear in zero prompts).
