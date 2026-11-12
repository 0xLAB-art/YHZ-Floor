# End-to-End Attribution (TOEEA-1) — Confirmatory Results

**Experiment:** Stage 1 of the ACTS-Attack next phase.
**Protocol (frozen before execution):** `sp2027/analysis/acts_next_phase_20261019/stage1_attribution/s1_protocol.md`
**Deviations log:** `…/stage1_attribution/s1_deviations.md`
**Integrity manifest (audited):** `…/stage1_attribution/s1_integrity_manifest.json` — schema `acts-integrity-remediation/1`, verified by the **unmodified** `heb1_remediation_v1/integrity/manifest_verifier.py`
**Raw results:** `…/stage1_attribution/runs/results.json` — schema `acts-next-phase/s1-results/1`
**Recomputed metrics:** `…/stage1_attribution/runs/summary.md`, `runs/summary.json` (produced by `s1_metrics.py`, which performs **no measurement**)

---

## 0. Scope and non-claims (read before the numbers)

This is a **local, offline, authorised, constructed evaluation experiment**. It is:

* **NOT** an exploit against a deployed security service;
* **NOT** a live-campaign result;
* **NOT** evidence of deployed attacker reachability;
* **NOT** a novelty claim — the mechanism it implements is specified normatively in RFC 9334, in-toto, SLSA, TUF and Sigstore (see `NOVELTY_PRIOR_ART_MATRIX.md`);
* **NOT** an AI-specific result — the producer arm is **scripted**, not a model.

The contradiction-family cases (C01–C12) and the replay cases (R01–R02) are **synthetic contradiction-detection fixtures**. They establish that a given contract *can* discriminate a condition. They do **not** establish that an attacker can cause that condition in the ACTS-Attack pipeline. Reachability is a separate question, answered separately in §7 and in `stage3_boundary/`.

## 1. What was built

A new, separately versioned evaluation stack, in which the trusted component is a **Trusted Execution Observer (TEO)** that holds its own Ed25519 key and signs what it read — never what the producer asserted.

| Object | Who produces it | Bound by |
|---|---|---|
| Program source bytes | producer | TEO pre/post-exec digest; producer's signed `artifact_record` |
| Exact executed bytes | TEO | TEO-signed `program_source_sha256` (+ `_after`, to detect self-modification) |
| Invocation / environment | TEO | TEO-signed `argv`, `env_sha256`, `cwd` |
| Input / public-instance digest | TEO | TEO-signed `input_sha256` **and** `stdin_sha256`; the evaluator checks the two agree |
| Captured stdout / stderr | TEO | TEO-signed digests; the reference verifier consumes the *stdout file* whose digest the TEO signed |
| Parsed output artifact | TEO writes it, from its own capture | TEO-signed `output_file_sha256`; the evaluator **re-derives** the parse from the captured stdout |
| Target identity / state digest | harness | the evaluator's `RunExpectation`, supplied by the *party running the evaluation*, not by the bundle |
| Attempt / session / epoch | harness | signed 6-field context, exactly compared to the expectation |
| Independent cryptographic verdict | reference verifier (its own key) | signed `reference_verdict` bound to `stdout_sha256` and `target_state_sha256` |
| Signed evidence with issuer identity and role | three distinct roles | `protected_signing` (Ed25519, role/kind/domain authorised) + `context_validator` (exact binding, replay ledger, path confinement) |
| Aggregated certificate | the bundle | digest-indexed; every declared file verified |
| Final attributed-success claim | the adjudicator | tri-state, six-level ladder |

The **cryptographic predicate is not re-implemented**: the new reference verifier imports the **frozen** `contract_sound_stage01_reference_verifier_v2.py` (hash-pinned at load time, fail-closed). The new source policy is a verbatim reproduction of the historical `safe_source` and is **tested for equivalence** against a literal transcription in the unit suite.

## 2. The four contracts compared (all on the *same* bundle set)

| Contract | Verifies file digests | Verifies record signatures + role/kind | Verifies signed context, replay ledger, path confinement | Performs cross-record causal joins | Tri-state |
|---|---|---|---|---|---|
| **E0 `digest_only`** | yes | no | no | no | yes |
| **E1 `signed_digest_only`** | yes | yes | no | no | yes |
| **E2 `signed_context_only`** | yes | yes | yes | **no** | yes |
| **E3 `full`** | yes | yes | yes | **yes** | yes |

