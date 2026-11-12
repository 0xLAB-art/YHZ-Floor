# INSTRUMENT NOTE — P016 withheld arms returned no text on `gpt-5.6-sol`

**Namespace:** `info_contract_aesgcm_labels_20261102/`
**Written:** 2026-11-02, after the cohort closed at 128/128 slots, before the result is quoted anywhere.
**Status:** disclosure only. Estimator, runner, adapter, `_REGISTRATION.json`, prompts and data are unchanged.

## What was observed

For `gpt-5.6-sol`, all 32 withheld-premise slots ended terminal:

| cell | premise | sessions | status | evaluable |
|---|---|---|---|---|
| C1 | stated | 16 | 16 SUCCESS | 16 |
| C2 | withheld | 16 | 16 EMPTY_RESPONSE | 0 |
| C3 | stated | 16 | 16 SUCCESS | 16 |
| C4 | withheld | 16 | 16 EMPTY_RESPONSE | 0 |

`EMPTY_RESPONSE` in `provider_adapter_agentrouter.py:134` means **HTTP 200 with no text in the
response body** — not `HTTP_ERROR`, not `TIMEOUT`, not a 429. The pattern is perfectly separated by
cell: 32/32 stated-arm calls returned text (32/32 accepted), 32/32 withheld-arm calls returned none.
This is a behavioural separation, not random provider flakiness.

## Why it matters for the printed classification

PREREGISTRATION §4 classifies a label as *direction replicated* when **C1 ≥ 12/16 and C2 ≤ 4/16**,
by acceptance count against the registered 16-seed denominator. `gpt-5.6-sol` satisfies that
literally (C1 = 16, C2 = 0), and the frozen estimator prints `direction replicated`.

But C2's acceptance is **0 accepted out of 0 evaluable**, so the withheld side of that label
contributes **no scored attempt**. The defensible statement for this label is:

> every stated-premise session was accepted, and every withheld-premise session returned no text.

It is **not** evidence that the model attempted the withheld variant and failed it. No withheld-arm
defect rate, no failure rate and no per-seed pairing exist for this label.

The estimator's own guard covers only short cohorts (`< 16` seeds); it has no guard for
zero-evaluable cells. That guard was not added after the fact, because the estimator was frozen
before either label completed and the preregistered thresholds are what they are. The limitation is
recorded here instead of being repaired in the analysis.

## Contrast with the other label

`gpt-6.1-sol` kept the withheld side observable in one cell: C4 had 10 evaluable attempts (all
rejected) and 8 evaluable C1/C4 pairs, giving 8/0 discordant, exact binomial two-sided
p = 0.0078125; C2 was 0/0 there as well (16 `EMPTY_RESPONSE`). So the paired test is meaningful for
`gpt-6.1-sol` and undefined for `gpt-5.6-sol`.

## Denominator warning for the P014 comparison row

The P014 column in `analysis_p016.txt` is **accepted/registered** (C2 0/16, C4 0/16) and discloses
its own dropout in `REPORT_P014.md`. The P016 label columns are **accepted/evaluable** (C2 0/0,
C4 0/0 or 0/10). These are different denominators; the columns must be read as direction and
magnitude, never subtracted, and never pooled.

## What is still claimed

On the frozen AES-GCM fixture, holding transport, key and adapter fixed, the stated-vs-withheld
separation reproduces on two labels other than P014's: `gpt-6.1-sol` with a scored paired test, and
`gpt-5.6-sol` at the level of "no text at all on the withheld side". Still a within-route,
cross-label result — not provider generalization.
