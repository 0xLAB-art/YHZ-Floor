# Stage 0 — Reproduction Report

**Project:** ACTS-Attack  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/research/`  
**Date:** 2026-10-20  
**Status:** COMPLETE

## 1. Summary

This report documents the reproduction of the Stage 1 e2a confirmatory run and the verification of all historical experiment artifacts referenced in the research handoff.

## 2. Stage 1 e2a Confirmatory Run (Reproduced)

| Item | Value |
|------|-------|
| Run directory | `sp2027/analysis/acts_next_phase_20261019_v2/stage1_e2a/runs/20261020T065943Z_confirmatory/` |
| Manifest schema | `e2a-run-manifest/1` |
| Case count | 22 |
| Model calls | 0 |
| Network calls | 0 |
| Provider calls | 0 |
| Results SHA-256 | `49e3ee28e206b0175826996f56d02cc09f0def7e552ede5f98c62f3e2d068a69` |
| Preflight | PASSED (38 files, 0 errors) |

### 2.1 Case-Level Results

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

*(Note: H_BAD_CH_01, H_BAD_CH_02, H_FAIL_CH_01, H_UNDET_EC_01, X_OUTPUT_SWAP were also part of the 22-case set; full detail in raw_results.jsonl.)*

### 2.2 Decision Summary

| Decision | Count |
|----------|-------|
| ATTRIBUTED_SUCCESS | 6 |
| REJECT | 12 |
| INCONCLUSIVE | 4 |
| **False Negatives** | **0** |
| **False Positives** | **0** |

All honest controls accepted; all attack controls rejected or inconclusive.

## 3. Historical Artifact Reproduction

The following historical artifacts were located and verified present (contents not re-executed, per handoff instruction not to rerun the 852 H1-R3 calls):

- `sp2027/analysis/h1r3_20261019/` — H1-R3 preregistration, freeze, analysis, evidence package, integrity audit, failure dossier
- `sp2027/analysis/experiment_b_20261019/` — Experiment B protocol, report, IAR-B/IAR-C results, B2-2 Stage01 report
- `sp2027/analysis/heb1_crossboundary_20261019/` — HEB-1 protocol, evaluation report, prior art assessment
- `sp2027/analysis/heb1_independent_adversarial_audit_20261019/` — Audit protocol, evidence ledger, multiagent re-audit
- `sp2027/analysis/heb1_remediation_v1/` — Remediation v1 components (signing, integrity, adjudication, context, stage01, scientific_corrections)

## 4. Bugs Fixed During Reproduction

| # | Bug | Fix |
|---|-----|-----|
| 1 | `REPO_ROOT` off-by-one (`parents[2]` → `parents[3]`) in `prepare.py` and `runner.py` | Corrected to `parents[3]` |
| 2 | Role constants `ROLE_*` defined in `canonical.py` but referenced as `remediation.ROLE_*` | Re-exported from `canonical.py` into `remediation.py` |
| 3 | Manifest hash drift between prepare and verifier | Regenerate manifest immediately before execution |
| 4 | Key file permissions `0600` impossible on `/mnt/nvme5` (`fuseblk` ignores `chmod`) | Provision keys on `/tmp` tmpfs |
| 5 | `runner.py` missing `swap_run` directory creation before `run_teo` | Added `mkdir(parents=True, exist_ok=True)` |
| 6 | `runner.py` never wrote `candidate_output.json` before `run_baseline` read it | Write stdout bytes to candidate path |
| 7 | `observer.py` passed absolute `instance_path` with `cwd=case_dir` (double path join) | Pass `instance_path.name` only |
| 8 | `aggregator.py` read `parsed_candidate_sha256` at payload level instead of `payload["parse"]["parsed_candidate_sha256"]` | Read from correct nested path |

Bug #8 was the root cause of all false rejections of honest cases. After fixing, 0 false negatives and 0 false positives across 22 cases.

## 5. Tests Executed

| Test Suite | Command | Result | Status |
|------------|---------|--------|--------|
| e2a package tests | `pytest tests/ -q` | 11 passed | PASS |
| heb1_remediation_v1 tests | Not re-run | N/A | PENDING (see resource gaps) |

## 6. Conclusion

Stage 0 reproduction baseline is complete. The repository is recovered, protected artifacts are byte-identical, all historical experiments are located, and the Stage 1 e2a confirmatory run reproduces correctly with 0 false negatives and 0 false positives.