E0–E2 are **design classes**, labelled as such everywhere. They are *not* in-toto, SLSA, or any other product. They exist to isolate which layer contributes what. The *frozen historical Stage01 pair* is a separate, genuine baseline (§6).

E3 is evaluated under two **predeclared** execution contracts: **strict** (primary — the observed execution must have returned 0) and **lenient** (sensitivity — a parsed output counts as a successful execution even if the program then exited non-zero). The lenient variant exists because exactly one case (A05) is sensitive to it; it was declared in advance precisely so the choice could not be made after seeing the outcome.

## 3. The corpus

27 cases, frozen in `s1_case_manifest.json` before execution, materialised as 56 files under `s1_case_inventory/`:

* **Family A (8)** — honest executions: two correct solutions, two wrong answers, a non-zero exit that nevertheless produced a *cryptographically correct* answer, malformed stdout, empty stdout, and a C0 underdetermined instance.
* **Family B (5)** — **omission**: each removes one required piece of evidence.
* **Family C (12)** — **contradiction**: producer digest mismatch, credited program not executed, submitted output not observed, context attempt conflict, target substitution, stale epoch, tampered signature, unauthorised signer, conflicting duplicate record, stale bundle digest, stale attempt, observation asserts an output the bundle lacks.
* **Family R (2)** — replay against a shared ledger, and a prior attempt's *real* observation replayed into a later attempt.

Ground truth is recorded twice per case and the two are kept distinct: `expected_decision` (is this bundle a correctly attributable success?) and `expected_crypto_success` (is the cryptographic predicate true on the presented output?). They differ for the whole contradiction family, and conflating them is exactly the error the multi-agent re-audit warned about.

## 4. Results

### 4.1 Primary metric — attribution ground truth (n_success = 2, n_non_success = 25)

| contract | false attribution | Wilson 95 % CI | correct attribution | false rejection | Wilson 95 % CI | correct rejection |
|---|---|---|---|---|---|---|
| `digest_only` | **13/25** | [0.335, 0.700] | 2/2 | 0/2 | [0.000, 0.658] | 12/25 |
| `signed_digest_only` | **11/25** | [0.267, 0.629] | 2/2 | 0/2 | [0.000, 0.658] | 14/25 |
| `signed_context_only` | **6/25** | [0.115, 0.434] | 2/2 | 0/2 | [0.000, 0.658] | 19/25 |
| **`full` (strict)** | **0/25** | [0.000, 0.133] | 2/2 | **0/2** | [0.000, 0.658] | **25/25** |
| `full_lenient` | 1/25 (`A05` only) | [0.007, 0.195] | 2/2 | 0/2 | [0.000, 0.658] | 24/25 |

### 4.2 Family decomposition

| contract | A: success attributed (of 2) | A: non-success promoted (of 6) | B: INCONCLUSIVE (of 5) | B: REJECT (of 5) | C+R: detected as REJECT (of 14) |
|---|---|---|---|---|---|
| `digest_only` | 2/2 | 1 | 5/5 | 0/5 | **2/14** |
| `signed_digest_only` | 2/2 | 1 | 5/5 | 0/5 | **4/14** |
| `signed_context_only` | 2/2 | 1 | 5/5 | 0/5 | **9/14** |
| `full` | 2/2 | **0** | 5/5 | 0/5 | **14/14** |
| `full_lenient` | 2/2 | 1 | 5/5 | 0/5 | 14/14 |

### 4.3 The preregistered metric (SET 1) and its caveat

SET 1 measures false attribution against `expected_crypto_success` (n = 21 true, 6 false):

| contract | false attribution | false rejection |
|---|---|---|
| `digest_only` | 1/6 | 7/21 |
| `signed_digest_only` | 1/6 | 9/21 |
| `signed_context_only` | 1/6 | 14/21 |
| `full` | 0/6 | 19/21 |
| `full_lenient` | 0/6 | 18/21 |

**Material caveat (deviation D-06).** For the contradiction family the cryptographic predicate is true *by construction* — the contradiction lies elsewhere (the credited program was not the executed one, the output was never observed, the signature was tampered) — while the correct decision for those cases is REJECT. SET 1's "false rejection" column therefore counts E3's **correct** rejections as false rejections. SET 1 is reported because it is preregistered; SET 2 is the interpretable one and was added post-hoc. **No metric, threshold, denominator, decision rule or case expectation was changed after the confirmatory run began.**

