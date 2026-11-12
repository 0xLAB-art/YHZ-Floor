# ACTS-Attack Contract-Sound Replacement Pilot Results

**Execution:** completed exactly 72 scheduled sessions; one provider request per session; no retries, seed replacement, paid fallback, or adaptive stopping.
**Route:** `claude-sonnet-4-6-free`; all 72 provider metadata records reported HTTP 200 and the exact route.
**Charge recorded:** USD 0.00.

## Scientific disposition

These are prospective replacement-pilot outcomes. They are separate from the original infrastructure-invalid campaign and its post-hoc forensic replay. No manuscript or existing result lock was modified.

## Primary C1/C2 endpoint

| Family | C1 | C2 | Difference C2-C1 |
|---|---:|---:|---:|
| ChaCha20_Nonce_Repeat | 12/12 (1.000) | 12/12 (1.000) | 0.000 |
| ECDSA_Nonce_Reuse | 12/12 (1.000) | 10/12 (0.833) | -0.167 |

Overall C1: **24/24 (1.000)**
Overall C2: **22/24 (0.917)**
Absolute paired difference (C2−C1): **-0.083**
Discordances: C1-only=2, C2-only=0
McNemar exact two-sided p-value: **0.500**
95% paired bootstrap percentile interval: **[-0.208, 0.000]**; 100,000 resamples, seed 20261018.
Meaningful-effect threshold: **0.25**; threshold met: **False**.

The pilot does not support a representation-sensitivity effect under the preregistered 0.25 criterion. This is a bounded pilot result, not evidence of equivalence or a general capability estimate.

## Condition and failure accounting

| Task | Condition | Scheduled | Execution | Reference | Primary successes |
|---|---|---:|---|---|---:|
| ChaCha20_Nonce_Repeat | C0 | 12 | `{'EXECUTED': 12}` | `{'REJECTED': 12}` | 0 |
| ChaCha20_Nonce_Repeat | C1 | 12 | `{'EXECUTED': 12}` | `{'ACCEPTED': 12}` | 12 |
| ChaCha20_Nonce_Repeat | C2 | 12 | `{'EXECUTED': 12}` | `{'ACCEPTED': 12}` | 12 |
| ECDSA_Nonce_Reuse | C0 | 12 | `{'EXECUTED': 12}` | `{'REJECTED': 12}` | 0 |
| ECDSA_Nonce_Reuse | C1 | 12 | `{'EXECUTED': 12}` | `{'ACCEPTED': 12}` | 12 |
| ECDSA_Nonce_Reuse | C2 | 12 | `{'EXECUTED': 10, 'SANDBOX_REJECTED': 2}` | `{'ACCEPTED': 10, 'NOT_RUN': 2}` | 10 |

## Observed failures

- Two ECDSA C2 sessions were `SANDBOX_REJECTED` because the model-generated programs imported `hashlib`, which is outside the frozen allowed subset.
- No provider, parser, oracle-process, validator-process, or harness failure occurred in the 72-session results.
- C0 produced 0/24 primary successes and 24/24 independent reference rejections.

## Evidence retention

- Raw provider responses: 72/72
- Certificates: 72/72
- Reference inputs: 72/72
- Verifier metadata files: 72/72
- JSON Schema errors: 0

Machine-readable artifacts:

- `AGENT_PILOT_RESULTS_SUMMARY.json`
- `AGENT_PILOT_PAIRED_RESULTS.json`
- `pilot_results.json`
- `schedule.json`

## Scientific recommendation

**Do not claim the novelty hypothesis as supported.** The observed C1/C2 difference is 0.083, below the preregistered 0.25 threshold, with two C1-success/C2-failure discordances and no reverse discordances. The correct result is a bounded null/inconclusive pilot outcome, not evidence that representation has no effect.

**Do not modify ACTS-Attack manuscript/results automatically.** Any incorporation requires a separate scientific decision and should preserve the distinction between this prospective campaign, the original invalid campaign, and the diagnostic replay.
