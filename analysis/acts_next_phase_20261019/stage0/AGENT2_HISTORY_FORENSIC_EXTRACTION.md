# AGENT2 — History Forensic Extraction (independent recomputation from raw artifacts)

**Scope of this document.** This is an *independent recomputation* of the historical
measurements of Experiment B (HEB-1 held-out, IAR-A, IAR-B, IAR-C) and B2-2 Stage01,
performed **read-only** against the retained raw artifacts. No experiment was
executed, no validator/runner/campaign was invoked, no network call was made, and
no file was modified except this one.

**What this document is not.** It is not a restatement of the narrative. Where the
narrative and the raw data agree, the agreement is stated with the JSON key path that
proves it. Where they differ, the difference is stated. Where a claim cannot be
checked against retained raw data at all, it is marked **UNVERIFIABLE** rather than
assumed.

**Provenance of the claims checked.** The claim list was supplied in the task brief and
cross-read against these narrative sources:

- `sp2027/analysis/experiment_b_20261019/EXPERIMENT_B_REPORT.md` (primary)
- `sp2027/analysis/experiment_b_20261019/EXPERIMENT_B_PROTOCOL.md`
- `sp2027/analysis/experiment_b_20261019/iar_c/IAR_C_RESULTS_REPORT.md`
- `sp2027/analysis/experiment_b_20261019/IAR_B_RESULTS_REPORT.md`
- `sp2027/analysis/experiment_b_20261019/b2_2_stage01/B2_2_STAGE01_REPORT.md`
- `sp2027/analysis/experiment_b_20261019/b2_2_stage01_v2_20261019/B2_2_FINAL_REPORT.md`
- `sp2027/analysis/heb1_crossboundary_20261019/HEB1_EVALUATION_REPORT.md`
- `sp2027/analysis/heb1_crossboundary_20261019/HEB1_ADJUDICATION_RESPONSE_20261019.md`
- `sp2027/analysis/heb1_remediation_v1/adjudication/AUDIT_NOTES.md` (the "corrected metrics audit")
- `sp2027/analysis/heb1_independent_adversarial_audit_20261019/*` (multi-agent re-audit)

---

## 1. METHOD

### 1.1 General procedure

For each experiment I (a) located the retained raw result JSON, (b) read the runner
source that produced it to recover the **exact** metric predicate, (c) re-implemented
that predicate independently in a separate read-only Python script over the raw
`per_case` / `cases` rows, and (d) compared my recomputed numbers field-by-field with
the numbers the artifact itself recorded, and with the numbers the narrative reports.

Where a second, independently-written metric implementation exists in-tree
(`sp2027/analysis/heb1_remediation_v1/adjudication/audit_recompute.py`), I re-implemented
*that* logic as a second independent check, because it uses **different denominators**
from the original runner. This is the single most important methodological decision in
this document: the tree contains two different, both "raw", denominator conventions, and
they produce different-looking numbers for the same experiment.

### 1.2 Metric predicates as implemented in the source (not as described in prose)

| Experiment | Metric | Exact predicate (from source) | Source location |
|---|---|---|---|
| HEB-1 held-out | attack false promotion | `systems[S].decision=="EMIT" and systems[S].level==6 and not adjudicator.truth_strong`, **restricted to** `family in {B1,B2,B3,B4a,B4b,B5}` | `heb1_crossboundary_20261019/heldout/heb1_heldout_runner.py:178-194` |
| HEB-1 held-out | `any_positive_gt_truth` | `systems[S].level (int) > adjudicator.level (or 0)`, **all 64 cases, no family filter** | `heb1_heldout_runner.py:216-218` |
| HEB-1 held-out | true-accept B0 / C1 | `decision=="EMIT" and level==6 and adjudicator.truth_strong` | `heb1_heldout_runner.py:209-213` |
| IAR-C | level-6 FP | `level6_promotion[S] and adj.truth_strong is False` (optionally `family in ATTACK`) | `experiment_b_20261019/iar_c/eb_independent_runner.py:213-226` |
| IAR-C | `ATTACK` denominator set | `{"S4","S5","S6","S7","S8","S9","S10","S11","S12","S14","S15"}` = 11 families → **28 cases** | `eb_independent_runner.py:57` |
| IAR-C | `HONEST` denominator set | `{"S1","S2","S3","S13"}` → **16 cases** | `eb_independent_runner.py:56` |
| IAR-C | `honest_within_evidence` | `not malformed and supported>=1 and requested<=supported` | `eb_independent_runner.py:236-241` |
| IAR-C | false reject | over `honest_within_evidence` rows: `asserted[S] != adj.supported` | `eb_independent_runner.py:243-250` |
| IAR-C | overclaim | `not malformed and asserted[S] is not None and asserted[S] > adj.supported` | `eb_independent_runner.py:228-234` |
| IAR-C | agreement | `asserted[S] is not None and asserted[S]==adj.supported` (numerator only; **denominator not stored**) | `eb_independent_runner.py:252-257` |
| IAR-C (audit convention) | `attack` (substantive) | `not malformed and family not in HONEST_FAMILIES` → **20 cases** | `audit_recompute.py:151-154` |
| IAR-C (audit convention) | `partial_claimable` | `family in HONEST and family in PARTIAL_FAMILIES(={"S13"}) and requested<=supported and requested<6` → **10 cases** | `audit_recompute.py:156-158, 18` |
| IAR-C (audit convention) | `honest_full_claims` | `family in HONEST and requested==6` → **2 cases** (S1) | `audit_recompute.py:155` |
| B2 | level-6 FP | `level6_promotion[S] and adj.truth_strong is not True` — **no family filter, no denominator recorded** | `experiment_b_20261019/b2/b2_runner.py:263-268` |
| B2 | false reject | `not malformed and supported>=1 and requested<=supported and decisions[S] in (None,"REJECT")` | `b2_runner.py:283-296` |

### 1.3 Terminology discipline (as required by the task)

- **False promotion** = the system asserted an attribution level that the adjudicator's
  truth does not support (asserted level > supported level, or asserted level 6 when
  `truth_strong` is False). It is an *attribution* failure.
- **False cryptographic success** = the cryptographic predicate itself was wrong
  (e.g. `crypto_details.signatures_verify == false`, `recovered_d_matches == false`).
  These are **separate** quantities and are reported separately in §2.

In every artifact examined here, the cryptographic predicate was **correct in every
case** — the defects are all binding/provenance defects, never crypto defects. This is
confirmed by the raw `adjudicator.crypto_ok` fields and by
`crypto_details.{public_key_matches,recovered_d_matches,recovered_k_matches,repeated_r,signatures_verify}`
being all-`true` in every retained B2-2 reference-verifier verdict. **The measured
failure mode is false promotion (attribution without support), not false cryptographic
success.**

### 1.4 What was NOT done

No runner, validator, adjudicator, generator, or campaign script was executed. The
`audit_recompute.py` and `verify_iar_a.py` utilities were **read** and their logic
**re-implemented independently** in a scratch script; neither was invoked. The retained
`/tmp/opencode/iar_a_verify/verify_report.json` was read as a pre-existing artifact.

---

## 2. RAW-RECOMPUTED TABLES

### 2.1 HEB-1 held-out (64 cases)

**Source artifact:** `sp2027/analysis/heb1_crossboundary_20261019/heldout/heldout_results.json`
(sha256 `4bda7b8f4183b577d1b6ab6dd998d7147e086e70ee2e1f202b7eb3726d1f7265` — matches the
hash quoted in `EXPERIMENT_B_REPORT.md:161`).
**Row source:** `cases[cid].systems.<V0|V1|V2>.{decision,level}` and
`cases[cid].adjudicator.{level,truth_strong,malformed}`.
**Family roster** (from `cases[cid].family`): B0=8, B1=6, B2=6, B3=6, B4a=6, B4b=6, B5=6,
C1=4, C2=4, C3=4, C4=4, C5=4 → 64.

| Variant | Denominator definition | False promotions | Denominator | Rate | Raw evidence (JSON key path) | My recompute == recorded? |
|---|---|---|---|---|---|---|
| V0 (schema+reference) | attack families {B1,B2,B3,B4a,B4b,B5} | 36 | 36 | 1.00 | `metrics.systems.V0.attack_fp.n` / `.d` / `.rate` | **YES** (36/36, 1.0) |
| V1 (hash integrity) | attack families {B1,B2,B3,B4a,B4b,B5} | 36 | 36 | 1.00 | `metrics.systems.V1.attack_fp.n` / `.d` / `.rate` | **YES** (36/36, 1.0) |
| V2 (claim binding) | attack families {B1,B2,B3,B4a,B4b,B5} | 0 | 36 | 0.00 | `metrics.systems.V2.attack_fp.n` / `.d` / `.rate` | **YES** (0/36, 0.0) |
| V0 — per family | B1..B5, 6 each | 6,6,6,6,6,6 | 6 each | 1.00 | `metrics.systems.V0.attack_fp.by_family` | **YES** |
| V1 — per family | B1..B5, 6 each | 6,6,6,6,6,6 | 6 each | 1.00 | `metrics.systems.V1.attack_fp.by_family` | **YES** |
| V2 — per family | B1..B5, 6 each | 0,0,0,0,0,0 | 6 each | 0.00 | `metrics.systems.V2.attack_fp.by_family` | **YES** |
| V0 — *all* level-over-truth cases (no family filter) | all 64 | 40 | 64 | 0.625 | `metrics.systems.V0.any_positive_gt_truth` | **YES** (mine 40) |
| V1 — *all* level-over-truth cases | all 64 | 40 | 64 | 0.625 | `metrics.systems.V1.any_positive_gt_truth` | **YES** (mine 40) |
| V2 — *all* level-over-truth cases | all 64 | 0 | 64 | 0.000 | `metrics.systems.V2.any_positive_gt_truth` | **YES** (mine 0) |

