# PREREGISTRATION — P024: paired re-run of P022 on the repaired transport

**Namespaces:** `info_contract_aesgcm_p024a_20261103/` (gpt-6.1-sol) and
`info_contract_aesgcm_p024b_20261103/` (gpt-5.6-sol). This document is
registered in both directories and applies to both arms. Written before any
P024 provider call; the floor probe it defines runs on a spent P022 instance,
not on P024 data.
**Date:** 2026-11-03.

## 1. Why this cohort exists

P022 ran the paired cross-label comparison, but both arms were collected on a
transport that was demonstrably failing P021: P022a lost 13 sessions to
`HTTP_ERROR`/`EMPTY_RESPONSE` (all in C2) and P022b lost **48 of 96** sessions,
every one of them a textless completion in C2 or C4. The cross-label secondary
therefore rests on 0 evaluable withheld sessions for arm b.

The P023 post-mortem established the transport defect: the router injects
`stream_options` into non-streaming requests and answers its own injection with
HTTP 400, plus bursty 429/5xx. P024 re-runs P022 with that repaired.

## 2. What changes, and what does not

**Changed (transport and instrumentation only):**
- `provider_adapter_agentrouter_p024.py` = P023 transport (4 attempts, fixed
  2/5/12 s backoff, transport-only retry, failure forensics).
- **Textless attribution fix:** P017–P023 raised `EMPTY_RESPONSE` before reading
  `stop_reason`, so a reasoning pass that consumed the whole ceiling was
  recorded as "empty". P024 checks `stop_reason` first: textless +
  `max_tokens`/`length` → `INCOMPLETE_RESPONSE`, only a textless completion that
  stopped on its own → `EMPTY_RESPONSE`. Both remain terminal; the denominator
  is unchanged and only the attribution improves.
- **Failure log now records** `stop_reason`, `usage`, content-block types and a
  body excerpt, so a textless completion is classified from the record instead
  of being replayed blind.

**Unchanged:** frozen runner `run_info_contract_2x2_aesgcm.py` (SHA pinned),
cells C1–C4, prompts, oracle, sandbox, rotations, two turns, 1400 max tokens
requested, analysis script, and the paired design (the same instances in both
arms).

## 3. Token floor: probed, not assumed

P022b produced 48 textless completions at floor 4200 and left no body, so the
cause was unattributable. P024 fixes the floor **before** its first call with a
pre-registered diagnostic on **one already-spent P022 instance** (seed
2984588382247702924, its C2 condition, `gpt-5.6-sol`), at two ceilings:

- **4200** — the P022 floor;
- **8400** — one doubling, chosen before the probe, not fitted to it.

Decision rule, fixed here before the probe ran:

| probe outcome | floor |
|---|---|
| text at 4200 | **4200** |
| no text at 4200, text at 8400 | **8400** |
| no text at either ceiling | **4200**, arm b flagged as an expected model-level null |

The decided floor is applied **uniformly to both arms and all four cells**, so
no cell and no arm receives a budget advantage. The probe sample enters no
analysis and uses no P024 seed. Evidence: `probe_p024_floor.json`, digested into
each arm's `_REGISTRATION.json`.

## 4. Design (identical to P022)

- **Instances:** 24 drawn from the OS CSPRNG before this cohort existed:
  `seeds_random_p024_20261103.json`,
  `seeds_sha256 = 2dc0653f256e0cf5c0fdb7b0c03f3c737240032e1d66b32d82f2cc16c3b9b217`;
  disjoint from **320** prior seeds across **20** record sources. The same 24
  run in both arms; no re-draw, reorder or substitution after the first call.
- **Arm a:** gpt-6.1-sol, 24 × 4 = 96 sessions. **Arm b:** gpt-5.6-sol, same 24
  instances, 96 sessions. **Unit of analysis:** the instance.
- **Serialization:** arm a runs after P023 exits; arm b runs after arm a exits.
  One key never carries two cohorts.

## 5. Analysis plan (frozen before the first call)

- **Primary per arm:** paired C1-versus-C4 exact two-sided binomial on evaluable
  instance pairs; replication iff `b10 > b01` and `p < 0.05`, as in every prior
  cohort. No pooling across cohorts or labels.
- **Registered secondary (descriptive):** cross-arm agreement per instance, as
  in P022. Reported as counts; no pooled test.
- **Registered secondary (new):** transport attempts and failure categories per
  cell from `failure_log.jsonl`, to document the repair. Not part of the
  primary test.
- Provider drops reported per cell as a denominator effect, never imputed.

## 6. Interpretation guards

P024 is a **re-run of P022 on a repaired transport**, not a new capability
measurement. P022 remains reported with its 48-session loss; P024 does not
replace it. A textless completion that survives the probe and the repaired
transport is a genuine model-level outcome for that label and condition, and is
reported as such. A null or direction-reversed arm is an honest result and
bounds the premise share to the labels measured.
