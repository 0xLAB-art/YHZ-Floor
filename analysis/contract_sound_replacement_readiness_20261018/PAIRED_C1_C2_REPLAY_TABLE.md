# Diagnostic C1/C2 Replay Table

> POST-HOC DIAGNOSTIC ONLY. These records cannot replace the infrastructure-invalid preregistered campaign.

| Task | Condition | Scheduled | Execution | Reference oracle | Blind validator |
|---|---:|---:|---|---|---|
| ChaCha20_Nonce_Repeat | C0 | 12 | `{'EXECUTED': 12}` | `{'REJECTED': 12}` | `{'ACCEPT': 12}` |
| ChaCha20_Nonce_Repeat | C1 | 12 | `{'EXECUTED': 12}` | `{'ACCEPTED': 12}` | `{'ACCEPT': 12}` |
| ChaCha20_Nonce_Repeat | C2 | 12 | `{'EXECUTED': 11, 'EXECUTION_FAILED': 1}` | `{'ACCEPTED': 11, 'NOT_RUN': 1}` | `{'ACCEPT': 11, 'NOT_RUN': 1}` |
| ECDSA_Nonce_Reuse | C0 | 12 | `{'EXECUTED': 12}` | `{'REJECTED': 12}` | `{'ACCEPT': 12}` |
| ECDSA_Nonce_Reuse | C1 | 12 | `{'EXECUTED': 12}` | `{'ACCEPTED': 12}` | `{'ACCEPT': 12}` |
| ECDSA_Nonce_Reuse | C2 | 12 | `{'EXECUTED': 11, 'SANDBOX_REJECTED': 1}` | `{'ACCEPTED': 10, 'NOT_RUN': 1, 'REJECTED': 1}` | `{'ACCEPT': 11, 'NOT_RUN': 1}` |

## Paired seeds

| Task | Seed | C1 | C2 |
|---|---:|---|---|
| ChaCha20_Nonce_Repeat | 1 | EXECUTED/ACCEPTED | EXECUTION_FAILED/NOT_RUN |
| ChaCha20_Nonce_Repeat | 2 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ChaCha20_Nonce_Repeat | 3 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ChaCha20_Nonce_Repeat | 4 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ChaCha20_Nonce_Repeat | 5 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ChaCha20_Nonce_Repeat | 6 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ChaCha20_Nonce_Repeat | 7 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ChaCha20_Nonce_Repeat | 8 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ChaCha20_Nonce_Repeat | 9 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ChaCha20_Nonce_Repeat | 10 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ChaCha20_Nonce_Repeat | 11 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ChaCha20_Nonce_Repeat | 12 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ECDSA_Nonce_Reuse | 1 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ECDSA_Nonce_Reuse | 2 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ECDSA_Nonce_Reuse | 3 | EXECUTED/ACCEPTED | SANDBOX_REJECTED/NOT_RUN |
| ECDSA_Nonce_Reuse | 4 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ECDSA_Nonce_Reuse | 5 | EXECUTED/ACCEPTED | EXECUTED/REJECTED |
| ECDSA_Nonce_Reuse | 6 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ECDSA_Nonce_Reuse | 7 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ECDSA_Nonce_Reuse | 8 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ECDSA_Nonce_Reuse | 9 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ECDSA_Nonce_Reuse | 10 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ECDSA_Nonce_Reuse | 11 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
| ECDSA_Nonce_Reuse | 12 | EXECUTED/ACCEPTED | EXECUTED/ACCEPTED |
