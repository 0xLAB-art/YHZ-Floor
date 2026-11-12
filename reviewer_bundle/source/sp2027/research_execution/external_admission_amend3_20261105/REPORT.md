# REPORT — Amendment 3: expanded external-task admission portability grid

**Namespace:** `sp2027/research_execution/external_admission_amend3_20261105`
**Protocol:** PHASE2-EXTERNAL-ADMISSION-AMEND3-v1 · **Date:** 2026-11-05
**Status: COMPLETED — 168/168 terminal; F1 FALSE on all three labels · F2 TRUE · F3 PASSED_preservation · cross-label not replicable**

## 1. Headline

The registered three-label panel ran to completion: **168/168** sessions
terminal (4 execution windows; 3 provider-rate-limit halts and resumes), with
**156** sessions producing model content and **12** slots excluded as
`provider_no_content` under the pre-registered two-sided rule. The run retained
**282 programs**. **None is oracle-correct** (0/282). The declared v4 arm
qualifies **261/282** programs (92.6%), the stress-repaired arm **149/282**
(52.8%), and the cleanup arm **194/282** (68.8%) — the interface that made
Amendment 1 degenerate (0/37 admissible) is **no longer the blocker**.

The registered per-label F1 is nevertheless **FALSE on all three labels**:
on every task where the stress arm has a denominator the representation
contrast is exactly **0** (there are no oracle-correct programs to move it),
and on the remaining tasks the stress arm qualifies no program, so the
contrast is **undefined** (never counted as zero). F2 is **TRUE** (honest null
band), F3 is **PASSED_PRESERVATION** (282/282 byte-identical outputs), and the
cross-label rule (≥2 of 3 labels with F1 TRUE) is **not met**.

This is a **measured, non-degenerate null**: the external interface is
testable, but this model family does not solve the external tasks, so the
registered portability contrast cannot move. It is not a benchmark-quality
claim and not a structural-degeneracy repeat.

## 2. Gates

| Gate | Result |
|---|---|
| Program hashes vs `results.jsonl` | **282/282** |
| Registry attribution (three labels, 168-slot plan) | **PASS** |
| F3 cleanup output preservation | **282/282 True** |
| Provider-failure two-sided rule | 12 slots excluded with `produced_model_content=false`; all attempts ledgered |
| Accounting cost | **$0.00** (APINEX free tier; `cost_tokens=0` in every usage record) |

## 3. Per-label verdicts (from `regrade_contrast_amend3.json`)

| Label | Sessions | Content | Programs | Correct | Declared q. | Stress q. | Cleanup q. | F1 | F2 | F3 | Defined / moved / undefined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `free/gpt-6-luna` | 56 | 53 | 92 | 0 | 86 | 51 | 65 | **FALSE** | TRUE | PASSED | 4 / 0 / 3 |
| `free/qwen-3.8-max` | 56 | 51 | 94 | 0 | 87 | 54 | 67 | **FALSE** | TRUE | PASSED | 5 / 0 / 2 |
| `free/deepseek-v4.1-flash` | 56 | 52 | 96 | 0 | 88 | 44 | 62 | **FALSE** | TRUE | PASSED | 4 / 0 / 3 |

Cross-label: `f1_true = []`; `replicable_across_labels = false`
(rule: ≥2 of 3 labels with F1 TRUE and F3 PASSED; no pooling).

Undefined tasks (stress arm qualifies no program in at least one
representation; undefined ≠ zero):

- **gpt-6-luna:** eps, lowe, crack_me.
- **qwen-3.8-max:** lowe, crack_me.
- **deepseek-v4.1-flash:** another_xor, lowe, crack_me.

On every defined task the movement is **0.00 pp**; there are no movers.

## 4. Admission reading

- **Declared v4 (policy `v3`):** 261/282 programs qualified (92.6%).
- **Stress-repaired (policy `legacy`):** 149/282 qualified (52.8%); the stress
  arm rejects **112 of the 261 declared-qualified programs** (42.9%). This is
  the import-axis narrowness the external phases were built to measure.
- **Cleanup arm:** 194/282 qualified; 282/282 output-preserved.
- **Oracle-correct programs:** **0**; therefore `recall_of_correct` is
  undefined (0/0), not zero. The informative admission numbers here are the
  qualification counts and the stress discard count, not a recall.

## 5. Falsifiers (registered; quoted from the frozen JSON)

- **F1:** FALSE on all three labels (0 movers; threshold M=4 of 7; movement
  defined on 4/4/5 tasks per label).
- **F2:** TRUE on all three labels (honest null band).
- **F3:** PASSED_PRESERVATION on all three labels (282/282).
- **Cross-label:** not replicable (0/3 labels with F1 TRUE).

## 6. Execution windows and exclusions

The grid ran in four windows (47 + 61 + 15 + 45 sessions). Three halts were
the registered ≥3-consecutive provider-failure rule, all on **HTTP 429**
(rate limit); after each halt the provider recovered (16-token probes ok,
`cost_tokens=0`) and the run resumed under the same frozen design. The
operational record is `RESUME_RECORD.md` (commits `56474f6`, `9601b97`,
`327c624`, `d047bd0`).

