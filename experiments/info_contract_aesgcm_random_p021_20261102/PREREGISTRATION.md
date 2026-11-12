# PREREGISTRATION — P021: AES-GCM power cohort on CSPRNG-drawn instances

**Namespace:** `sp2027/research_execution/info_contract_aesgcm_random_p021_20261102/`
**Date:** 2026-11-02 · Written before any provider call under this protocol.
**Status:** registered; launcher (`run_p021_aesgcm.py`), frozen runner, adapter and
seed receipt pinned in `_REGISTRATION.json`.

## 1. The defect this cohort addresses

P018 answered the sampling-frame objection (hand-declared seed blocks) with 24
CSPRNG instances: direction replicated, but per-cell $n$ stayed small
(13–24 evaluable), so the small-sample objection survives in weakened form.
P011-L3-N32 raised per-cell $n$ to 32 on ChaCha20 but kept hand-declared
seeds. No cohort has yet combined **CSPRNG instance sampling** with
**power-sized per-cell $n$**. P021 is that cohort.

## 2. The single change: cohort size

- **Seeds:** 96 values drawn from the OS CSPRNG by
  `research_execution/register_instance_seeds.py` **before this cohort
  existed**: `seeds_random_p021_20261102T182345Z.json`,
  `seeds_sha256 = 07a9e4422a0c7b7f72453a8dadc3104aba7454e5b1f605ac39661b24b820f867`.
  Disjointness against every seed already declared under
  `research_execution/**/_REGISTRATION.json` and `_LAUNCH.json` was checked at
  draw time (104 prior seeds, 12 sources).
- **No re-draw, no reorder, no substitution** after the first provider call.
  The cohort consumes `draw_order` in order.
- **Unit of analysis:** the instance. Session-level turns are
  within-instance repetitions and estimate run-to-run variance only.

Everything else is held fixed: frozen runner `run_info_contract_2x2_aesgcm.py`
(SHA pinned, byte-identical to P014/P016/P017/P018), adapter
`provider_adapter_agentrouter_p017.py` at floor **4200**, label
`gpt-6-astra`, cells C1–C4, prompts, oracle, sandbox, 2 turns, 1400 max
tokens requested.

## 3. Design

- **Instances:** 96 (CSPRNG draw). **Sessions:** 4 × 96 = 384.
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−), rotations by
  instance index exactly as in P014–P020.
- **Provider failures:** terminal per session, never retried, never imputed.
- **Scheduling:** launched only after the P018→P019→P020 chain exits, so one
  key never carries two cohorts. Budget: estimated ≈ USD 21 on the same
  accounting basis; cumulative stays under the USD 200 hard stop.

## 4. Analysis plan (frozen before the first call)

- Estimator: `analyze_p017.py`-equivalent per-cell accepted/evaluable counts,
  paired C1-versus-C4 exact binomial on evaluable instance pairs, premise and
  naming marginals (descriptive), Wilson 95% CIs per cohort.
- **Registered primary:** the paired C1-versus-C4 exact two-sided test on
  evaluable instance pairs. At 96 instances with no ties the resolution is
  $p = 2\times2^{-96}$; the registered interpretation is one-directional
  replication (b10 > b01 and $p<0.05$), never a capability rate.
- **Family placement:** this cohort enters the registered Holm family as a
  pre-specified member (declared here, before any call), keeping the
  family-exhaustive guard intact.
- Provider failures are reported as counts per cell; attrition concentration
  is tested stated-vs-withheld (the P017 rule) and reported either way.

## 5. Interpretation guards

No rate is pooled across cohorts. The cohort estimates mechanism
identification, not capability. A null or direction-reversed result is
reported as an honest outcome and bounds the premise share on this
fixture/label pairing.
