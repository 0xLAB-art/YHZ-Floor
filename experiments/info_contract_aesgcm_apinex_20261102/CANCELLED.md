# P015 — CANCELLED (no funded second provider route)

**Date:** 2026-11-02 · **Sessions run: 0.** This is a cancelled cohort, not a
null result. Nothing here may be counted as evidence about the information
contract.

## Why

P015 was registered to test transfer of the premise effect to a *different
provider family*. AMENDMENT_01 fixed the replacement procedure before any
replacement call: probe the remaining routes, register the first two distinct
families that return text, and if fewer than two answer, report the transfer
test as single-label; if none answer, cancel the cohort.

Measured route status, all beds recorded in `research_execution/`:

| route | inventory | completion attempt | verdict |
|---|---|---|---|
| APINEX | 44 ids via `GET /v1/models` | **402** on `claude-opus-5.5` and `gemini-3.1-pro` (0.4 s / 0.6 s) | key valid, **unfunded** |
| APMix | `/models` 404; ids exist but are tier-gated | `gpt-6-astra` **403** "needs the Max plan"; `gemini-3.1-pro` **403** "needs the Pro plan"; sweep of 15 ids: 10 × 403 (8 Starter, 3 Pro), 5 × 404 | key valid, **entitled to nothing** |
| OpenRouter | 20 ids, **all** nested like `anthropic/openai/gpt-6.1-terra` | **401** "Missing Authentication header" on all three configured keys, with `Authorization` set and with `Authorization` only | **catalog unusable, auth rejected** |
| AgentRouter | 3 ids | **200**, used by P014 | **only working route** |

Files: `labels_probe_20261102.json`, `route_probe_20261102.json`,
`route_probe2_20261102.json`, `apmix_entitlement_20261102.json`,
`info_contract_aesgcm_apinex_20261102/smoke/labels_smoke_20261102.json`.

No funded second provider exists in this project right now. The cross-provider
transfer question therefore stays **open**, and the paper must keep saying so;
it may cite this cancellation as evidence that the question was attempted
rather than assumed.

## What this does not license

It does not license reporting "transfer failed" — no transfer test was run. It
does not license pooling the three AgentRouter labels as if they were three
providers: they share a route, a key and an adapter, and P016 is scoped and
reported as a **within-route** replication for exactly that reason.
