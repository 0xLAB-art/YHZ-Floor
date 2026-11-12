# H1-R3 Confirmatory Analysis

Sessions analysed: **852**  
Equivalence margin: **±0.10**  

## Session inventory

| Terminal stage | n |
|---|---:|
| `SUCCESS` | 821 |
| `CRYPTOGRAPHIC_PREDICATE` | 28 |
| `EXECUTION` | 2 |
| `SOURCE_SYNTAX` | 1 |

## Terminal success by cell

| Level | Family | R0 | R1 | R2 |
|---|---|---:|---:|---:|
| L1 | XOR_Keystream_Reuse | 32/32 | 32/32 | 32/32 |
| L1 | ECDSA_Nonce_Reuse | 29/32 | 32/32 | 23/32 |
| L2 | XOR_Keystream_Reuse | 32/32 | 32/32 | 30/32 |
| L2 | ECDSA_Nonce_Reuse | 32/32 | 32/32 | 25/32 |
| L3 | XOR_Keystream_Reuse | 63/64 | 64/64 | 63/64 |
| L3 | ECDSA_Nonce_Reuse | 62/64 | 62/64 | 61/64 |

## Paired contrasts (τ = treatment − R0)

| Contrast | n | R0 rate | Tx rate | τ | 95% CI | b (R0-only) | c (tx-only) | McNemar p | Decision |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| L1|R1_vs_R0|ECDSA_Nonce_Reuse | 32 | 0.906 | 1.000 | 0.094 | [0.000, 0.219] | 0 | 3 | 0.250 | INCONCLUSIVE |
| L1|R1_vs_R0|XOR_Keystream_Reuse | 32 | 1.000 | 1.000 | 0.000 | [0.000, 0.000] | 0 | 0 | 1.000 | EQUIVALENT_WITHIN_MARGIN |
| L1|R1_vs_R0|pooled | 64 | 0.953 | 1.000 | 0.047 | [0.000, 0.109] | 0 | 3 | 0.250 | INCONCLUSIVE |
| L1|R2_vs_R0|ECDSA_Nonce_Reuse | 32 | 0.906 | 0.719 | -0.188 | [-0.375, 0.001] | 9 | 3 | 0.146 | INCONCLUSIVE |
| L1|R2_vs_R0|XOR_Keystream_Reuse | 32 | 1.000 | 1.000 | 0.000 | [0.000, 0.000] | 0 | 0 | 1.000 | EQUIVALENT_WITHIN_MARGIN |
| L1|R2_vs_R0|pooled | 64 | 0.953 | 0.859 | -0.094 | [-0.203, 0.000] | 9 | 3 | 0.146 | INCONCLUSIVE |
| L2|R1_vs_R0|ECDSA_Nonce_Reuse | 32 | 1.000 | 1.000 | 0.000 | [0.000, 0.000] | 0 | 0 | 1.000 | EQUIVALENT_WITHIN_MARGIN |
| L2|R1_vs_R0|XOR_Keystream_Reuse | 32 | 1.000 | 1.000 | 0.000 | [0.000, 0.000] | 0 | 0 | 1.000 | EQUIVALENT_WITHIN_MARGIN |
| L2|R1_vs_R0|pooled | 64 | 1.000 | 1.000 | 0.000 | [0.000, 0.000] | 0 | 0 | 1.000 | EQUIVALENT_WITHIN_MARGIN |
| L2|R2_vs_R0|ECDSA_Nonce_Reuse | 32 | 1.000 | 0.781 | -0.219 | [-0.375, -0.094] | 7 | 0 | 0.016 | INCONCLUSIVE |
| L2|R2_vs_R0|XOR_Keystream_Reuse | 32 | 1.000 | 0.938 | -0.062 | [-0.156, 0.000] | 2 | 0 | 0.500 | INCONCLUSIVE |
| L2|R2_vs_R0|pooled | 64 | 1.000 | 0.859 | -0.141 | [-0.234, -0.062] | 9 | 0 | 0.004 | INCONCLUSIVE |
| L3|R1_vs_R0|ECDSA_Nonce_Reuse | 64 | 0.969 | 0.969 | 0.000 | [-0.062, 0.062] | 2 | 2 | 1.000 | EQUIVALENT_WITHIN_MARGIN |
| L3|R1_vs_R0|XOR_Keystream_Reuse | 64 | 0.984 | 1.000 | 0.016 | [0.000, 0.047] | 0 | 1 | 1.000 | EQUIVALENT_WITHIN_MARGIN |
| L3|R1_vs_R0|pooled | 128 | 0.977 | 0.984 | 0.008 | [-0.023, 0.039] | 2 | 3 | 1.000 | EQUIVALENT_WITHIN_MARGIN |
| L3|R2_vs_R0|ECDSA_Nonce_Reuse | 64 | 0.969 | 0.953 | -0.016 | [-0.078, 0.047] | 3 | 2 | 1.000 | EQUIVALENT_WITHIN_MARGIN |
| L3|R2_vs_R0|XOR_Keystream_Reuse | 64 | 0.984 | 0.984 | 0.000 | [-0.047, 0.047] | 1 | 1 | 1.000 | EQUIVALENT_WITHIN_MARGIN |
| L3|R2_vs_R0|pooled | 128 | 0.977 | 0.969 | -0.008 | [-0.047, 0.031] | 4 | 3 | 1.000 | EQUIVALENT_WITHIN_MARGIN |