### 4.4 Hypothesis outcomes

| Hypothesis | Preregistered statement | Outcome | Evidence |
|---|---|---|---|
| **H1** causal binding | adding the cross-record joins strictly reduces false attribution relative to the no-join contracts | **SUPPORTED** | 13 → 11 → 6 → **0** across E0 → E1 → E2 → E3, monotone |
| **H2** non-regression | the added layers do not cause false rejections of honest successes | **SUPPORTED** | 0/2 false rejections for E3, both contracts |
| **H3** tri-state | absent evidence is classified INCONCLUSIVE, not REJECT | **SUPPORTED** | 5/5 on the omission family; the frozen Stage01 pair has **no** INCONCLUSIVE category and rejected both omission cases it could express |
| **H4** baseline capability gap | the frozen Stage01 pair accepts a bundle whose credited program was never executed, or whose credited output was never observed | **SUPPORTED** | Stage01 ACCEPTED on `C02` and `C03`; E3 rejected both; the baseline accepted 2/2 honest successes (positive control) |

### 4.5 Controls

| Control | Result |
|---|---|
| Positive control (6 honest successes must be attributed) | E3 attributes 2/2 |
| Baseline positive control (the Stage01 pair must accept ≥ 1 honest case) | ACCEPTED 2/2 — **the baseline is not a strawman** |
| Cross-implementation predicate check (new verifier vs frozen `ecdsa_valid`) | agree |
| Source-policy equivalence (new observer vs literal transcription of the historical `safe_source`, 7 parametrised sources) | agree |
| Manifest preflight fail-closed (tampered manifest) | correctly rejected |
| Replay control (second evaluation against a shared ledger) | REJECT, `context-replay-exceeded` |
| Missing-evidence control | INCONCLUSIVE, **not** REJECT |
| Observer control (policy-violating program) | refused, not executed |
| Digest-pin control (tampered frozen component) | `RuntimeError: digest changed` |

## 5. The two headline cases

**`C02_credited_program_not_executed`.** The observer executed program P1 and captured a correct output O1. The bundle presents program **P2** (a different program, built against the same instance), a producer record re-signed for P2, and the *unchanged* output O1. The output join passes; the program join fails (`observation.program_source_sha256` = digest(P1) ≠ digest(P2)). The **frozen Stage01 pair ACCEPTS** the bundle: its `agent_artifact` is P2, its candidate is O1, its reference verdict is ACCEPTED, its consistency checks pass. The certificate therefore asserts `artifact_authorship = PROVEN` and `execution_identity = PROVEN` for a program that was never executed. E3 rejects it.

**`C03_submitted_output_not_observed`.** The observer executed program P1 and captured a *wrong* output O1. The bundle presents P1, but the output file is **O2** — a different, cryptographically *correct* output obtained from a different run — with the bundle digest updated to O2 and a fresh reference verdict computed over O2 (ACCEPTED). The **frozen Stage01 pair ACCEPTS**: the credited output could not have been produced by the credited program. E3 rejects it, because the TEO-signed output digest does not match the submitted bytes.

Both are **synthetic** fixtures, and neither is presented as a live exploit. What they establish is a **component-level capability gap in a real, frozen, deployed component**, demonstrated on a real execution, and that gap is the correct and honest form of the Stage 1 result.

## 6. The frozen Stage01 baseline, precisely

13 of 27 cases have a direct Stage01 analogue; the other 14 are **N/A** and are counted in neither direction (a functionality mismatch is not a security failure).

| case | Stage01 final | E3 | ground truth |
|---|---|---|---|
| A01_ecdsa_correct | **ACCEPTED** | ATTRIBUTED_SUCCESS | ATTRIBUTED_SUCCESS |
| A02_chacha_correct | **ACCEPTED** | ATTRIBUTED_SUCCESS | ATTRIBUTED_SUCCESS |
| A03_ecdsa_wrong_answer | REJECTED | REJECT | REJECT |
| A04_chacha_wrong_answer | REJECTED | REJECT | REJECT |
| A05_nonzero_exit_valid_output | REJECTED | REJECT | REJECT |
| A06_malformed_stdout | REJECTED | REJECT | REJECT |
| A07_empty_stdout | REJECTED | REJECT | REJECT |
| A08_underdetermined_c0 | REJECTED | REJECT | REJECT |
| B01_missing_observation | REJECTED | INCONCLUSIVE | INCONCLUSIVE |
| B04_missing_program_source_file | REJECTED | INCONCLUSIVE | INCONCLUSIVE |
| C01_producer_digest_mismatch | REJECTED | REJECT | REJECT |
| **C02_credited_program_not_executed** | **ACCEPTED** | REJECT | REJECT |
| **C03_submitted_output_not_observed** | **ACCEPTED** | REJECT | REJECT |

