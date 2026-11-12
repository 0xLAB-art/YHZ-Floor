# PREREGISTRATION — P022: cross-label repair cohort (two label arms, shared CSPRNG instances)

**Namespaces:** `info_contract_aesgcm_p022a_20261102/` (gpt-6.1-sol) and
`info_contract_aesgcm_p022b_20261102/` (gpt-5.6-sol). This document is
registered in both directories and applies to both arms; it is written before
any provider call under either protocol.
**Date:** 2026-11-02 · **Status:** registered; launcher, frozen runner,
adapter and shared seed receipt pinned in each `_REGISTRATION.json`.

## 1. The defect this cohort addresses

P016 reran the AES-GCM factorial cross-route but its gpt-5.6-sol arm lost
every withheld-arm session to terminal provider failures, so the second
label's generality on modern AEAD rests on one evaluable arm (gpt-6.1-sol,
8/0) and one unmeasured arm. P022 reruns the same comparison on CSPRNG-sampled
instances so the cross-label claim rests on random instances, not the
hand-declared seed blocks P016 inherited.

## 2. The single change: shared CSPRNG instances, two labels

- **Seeds:** 24 values drawn from the OS CSPRNG by
  `research_execution/register_instance_seeds.py` before this cohort existed:
  `seeds_random_p022_20261102T183823Z.json`,
  `seeds_sha256 = 4c3f863f366fb8765c96cb6cbed55c806e978890c58a31c64ab72b7a0098c334`.
  Disjointness checked at draw time (104+ prior seeds across 14 sources).
- **The same 24 instances run in BOTH arms** — a paired cross-label design:
  instance i's C1 result on label 1 is compared with instance i's C1 result on
  label 2. This is the one intentional change relative to P016 (which reused
  hand-declared seeds 601–616).
- **No re-draw, no reorder, no substitution** after the first provider call.

Everything else held fixed: frozen runner `run_info_contract_2x2_aesgcm.py`
(SHA pinned), adapter `provider_adapter_agentrouter_p017.py` at floor 4200,
cells C1–C4, prompts, oracle, sandbox, 2 turns, 1400 max tokens.

## 3. Design

- **Arm a:** gpt-6.1-sol, 24 instances × 4 cells = 96 sessions.
- **Arm b:** gpt-5.6-sol, same 24 instances × 4 cells = 96 sessions.
- **Provider failures:** terminal per session, never retried, never imputed.
  If an arm loses every withheld-arm session again, the arm is reported as
  unevaluable under the registered non-acceptance rule — a count, not a null.
- **Scheduling:** arm a launches only after P021 has fully exited and its
  analysis is written; arm b launches only after arm a has fully exited. One
  key never carries two cohorts. Estimated budget ≈ USD 10–13 total on the
  registered accounting basis; cumulative stays under the USD 200 hard stop.

## 4. Analysis plan (frozen before the first call)

- Per-arm: per-cell accepted/evaluable, paired C1-versus-C4 exact two-sided
  test on evaluable instance pairs, premise/naming marginals descriptive.
- **Registered primary:** per-arm paired C1-versus-C4 one-directional
  replication (b10 > b01, p < 0.05), as in every prior cohort.
- **Registered secondary (descriptive):** cross-arm agreement per instance —
  does instance i accepted on label a also accept on label b (and the
  withheld-arm mirror)? Reported as counts, no pooled test.
- Family placement: both arms enter the registered Holm family as
  pre-specified members (declared here, before any call).
- Provider failures reported per cell; attrition concentration tested
  stated-vs-withheld and reported either way.

## 5. Interpretation guards

No rate is pooled across cohorts or labels. Mechanism identification, never a
capability rate. A null or direction-reversed arm is reported as an honest
outcome and bounds the premise share to the labels measured.
