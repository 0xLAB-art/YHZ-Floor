# Remaining Experiments Plan — 2026-10-23

Status: APPROVED PLAN. Phases 1–3 are runnable experiments; Phase 4 is paper
integration. Each phase below carries a self-contained subagent prompt at the
end. Launch phases in order 0→4; Phases 1, 2 and 3 touch disjoint namespaces
and may run in parallel if separate sessions are available.

## Global constraints (bind every phase)

- Provider: `claude-sonnet-4-6-free` via `https://api.apmix.ai/v1`
  (Anthropic-compatible messages endpoint), configured in root `.env` as
  `APMIX_BASE_URL`, `APMIX_API_KEY`, `APMIX_MODEL`. Provider-attested label
  only; never claim hosted-weight identity.
- Auth/connectivity probes are `AUTH_SMOKE` non-evidence and must be logged
  separately from experiment sessions (protocol of the 2026-10-18 NO-GO
  pilot: every 401 before model output invalidated that campaign — health
  must be verified BEFORE session creation, and a session that fails
  provider-side before any model content is `PROVIDER_UNAVAILABLE`, never a
  task failure, never retried unless the phase prereg says so).
- Preregistration file (`PREREGISTRATION.md` + freeze JSON with SHA-256 of
  every prompt/fixture/policy file) is written and hashed BEFORE the first
  model call of that phase. Commit the prereg before outcomes exist.
- New namespace directories only. Never modify frozen records, H1-R3
  artifacts, P010, or any historical cohort. Append-only ledgers.
- Terminal states restricted to the project enum: SUCCESS · ORACLE_FAIL ·
  TIMEOUT · AGENT_GIVEUP · MODEL_REFUSAL · TOOL_FAILURE ·
  PROVIDER_UNAVAILABLE · HARNESS_ERROR.
- Budget: append every call's token usage and estimated cost to
  `sp2027/research_execution/BUDGET_LEDGER.jsonl`. Project guardrails stay in
  force ($50 alert / $200 hard stop). Estimated total for Phases 1–3 at the
  free route: under $2 (P010 precedent: 16 sessions ≈ $0.08).
- Honest nulls are first-class results. No retries, no seed replacement, no
  arm expansion without a new prereg amendment recorded before execution.
- Every phase ends with: `REPORT.md` + `results.jsonl`/`summary.json` +
  `PROMPT_HASHES.json` + ledger entries + a git commit.

---

## Phase 0 — Safety baseline (offline + 1 smoke call) — PARTIALLY DONE

Done on 2026-10-23 (this session): API key stored in root `.env`
(gitignored, verified); `/v1/models` probe OK (model listed, plan=free);
`/v1/messages` 16-token smoke OK (`AUTH_SMOKE` msg_6fe60bf37dd380a3cfefadba).

Remaining:
1. Record the smoke evidence: create
   `sp2027/research_execution/provider_health_20261023/HEALTH.json` with the
   two probe responses, timestamped, labeled `AUTH_SMOKE, non-evidence`.
2. Baseline commit: `git checkout -b paper-upgrade-evidence` in the OUTER
   repo; `git add` the uncommitted upgrade material —
   `sp2027/research_execution/info_contract_2x2_20261018/`,
   `sp2027/analysis/policy_mechanism_20261021/`,
   `sp2027/analysis/contribution_audit_20261021/`,
   `sp2027/analysis/external_validation_20261021/`,
   `sp2027/analysis/final_deliverables_20261018/` — plus this plan file.
   Commit message: `baseline: preserve uncommitted upgrade evidence + remaining-experiments plan`.
   Do NOT commit `.env`, secrets, or the inner ACTS-ATTACK untracked dirs in
   this commit.
3. Inner repo: leave `ACTS-ATTACK/` untouched this phase (its untracked
   files are harness code; a separate commit there is optional later).

Acceptance: HEALTH.json exists; branch `paper-upgrade-evidence` exists with
the named paths committed; `git status` for those paths is clean.

