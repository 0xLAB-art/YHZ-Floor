# TOEEA-1 — End-to-End Attribution Protocol and Preregistration

**Experiment ID:** `TOEEA-1` (Trusted-Observer End-to-End Attribution, Stage 1)
**Tree:** `sp2027/analysis/acts_next_phase_20261019/stage1_attribution/`
**Date written:** 2026-10-20 (pre-confirmatory-run)
**Status:** PREREGISTERED. This document is hashed into the Stage 1 integrity
manifest (`s1_integrity_manifest.json`) and the manifest is verified by the
audited remediation preflight (`heb1_remediation_v1/integrity/manifest_verifier.py`)
**before** the confirmatory run is allowed to start.

---

## 0. Scope, authorisation, and what this experiment is NOT

This is a **local, offline, authorised, constructed evaluation experiment** run
inside the ACTS-Attack research repository.

It is **NOT**:

* an exploit against any deployed or third-party service;
* a live-campaign result;
* evidence of deployed attacker reachability;
* a claim of a previously unknown security mechanism (see §9 and
  `NOVELTY_PRIOR_ART_MATRIX.md` — the mechanism family is prior art);
* a comparison against a real provenance product (in-toto / SLSA / Sigstore are
  analysed in Stage 2, not exercised here; see §8.4).

The historical campaign path constructs its own certificates internally
(`sp2027/analysis/run_contract_sound_agent_pilot.py:161-170`) and exposes **no**
external certificate-composition interface. That is a source-level negative
finding, restated here as the standing limitation of this experiment:
`NO_EXTERNAL_CERTIFICATE_COMPOSITION_INTERFACE_FOUND_IN_INSPECTED_REPOSITORY_PATHS`.

**The C-family cases in this experiment are synthetic contradiction-detection
fixtures.** They demonstrate that a verifier *can* discriminate the listed
contradiction classes. They do **not** demonstrate that an attacker can reach
that condition in the live campaign. Reachability is a separate question,
addressed in Stage 1B (boundary capability probe) and Stage 3 (operational
boundary).

**The producer arm is scripted, not a model.** Therefore no AI-specific claim
may be derived from any result in this experiment (historical correction
C-04: an AI-only outcome difference would be an arm-specific outcome, not a
mechanism).

---

## 1. Research question and hypotheses

**RQ.** Under one identical bundle set, one identical decision vocabulary and
one identical ground truth, how many ground-truth *non-success* cases does each
of four verification contracts permit to be promoted to an *attributed success*,
and how many ground-truth *successes* does each contract wrongly reject?

**H1 (causal binding).** A contract that joins the program bytes, the captured
stdout, the parsed runtime output and the reference verdict across independently
signed records will attribute strictly fewer non-success cases than a contract
that verifies each record in isolation. *Prediction:* E3's false-attribution
count < E2's < E1's ≤ E0's.

**H2 (non-regression).** The causal-binding contract rejects **no** ground-truth
success that the digest-only contract accepts. *Prediction:* E3 false-rejection
count = 0 on the honest-success denominator.

**H3 (tri-state).** A contract that distinguishes *absent* evidence from
*contradictory* evidence will classify every evidence-omission case as
INCONCLUSIVE rather than REJECT. *Prediction:* E3 = INCONCLUSIVE on all 5
B-family cases; E0–E2 also INCONCLUSIVE on them (all four contracts share the
same presence policy in this experiment, so this hypothesis tests the ladder
*and* the presence policy, not the presence policy alone).

**H4 (baseline capability gap).** The frozen historical Stage01 pair
(`contract_sound_stage01_validator_v2.py` + `contract_sound_stage01_reference_verifier_v2.py`,
both hash-pinned) will ACCEPT at least one case in which the credited program
was not the executed program, or the credited output was not the observed
output, while the E3 contract REJECTs it. *This is the component-capability
claim of Stage 1.*

**H0 (null).** H1–H4 are not supported.

**Predeclared decision rule for the confirmatory pass.** H1/H2/H3/H4 are each
reported as SUPPORTED / NOT SUPPORTED / INCONCLUSIVE from the tabulated
per-case outcomes. No metric, threshold, denominator or decision rule may be
changed after the confirmatory run starts. Any change is a deviation and is
logged in `s1_deviations.md`.

