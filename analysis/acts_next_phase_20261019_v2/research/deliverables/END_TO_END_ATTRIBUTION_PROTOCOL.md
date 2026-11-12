# Stage 1 — End-to-End Attribution Protocol

**Project:** ACTS-Attack  
**Stage:** Stage 1 — Genuine End-to-End Attribution  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/`  
**Date:** 2026-10-20  
**Status:** FROZEN (preregistered before confirmatory execution)

---

## 1. Hypothesis

**Primary hypothesis (H1):** The end-to-end attribution evaluator can justify an attributable completion claim **only when** the complete causal and cryptographic evidence chain supports it — i.e., honest successful executions are attributed as success, and all negative controls (cryptographic failures, malformed output, missing evidence, replay, context conflict, identity/output/reference swaps) are rejected or inconclusive.

**Null hypothesis (H0):** The evaluator either falsely accepts invalid claims (false positives) or falsely rejects valid ones (false negatives).

**Decision rule:** Accept H1 if and only if 0 false negatives AND 0 false positives across all 22 preregistered cases.

---

## 2. Objects Distinguished (per handoff §8)

The experiment distinguishes at least these objects:

1. Model or scripted producer identity → `e2a-scripted-producer-v1` (scripted)
2. Exact program source bytes and SHA-256 → `program_source_sha256`
3. Exact executed program bytes → memfd-executed source (identical to declared)
4. Invocation command and arguments → recorded in observation `command`
5. Execution environment identity and version info → interpreter + environment block
6. Input/public-instance digest → `public_target_digest`
7. Target identity and state digest → `target_id` + `target_state_sha256`
8. Execution attempt/session identity → `attempt_id`
9. Actual captured stdout and stderr → `executor_stdout.txt` / `executor_stderr.txt`
10. Parsed `candidate_output.json` and its digest → `parsed_candidate_sha256`
11. Trusted execution-observer record → signed observation envelope
12. Independent cryptographic reference result → signed reference adjudication
13. Signed evidence records with explicit issuer identity and role → Ed25519 signatures per role
14. Aggregated certificate → `certificate.e2a.json`
15. Final attributed success claim → `claim.e2a.json` signed by aggregator

**Trusted execution observer:** The `observer` component (`e2a/observer.py`) is trusted to observe execution. It executes from an in-memory memfd, captures output, and signs the six-field context. The evidence chain does **not** rely solely on hashes supplied by an untrusted producer — the observer independently executes and captures output.

---

## 3. Controls (Preregistered)

### Positive Controls (honest success, expect ATTRIBUTED_SUCCESS)
- H_OK_EC_01, H_OK_EC_02, H_OK_EC_03 (ECDSA nonce reuse, correct)
- H_OK_CH_01, H_OK_CH_02, H_OK_CH_03 (ChaCha20, correct)

### Negative Controls (expect REJECT or INCONCLUSIVE)
- H_BAD_EC_01, H_BAD_CH_02 (incorrect crypto)
- H_FAIL_EC_01, H_FAIL_CH_01 (execution failure)
- H_MALFORMED_EC_01 (malformed output)
- H_UNDET_EC_01 (undetermined)
- M_MISSING_OBS, M_MISSING_REF (missing evidence → INCONCLUSIVE, not zero failure)

### Attack Variants (expect REJECT or INCONCLUSIVE)
- X_IDENTITY (identity swap → REJECT: executed-program-identity-mismatch)
- X_OUTPUT_SWAP (output swap → REJECT: candidate-output-substitution)
- X_STALE_ATTEMPT (stale attempt → INCONCLUSIVE: observation-context-binding)
- X_CONTEXT_CONFLICT (context conflict → INCONCLUSIVE: observation-context-binding)
- X_REPLAY (replay → REJECT: observation-replayed)
- X_REF_MISMATCH (reference mismatch → REJECT: reference-does-not-adjudicate-this-observation)

---

## 4. Evaluation Checks (Ordered, per aggregator)

1. Certificate present / fields present → INCONCLUSIVE if missing
2. Authenticity: observation & reference signatures verified → INCONCLUSIVE if invalid
3. Kind and role correctness → INCONCLUSIVE if wrong
4. Replay check on signed context → REJECT if replayed
5. Six-field context binding (audited context_validator) → INCONCLUSIVE if binding fails
6. Cross-record consistency: observation record hash, stdout pin, candidate digest, target digest, target ID → REJECT on mismatch
7. Certificate-claim consistency: agent artifact hash, candidate output declaration → REJECT on mismatch
8. Reference adjudicator status → INCONCLUSIVE if not ADJUDICATED
9. Cryptographic predicate (crypto_ok AND verdict ACCEPTED) → ATTRIBUTED_SUCCESS or REJECT

**Missing evidence → INCONCLUSIVE, not counted as zero failure** (per audit correction).

---

## 5. Integrity Safeguards

- Complete runner code, validators, adjudicators, cases, manifests, trust roots, and metric definitions frozen before execution
- Preflight check run before execution (fail-closed)
- Every attempted case preserved, including unfavorable outcomes
- Raw stdout/stderr, return codes, and independent adjudication preserved
- Defensible denominators: 22 total cases, 6 positive controls, 16 negative controls
- REJECT distinguished from INCONCLUSIVE
- N/A treated as functionality mismatch where appropriate
- No metric redefined after inspecting outcomes
- No historical freeze retrofitted

---

## 6. Results (Confirmatory Run)

**Run directory:** `runs/20261020T065943Z_confirmatory/`  
**Results SHA-256:** `49e3ee28e206b0175826996f56d02cc09f0def7e552ede5f98c62f3e2d068a69`

| Decision | Count |
|----------|-------|
| ATTRIBUTED_SUCCESS | 6 |
| REJECT | 12 |
| INCONCLUSIVE | 4 |
| False Negatives | 0 |
| False Positives | 0 |

**Decision rule outcome:** 0 false negatives AND 0 false positives → **H1 accepted, H0 rejected.**

---

## 7. Limitations

- This Stage 1 protocol uses the local scripted producer only. A separate bounded Stage 4 analysis later examined model-authored artifacts; it does not alter this frozen protocol.
- This Stage 1 protocol has no external provenance comparator. Stage 2 later executed a separate bounded Cosign/in-toto/SLSA comparison.
- This Stage 1 run tested no network ingress; Stage 3 later constructed a loopback ingress and exercised the frozen contract across it.
- Local trusted execution observer; path confinement has TOCTOU limitations (documented)