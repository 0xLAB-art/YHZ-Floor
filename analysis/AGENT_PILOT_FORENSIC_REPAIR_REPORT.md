# ACTS-Attack — 72-Session Pilot Forensic Repair Report

**Date:** 2026-10-18  
**Scope:** Offline forensic and deterministic repair only  
**Provider/model calls during this phase:** 0  
**Original campaign:** `contract_sound_agent_pilot_20261018_free_v2`  
**Scientific status of original campaign:** infrastructure-invalid; excluded from C1/C2 inference  
**Replacement-pilot decision:** **NO-GO pending explicit approval and additional protocol review**

## Executive conclusion

The original 72-session campaign remains correctly excluded from the paper. Its provider responses are authentic and preserved, but its terminal records are not interpretable attack outcomes.

The forensic audit found two independent problems:

1. **Runner serialization defect:** the original runner passed a `Path` object to `json.dumps()` at the reference boundary. This caused `PosixPath` serialization failure before reference adjudication.
2. **Sandbox-contract inconsistency:** the prompt and executor require the candidate to read `argv[1]`, but the source checker rejected every `open(...)` call, including the intended read-only `open(sys.argv[1])` path. Therefore all 72 candidates were classified as sandbox-invalid before execution under the original checker.

The second issue is not evidence that the model succeeded or failed cryptographically. It is a mismatch between the declared candidate interface and the source-policy implementation. The repair permits only read-only `open(sys.argv[1])`; arbitrary writes, arbitrary file access, network/process access, and non-approved imports remain rejected.

## Immutable 72-session forensic audit

The original campaign was not modified. The per-session matrix is:

`sp2027/analysis/contract_sound_agent_forensic_matrix_20261018/FORENSIC_CLASSIFICATION_MATRIX.json`

The condition examples are:

`sp2027/analysis/contract_sound_agent_forensic_matrix_20261018/FORENSIC_EXAMPLES.json`

Results:

| Property | Result |
|---|---:|
| Original provider responses | 72/72 |
| Candidate artifacts | 72/72 |
| Extraction mismatch under the original extractor | 0/72 |
| Original source qualification | 72/72 rejected |
| `disallowed-boundary` | 71/72 in the original audit; after exact rule enumeration, all 72 include the forbidden `open(...)` boundary |
| Additional disallowed import-from violation | 1/72 |
| Candidate outputs in original campaign | 0/72 |
| Original reference verdicts | 0/72 |
| Original blind-validator verdicts | 0/72 |
| Provider calls in this forensic phase | 0 |

The source files retained in the original campaign exactly reproduce the provider metadata output after the original `extract_source` normalization. No extraction corruption was found.

### Examples by condition

- **C0:** candidates generally used `open(sys.argv[1])` to read the public instance; the original checker rejected the call as `open(...)`.
- **C1:** candidates used the same declared instance-read path; the original checker rejected the call before execution.
- **C2:** candidates similarly used the instance-read path; one also contained a disallowed import-from use. The representation condition itself was not altered by the repair.

This establishes a policy/interface mismatch, not an AI cryptographic result.

## Repaired pipeline

Implemented additive offline-only components:

- `sp2027/analysis/contract_sound_repaired_pipeline.py`
- `sp2027/analysis/contract_sound_repaired_runner_v3.py`
- `sp2027/analysis/test_contract_sound_repaired_pipeline.py`

### Repair properties

The repaired qualification policy:

- allows imports only from `json`, `sys`, and `base64`;
- allows only `open(sys.argv[1])` or `open(sys.argv[1], "r"/"rt")`;
- rejects arbitrary file paths and write modes;
- rejects subprocess, socket, requests, urllib, `os.` and dynamic import boundaries;
- preserves stderr and explicit terminal states;
- passes reference bundle paths as strings, never `Path` objects;
- invokes the reference verifier only after a valid `candidate_output.json` exists;
- invokes the blind validator only after a certificate and evidence set exist;
- records `SANDBOX_REJECTED`, `EXECUTION_FAILED`, `CANDIDATE_OUTPUT_INVALID`, `ORACLE_REJECTED`, `ACCEPTED`, and reference/validator failures separately.

