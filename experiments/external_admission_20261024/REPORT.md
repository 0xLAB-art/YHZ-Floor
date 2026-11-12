# REPORT — Phase 2: External-task admission portability (Cybench crypto subset)

**Namespace:** `sp2027/research_execution/external_admission_20261024`
**Protocol:** PHASE2-EXTERNAL-ADMISSION-v1 · **Date:** 2026-10-24
**Status: NO_GO (honest early stop at task selection — no experiment executed)**

## 1. Headline

The phase could not reach its preregistered 6-task grid. A complete census of
the pinned Cybench archive (`human_audit/source_freeze_20261005/archives/cybench__cybench__ca483c6443f1.tar.gz`,
sha256 `261cc002d315776cf424322a18a645a21b48b418f1425e3b10271e298da0b805`,
re-verified against `sp2027/analysis/external_validation_20261021/SOURCE_PREFLIGHT_V2.json`)
found **14 crypto-category tasks, of which only 4 qualify** under the
preregistered selection rule — below the required quorum of 6. Per the phase
prompt ("If fewer than 6 tasks qualify, stop honestly with status no_go and
document the selection"), the phase stopped before any experiment model call.
Nothing was fabricated, no selection criterion was relaxed, and no session was
run.

## 2. What was executed (and what was not)

Executed:

- Step zero: one 16-token AUTH_SMOKE provider probe, logged **non-evidence** in
  `HEALTH.json`. Two attempts are retained: attempt 1 failed with HTTP 404
  **pre-output** (my client appended `/v1/messages` to a configured base URL
  that already ends in `/v1`; zero model content, zero tokens; the client was
  fixed before any evidence call — the defect and fix are recorded in the
  freeze commit message lineage); attempt 2 succeeded
  (`msg_a185a3eb47b22dec20ce6bf3`, 11 input / 1 output tokens). Both attempts
  have cost lines in `sp2027/research_execution/BUDGET_LEDGER.jsonl`.
- Task census and selection with full exclusion documentation
  (`TASK_SELECTION.md`, `selection/census.json`), made before any outcome
  inspection (no outcomes existed).
- Offline verification of the qualifying set: stdlib-only reference solvers
  (`selection/reference_solvers/`) reproduce all four pinned metadata answers
  exactly (`selection/reference_solve_run.jsonl`). The official Partial Tenacity
  solver (pycryptodome-based) was additionally run and agrees.
- Policy snapshots for the regrade triple, extracted **verbatim by AST slicing**
  from the original sources and functionally smoke-tested:
  - (a) declared permissive rule = v3 inert-stdlib set — `policies/rule_a_permissive_v3.py` (port of `sp2027/analysis/h1r3_20261019/h1r3_contract.py`);
  - (b) OUR counterfactual stress rule = legacy {json, sys, base64} — `policies/rule_b_stress_legacy.py`; rejects, e.g., a `math` import;
  - (c) rule (b) + output-preserving unused-import cleanup with byte-identical stdout check — `policies/rule_c_cleanup.py` (port of the `transform` in `sp2027/analysis/contribution_audit_20261021/policy_mechanism/audit.py`); removes an unused `math` import and preserves output.
- R0/RT representation machinery and the **decode-equality hard gate**
  (`fixtures/rt_transform/`): the gate PASSes for all 4 qualified tasks — every
  base64 RT artifact block decodes byte-identically to its R0 fixture and the
  statement text is identical across representations
  (`fixtures/decode_equality_log.json`). This is a **design-readiness** record:
  no generation ever followed it.
- Preregistration + freeze: `PREREGISTRATION.md`, `FREEZE.json` (SHA-256 of 28
  prompt/fixture/policy/harness files), `PROMPT_HASHES.json` (the 8 instantiated
  prompts the design would have sent), committed **before** any experiment
  model call (freeze commit `08d9fb5`).

Not executed (by design of the early stop): the 24-session grid (6 tasks ×
{R0, RT} × seeds 71, 72), turn-2 feedback, the offline triple regrade on
retained programs, and the portability analysis. `sessions/` and `regrade/`
contain explicit empty-state notes. Zero experiment provider calls were made.

## 3. Why 4 of 14 crypto tasks qualify (selection record)

Full per-task table with reasons in `TASK_SELECTION.md` and machine-readable
form in `selection/census.json`. Summary:

- **9 excluded — external service.** 7 tasks declare a `target_host`
  (ezmaze, failproof, robust-cbc, noisier-crc, noisy-crc, 21-elgamal, Path of
  Survival); 2 more (`diffecient`, `randsubware`) have empty `target_host`
  fields but are network-service challenges by construction (Dockerfile/xinetd;
  official solutions use `pwn.remote`; `diffecient` needs non-stdlib `mmh3`,
  `randsubware` needs `z3`).
- **1 excluded — solver requirements outside the frozen admission set.**
  `[Hard] Permuted`: official `htb/solve.py` requires pycryptodome AES-CBC and
  sympy CRT; under the frozen declared rule an admissible solver would need a
  from-scratch AES implementation the fixed per-session token budget cannot
  plausibly deliver, yielding a structurally degenerate contrast.
- **4 QUALIFY** (each verified offline with a stdlib-only reference solve whose
  output exactly equals the pinned metadata answer): Makeshift, Dynastic,
  Primary Knowledge, Partial Tenacity.

**Quorum robustness:** even admitting Permuted despite its exclusion grounds
gives 5 < 6 — the quorum failure does not hinge on that judgment call.

The plan's phrase "select only `tasks/` crypto entries" maps to the pinned
snapshot's `benchmark/` tree (the archive contains no `tasks/` directory; 43
task entries were enumerated).

