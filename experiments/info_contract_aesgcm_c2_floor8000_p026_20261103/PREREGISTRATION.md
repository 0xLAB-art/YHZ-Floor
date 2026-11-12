# P026 — C2 floor-sensitivity (pre-registered before first call)

**Date**: 2026-11-03, before the first session runs.
**Basis**: `research_execution/EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md` — the
C2 `EMPTY_RESPONSE` signature (HTTP 200, `output_tokens` exactly 4200,
`stop_reason:"length"`, empty text block, 68/68 observations) and the causal
chain (withheld+bearing maximizes hidden deliberation; the route surfaces no
reasoning channel; the 4200 floor slices C2's deliberation distribution at ~53%).

## Manipulated factor — one, disclosed

The adapter floor only: `P017_TOKEN_FLOOR` 4200 → 8000
(`provider_adapter_agentrouter_p026_floor8000.py`, sha256-pinned in
`_REGISTRATION.json`; one-line delta from the frozen p023 adapter).

Everything else is carried over byte-identical from
`info_contract_aesgcm_random_p021ar_20261103`: the same 96 seeds (same
registration file), label `gpt-6-astra`, AES-GCM fixture, prompts, oracle,
4200-floor-irrelevant predicate, rotation position mapping (C2 only).

## Scope

C2 only (the only cell that floor-exhausts): 96 sessions.

## Falsifiable predictions

1. `EMPTY_RESPONSE` rate ≈ 0 at floor 8000. Any remainder is the deliberation
   tail beyond 8000 and is reported as such.
2. Acceptance remains 0/96 — the withheld premise strands the agent at any
   budget. If acceptance rises above 0, the floor was suppressing capability,
   and the information-contract interpretation must be revisited.
3. Recovered sessions are `ORACLE_FAIL` with full text; their output-token
   distribution completes the causal analysis (>4200 half).

## Reporting obligations

- Primary and floor-4200 counts side by side (per A3 discipline).
- Any session still empty at 8000 is reported with its exact `output_tokens`.
- The registered 4200 cohorts are untouched; no acceptance number from this
  cohort is merged into the primary analysis without separate disclosure.
