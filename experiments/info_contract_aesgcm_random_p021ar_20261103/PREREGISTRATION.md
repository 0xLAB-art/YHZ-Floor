# P021/AR — re-run of P021 on AgentRouter, original label (registered 2026-11-03)

## Why here

P021 was run on `gpt-6-astra` and lost **189 of 384 sessions** to transport
failures (census, 2026-11-03: every lost session carries a provider event on the
same seed and cell). Two re-run routes were considered and one was abandoned:

- **APINEX** was tried first because it is the standing route. It does not serve
  `gpt-6-astra` on this account (`HTTP 402`), and its free labels solve the
  bearing cell at 0–25% against P021's 55%. An APINEX re-run would therefore
  measure a substitute model. That pilot is preserved as a label probe and is not
  used as a cohort.
- **AgentRouter** still serves the original label. A six-call probe returned 6/6
  with ~3.6 s latency, and P024A — which used the same retry adapter — finished
  96/96 sessions with zero provider failures.

## What is identical to P021

| Element | Value |
|---|---|
| Frozen runner | `run_info_contract_2x2_aesgcm.py`, sha256 `cf0a806a…4afb9`, asserted against both registrations |
| Seeds | the 96 registered CSPRNG instances, sha256 `07a9e442…f867` |
| Cells, rotation, prompts, feedback, policy, oracle | untouched |
| Label | `gpt-6-astra` — unchanged |
| Token floor | 4200 — unchanged |
| Session status vocabulary | unchanged |

## What differs, disclosed

1. **Adapter.** `provider_adapter_agentrouter_p023.py` instead of the P017 adapter.
   It never sends `stream` or `stream_options` (the P017 adapter's 400 defect),
   and it retries the registered transient classes — 408/409/425/429/5xx plus a
   `400` whose body carries a `stream_options` marker — up to 4 attempts with
   backoff `(2, 5, 12)` s. Every retried attempt is written to `failure_log.jsonl`.
2. **Scheduling.** 8-worker thread pool (`parallelize_cohort.py`); rows carry
   `execution_concurrency` and `execution_phase`.

## Predictions

- Provider failures should stay at or near P024A's zero, not P021's 59%.
- Bearing cells (C1, C3) accept at approximately P021's rate (~55%).
- Withheld cells (C2, C4) accept at zero.

## Falsifiers

- provider failure rate above 5% of sessions → transport still unfit; stop and
  report rather than analyse a third damaged cohort;
- C1/C3 acceptance far below ~40% → the retry adapter changed the sampling
  regime or the label drifted; report as non-comparable;
- any acceptance in C2/C4 → the withheld cells leak; contradicts both P021 and
  the whole information-contract reading and must be reported as a contradiction.

## Relation to the abandoned APINEX pilot

`info_contract_aesgcm_random_p021r_20261103/` holds 61 sessions from
`free/gpt-6-luna` on APINEX plus its probe record. It is kept as evidence about
APINEX's free-tier labels and is **not** pooled with this cohort: different label,
different transport, weaker capability regime.
