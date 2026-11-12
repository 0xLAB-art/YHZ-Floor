# P021/R — re-run of P021 on APINEX (registered 2026-11-03, before the run)

## Why this exists

`CENSUS_P_PROVIDER_20261103.md` found that P021 lost **189 of its 384 sessions** to
AgentRouter provider failures, including **86 of the 192 oracle-bearing sessions**
(C1 and C3). Every lost session carries a `provider_failure` event on the same seed
in the same cell, so none of the loss is model or runner behaviour. A cohort in which
45% of the oracle-bearing sessions never ran cannot carry the acceptance rate it
reports.

This namespace re-runs P021 **in full**, not as a top-up. A top-up would leave the
surviving half on AgentRouter and the new half on APINEX, and the resulting estimate
would be a mixture of two transport stacks — a worse defect than the one being fixed.

## What is held identical

| Element | Value |
|---|---|
| Frozen runner | `run_info_contract_2x2_aesgcm.py`, sha256 `cf0a806a…4afb9` (asserted at launch against both registrations) |
| Seeds | the original P021 list of 96 CSPRNG instances, sha256 `07a9e442…f867` |
| Cells and rotation | C1–C4, rotation identical to P021 |
| Prompt bytes, feedback strings, policy | untouched, from the frozen runner |
| Oracle and predicate | untouched |
| Token floor | 4200, unchanged |
| Session status vocabulary | unchanged |

## What differs, disclosed

1. **Transport.** APINEX OpenAI-compatible `/v1/chat/completions` instead of
   AgentRouter's Anthropic `/v1/messages`. The adapter is
   `provider_adapter_apinex_p021.py`, interface-identical to the frozen adapter.
2. **Label.** `free/gpt-6-luna` instead of `gpt-6-astra`. This is forced: APINEX
   serves no free `gpt-6-astra`, and the paid listing returns `HTTP 402`
   (insufficient balance) on this account. The substitute is the same vendor
   family; the re-run is a **cross-model replication of P021's design**, not a
   byte-identical repeat.
3. **Scheduling.** 10-worker thread pool (`parallelize_cohort.py`), as in
   P023/P024; each row carries `execution_concurrency` and `execution_phase`.
4. **Pacing.** The account's free plan allows 15 requests/minute. The adapter
   paces to 12 requests/minute and retries `429` up to 4 times with backoff, so
   the cohort does not inherit rate-limit storms as session failures. Attempts
   made are recorded per call as `rate_limit_retries`.

## Predictions carried over from P021

The bearing cells (C1, C3) accept; the withheld cells (C2, C4) do not. P021
observed 106/106 accepted across C1+C3 and 0/152 across C2+C4. Any acceptance in
C2 or C4 would contradict the information-contract reading and must be reported as
such, not smoothed.

## What would falsify the re-run's usefulness

- C1/C3 acceptance near zero (would mean the substitute label cannot do the task,
  and the re-run says nothing about P021's design);
- provider failure rate above 5% of sessions (would mean the transport is still
  unfit and the cohort must be re-launched, not analysed);
- any acceptance in C2/C4 (would mean the withheld cells leak, contradicting the
  original).

## Instrument test discarded before this registration

A 6-seed smoke run was executed with no pacing and produced 20 `HTTP_ERROR` (429)
sessions. Those rows were deleted before this file was written: they test the
adapter, not the design, and keeping them would have put rate-limit artefacts into
a registered cohort. The adapter gained the pacer as a result.

## Amendment A1 — token floor 4200 → 8192 (before any analysed session)

Written after two pilot sessions under the frozen 4200 floor, before this
namespace was cleared and restarted. `free/gpt-6-luna` returned
`finish_reason=length` at 4200 on the harder cells, which is exactly the
cell-correlated truncation the floor exists to prevent. The new floor is 8192,
applied uniformly to every cell. Both pilot rows were deleted rather than mixed
into a cohort with a different floor: a cohort cannot carry two floors across its
cells, and a truncated session is a transport artefact, not an observation.

Disclosure unchanged: this run is a cross-model replication of P021's design on
APINEX (`free/gpt-6-luna`), paced at 12 requests/minute for the account's
15/min free-plan ceiling.

## Amendment A2 — framing: structural replication, not rate replication

A label probe (three registered C1 seeds) returned 0/3 for `free/qwen-3.8-max`,
`free/deepseek-v4.1-flash` and `free/glm-5.3`, and the `free/gpt-6-luna` pilot
accepted 2/8 in C1 (25%) against P021's 55%. The re-run therefore does **not**
replicate P021's acceptance rate and must not be quoted as one. It tests the
design's structural claim only: bearing cells accept, withheld cells do not.

Consequence for the falsifiers above: the useful failure condition is C1/C3
acceptance near zero, not acceptance near 55%. A rate materially below P021's is
expected and is a label property, reported as such.

Scheduling is 6 workers under the 12 req/min pacer. Sessions that ended in a
terminal transport failure during the pilot were removed from `results.jsonl`
before this restart so the driver re-attempts those (seed, cell) pairs; no
successful session was removed.