Supplementary recomputed values (all match the artifact exactly):
`true_accept_b0` = 8/8 and `true_accept_c1` = 4/4 for **all three** systems;
`false_rejects` = 0/0/0; `errors` = 0/0/0;
`metrics.systems.V2.stated_vs_adjudicated_level_agreement` = "38/38" (I recomputed
38/38 by regexing `supported=(\d+)` out of `cases[cid].systems.V2.reason` and comparing to
`cases[cid].adjudicator.level`).

**Finding H1 (material, denominator scoping).** The headline "36/36" is
**attack-family-scoped**. The raw artifact's own `any_positive_gt_truth` = **40** for
V0 and V1. The 4 extra cases are in control family **C4**
(`"reference-acceptance-without-attribution → strong claim must not be emitted"`,
`HEB1_EXPERIMENT_PROTOCOL_20261019.md:34`): adjudicator truth level = **1**, but V0 and
V1 both `EMIT` level **6**. I identified them directly:
`hx-476703df98`, `hx-663f7774a9`, `hx-7bed328d67`, `hx-9838ff7331` (all family C4).
So across the full 64-case held-out set the level-6 false promotions for V0/V1 are
**40**, not 36. The C4 failures are the *intended* control test, so the "36/36" figure is
not wrong — but any presentation of "36/36" as *the* held-out false-promotion count
understates the total by 4 (11 % relative). Control-family behaviour, recomputed:

| Control family | n | adjudicator.level | V0 | V1 | V2 |
|---|---|---|---|---|---|
| B0 (coherent, true-accept) | 8 | 6 | EMIT 6 ×8 | EMIT 6 ×8 | EMIT 6 ×8 |
| C1 (valid+valid, true-accept) | 4 | 6 | EMIT 6 ×4 | EMIT 6 ×4 | EMIT 6 ×4 |
| C2 (honest level 2) | 4 | 2 | EMIT 2 ×4 | EMIT 2 ×4 | REJECT ×4 |
| C3 (malformed) | 4 | 0 | REJECT ×4 | REJECT ×4 | REJECT ×4 |
| C4 (ref-acceptance w/o attribution) | 4 | 1 | **EMIT 6 ×4** | **EMIT 6 ×4** | REJECT ×4 |
| C5 (stale/mismatched run id) | 4 | 1 | EMIT 1 ×4 | EMIT 1 ×4 | REJECT ×4 |

Malformed cases in HEB-1: 4, all family C3 (`adjudicator.malformed == true`).
Malformed cases are **excluded** from the attack-family denominator (C3 is not an attack
family) — see §4.

### 2.2 IAR-C (44 cases) — preserved pass `runs/20261019_121621/results.json`

**Source artifact:** `sp2027/analysis/experiment_b_20261019/iar_c/runs/20261019_121621/results.json`
(sha256 `7ad02c14f9328d82ccdfe3cdfbe7b0d0d88143b6f8393222701c7872187de785` — matches
`IAR_C_RESULTS_REPORT.md:70` and `B2_2_FINAL_REPORT.md:43`).
**Calibration pass** `runs/20261019_121420/results.json`
(sha256 `cb3df2b0a6668812990536dd3f6bc8b24a0b334ea04403cc4b7b0c1e7b79c185` — matches
`IAR_C_RESULTS_REPORT.md:65`): **`per_case` arrays are byte-equal** and **`metrics` are
equal except `overhead_ms_mean`**. The two passes are therefore the same measurement.
Run `121420` has `frozen_component_check = null` (freeze not yet present);
run `121621` has all 8 frozen-component hashes `match: true`.

**Cohort reconstruction** (from `per_case[].family` × `per_case[].adj.malformed`):

| Cohort | Definition | Cases | Derivation |
|---|---|---|---|
| All | every row | 44 | `len(per_case)` == `metrics.cases` = 44 |
| Malformed | `adj.malformed is True` | 8 | family S15 (a,b,c,d × 2) |
| Substantive | `not adj.malformed` | 36 | 44 − 8 |
| Attack, attack-inclusive | `family in ATTACK` (S4–S12, S14, S15) | **28** | 20 substantive + 8 malformed |
| Attack, substantive only | substantive and `family not in HONEST` | **20** | S4–S12, S14 |
| Honest | `family in HONEST` = {S1,S2,S3,S13} | **16** | == `metrics.honest_within_evidence_cases` = 16 |
| Honest full claims | honest and `requested == 6` | **2** | S1 only |
| Eligible partial claims (audit convention) | honest, `family in {S13}`, `requested<=supported`, `requested<6` | **10** | S13 k=1..5 |
| Other honest partial claims (NOT in audit denominator) | honest, `requested<6`, `requested<=supported` | **4** | S2 (n=2, level 2), S3 (n=2, level 2) |

#### 2.2.1 Runner-convention metrics (as recorded in `results.json`)

| Metric | Denominator definition | V2 | V3-sig | V3-full | Raw evidence (key path) | Recompute == recorded? |
|---|---|---|---|---|---|---|
| Level-6 FP, attack-inclusive | `family in ATTACK` (n=28) | **10** | **14** | **0** | `metrics.fp_level6.<s>.attack` | **YES** (10/14/0) |
| Level-6 FP, all cases | all 44 | 10 | 14 | 0 | `metrics.fp_level6.<s>.all` | **YES** (10/14/0) |
| Level-6 FP, substantive attacks | n=20 | 10 | 14 | 0 | *derived* (`per_case`) | **YES** |
| Level-6 FP by family | per family | S7×2, S9×2, S10×2, S11×2, S12×2 (10) | S4×2, S5×2, S6×2, S7×2, S8×2, S11×2, S14×2 (14) | `{}` (0) | `metrics.fp_level6.<s>.by_family` | **YES** |
| Overclaim (asserted > supported), substantive | n=36 | 10 | 14 | 0 | `metrics.overclaim.<s>` | **YES** |
| False reject (honest-within-evidence) | n=16 | 14 | 0 | 0 | `metrics.false_reject.<s>` | **YES** |
| Honest accepted at true supported level | n=16 | 2 | 16 | 16 | `metrics.honest_accept_full.<s>` | **YES** |
| Agreement with adjudicator (where asserted) | asserted≠null | **2/12** | **16/30** | **16/16** | numerator in `metrics.agreement.<s>`; **denominator NOT in artifact**, recomputed from `per_case[].asserted` | **YES** on numerator; denominators 12/30/16 are *derived*, not raw |
| Malformed S15 handled | n=8 | 8/8 REJECT | 8/8 REJECT | 8/8 REJECT | `per_case[].systems.<s>` | **YES** |
| Fixture failures / label deviations / determinism / system failures | — | 0 / 0 / 0 / 0 | | | `metrics.fixture_failures`, `.label_deviations`, `.determinism_mismatches`, `.system_failures` | **YES** |

#### 2.2.2 Audit-convention metrics (independent re-implementation of `audit_recompute.py`)

| Metric | Denominator | V2 | V3-sig | V3-full | Note |
|---|---|---|---|---|---|
| `false_promotion` / `level6_false_promotion` | attack substantive, n=**20** | **10/20** | 14/20 | 0/20 | == AUDIT_NOTES "V2 false promotion is 10/20" |
| `overclaim` | substantive, n=36 | 10/36 | 14/36 | 0/36 | |
| `false_reject_honest` | honest full claims, n=**2** | **0/2** | 0/2 | 0/2 | == AUDIT_NOTES "V2 full-claim false rejection is 0/2" |
| `raw_rejection_coverage` | eligible partial, n=**10** | **10/10** | 0/10 | 0/10 | == AUDIT_NOTES "raw partial rejection coverage 10/10" |
| `partial_acceptance` | eligible partial, n=**10** | **N/A** | 10/10 | **10/10** | == AUDIT_NOTES "V2 partial is N/A", "V3-full partial acceptance is 10/10" |
| `partial_acceptance` **ALT** (partial widened to include S2,S3, n=14) | n=14 | 0/14 (14/14 raw rejection) | **14/14** | **14/14** | see Finding I2 |

**Finding I1 (numerator is denominator-invariant; the two headline denominators are not
interchangeable).** The same underlying measurement — V2 promoting 10 cases in IAR-C —
is reported as **10/28** in `IAR_C_RESULTS_REPORT.md:80` and `EXPERIMENT_B_REPORT.md:62`,
and as **10/20** in `AUDIT_NOTES.md:21`. Both are internally correct:
- 28 = `ATTACK` family set = 20 substantive attacks **+ 8 malformed S15 controls**;
- 20 = substantive attacks only, malformed excluded.

