# HEB-2 — Contract V2: Specified Execution-Completion Semantics and a Mechanized Soundness Check

**Project:** ACTS-Attack  
**Date:** 2026-10-20  
**Status:** COMPLETE — preregistered, hash-frozen, fail-closed preflight, executed

## 1. What this stage resolves

Stage 4's matched arm produced a case the Stage 1 preregistration did not specify: a program that
**printed a correct candidate and then exited non-zero**. The frozen V1 check order contains no
execution-status check, and the preregistration states no rule about execution completion. The
audit question was therefore not "is the attribution right" but "which rule applies, and who decides".

This stage decides the rule **in advance**, in a separately versioned contract, and measures both
readings on identical evidence.

## 2. The two preregistered semantics

| Arm | Precondition | Meaning |
|---|---|---|
| `output` | none beyond V1 | Attribution asserts the executed bytes produced a candidate the independent reference adjudicated as satisfying the predicate. |
| `completion` | the observation must record `execution_status == EXECUTED` (returncode 0) | Attribution asserts the above **and** that the execution completed. |

The completion precondition is evaluated on the attribution boundary, which is exactly equivalent to
evaluating it immediately before the terminal predicate step. The V1 aggregator was **not** modified;
V2 composes it by subclassing.

## 3. Freeze and execution

| Item | Value |
|---|---|
| Preregistration | `heb2_contract_v1/PREREGISTRATION.md` — SHA-256 `f3d7ce2f5f674faaa2b623f2af255c7228da9e7f643f2f1ad8b1171eefbc7f86` |
| Freeze manifest | `heb2_contract_v1/FREEZE.json` — SHA-256 `fa67ec394ddea3f8ad8e71689b8f8ccd857456136fdf17cec93bc9572822d8a9` |
| Fail-closed preflight | **passed** (37 files, 0 errors) via the audited `heb1_remediation_v1/integrity/manifest_verifier.py` |
| Fresh trust material | yes, own keys and bundle; the frozen Stage 1 bundle untouched |
| V2 run | `heb2_contract_v1/runs/20261020T091958Z_v2`, `raw_results.jsonl` SHA-256 `dfcbf2493458995c816cb3881b386c6db5ae163dc92f9a64fa3de02744352e20` |

The V2 run reproduces the Stage 1 scripted decisions (6 attributed, 0 false negatives, 0 false
positives) on the frozen 22-case inventory — an independent replication of Stage 1 under a new
contract.

## 4. The semantic contrast, measured on four corpora

`heb2_contract_v1/evaluate_existing_evidence.py` applies the frozen V2 contract to evidence that
already existed, with a second freeze and its own fail-closed preflight
(`FREEZE_EVALUATION.json`, SHA-256 `c3412e18da4b9eeaf9749f1cd9d65d8614fb8b650e58c406097e1c1995282fe2`).

| Corpus | Attributed (`output`) | Attributed (`completion`) | Cases whose decision changes |
|---|---|---|---|
| Stage 1 confirmatory (scripted) | 6 | 6 | none |
| HEB-2 V2 run (scripted) | 6 | 6 | none |
| Stage 4 model arm, run 1 | 4 | 3 | `H_FAIL_CH_01` |
| Stage 4 model arm, run 2 | 4 | 3 | `H_FAIL_CH_01` |

**H2-A is confirmed for the model arms and refuted for the scripted inventory.** The difference is
confined to cases whose observation records a non-zero exit status, exactly as preregistered. On the
scripted inventory the gap is **latent**: the scripted `fail` variant emits no output, so it is
refused as unparseable under both readings.

The earlier characterisation of `H_FAIL_CH_01` as "a labelling artifact" was **too lenient** and is
withdrawn. The correct statement: the preregistration does not specify the case, and under the
strict reading the attribution is a genuine false positive of one per model-arm run.

## 5. Mechanized soundness check

**Property S1 (preregistration §4).** If the contract returns `ATTRIBUTED_SUCCESS` then: (a) both
evidence records verify under the trust bundle and issuer policy; (b) their signed contexts bind to
the certificate's `(target_id, attempt_id, epoch)` with the authorized role and kind; (c) the
reference's stdout pin equals the observer's captured-stdout digest and its candidate digest equals
the observer's parsed-candidate digest; (d) the reference independently adjudicated
`crypto_ok = true` with `verdict = ACCEPTED`; (e) *(completion arm only)* the observation records
`execution_status = EXECUTED`.

