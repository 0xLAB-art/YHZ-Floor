# PREREGISTRATION — Amendment 2 to the external admission portability design

**Namespace:** `sp2027/research_execution/external_admission_amend2_20261025/`
**Authorizes:** the replanning requirement named in the amendment-1 outcome record
(`external_admission_amend1_20261024/REPORT.md` §4) and in the paper's external
boundary section: *"a read rule matching the working-directory contract, or
prompts that state `argv[1]`."*
**Date:** 2026-10-25 · **Zero provider calls, zero new sessions.**

## 1. What changed and why (exactly one thing)

Amendment 1 executed its registered 4-task grid to 32/32 terminal sessions and
retained 37 programs, but the offline triple regrade was **degenerate**: the
frozen admission rules' read-boundary clause (`open:not-readonly-argv1`) rejects
any `open()` that is not a read-only open of `sys.argv[1]`, while the frozen
prompts direct programs to read artifacts by fixed name from the working
directory ("The provided artifact files are also present, under the same names,
in your program's working directory"). Every retained program reads
`open('output.txt', 'r')` — a constant working-directory path — so the boundary
clause fired 37/37 and the import axis (the mechanism under test) never bound.

Amendment 2 revises **only the read-boundary clause** of the three regrade
policies to match the frozen prompt contract: a read-only `open()` of a
constant string path (or the legacy `sys.argv[1]` form) is permitted; all other
open() forms (write/append modes, dynamic paths, keyword arguments) remain
`disallowed-boundary` violations. **The import axes are untouched byte-for-byte
in semantics:** rule (a2) keeps the declared inert-stdlib v3 set, rule (b2)
keeps OUR counterfactual stress rule {json, sys, base64}, rule (c2) keeps the
frozen cleanup `transform()` unchanged. No prompt, fixture, program, session
record, or oracle outcome is modified; the 37 programs are referenced by their
retained SHA-256 values.

This is a design-compatibility repair of our evaluator stack (the mismatch was
ours, not a benchmark property), registered before any regrade computation.

## 2. Frozen objects

- New policy snapshots (`policies_amend2/`): `rule_a2_permissive_v3_wdreads.py`,
  `rule_b2_stress_legacy_wdreads.py`, `rule_c2_cleanup_wdreads.py` — each
  derived from its amendment-1 frozen source by replacing only the read clause
  (SHA-256 of each is in `FREEZE.json`; the derivation script asserted the
  frozen basis hashes 372bab44…, 257b7805…, 7419e861… before deriving).
- Programs: the 37 retained programs of
  `external_admission_amend1_20261024/sessions/programs/` (hash-asserted at
  regrade time against `results.jsonl` program_sha256 values).
- Analysis script: `regrade_amend2.py` (also hashed in FREEZE.json).

## 3. Procedure (offline; deterministic)

`regrade_amend2.py` re-qualifies all 37 retained programs under BOTH rule
generations on the same sources: (a/b/c) the frozen amendment-1 policies
(hash-asserted) — reproducing the recorded degenerate baseline as an internal
control — and (a2/b2/c2) the amendment-2 policies. Session-level acceptance per
rule = any submitted program that both qualifies under the rule and matches the
oracle. Per-task acceptance rates, representation contrasts (RT−R0, pp),
movement = contrast(b2) − contrast(a2), and the cleanup arm (c2) exactly as in
amendment 1. Cleaned sources run through the same sandbox code path with the
task artifacts present, byte-identical stdout required.

## 4. Prespecified falsifiers (unchanged from amendment 1, 4-task thresholds)

- **F1 (mechanism ports):** regrade (b2) moves the per-task representation
  contrast outside ±10 pp on ≥ 2 of the 4 tasks.
- **F2 (honest null):** movement within the margin on ≥ 3 of 4 tasks.
- **F3 (analysis defect):** cleanup fails byte-identical output preservation on
  any program → investigate; do not publish the contrast.
- **Degeneracy guard (new, explicit):** if any retained program is rejected
  under (a2) solely by the read-boundary clause, the amendment FAILED to match
  the prompt contract — report and stop.

## 5. Labeling (unchanged)

Every conclusion is *portability + evaluator sensitivity under OUR stress
rule*; nothing is a claim about Cybench; the census describes the pinned
2026-10-05 snapshot; no pooling with any other cohort; per-task n=4 detects
only large effects; all statistics descriptive.