**Stage01 false attributions = 2/25.** The Stage01 pair also has **no INCONCLUSIVE** verdict: it rejects the two omission cases it can express, which is a classification-quality difference, not a false-attribution difference.

## 7. Contract sensitivity (one case, declared in advance)

`A05_nonzero_exit_valid_output` is the only contract-sensitive case. The program prints a *cryptographically correct* answer and then exits 3.

* Under the **strict** contract (primary): E3 REJECTs it, because a non-zero exit means the execution did not complete inside the declared boundary. The frozen Stage01 pair also rejects it.
* Under the **lenient** contract (sensitivity): E3 attributes it, and so do E0–E2.

This is a genuine, honest demonstration that the strict/lenient boundary is a *contract choice*, not a free parameter, and that E3's rejection of A05 is a consequence of the declared strict contract rather than of a hidden heuristic. It is the only case where the two contracts differ.

## 8. Limitations (binding on any downstream claim)

1. **Constructed cases.** The corpus is balanced by design. It is a **characterisation of discrimination, not a population rate**, and no population prevalence is claimed.
2. **Small denominator.** n_success = 2. The Wilson intervals are wide; the false-attribution difference between E0 (13/25) and E3 (0/25) is large and directionally unambiguous, but the estimate of E3's *true* false-attribution rate is only bounded above by 13.3 % (95 %).
3. **Byte-identity contract.** Artifact identity is byte identity. A semantic-equivalence contract would produce different numbers.
4. **Residual TOCTOU.** The observer hashes the program file, then executes it from that path. A concurrent modification between the two is not excluded (the post-exec digest catches in-place modification, not a swap-and-restore race). The concurrent sibling tree's `memfd` observer removes this window; it was not adopted here because that tree is not ours and was not executed.
5. **No namespace isolation.** The observer sets a minimal environment and uses `python -I`, but there is no network namespace; the historical static source policy is a *declaration* of the boundary, and its enforcement was verified by test, not by kernel-level isolation.
6. **In-memory replay ledger.** `context_validator.ReplayState` is not durable and not atomic across processes.
7. **Not a production PKI.** The three roles use fresh Ed25519 keys with a public bundle; there is no transparency log, revocation, key rotation, or epoch lifecycle.
8. **The producer arm is scripted.** No AI-specific claim is possible from this experiment.
9. **Single run.** The confirmatory pass was executed once. A component crash is recorded as the case outcome; nothing was re-run with a patched configuration.
10. **Baseline asymmetry.** E3 and the Stage01 pair do **not** implement the same contract; the difference measured is a difference in *contract coverage*, not a controlled A/B of one contract. Each evaluator was given its best-case valid input on every case, so the Stage01 pair was never handicapped by malformed input.

## 9. Reproduce

```
cd sp2027/analysis/acts_next_phase_20261019/stage1_attribution
python3 -m pytest -q test_s1_attribution.py     # 17 passed
python3 s1_make_cases.py                        # materialise the frozen corpus
python3 s1_freeze.py && python3 s1_freeze.py --verify
rm -rf work runs && python3 s1_runner.py         # refuses to start unless preflight passes
python3 s1_metrics.py                           # recomputation only
```

## 10. Determination for Objective 4

**Objective 4 — build and experimentally validate trustworthy end-to-end attribution across program source → execution → runtime output → cryptographic reference verification → evidence → final security claim.**

> **ESTABLISHED (on the frozen corpus, within the stated scope).**

Evidence: 0/25 false attributions, 0/2 false rejections, 25/25 correct rejections, 5/5 correct INCONCLUSIVE classifications, a genuine trusted execution observer with a key the producer never holds, a reference verifier bound to the observer's signed stdout capture, an audited fail-closed integrity preflight that gates the run, and an independent recomputation of every metric from raw artefacts.

Limitations: the scope is the frozen 27-case corpus; the corpus is balanced and constructed; byte-identity artifact identity; residual TOCTOU; no kernel isolation; in-memory replay ledger; no AI producer arm; one run.
