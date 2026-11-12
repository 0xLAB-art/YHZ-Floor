# PREREGISTRATION — Phase 2: External-task admission portability (Cybench crypto subset)

- **Protocol:** PHASE2-EXTERNAL-ADMISSION-v1 (namespace `external_admission_20261024`)
- **Date frozen:** 2026-10-24 (freeze committed before any experiment model call)
- **Plan source:** `sp2027/research_execution/REMAINING_EXPERIMENTS_PLAN_20261023.md` (Phase 2, APPROVED)
- **Status of this preregistration:** frozen design; **early stop executed at task selection** (selection quorum unmet). No experiment model call was made under this preregistration. The only provider call in this namespace is one 16-token `AUTH_SMOKE` probe (`HEALTH.json`, classified non-evidence).

## 1. Objective

Reproduce the admission-mechanism result — a representation contrast on fixed
programs moved by an admission-rule change, plus an output-preserving cleanup
control — on independently authored tasks (the Cybench crypto subset), under
our evaluator. Every conclusion would have been labeled **portability +
evaluator sensitivity under OUR stress rule**. This design never asserts a
native Cybench defect: the preflight (`sp2027/analysis/external_validation_20261021/SOURCE_PREFLIGHT_V2.json`)
found no import gate in Cybench's inspected entrypoints; the narrower rule is
**OUR counterfactual stress rule**, provenance-justified from the H1-R3 legacy
filter (`sp2027/analysis/h1r3_20261019/h1r3_contract.py` `POLICIES["legacy"]`).

## 2. Key inputs (read-only)

- `sp2027/analysis/external_validation_20261021/RESEARCH_PLAN.md` (evidence levels 1–2; portability framing)
- `sp2027/analysis/external_validation_20261021/SOURCE_PREFLIGHT_V2.json` (pinned archive path + sha256)
- Pinned archive: `human_audit/source_freeze_20261005/archives/cybench__cybench__ca483c6443f1.tar.gz`, sha256 `261cc002d315776cf424322a18a645a21b48b418f1425e3b10271e298da0b805` (re-verified this phase with `sha256sum`)
- Legacy-filter semantics: `sp2027/analysis/h1r3_20261019/h1r3_contract.py` (policies, `qualify_source`)
- Cleanup transform: `sp2027/analysis/contribution_audit_20261021/policy_mechanism/audit.py` (`transform`, unused-import removal)
- H1-R3 admission context: `sp2027/paper/anonymous_reviewer_artifact_v23/h1r3_check.py` (read-only)
- Runner pattern: `sp2027/research_execution/run_info_contract_2x2_chacha20.py` + `runs_009/provider_adapter.py`
- Provider: `claude-sonnet-4-6-free` via APMIX (`.env`), Anthropic-compatible `/v1/messages`; provider-attested route label only, no hosted-weight identity claimed.

## 3. Task selection rule (fixed before outcome inspection)

From the pinned archive's task tree (`benchmark/`, 43 task entries; the plan's
"`tasks/`" tree corresponds to this path in the snapshot — no `tasks/` directory
exists), keep tasks where ALL hold:

1. metadata `categories` includes `crypto`;
2. the final subtask answer is a static deterministic string, exact-match checkable (native semantics confirmed: `analytics/analyze_benchmark_run.py:111` compares `stdout.strip() == expected_answer`);
3. runnable offline in the harness: no external service (no `target_host`, no service-by-construction challenge), artifacts complete in the release files;
4. task statement public (release files + metadata prompts);
5. solvable by a program admissible under the frozen declared permissive rule within the fixed per-session token budget.

Target: 6 tasks. **Every exclusion recorded with a reason** (`selection/census.json`, `TASK_SELECTION.md`).

## 4. Representations (information-preserving; hard gate)

- **R0 (canonical):** task statement verbatim from metadata `hard_prompt`; provided release artifacts (`source.py`, `output.txt`) embedded verbatim; the same files are written to the solver program's working directory at execution time.
- **RT (transformed):** identical statement text; each provided artifact presented base64-encoded with an explicit decode note ("decode with base64.b64decode to obtain the exact original file bytes").
- **Hard gate:** `fixtures/rt_transform/verify_decode_equality.py` must verify, before any generation, that every RT artifact block decodes byte-identically to its R0 fixture file AND the statement text is identical across representations. Gate status recorded in `fixtures/decode_equality_log.json`. Generation is forbidden unless the gate PASSes.
- Seeds 71/72 carry no per-seed randomness; prompt text per (task, representation) is identical across seeds.

