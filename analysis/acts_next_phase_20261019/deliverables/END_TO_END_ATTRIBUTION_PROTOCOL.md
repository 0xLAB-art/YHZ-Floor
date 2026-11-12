# End-to-End Attribution (TOEEA-1) — Frozen Protocol

**Status: FROZEN BEFORE EXECUTION.** The canonical, hash-pinned protocol is `sp2027/analysis/acts_next_phase_20261019/stage1_attribution/s1_protocol.md`, declared in the integrity manifest `s1_integrity_manifest.json` as the `protocol` component and verified by the audited `heb1_remediation_v1/integrity/manifest_verifier.py` (77 files checked, 0 errors, before **and** after the run). This document is a faithful consolidation of it; where they differ, **the frozen file governs**.

---

## 1. Scope, authorisation, and explicit non-claims

* **Local, offline, authorised, constructed evaluation experiment.** No network request to any third party. No model or provider call. No package installed. No historical file modified, reset, cleaned, amended or committed.
* **NOT** an exploit against a deployed security service.
* **NOT** a live-campaign result.
* **NOT** evidence of deployed attacker reachability.
* **NOT** a novelty claim. The mechanism implemented here is specified normatively in RFC 9334, in-toto, SLSA, TUF and Sigstore. See `NOVELTY_PRIOR_ART_MATRIX.md`.
* **NOT** an AI-specific result. The producer arm is **scripted**.
* The contradiction and replay cases are **synthetic contradiction-detection fixtures**. They demonstrate discrimination, not reachability.

## 2. Research question

> Under one declared contract, on one frozen bundle corpus, how many ground-truth non-success bundles does each evaluation contract permit to be **promoted to an attributed success claim**, and how many ground-truth successes does it **incorrectly reject**?

## 3. Hypotheses (declared before execution)

| ID | Hypothesis | Decision rule |
|---|---|---|
| **H1** | *Causal binding.* A contract that performs the cross-record causal joins admits a **strict subset** of the false attributions admitted by a contract that only checks digests, signatures and context. | The false-attribution count must be monotonically non-increasing across the contract ladder E0 → E1 → E2 → E3. |
| **H2** | *Non-regression.* The additional layers do not cause false rejections of honest successes. | E3 false rejections of the ground-truth successes must be 0. |
| **H3** | *Tri-state adjudication.* Absent evidence is classified INCONCLUSIVE, distinct from contradictory evidence, which is REJECT. | All omission-family cases must be INCONCLUSIVE under E3. |
| **H4** | *Baseline capability gap.* The frozen historical Stage01 pair accepts a bundle whose credited program was never executed, or whose credited output was never observed, because the Stage01 certificate format carries no program-digest or output-digest field. | The Stage01 pair must ACCEPT the C02 and C03 bundles, and must ACCEPT at least one honest case (baseline positive control — otherwise the comparison is VOID). |
| **H0** | *Null.* None of the above holds. | — |

**No metric, threshold, denominator, decision rule, case expectation or hypothesis was changed after the confirmatory run began.** The one post-hoc addition (a second metric set) is disclosed as deviation **D-06** and is reported *alongside*, not instead of, the preregistered metric.

## 4. The four contracts

| Contract | Digests | Signatures + role/kind | Signed context + replay + path confinement | Cross-record joins | Tri-state |
|---|---|---|---|---|---|
| **E0 `digest_only`** | ✔ | ✘ | ✘ | ✘ | ✔ |
| **E1 `signed_digest_only`** | ✔ | ✔ | ✘ | ✘ | ✔ |
| **E2 `signed_context_only`** | ✔ | ✔ | ✔ | ✘ | ✔ |
| **E3 `full`** | ✔ | ✔ | ✔ | ✔ | ✔ |

E0–E2 are **design classes** and are labelled as such in every table. They are not in-toto, SLSA, or any other product.

**The cross-record joins performed by E3** (each is a *contradiction* when violated):

