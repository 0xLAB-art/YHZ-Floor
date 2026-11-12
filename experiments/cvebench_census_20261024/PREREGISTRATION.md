# PREREGISTRATION — CVE-Bench external source census (expanded-source option) with conditional grid

- **Protocol:** CVEBENCH-CENSUS-v1 (namespace `cvebench_census_20261024`)
- **Date frozen:** 2026-10-24 (freeze committed before any experiment model call — of which none exist)
- **Plan source:** `sp2027/research_execution/REMAINING_EXPERIMENTS_PLAN_20261023.md` (Global constraints) + the phase prompt for the CVE-Bench census ("the expanded-source option" named in the Phase 2 report's §6 "What a future re-plan would need")
- **Status of this preregistration:** frozen conditional design; **the census arm executed and the early stop fired at task selection** (quorum unmet: 0 of 40 tasks qualify). No experiment model call was made under this preregistration. The only provider call in this namespace is one 16-token `AUTH_SMOKE` probe (`HEALTH.json`, classified non-evidence).

## 1. Objective

Test whether the expanded external source (the pinned CVE-Bench archive) can
supply the qualifying crypto-task pool that the pinned Cybench archive could
not (its own census yielded 4 of 14; `external_admission_20261024/`), and if so,
run the same portability + evaluator-sensitivity grid on it. Selection criteria
are mirrored **exactly** from `external_admission_20261024/TASK_SELECTION.md`.
Every conclusion, had the grid run, would have been labeled **portability +
evaluator sensitivity under OUR stress rule** — never a native benchmark defect,
and describing the pinned snapshot only.

## 2. Key inputs (read-only)

- `sp2027/analysis/external_validation_20261021/RESEARCH_PLAN.md` (evidence levels 1–2)
- `sp2027/analysis/external_validation_20261021/SOURCE_PREFLIGHT_V2.json` (pinned CVE-Bench archive path + sha256 + 550 regular files)
- Pinned archive: `human_audit/source_freeze_20261005/archives/cve_bench__cve-bench__9fb3e068f260.tar.gz`, sha256 `b7ccc67e777412e46ec4dbff1f0a3871ff268cb9ac4f3ce4f6db7f799ee9c239` — re-verified this phase (`ARCHIVE_VERIFICATION.json`); extracted read-only to `/tmp/cvebench_pin/`
- Selection criteria to mirror: `external_admission_20261024/TASK_SELECTION.md` (5 criteria)
- rt_transform semantics, **hash-referenced**: `external_admission_20261024/fixtures/rt_transform/build_representations.py` (sha256 `5b12a85329539053eb5bd7f4539c7bfe27910cba39d53cee3379c2d5756a649e`), `verify_decode_equality.py` (sha256 `27d2263fadf50aeca2965b79f51e28f5a06afd4bfbbc79cfcfa1089c5b8e4cc0`) — recomputed this phase
- Policy snapshots, **hash-referenced**: `external_admission_20261024/policies/rule_a_permissive_v3.py` (sha256 `372bab44bc12ff6a377671516217f268e55132cda9d0304405d1c8619602df6f`), `rule_b_stress_legacy.py` (sha256 `257b7805a847729c29ebf2960b6d00d7a73845721459fbd3fd972b36c93a2891`), `rule_c_cleanup.py` (sha256 `7419e861a4d1abeb5f9d7623ab2b4c4d79ef4647b7ea186639379771313a4373`) — recomputed this phase
- Runner pattern: `sp2027/research_execution/run_info_contract_2x2_chacha20.py` + the `external_admission_20261024` client/smoke pattern
- Provider: `claude-sonnet-4-6-free` via APMIX (`.env`), Anthropic-compatible `/v1/messages`; provider-attested route label only, no hosted-weight identity claimed.

## 3. Step-zero health rule (preregistered)

One 16-token `AUTH_SMOKE` probe through the exact session code path
(`ApmixClient.call`), logged in `HEALTH.json` as non-evidence, excluded from
all analyses (2026-10-18 NO-GO pilot protocol). Executed 2026-10-24: OK
(`msg_5b7f43c1eb77e7f6027b4e78`, 11 input / 4 output tokens). Any pre-output
provider failure would have been retained verbatim as infrastructure, never a
task failure, never retried.

## 4. Seed range (verified unused before freezing)

Seeds **95–96** for the grid arm. Verified before the freeze against every
`PREREGISTRATION.md` and every `results.jsonl` under `sp2027/`: zero prior use
of seed 95 or 96 anywhere (prior ranges in use: 1–2, 41–44, 5002, 61–64, 71–72,
81–84). No collision → no escalation needed; no seed replacement permitted
later.

## 5. Census rule (fixed before outcome inspection)

From the pinned archive's task tree, keep tasks where ALL hold (criteria
mirrored exactly from `external_admission_20261024/TASK_SELECTION.md`):

