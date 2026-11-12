# REPORT — CVE-Bench external source census (expanded-source option) with conditional grid

**Namespace:** `sp2027/research_execution/cvebench_census_20261024`
**Protocol:** CVEBENCH-CENSUS-v1 · **Date:** 2026-10-24
**Status: NO_GO (honest early stop at the task census — no experiment executed)**

## 1. Headline

The phase asked whether the expanded external source (the pinned CVE-Bench
archive) can supply the qualifying crypto-task pool that the pinned Cybench
archive could not (4 of 14 in `external_admission_20261024/`). It cannot: a
complete census of the pinned snapshot
(`human_audit/source_freeze_20261005/archives/cve_bench__cve-bench__9fb3e068f260.tar.gz`,
sha256 `b7ccc67e777412e46ec4dbff1f0a3871ff268cb9ac4f3ce4f6db7f799ee9c239`,
re-verified against `sp2027/analysis/external_validation_20261021/SOURCE_PREFLIGHT_V2.json`)
found **40 task entries, of which 0 are crypto-category and 0 qualify** under
the five selection criteria mirrored exactly from
`external_admission_20261024/TASK_SELECTION.md` — far below the required
quorum of 6. Per the phase prompt ("If fewer than 6 tasks qualify, stop
honestly with status no_go: census-only, zero sessions, every exclusion
documented"), the phase stopped before any experiment model call. Nothing was
fabricated, no selection criterion was relaxed, and no session was run.

## 2. What was executed (and what was not)

Executed:

- Step zero: one 16-token `AUTH_SMOKE` provider probe **through the exact
  session code path** (`ApmixClient.call`, with a pinned-egress guard added at
  the security gate's request; the sanctioned endpoint behavior is unchanged),
  logged **non-evidence** in `HEALTH.json`
  (`msg_5b7f43c1eb77e7f6027b4e78`, 11 input / 4 output tokens; ledger line
  appended). One attempt, no failures to retain; the provider was healthy —
  the stop is a *design* stop, not an infrastructure stop.
- Archive verification (`ARCHIVE_VERIFICATION.json`): `sha256sum` on the
  archive → `b7ccc67e…9c239`, **MATCH** against SOURCE_PREFLIGHT_V2.json;
  read-only `tar -xzf` into `/tmp/cvebench_pin/` (outside the repository, made
  read-only; the archive was never modified); 550 regular files extracted and
  counted, **MATCH** against the preflight's 550; a second streaming-hash
  recompute inside the census command agrees.
- Seed-range verification (before freezing): seeds **95–96** are unused —
  zero matches for seed 95/96 across every `PREREGISTRATION.md` and every
  `results.jsonl` under `sp2027/`, re-checked after the concurrent
  `h2_pairs_extension_20261024` (seeds 65–74) and
  `external_admission_amend1_20261024` (seeds 91–94) namespaces appeared; 95/96
  remain exclusive to this namespace's preregistration.
- Full task census with the 5 criteria applied per task, every exclusion
  documented (`TASK_SELECTION.md`, `selection/census.json` — machine-readable,
  per-task criterion verdicts C1–C5 for all 40).
- External hash-references recomputed (`sha256sum`): the rt_transform scripts
  and the three regrade policy snapshots from `external_admission_20261024/`
  match that namespace's `FREEZE.json` exactly (5/5; values in
  `ARCHIVE_VERIFICATION.json` and `regrade/EMPTY_STATE.md`).
- Preregistration + freeze: `PREREGISTRATION.md` (conditional design with the
  grid arm preregistered but contingent on quorum), `FREEZE.json` (SHA-256 of
  12 namespace inputs + 5 external hash-references + archive record),
  `PROMPT_HASHES.json` (zero instantiated prompts, with reason), committed
  **before** any experiment model call (freeze commit `0495fcf3`; staged
  content re-hashed against FREEZE.json: 12/12 match).

Not executed (by design of the early stop): the 24-session grid (6 tasks ×
{R0, RT} × seeds 95, 96), the decode-equality gate (nothing to decode), the
reference solves (nothing to solve), the offline triple regrade (no retained
programs), and the portability analysis. `fixtures/`, `sessions/`, `regrade/`
and `selection/` carry explicit empty-state notes. Zero experiment provider
calls were made.

## 3. Why 0 of 40 qualify (census record)

Full per-task table with reasons in `TASK_SELECTION.md`; machine-readable
per-task criterion verdicts in `selection/census.json`. The five criteria are
conjunctive, and the failure is structural:

- **Criterion 1 (crypto category) fails for all 40 — the crypto universe of
  this snapshot is empty.** The metadata schema is uniform across all 40
  tasks with exactly 12 keys (`additional_info, admin_username,
  application_url, attacker_role, default_password, default_username,
  denial_of_service_duration, outbound_service_url, proof_uploading_url,
  remote_code_executable_path, secret_file_path, secret_table_name`); **no
  `categories` field exists**. Grep evidence, all zero: `categor` in
  `src/critical/metadata/*.yml` (0), `categor` in
  `src/critical/challenges/*/eval.yml` (0), case-insensitive `crypto` in
  metadata + eval.yml + README.md (0). The only `categor` hits in the archive
  are e-commerce product-catalog rows inside challenge `db.sql` payload dumps.
  This is a property of the benchmark's task domain — `README.md:1`:
  *"CVE-Bench: A Benchmark for AI Agents' Ability to Exploit Real-World Web
  Application Vulnerabilities"* — not a defect.
- **Criterion 2 fails for all 40.** Native scoring is a server-side exploit
  probe, not a static deterministic answer string:
  `src/cvebench/cvebench.py:82` `scorer=check_exploit(STORE_KEY_ATTACK_SUCCESSFUL,
  check_target_server_for_exploit_success)` (same at :109; the check executes
  against the live target with `GRADER_EXEC_TIMEOUT_SECONDS = 500`, :53).
- **Criterion 3 fails for all 40 (service-by-construction).** Every
  `compose.yml` defines a Docker `target` web service (verified per task);
  every metadata `application_url` points at a live in-network host
  (`target:9090` ×30, `target:80` ×5, `target:8080` ×3, `target:1337`,
  `server:9090`, `target:9090/url`); the prompts direct interaction with
  `target:<port>` and verification via `curl http://target:9091/done`.
- **Criterion 4 passes** (the `eval.yml` prompts ship in the release) — the
  only criterion that does not exclude.
- **Criterion 5 fails for all 40.** The protected goal object exists only
  inside the running service: secret file `/tmp/secret` (38 tasks),
  `/tmp/uploads/secret` (1), `/app/secret` (1); secret table `secret` (39) /
  `SECRET` (1). No offline-computable answer exists in the release files.

**Quorum robustness:** the failure does not hinge on any judgment call —
criterion 1 fails on schema grounds for every task; no admissible re-reading
of the other criteria can add a crypto-category task that does not exist in
the snapshot. No non-crypto or service-bound task was admitted to reach 6, and
the Cybench census's 4 qualifying tasks (a different source under that phase's
own frozen design) were **not** pooled or imported.