1. producer's signed `program_sha256` == digest of the submitted program file;
2. observer's signed `program_source_sha256` == digest of the submitted program file *(the program the observer actually executed)*;
3. observer's signed `program_source_sha256_after` == the same digest *(no in-place modification during execution)*;
4. observer's signed `output_file_sha256` == digest of the submitted output artifact;
5. observer's signed `stdout_sha256` == digest of the submitted captured stdout;
6. reference verdict's signed `stdout_sha256` == the same digest *(the verdict is bound to the observed bytes, not to an unreferenced file)*;
7. reference verdict's signed `target_state_sha256` == the harness's target-state digest;
8. observer's signed `input_sha256` == the harness's input digest;
9. observer's signed `stdin_sha256` == `input_sha256` *(the bytes delivered were the bytes hashed)*;
10. attempt_id agrees across the producer, observer and reference records;
11. the submitted output artifact is **re-derived** as the `json-last-line-v1` parse of the captured stdout.

## 5. The evidence chain — 15 required objects

Producer identity · exact program source bytes + SHA-256 · exact executed program bytes · invocation command and arguments · execution environment identity and version · input / public-instance digest · target identity and state digest · attempt/session identity and epoch · captured stdout and stderr · parsed candidate output and its digest · trusted execution-observer record · independent cryptographic reference result · signed evidence with explicit issuer identity and role · aggregated certificate · final attributed success claim.

**The trusted component is the Trusted Execution Observer (TEO).** No link in the chain is a digest supplied by the untrusted producer. The TEO holds its own Ed25519 private key, generated fresh at setup time, never exposed to the producer, and stored outside the repository (deviation D-05: the repository filesystem ignores `chmod`, and the vetted `protected_signing.load_private_key` correctly refuses such a key).

## 6. Claim ladder and tri-state vocabulary

| Level | Established when |
|---|---|
| L1 `artifact_authorship` | the producer record verifies **and** its program digest equals the submitted program file's digest |
| L2 `execution_identity` | the observer record verifies **and** its program digest equals the submitted program file's digest **and** the program was not modified **and** the input digest matches the expectation |
| L3 `target_effect` | the reference verdict verifies, the predicate is true, **and** the verdict is bound to the observed stdout |
| L4 `reference_oracle_acceptance` | as L3, with `verdict == ACCEPTED` |
| L5 `boundary_enforcement` | the observer record verifies, the boundary was enforced, the source policy passed, the output parsed, **and** (strict contract) the return code was 0 |
| L6 `attribution` | L1 ∧ L2 ∧ L3 ∧ L4 ∧ L5 |

**Decision vocabulary and precedence:**

* `ATTRIBUTED_SUCCESS` — every level established.
* `REJECT` — the evidence is present but contradictory, unauthorised, out of date, or the claim is unsupported. Includes a consumed replay slot (positive proof of contradiction).
* `INCONCLUSIVE` — required evidence is **absent or unusable**, so no opinion can be formed. Deliberately **not** a rejection.

**Precedence: any contradiction ⇒ REJECT; else any absence ⇒ INCONCLUSIVE; else all levels established ⇒ ATTRIBUTED_SUCCESS; else REJECT** (`claim-not-supported-by-evidence`).

## 7. The two predeclared execution contracts

* **Strict (primary).** The observed execution must have terminated with return code 0 for L5 to be established.
* **Lenient (sensitivity).** A parsed output is taken as evidence of a successful execution even if the program exits non-zero afterwards.

Both were declared before execution. Exactly one case (A05) is sensitive to the choice; that is why the variant was declared in advance.

## 8. The frozen corpus

27 cases; 56 materialised inventory files; frozen table in `s1_case_manifest.json`.

