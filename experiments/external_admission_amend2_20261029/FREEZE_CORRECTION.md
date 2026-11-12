# Correction to `FREEZE.json` (2026-10-29, post-outcome)

`FREEZE.json` is left byte-unchanged. Its `claim` field was written at freeze
time, before the regrade ran, and reads:

> ... movement vs rule (b) is −100.0 / −33.3 / 0.0 / −77.8 pp on the four
> tasks; F1 TRUE, F2 FALSE.

Two parts of that sentence are superseded by the outcome, and neither is
withdrawn silently:

1. **The −100.0 / −33.3 / 0.0 / −77.8 pp figures** compare a repaired declared
   arm against an *unrepaired* stress arm. With the same interface repair
   applied to rule (b) — which is required, because the read boundary is an
   interface defect and not a policy axis — they collapse to 0.0 pp wherever
   both arms retain programs.
2. **F1 TRUE** does not survive the registered definition. The parent protocol
   defines F1 on the per-task *representation contrast*. That contrast moves
   on 0 of 4 tasks and is undefined on 2 of 4, so F1 is FALSE.

Authoritative records after the run:

- `regrade_amend2_contrast.py` → `regrade_contrast_amend2.json` (registered
  quantity, F1 FALSE, 12/19 correct programs retained under the stress rule);
- `REPORT.md` §4–§7 (withdrawn readings, boundaries, the supported claim);
- `PREREGISTRATION.md` §7 (post-outcome addendum).

What survives from the freeze-time claim: 31/37 programs qualify under the
repaired declared rule, all 19 oracle-correct programs are retained, and rule
(b) is the binding limit.