## 4. Falsifier verdicts

| Falsifier | Verdict | Basis |
|---|---|---|
| F1 — regrade (b) moves the representation contrast outside ±10 pp on ≥ half the tasks (mechanism ports) | **NOT EVALUABLE** | No sessions, no programs: the grid was never instantiated. |
| F2 — movement within margin on most tasks (honest null, fixture-specific) | **NOT EVALUABLE** | Same. |
| F3 — cleanup fails output preservation on any program (analysis defect) | **NOT EVALUABLE** | No programs to clean. The cleanup transform itself was smoke-tested on synthetic input and preserved output, which is a tool check, not F3 evidence. |

## 5. Budget

Total namespace provider cost: **≈ $0.00005** (one 16-token smoke; the 404
attempt consumed nothing). Phase ceiling $5 — not approached. Two appended
lines in `sp2027/research_execution/BUDGET_LEDGER.jsonl` (one per probe
attempt), each a single JSONL line. Project guardrails ($50/$200) untouched.

## 6. Conclusions and their boundary

- **No portability, mechanism, or evaluator-sensitivity conclusion is produced.**
  Had the design executed, every conclusion would have been labeled
  *portability + evaluator sensitivity under OUR stress rule*; that framing is
  preserved in the frozen preregistration for any future re-plan.
- **No benchmark-quality claim of any kind is made.** In particular, the
  service-bound share of the pinned archive's crypto subset (9/14) is a
  property of that snapshot's task selection; it is not evidence of a Cybench
  defect, and nothing here is described as a native benchmark defect. The
  narrower import filter remains **OUR counterfactual stress rule**
  (provenance: H1-R3 legacy filter), not a Cybench-native rule — consistent
  with the preflight finding that no import gate exists in Cybench's inspected
  entrypoints.
- The census describes the pinned 2026-10-05 snapshot only: no claim about the
  current upstream repository, other archives, or other task categories.
- **What a future re-plan would need:** either a relaxed quorum with a
  preregistered amendment (e.g., 4-task grid with correspondingly adjusted
  falsifier thresholds), or an expanded external task source beyond the pinned
  archive. Both are unregistered design changes and were deliberately NOT made
  here.

## 7. Integrity notes

- Freeze discipline: preregistration, FREEZE.json, TASK_SELECTION.md, policy
  snapshots, fixtures, and gate scripts were committed (`08d9fb5`) before any
  experiment model call (of which there were none); FREEZE.json hashes were
  re-verified after the commit (28/28 match).
- The auth-smoke 404 is retained verbatim in `HEALTH.json` and in the budget
  ledger; it was pre-output infrastructure, not a task failure, and no session
  ever depended on it.
- Selection artifacts that quote answers: `oracle/answers.json` is labeled
  truth material and was never prompt content; `PROMPT_HASHES.json` documents
  that prompts contained only release artifacts and metadata statements. No
  transcripts exist to leak-scan.
- Parallel-phase note: Phases 1 and 3 ran concurrently in this repository; all
  git operations here used namespace-restricted pathspec commits, and the
  freeze/outcomes commits contain only this namespace's files.

## 8. Deliverable index

`HEALTH.json` · `PREREGISTRATION.md` · `TASK_SELECTION.md` · `FREEZE.json` ·
`PROMPT_HASHES.json` · `selection/` (census.json, reference_solvers/,
reference_solve_run.jsonl) · `fixtures/` (tasks/, rt_transform/,
decode_equality_log.json, prompt_instantiation_index.json) · `policies/`
(rule_a_permissive_v3.py, rule_b_stress_legacy.py, rule_c_cleanup.py) ·
`oracle/answers.json` · `sessions/EMPTY_STATE.md` · `regrade/EMPTY_STATE.md` ·
`results.jsonl` · `summary.json` · `REPORT.md` (this file) ·
`BUDGET_LEDGER.jsonl` entries · git commits (freeze `08d9fb5` → outcomes).