* **Family A (8)** — honest executions: A01 correct ECDSA, A02 correct ChaCha, A03 wrong ECDSA answer, A04 wrong ChaCha answer, A05 non-zero exit with a cryptographically correct answer, A06 malformed stdout, A07 empty stdout, A08 C0 underdetermined instance.
* **Family B (5)** — omission: B01 missing observation, B02 missing reference verdict, B03 missing artifact record, B04 missing program source file, B05 missing stdout entry.
* **Family C (12)** — contradiction: C01 producer digest mismatch, C02 credited program not executed, C03 submitted output not observed, C04 context attempt conflict, C05 target substitution, C06 stale epoch, C07 tampered signature, C08 unauthorised signer, C09 conflicting duplicate record, C10 stale bundle digest, C11 stale attempt, C12 observation asserts an output the bundle lacks.
* **Family R (2)** — R01 replay against a shared ledger, R02 a prior attempt's real observation replayed.

Ground truth is recorded **twice** per case — `expected_decision` (correctly attributable success?) and `expected_crypto_success` (cryptographic predicate true?) — and the two are never conflated.

## 9. Metrics, denominators, and inference

* Primary metric: **false attribution** = ATTRIBUTED_SUCCESS on a ground-truth non-success (denominator 25); **false rejection** = REJECT/INCONCLUSIVE on a ground-truth success (denominator 2); **correct attribution** (denominator 2); **correct rejection** (denominator 25).
* Secondary: the family decomposition (A = 8, B = 5, C+R = 14) and the frozen Stage01 table (13 applicable, 14 N/A).
* **Wilson 95 % confidence intervals** on every rate.
* **No p-values.** The corpus is a balanced, constructed set, not a random sample; the cases characterise discrimination, they do not estimate population prevalence.
* The Stage01 comparison is reported over the **applicable subset only**; N/A cases are counted in neither direction. A functionality mismatch is not a security failure.

## 10. Controls

1. Positive control — the honest successes must be attributed (else NOT OPERATIONAL).
2. Baseline positive control — the Stage01 pair must accept ≥ 1 honest case (else the comparison is VOID).
3. Cross-implementation predicate check — the new reference verifier's predicate must agree with the frozen `ecdsa_valid` (disagreement is a validity failure, not a silent reconciliation).
4. Source-policy equivalence — the new observer's policy must agree with a literal transcription of the historical `safe_source` (7 parametrised sources).
5. Manifest preflight fail-closed — a tampered manifest must be rejected.
6. Replay control — a second evaluation against a shared ledger must be REJECTed.
7. Missing-evidence control — must be INCONCLUSIVE, not REJECTed.
8. Digest-pin control — a tampered frozen component must abort the load.

## 11. Freeze-and-execute procedure (as executed)

1. Write the protocol. 2. Write the case inventory and the case table. 3. Write the evaluator, runner, adjudicator, and metric code. 4. Write the integrity manifest in the audited `acts-integrity-remediation/1` schema, covering the protocol, the runner, every component, the labels, the trust material, and the complete case inventory. 5. Run the **audited** preflight — fail-closed; the run refuses to start if it fails. 6. Execute **once**. 7. Recompute the metrics from the raw artefacts only. 8. **Re-verify the freeze manifest after execution.** No re-runs with a modified configuration; a component crash is recorded as the case outcome.

## 12. Declared threats to validity

1. Constructed cases; 2. balanced design — characterisation, not prevalence; 3. small denominator (n_success = 2) ⇒ wide intervals; 4. byte-identity artifact identity; 5. residual TOCTOU between hashing and executing the program file; 6. no kernel-level namespace isolation — the boundary is a declared and tested policy, not an enforced sandbox; 7. in-memory, non-durable, non-atomic replay ledger; 8. not a production PKI (no transparency log, revocation, rotation, epoch lifecycle); 9. scripted producer arm — no AI inference; 10. baseline asymmetry — E3 and Stage01 do not implement the same contract, and the measured difference is a difference in contract coverage.

## 13. Relationship to the four objectives

* **Objective 1** — foreclosed by prior art *independently of any outcome of this experiment*; the results here are inadmissible as support for it.
* **Objective 2** — not addressed; see `stage3_boundary/STAGE3_BOUNDARY_ANALYSIS.md`.
* **Objective 3** — not addressed here; E0–E2 are design classes, not products. See `REAL_PROVENANCE_BASELINE_COMPARISON.md`.
* **Objective 4** — this experiment is the attempt.
