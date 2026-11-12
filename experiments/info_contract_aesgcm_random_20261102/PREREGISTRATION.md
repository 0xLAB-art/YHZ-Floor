# PREREGISTRATION — P018: AES-GCM on CSPRNG-drawn instances

**Namespace:** `sp2027/research_execution/info_contract_aesgcm_random_20261102/`
**Date:** 2026-11-02 · Written before any provider call under this protocol.
**Status:** registered; runner, adapter and seed receipt pinned in `_REGISTRATION.json`.

## 1. The defect this cohort addresses

P014/P016 used hand-declared contiguous seed blocks (401–416, 601–616). Each seed
deterministically expands to one fixture instance, so the cohort's replication unit was
a fixed instance, and the paired test was conditional on those instances. A reviewer is
entitled to read that as "the instances were arbitrary, and the reps are one instance
repeated". P017 fixed the token floor; it did not fix the sampling frame.

## 2. The single change: instance sampling

- **Seeds:** 24 values drawn from the OS CSPRNG by
  `research_execution/register_instance_seeds.py` **before this cohort existed**:
  `seeds_random_20261102T104901Z.json`, `seeds_sha256 = 4bc60999fa67…`.
  Disjointness against every `seeds` array already declared under
  `research_execution/**/_REGISTRATION.json` and `_LAUNCH.json` was checked at draw time
  (48 prior seeds, 6 sources) and is re-checked by `--verify`.
- **No re-draw, no reorder, no substitution** after the first provider call. The cohort
  consumes `draw_order` in order.
- **Unit of analysis:** the instance. Session-level turns are within-instance repetitions
  and estimate run-to-run variance only.

Everything else is held fixed: runner `run_info_contract_2x2_aesgcm.py` (SHA pinned,
byte-identical to P014/P016), adapter `provider_adapter_agentrouter_p017.py` at floor
**4200**, label `gpt-6-astra`, cells C1–C4, prompts, oracle, sandbox, 2 turns, 1400 max
tokens requested.

## 3. Design

- **Instances:** 24 (CSPRNG draw). **Sessions:** 4 × 24 = 96.
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−), rotations by instance index
  exactly as in P014/P016.
- **Provider failures:** terminal per session, never retried, never imputed.
- **Scheduling:** starts only after P017 exits, so one key never carries two cohorts.
  Same rule as P014→P016→P017.

## 4. Analysis plan (frozen before any call)

- **Primary:** paired C1-vs-C4 discordance over instances where **both** cells produced an
  evaluable verdict; exact binomial two-sided. *Direction replicated* iff b10 > b01 and
  p < 0.05.
- **Secondary (prespecified):** per-cell accepted/evaluable with Wilson 95% CIs; premise
  marginal (C1+C3 vs C2+C4), Fisher two-sided; terminal drops by cell, disclosed as a
  denominator effect.
- **Falsifiers:** (i) no evaluable C4 sessions at all — then the paired test is undefined
  and the cohort reports only the stated-arm rate; (ii) b01 ≥ b10 — the direction does not
  replicate under random instances.

No rate is pooled with P014, P016, P017, P019 or P020.

## 5. What this does not establish

Instance-level generalization to *all* AES-GCM nonce-reuse tasks — 24 draws estimate a
rate on that population only in the weak sense of a small sample; it is not a benchmark.
No provider or model-family claim: one route, one key, one label.
