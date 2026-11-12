# ACTS-Attack H1 revalidation v2

Status: `PARTIAL_EXECUTION`

The original H1 report is invalid for confirmatory interpretation. Its underdetermined prompts used placeholders and its arm IDs did not match the frozen registry. It is retained only as provenance.

## Corrected execution

The v2 run used registry arm IDs `A_RC4_UNDET`, `A_ECDSA_UNDET`, and `A_XOR_UNDET`, with 10 matched seeds per condition. Named and unnamed conditions shared the same sufficient public instance. Underdetermined controls used genuine insufficient observations: RC4 target ciphertext at an unobserved keystream offset, one ECDSA signature, or one-byte XOR observations for a 16-byte target.

| Arm family | Named | Unnamed | Underdetermined |
|---|---:|---:|---:|
| RC4 | 0/10 | 0/10 | 10/10 correct abstention |
| ECDSA | 0/10 | 0/10 | 10/10 correct abstention |
| XOR | 0/10 | 0/10 | 10/10 correct abstention |

There were 90 genuine provider calls, 90 provider responses, zero provider failures, 13,235 input tokens, 6,611 output tokens, and estimated accounting cost of `$0.138870`. No model oracle-backed recovery succeeded. The 30 correct outcomes were all genuine underdetermination decisions.

The result supports only a bounded observation: under this prompt and output contract, the model abstained correctly when observations were structurally insufficient but did not recover secrets from the sufficient RC4, ECDSA, or XOR observations. This is compatible with an inference/construction failure, not cryptographic non-identifiability. It is not evidence for a universal mechanism or general cryptanalytic incapability.

## Validation

`revalidation_v2/validation_report.json` confirms registry membership, unique `(arm, seed, protocol)` combinations, independent local fixture recoverability, no verifier truth in revalidation prompts, complete provider metadata, and raw-response hash consistency.

Deterministic controls, pilots, the prior invalid H1 run, and CBC feasibility remain separate populations.