---

## Phase 1 — H2: CBC agency/delegation intervention (model calls)

Objective: execute the already-preregistered hypothesis H2 from
`sp2027/analysis/checkpoint007_active_experiments/01_PREREGISTERED_HYPOTHESES.md`
— for the same CBC padding-oracle contract, does an interactive agent
(generation + revision with local tool feedback) differ from a one-shot
model-written solver executed by the harness, in acceptance, revisions,
logical errors and cost?

Key inputs (read-only):
- Preregistered hypotheses: `sp2027/analysis/checkpoint007_active_experiments/01_PREREGISTERED_HYPOTHESES.md` (H2 section)
- Fixture semantics: `sp2027/research_execution/info_contract_2x2_20261018/` runner architecture (P009/P010 harness pattern: freeze → preflight deterministic gate → sessions → leak scan → report)
- CBC budget-qualified control facts: 15-byte plaintext + PKCS#7 recovered at 2,021 oracle queries under a 4,096-query budget; 400-query budget fails (recorded in paper §budget and budget control namespace)
- Harness/runner reference: `sp2027/research_execution/run_info_contract_2x2_chacha20.py` (reuse its provider client, freezing, hashing, event logging; change fixture to CBC)

Design to freeze (write as `PREREGISTRATION.md` before any call):
- Namespace: `sp2027/research_execution/h2_cbc_agency_20261023/`
- Fixture: CBC padding oracle, 15-byte plaintext + PKCS#7, per-session fresh
  key/IV, oracle budget 4,096 queries, exact-match predicate on plaintext hex.
- Arms (only the arm axis differs; prompts, seeds, budget, parser, oracle identical):
  - `A_INTERACTIVE`: agent loop, ≤2 turns, rejection feedback string after turn 1
  - `B_ONESHOT`: single model call must emit a complete solver program; harness executes it once; no feedback turn
- Grid: 2 arms × 4 seeds (use seeds 61,62,63,64 — unused by prior cohorts) = 8 sessions.
- Deterministic gate (before sessions): local solver recovers plaintext ≤4,096 queries on all 4 seeds; wrong candidate rejected; gate output hashed into freeze.
- Measurements: acceptance, submissions, turns, oracle queries used, per-rejected-program error class (syntax / padding-logic / block-off-by-one / encoding / other), tokens, cost.
- Falsifiers (prespecify): F1 `A acceptance > B acceptance` (supports H2a);
  F2 `acceptance equal and revision counts equal` (null — both loci equivalent here);
  F3 any arm's accepted program uses > 4,096 queries (gate/budget defect → invalidate arm, investigate).
- Analysis: descriptive per-cell table; Fisher exact on 4v4 acceptance; NO pooled capability rate; no causal language beyond the arm axis.

Deliverables: namespace dir with PREREGISTRATION.md, FREEZE.json, PROMPT_HASHES.json,
preflight/, sessions/ (raw responses, events, candidates), results.jsonl,
summary.json, LEAK_SCAN.json, REPORT.md, BUDGET_LEDGER entries, git commit
before analysis if possible (commit freeze first, outcomes second).

Acceptance: 8/8 sessions terminal-state recorded (any PROVIDER_UNAVAILABLE
retained, not retried); deterministic gate log present; REPORT.md answers H2
with the falsifier verdicts; ledger updated.