---

## 2. The four contracts under comparison

All four consume **the same bundle**, apply **the same presence policy**, and
emit **the same tri-state verdict vocabulary**.

| ID | Name | What it verifies | What it does NOT verify |
|---|---|---|---|
| E0 | `digest_only` | file digests against the bundle index; reads the reference verdict's `verdict` **without authenticating it** | record signatures, role authorization, context binding, replay, and **any** cross-record causal join |
| E1 | `signed_digest_only` | E0 + Ed25519 record signatures, role/kind/domain authorization (`protected_signing`) | context binding, replay, cross-record joins |
| E2 | `signed_context_only` | E1 + signed six-field context binding, replay ledger, path confinement (`context_validator`) | **cross-record joins** (it never compares the reference verdict to the submitted output, nor the producer's program digest to the program file, nor the observation's program digest to the program file) |
| E3 | `full` | E2 + the cross-record causal joins + the six-level claim ladder | — |

**E0–E2 are design classes, not products.** They are labelled that way
everywhere. They are an explicit *lower bound* on what a provenance-style
contract that attests artifacts but not executions can do. They are **not**
in-toto, SLSA, TUF, Sigstore or any other product, and no result in this
experiment may be presented as a product comparison.

**Frozen historical baseline (separate axis).** The frozen Stage01 pair is run
on the same executions wherever a direct analogue exists, and is reported in its
own column. It implements a *different* contract (a blind full-attribution
consistency checker with no trusted execution observer), so the comparison is a
**contract-coverage** comparison, not an equal-contract head-to-head. Where no
analogue exists the cell is reported as `N/A`.

---

## 3. The evidence chain and the trusted component

The bundle contains seven evidence entries. The *trusted component* is the
**trusted execution observer (TEO)**, which holds an Ed25519 private key that
the producer never holds, reads the program bytes, invocation, environment and
captured streams **itself**, and signs what it read.

| # | Object | Produced by | Carried in the bundle as | Bound to |
|---|---|---|---|---|
| 1 | Producer identity | producer role | `artifact_record` (signed) | — |
| 2 | Exact program source bytes + SHA-256 | producer writes; TEO hashes | `program_source` (file) | `artifact_record.program_sha256`, `observation.program_source_sha256` |
| 3 | Exact executed program bytes | TEO | — | `observation.program_source_sha256` + `program_source_sha256_after` |
| 4 | Invocation command + args | TEO | `observation.facts.argv` | — |
| 5 | Execution environment identity | TEO | `observation.facts.env_allowlist`, `env_sha256` | — |
| 6 | Input / public-instance digest | TEO | `observation.facts.input_sha256`, `stdin_sha256` | `expectation.input_sha256` |
| 7 | Target identity + target-state digest | reference verifier | `observation`/`reference_verdict` targets | `expectation.target_state_sha256` |
| 8 | Attempt / session identity + epoch | harness | signed context (6 fields) | all three signed records |
| 9 | Captured stdout / stderr | TEO | `execution_stdout`, `execution_stderr` (files) | `observation.stdout_sha256`, `reference_verdict.stdout_sha256` |
| 10 | Parsed runtime output + digest | TEO (parser `json-last-line-v1`) | `program_output` (file) | re-derivation check against the captured stdout |
| 11 | Trusted execution-observer record | TEO | `execution_observation` (signed) | — |
| 12 | Independent cryptographic reference result | reference verifier (holds the private target state + a secret key) | `reference_verdict` (signed) | `stdout_sha256`, `target_state_sha256` |
| 13 | Signed evidence with issuer identity + role | three roles | signed records | `protected_signing` public bundle |
| 14 | Aggregated certificate | harness (the bundle index) | `bundle.json` | file digests |
| 15 | Final attributed-success claim | E3 evaluator | the verdict | the six-level ladder |

