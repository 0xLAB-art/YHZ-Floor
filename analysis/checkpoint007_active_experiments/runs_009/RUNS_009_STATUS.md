# ACTS-Attack runs_009 status

Status: `PARTIAL_EXECUTION`

This namespace is additive. Frozen checkpoint 007/007C/007D/008 files were not modified.

## Completed in this namespace

| Item | Evidence | Result |
|---|---|---|
| CBC fixture qualification | `fixture_qualification.json` | Frozen 400-query condition did not recover the target; amended 4096-query local control recovered the 15-byte target in 2,021 oracle queries and matched verifier-held plaintext. |
| RC4 information boundary | `fixture_qualification.json` | Solver recovered the target using only known plaintext/ciphertext and target ciphertext; encryption key was not passed to the solver. |
| ECDSA qualification | `fixture_qualification.json` | Two different messages, shared nonce-derived `r`, actual secp256k1 arithmetic, and independent public-key verification passed. |
| XOR qualification | `fixture_qualification.json` | Named/unnamed observation contract is equal; underdetermined control is represented as no unique secret claim. |
| `E_GRADER_MAP` | `E_GRADER_MAP__*.json` | Identical candidate bytes; invariant underlying acceptance; differing recorded labels. |
| `E_EXEC_CONTRACT` | `E_EXEC_CONTRACT__*.json` | Actual subprocess test: argv yields verdict and stdin reproduces no-verdict behavior. |
| `E_TRANSCRIPT_SCAN` | `E_TRANSCRIPT_SCAN__*.json` | Raw sentinel set empty; appended sentinel retained separately. |
| `F_FAULT_INJECT` | `F_FAULT_INJECT__*.json` | 60/60 classifications recorded in the new control lane. |
| `F_CLOCK_CALIB` | `F_CLOCK_CALIB__*.json` | Four clock sources recorded, with interval measurement explicitly marked. |
| Provider metadata | `provider_attestation.json` | HTTP 200 and route listed by provider; this does not establish model-weight provenance. |

The append-only journal is `events.jsonl`; durable state is `state.json`; file hashes are in `integrity_report.json`.

## Model-backed execution

The provider adapter and crash-safe combination scheduler were tested with two fake-provider restart records and then used for 94 genuine provider calls: 3 nonconfirmatory integration calls, 90 H1 calls, and 1 annotation call. The H1 matrix completed 30 matched named/unnamed pairs plus 30 underdetermined decisions. All 90 H1 responses were delivered; 0 were oracle-backed recoveries and 30/30 underdetermination decisions were correct. Estimated token-accounting cost across genuine calls was `$0.094371`; the provider route reported a free plan, so this is accounting cost rather than a claim of charged spend.

The three integration calls are separate: the first was underidentified, the second failed the secret-material boundary, and the amended third passed boundary and JSON checks but failed oracle grading. The annotation call used a redacted transcript, passed schema validation, and matched its held-out label once; this is not human-gold validation.

The first H1 report is invalid for confirmatory interpretation because its underdetermined observations were placeholders and its `*_UNDETERMINED` arm IDs were not in the frozen registry. Corrected v2 evidence is in `REVALIDATION_V2_REPORT.md`: 90 registry-valid provider calls, 30/30 genuine underdetermination decisions, 0 oracle-backed recovery successes, and independent validation passed.

## Not completed

No CBC model-backed run was launched. The old pilot stub and v3 scaffold remain preserved as historical artifacts; the new adapter is confined to this additive namespace. CBC model arms remain held pending the amended instrument and complete response-validation path.

Exact deferred arms: `B_CBC_INTERACTIVE`, `B_CBC_ONESHOT`, `C_CBC_BINARY`, `C_CBC_ENRICHED`.

## Scientific interpretation boundary

The local results qualify fixtures and instrumentation only. They are not model capability estimates, not confirmatory H1-H5 estimates, and not evidence that CBC is impossible under the frozen budget beyond this deterministic instance/control. The amended CBC result supports feasibility at this instance and budget, not a general success-rate claim.

## Next executable action

Implement and test a new model adapter in this namespace with: path-independent loading, append-only model/provider/harness/oracle/verifier events, response-body and finish-reason retention, incomplete-response rejection, verifier-only secret escrow, generated-code syntax/execution validation, per-arm query/turn budgets, and matched seed scheduling. Then run the preregistered eligible H1/H4 conditions without pooling them with deterministic controls.