SUBAGENT PROMPT (Phase 1):
> You are executing Phase 1 of /mnt/nvme5/ACTS-Attack/sp2027/research_execution/REMAINING_EXPERIMENTS_PLAN_20261023.md. Read that file fully first, then read the H2 section of sp2027/analysis/checkpoint007_active_experiments/01_PREREGISTERED_HYPOTHESES.md and the runner sp2027/research_execution/run_info_contract_2x2_chacha20.py. Load provider config from /mnt/nvme5/ACTS-Attack/.env (APMIX_*). Steps: (1) verify provider health with a 16-token AUTH_SMOKE probe logged to provider_health under the new namespace; (2) write sp2027/research_execution/h2_cbc_agency_20261023/PREREGISTRATION.md + FREEZE.json exactly per the phase spec (CBC fixture, arms A_INTERACTIVE/B_ONESHOT, seeds 61–64, ≤2 turns, 4,096-query budget) and hash every prompt/fixture; commit the freeze before any experiment call; (3) run the deterministic gate (local CBC solver ≤4,096 queries on all seeds, wrong-candidate rejection) and freeze its output; abort NO-GO if it fails; (4) execute the 8 sessions with the project terminal-state enum, retaining every failure; (5) classify rejected programs; (6) write results.jsonl, summary.json, LEAK_SCAN.json (no truth material in prompts/transcripts beyond expected recovered output), REPORT.md with falsifier verdicts F1–F3; (7) append costs to BUDGET_LEDGER.jsonl; (8) git commit outcomes. Never modify frozen records or other cohorts. Report honestly if the result is null.

---

## Phase 2 — External-task admission portability (model calls + offline regrade)

Objective: reproduce the admission-mechanism result (representation contrast
moved by an admission-rule change on fixed programs, plus cleanup control) on
independently authored tasks — the Cybench crypto subset — under our
evaluator. This is a portability + evaluator-sensitivity study per
`sp2027/analysis/external_validation_20261021/RESEARCH_PLAN.md` evidence
levels 1–2. It must NOT be described as a native Cybench defect (preflight
found no import gate there; the restrictive rule is OUR stress-test rule,
provenance-justified from the H1-R3 legacy filter).

Key inputs (read-only):
- `sp2027/analysis/external_validation_20261021/RESEARCH_PLAN.md` + `SOURCE_PREFLIGHT_V2.json` (pinned archives, hashes)
- Cybench pinned archive location recorded in the preflight (7,460 files; select only `tasks/` crypto entries)
- Legacy-filter semantics + cleanup transform: `sp2027/analysis/policy_mechanism_20261021/` and H1-R3 admission machinery in `sp2027/paper/anonymous_reviewer_artifact_v23/h1r3_check.py` context
- Runner pattern: `run_info_contract_2x2_chacha20.py`

Design to freeze:
- Namespace: `sp2027/research_execution/external_admission_20261024/`
- Task selection rule (before outcome inspection): from the pinned Cybench
  `tasks/` tree keep crypto tasks whose answer is a deterministic checkable
  value (flag/secret string) runnable offline in the harness; require the
  task statement public and no external service. Target 6 tasks; record every
  exclusion with reason. Freeze task IDs + source file SHA-256.
- Representations (information-preserving, verified by decode-equality check
  before generation): R0 canonical task statement as-is; RT transform any
  provided encoded artifacts to base64 (or the statement's natural secondary
  encoding) with an explicit decode note. Decode-equality is a hard gate.
- Grid: 6 tasks × {R0, RT} × 2 seeds = 24 sessions; ≤2 turns; rejection
  feedback identical across arms; fixed token budget.
- Regrade (offline, on retained programs): (a) declared permissive rule;
  (b) H1-R3-style narrower import filter (labeled counterfactual stress
  rule); (c) rule (b) + output-preserving unused-import cleanup. Record
  per-arm rejections, corrected-outputs check (byte-identical), and the
  contrast movement per task; weight tasks equally in the primary contrast.
- Falsifiers: F1 movement under (b) outside [-10,+10] pp on ≥ half the tasks
  (mechanism ports); F2 movement within margin on most tasks (mechanism is
  fixture-specific — honest null); F3 cleanup fails to preserve output on any
  program (analysis defect → investigate, do not publish contrast).
- Analysis: per-task table + equal-weight paired contrast + sign test across
  tasks; NO benchmark-quality claim; NO pooling with H1-R3 numbers.

