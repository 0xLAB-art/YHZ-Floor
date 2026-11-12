# AMENDMENT 01 — P015 label list (written before any replacement label's first call)

**Namespace:** `sp2027/research_execution/info_contract_aesgcm_apinex_20261102/`
**Date:** 2026-11-02 · Before any experiment call under this protocol.

## What happened

The APINEX inventory probe returned 44 ids, so `claude-opus-5.5` and
`gemini-3.1-pro` were registered in `PREREGISTRATION.md` §2. The off-fixture
smoke probe (`smoke/labels_smoke_20261102.json`) then returned **HTTP 402** on
both labels:

| label | status | latency |
|---|---|---|
| `claude-opus-5.5` | `HTTP_ERROR` 402 | 0.4 s |
| `gemini-3.1-pro` | `HTTP_ERROR` 402 | 0.6 s |

402 is a funding/quota rejection, not an authentication failure: the key is
accepted and the model ids are served by `GET /v1/models`, but no completion is
authorized. Both labels are therefore **dropped before the first session** —
exactly the drop the preregistration anticipated ("dropped and disclosed as
dropped, never silently replaced"). Zero sessions were registered against them
and no results file was created.

## Consequence for the design

The APINEX route cannot carry this cohort. Because the cohort's whole purpose is
a cross-**provider** replication, the label list has to come from a route that
actually serves completions. The replacement procedure, fixed here before
looking at any replacement candidate:

1. Probe the remaining configured routes with (a) `GET /models` for the id
   inventory and (b) at most four 16-token off-fixture smoke calls, recorded in
   `research_execution/route_probe_20261102.json`. No fixture, no cell slot.
2. Register the first two **distinct model families** that return non-empty text
   in ≤60 s, in the priority order declared in the probe file: Anthropic-family,
   Gemini-family, then GPT-family, then any other family.
3. If fewer than two families answer, the cohort runs on whatever number
   answered and the paper reports the transfer test as **single-label**, with
   the unfunded routes disclosed as a limitation. A zero-label outcome cancels
   P015 and is reported as a cancelled cohort, not as a null result.
4. No label from the dropped APINEX pair may be re-tried inside P015; a later
   funded retry would be a new protocol number.

Everything else in `PREREGISTRATION.md` — fixture, cells, seeds 501–516, Latin
squares, per-label isolation, terminal provider failures, analysis plan,
falsifiers F1–F4 — stands unchanged. Seeds stay 501–516 because no session was
ever run under the dropped labels.
