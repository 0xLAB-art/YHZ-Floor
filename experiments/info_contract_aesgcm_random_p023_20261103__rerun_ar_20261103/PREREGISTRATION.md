# PREREGISTRATION — P023: exact P021 re-run on a repaired transport

**Namespace:** `sp2027/research_execution/info_contract_aesgcm_random_p023_20261103/`
**Date:** 2026-11-03 · Written before any provider call under this protocol.
**Status:** registered; launcher (`run_p023_aesgcm.py`), frozen runner, adapter,
transport policy and seed receipt pinned in `_REGISTRATION.json`.

## 1. Why this cohort exists

P021 (same design, 96 CSPRNG instances, `gpt-6-astra`) lost **226 of 384
sessions** to terminal provider failures: 189 `HTTP_ERROR`, 35
`EMPTY_RESPONSE`, 2 `TIMEOUT`. The route was demonstrably up throughout (200s
interleaved with the failure bursts) and the failures arrived a median 2.25 s
after the request started. Because the P017 adapter recorded only a category,
the status and body needed to identify the cause were discarded.

Two defects are now established from the preserved smoke-test evidence:

1. **Router-injected parameter.** A live 400 returned
   `{"error":{"message":"Bad request: The 'stream_options' parameter is only
   allowed when 'stream' is enabled."}}` on a request that never sends
   `stream_options`. The router rejects its own injection before generation.
2. **Router-side 429/5xx and connection failures.** Fast, bursty, interleaved
   with successful 200s on the same key and model.

Neither defect is a property of the model or of the information condition.
P023 re-runs P021 exactly, on a transport that survives them.

## 2. The single change: transport layer, nothing the model sees

`provider_adapter_agentrouter_p023.py` is `provider_adapter_agentrouter_p017.py`
plus one registered layer:

- **Retried (transport only, no completion delivered):** connection errors,
  timeouts, HTTP 408/409/425/429/5xx/52x, a 200 whose body is not JSON, and a
  400 whose body carries a P023 retry marker (currently `stream_options`).
  At most **4 attempts**, fixed **2/5/12 s** backoff, no jitter.
- **Never retried (model-level outcomes):** `EMPTY_RESPONSE`,
  `INCOMPLETE_RESPONSE`, non-marker 4xx, and every oracle/parse outcome. Those
  remain terminal per session exactly as in P014–P022. Retrying them would
  resample the model, not repair transport.
- **Forensics:** every failed attempt appends one JSON line to
  `failure_log.jsonl` with attempt number, category, HTTP status and the first
  400 bytes of the body. P021 had no such record; that is why its cause was
  unrecoverable.

Byte-identical to P017 otherwise: floor **4200**, label `gpt-6-astra`, the
`claude-cli` User-Agent, `x-api-key` + Bearer, `/v1/messages`, 600 s timeout,
1400 max tokens requested.

## 3. Design (identical to P021)

- **Instances:** 96, drawn from the OS CSPRNG before this cohort existed:
  `seeds_random_20261103T080050Z.json`,
  `seeds_sha256 = 056aa34e8e53698220ee81288763db7ca6064c9069fd5b7197caddc13653d8ae`.
  Disjointness verified against **224** prior seeds across **18** record
  sources. No re-draw, no reorder, no substitution after the first call.
- **Sessions:** 4 × 96 = 384; cells C1–C4; rotations by instance index exactly
  as P014–P022; two turns; frozen runner
  `run_info_contract_2x2_aesgcm.py` (SHA pinned, unchanged).
- **Unit of analysis:** the instance. Turns are within-instance repetitions.

## 4. Analysis plan (frozen before the first call)

Frozen analyzer `analyze_random_cohort.py`, unchanged: per-cell
accepted/evaluable with Wilson 95% CIs; **registered primary** = paired
C1-versus-C4 exact two-sided binomial on evaluable instance pairs, replication
iff `b10 > b01` and `p < 0.05`; premise marginal (Fisher) and naming marginal
descriptive. Provider drops reported per cell as a denominator effect.

**Registered secondary (new, declared here):** transport-attempt counts and
failure-category counts per cell from `failure_log.jsonl`, reported to
document the repair. No retry statistic enters the primary test.

**Family placement:** P023 enters the registered Holm family as a
pre-specified member, declared before any call.

## 5. Interpretation guards

No rate is pooled across cohorts. P023 is a **re-run of the P021 design on a
repaired transport**, not a new capability measurement and not a replacement
for P021: both cohorts are reported, P021 with its 226 drop count. A null or
direction-reversed result is reported as an honest outcome.

## 6. Pre-launch gate (recorded before this document was finalised)

`smoke_p023_transport.py` ran 12 neutral calls (no P023 instance) through this
adapter: **12/12 completed** after the marker retry was added, median latency
5.9 s, zero unresolved transport failures. Evidence:
`smoke_p023_transport.json` + `smoke_p023_failures.jsonl`. The 96-seed draw was
taken **before** this gate was re-run, and no cohort call used a P023 seed
before this file existed.