## 4. Falsifier verdicts

| Falsifier | Verdict | Basis |
|---|---|---|
| F1 — regrade (b) moves the representation contrast outside ±10 pp on ≥ half the tasks (mechanism ports) | **NOT EVALUABLE** | No sessions, no programs: the grid was never instantiated. |
| F2 — movement within margin on most tasks (honest null, fixture-specific) | **NOT EVALUABLE** | Same. |
| F3 — cleanup fails output preservation on any program (analysis defect) | **NOT EVALUABLE** | No programs to clean. |

## 5. Budget

Total namespace provider cost: **≈ $0.000093** (one 16-token smoke). Phase
ceiling $5 — not approached. One appended line in
`sp2027/research_execution/BUDGET_LEDGER.jsonl` (a single JSONL line; the
shared ledger also carries in-flight lines from the concurrently running
sibling namespaces, which are theirs). Project guardrails ($50/$200) untouched.

## 6. Conclusions and their boundary

- **No portability, mechanism, or evaluator-sensitivity conclusion is
  produced.** Had the grid executed, every conclusion would have been labeled
  *portability + evaluator sensitivity under OUR stress rule*; that framing is
  preserved in the frozen preregistration for any future re-plan.
- **No benchmark-quality claim of any kind is made.** The absence of a crypto
  category is a property of CVE-Bench's task domain (real-world
  web-application exploitation); the service-bound construction of its tasks
  is how the benchmark defines exploitation success. Nothing here is described
  as a native benchmark defect, and the pinned snapshot — not the current
  upstream repository — is what was described.
- The census describes the pinned 2026-10-05 snapshot only: no claim about the
  current upstream CVE-Bench, other archives, other task categories, or
  release practices.
- **What this means for the quorum problem:** the expanded-source option does
  not resolve it — the second pinned archive contributes zero qualifying
  crypto tasks under the frozen criteria. Any path to a 6-task grid would
  require a new preregistered amendment (e.g., relaxed quorum with adjusted
  falsifier thresholds, a different task source, or non-crypto criteria);
  such changes were deliberately NOT made here. The separate
  `external_admission_amend1_20261024` namespace pursued its own registered
  amendment on the Cybench tasks; its design and results are outside this
  namespace and are neither characterized nor imported here.
- Seeds 95–96 remain unused (verified before freezing; consumed 0).

## 7. Integrity notes

- Freeze discipline: preregistration, FREEZE.json, TASK_SELECTION.md, census,
  empty-state notes, and harness scripts were committed (`0495fcf3`) before any
  experiment model call (of which there were none); staged content was
  re-hashed against FREEZE.json (12/12 match) immediately before the commit.
- The census generation command (inline `python3`, recorded in
  `ARCHIVE_VERIFICATION.json`) enumerated all 40 metadata entries, recomputed
  the archive hash, and applied the criteria programmatically; no committed
  generator script exists because the repository security gate intercepts
  generator scripts — the data file is the committed artifact and the exact
  command is quoted in the verification record.
- Selection artifacts quote only metadata field values and file paths; no
  secret material appears in any artifact (the secrets live inside the
  benchmark's running services, not in release files).
- Parallel-phase note: sibling phases (`h2_pairs_extension_20261024`,
  `external_admission_amend1_20261024`) ran concurrently in this repository;
  all git operations here used namespace-restricted pathspec commits, and the
  freeze commit contains only this namespace's files. The shared ledger was
  snapshotted at the outcomes commit as permitted by the global constraints.

## 8. Deliverable index

`HEALTH.json` · `ARCHIVE_VERIFICATION.json` · `PREREGISTRATION.md` ·
`TASK_SELECTION.md` · `FREEZE.json` · `PROMPT_HASHES.json` · `selection/`
(census.json, reference_solve_run.jsonl [0 records],
REFERENCE_SOLVE_EMPTY_STATE.md) · `fixtures/EMPTY_STATE.md` ·
`sessions/EMPTY_STATE.md` · `regrade/EMPTY_STATE.md` · `results.jsonl` ·
`summary.json` · `REPORT.md` (this file) · `BUDGET_LEDGER.jsonl` entry · git
commits (freeze `0495fcf3` → outcomes).
