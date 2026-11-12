# Canonical V4 trajectory audit

Status: `PARTIAL_EXECUTION`

This audit reads the 12 retained namespace-02 run records and keeps task, model, program, and oracle fields linked by run ID.

## Findings

- Rows: 12; statuses: {'ORACLE_FAIL': 4, 'SUCCESS': 8}; submitted-program records: 31.
- Explicit accepted oracle outcomes: 8; oracle-failed rows: 4.
- Separate-process oracle records: 12/12.
- The accepted and failed rows are direct attack evidence under this V4 task contract. They are not pooled with deterministic executors, H1 V2, or other historical namespaces.
- The cohort does not support a causal claim that feedback caused success; a matched no-feedback intervention is absent.

## Per-task status

- `cbc_padding_oracle`: SUCCESS=3
- `chacha20_nonce_reuse`: ORACLE_FAIL=1, SUCCESS=2
- `ecdsa_nonce_reuse`: SUCCESS=3
- `rc4_keystream_reuse`: ORACLE_FAIL=3

The complete row-level matrix is `V4_TRAJECTORY_MATRIX.csv`.