The 8 malformed S15 cases contribute **0** to the numerator (all three systems REJECT
all 8), so the numerator is 10 under either denominator. But the *rates* differ
(0.357 vs 0.500) and the 28-denominator is inflated by 8 cases whose rejection is
trivial. The two numbers must never be substituted for one another, and the raw
artifact stores **only the numerator** (`metrics.fp_level6.<s>.attack` = 10/14/0) — the
denominator 28 is not recorded anywhere in `results.json`; it is recoverable only from
`eb_independent_runner.py:57` + `per_case[].family`.

**Finding I2 (material: the "10 eligible partial claims" denominator is a family
whitelist, not a data property).** `audit_recompute.py:18` hard-codes
`PARTIAL_FAMILIES = frozenset({"S13"})`. The raw IAR-C data contain **14** honest
partial-claim cases, not 10: S13 (n=10, k=1..5) **plus S2 (n=2, requested=2,
supported=2) and S3 (n=2, requested=2, supported=2)**. S2/S3 are honest *failure*
cases whose adjudicated support is level 2 < 6, i.e. partial claims, and V3-sig and
V3-full both ACCEPT them at exactly level 2 (visible in `per_case[].asserted`).
Consequence if the whitelist is widened:
- V2 raw partial rejection: **10/10 → 14/14**
- V3-full partial acceptance: **10/10 → 14/14**
- V3-sig partial acceptance: **10/10 → 14/14**
- V2 partial acceptance: stays N/A (V2 emits no partial level at all — it EMITs only
  level 6 or REJECTs; verified: V2 `asserted` values in S13 are all `null`).

So the AUDIT_NOTES sentence "10 eligible partial claims" is **true as recomputed
against its own stated definition** but is **not** the count of honest partial-claim
cases in the raw data. The definition is defensible (S2/S3 are honest *failures*, not
"partial evidence" cases) but it is a choice, and it is not visible in the number
itself. `AUDIT_NOTES.md` does not state that S2/S3 are excluded — a reader of
"10 eligible partial claims" would not know 4 more exist.

**Finding I3 (narrative denominator wording).** `IAR_C_RESULTS_REPORT.md:85` reports
"Honest accepted at true supported level (n=16)" and `:136-138` describes the 16 as
"levels 1–5, including all S13 partial fractions". The 16 are actually 2 × S1 at level
**6**, 4 × S2/S3 at level 2, and 10 × S13 at levels 1–5. The phrase "levels 1–5" is
inaccurate for the 2 S1 cases.

### 2.3 IAR-A (stage01 cross-boundary transfer)

**Source artifact:** `sp2027/analysis/heb1_crossboundary_20261019/iar/iar_a_20261019/iar_a_results.json`
(sha256 `c3f225825d8b0989d6a14336ba44e80342c572a23bee9b64b79448f300401313`).

| Variant | Blind validator | Reference verifier | both_accept | candidate_matches_registry | Raw key path |
|---|---|---|---|---|---|
| `baseline_A0` | ACCEPT | ACCEPTED (predicate true, integrity true) | — | — | `baseline_A0.*` |
| `A1_trace_candidate_splice` | ACCEPT | ACCEPTED | **true** | **false** | `A1_trace_candidate_splice.both_accept` / `.candidate_matches_registry` |
| `A2_trace_hash_wrong` | ACCEPT | ACCEPTED | **true** | **false** | `A2_unbound_references[0].*` |
| `A2_agent_session_mismatch` | ACCEPT | ACCEPTED | **true** | **false** | `A2_unbound_references[1].*` |
| `A2_reference_claim_unbound` | ACCEPT | ACCEPTED | **true** | **false** | `A2_unbound_references[2].*` |
| `A3_relabeled_trace` | ACCEPT | ACCEPTED | **true** | **false** | `A3_relabeled_trace.both_accept` / `.candidate_matches_registry` |

Ground-truth registry (never supplied to the systems): `registry.X.candidate_sha256 =
aed7e1d8…`, `registry.Y.candidate_sha256 = e1647eab…`; every variant's
`submitted_candidate_sha256 = e1647eab…` while `registry_candidate_sha256 = aed7e1d8…`
→ candidate does not match registry in all 5 attack variants. I independently re-hashed
all 5 `public_certificate_sha256` values against the files: **5/5 match**.

**IAR-A reproduction check ("75 PASS / 2 WARN / 0 FAIL").**
Retained raw artifact: `/tmp/opencode/iar_a_verify/verify_report.json` (10331 bytes,
JSON, sha256 `be8329716d84…`). It is produced by
`heb1_crossboundary_20261019/iar/verify_iar_a.py` (declared in `report.verifier`).

| Item | Recomputed | Claimed | Verdict |
|---|---|---|---|
| Total checks | 77 | 77 | **AGREES** |
| PASS | 75 | 75 | **AGREES** |
| WARN | 2 | 2 | **AGREES** |
| FAIL | 0 | 0 | **AGREES** |

The two WARN rows are, verbatim:
- `["WARN", "A1b_session_binding: stored verdict in archive", "no entry in iar_a_results.json"]`
- `["WARN", "archive: A1b control verdict absent from iar_a_results.json", "re-verified here from stored A1b files; memo row only"]`

Component hashes in the report re-verify against the live tree: validator
`f248413d9b47…`, reference `15bb4095ee39…`, results `c3f225825d8b…` — **3/3 match**.

**Finding A1 (retention gap, material for citation).** The `75 PASS / 2 WARN / 0 FAIL`
figure is **not retained inside the repository**. `verify_iar_a.py` writes its report to
`/tmp/opencode/iar_a_verify/verify_report.json` (`verify_iar_a.py:331`), and that file
still exists on this machine, but it is outside version control and is not referenced by
any committed artifact. The **A1b control verdict is absent from the committed
`iar_a_results.json`** — this is the subject of both WARNs, and it is the same gap
acknowledged in `HEB1_MULTIAGENT_REAUDIT_20261019.md:61` and
`EVIDENCE_LEDGER.md:25`. Consequence: the narrative statement in
`EXPERIMENT_B_REPORT.md:167-170` that *"the real stage01 validator v2 + reference
verifier v2 … rejected the session-mismatch variant via `execution-session-binding`"*
is **not supported by the committed IAR-A results JSON**; it is supported only by the
un-committed `/tmp` report and by the A1b re-run inside B2-2 (see §2.5, case
`a1b_reproduction`, which *does* independently show `REJECT / execution-session-binding`
from both the original validator and the original reference verifier). So the A1b
behaviour is corroborated by B2-2's raw subprocess records, but the IAR-A archive
itself does not contain it.

### 2.4 IAR-B dev + held-out, and B2 (dev + held-out)

**Source artifacts:**
- `experiment_b_20261019/iar_b/runs/20261019_112227/results.json` (dev, 54 cases,
  sha256 `032c93bedb65…` — matches `IAR_B_RESULTS_REPORT.md:59` and `B2_2_FINAL_REPORT.md:41`)
- `experiment_b_20261019/iar_b_heldout/runs/20261019_114849/results.json` (held-out, 58 cases,
  sha256 `be08433db0d…` — matches `IAR_B_RESULTS_REPORT.md:197` and `B2_2_FINAL_REPORT.md:42`)
- `experiment_b_20261019/b2/runs/20261019_140814/results.json` (B2, 470709 bytes)

#### 2.4.1 IAR-B (runner convention)

| Set | Metric | Denom. | V2 | V3-sig | V3-full | Raw key path | Recompute |
|---|---|---|---|---|---|---|---|
| dev (54) | level-6 FP (all cases) | 54 | 16 | 24 | 0 | `metrics.fp_level6.v2_all` / `.v3sig_attack` / `.v3full_all` | **YES** |
| dev (54) | FP families | — | H5,H6a,H6b,H9 | H1,H2,H3,H4,H6b,H9 | — | `metrics.fp_families` | **YES** |
| dev (54) | false reject | honest+within-evidence | 10 | 0 | 0 | `metrics.false_reject` | **YES** |
| dev (54) | agreement | asserted≠null | 4 | 14 | 14 | `metrics.agreement` (numerator) | **YES** |
| held-out (58) | level-6 FP (all cases) | 58 | 16 | 28 | 0 | same | **YES** |
| held-out (58) | FP families | — | H5,H6a,H6b,H9 | H1,H2,H3,H4,H6b,H9,H10 | — | `metrics.fp_families` | **YES** |
| held-out (58) | false reject | honest+within-evidence | 10 | 0 | 0 | `metrics.false_reject` | **YES** |
| held-out (58) | label deviations | — | **4** (H10, expected REJECT/3, got REJECT/5) | 0 | 0 | `metrics.label_deviations` (list, 4 entries) | **YES** |
| held-out (58) | gates | — | G-B1..G-B5 all `pass: true` | | | `gates` | **YES** |

