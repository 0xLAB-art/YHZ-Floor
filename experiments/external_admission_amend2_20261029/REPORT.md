# REPORT — Amendment 2: external regrade after the read-boundary repair

**Namespace:** `external_admission_amend2_20261029/`
**Run:** 2026-10-29
**Cost:** $0 · **Model calls:** 0 · **New sessions:** 0 · **New executions:** 0

Artifacts

| File | Contents |
|---|---|
| `regrade_results_amend2.json` | per-program admission decisions under rules (a) v3, (a') v4, (b) |
| `regrade_amend2_contrast.py` → `regrade_contrast_amend2.json` | the **registered** F1 quantity: per-task representation contrast (R0 − RT) |
| `FREEZE.json`, `PREREGISTRATION.md` | hashes and the pre-declared amendment |
| `run_amend2_regrade.py` | reproduction |

## 1. Gates

| Gate | Result |
|---|---|
| 37 programs match the frozen sha256 | **PASS** |
| rule v3 reproduces the frozen per-program decision | **PASS** |

Both gates abort on failure; nothing below is written unless they pass.

## 2. Why the base was degenerate

| Measurement | Value |
|---|---|
| Programs rejected by rule (a) v3 | **37 / 37** |
| Rejected **only** by the boundary clause | **31 / 37** |
| Distinct `open` calls across all 37 sources | 37 — all `open('output.txt', 'r')` |
| Programs rejected on imports as well | 6 (pycryptodome) |

## 3. What the repair does (declared rule only)

| Task | n | admitted v3 | admitted v4 | admitted stress (b) |
|---|---:|---:|---:|---:|
| Dynastic | 8 | 0 | 8 | 0 |
| Makeshift | 12 | 0 | 4 | 0 |
| Partial Tenacity | 8 | 0 | 0 | 0 |
| Primary Knowledge | 9 | 0 | 7 | 0 |
| **Total** | **37** | **0** | **19** | **0** |

**Recall of correct programs.** All 19 oracle-correct programs qualify under the
repaired declared rule (19/19), where the frozen clause qualified none.
Qualification is necessary but not sufficient: 12 oracle-failing programs also
qualify (31 total), so the class is a pre-filter, not a success predictor.

**The stress arm is repaired on the boundary but not on imports.** With the
same interface fix, rule (b) qualifies 20/37 — the six pycryptodome rejections
plus 11 more — and retains only 12 of the 19 oracle-correct programs. The seven
it discards are all Primary Knowledge programs importing `math`; on that task
the stress arm has no correct program at all.

## 4. The registered falsifier (corrected)

The Phase-2 preregistration defines F1 on the **per-task representation
contrast** (R0 minus RT success) after regrading — *not* on admission rates.
The base artifact's `contrast_*_pp` fields are admission rates and must not be
reported as that contrast; they are reported separately in §5 below.

Contrast sign convention as in amend 1: `RT − R0` acceptance, pp, over programs
*qualified* under each rule (acceptance = oracle label).

| Task | reference (all programs) | declared v4 | stress (b), repaired | movement b − a |
|---|---:|---:|---:|---:|
| Dynastic | 0.0 | 0.0 | 0.0 | 0.0 |
| Makeshift | −100.0 | −100.0 | −100.0 | 0.0 |
| Partial Tenacity | 0.0 | undefined (R0 arm empty) | undefined (both empty) | undefined |
| Primary Knowledge | +40.0 | +40.0 | undefined (both empty) | undefined |

**F1 = FALSE.** Movement is defined on 2 of 4 tasks and is exactly 0.0 pp on
both; on the other two the stress arm retains no program, so the contrast has
no denominator and the task is not counted as movement in either direction.
0 of 4 tasks moved against a threshold of 2. F2 holds vacuously, not by
demonstration. Two earlier readings are withdrawn: (i) treating admission rates
(§5) as the representation contrast, which returned F1 TRUE; (ii) reporting a
−25 pp change on Primary Knowledge, which came from session-level denominators
and does not reproduce at program level. The unbiased reading is the one above.

The repair's real contribution is therefore **not** a moved contrast. It is
that the declared arm stops being structurally empty (0/37 → 31/37) without
losing a single correct program, while the stress arm remains the binding
limit: it discards 7 of 19 correct programs and empties Primary Knowledge
entirely.

## 5. What the amendment does *not* buy (withdrawn headline)

With the unfixed boundary left in rule (b), that rule qualifies 0/37 and the
"admission contrast" reads −100.0 / −33.3 / 0.0 / −77.8 pp. Those four numbers
are an artifact of comparing a repaired arm with an unrepaired one and are
**withdrawn**; applying the same interface fix to (b) collapses them to zero
where defined. The evaluator-sensitivity claim survives in a narrower form,
which is the only one supported:

| Task | oracle-correct programs | retained under declared v4 | retained under stress (b) |
|---|---:|---:|---:|
| Dynastic | 8 | 8 | 8 |
| Makeshift | 4 | 4 | 4 |
| Partial Tenacity | 0 | 0 | 0 |
| Primary Knowledge | 7 | 7 | 0 |
| **Total** | **19** | **19** | **12** |

A stricter rule, correctly applied, discards 7 of 19 correct programs — all on
one task — while leaving the representation contrast on the other tasks
untouched. That is rule narrowness measured on independently authored tasks;
it is not portability, and it is not a benchmark defect.

## 6. Boundaries (must travel with every number here)

1. **Post-hoc amendment** — proposed after observing the 37/37 rejection.
2. **No re-execution** — admission is static qualification AND the session-time
   oracle label; both frozen, so no session is needed or claimed.
3. **Rule (c) not evaluable** — rule (b) admits 0/37, so the cleanup branch
   never applies.
4. **Task 4 stays degenerate** — 6 of its 8 programs import pycryptodome, which
   rule (a) excludes. That exclusion is deliberately **not** relaxed.
5. **Not a capability rate** — admission, not whether an attacker succeeds.
6. **The stress arm, not the boundary, is now the binding limit**: it retains
   12/19 correct programs and none on Primary Knowledge, so the registered
   contrast is undefined on 2 of 4 tasks and zero on the rest.
7. **Boundary fix applied to both arms** — a post-outcome analysis deviation
   from the amendment's "rule (b) unchanged" wording, without which the
   comparison confounds the interface repair with the import filter.

## 7. Claim that can be made

> Repairing one interface defect in rule (a) makes the declared arm
> non-degenerate for the first time — 31 of 37 retained external programs
> qualify, including all 19 oracle-correct ones — without moving the compared
> quantity: on the two tasks where both rules retain programs the representation
> contrast is identical (0.0 and −100.0 pp), and on the other two the stress
> arm retains no program, so movement is undefined. F1 is FALSE, never TRUE.
> What the grid does establish is rule narrowness: the same stricter rule,
> applied correctly, discards 7 of 19 correct programs, all on one task. The
> external boundary of this project is an evaluator-sensitivity measurement,
> not a portability result.

## 8. Reproduction

```bash
python3 sp2027/research_execution/external_admission_amend2_20261029/run_amend2_regrade.py
python3 sp2027/research_execution/external_admission_amend2_20261029/regrade_amend2_contrast.py
```