**No chain link is a digest supplied by the untrusted producer.** The producer
supplies only: the program bytes, the signed `artifact_record`, and the
`bundle.json` index. Every digest the TEO and the reference verifier assert is
computed by the TEO or the reference verifier from bytes they read themselves.

### 3.1 The six-level ladder (E3)

| Level | Established when |
|---|---|
| L1 `artifact_authorship` | the `artifact_record` verifies **and** its `program_sha256` equals the digest of the program file in the bundle |
| L2 `execution_identity` | the `execution_observation` verifies **and** its `program_source_sha256` equals the program-file digest **and** the program was not modified during execution **and** its `input_sha256` equals the expectation's input digest |
| L3 `target_effect` | the `reference_verdict` verifies, says ACCEPTED with `cryptographic_predicate == true`, **and** is bound to the captured stdout that the observation recorded |
| L4 `reference_oracle_acceptance` | as L3 |
| L5 `boundary_enforcement` | the `execution_observation` verifies, `boundary.enforced` is true, the static source policy passed, the output parsed, **and** (strict contract) the return code was 0 |
| L6 `attribution` | L1 ∧ L2 ∧ L3 ∧ L4 ∧ L5 |

### 3.2 Decision vocabulary (identical for E0–E3)

* `ATTRIBUTED_SUCCESS` — every level established.
* `REJECT` — the evidence is present but contradictory, unauthorized, out of
  date, replayed, or the claim is not supported by the evidence.
* `INCONCLUSIVE` — required evidence is **absent** or unusable, so no opinion
  can be formed. **Missing is not a rejection.** A level whose supporting
  evidence is absent is reported as `INCONCLUSIVE`, not `NOT_ESTABLISHED`.

Precedence: **contradiction ⇒ REJECT; else absence ⇒ INCONCLUSIVE; else all
levels established ⇒ ATTRIBUTED_SUCCESS; else REJECT**
(`claim-not-supported-by-evidence`).

### 3.3 The two predeclared execution contracts

* **Strict (primary).** L5 requires `returncode == 0`.
* **Lenient (preregistered sensitivity variant).** L5 treats a parsed output as
  evidence of a successful execution even if the program later exited non-zero.

The variant is declared here, before execution, precisely so that it cannot be
selected after the fact. It affects **one** case (`A05_nonzero_exit_valid_output`).

---

## 4. Frozen case inventory

27 bundles, frozen in `s1_case_manifest.json` (generated by `s1_cases.py`).
The complete table — case id, family, program, seed, condition, mutation,
expected strict decision, expected lenient decision, expected cryptographic
success, ground truth, Stage01 analogue, derived-from — is machine-readable in
that file and is hashed into the integrity manifest.

* **Family A (8) — honest executions.** Correct ECDSA, correct ChaCha, wrong
  ECDSA answer, wrong ChaCha answer, non-zero exit with a valid answer,
  malformed stdout, empty stdout, and an honest C0 underdetermined abstention.
* **Family B (5) — evidence omission.** Missing observation, missing reference
  verdict, missing artifact record, missing program file, missing stdout entry.
* **Family C (12) — contradiction.** Producer digest mismatch, credited program
  not executed, submitted output not observed, context attempt conflict, target
  substitution, stale epoch, tampered signature, unauthorized signer,
  conflicting duplicate record, stale bundle digest, stale attempt, observation
  asserts an output the bundle lacks.
* **Family R (2) — replay.** Shared replay ledger (second evaluation of the
  same bundle against one consumed ledger), and a prior attempt's genuine
  observation replayed into a later attempt's bundle.

**Ground truth** is recorded per case as `expected.crypto_success` — whether
the *cryptographic predicate* is true — **separately** from the expected
verdict. A cryptographically true case that is rejected for a non-cryptographic
reason (A05) is therefore a **false rejection**, not a cryptographic failure.
Every metric below is computed against the declared ground truth with the
denominator stated.

---

## 5. Metrics, denominators, and uncertainty

Let `n = 27` bundles, of which `n_success = 14` have `crypto_success == true`
and `n_failure = 13` have `crypto_success == false`. (Exact counts are
recomputed from the frozen manifest and printed in the results; the
preregistration fixes the *rule*, and the frozen manifest fixes the numbers.)