## 5. Session grid (frozen; not executed)

- 6 tasks × {R0, RT} × seeds {71, 72} = 24 sessions; ≤2 turns; turn-1 generation, turn-2 identical rejection feedback across arms; fixed `max_tokens` 1600; temperature provider default; one model route (`claude-sonnet-4-6-free`).
- Terminal states restricted to the project enum: SUCCESS · ORACLE_FAIL · TIMEOUT · AGENT_GIVEUP · MODEL_REFUSAL · TOOL_FAILURE · PROVIDER_UNAVAILABLE · HARNESS_ERROR. Every failure retained; no retries; no seed replacement. A session failing provider-side before model content is `PROVIDER_UNAVAILABLE` (infrastructure), never a task failure. If the provider failed on most consecutive sessions, the phase stops with status `halted`.

## 6. Offline triple regrade (on retained programs)

- **(a) Declared permissive rule:** the v3 inert-stdlib module set (17 modules) with the H1-R3 sandbox checks — snapshot `policies/rule_a_permissive_v3.py` (verbatim port of `h1r3_contract.py`).
- **(b) OUR counterfactual stress rule:** legacy import filter {json, sys, base64} with the same other checks — snapshot `policies/rule_b_stress_legacy.py`. Labeled as our stress-test rule; never a Cybench-native rule.
- **(c) Rule (b) + output-preserving unused-import cleanup** with a byte-identical stdout check — snapshot `policies/rule_c_cleanup.py` (verbatim port of the audit.py `transform` plus comparison harness).
- Recorded per arm: rejections with violation reasons, corrected-outputs check, per-task contrast movement; tasks weighted equally in the primary contrast.

## 7. Prespecified falsifiers

- **F1:** regrade (b) moves the per-task representation contrast outside ±10 percentage points on ≥ half the tasks → mechanism ports.
- **F2:** movement within the margin on most tasks → honest null (fixture-specific).
- **F3:** cleanup fails output preservation on any program → analysis defect; investigate, do not publish the contrast.

## 8. Analysis plan (would have been executed on 24 sessions)

Per-task table; equal-weight paired within-task representation contrast under each rule; sign test across tasks; **NO benchmark-quality claim; NO pooling with H1-R3 numbers.**

## 9. Early-stop rule and its execution

The phase prompt prescribes: *if fewer than 6 tasks qualify, stop honestly with status `no_go` and document the selection.*

**Executed on 2026-10-24.** Census of the pinned archive: 14 crypto-category tasks; 9 excluded (external service or service-by-construction, with non-stdlib solver dependencies), 1 excluded (official solver requires pycryptodome AES + sympy CRT, outside the frozen declared admission set within the fixed token budget), **4 qualify** (verified by offline stdlib-only reference solves reproducing the metadata answers exactly — `selection/reference_solve_run.jsonl`). 4 < 6 → status **no_go**. Robustness: admitting Permuted despite its exclusion grounds would still yield 5 < 6.

Consequences: falsifiers F1–F3 are **NOT EVALUABLE** (no sessions, no programs); the representation contrast, regrade triple, and portability conclusion are not produced. Nothing was fabricated to fill the quorum; task selection was not widened post hoc to reach 6.

## 10. Deliverables in this state

`HEALTH.json`, `PREREGISTRATION.md`, `TASK_SELECTION.md`, `FREEZE.json`,
`PROMPT_HASHES.json`, `selection/` (census, reference solvers + run log),
`fixtures/` (task fixtures, RT transform, decode-equality log),
`policies/` (rule snapshots), `oracle/answers.json` (truth material, never
prompt content), `sessions/` and `regrade/` (empty with explicit empty-state
notes), `results.jsonl` (zero session rows), `summary.json`, `REPORT.md`,
`BUDGET_LEDGER.jsonl` entries, git commits (freeze → outcomes).
