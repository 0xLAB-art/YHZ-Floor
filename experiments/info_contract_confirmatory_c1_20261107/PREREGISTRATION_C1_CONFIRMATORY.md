# PREREGISTRATION — C1: confirmatory information-contract cohort (Holm family declared up front)

**Protocol:** P010-INFO-CONTRACT-2X2-CHACHA20-CONFIRMATORY-C1-v1 · **Namespace:** `info_contract_confirmatory_c1_20261107` · **Registered:** 2026-11-07, before the first model call.

## 1. The commitment this executes

Registered follow-up commitment (C1), Section 11: *"One confirmatory cohort with the Holm family declared and hashed before its first model call."* This document declares that family, hashes it (via FREEZE_C1.json over this file, the runner, the analysis script, and the P009 dependency chain), and commits to quoting only the registered script's output.

## 2. Design

- **Fixture/protocol:** the frozen ChaCha20 2×2 information-contract protocol verbatim (`run_info_contract_2x2_chacha20.py`, protocol P010-v1): same four cells (C1 = A+ B+, C2 = A− B−, C3 = A− B+, C4 = A+ B−), same Latin-square rotation, same prompt slots, same P009 fixture/oracle/policy/feedback/turn flow, same 2-turn limit and submission policy.
- **The single disclosed harness delta:** the transport is the agentrouter Anthropic-messages client (route-default temperature, uniform across cells — the Amend-4 prereg amendments 1–2 constraint) and the token floor is **8400** (the P024-registered doubled floor; the 4200 floor confounds the withheld arm with floor-exhaustion, and P026's registered reading shows acceptance stays zero at both floors). The namespace-local P009 dependency copy has ONE disclosed line-diff: the dead `h1_campaign`/ECDSA import is removed (ChaCha20-only cohort; the ECDSA branch raises if ever reached).
- **Seeds:** 425–440 (16 seeds × 4 cells = **64 sessions**; sweep-verified free; `instance(seed)` is deterministic per seed — no per-seed randomness beyond the fixture).
- **Label:** `gpt-5.6-sol`, route-default temperature, single-label cohort (never pooled with any other cohort).

## 3. THE HOLM FAMILY — declared and hashed before the first model call

The cohort's registered tests, computed only by the frozen script
`c1_holm_analysis.py` on the frozen `results.jsonl` rows:

| # | test | definition |
|---|---|---|
| H1 (PRIMARY) | paired C1-vs-C4 discordance | exact two-sided binomial on the one-directional discordance count over evaluable C1/C4 pairs (a session with no accepted program on either side is a tie, not a scored non-acceptance) |
| H2 | premise marginal | Fisher exact, one-sided: accepted sessions in premise-stated cells (C1+C3) vs withheld cells (C2+C4) |
| H3 | naming marginal | Fisher exact, two-sided: accepted sessions in named cells (C1+C4) vs unnamed (C2+C3) |

**m = 3. Holm step-down at FWER 0.05 within this family:** sort the three
p-values ascending; p(1) × 3, p(2) × 2, p(3) × 1, each compared to 0.05 with
step-down monotonicity. **Registered bar:** H1 clears Holm within the family.
No other test is registered; no pooled statistic is computed; the cohort is
never pooled with any other cohort.

## 4. Verdict semantics

- **Confirmatory success:** H1 Holm-significant AND one-directional (every
  evaluable pair discordant in the C1-solves/C4-fails direction — ties
  allowed, no counter-directional discordance).
- **Any other outcome** is reported as measured (the confirmatory cohort is
  a test, not a replication requirement).
- The premise/naming marginals are reported under the same Holm family for
  completeness; they are supportive, not the registered bar.

## 5. Operational rules (frozen)

- Transport: agentrouter Anthropic-messages client (the Amend-4 client,
  hash-registered); route-default temperature; AUTH_SMOKE before the run
  (HEALTH.json, non-evidence).
- Halt rule: ≥3 consecutive provider-side pre-output failures ⇒ halted;
  resume cycles append-only.
- Cost ceiling: 1,500,000 output tokens for the wave, enforced live.
- Freeze: `FREEZE_C1.json` over this preregistration, the runner, the
  client, the P009 dependency chain (with the disclosed single-line ECDSA
  removal), `c1_holm_analysis.py`, and `PROMPT_HASHES_C1.json`. The
  namespace-restricted commit is the registration act; live mode refuses
  without `FREEZE_COMMIT_C1.txt`.