The 4 held-out label deviations **are disclosed** in the narrative
(`IAR_B_RESULTS_REPORT.md:98-110`: "Exactly four deviations, all on H10 and all on V2,
expected `{REJECT, level 3}` vs actual `{REJECT, level 5}`"). Both verdicts are REJECT,
so they do not affect any promotion metric. **This is a disclosed, non-material
deviation — not a discrepancy.**

#### 2.4.2 B2 (held-out set)

**Structural fact established from the raw paths:** B2's two sets are **not new case
sets**. `sets[0].paths.cases` == IAR-B dev case dir; `sets[1].paths.cases` ==
IAR-B held-out case dir. The case-ID sets are **identical** (dev 54/54, held-out 58/58)
and the **v3-full decisions match IAR-B's on 58/58 held-out cases**. B2 re-analyses the
*same* IAR-B data with added baseline systems; it is not an additional held-out draw.

| Variant | Denominator definition | False promotions | Denominator | Rate | Raw key path | Recompute |
|---|---|---|---|---|---|---|
| digest-only | **none recorded in artifact** | **8** | 58 (all) / 44 (attack fam.) / 36 (substantive attack) — **not stated** | — | `sets[1].metrics.fp_level6["digest-only"]` | **YES** (8) |
| digest-session | same | **0** | same — not stated | — | `sets[1].metrics.fp_level6["digest-session"]` | **YES** (0) |
| v3-full | same | **0** | same — not stated | — | `sets[1].metrics.fp_level6["v3-full"]` | **YES** (0) |
| v2 | same | 16 | same | — | `sets[1].metrics.fp_level6["v2"]` | **YES** |
| v3-sig | same | 28 | same | — | `sets[1].metrics.fp_level6["v3-sig"]` | **YES** |
| abl-authjoin / abl-executor / abl-refjoin / abl-tracejoin | same | 4 / 4 / 4 / 0 | same | — | `sets[1].metrics.fp_level6.*` | **YES** |
| dev-set counterparts | same | digest-only 4, digest-session 0, v3-full 0, v2 16, v3-sig 24 | — | — | `sets[0].metrics.fp_level6.*` | **YES** |

**Finding B1 (material: B2 reports a bare count with no denominator).**
`b2_runner.py:263-268` computes `fp_count(system)` over **all** cases in the set with
**no family filter** and **no denominator is stored anywhere in `results.json`**.
`EXPERIMENT_B_REPORT.md:57-62` places the B2 numbers in a table with an `n` column
(64 / 54 / 58 / 44) but the B2 row of the *per-part* report
(`b2/B2_BASELINE_COMPARISON_REPORT.md`) and the `fp_level6` key itself carry no
denominator. The three defensible denominators for the held-out set are:
- **58** — all cases in the set;
- **44** — attack families, excluding H0 (clean, n=4) and H7 (honest partial, n=10);
- **36** — substantive attacks, additionally excluding the 8 malformed H8 cases.
The numerator 8 is the same under all three (8 = 4 × H6b [supported 0] + 4 × H10
[supported 3]). **A rate cannot be stated for B2 from the raw artifact without adding a
denominator that the artifact does not contain.**

**Finding B2 (scoping).** In the B2 held-out set, `level6_promotion["v3-full"]` is
`true` on **4** rows — but all 4 are H0 (clean, `truth_strong: true`, supported 6), i.e.
legitimate full accepts. The recorded false-promotion count of 0 excludes them via
`adj.truth_strong is not True` (`b2_runner.py:265`). The same holds for `digest-only`
(4 of its 8 raw `level6_promotion` rows are H0). The raw `level6_promotion` flag is
therefore **not** a false-promotion flag; it is an "asserted level 6" flag. Any
downstream reader that treats `per_case[].level6_promotion` as a false promotion will
over-count by the number of clean cases (4 in B2 held-out; 2 in IAR-C).

**Finding B3 (disclosed, non-material).** `sets[1].metrics.reference_deviations` has 4
entries — the same 4 H10 V2 deviations as IAR-B held-out. `b2_runner.py` records them
but no B2 gate checks them, and `B2_BASELINE_COMPARISON_REPORT.md` does not surface
them. Not a contradiction, but the B2 held-out set carries a known 4-row label deviation
that its gate set (`all_gates.B2-G1..B2-G5`, all `true`) does not test.

### 2.5 B2-2 Stage01 (5-case matrix)

**Source artifacts:**
- `experiment_b_20261019/b2_2_stage01/B2_2_RESULTS.json` (30456 bytes, sha256
  `ad4be099a2cb97a4fd86eb497d3b7c8bdaea38f8848be00801cb632a4128a7cd` — matches the
  hash quoted in `B2_2_STAGE01_REPORT.md:48-49` **and** `B2_2_SUMMARY.json.results_sha256`,
  which I verified byte-for-byte)
- `experiment_b_20261019/b2_2_stage01_v2_20261019/raw_subprocess/*.json` (5 files) — an
  **independent second capture** of the same five cases by a different runner
  (`b2_2_stage01_v2_20261019/run_independent_audit.py`)

| Case | Original validator | Original reference verifier | External wrapper | Outer hashes | v1 key path | v2 raw key path | v1 == v2? |
|---|---|---|---|---|---|---|---|
| `clean_control` | ACCEPT / public-evidence-consistent | ACCEPTED / predicate true / integrity true | INCONCLUSIVE / trace-has-no-candidate-hash | — | `cases[i].original_validator.verdict` | `raw_subprocess/clean_control.json` | **YES** |
| `a1_reproduction` | ACCEPT | ACCEPTED | INCONCLUSIVE | — | same | `raw_subprocess/a1_reproduction.json` | **YES** |
| `a1b_reproduction` | **REJECT / execution-session-binding** | **REJECTED** / execution-session-binding / integrity false / predicate true | INCONCLUSIVE | — | same | `raw_subprocess/a1b_reproduction.json` | **YES** |
| `candidate_binding_mismatch` | **ACCEPT** | **ACCEPTED** / integrity true / predicate true | **REJECT / semantic-candidate-execution-mismatch** | all match | same | `raw_subprocess/candidate_binding_mismatch.json` | **YES** |
| `candidate_binding_match_control` | ACCEPT | ACCEPTED | **ACCEPT / candidate-execution-bound** | all match | same | `raw_subprocess/candidate_binding_match_control.json` | **YES** |

**Independent re-hash of the mismatch case's outer integrity** (I re-computed the
SHA-256 of every referenced file rather than trusting the recorded `match: true`):
candidate `e1647eab…` ✔, `agent_artifact` `7adb445b…` ✔, `execution_trace` `32f2c79d…` ✔,
`target_effect` `ec529447…` ✔, `verifier_metadata` `576521b7…` ✔, `boundary` `d85bd02b…` ✔
— **6/6 match**. Raw key path: `raw_subprocess/candidate_binding_mismatch.json →
outer_integrity`.

