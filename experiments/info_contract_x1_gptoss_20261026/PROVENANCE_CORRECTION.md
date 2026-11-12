# PROVENANCE CORRECTION — P010X1 delivered the primary label, not gpt-oss:120b-cloud

**Date:** 2026-10-30 (found during the elite build's referee-response pass)
**Found by:** fingerprint audit of every raw provider response, triggered while
preparing the fourth-label cohort (the AgentRouter label-selection probe).

## The defect

The P010X1 cohort (`info_contract_x1_gptoss_20261026/`) is registered and
published as the cross-vendor replication: "gpt-oss:120b-cloud served through
the local Ollama gateway's cloud route". The runtime record proves the cohort
actually ran on **`claude-sonnet-4-6-free` via `https://api.apmix.ai/v1/messages`**
-- the same primary label and route as every same-label cohort.

## Evidence (runtime artifacts, written at execution time)

1. **Raw provider responses (97/97):** every file in `raw_provider_responses/`
   is an Anthropic-style message with `"model": "claude-sonnet-4-6-free"` and
   `msg_…` identifiers. Zero Ollama-fingerprinted objects (`chat.completion`,
   `fp_ollama`, `gpt-oss`) exist anywhere in the namespace.
2. **`run_info.json`** (written by the frozen runner at launch): `"endpoint":
   "https://api.apmix.ai"`, `"model": "claude-sonnet-4-6-free"`.
3. **`events.jsonl`** per-turn `provider_metadata`: endpoint
   `https://api.apmix.ai/v1/messages`, `model_requested: claude-sonnet-4-6-free`
   on every turn.

## Root cause

The wrapper (`run_p010x1_gptoss.py`) performs a "configuration-only provider
redirect": it sets `ACTS_PROVIDER_ENDPOINT=http://127.0.0.1:11434/v1` and
`ACTS_PROVIDER_MODEL=gpt-oss:120b-cloud` before importing the frozen runner,
stating these are "variables the frozen module's own
provider_adapter.ClaudeProvider already reads". That statement is false of the
shipped code: neither the frozen runner (`run_info_contract_2x2_chacha20.py`,
SHA `a08eab6f…`) nor the frozen adapter
(`analysis/checkpoint007_active_experiments/runs_009/provider_adapter.py`)
reads either variable; the adapter takes endpoint/model as constructor
arguments with apmix/sonnet defaults, and the frozen runner instantiates it
with `ClaudeProvider()` -- no arguments. The redirect was inert; the smoke
probe (`smoke_x1.py`) used the same inert path, so its "OK" validated the
apmix route, not the Ollama route.

The pre-freeze steps that WOULD have caught this (a route-level identity probe
comparing responses across routes) were not part of the X1 preflight; the
freeze recorded intent, and intent was never bound to transport.

## What survives

- The 97 sessions ran to completion and their **numbers are real measurements
  of the primary label on fresh seeds 161--176**: C1 16/16, C2 6/16, C3 16/16,
  C4 6/16; paired C1-vs-C4 10/0, p = 0.001953; premise marginal 32/32 vs 12/32.
  P010X1 is therefore a **same-label n=16 replication on fresh seeds** whose
  primary statistic exactly reproduces P010N16's 10/0 -- it retains evidential
  value, just not vendor value.
- The cross-LABEL replications are unaffected: fingerprint audit shows L2's 44
  raw responses all echo `gpt-6.1-sol` and L3's 48 all echo `gpt-6-astra`
  (the AgentRouter adapter was explicitly injected in those cohorts and its
  route binds the label).

## What is withdrawn

Every second-vendor claim derived from P010X1: "different vendor", "unrelated
route", "no shared weights, serving stack, or vendor", "two vendors", and the
Figure-4 legend/category "second vendor". The cross-vendor question returns to
OPEN, with this cohort recorded as attempted-and-withdrawn.

## Disposition

All paper surfaces carrying the second-vendor claim are corrected in the same
commit series as this file, with the correction itself disclosed in the
manuscript (Section 5, information-contract section; Section 11 limits). The
verify script's echo needles are realigned to the corrected sentences, per the
established needle-realignment discipline.