Deliverables: namespace with PREREGISTRATION.md, TASK_SELECTION.md (with
exclusions), FREEZE.json, decode-equality logs, sessions/, regrade/
(programs, policy snapshots, verdicts), results.jsonl, REPORT.md, ledger,
commits (freeze → outcomes).

Acceptance: ≥6 tasks frozen or honest early stop documented; decode-equality
gate passed before generation; 24 sessions terminal; regrade triple recorded;
REPORT.md states the portability boundary explicitly.

SUBAGENT PROMPT (Phase 2):
> You are executing Phase 2 of /mnt/nvme5/ACTS-Attack/sp2027/research_execution/REMAINING_EXPERIMENTS_PLAN_20261023.md. Read that file fully, then sp2027/analysis/external_validation_20261021/RESEARCH_PLAN.md and SOURCE_PREFLIGHT_V2.json. Load provider config from .env (APMIX_*). Follow the phase spec exactly: task selection from the pinned Cybench archive (crypto subset, deterministic checkable answers, record exclusions), freeze task IDs + SHA-256, verify decode-equality of R0/RT before any generation, run 6×2×2=24 sessions (seeds 71–74, ≤2 turns), then the offline triple regrade (declared rule / narrower stress rule / +cleanup) on the retained programs with output-preservation checks. All conclusions must be labeled portability + evaluator sensitivity under OUR stress rule — never a native benchmark defect claim. Write REPORT.md with falsifier verdicts F1–F3, update BUDGET_LEDGER.jsonl, commit freeze before outcomes. If <6 tasks qualify, stop honestly and document.

---

## Phase 3 — 2×2 premise-study extension to RC4 (model calls, cheapest)

Objective: test whether the P010 finding (zero-reference premise is
load-bearing; naming is not; named-but-unstated is worst) generalizes beyond
ChaCha20, by replicating the exact 2×2 on the RC4 keystream-reuse fixture
with an unstated-content reference ciphertext.

Key inputs (read-only):
- `sp2027/research_execution/info_contract_2x2_20261018/` (P010 protocol, REPORT.md, PREREGISTRATION.md — copy its structure, do not modify)
- RC4 fixture semantics from the explicit-observation cohorts (known-plaintext + ciphertext + target)

Design to freeze:
- Namespace: `sp2027/research_execution/info_contract_2x2_rc4_20261024/`
- Fixture: RC4 keystream reuse; `c_ref = RC4(k, nonce, REFERENCE)` where
  REFERENCE is a fixed 32-byte constant; public JSON gives algorithm,
  keystream-reuse flag, c_target, c_ref, protected_length,
  claim_field. Predicate: exact match of target plaintext hex.
- Cells (only A/B slots differ, mirrors P010):
  C1 A+ (named RC4 keystream-reuse instance) B+ (statement says c_ref encrypts the fixed reference value);
  C2 A− B+; C3 A− B+ combined as in P010 — keep P010's exact cell matrix:
  C1(A+B+), C2(A−B− with derive-frame), C3(A−B+), C4(A+B− "encrypts a 32-byte reference", content unstated).
- Seeds 81–84 (fresh, unused); Latin-square rotation as in P010; 16 sessions,
  ≤2 turns, ≤32 calls; identical everything else.
- Preflight: local solver succeeds via reference on all seeds; without the
  reference value the instance is underdetermined for exact-match (retain
  ambiguity witness); cell-text audit: only A/B slots differ.
- Falsifiers mirrored: F1 C4 ≈ C1 (premise not load-bearing here — honest
  null); F2 C3 fails while C1 succeeds; F3 C2 succeeds.
- Analysis: same descriptive marginals + Fisher exacts as P010; no alpha
  claim; no pooling with P010 (report side by side).

Deliverables: namespace with prereg/freeze, preflight, sessions, LEAK_SCAN,
results, REPORT.md, ledger, commits.

