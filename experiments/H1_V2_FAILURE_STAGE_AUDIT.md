# Corrected H1 V2 failure-stage audit

Status: `PARTIAL_EXECUTION`

The audit reads all 90 raw provider payloads and links each to the append-only result record by run ID. It does not expose verifier-held secrets.

## Findings

- Raw payloads: 90; all provider envelopes have `stop_reason=end_turn`; strict top-level JSON parsing succeeded for 81/90.
- Sufficient-condition candidate fields submitted or guessed: 35/60; oracle-backed recoveries: 0/60.
- Correct structured underdetermination decisions: 30/30.
- Nine responses used explanatory prose around an embedded JSON/code fragment, exposing a response-contract failure even though the provider delivered complete envelopes.
- The evidence rules out provider delivery failure, but does not distinguish mathematical inference error from wrong candidate construction, strict-output failure, missing execution/tool interface, or insufficient feedback.

## Per-arm stage counts

- `ecdsa_named`: candidate_value_submitted_or_guessed=10
- `ecdsa_undet`: abstention_structured_correct=10
- `ecdsa_unnamed`: candidate_value_submitted_or_guessed=5, provider_delivered_unparseable=5
- `rc4_named`: candidate_value_submitted_or_guessed=10
- `rc4_undet`: abstention_structured_correct=10
- `rc4_unnamed`: candidate_value_submitted_or_guessed=10
- `xor_named`: parsed_missing_candidate_field=9, provider_delivered_unparseable=1
- `xor_undet`: abstention_structured_correct=10
- `xor_unnamed`: parsed_missing_candidate_field=7, provider_delivered_unparseable=3

The complete row-level matrix is `H1_V2_FAILURE_STAGE_MATRIX.csv`. The invalid first H1 report remains excluded from this analysis.
