# Non-offensive measurement controls — 2026-10-04

These are instrument-development controls, not autonomous-security-agent
experiments, attack success measurements, or human annotation evidence.
They do not replace E2 or make the failed corpus analysis-eligible.

## Completed synthetic provider-failure control

`fault_20261004_01`: 180/180 frozen cases completed. Six response scenarios
× three retry limits × two latency settings × five replicates, shuffled
with seed 20261004. Scenarios: normal response, one-shot 429, one-shot 503,
persistent 429, persistent 503, malformed answer. Per-attempt latency:
0 or 5 ms. Retry limits: 0, 1, 2. Fixed backoff: 2 ms.
All are **simulated in-process**; no real HTTP server, quota, or provider
was exercised. Counts are prescribed by the injection design, not discoveries
about a provider population: 70 SUCCESS, 80 PROVIDER_UNAVAILABLE, 30 ORACLE_FAIL.

One-shot errors recover with retry; persistent errors remain availability
outcomes despite retries; malformed content remains a grading failure.
Unavailable responses are never converted into arithmetic failures.
Median measured request span: 4.7434405 ms; median grading span:
0.0092285 ms. Zero injected latency still has scheduler/Python overhead.
These spans include injected sleeps and are not inference timings.
The 5-ms one-shot-503 median is 5.127668 ms without retry versus
12.338555 ms with one retry and a successful response. This is a bounded
clock/accounting canary, not a result about a real serving stack or the
production agent driver.

Identity checks and separate offline reconstruction pass: scheduled
inventory, unique IDs, task/track/condition identity, frozen-plan digest,
file hashes, injected attempt codes, and independent arithmetic verdicts.
This validates this **benign control namespace**, not a fresh security campaign.

Reconstruct without model/network access:

```bash
python3 sp2027/analysis/replay_benign_controls.py sp2027/analysis/benign_controls/fault_20261004_01
```

## Local-backend launch — incomplete, not performance evidence

`local_20261004_01/PLAN.json` was written before inference: 12 four-integer
addition prompts, no agent/tools, strict integer grading, 40-second timeout,
no retries, temperature 0, seed 20261004, 32 output tokens, 2048 context,
thinking disabled. Loopback Ollama 0.20.5, proxies disabled, catalog rejects
remote/relay models. Local 7.5B Q4_K_M catalog digest:
`37709e679eb9da5d69501b3cd417af714b8a91ceb23b14dce849e4503e5dd225`.
Native execution has no container digest; none is fabricated.
Protocol checked against [official Ollama API documentation](https://docs.ollama.com/api/generate).

Four completed requests timed out. The client was terminated after
observing severe memory pressure; eight scheduled cases have no completed
record and are NOT_RUN_OR_INTERRUPTED, not oracle failures. An in-flight
request may have existed at termination. No model output was obtained;
there is no stable-backend capability/timing estimate. Empty loaded-model
catalog and low available memory suggest a launch problem but do not prove
its cause. User applications and the Ollama service were not terminated.
No credentials were used or raw records edited. `ABORT.json` records
the disposition separately.

Before another launch: sufficient memory or an already installed smaller
local generation model, a new frozen namespace, retained startup failures.
Do not change this failed run's timeout or silently exclude it.

## Still missing

Independent human E1 ratings and human weakness/status annotations; clean
security-agent cohort; stable-backend, cross-provider/model/host and temporal
replication; external benchmark remeasurement; third-party reproduction.
External artifact delivery remains deferred. These controls close none of
those gaps. The new results remain supplementary development evidence and
are not added as a headline manuscript claim.
