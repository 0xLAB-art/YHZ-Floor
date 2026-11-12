# PREREGISTRATION — Amendment 4: frontier-label external admission panel

**Protocol:** PHASE2-EXTERNAL-ADMISSION-AMEND4-FRONTIER-v1 · **Namespace:** `sp2027/research_execution/external_admission_amend4_frontier_20261106` · **Registered:** 2026-11-06, before the first experiment model call.

## 1. Question

The registered Amendment-3 record (168 sessions, three labels, 282 programs) left the portability question unanswered for a capability reason: no program was oracle-correct under the registered whole-stdout rule, so the per-task representation contrast had nothing to move (F1 FALSE on all three labels; 0 movers). Amendment 4 repeats the **identical frozen protocol** on **frontier labels from the paper's own registered label list** to give the registered bar (movement on 4 of 7 tasks) its first full test. The Amendment-3 record stands unchanged; this is a new, separately registered panel — never pooled with Amendment-3 or any other cohort.

## 2. Design (frozen constants)

- **Grid:** 3 labels × 7 criterion-5 tasks × {R0, RT} × seeds [421, 422, 423, 424] = **168 sessions**, n=4 per (label, task, representation) cell. Seeds label the session only (no per-seed randomness — Amend-3 convention); sweep receipt: `seed_sweep_SEED_SWEEP.json` (range free).
- **Labels:** `gpt-5.6-sol`, `gpt-6-astra`, `gpt-6.1-sol` — the paper's registered GPT-family labels (Sections 4–7 list). Route: the operator's existing gateway, Anthropic-messages transport (`/v1/messages`, `claude-cli` User-Agent per the frozen adapters), provider-attested at call time, never digest-pinned.
- **Tasks/artifacts/prompts:** the 7 criterion-5 tasks, the 10 declared handout artifacts, and the 14 frozen (task, representation) prompt files are **byte-identical copies** of the Amendment-3 frozen inputs (hash-asserted at runtime against `PROMPT_HASHES.json`). Prompt text per (task, representation) is identical across seeds and labels.
- **Turns:** ≤2, feedback string verbatim (`EXECUTION_OR_ORACLE_REJECTED: …`), temperature 0.2, `python -I prog` sandbox execution with the declared artifacts only, 30 s exec timeout — all verbatim from Amendment-3.
- **Token floor:** `max_tokens = 4200` per call, **uniform across labels, tasks, representations, and turns** (the P017-registered floor: 1.5× the maximum observed completion of the reasoning-family label; raised from Amendment-3's 1600 because the 4200 floor is the registered value for this label family). Floor-exhausted completions are a measured outcome (EMPTY_RESPONSE taxonomy), never imputed.

## 3. Oracle — two admissible codings, registered before the first call

For every executed program, both codings are computed and recorded per turn:

- **C1 (registered primary, unchanged from Amendment 3):** `stage == output AND returncode == 0 AND stdout.strip() == pinned answer` — the entire stripped stdout must equal the pinned token.
- **C2 (registered second admissible normalization):** the first flag-shaped token extracted from stdout by `flag\{[ -~]*?\}` equals the pinned answer, with `returncode == 0` and `stage == output`.

Acceptance (`SUCCESS`, the registered estimand) is **C1 acceptance**; C2 is reported side by side per the both-codings discipline (P024b precedent: both admissible codings computed and printed, so no coding can be chosen by narrative after the fact). **Both codings are declared here, before any outcome exists.** The per-task representation contrast, its movement (stress minus declared), and the falsifiers are computed **under each coding separately**; both verdicts are the product. The two codings' disagreement is itself a registered measurement of the answer-normalization owner.

## 4. Status taxonomy — CRASH class added

Terminal states: SUCCESS, **CRASH** (new: the final submitted program ran and exited non-zero — `returncode ∉ {0, None}` on the last submitted turn), ORACLE_FAIL (final submitted program ran clean, rc=0, and failed both codings), TIMEOUT, AGENT_GIVEUP, MODEL_REFUSAL, TOOL_FAILURE, PROVIDER_UNAVAILABLE, HARNESS_ERROR. Amendment-3's finding (120 of 145 ORACLE_FAIL sessions had ≥1 crash; 103 terminal crashes hidden by the missing class) motivates this class; it is registered up front, not post-hoc.

## 5. Admission rules and regrade

The three frozen admission arms of Amendment-3 apply unchanged to the retained programs: declared v4 (policy v3), stress-repaired, and cleanup; qualification and output preservation are recomputed by the same regrade scripts on this namespace's frozen programs. Per-task movement = stress contrast − declared contrast, computed **under C1 and under C2 separately**; undefined (no denominator in at least one representation) is never counted as zero.

## 6. Registered falsifiers (per coding)

- **F1 (mechanism ports):** movement outside the ±10 pp margin on **≥4 of 7 tasks** on at least one label? (Amendment-3 registered bar.)
- **F2 (honest null band):** every defined contrast within the margin.
- **F3 (preservation):** cleanup preserves byte-identical stdout on all edited programs.
- **Cross-label rule:** F1 TRUE on ≥2 of 3 labels (with F3 PASSED).

## 7. Operational rules (frozen)

- **Halt rule:** ≥3 consecutive provider-side pre-output failures ⇒ status halted; resume windows recorded in `RESUME_RECORD.md` (Amendment-3 precedent: 3 halts/resumes). Auth/billing errors are HARNESS_ERROR and halt the phase.
- **Transient provider failures:** up to 2 re-attempts per failed call, all attempts ledgered; excluded from acceptance denominators exactly when no model content was produced (two-sided rule, verbatim from Amendment-3).
- **Label substitution order (registered up front):** if a label exhausts quota or sustains sustained rate limiting, its remaining slots re-run on the first label in the registered order [`gpt-6.1-sol`, `gpt-5.6-sol`, `gpt-6-astra`] not itself exhausted or already substituted; per-label group splits are always reported and never pooled; the substitution and its boundary row are recorded in `RECOVERY_LABEL_SUBSTITUTION.md`.
- **Cost ceiling:** the phase ceiling is **2,500,000 output tokens** (enforced live — the runner halts at the ceiling; token counts are the measurement-relevant quantity per Section 11's cost disclosure) with a soft checkpoint at 2,000,000; USD is reconciled at settlement from the gateway's invoicing and recorded in the ledger. At the campaign's observed rates for this label family this sits well below the largest completed single wave.
- **Fingerprint audit:** post-run, every raw provider response is checked for the attested label echo; a drifting cohort is withdrawn to same-label with its numbers retained as same-label evidence (P010X1 discipline).
- **Non-evidence probes:** one AUTH_SMOKE per label before the run (`HEALTH.json`, evidence=false).

## 8. What would count against the thesis

Nothing in this panel grades the agents. A positive result (movement under either coding) instantiates the admission owner on external tasks; a null under both codings with correct programs present would mean the external correct programs are rule-invariant (the Amendment-2 Cybench finding), which is itself a measured owner boundary. Every outcome is a measurement; none is a benchmark-quality claim.

## 9. Frozen-input integrity

`FREEZE.json` lists SHA-256 for: this preregistration, the runner, the client, the 14 prompt files, the 10 artifacts, `oracle/answers.json`, `census_nyu/criterion5_outcomes.json`, `seed_sweep_SEED_SWEEP.json`, and `PROMPT_HASHES.json`. The namespace-restricted freeze commit is the registration act; live mode refuses to run until `FREEZE_COMMIT.txt` exists. The API key is read from the process environment, never printed, never written to any artifact.


## 10. Pre-first-call amendment 1 (2026-11-06, before any evidence call): per-label temperature

The AUTH_SMOKE (non-evidence, HEALTH.json) exposed a route constraint: the
gpt-6.1-sol route rejects an explicit temperature of 0.2 (HTTP 400: only its
default, 1.0, is supported). Registered resolution: the panel runs per-label
temperature — 0.2 for gpt-5.6-sol and gpt-6-astra (the registered design
value), and the gpt-6.1-sol route default (temperature field omitted) for
gpt-6.1-sol. This is a transport constraint of the attested route, recorded
here and in FREEZE.json (design.temperature_by_label) before any evidence
call; no task-prompt call was made before this amendment. The token floor
(4200) and every other constant are unchanged.


## 11. Pre-first-call amendment 2 (2026-11-06, before any evidence call): route-default temperature on all labels

Amendment 1 scoped the 0.2 temperature to two labels after the gpt-6.1-sol
route rejected it. The re-smoke then showed the same rejection on
gpt-6-astra (intermittently per backend shard; the first probe had passed).
Registered resolution: the temperature field is OMITTED for every label —
the route default (1.0) applies UNIFORMLY across all labels, tasks,
representations, and turns. The 0.2 design value is unenforceable on this
transport; uniformity preserves the design's no-differential-treatment
property. Token floor and all other constants unchanged.