The **12 excluded slots** (all `provider_no_content`, per §8):

- `free/gpt-6-luna`: lowe / RT / seeds 417, 418, 419.
- `free/qwen-3.8-max`: babycrypto / R0 / 419, 420; crack_me / R0 / 418, 419, 420.
- `free/deepseek-v4.1-flash`: eps_part2 / R0 / 417, 418, 419; lowe / RT / 419.

## 7. What the result means — and does not mean

- **The interface is non-degenerate.** 261/282 declared-qualified programs
  (versus 0/37 in Amendment 1) means the read-boundary repair and the compat
  pre-gate did their job: the admission rule is now measuring the import axis,
  not an impossible file-access clause.
- **The null is a capability floor.** The three free APINEX labels produced
  plausible but incorrect solvers; the tasks' oracle answers were not reached.
  The registered contrast therefore has no correct programs to move; F1 is
  FALSE and F2 is TRUE. The portability question remains unanswered at the
  registered bar for a model-capability reason, not a structural one.
- **No benchmark-quality claim.** The census is OUR contract applied to the
  pinned NYU snapshot; the null says nothing about the benchmark. The labels
  are provider-attested only and are never pooled.
- **No significance claim.** At N=7 and n=4 per (label, task, representation)
  cell the design remains descriptive; the F1/F2/F3 verdicts are the product.

**What a positive instantiation would require:** a model that actually solves
these external tasks (or a registered follow-up wave with an explicit
output-contract clarification on the trivial tasks, e.g. eps/eps_part2, where
gpt-6-luna decoded correctly but printed the whole text instead of the exact
answer). That is a new amendment, not a post-hoc edit of this one.

### 7a. Post-hoc decomposition audit (disclosed; verdicts unchanged)

`FINDING_NULL_DECOMPOSITION.md` / `AUDIT_NULL_DECOMPOSITION.json` (audit v3,
deterministic, frozen inputs only) decomposes the 156 content sessions
(145 recorded ORACLE_FAIL, 9 timeouts, 2 give-ups) into three measured
layers under two stated counting rules. At the terminal rule (the final
submitted program): **8 sessions' submitted output printed the correct flag**
(all eps R0, all three labels) — the task statement says "the flag is the
entire thing decrypted" while the registered oracle requires the entire
stdout to equal the flag token; under the benchmark's own flag-in-output
diagnostic (solve = the flag appears in ANY produced message —
`scripts/flag_in_output.py` in the pinned harness) **11 sessions** count
(8 terminal + 3 that solved on an earlier turn and lost it to a crashed
revision); the benchmark's primary metric, an exact-string CheckFlag tool,
has no counterpart in this harness. **103 sessions' final program crashed**
(`returncode != 0`), a class the status vocabulary lacks — 48 on the
`b64decode(...).decode()` idiom; counting every crashed program across
turns, 120 sessions crashed at least once (58 events on that idiom). The
remaining 45 terminal outcomes ended without a crash or a flag (34 clean
runs, 9 timeouts, 2 give-ups). RT delivery is verified byte-exact in 84/84
prompts (an earlier "broken delivery" suspicion was an audit-regex bug,
withdrawn). The eps R0→RT collapse (11/12 → 0/12 any-turn; 8/12 → 0/12 at
the final submission) is mechanistic: 12/12 eps-RT programs base64-decode
the working-dir file whose content is visibly plain bits — the DECODE NOTE's
framing overrode the file's self-evident content. Audit v3 also fixes the v2
per-arm aggregation bug (`if r in layer1` compared session dicts against
6-key records — always False; every arm printed solved=0/crashed=0/wrong=n,
contradicting v2's own summary). No new wave is registered; this is a
reading of existing frozen data.

## 8. Artifacts

| File | Contents |
|---|---|
| `results.jsonl` | 168 terminal session records (12 provider-excluded, 156 content) |
| `sessions/programs/` | 282 retained programs (turn 1/2) |
| `sessions/events/events_amend3.jsonl` | execution/event ledger |
| `sessions/raw_provider_responses/` | raw provider bodies |
| `HEALTH.json` | post-freeze AUTH_SMOKE, non-evidence (3/3 ok, $0) |
| `regrade_results_amend3.json` | per-program triple-arm qualification + output preservation |
| `regrade_contrast_amend3.json` | registered per-label F1/F2/F3 + cross-label verdicts |
| `RESUME_RECORD.md` | halt/resume and exclusion record |
| `FREEZE.json`, `FREEZE_COMMIT.txt` | freeze manifest (64 inputs) and commit marker |

Freeze commit: `a5283b3fbaebe8323637c1dedbe951530ce222c3`.
Post-freeze record: `e1d14f518b913d4059e03fde1d8ad99a1ed23890`.

## 9. Boundary

Portability + evaluator sensitivity under OUR stress rule only; no native
benchmark defect; no pooling across labels or with any other cohort; the
external task set is the pinned 2026-10-05 NYU CTF Bench crypto census
(7 criterion-5-qualified tasks). The run used APINEX free-tier models; the
provider-attested labels are not weight-identity claims.