For each contract, over the same bundle set:

* **False attribution (FA)** — `ATTRIBUTED_SUCCESS` on a `crypto_success == false`
  case. Denominator = `n_failure`. **Wilson 95% CI.**
* **Correct attribution (CA)** — `ATTRIBUTED_SUCCESS` on a `crypto_success == true`
  case. Denominator = `n_success`. Wilson 95% CI.
* **False rejection (FR)** — `REJECT` **or** `INCONCLUSIVE` on a
  `crypto_success == true` case. Denominator = `n_success`. Wilson 95% CI.
* **Correct rejection (CR)** — `REJECT` **or** `INCONCLUSIVE` on a
  `crypto_success == false` case. Denominator = `n_failure`. Wilson 95% CI.

`REJECT` and `INCONCLUSIVE` are **also** reported separately (a REJECT-to-
INCONCLUSIVE substitution is a classification-quality difference, not a
security difference), with an explicit per-case contingency table.

**No p-values.** These 27 bundles are a deliberately balanced characterisation
corpus, not a random sample of any population; a p-value would misrepresent
them. Wilson intervals are reported as descriptive precision only, and are
labelled as such.

**The frozen Stage01 pair** is reported in its own table with its own
denominator (number of cases with a direct analogue) and `N/A` elsewhere. Its
verdict vocabulary is binary (`ACCEPTED`/`REJECTED`); it has no INCONCLUSIVE
category, and that absence is itself a reported finding.

---

## 6. Controls

* **Positive control (operational).** A01 and A02 must yield
  `ATTRIBUTED_SUCCESS` under E3. If not, the experiment is **NOT OPERATIONAL**
  and no other result is reported.
* **Positive control (baseline).** The frozen Stage01 pair must ACCEPT at least
  one honest case. If it does not, the Stage01 comparison is **VOID** (it
  would be a strawman).
* **Negative controls.** Family A's cryptographically-false members (A03, A04,
  A06, A07, A08) must not be promoted by any contract that is claimed to bind
  the reference result.
* **Cross-implementation check.** The E3 reference verdict and the frozen
  Stage01 reference verdict are computed by the **same frozen predicate**
  (`contract_sound_stage01_reference_verifier_v2.py`). Any disagreement is a
  validity failure, not a reconcilable difference.
* **Claim-invariance control.** Two Stage01 certificates over byte-identical
  evidence files that differ only in `claims` are not constructed in this
  experiment; the equivalent control in the new contract is that the E3 verdict
  is a function of the *evidence*, not of the claims (the claims are not read
  by E3 at all — E3 recomputes them from the ladder).

---

## 7. Freeze and execution procedure

1. `s1_protocol.md` (this file) and `s1_deviations.md` are written.
2. `s1_case_manifest.json` is generated from `s1_cases.py` (frozen case table).
3. All component source is final.
4. `s1_freeze.py` writes `s1_integrity_manifest.json` covering: the protocol,
   the measurement runner, every component source file, the labels/expected
   outcomes, the trust material, and the case inventory.
5. The **audited** preflight `heb1_remediation_v1/integrity/manifest_verifier.py`
   verifies the manifest. **The run refuses to start if the preflight fails.**
6. The confirmatory pass is executed **once**. A component crash is recorded as
   the case outcome; it is not re-run with a patch.
7. The freeze manifest is **re-verified after execution**; a failure there is
   reported as a validity failure.
8. The report is written from the recomputed metrics only.

**Key custody.** The three Ed25519 private keys are generated fresh by
`protected_signing.generate_issuer` and stored **outside the repository** by
default (`/tmp/acts_s1_keystore`, or `$ACTS_S1_KEYSTORE`), because the
repository filesystem is `fuseblk` and reports every file as mode `0777`,
which the vetted `protected_signing.load_private_key` correctly refuses to
accept. Only the **public** bundle and the custody record live in the
repository. This is disclosed as a deviation from the "trust material inside
the frozen tree" ideal and as an environment limitation.

---

## 8. Declared threats to validity, before execution

