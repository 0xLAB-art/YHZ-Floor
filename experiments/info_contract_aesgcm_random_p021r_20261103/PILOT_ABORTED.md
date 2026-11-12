# P021/R — pilot aborted: no free APINEX label reproduces the C1 rate

**Status:** aborted after a label probe, before the cohort could be analysed.
The namespace holds 23 pilot sessions from `free/gpt-6-luna` and no summary.

## What happened

`gpt-6-astra` is not usable on this account: it is listed, but every call returns
`HTTP 402 Insufficient balance`, and the free tier is `HTTP 402 / subscription
required`. The only callable labels are the 21 `free/*` models, behind a
**15 requests/minute** account ceiling (handled by the adapter's pacer).

P021's bearing cells accepted at 106/192 ≈ 55% under `gpt-6-astra`. I probed
three free labels on three registered C1 seeds — the cell where the original run
succeeded most:

| Label | C1 successes | Failure modes |
|---|---|---|
| `free/qwen-3.8-max` | 0/3 | ORACLE, PARSE, EXEC |
| `free/deepseek-v4.1-flash` | 0/3 | PARSE, ORACLE, EXEC |
| `free/glm-5.3` | 0/3 | PARSE ×3 |
| `free/gpt-6-luna` (31-session pilot) | 2/8 in C1 (25%), 1/7 in C3 | NO_SUBMISSION, INCOMPLETE_RESPONSE, HTTP_ERROR |

The three-label probe is **0/9** on C1 where the original rate was 55%; under that
rate the probability is ≈0.08%. `free/gpt-6-luna` is the strongest free label at
≈25% in C1 — half the original rate, and still far above zero.

## What this rules out, and what it does not

What it rules out: quoting the re-run as a replication of P021's **rate**. At
≈25% in C1 against 55%, the substitute label is a different difficulty regime;
the number would be a model property reported as a replication.

What it does not rule out: the **structure**. The design's claim is that bearing
cells accept and withheld cells do not. At 25% there is still room for that
contrast to appear, and three of the probe labels cannot even emit parseable
actions — which is itself a capability boundary, not a transport effect.

The pacer and floor work: 8192 tokens eliminated most truncation, and 12 req/min
kept 429s near zero over 23 sessions. The transport is not the blocker.

## What would unblock a real re-run

1. **Balance or a subscription on APINEX** so `gpt-6-astra` can be called. This
   restores the identical label and makes the re-run a true transport swap. It is
   the only option that reproduces P021's estimand.
2. **A different account that serves `gpt-6-astra` or an equivalent.** Same
   requirement, different vendor.
3. **Re-frame as a weak-label structural replication** — report only the
   bearing-versus-withheld contrast, never an acceptance rate, and mark it as
   cross-model. With `free/gpt-6-luna` at ≈25% in C1 this is feasible and is the
   path taken: the cohort restarted under that framing at 6 workers.

Until one of these is chosen, P021's own numbers stay as published and as
disclosed in the manuscript ("lost 226 of its 384 sessions to terminal provider
failures"), and the census stands as the record of the damage.
