# TASK_SELECTION — CVE-Bench external source census (expanded-source option), 2026-10-24

Purpose: document the task census, selection verdicts, and exclusion reasons for
the CVE-Bench expanded-source census, made **before outcome inspection** (no
experiment session, no program, and no experiment model call exists in this
namespace; the only provider call is the non-evidence AUTH_SMOKE probe recorded
in `HEALTH.json`).

## Source and provenance

- Pinned archive: `human_audit/source_freeze_20261005/archives/cve_bench__cve-bench__9fb3e068f260.tar.gz`
- sha256 (recomputed this phase, twice: `sha256sum` and a streaming hashlib pass
  inside the census command): `b7ccc67e777412e46ec4dbff1f0a3871ff268cb9ac4f3ce4f6db7f799ee9c239`
  — matches `sp2027/analysis/external_validation_20261021/SOURCE_PREFLIGHT_V2.json`
  exactly (550 regular files recorded there; 550 extracted and counted here).
- Extraction for inspection: read-only `tar -xzf` into `/tmp/cvebench_pin/`
  (outside the repository; tree made read-only). The archive was never modified.
  Verification details and exact commands: `ARCHIVE_VERIFICATION.json`.
- Tree note: the pinned snapshot contains a single severity tree, `src/critical/`
  (checked: no `src/high|medium|low` paths exist), with **40 task entries** —
  each `src/critical/challenges/CVE-*/` carries `eval.yml` + `compose.yml` (+ `.env`),
  with `src/critical/metadata/CVE-*.yml`, `src/critical/nvd/CVE-*.json` and
  `src/critical/evaluations/*_grader.py` alongside. Challenge dirs, metadata
  files and NVD files cross-check 40 / 40 / 40 (no orphans either way, checked
  with `comm`).

## Selection criteria (mirrored exactly from external_admission_20261024/TASK_SELECTION.md, fixed before outcome inspection)

1. metadata `categories` includes `crypto`;
2. final subtask answer is a static deterministic string (native exact-match
   semantics — in Phase 2 this was confirmed at Cybench's
   `analytics/analyze_benchmark_run.py:111`; the CVE-Bench analogue is checked
   below);
3. runnable offline in the harness: no `target_host` analogue, no
   service-by-construction challenge, artifacts complete in release files;
4. public task statement;
5. solvable offline by a program admissible under the frozen declared rule
   (v3 inert-stdlib module set, hash-verified snapshot
   `external_admission_20261024/policies/rule_a_permissive_v3.py`) within the
   fixed per-session token budget.

## Headline census result

**0 of 40 tasks qualify. The crypto-category universe of this snapshot is empty.**

The five criteria are conjunctive, and criterion 1 fails for every task on
schema grounds, before any per-task judgment:

- The metadata schema is **uniform across all 40 tasks** with exactly 12 keys:
  `additional_info, admin_username, application_url, attacker_role,
  default_password, default_username, denial_of_service_duration,
  outbound_service_url, proof_uploading_url, remote_code_executable_path,
  secret_file_path, secret_table_name`. **No `categories` field exists.**
- Grep evidence (all zero): `categor` in `src/critical/metadata/*.yml` → 0;
  `categor` in `src/critical/challenges/*/eval.yml` → 0; case-insensitive
  `crypto` in metadata + eval.yml + README.md → 0. (The only `categor` hits in
  the archive are e-commerce product-catalog rows inside challenge `db.sql`
  data dumps, e.g. `src/critical/challenges/CVE-2024-34716/db/db.sql` — challenge
  payload data, not task metadata.)
- This is a property of the benchmark's task domain, not a defect:
  `README.md:1` — "CVE-Bench: A Benchmark for AI Agents' Ability to Exploit
  Real-World Web Application Vulnerabilities". Its tasks are live web-application
  exploitation, not CTF-style crypto puzzles.

The remaining criteria were still evaluated per task for completeness; they
corroborate the structural exclusion:

- **Criterion 2 fails for all 40.** The native scorer is a server-side exploit
  probe, not a static answer string: `src/cvebench/cvebench.py:82`
  `scorer=check_exploit(STORE_KEY_ATTACK_SUCCESSFUL, check_target_server_for_exploit_success)`
  (same at line 109 for the solution task; `GRADER_EXEC_TIMEOUT_SECONDS = 500`
  bounds the `done.sh` end-to-end check at `cvebench.py:53`). There is no
  exact-match comparison against a release-stored answer.
- **Criterion 3 fails for all 40 (service-by-construction).** Every
  `compose.yml` defines a Docker `target` web service (11 via
  `compose-target.yml` extends, the other 29 via other extends/inline defs —
  all 40 verified to contain a `  target:` service key). Every metadata
  `application_url` points at a live in-network host (`target:9090` ×30,
  `target:80` ×5, `target:8080` ×3, plus single variants `target:1337`,
  `server:9090`, `target:9090/url`, and two multi-host entries); the prompt
  variant text directs the agent to interact with `target:<port>` and to verify
  success via `curl http://target:9091/done`.
- **Criterion 4 passes** (the `eval.yml` prompts ship in the release files) —
  the only criterion that does not exclude.
- **Criterion 5 fails for all 40.** The protected object — the goal "answer" —
  exists only inside the running service: secret file `/tmp/secret` (38 tasks),
  `/tmp/uploads/secret` (1), `/app/secret` (1); secret table name `secret`
  (39) / `SECRET` (1). No offline-computable value exists in the release files,
  so no offline admissible stdlib program could produce an answer.

## Complete census (40 tasks; machine-readable form with per-task criterion verdicts in `selection/census.json`)

| Task (metadata `src/critical/metadata/<id>.yml`) | application_url | Verdict | Ground |
|---|---|---|---|
| CVE-2023-37999 | target:9090 | EXCLUDED | C1 (no categories field) + C2/C3/C5 |
| CVE-2023-51483 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-22120 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-2359 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-25641 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-2624 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-2771 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-30542 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-31611 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-32167 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-3234 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-32511 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-32964 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-32980 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-32986 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-34070 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-3408 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-34340 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-34359 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-34716 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-3495 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-35187 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-3552 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-36412 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-36675 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-36779 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-36858 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-37388 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-37831 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-37849 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-4223 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-4320 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-4323 | target:9090/url | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-4442 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-4443 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-4701 | target:80 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-5084 | target:80 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-5314 | target:8080,server:10051 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-5315 | target:9090 | EXCLUDED | C1 + C2/C3/C5 |
| CVE-2024-5452 | target:1337 | EXCLUDED | C1 + C2/C3/C5 |

(Port counts from the raw metadata values: `target:9090` 30 — of which one is
`target:9090/url` and one pairs `mailhog:8025` — `target:80` 5, `target:8080` 3,
`target:1337` 1, `server:9090` 1. `CVE-2024-2624`'s metadata block shown above in
session is representative; per-task raw values are in `selection/census.json`.)

## Verification evidence for the qualifying set

None exists, because **the qualifying set is empty**. No reference solver was
written or run (there is no answer to reproduce: the native goal object lives
inside the running service, and no static answer string exists to compare
against). `selection/reference_solve_run.jsonl` is committed with zero records
and `selection/REFERENCE_SOLVE_EMPTY_STATE.md` documents this explicitly.

## Quorum decision

- Required: 6 tasks. Qualified: **0**. → **no_go** (honest early stop,
  census-only, zero experiment sessions), as prescribed by the phase prompt
  and the plan's Phase-2-style acceptance ("≥6 tasks frozen or honest early
  stop documented").
- Robustness: the failure is structural, not a judgment call — criterion 1
  fails on schema grounds for every task; there is no admissible re-reading of
  the other criteria that could add a crypto-category task that does not exist
  in the snapshot.
- No criterion was relaxed and no non-crypto or service-bound task was admitted
  to reach 6. The Cybench census's 4 qualifying tasks
  (`external_admission_20261024/`) are a different source under that phase's
  own frozen design and are **not** pooled or imported here.

## Boundary

This census describes the pinned 2026-10-05 snapshot only. The absence of a
crypto category is a property of CVE-Bench's task domain (real-world
web-application exploitation). It supports no claim about the current upstream
repository, other archives, other task categories, or benchmark quality.
Nothing in this phase is described as a native benchmark defect.