**Corpus.** A seeded mutation corpus (seed 20261020) of **1,407 mutants per corpus**, built from
the genuine per-case certificates by 19 mutation operators (signature corruption, key-id
substitution, payload corruption in each record, certificate-field corruption, evidence deletion,
cross-case splicing, claim-block changes, evidence permutation) plus 1,000 random mutants. Each
mutant is evaluated under both semantics — **2,814 evaluations per corpus** — with a **fresh**
aggregator, so the replay ledger is empty and the check is strictly harder on the contract than a
normal evaluation.

| Corpus | Corpus size | Evaluations | Accepted mutants | **Soundness violations** | Genuine-bundle violations |
|---|---|---|---|---|---|
| Stage 4 model arm, run 1 | 1,407 | 2,814 | 43 | **0** | 0 |
| Stage 4 model arm, run 2 | 1,407 | 2,814 | 43 | **0** | 0 |
| Stage 1 confirmatory (scripted) | 1,407 | 2,814 | 47 | **0** | 0 |
| HEB-2 V2 run (scripted) | 1,407 | 2,814 | 47 | **0** | 0 |

**11,256 evaluations, zero soundness violations.** Every bundle the contract attributed satisfied
S1.

**The only mutation class that remains acceptable is the claim-block mutation** — setting
`claims.attribution` to either value. That is by design and is a direct confirmation of the
declaration-invariance property: the claimant's assertion cannot change the verdict, while every
mutation that touches the chain is refused.

The mutation corpus is a falsification attempt with a stated scope, not a formal proof.

## 6. Two corrections made during the stage, both disclosed

1. **The property was initially applied to refused bundles.** The first evaluation reported 130
   "violations" that were the expected non-violations of refused bundles (a refused bundle need not
   have a true predicate). The check was corrected to constrain accepted bundles only; the first
   attempt is retained under `heb2_contract_v1/attempt1_vacuous_property_check/`.
2. **The mutation-corpus builder assumed every case carries both evidence records.** Some cases
   legitimately omit one, so the builder was given explicit per-operator preconditions; the
   intermediate attempts are retained under `attempt2_fuzz_donor_bug/` and `attempt3_operator_preconditions/`.

The frozen `soundness_check.py` was left byte-identical to what the V2 freeze pinned; the corrected
check is a separate, separately pinned component (`soundness_check_v2.py`, SHA-256
`7a05ba88c50db548dc864ebd6b21579c1eb54c26f7ae1eac16c4079aa8ba64da`).

## 7. Determination

1. The execution-completion ambiguity is **resolved into a specified, frozen, measured contract**:
   two preregistered semantics, both evaluated on identical evidence, with the difference quantified
   (one case, in the model arms, confined to a non-completed execution).
2. **The contract is sound on the tested corpus**: 11,256 evaluations, zero violations, with the
   only acceptable mutation being the deliberately-ignored claim block.
3. The **scripted inventory cannot expose the gap**; only a producer that both outputs a valid
   candidate and fails can, and the model arm produced exactly that. This is a concrete instance of
   the general claim that a contract's untested combinations are discovered by adversarial producers,
   not by the contract's own test suite.
4. The frozen V1 contract and its recorded results are **unchanged**; V2 is additive.

## 8. Reproduction

```
heb2_contract_v1/PREREGISTRATION.md        the preregistration (written before execution)
heb2_contract_v1/contract.py               Contract V2: two semantics + the executable S1 check
heb2_contract_v1/run_contract_v2.py        freeze, fail-closed preflight, paired arm evaluation
heb2_contract_v1/evaluate_existing_evidence.py  applies V2 to four existing corpora
heb2_contract_v1/soundness_check_v2.py     seeded mutation corpus and S1 verification
heb2_contract_v1/FREEZE.json               run freeze (verified fail-closed)
heb2_contract_v1/evaluation_results.json   four-corpus comparison
heb2_contract_v1/soundness_*.json          the four soundness reports
```