**The semantic mismatch itself, from raw bytes**
(`b2_2_stage01/cases/candidate_binding_mismatch/evidence/execution_trace.json`):
`candidate_sha256 = aed7e1d8456b…` (run X's candidate, per
`iar_a_results.json → registry.X.candidate_sha256`), while the certificate's candidate
pointer is `e1647eab901a…` (run Y's candidate, `registry.Y.candidate_sha256`). The
outer hashes are all valid, so this is a *semantic* binding failure, not a stale-hash
failure. The `a1b_reproduction` case is the converse and is rejected by both original
components.

**V3-full comparison:**
- `b2_2_stage01/B2_2_RESULTS.json → v3_full_comparison.status` = **"NOT_COMPARABLE"**,
  `action` = *"not invoked; no V3-full verdict is claimed"*, with 4 named
  `missing_contract_elements`.
- `b2_2_stage01_v2_20261019/B2_2_FINAL_REPORT.md:68` gate table states
  **"V3-full comparison | PASS as read-only baseline"** (existing IAR-B/IAR-C results
  consumed, not rerun). `B2_2_INDEPENDENT_AUDIT.json → v3_full_established_results`
  lists the 3 established artifacts with "mode: read-only established result; not rerun".

**Finding C1 (framing divergence between the two B2-2 reports).** The two B2-2
artifacts use *opposite* dispositions for the same non-event: v1 records
`status: "NOT_COMPARABLE"`; v2 records a **gate PASS** ("PASS as read-only baseline").
Both agree V3-full was never run on Stage01 inputs. A reader comparing the two
documents, or citing the gate table, could conclude that a V3-full comparison was
validated when in fact none was performed. The task-brief claim ("direct V3-full
comparison was NOT_COMPARABLE") matches the **v1** raw artifact and is **DISAGREED** by
the **v2** report's gate table.

**Finding C2 (retention).** B2-2 v2 (`b2_2_stage01_v2_20261019/`) is the *newer*
artifact and contains the independent re-capture (`raw_subprocess/`) plus
`B2_2_INDEPENDENT_AUDIT.json`. The v1 directory (`b2_2_stage01/`) has no per-case raw
subprocess capture — only the consolidated `B2_2_RESULTS.json`. Both are consistent;
the v2 capture is the stronger evidence and it confirms v1.

### 2.6 Cross-artifact hash verification (integrity spot-check)

Every artifact hash quoted in the narrative was re-computed from the live tree:

| Artifact | Claimed in | Recomputed | Match |
|---|---|---|---|
| `heldout/heldout_results.json` | `EXPERIMENT_B_REPORT.md:161` | `4bda7b8f4183…` | **YES** |
| `HEB1_ADJUDICATION_RESPONSE_20261019.md` | `EXPERIMENT_B_REPORT.md:164` | `d0ab76e110d9…` | **YES** |
| `iar_c/runs/20261019_121620/results.json` | `IAR_C_RESULTS_REPORT.md:65` | `cb3df2b0a666…` | **YES** |
| `iar_c/runs/20261019_121621/results.json` | `IAR_C_RESULTS_REPORT.md:70` | `7ad02c14f932…` | **YES** |
| `iar_c/freeze/IAR_C_FREEZE.json` | `IAR_C_RESULTS_REPORT.md:187` | `a2145de564c1…` | **YES** |
| `iar_c/freeze/IAR_C_CASE_MANIFEST.json` | `IAR_C_RESULTS_REPORT.md:188` | `d2640d409886…` | **YES** |
| `iar_c/eb_independent_gen.py` | `IAR_C_RESULTS_REPORT.md:189` | `dba82edd4fd3…` | **YES** |
| `iar_c/eb_independent_adj.py` | `IAR_C_RESULTS_REPORT.md:190` | `528dcb43657e…` | **YES** |
| `iar_c/eb_independent_runner.py` | `IAR_C_RESULTS_REPORT.md:191` | `d9aebb8d93fd…` | **YES** |
| `iar_c/data/labels/iar_c_labels.json` | `IAR_C_RESULTS_REPORT.md:192` | `75776db2e9f2…` | **YES** |
| `iar_c/data/trust/iar_c_run_keys.json` | `IAR_C_RESULTS_REPORT.md:193` | `d4629a4aa477…` | **YES** |
| `eb_v3_sig.py` | `IAR_C_RESULTS_REPORT.md:194` | `6b17954b0441…` | **YES** |
| `eb_v3_full.py` | `IAR_C_RESULTS_REPORT.md:195` | `6c7d0d8b564e…` | **YES** |
| `heb1_v2_claim_binding.py` | `IAR_C_RESULTS_REPORT.md:196` | `3585f876a39d…` | **YES** |
| `iar_b/runs/20261019_112227/results.json` | `IAR_B_RESULTS_REPORT.md:59` | `032c93bedb65…` | **YES** |
| `iar_b_heldout/runs/20261019_114849/results.json` | `IAR_B_RESULTS_REPORT.md:197` | `be08433db0da…` | **YES** |
| `b2_2_stage01/B2_2_RESULTS.json` | `B2_2_STAGE01_REPORT.md:48` | `ad4be099a2cb…` | **YES** |
| `b2_2_stage01/B2_2_SUMMARY.json.results_sha256` | — | matches `B2_2_RESULTS.json` | **YES** |
| Stage01 validator | `B2_2_STAGE01_REPORT.md:36` | `f248413d9b47…` | **YES** |
| Stage01 reference verifier | `B2_2_STAGE01_REPORT.md:39` | `15bb4095ee39…` | **YES** |
| external binding wrapper | `B2_2_STAGE01_REPORT.md:42` | `2589c98c89fe…` | **YES** |
| B2-2 protocol | `B2_2_STAGE01_REPORT.md:43` | `a08869a5e103…` | **YES** |
| `iar_a_results.json` | `verify_report.json → component_sha256.results` | `c3f225825d8b…` | **YES** |
| 5 × campaign runner hashes | `B2_2_FINAL_REPORT.md:53-57` | all 5 match | **YES** |

**23/23 quoted hashes verify.** No artifact-integrity discrepancy was found.

---

## 3. CLAIM-vs-RAW RECONCILIATION

| # | Claim | Source document | Raw-recomputed value | Verdict | Note |
|---|---|---|---|---|---|
| 1 | HEB-1 held-out: V0/V1 **36/36** false promotions | `EXPERIMENT_B_REPORT.md:158-159`; `HEB1_EVALUATION_REPORT.md:73,102-103`; `HEB1_ADJUDICATION_RESPONSE_20261019.md:21`; `EVIDENCE_LEDGER.md:24` | `metrics.systems.V0.attack_fp` = n 36 / d 36, rate 1.0; V1 identical; recomputed from `cases[cid].systems.*` | **AGREES** | Attack-family scoped. The same artifact records `any_positive_gt_truth` = **40**; the extra 4 are C4 control cases (truth level 1) where V0/V1 EMIT 6. See Finding H1. |
| 2 | HEB-1 held-out: V2 **0/36** false promotions | same | `metrics.systems.V2.attack_fp` = n 0 / d 36, rate 0.0; recomputed 0 | **AGREES** | `any_positive_gt_truth` = 0 for V2 across all 64; `false_rejects` = 0; B0 8/8, C1 4/4. |
| 3 | HEB-1 held-out "V2 rejected 36/36" | `EXPERIMENT_B_PROTOCOL.md:18`; `EXPERIMENT_B_REPORT.md:159` | V2 REJECTs **52/64**; REJECTs all 36 attack-family cases | **AGREES (scoped)** | 36/36 is attack-family scoped; total REJECTs = 52 (36 attack + 16 of the 28 non-attack cases). |
| 4 | IAR-C attack-inclusive: V2 **10/28** | `IAR_C_RESULTS_REPORT.md:80`; `EXPERIMENT_B_REPORT.md:62,284-285` | `metrics.fp_level6.v2.attack` = 10; denominator 28 = `ATTACK` family set (S4–S12,S14,S15) = 20 substantive + 8 malformed | **AGREES** | Numerator is raw; **denominator 28 is not stored in `results.json`** (derived from `eb_independent_runner.py:57`). See Finding I1. |
| 5 | IAR-C attack-inclusive: V3-sig **14/28** | same | `metrics.fp_level6["v3-sig"].attack` = 14 | **AGREES** | by_family = S4,S5,S6,S7,S8,S11,S14 ×2. |
| 6 | IAR-C attack-inclusive: V3-full **0/28** | same | `metrics.fp_level6["v3-full"].attack` = 0, `by_family` = `{}` | **AGREES** | 4 raw `level6_promotion` rows are true for V3-full, all S1 (truth_strong=true) → correctly excluded. |
| 7 | IAR-C: **20 substantive attacks** | `AUDIT_NOTES.md:19-20` | 20 (36 substantive − 16 honest) | **AGREES** | Reproduced by re-implementing `audit_recompute.py:151-154`. |
| 8 | IAR-C: **16 honest cases** | `AUDIT_NOTES.md:20` | 16 = `metrics.honest_within_evidence_cases` = 16 | **AGREES** | |
| 9 | IAR-C: **2 honest full claims** | `AUDIT_NOTES.md:20` | 2 (S1, `requested==6`) | **AGREES** | |
| 10 | IAR-C: **10 eligible partial-claim cases** | `AUDIT_NOTES.md:20` | 10 **under the audit's own definition** (`PARTIAL_FAMILIES={"S13"}`); **14** under a data-driven definition (adds S2 n=2, S3 n=2) | **DISAGREES (definition-dependent)** | The number is definition-bound and the exclusion of S2/S3 is not stated in AUDIT_NOTES. See Finding I2. |
| 11 | IAR-C: V2 false promotion **10/20** | `AUDIT_NOTES.md:21` | 10/20 (substantive attack denominator) | **AGREES** | Numerator identical to the 10/28 figure; denominators differ. |
| 12 | IAR-C: V2 full-claim false rejection **0/2** | `AUDIT_NOTES.md:21` | 0/2 | **AGREES** | V2 `asserted`=6 == `adj.supported`=6 on both S1 cases. |
| 13 | IAR-C: V2 partial = **N/A** | `AUDIT_NOTES.md:21-23` | N/A by construction (`audit_recompute.py:168-169`); V2 emits no partial level in any of the 10 (or 14) partial cases | **AGREES** | Defensible: V2 is a full-attribution emitter. Raw evidence: all S13 `asserted["v2"]` are `null`. |
| 14 | IAR-C: V2 raw partial rejection coverage **10/10** | `AUDIT_NOTES.md:22-23` | 10/10 (S13); **14/14** if S2/S3 included | **AGREES (scoped)** | Scope not stated. |
| 15 | IAR-C: V3-full partial acceptance **10/10** | `AUDIT_NOTES.md:23` | 10/10 (S13); **14/14** if S2/S3 included | **AGREES (scoped)** | Scope not stated. |
| 16 | IAR-C: V2 rejects 14/16 honest-within-evidence | `EXPERIMENT_B_REPORT.md:119-120`; `IAR_C_RESULTS_REPORT.md:83,138` | `metrics.false_reject.v2` = 14, denominator `honest_within_evidence_cases` = 16 | **AGREES** | The 14 rejected are exactly the 14 partial-claim cases (S2,S3,S13); the 2 accepts are the 2 S1 full claims. |
| 17 | IAR-C agreement "2/12, 16/30, 16/16" | `IAR_C_RESULTS_REPORT.md:84` | numerators 2/16/16 = `metrics.agreement`; denominators 12/30/16 recomputed from `per_case[].asserted != null` | **AGREES** | Denominators are **not** in the raw artifact — derived. |
| 18 | IAR-C: "Honest accepted at true supported level (n=16)" | `IAR_C_RESULTS_REPORT.md:85` | `metrics.honest_accept_full` = 2 / 16 / 16 (denominator 16) | **AGREES** | The report's gloss "levels 1–5" (`:136-138`) is inaccurate — 2 of the 16 are level 6 (S1). See Finding I3. |
| 19 | IAR-C: all 8 malformed S15 REJECTed by all 3 systems | `IAR_C_RESULTS_REPORT.md:86,139-141` | 8/8 REJECT for v2, v3-sig, v3-full | **AGREES** | |
| 20 | IAR-A reproduction: **75 PASS / 2 WARN / 0 FAIL** | `EXPERIMENT_B_REPORT.md:171`; `AUDIT_PROTOCOL.md:35`; `EVIDENCE_LEDGER.md:25`; `HEB1_MULTIAGENT_REAUDIT_20261019.md:61` | `/tmp/opencode/iar_a_verify/verify_report.json`: 77 checks, 75 PASS, 2 WARN, 0 FAIL | **AGREES** | **But the artifact is outside the repository** (written to `/tmp/opencode/iar_a_verify/` by `verify_iar_a.py:331`). The A1b verdict is absent from the committed `iar_a_results.json`. See Finding A1. |
| 21 | IAR-A: A1 and A1b reproduced; A2/A3 unbound fields accept | `EVIDENCE_LEDGER.md:25` | A1, A2×3, A3 all `both_accept: true` in `iar_a_results.json`; A1b **absent** from `iar_a_results.json` | **PARTIALLY UNVERIFIABLE** | A1b is corroborated only by the un-committed `/tmp` report and by B2-2 `a1b_reproduction` raw subprocess record (REJECT/execution-session-binding). |
| 22 | B2 held-out: digest-only **8** false promotions | `b2/B2_BASELINE_COMPARISON_REPORT.md`; `EXPERIMENT_B_REPORT.md` B2 section | `sets[1].metrics.fp_level6["digest-only"]` = 8 | **AGREES** | Bare count. **No denominator recorded in the artifact.** See Finding B1. |
| 23 | B2 held-out: digest-session **0** | same | `sets[1].metrics.fp_level6["digest-session"]` = 0 | **AGREES** | Bare count, no denominator. |
| 24 | B2 held-out: V3-full **0** | same | `sets[1].metrics.fp_level6["v3-full"]` = 0 | **AGREES** | 4 raw `level6_promotion` true rows are all H0 `truth_strong=true` → excluded. See Finding B2. |
| 25 | B2 "held-out" is a held-out set | `EXPERIMENT_B_REPORT.md:61` | `sets[1].paths.cases` == IAR-B held-out case dir; **identical 58 case IDs**; v3-full decisions identical 58/58 | **DISAGREES (in the strict sense)** | B2's held-out set **is** the IAR-B held-out set re-analysed with added baselines, not an additional blind held-out draw. The word "held-out" is inherited, not new. |
| 26 | B2-2: unchanged Stage01 validator + reference verifier **accepted** a candidate/execution mismatch | `B2_2_STAGE01_REPORT.md:18`; `B2_2_FINAL_REPORT.md:21`; `EXPERIMENT_B_REPORT.md` B2-2 section | `B2_2_RESULTS.json → cases[3].original_validator.verdict.decision == "ACCEPT"`; `cases[3].original_reference.verdict.reference_verdict == "ACCEPTED"`; independently re-captured in `raw_subprocess/candidate_binding_mismatch.json` | **AGREES** | All 6 outer hashes independently re-verified as matching. |
| 27 | B2-2: external semantic check **rejected** the mismatch | `B2_2_STAGE01_REPORT.md:18`; `B2_2_FINAL_REPORT.md:21` | wrapper verdict `status: "REJECT"`, `reason: "semantic-candidate-execution-mismatch"`, cert candidate `e1647eab…` vs trace candidate `aed7e1d8…` | **AGREES** | |
| 28 | B2-2: matching positive control **accepted** | `B2_2_STAGE01_REPORT.md:19`; `B2_2_FINAL_REPORT.md:22` | wrapper verdict `status: "ACCEPT"`, `reason: "candidate-execution-bound"`, both hashes `e1647eab…` | **AGREES** | |
| 29 | B2-2: direct V3-full comparison **NOT_COMPARABLE** | `B2_2_RESULTS.json → v3_full_comparison.status` | `"NOT_COMPARABLE"`, `action: "not invoked; no V3-full verdict is claimed"` | **AGREES vs v1 / DISAGREES vs v2 report** | `B2_2_FINAL_REPORT.md:68` records the same gate as **"PASS as read-only baseline"**. See Finding C1. |
| 30 | B2-2: `a1b_reproduction` rejected by original components via `execution-session-binding` | `B2_2_STAGE01_REPORT.md:17`; `B2_2_FINAL_REPORT.md:20` | validator `REJECT / execution-session-binding`; reference `REJECTED`, `certificate_integrity: false`, `cryptographic_predicate: true` | **AGREES** | |
| 31 | IAR-B held-out: 4 label deviations (H10, V2, REJECT/3 vs REJECT/5) | `IAR_B_RESULTS_REPORT.md:98-110` | `metrics.label_deviations` = 4 entries, exactly as described; also `b2` `sets[1].metrics.reference_deviations` = same 4 | **AGREES** | Disclosed in the narrative; not gated in either runner. |
| 32 | "No inspected historical record contains a false promotion of unsupported attribution" (free_v2 arm) | `EXPERIMENT_B_REPORT.md:46-47`; `historical/HISTORICAL_VALIDATION_NOTES.md` | Not recomputed in this pass (historical arm outside the named raw sources) | **UNVERIFIABLE** | The cited gate records are `contract_sound_72_repair_deterministic_20261018*` trees, which I did not open. Marked unverifiable, not false. |
| 33 | IAR-C "all 8 frozen component hashes verified" | `IAR_C_RESULTS_REPORT.md:74-75` | `frozen_component_check` in run `121621`: 8/8 `match: true` | **AGREES** | Run `121420` has `frozen_component_check: null` — the calibration pass did **not** verify frozen hashes. Both passes produce identical `per_case`/`metrics` (excluding timing), so this is not a substantive difference, but the calibration pass carries weaker provenance evidence. |
| 34 | IAR-C / IAR-B / B2 offline, $0 spend | `IAR_C_RESULTS_REPORT.md:163`; `EXPERIMENT_B_REPORT.md:157` | `manifest.model_calls / network_calls / provider_calls` = 0/0/0 in all three results.json | **AGREES** | Self-declared by the artifact; not independently provable from the artifact. |

---

## 4. DENOMINATOR DEFINITIONS

This section states, for every rate in this document, the exact denominator, and
explicitly whether malformed / malformed-control cases are included.

| Rate as reported | Denominator | Definition of the denominator | Malformed included? | Honest-control cases included? |
|---|---|---|---|---|
| HEB-1 V0/V1 "36/36" | 36 | `cases[cid].family ∈ {B1,B2,B3,B4a,B4b,B5}` (6 families × 6) | **No** — the 4 malformed cases are family C3, not an attack family | **No** — B0/C1/C2/C4/C5 (24 cases) excluded |
| HEB-1 V2 "0/36" | 36 | same | No | No |
| HEB-1 `any_positive_gt_truth` = 40 | 64 | all cases in `cases` | Yes (4 C3 malformed, none of which contribute) | Yes — this is where the 4 C4 false promotions appear |
| HEB-1 true-accept B0 | 8 | `family == "B0"` | No | — |
| HEB-1 true-accept C1 | 4 | `family == "C1"` | No | — |
| HEB-1 V2 level agreement "38/38" | 38 | cases where `systems.V2.reason` matches `supported=(\d+)` | No | Partly (B0, C1, C2, C4, C5 minus those without a level) |
| IAR-C "10/28, 14/28, 0/28" (attack-inclusive) | 28 | `per_case[].family ∈ ATTACK = {S4..S12, S14, S15}` — 20 substantive attacks **+ 8 malformed S15** | **YES — malformed S15 controls are IN the denominator** | No (S1,S2,S3,S13 excluded) |
| IAR-C "10/20, 14/20, 0/20" (substantive attacks) | 20 | substantive (non-malformed) and `family ∉ {S1,S2,S3,S13}` | **No — malformed S15 EXCLUDED** | No |
| IAR-C overclaim | 36 | substantive (non-malformed) | No | Yes (S2,S3,S13 rows can in principle overclaim; they do not) |
| IAR-C false reject | 16 | `honest_within_evidence` = not malformed ∧ supported ≥ 1 ∧ requested ≤ supported → S1(2)+S2(2)+S3(2)+S13(10) | No | Yes — this denominator is *only* honest cases |
| IAR-C honest_accept_full | 16 | same 16 | No | Yes |
| IAR-C agreement "2/12, 16/30, 16/16" | 12 / 30 / 16 | cases where `per_case[].asserted[<s>] != null` (i.e. the system asserted *some* level) | No (malformed cases are all REJECT → asserted null) | Yes |
| IAR-C malformed handling "8/8" | 8 | `family == "S15"` | This **is** the malformed set | — |
| IAR-C "eligible partial claims" (audit) | 10 | honest ∧ `family ∈ {S13}` ∧ requested ≤ supported ∧ requested < 6 | No | S13 only; **S2 and S3 (4 cases) excluded by family whitelist** |
| IAR-C "honest full claims" | 2 | honest ∧ `requested == 6` → S1 | No | S1 only |
| IAR-C "20 substantive attacks" | 20 | substantive ∧ family ∉ HONEST | No | No |
| IAR-C "16 honest cases" | 16 | substantive ∧ family ∈ HONEST | No | Yes |
| B2 held-out FP counts (8/0/0/16/28/4/4/4/0) | **not recorded** | Defensible: 58 (all) / 44 (attack families, excl. H0+H7) / 36 (substantive attacks, excl. 8 malformed H8) | **Undetermined** — the artifact does not say. The 8 malformed H8 cases contribute 0 to every B2 numerator. | Undetermined |
| B2 dev FP counts (4/0/0/16/24/…) | **not recorded** | 54 (all) / 40 (attack fam.) / 32 (substantive attack) | Undetermined; 8 malformed H8 contribute 0 | Undetermined |
| IAR-B dev/held-out FP counts | **not recorded** | 54 / 40 / 32 (dev); 58 / 44 / 36 (held-out) | Undetermined; 8 malformed H8 contribute 0 | Undetermined |
| IAR-A "75 PASS / 2 WARN / 0 FAIL" | 77 checks | all rows in `verify_report.json → checks` | n/a (not case-based) | n/a |

**Summary of the malformed-inclusion question.** Only **one** headline rate in the whole
tree includes malformed cases in its denominator: IAR-C's "n=28" attack-inclusive rate
(8 malformed S15 controls inside 28). Every other substantive rate excludes them —
explicitly in `audit_recompute.py:151-152` (`malformed` vs `substantive` split, with
`"malformed cases are excluded from substantive rates"` as a stated limitation) and
implicitly in HEB-1's attack-family filter (malformed lives in C3). Because the
malformed cases contribute 0 to every numerator, **no false-promotion rate in the tree
is numerically distorted by their inclusion — only the denominator (and hence the
rate) moves.** The single exception where the choice *does* change the numerator is
none.

---

## 5. UNRESOLVED DISCREPANCIES

Ordered by materiality. **D1–D3 are the substantive findings.**

**D1 — Two irreconcilable denominators are published for the same IAR-C numerator.**
`10/28` (malformed-inclusive) and `10/20` (malformed-excluded) appear in the same
tree, both as "the" V2 false-promotion figure. Rates 0.357 vs 0.500. Neither raw
artifact records the denominator — `results.json` stores only the numerator. Any
downstream table that mixes the two (e.g. a table with an IAR-C row of "10/28" next to
an audit column of "10/20" without labelling the convention) is misleading.
*Recommendation:* publish both with explicit labels, or publish one and state the
convention inline; never let "10/28" and "10/20" float unlabelled.

**D2 — "10 eligible partial claims" silently excludes 4 honest partial-claim cases.**
`PARTIAL_FAMILIES = {"S13"}` (`audit_recompute.py:18`) is a hard-coded whitelist.
S2 and S3 are honest cases with `requested = supported = 2 < 6`; V3-sig and V3-full
both accept them at level 2. Under a data-driven definition the partial-claim
denominator is **14**, and V2's raw partial-rejection coverage is **14/14**, not
10/10. `AUDIT_NOTES.md` does not state the exclusion, so a reader sees "10" and
cannot know that 4 more exist. *Recommendation:* state the family whitelist next to
the number, or report 14 with a breakdown (S13 10 + S2 2 + S3 2).

**D3 — HEB-1's "36/36" under-reports the total held-out false promotions by 4.**
The artifact's own `any_positive_gt_truth` = 40 for V0 and V1. The 4 excluded
promotions are in control family C4 ("reference-acceptance-without-attribution → strong
claim must not be emitted"), which by construction requires a level-6 emission to fail.
These are genuine unsupported-attribution promotions, not a metric artefact, and they
are the *designed* failure of the V0/V1 contract. The narrative "36/36" is scoped to
the defect suite and is defensible; the risk is that it is read as the total.
*Recommendation:* when citing HEB-1, report both "36/36 attack families" and "40/64
level-over-truth cases", and name the 4 C4 cases.

**D4 — B2 publishes counts with no denominators, and its "held-out" set is IAR-B's
held-out set.** `fp_level6` in `b2/runs/20261019_140814/results.json` is a bare count
over all 58 (or 54) cases, with no family filter and no denominator field. The B2
case-set paths point at `iar_b/cases/dev` and `iar_b_heldout/cases/dev`, and the case
IDs are identical to IAR-B's (58/58 and 54/54), with identical v3-full decisions. So
"B2 held-out" adds baseline systems, not new held-out data. A table presenting B2 as a
separate held-out experiment with an "n" in the same column as IAR-B's is easy to
misread as independent evidence.

**D5 — The IAR-A "75 PASS / 2 WARN / 0 FAIL" artifact is not in the repository.**
`verify_report.json` lives in `/tmp/opencode/iar_a_verify/`, and the committed
`iar_a_results.json` has **no A1b entry** (both WARNs say so). The A1b behaviour is
corroborated by B2-2's `raw_subprocess/a1b_reproduction.json` (validator
`REJECT/execution-session-binding`, reference `REJECTED`), so the underlying claim
survives — but the specific IAR-A archive does not contain the A1b verdict that
`EVIDENCE_LEDGER.md:25` and `EXPERIMENT_B_REPORT.md:167-170` cite.

**D6 — The two B2-2 reports give opposite dispositions for the same non-event.**
`B2_2_RESULTS.json → v3_full_comparison.status = "NOT_COMPARABLE"` vs
`B2_2_FINAL_REPORT.md:68` gate "V3-full comparison | PASS as read-only baseline".
Both agree V3-full was never run on Stage01 inputs, but a gate table reading "PASS"
can be mis-cited as a successful comparison.

**D7 — The IAR-C calibration pass (121420) has no frozen-component verification.**
`frozen_component_check = null` in run `121420`; it is fully populated (8/8 match) in
run `121621`. Metrics and `per_case` are otherwise identical. Low materiality, but
`IAR_C_RESULTS_REPORT.md:65-66` cites the calibration pass by hash without noting the
weaker provenance.

**D8 — IAR-C agreement denominators are derived, not raw.**
`metrics.agreement` stores only numerators (2/16/16). The "12/30/16" denominators in
`IAR_C_RESULTS_REPORT.md:84` are recoverable from `per_case[].asserted` and I confirmed
them — but the artifact alone cannot be checked for them.

**D9 — `level6_promotion` is an "asserted level 6" flag, not a false-promotion flag.**
In HEB-1 (`heldout_results.json`), IAR-C (`results.json`) and B2
(`b2/runs/.../results.json`) the flag is `true` on legitimate clean/strong cases too
(IAR-C: 2 S1 rows; B2 held-out: 4 H0 rows for v3-full and 4 H0 rows for digest-only).
The false-promotion metrics add a `truth_strong` filter. Any consumer that reads the
raw flag as "false promotion" over-counts. `audit_recompute.py:26-27` explicitly
declares this ("stored `level6_promotion` flags are not treated as verdicts") — good,
but the caveat lives in one audit note, not in the artifacts that carry the flag.

**D10 — Minor: `IAR_C_RESULTS_REPORT.md:136-138` describes the 16 honest-within-evidence
cases as "levels 1–5".** Two of the 16 (S1) are level 6. Wording only.

**D11 — Unverifiable in this pass.** The historical (`free_v2`, 72-session) arm's
"no false promotion of unsupported attribution" claim was not recomputed: the cited
gate records live in `contract_sound_72_repair_deterministic_20261018*` trees that
were not opened for this extraction. Marked **UNVERIFIABLE**, not disputed.

**D12 — Provenance claims that the artifact cannot self-certify.** "model_calls / network
/ provider calls = 0" and "no provider was called" are self-declared manifest fields
(`manifest.*`). `audit_recompute.py:32-34` makes the same concession ("it does not
prove that … a provider was not called"). Accepted as declared, not as verified.

**No item in this document is a fabricated, reversed, or contradicted measurement.**
Every numeric claim in the brief that had a retained raw artifact behind it reproduced
exactly, on re-execution of the metric logic over the raw rows. The findings are about
**denominator labelling, scope, retention and framing** — not about the underlying
measurements.

---

## 6. FILE INVENTORY

Every file opened during this extraction, with byte size, a SHA-256 prefix, and
parseability. `JSON OK` = parsed by `json.loads`. `text/utf-8` = Python source or
Markdown (parsed as UTF-8; not JSON). All paths are relative to
`/mnt/nvme5/ACTS-Attack` unless absolute.

| # | File | Bytes | sha256 (12) | Parseable |
|---|---|---|---|---|
| 1 | `sp2027/analysis/heb1_crossboundary_20261019/heldout/heldout_results.json` | 109230 | `4bda7b8f4183` | **JSON OK** — primary HEB-1 raw artifact |
| 2 | `sp2027/analysis/heb1_crossboundary_20261019/heldout/heb1_heldout_runner.py` | 15972 | `5f74d9ab9c04` | text/utf-8 — HEB-1 metric predicates |
| 3 | `sp2027/analysis/heb1_crossboundary_20261019/heldout/heb1_heldout_gen.py` | 6520 | `076c56144775` | text/utf-8 |
| 4 | `sp2027/analysis/heb1_crossboundary_20261019/build/labels/heldout_labels.json` | 16547 | `5e2f84a7d278` | **JSON OK** — family roster cross-check |
| 5 | `sp2027/analysis/heb1_crossboundary_20261019/HEB1_EXPERIMENT_PROTOCOL_20261019.md` | 7988 | `ab25961e5410` | text/utf-8 — control-family semantics (C1–C5) |
| 6 | `sp2027/analysis/heb1_crossboundary_20261019/HEB1_ADJUDICATION_RESPONSE_20261019.md` | 13770 | `d0ab76e110d9` | text/utf-8 — claim source + hash |
| 7 | `sp2027/analysis/heb1_crossboundary_20261019/iar/iar_a_20261019/iar_a_results.json` | 10799 | `c3f225825d8b` | **JSON OK** — primary IAR-A raw artifact |
| 8 | `sp2027/analysis/heb1_crossboundary_20261019/iar/verify_iar_a.py` | 18253 | `fe1eb86c90ba` | text/utf-8 — **read only, not executed**; report output path at L331 |
| 9 | `sp2027/analysis/experiment_b_20261019/iar_c/runs/20261019_121621/results.json` | 37750 | `7ad02c14f932` | **JSON OK** — IAR-C preserved pass (primary) |
| 10 | `sp2027/analysis/experiment_b_20261019/iar_c/runs/20261019_121420/results.json` | 35982 | `cb3df2b0a666` | **JSON OK** — IAR-C calibration pass |
| 11 | `sp2027/analysis/experiment_b_20261019/iar_c/eb_independent_runner.py` | 14571 | `d9aebb8d93fd` | text/utf-8 — IAR-C metric predicates, ATTACK/HONEST sets (L56-57) |
| 12 | `sp2027/analysis/experiment_b_20261019/iar_c/data/labels/iar_c_labels.json` | 23039 | `75776db2e9f2` | **JSON OK** — generator labels, `expected_adjudicator` / `expected_systems` |
| 13 | `sp2027/analysis/experiment_b_20261019/iar_c/freeze/IAR_C_FREEZE.json` | 3960 | `a2145de564c1` | **JSON OK** — declared component hashes |
| 14 | `sp2027/analysis/experiment_b_20261019/iar_c/freeze/IAR_C_CASE_MANIFEST.json` | 96294 | `d2640d409886` | **JSON OK** — 762-file case manifest |
| 15 | `sp2027/analysis/experiment_b_20261019/iar_c/IAR_C_RESULTS_REPORT.md` | 10815 | `7f9c7ecbd78c` | text/utf-8 — claim source |
| 16 | `sp2027/analysis/experiment_b_20261019/iar_b/runs/20261019_112227/results.json` | 34266 | `032c93bedb65` | **JSON OK** — IAR-B dev |
| 17 | `sp2027/analysis/experiment_b_20261019/iar_b_heldout/runs/20261019_114849/results.json` | 37580 | `be08433db0da` | **JSON OK** — IAR-B held-out |
| 18 | `sp2027/analysis/experiment_b_20261019/IAR_B_RESULTS_REPORT.md` | 10713 | `e5a988fbfcf5` | text/utf-8 — claim source; discloses the 4 H10 deviations |
| 19 | `sp2027/analysis/experiment_b_20261019/b2/runs/20261019_140814/results.json` | 470709 | `0c492313aa5c` | **JSON OK** — B2 dev + held-out (primary) |
| 20 | `sp2027/analysis/experiment_b_20261019/b2/b2_runner.py` | 17467 | `08af179262cb` | text/utf-8 — B2 metric predicates (no denominator) |
| 21 | `sp2027/analysis/experiment_b_20261019/b2/B2_BASELINE_COMPARISON_REPORT.md` | 8819 | — | text/utf-8 — claim source |
| 22 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01/B2_2_RESULTS.json` | 30456 | `ad4be099a2cb` | **JSON OK** — B2-2 v1 primary |
| 23 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01/B2_2_SUMMARY.json` | 5157 | `a0f806cdf933` | **JSON OK** — `results_sha256` verified against #22 |
| 24 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01/B2_2_STAGE01_REPORT.md` | 7677 | `58a82c0cb6e8` | text/utf-8 — claim source |
| 25 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01/B2_2_PROTOCOL.md` | 5166 | `a08869a5e103` | text/utf-8 — hash verified |
| 26 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01/external_candidate_binding_wrapper.py` | 3361 | `2589c98c89fe` | text/utf-8 — the external semantic check; **read only** |
| 27 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01_v2_20261019/B2_2_FINAL_REPORT.md` | 6695 | `38c0cde19d92` | text/utf-8 — claim source (v2 framing) |
| 28 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01_v2_20261019/B2_2_INDEPENDENT_AUDIT.json` | 79187 | `3677a2497c30` | **JSON OK** — B2-2 v2 audit record |
| 29 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01_v2_20261019/raw_subprocess/clean_control.json` | 6073 | `c47bc7830260` | **JSON OK** |
| 30 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01_v2_20261019/raw_subprocess/a1_reproduction.json` | 6093 | `bad63d7354ea` | **JSON OK** |
| 31 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01_v2_20261019/raw_subprocess/a1b_reproduction.json` | 6175 | `2a688dd2c4fc` | **JSON OK** — A1b REJECT evidence |
| 32 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01_v2_20261019/raw_subprocess/candidate_binding_mismatch.json` | 6620 | `56f4c6977eb9` | **JSON OK** — key mismatch case |
| 33 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01_v2_20261019/raw_subprocess/candidate_binding_match_control.json` | 6646 | `ef6aea7ba238` | **JSON OK** — positive control |
| 34 | `sp2027/analysis/experiment_b_20261019/EXPERIMENT_B_REPORT.md` | 32692 | `fd6cdb6bceb5` | text/utf-8 — primary narrative claim source |
| 35 | `sp2027/analysis/experiment_b_20261019/EXPERIMENT_B_PROTOCOL.md` | 15538 | — | text/utf-8 — claim source |
| 36 | `sp2027/analysis/heb1_remediation_v1/adjudication/AUDIT_NOTES.md` | 2700 | `93babc8686dc` | text/utf-8 — "corrected metrics audit" claim source |
| 37 | `sp2027/analysis/heb1_remediation_v1/adjudication/audit_recompute.py` | 13910 | `95e9209b9048` | text/utf-8 — **read only, not executed**; logic independently re-implemented |
| 38 | `sp2027/analysis/heb1_independent_adversarial_audit_20261019/AUDIT_PROTOCOL.md` | 2406 | `0751bf54b2a2` | text/utf-8 — "75 PASS / 2 WARN / 0 FAIL" claim source |
| 39 | `sp2027/analysis/heb1_independent_adversarial_audit_20261019/EVIDENCE_LEDGER.md` | 5719 | `8d065d3a2a3a` | text/utf-8 — claim source |
| 40 | `sp2027/analysis/heb1_independent_adversarial_audit_20261019/HEB1_MULTIAGENT_REAUDIT_20261019.md` | 18200 | `150b485af517` | text/utf-8 — claim source; notes the A1b archival gap |
| 41 | `sp2027/analysis/contract_sound_stage01_validator_v2.py` | 4435 | `f248413d9b47` | text/utf-8 — hashed only (**not executed**) |
| 42 | `sp2027/analysis/contract_sound_stage01_reference_verifier_v2.py` | 6588 | `15bb4095ee39` | text/utf-8 — hashed only (**not executed**) |
| 43 | `sp2027/analysis/run_contract_sound_stage01.py` | 26907 | `982978d1db85` | text/utf-8 — hashed only |
| 44 | `sp2027/analysis/run_contract_sound_stage01_hardened.py` | 22884 | `f46395a309cd` | text/utf-8 — hashed only |
| 45 | `sp2027/analysis/run_contract_sound_agent_pilot.py` | 14844 | `144984fcfd77` | text/utf-8 — hashed only |
| 46 | `sp2027/analysis/run_contract_sound_agent_pilot_free_v2.py` | 17046 | `7c81945d3e6d` | text/utf-8 — hashed only |
| 47 | `sp2027/analysis/run_contract_sound_agent_replacement_v1.py` | 11171 | `76f5b530a0a8` | text/utf-8 — hashed only |
| 48 | `/tmp/opencode/iar_a_verify/verify_report.json` | 10331 | `be8329716d84` | **JSON OK** — the retained IAR-A 77-check report. **Outside the repository**; written by `verify_iar_a.py` to `/tmp/opencode/iar_a_verify/`. |
| 49 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01/cases/candidate_binding_mismatch/evidence/execution_trace.json` | 209 | — | **JSON OK** — the mismatch bytes (X's candidate hash inside a Y-pointing certificate) |
| 50 | `sp2027/analysis/experiment_b_20261019/b2_2_stage01/cases/candidate_binding_mismatch/candidate.json` | 153 | — | **JSON OK** — Y's candidate material |

**Files read but not needed for a count:** none. **Files cited but NOT opened (so their
contents are unverified here):** `sp2027/analysis/experiment_b_20261019/historical/HISTORICAL_VALIDATION_NOTES.md`
and the `contract_sound_72_repair_deterministic_20261018*` trees it references (the
historical arm — see D11); `sp2027/analysis/experiment_b_20261019/iar_c/data/cases/**`
and `iar_c/data/private/**` (per-case inputs — the case-level verdicts were taken from
the runner's retained `per_case` rows, which are the primary measurement record);
`sp2027/analysis/heb1_crossboundary_20261019/build/cases/**` and `build/labels/**`
beyond `heldout_labels.json`.

**Parseability:** every one of the 16 JSON artifacts opened parsed cleanly with
`json.loads`; no malformed or truncated JSON was encountered. No file in the tree was
written to, and no experiment was executed.

---

*Extraction performed read-only by AGENT2. All numbers in §2 are independent
recomputations over raw rows, not transcriptions of the artifacts' own metric blocks —
though §2 also reports the artifact's own block alongside, and the two agree in every
case where both are defined.*