1. metadata `categories` includes `crypto`;
2. the final subtask answer is a static deterministic string, exact-match checkable under native semantics;
3. runnable offline in the harness: no target service, no service-by-construction challenge, artifacts complete in release files;
4. public task statement (release files + metadata prompts);
5. solvable offline by a program admissible under the frozen declared rule (v3 inert-stdlib set) within the fixed per-session token budget.

Every exclusion recorded with a reason (`TASK_SELECTION.md`,
`selection/census.json`). Qualifiers require offline stdlib-only reference
solvers reproducing their answers exactly (`selection/reference_solve_run.jsonl`).

## 6. Conditional grid (frozen; contingent on quorum — NOT triggered)

If ≥ 6 tasks qualify:

- Freeze task IDs + per-task source-file SHA-256 + instantiated prompts
  (`PREREGISTRATION.md` + `FREEZE.json` committed before any experiment model call).
- Hard decode-equality gate for R0/RT reusing the hash-referenced
  `verify_decode_equality.py` semantics; generation forbidden unless PASS.
- Grid: 6 tasks × {R0, RT} × seeds {95, 96} = 24 sessions; ≤2 turns; turn-1
  generation, turn-2 identical rejection feedback across arms; fixed
  `max_tokens` 1600; temperature provider default; one model route
  (`claude-sonnet-4-6-free`).
- Terminal states restricted to the project enum: SUCCESS · ORACLE_FAIL ·
  TIMEOUT · AGENT_GIVEUP · MODEL_REFUSAL · TOOL_FAILURE ·
  PROVIDER_UNAVAILABLE · HARNESS_ERROR. Every failure retained; no retries; no
  seed replacement. A session failing provider-side before model content is
  `PROVIDER_UNAVAILABLE` (infrastructure), never a task failure. If the
  provider failed on most consecutive sessions, the phase stops with status
  `halted`.
- Offline triple regrade on retained programs with the hash-referenced policy
  snapshots (a) declared permissive rule, (b) OUR counterfactual stress rule,
  (c) rule (b) + output-preserving unused-import cleanup with byte-identical
  stdout check; tasks weighted equally in the primary contrast.

## 7. Prespecified falsifiers (if the grid runs — same form as Phase 2)

- **F1:** regrade (b) moves the per-task representation contrast outside ±10
  percentage points on ≥ half the tasks → mechanism ports.
- **F2:** movement within the margin on most tasks → honest null (fixture-specific).
- **F3:** cleanup fails output preservation on any program → analysis defect;
  investigate, do not publish the contrast.

## 8. Early-stop rule (preregistered) and its execution

The phase prompt prescribes: *if fewer than 6 tasks qualify, stop honestly with
status `no_go` — census-only, zero sessions, every exclusion documented.*

**Executed on 2026-10-24.** Census of the pinned archive: 40 task entries, all
under `src/critical/`; the metadata schema (12 uniform keys across all 40) has
**no `categories` field**, so the crypto-category universe is empty and
criterion 1 fails for every task — corroborated by criteria 2 (native scorer is
a server-side exploit probe, `src/cvebench/cvebench.py:82`, not a static answer
string), 3 (all 40 compose.yml define a Docker `target` service;
`application_url` is a live in-network host for all 40), and 5 (the protected
secret file/table exists only inside the running service). **0 qualify**; 0 < 6
→ status **no_go**. No criterion was relaxed; no non-crypto or service-bound
task was admitted; the Cybench census's 4 qualifying tasks are not pooled or
imported.

Consequences: falsifiers F1–F3 are **NOT EVALUABLE** (no sessions, no
programs); the representation contrast, decode-equality gate, regrade triple,
and portability conclusion are not produced. Nothing was fabricated; the
census-only path commits its census artifacts.

## 9. Analysis plan (would have been executed on 24 sessions)

Per-task table; equal-weight paired within-task representation contrast under
each rule; sign test across tasks; **NO benchmark-quality claim; NO pooling
with H1-R3 numbers or with the Phase 2 Cybench cohort.**

## 10. Deliverables in this state

`HEALTH.json`, `ARCHIVE_VERIFICATION.json`, `PREREGISTRATION.md`,
`TASK_SELECTION.md`, `FREEZE.json`, `PROMPT_HASHES.json`, `selection/`
(census.json, reference_solve_run.jsonl zero-record + empty-state note),
`fixtures/` (empty-state note incl. decode-equality status), `sessions/` and
`regrade/` (empty-state notes), `results.jsonl` (zero session rows),
`summary.json`, `REPORT.md`, `BUDGET_LEDGER.jsonl` entries, git commits
(freeze → outcomes).
