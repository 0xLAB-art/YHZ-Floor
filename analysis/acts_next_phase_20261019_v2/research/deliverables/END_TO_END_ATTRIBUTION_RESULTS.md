# Stage 1 — End-to-End Attribution Results

**Project:** ACTS-Attack  
**Stage:** Stage 1 — Genuine End-to-End Attribution  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/`  
**Date:** 2026-10-20  
**Status:** COMPLETE (confirmatory run executed)

---

## 1. Executive Summary

A single frozen, preregistered confirmatory run was executed against 22 test cases covering honest controls, cryptographic failures, malformed controls, missing-evidence controls, and attack variants (identity swap, output swap, stale attempt, context conflict, replay, reference mismatch).

**Headline result:** 0 false negatives, 0 false positives across all 22 cases. All 6 honest successful cases were attributed as success; all 12 negative controls were rejected or inconclusive (no attack succeeded).

No model calls, no network calls, no provider calls were made. The experiment ran entirely offline and locally.

---

## 2. Experimental Setup

### 2.1 Frozen Artifacts

All components, cases, labels, trust material, and the integrity manifest were frozen via `e2a.prepare` and verified fail-closed by the audited remediation preflight component (`heb1_remediation_v1/integrity/manifest_verifier.py`) before execution.

| Artifact | Path | Notes |
|----------|------|-------|
| Integrity manifest | `E2A_FREEZE.json` | Schema `acts-integrity-remediation/1`; verified by audited verifier |
| Case inventory (22 cases) | `frozen/case_index.json` | Schema `e2a-case-index/1` |
| Labels table | `frozen/labels.json` | — |
| Trust policy | `frozen/trust_policy.json` | Issuer policy with 3 Ed25519 roles |
| Issuer public bundle | `frozen/issuers_public.json` | 3 fresh random Ed25519 keys (not derived from session IDs) |
| Preflight report | `preflight_report_prestage.json` | 38 files checked, 0 errors |

### 2.2 Components Under Test

| Component | Role | Status |
|-----------|------|--------|
| `canonical` | Canonical constants & serialization | Frozen |
| `remediation` | Signed context, replay ledger, manifest verifier, protected signing | Frozen audited component |
| `producers` | Scripted producer source generation | Frozen |
| `observer` | Trusted execution observer (TEO) | Frozen |
| `reference` | Trusted reference adjudicator | Frozen |
| `aggregator` | Final attribution decision | Frozen |
| `baseline` | Stage 01 certificate builder + frozen validator/reference | Frozen |
| `cases` | Case definitions | Frozen |
| `truth` | Ground truth labels | Frozen |
| `adjudicate` | Adjudication logic | Frozen |
| `prepare` | Pre-execution preparation | Frozen |

### 2.3 Trusted Execution Observer

The TEO is the component trusted to observe execution. It:
- Executes the candidate program from an in-memory memfd (exact bytes hashed)
- Captures stdout/stderr/returncode
- Parses candidate output (strict: exactly one non-empty JSON object line)
- Signs the six-field context (attempt_id, domain, epoch, kind, role, target_id) with the issuer's Ed25519 key
- Produces a signed observation envelope (`e2a-signed-record/1`)

### 2.4 Case Classes

| Class | Count | Description |
|-------|-------|-------------|
| H_OK (honest success) | 6 | Correct execution, valid crypto predicate |
| H_BAD / H_FAIL (honest failure) | 5 | Incorrect crypto / execution failure |
| H_MALFORMED | 1 | Malformed output |
| H_UNDET | 1 | Undetermined |
| M_MISSING (missing evidence) | 2 | Missing observation / missing reference |
| X_ (attack variants) | 6 | Identity swap, output swap, stale attempt, context conflict, replay, reference mismatch |

---

## 3. Results

### 3.1 Decision Summary

| Decision | Count | Cases |
|----------|-------|-------|
| ATTRIBUTED_SUCCESS | 6 | H_OK_EC_01, H_OK_EC_02, H_OK_EC_03, H_OK_CH_01, H_OK_CH_02, H_OK_CH_03 |
| REJECT | 12 | All negative controls (cryptographic failures, malformed, attacks) |
| INCONCLUSIVE | 4 | Missing evidence (M_MISSING_OBS, M_MISSING_REF), context binding issues (X_STALE_ATTEMPT, X_CONTEXT_CONFLICT) |
| **False Negatives** | **0** | — |
| **False Positives** | **0** | — |

### 3.2 Case-Level Results

| Case ID | Ground Truth | Decision | Reason | Correct? |
|---------|-------------|----------|--------|----------|
| H_OK_EC_01 | True | ATTRIBUTED_SUCCESS | predicate-true-and-chain-complete | YES |
| H_OK_EC_02 | True | ATTRIBUTED_SUCCESS | predicate-true-and-chain-complete | YES |
| H_OK_EC_03 | True | ATTRIBUTED_SUCCESS | predicate-true-and-chain-complete | YES |
| H_OK_CH_01 | True | ATTRIBUTED_SUCCESS | predicate-true-and-chain-complete | YES |
| H_OK_CH_02 | True | ATTRIBUTED_SUCCESS | predicate-true-and-chain-complete | YES |
| H_OK_CH_03 | True | ATTRIBUTED_SUCCESS | predicate-true-and-chain-complete | YES |
| H_BAD_EC_01 | False | REJECT | cryptographic-predicate-false | YES |
| H_FAIL_EC_01 | False | REJECT | candidate-output-substitution | YES |
| H_MALFORMED_EC_01 | False | REJECT | candidate-output-substitution | YES |
| M_MISSING_OBS | False | INCONCLUSIVE | evidence-record-missing | YES |
| X_IDENTITY | False | REJECT | executed-program-identity-mismatch | YES |
| X_OUTPUT_SWAP | False | REJECT | candidate-output-substitution | YES |
| X_STALE_ATTEMPT | False | INCONCLUSIVE | observation-context-binding | YES |
| X_CONTEXT_CONFLICT | False | INCONCLUSIVE | observation-context-binding | YES |
| X_REPLAY | False | REJECT | observation-replayed | YES |
| X_REF_MISMATCH | False | REJECT | reference-does-not-adjudicate-this-observation | YES |

*(Remaining cases: H_BAD_CH_01, H_BAD_CH_02, H_FAIL_CH_01, H_UNDET_EC_01 — see raw_results.jsonl for full detail.)*

### 3.3 Control Evaluation

**Positive controls (honest success, gt=True):** 6/6 correctly attributed as ATTRIBUTED_SUCCESS. The harness accepts genuine success.

**Negative controls:**
- Cryptographic failures: REJECT (cryptographic predicate not satisfied)
- Malformed/missing output: REJECT or INCONCLUSIVE (never falsely promoted)
- Missing observation/reference: INCONCLUSIVE (missing evidence is not counted as zero failure, per audit correction)
- Attack variants: REJECT or INCONCLUSIVE (no attack achieved ATTRIBUTED_SUCCESS)

---

## 4. Integrity

| Check | Result |
|-------|--------|
| Preflight fail-closed verification | PASSED (38 files, 0 errors) |
| Manifest schema | `acts-integrity-remediation/1` (verified) |
| Component hashes pinned | All components hash-pinned in E2A_FREEZE.json |
| No model/network calls | 0 model, 0 network, 0 provider calls |
| Raw results preserved | `raw_results.jsonl` with SHA-256 `49e3ee28e206b0175826996f56d02cc09f0def7e552ede5f98c62f3e2d068a69` |
| Every case preserved | All 22 cases retained, including unfavorable outcomes |

---

## 5. Limitations

1. This is a local, scripted-producer experiment. A separate bounded Stage 4 analysis later examined model-authored artifacts; those results are not merged into the frozen 22-case Stage 1 denominator.
2. A separate bounded Stage 2 study later compared the signed bytes against Cosign, in-toto and SLSA Verifier; those results are not merged into the frozen 22-case Stage 1 denominator.
3. This Stage 1 run tested no network ingress. Stage 3 later constructed a loopback ingress and exercised the frozen contract across it.
4. The trusted execution observer is local and in-process path confinement has TOCTOU limitations (documented in remediation v1 limitations).

---

## 6. Conclusion

The Stage 1 end-to-end attribution evaluator can justify an attributable completion claim **only when** the complete causal and cryptographic evidence chain supports it. Honest success is accepted (6/6); all negative controls are rejected or inconclusive (0 false positives). The success criterion from the handoff is met for this stage.