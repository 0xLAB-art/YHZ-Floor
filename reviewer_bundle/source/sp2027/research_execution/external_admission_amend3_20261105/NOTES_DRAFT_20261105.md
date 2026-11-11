# AMENDMENT 3 — preparation notes (DRAFT 2026-11-05, $0, offline)

## What this namespace is

Preparation workspace for **Amendment 3** of the external-admission portability
line. It turns the paper's weakest point — *"portability remains unestablished"*
(§7) — into an answerable registered experiment, by fixing, **pre-outcome**, the
exact defect classes that made the previous attempts degenerate.

Every artifact here is offline: the pinned NYU CTF archive inspection, the census,
the compat gate, and the policy drafts. Zero model calls, zero sessions, $0.

## The defect → fix map (the "why we couldn't apply it" record)

| # | Defect in the previous attempts | Where it is recorded today | Amendment-3 fix (already prepared here) |
|---|---|---|---|
| 1 | Task pool too small: pinned Cybench crypto subset = 4 qualifying < quorum 6; CVE-Bench = 0 crypto (all service-bound) | `external_admission_20261024/REPORT.md` §1, §6 | Expansion source already pinned in the source freeze: **NYU CTF Bench**, sha `ad376a2e…` — census run (below) finds **16 offline candidates** under the SAME frozen rule ⇒ 4+16 candidates, quorum reachable with zero criterion relaxation |
| 2 | Prompt/rule interface contradiction: v3 boundary clause admits only `open(sys.argv[1],"r")` while the frozen prompts direct cwd-name reads ⇒ 0/37 admissible, mechanism untestable | amend1 REPORT §1, §4; paper Appendix D.3 'Regrade-degeneracy explanation' | **Compat pre-gate** (`compat_gate/`): at freeze time, the minimal contract-reference program must QUALIFY under EVERY arm. Demonstration ran on the amendment-1 FROZEN prompts: un-repaired arms 0/8 (this is the 37/37 class, caught pre-freeze), repaired arms 8/8 |
| 3 | Boundary repair applied late + asymmetrically (declared only, then back-applied to stress as a post-outcome deviation) | amend2 20261029 REPORT §6 boundary 7; PREREGISTRATION.md §7 | Registered pairing from the start: stress arm = `POLICIES["legacy"]` + repaired boundary, shipped as `policies_amend3_draft/rule_b_stress_legacy_repaired.py` (verbatim v4-module copy, diff-verified) — the deviation class cannot recur |
| 4 | F1 computed wrong once (admission rates treated as the representation contrast inside a freeze claim; −100/−33.3/0/−77.8 pp withdrawn) | amend2 20261029 `FREEZE_CORRECTION.md` §1–2 | The registered F1 script (`regrade_amend3_contrast.py`) is frozen INSIDE FREEZE.json; the REPORT is only allowed to quote its verdict fields (self-check greps both) |
| 5 | Analysis-harness fix post-freeze (cleanup-compare sandbox never created ⇒ `output_preserved=None` on 17; formula mislabel) | amend1 REPORT §7 + `regrade/ANALYSIS_FIX_NOTE.md` | F3 requires 0 lost/None entries BY CONSTRUCTION (the compare harness creates its dirs first; recorded in the prereg §9) |
| 6 | Flag-material leak risk unaddressed at census level | (class the paper's LEAK_SCAN covers post-hoc) | **Flag-material pre-gate** in the census: every offline candidate scanned for pinned-flag bytes in handout files/description — all 16 CLEAN; hits elsewhere recorded (`slurp.py`, `Katy/release`, both non-candidates) |
| 7 | One-sided provider-failure rule (a task-side framing of infra failures) | paper §7's own requirement list ('two-sided provider-failure rule') | Registered two-sided rule (prereg §8): infrastructure failures re-attempt ≤2, never consume a task-side terminal state |
| 8 | No power statement tying quorum → decision | paper §7's own requirement list | Registered power statement (prereg §10): N≥6, n=4/cell, threshold ⌈N/2⌉, sign-test floor stated (you cannot claim significance at n=4/cell — falsifier-verdict product only) |

## What has already been produced here

- `census_nyu/` — census of the pinned NYU CTF Bench archive under the frozen
  Phase-2 rule. **Complete accounting: 75 rows** = 63 manifest members
  (development 11 + test 52, manifest reconciliation 0 diff BOTH sides) +
  10 explicit BENCHMARK_REMOVED + 1 DANGLING_ARCHIVE_ENTRY (broken symlink
  inside the release) + 1 EXCLUDED_BY_CRITERION_1 (metadata `warm-up`).
  **16 OFFLINE_CANDIDATE** tasks clear criteria 1–4 (incl. `CSAWpad`, which
  entered on the repaired listen statement filter — its README prose "listen
  to the William Tell Overture" was a false positive of the first filter
  version; the repaired filter requires host:port or socat/xinetd), all
  declared files present, all flag-material CLEAN.
- `census_nyu/reference_solvers/` — **criterion-5 verification EXECUTED**
  (offline, $0, zero model calls): 8 stdlib-only solvers, a reproducible
  runner, and a pure-Python DES implementation (50/50 cross-checked against
  pycryptodome, test-only). **7 tasks qualified** (quorum 6 MET):
  `almost_xor`, `another_xor`, `babycrypto`, `lowe`, `Crack-Me`, `eps`,
  `eps_part2` — each reproduces the pinned flag byte-exactly, is QUALIFIED
  under the declared arm, carries no pinned-answer bytes, and fits the
  1600-token program budget (largest 4036 chars / ≤1009 est. tokens).
  `DES 2 Bites` also verifies but is budget-excluded (8191 chars, ≈2047+
  est. tokens). `collusion` and `stfu` fail criterion 5 (not recoverable from
  the declared artifacts / visual rendering); 6 candidates were not reached
  once the quorum was exceeded. Full record:
  `census_nyu/criterion5_outcomes.json` + `CRITERION5_VERIFICATION.md`.
- `compat_gate/gate_run_log.json` — demonstration on the 8 amendment-1 frozen
  prompts: hashes re-verified, representation name-invariance asserted,
  artifacts materialized, un-repaired arms 0/8 vs repaired arms 8/8.
- `fixtures/` — **7 tasks, 14 prompts** built from the criterion-5-eligible
  set (statement = `challenge.json` description only; declared artifacts at
  their basenames, materialized flat). **Decode-equality gate: PASS 7/7**
  (`fixtures/decode_equality_log.json`).
- `compat_gate/gate_run_amend3.json` — **freeze check on the NEW prompts:
  PASS**, 14/14 under both registered arms (declared v4 + stress-repaired),
  exit 0. The gate that would have stopped amendment 1 is now green *before*
  the freeze.
- `seed_sweep/SEED_SWEEP.json` — the draft's seed range 101–104 was found
  **spent** (info_contract_powered results use them; the P010 family lists
  101–118), so the registered range is **417–420**, verified free at field
  level.
- `regrade_amend3_contrast.py` — the per-label F1/F2/F3 machinery. Validated
  offline: exact reproduction of all four amended-2 per-task contrasts
  (single label) and the F1 FALSE verdict; synthetic 3-label fixture exercises
  2/3 labels TRUE ⇒ replicable, 1/3 ⇒ not replicable, and the F3 failure
  branch (exit 3, `ANALYSIS_DEFECT_DO_NOT_PUBLISH`).
- `oracle/answers.json` — oracle truth material for the 7 answers (never
  prompt or transcript content), built from the verified reference-solve log.
- `policies_amend3_draft/` — declared v4, stress-repaired, and cleanup
  modules, all verbatim copies with `diff` verification.
- `apinex_client.py` + `HEALTH_ROUTE_PROBE.json` — **pre-freeze route
  substitution**: the earlier single-route plan (`claude-sonnet-4-6-free` via
  APMIX) was unavailable (APMIX 404; agentrouter keys 401), and the APINEX
  OpenAI-compatible free route passed a 4-model, 16-token probe (all 200,
  `cost_tokens` 0). The registered design is 3 labels on that one route.
- `FREEZE.json` — the freeze manifest (64 files hashed), status
  `FROZEN — awaiting namespace-restricted commit`; the commit registers it.
- `PREREGISTRATION_AMEND3_DRAFT.md` — the complete preregistration draft
  (explicitly: not frozen, registers nothing until the freeze commit).

## What remains before freeze (execution order)

1. **Criterion-5 verification — DONE** (7 eligible, quorum MET).
2. **Fixtures + prompts + decode gate — DONE** (7 tasks, 14 prompts, PASS).
3. **Compat pre-gate on the NEW prompts — DONE** (PASS under both registered
   arms).
4. **Seed sweep — DONE** (101–104 rejected; 417–420 free).
5. **Harness + freeze bundle — DONE (pending commit).** `run_amend3_sessions.py`
   (168 slots across the 3 registered labels, two-sided provider rule, live
   mode refuses without the commit marker) + `smoke_amend3.py` written;
   `FREEZE.json` hashes the whole bundle; smoke PASS; dry-run reports 168
   sessions. Only the namespace-restricted freeze commit + `FREEZE_COMMIT.txt`
   record remain.
6. Grid (3 labels × 7 tasks × 8 = 168 sessions), triple regrade, per-label
   contrast script, REPORT with verdicts quoted only from the frozen JSON;
   then the paper's §7 + Appendix D.3 integration through the registered lock
   discipline.

## Expected outcomes (both honest, both stronger than today)

- **Per-label F1 TRUE** (movement defined and outside ±10 pp on ≥4 of 7
  tasks for a label): the paper's headline mechanism gains external
  instantiations at registered strength; **≥2/3 labels** makes the panel
  reading *replicable across labels* — the review panel's P0, now answered
  across model families rather than one route.
- **F1 FALSE / F2 null** with all denominators defined: the portability
  section now reports a *measured non-effect on independent tasks with a
  consistent interface*, no longer a structural degeneracy — the referee's
  strongest available objection ("degenerate, untestable") is closed either
  way.
- Either way the census upgrade (pool expansion on a second benchmark,
  manifest-reconciled 0-diff) lands in Appendix D as the third recorded
  census alongside the two NO_GO stops.

## Boundary statement

This workspace produces planning-class artifacts. The pinned archives are
never modified; extractions are read-only into `/tmp/opencode/`; no frozen
artifact anywhere in the project was touched; nothing here claims frozen
status (headers say DRAFT/NOT YET FROZEN explicitly); no model content was
generated; no git commit was made; no native-benchmark-defect claim exists in
any artifact.