Acceptance: 16/16 sessions terminal; cell-text audit passed; falsifier
verdicts stated; comparison table vs P010 in REPORT.md.

SUBAGENT PROMPT (Phase 3):
> You are executing Phase 3 of /mnt/nvme5/ACTS-Attack/sp2027/research_execution/REMAINING_EXPERIMENTS_PLAN_20261023.md. Read that file, then mirror the protocol of sp2027/research_execution/info_contract_2x2_20261018/ (P010) exactly onto the RC4 fixture per the phase spec: 2×2 cells C1–C4, seeds 81–84, Latin square, ≤2 turns, ≤32 calls, deterministic preflight incl. underdetermination witness for the withheld-premise world, cell-text audit. Load provider config from .env (APMIX_*). Write PREREGISTRATION.md + FREEZE.json first and commit; run 16 sessions with full terminal-state retention; LEAK_SCAN; REPORT.md with F1–F3 verdicts and a side-by-side comparison against P010 (no pooling). Update BUDGET_LEDGER.jsonl; commit outcomes.

---

## Phase 4 — Paper integration + verification (offline; requires Phases 0–3 outputs)

1. Integrate the ALREADY-COMPLETED P010 2×2 (independent of Phases 1–3):
   replace/extend the Reduced-Information subsection in
   `sp2027/paper/capability_revision_20261020/arxiv_version_evidence_revision_20261022/main_sections/04_capability.tex`
   with the P010 factorial (keep blind-opportunity as out-of-design
   corroboration), citing `final_deliverables_20261018/SCIENTIFIC_RESULTS_REPORT_20261018.md §3` numbers.
2. Add the runtime-tracing mechanism sentence (100/101 genuine loads, from
   `policy_mechanism_20261021/DERIVED.json`) to the admission subsection §4.2.
3. Sharpen intro/discussion with the CENTRAL_CLAIM boundary framing
   (`contribution_audit_20261021/CENTRAL_CLAIM.md`): what we own vs ABC/AgentSuite.
4. If Phase 1/2/3 completed with usable results: add their subsections
   (H2 agency; external admission portability — with its honest boundary;
   premise-extension) and update the external-coverage table row for Admission.
5. Extend `verify_evidence_revision.py` with checks for every number added;
   extend the Number Lock (`results_lock.py` → RESULTS_LOCK.json) for new
   claims; rebuild all PDFs; confirm 13+5 page budget; refresh
   ARTIFACT_ACCESS_SCOPE and REVISION_NOTES.
6. Update the supplement if any promoted table displaces content.

Acceptance: 48/48+ checks pass; page counts 13/5; Number Lock covers every
new quantitative claim; no frozen cohort numbers modified.

SUBAGENT PROMPT (Phase 4):
> You are executing Phase 4 of /mnt/nvme5/ACTS-Attack/sp2027/research_execution/REMAINING_EXPERIMENTS_PLAN_20261023.md. Read it fully plus REVISION_NOTES_20261022.md and verify_evidence_revision.py in the paper directory. Perform integration steps 1–6 exactly, changing no frozen numbers, keeping the 13+5 page budget, extending the verify script and Number Lock for every added number, rebuilding the arxiv/anonymous/supplement PDFs, and writing a new REVISION_NOTES dated today summarizing changes with page references.

---

## Sequencing and parallelism

- Phase 0 must complete first (health + baseline commit).
- Phases 1, 2, 3 are mutually independent (disjoint namespaces, disjoint
  seed ranges 61–64 / 71–74 / 81–84) and can run as parallel subagents or
  sequentially in one session.
- Phase 4 runs last; steps 1–3 (P010 2×2, runtime tracing, CENTRAL_CLAIM)
  are executable even if Phases 1–3 are not run — they need no new results.
- Stop conditions: provider outage (retain PROVIDER_UNAVAILABLE records,
  halt phase, report); deterministic gate failure (NO-GO, document);
  budget alert ($50) → pause and escalate to the author.
