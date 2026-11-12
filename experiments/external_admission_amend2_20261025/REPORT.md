# REPORT — Amendment 2: read-boundary repair and the non-degenerate external regrade

**Namespace:** `sp2027/research_execution/external_admission_amend2_20261025/`
**Protocol:** PHASE2-EXTERNAL-ADMISSION-AMEND2-v1 · 2026-10-25
**Status: COMPLETED (offline; 37/37 retained programs regraded; zero provider calls, zero new sessions)**

## 1. Headline

The registered read-boundary repair (Amendment 2) fully resolved the structural
degeneracy of the amendment-1 regrade: all 37 retained programs now pass the
read clause (their sole artifact access is `open('output.txt', 'r')` — a
read-only constant working-directory path, matching the frozen prompts'
contract), and the import axis became binding for the first time (17/37
programs rejected under the stress rule on imports alone). The regrade triple
is therefore **non-degenerate**, and its verdict is an honest, now-substantive
null: **F1 FALSE (movement outside ±10 pp on 1 of 4 tasks, threshold ≥2);
F2 TRUE (movement within margin on 3 of 4); F3 PASSED_preservation (17/17
byte-identical outputs on edited programs).**

## 2. Baseline reproduction (internal control)

Under the frozen amendment-1 policies, re-run on the same hash-asserted
programs: **0/37 qualified** under both rule (a) and rule (b) — reproducing the
recorded degenerate baseline exactly. The repair is therefore isolated to the
read clause, as registered.

## 3. Results under the amendment-2 rules

Qualified counts: (a2) declared v3 rule — 31/37; (b2) OUR stress rule
{json, sys, base64} — 20/37. Per-task acceptance (oracle ∧ qualified), R0/RT:

| Task | a2 R0 | a2 RT | b2 R0 | b2 RT | contrast a2 | contrast b2 | movement |
|---|---|---|---|---|---|---|---|
| Dynastic | 100 | 100 | 100 | 100 | 0 | 0 | 0 |
| Makeshift | 100 | 0 | 100 | 0 | −100 | −100 | 0 |
| Partial Tenacity | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Primary Knowledge | 75 | 100 | 0 | 0 | +25 | 0 | **−25** |

Sign test across tasks (zeros excluded): 0 positive / 1 negative / 3 ties,
two-sided p = 1.0 (descriptive).

## 4. Interpretation (bounded)

- **The import axis binds and is representation- and task-structured.** The 17
  stress-rule rejections fall entirely on Partial Tenacity (8: programs
  importing non-legacy modules — all oracle-failures regardless) and Primary
  Knowledge (9: all 7 oracle-passing PK programs import non-legacy modules,
  e.g. `math`, which the declared rule permits and the stress rule forbids).
- **Primary Knowledge is the one directional instantiation**: under the stress
  rule, every oracle-correct PK program is admission-rejected, collapsing a
  +25 pp oracle-level representation contrast to 0 (movement −25 pp, outside
  the margin). This is the paper's admission-artifact phenomenon occurring on
  an external task set — correct programs, rejected by rule narrowness — but
  on one task only, below the preregistered ≥2 threshold. Descriptive; per-task
  n = 4.
- **Dynastic and Makeshift are rule-invariant**: Dynastic programs need only
  legacy modules (contrast 0 under both); Makeshift's −100 pp contrast is a
  transport-encoding artifact at oracle level (RT conflation), identical under
  both rules.
- **F1 FALSE** therefore means: the admission mechanism did **not** port at the
  preregistered strength — one directional task, not two. The portability
  question remains unanswered at the registered bar, but it is now unanswered
  for a substantive reason (the external tasks' oracle-passing programs mostly
  do not import outside the legacy set — 3 of 4 tasks' passing programs are
  rule-invariant) rather than a structural one (nothing was admissible).
- **F3**: the cleanup transform edited 17 programs and preserved byte-identical
  stdout on 17/17 (the two PT 30-second-timeout pairs produced identical empty
  outputs, as in amendment 1).

## 5. What this changes (bounded)

- The paper's external record upgrades from *"0/37 admissible under any rule
  (degenerate)"* to *"37/37 admissible at the read boundary after a registered
  evaluator repair; the stress rule then rejects 17/37 on imports; movement
  outside margin on 1 of 4 tasks (F1 FALSE, F2 TRUE, F3 PASSED)"* — a
  design-compatibility repair of OUR stack, never a benchmark-defect claim.
- The −32.8 pp headline remains a within-harness counterfactual; this regrade
  does not instantiate it externally at the preregistered strength. It does
  provide the first non-degenerate external regrade and one directional
  (sub-threshold) instance of admission rejection of oracle-correct programs.
- Labeling unchanged: portability + evaluator sensitivity under OUR stress
  rule; the census describes the pinned 2026-10-05 snapshot; no pooling;
  descriptive statistics only; per-task n = 4.

## 6. Integrity

- Freeze commit `500fe600` (policies + preregistration + script) BEFORE any
  regrade computation; two hash-refresh commits (`39b0fe20`, `5bab23db`) cover
  pre-computation crash fixes (function name; phase_meta row filter) — no
  regrade computation completed before the final freeze state; policies and
  preregistration unchanged throughout.
- Program hashes asserted at runtime against `results.jsonl` program_sha256;
  basis policy hashes asserted against the frozen amendment-1 values.
- Provider calls: 0. Budget ledger: no new lines (offline phase).
- Artifacts: `regrade/regrade_results_amend2.json` (full per-program records),
  `FREEZE.json`, `PREREGISTRATION_AMENDMENT2.md`, `policies_amend2/`,
  `regrade_amend2.py`, this report.