1. **Constructed cases.** All 27 bundles are constructed. The C-family
   discriminates verifier capability; it does not establish reachability.
2. **Scripted producer.** No model call is made anywhere in this experiment.
   No AI-specificity claim is admissible.
3. **Residual TOCTOU.** The TEO hashes the program file immediately before
   `exec` and again immediately after. A write in the window between the hash
   and the `exec` is not excluded by hashing alone. (Mitigation: the file is
   re-hashed after execution and a difference is a contradiction. The window
   itself is not closed; a `memfd`-based execution, as used by the independent
   sibling tree `acts_next_phase_20261019_v2/stage1_e2a/e2a/observer.py`, would
   close it and is listed as a follow-up, not claimed here.)
4. **No namespace isolation.** The candidate runs without a network or mount
   namespace. The static source policy blocks the obvious primitives; this is
   policy, not isolation.
5. **In-memory replay ledger.** `context_validator.ReplayState` is not durable
   and not atomic across processes. It detects replay *within* one evaluation
   session, not across reboots.
6. **Not a production PKI.** The signing keys are local files; there is no
   transparency log, no revocation, no key rotation policy.
7. **Byte-identity contract.** Evidence identity is byte-identity of files. A
   semantic-equivalence contract (e.g. canonical JSON) would classify
   C10 ("stale bundle digest") differently.
8. **Baseline asymmetry.** E0–E3 and the Stage01 pair implement *different*
   contracts. The comparison measures contract coverage, not implementation
   quality.
9. **The frozen Stage01 pair is executed as a subprocess** with the public
   certificate on stdin, exactly as production invokes it; the reference
   verifier is invoked with a bundle on argv, exactly as the historical pilot
   invokes it. Its digests are pinned before and after the run.
10. **Balanced corpus.** The 27 bundles are not a population sample; rates are
    characterisation numbers for this corpus only.

---

## 9. Relationship to the research objectives and to prior art

* **Objective 1 (previously unknown mechanism):** foreclosed by prior art.
  RFC 9334 (RATS) §8.1 states that "Evidence needs to be securely associated
  with the Target Environment so that the Verifier cannot be tricked into
  accepting Claims originating from a different environment", and §12.3
  describes the confusion attack in which "a Verifier can be tricked into
  accepting Evidence coming from a past epoch as fresh". The mechanism family
  implemented here is therefore **known general principle (category A)**, and
  this experiment cannot support a novelty claim. The residual defensible
  contribution is **category C** (a measurement methodology and a reproducible
  corpus), and specifically the observation that RFC 9334's verdict is
  *binary* while the tri-state used here is not required by any identified
  prior standard — a narrow, not-yet-established distinction.
* **Objective 2 (reachable exploit):** not addressed by this experiment.
* **Objective 3 (advantage over real provenance implementations):** not
  addressed by this experiment. E0–E2 are design classes; the real-product
  comparison is Stage 2 and requires user approval before any installation.
* **Objective 4 (trustworthy end-to-end attribution):** this experiment is the
  core of Objective 4. Its success criterion: *the new evaluator justifies an
  attributed completion claim only when the complete required causal and
  cryptographic evidence chain supports it.* The predeclared test of that
  criterion is: **zero false attributions and zero false rejections on the
  frozen corpus**, plus the H4 capability gap against the frozen Stage01 pair.

---

## 10. Frozen artefacts

| Artefact | Path | Role |
|---|---|---|
| This protocol | `s1_protocol.md` | preregistration |
| Deviations log | `s1_deviations.md` | all post-hoc changes, logged |
| Case manifest | `s1_case_manifest.json` | frozen case table + expected outcomes |
| Integrity manifest | `s1_integrity_manifest.json` | preflight contract |
| Trust custody record | `trust/KEY_CUSTODY.json` | key ids, modes, holders (no private material) |
| Public trust bundle | `trust/public_bundle.json` | issuer roles + public keys |
| Confirmatory results | `runs/results.json` | raw per-case outcomes |
| Recomputed summary | `runs/summary.md`, `runs/summary.json` | metrics, recomputed from raw |
| Test suite | `test_s1_attribution.py` | component and property tests |