## Stage attribution of discordant pairs

- **L1|R2_vs_R0|ECDSA_Nonce_Reuse**: treatment-arm failure stages {"CRYPTOGRAPHIC_PREDICATE": 9}
- **L1|R2_vs_R0|pooled**: treatment-arm failure stages {"CRYPTOGRAPHIC_PREDICATE": 9}
- **L2|R2_vs_R0|ECDSA_Nonce_Reuse**: treatment-arm failure stages {"CRYPTOGRAPHIC_PREDICATE": 7}
- **L2|R2_vs_R0|XOR_Keystream_Reuse**: treatment-arm failure stages {"CRYPTOGRAPHIC_PREDICATE": 2}
- **L2|R2_vs_R0|pooled**: treatment-arm failure stages {"CRYPTOGRAPHIC_PREDICATE": 9}
- **L3|R1_vs_R0|ECDSA_Nonce_Reuse**: treatment-arm failure stages {"CRYPTOGRAPHIC_PREDICATE": 2}
- **L3|R1_vs_R0|pooled**: treatment-arm failure stages {"CRYPTOGRAPHIC_PREDICATE": 2}
- **L3|R2_vs_R0|ECDSA_Nonce_Reuse**: treatment-arm failure stages {"CRYPTOGRAPHIC_PREDICATE": 3}
- **L3|R2_vs_R0|XOR_Keystream_Reuse**: treatment-arm failure stages {"EXECUTION": 1}
- **L3|R2_vs_R0|pooled**: treatment-arm failure stages {"CRYPTOGRAPHIC_PREDICATE": 3, "EXECUTION": 1}

## Legacy import policy sensitivity

| Arm | n | legacy would reject | rate | would still have succeeded under v3 |
|---|---:|---:|---:|---:|
| R0 | 256 | 46 | 0.180 | 43 |
| R1 | 256 | 16 | 0.062 | 16 |
| R2 | 256 | 122 | 0.477 | 109 |

## Generalization to unpublished instances

| Arm | attempted | succeeded | rate |
|---|---:|---:|---:|
| R0 | 254 | 247 | 0.972 |
| R1 | 256 | 252 | 0.984 |
| R2 | 255 | 233 | 0.914 |

## Sampling-noise floor (exact duplicate prompts)

- cells: 32, sessions: 96
- cells with unanimous outcome: 31 (0.969)
- cells with byte-identical programs: 0 (0.000)
- mean distinct programs per cell: 3.000
- pairwise outcome kappa: -0.016

## C0 abstention control (separate predicate)

- scheduled 20, correct abstention 20
- terminal counts {"SUCCESS": 20}

## Primary Holm adjustment

- L3|R1_vs_R0|pooled: p=1.0000, p_Holm=1.0000
- L3|R2_vs_R0|pooled: p=1.0000, p_Holm=1.0000
