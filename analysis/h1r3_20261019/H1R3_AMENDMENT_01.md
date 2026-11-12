# H1-R3 Protocol Amendment 01 — Direction Convention in the Decision Table

**Date:** 2026-10-19
**Timing:** made after the confirmatory campaign started, **before any confirmatory
outcome was read or analysed**. The only analyses executed at this point were on
the exploratory calibration (`runs/calibration`) and sanity (`runs/sanity`) runs.
**Effect on the hypothesis, margin, estimand, or allocation:** none.

## Defect

`§8` of the preregistration defined

$$\tau_A = P(Y^{A}=1) - P(Y^{R0}=1)$$

(positive = treatment arm completes more often), but the decision table in the
same section labelled a lower confidence bound above $+\delta$ as
`MEANINGFULLY_WORSE_THAN_REFERENCE`. With that definition of $\tau$ the direction
was inverted.

## Correction

The implementation (`h1r3_stats.equivalence_assessment`) and the preregistration
table now read:

| Condition | Conclusion |
|---|---|
| CI inside $[-\delta, \delta]$ | `EQUIVALENT_WITHIN_MARGIN` |
| lower bound $> \delta$ | `MEANINGFULLY_BETTER_THAN_REFERENCE` |
| upper bound $< -\delta$ | `MEANINGFULLY_WORSE_THAN_REFERENCE` |
| otherwise | `INCONCLUSIVE` |

The equivalence region and the margin ($\delta = 0.10$) are unchanged.

## Consequence for the freeze record

`H1R3_FREEZE.json` records the pre-amendment hash of `h1r3_stats.py`. That hash is
retained unchanged as the historical value; the amended hash is recorded in
`H1R3_FREEZE_AMENDMENT_01.json` together with this note. No other file changed.

## Why this is not a post-hoc result adjustment

The correction changes only the *label* attached to an interval, not the
interval, the contrast, the margin, the sample, or the decision rule's
mathematical content. It was made before the confirmatory results file existed
in analysed form, and it is disclosed here rather than silently absorbed.
