# P014 instrument-risk memo — cell-correlated provider dropout in the withheld arms

**Date:** 2026-11-02 · Written mid-cohort (22/64 slots). Records a **measurement
of the instrument**, not a result of the experiment.

## Observation

Terminal provider-failure rows are not spread evenly across cells:

| cell | arm | terminal drops (of 6 seeds seen) |
|---|---|---|
| C1 | A+ B+ | 0 |
| C3 | A− B+ | 0 |
| C2 | A− B− | 5 |
| C4 | A+ B− | 1 |

Every drop is `EMPTY_RESPONSE`. Turn placement, from `events.jsonl`:

| seed | cell | turn of failure | stored response for that turn |
|---|---|---|---|
| 401 | C2 | 2 | turn 1 stored (text 506 chars, `end_turn`, 2726 output tokens) |
| 404 | C2 | 2 | turn 1 stored (text 576 chars, `end_turn`, 2546 output tokens) |
| 405 | C2 | 2 | turn 1 stored (text 617 chars, `end_turn`, 2666 output tokens) |
| 403 | C2 | 1 | none stored |
| 406 | C2 | 1 | none stored |
| 402 | C4 | 1 | none stored |

## What the stored bodies show

Successful and failing sessions are distinguishable on **output tokens**, not on
`stop_reason`: withheld-arm responses that did complete burned 2546–2726 output
tokens to emit 506–617 characters of text, against 512–1150 tokens for the
stated-arm responses. The token floor (2800, disclosed in the adapter) is
therefore close to binding on the reasoning-heavy arms, and the failing calls are
exactly the ones spending that budget.

For the three turn-2 and three turn-1 failures with **no stored body**, the
cause is not determinable from the evidence held here: the adapter raises
`EMPTY_RESPONSE` before the runner persists anything, so an empty-but-200
provider payload and an empty-content completion are indistinguishable in this
record.

## Why this matters for the final read

1. **The dropout is cell-correlated** — it lands on the two cells where the
   premise is withheld. A reader must not read "C2 produced no accepted
   submission" as behaviour when part of C2 produced no *response at all*.
2. **The evaluable denominator is the honest one.** `analyze_p014.py` already
   reports accepted/evaluable per cell and counts drops separately, so the
   registered premise marginal is computed over evaluable pairs only. With C2
   dropping at this rate, that marginal's denominator will be materially smaller
   than 32.
3. **The paired primary test is protected** by requiring an evaluable C1 *and*
   C4 verdict per seed, so dropout can only shrink the pair count, never flip a
   pair — but the pair count will be reported, not assumed to be 16.
4. **Reasoning budget is an instrument variable, not a treatment.** The 2800
   floor was set before the cohort on measured pre-freeze latency; this cohort
   suggests it is near-binding for withheld arms. Any future arm-comparable
   cohort should set the floor from the **maximum** observed completion, or
   record per-call `stop_reason` on failures too. That is a change of protocol
   number, not a mid-cohort edit.

## What is explicitly not claimed

No claim that the withheld premise *causes* the empties. No claim that these
rows are failures of the model rather than of the transport. No imputation, no
retry, no deletion: the rows stay terminal, as the preregistration requires.

---

## Final counts (cohort complete, added after the run)

The mid-cohort prediction held and worsened:

| cell | arm | terminal drops | evaluable | accepted |
|---|---|---|---|---|
| C1 | A+ B+ | 0 / 16 | 16 | 16 |
| C3 | A− B+ | 0 / 16 | 16 | 16 |
| C2 | A− B− | **14 / 16** | 2 | 0 |
| C4 | A+ B− | **5 / 16** | 11 | 0 |

Attrition contrast, withheld vs stated: 19/32 vs 0/32, Fisher two-sided
**p = 7.97 × 10⁻⁸**. Every failure category recorded is `EMPTY_RESPONSE`; no
HTTP error, timeout or truncation-finish occurred in this cohort.

So the instrument caveat stated mid-cohort became the dominant limitation: the
premise marginal is computable only over **13** withheld sessions that answered,
and the paired test only over **11** pairs. Both are reported, with the dropout
shown beside them — see `REPORT_P014.md` §5.