No provider execution is enabled by these repair components.

## Deterministic end-to-end controls

The offline test output is:

`sp2027/analysis/contract_sound_repaired_pipeline_tests_20261018/OFFLINE_REPAIR_TEST_RESULTS.json`

Results:

| Test | Result |
|---|---:|
| Valid ECDSA candidate executes | PASS |
| Valid ECDSA independently accepted | PASS |
| Invalid ECDSA independently rejected | PASS |
| Valid ChaCha20 candidate executes | PASS |
| Valid ChaCha20 independently accepted | PASS |
| Invalid ChaCha20 independently rejected | PASS |
| Blind validator completed on four adjudicated cases | PASS, 4/4 outputs |
| Prohibited import rejected | PASS |
| Arbitrary write boundary rejected | PASS |
| Malformed candidate JSON classified | PASS |
| Offline provider calls | 0 |
| Offline network calls | 0 |

The valid cases produced actual `candidate_output.json` files and reached independent reference-oracle verdicts. This closes the previously untested end-to-end path without using provider calls.

## Offline forensic replay of the original 72 artifacts

Replay output:

`sp2027/analysis/contract_sound_forensic_replay_20261018/FORENSIC_REPLAY_RESULTS.json`

This replay is a separate diagnostic protocol. It does not replace, repair, or reinterpret the original campaign results and must not be used as the preregistered C1/C2 estimate.

Replay summary:

| Condition | Executed | Execution failed | Sandbox rejected |
|---|---:|---:|---:|
| C0 | 24 | 0 | 0 |
| C1 | 24 | 0 | 0 |
| C2 | 22 | 1 | 1 |
| Total | 70 | 1 | 1 |

Across replayed candidates:

- independent reference verdicts: 45 accepted, 25 rejected;
- blind-validator decisions: 70 public-evidence decisions completed;
- provider calls: 0;
- network calls: 0.

The replay shows that the original source policy suppressed execution of all candidates, while the repaired policy permits most candidates to reach execution. It also reveals genuine model/harness-runtime failures among C2 artifacts. That is useful diagnostic evidence, but it is not a valid causal C1/C2 experiment because the replay was post hoc, uses retained outputs, and does not preserve the original execution state.

## Scientific interpretation

What is established:

- The original 72 provider calls reached the requested route.
- The original candidate extraction was faithful.
- The original source checker was inconsistent with the declared `argv[1]` file-reading interface.
- The original runner had a `Path` serialization defect.
- A repaired offline pipeline can execute valid and invalid cryptographic candidates and independently adjudicate them.
- The original campaign remains infrastructure-invalid.

What is not established:

- No original-pilot C1 success rate.
- No original-pilot C2 success rate.
- No original-pilot paired effect.
- No representation-sensitivity finding.
- No novelty claim.
- No evidence that Claude’s cryptographic reasoning was correct or incorrect in the original campaign.

The replay’s C2 execution irregularities should be treated as exploratory diagnostic evidence only. They motivate a protocol amendment concerning the candidate interface and qualification contract, but they do not justify a new scientific claim.

## Replacement-pilot gate

**NO-GO.** Do not initiate a replacement 72-session provider campaign yet.

Before requesting approval, the following must be completed:

1. review and approve the narrow source-policy amendment allowing the declared read-only `argv[1]` interface;
2. freeze the repaired runner and its hashes;
3. add deterministic tests for every terminal state and required-input boundary;
4. decide whether C2 runtime failures are model failures, task-card/interface effects, or another harness issue;
5. define how candidate qualification failures enter the preregistered denominator;
6. write a transparent protocol amendment explaining exclusion of the first campaign;
7. repeat deterministic controls independently;
8. obtain explicit approval for a separately labeled replacement pilot and its provider budget.

No provider calls, retries, paid fallback, manuscript changes, or result-lock changes were made during this repair phase.