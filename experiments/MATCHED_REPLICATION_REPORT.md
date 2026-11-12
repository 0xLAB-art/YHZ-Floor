# Matched corrected-interface replication report

Protocol: `P009-H1-EXP-CODE-FEEDBACK-replication-20261018`

This additive run used unseen seeds 3 and 4 in each already qualified
family-specific code-feedback fixture. It retained separate namespaces and
independent local oracle verdicts. It is not pooled with H1 V2, V4, CBC, or the
earlier n=2 exploratory cohorts.

| Family | Sessions | Provider responses | Programs executed | First-submission oracle accepted | Provider failures | Input/output tokens | Estimated accounting |
|---|---:|---:|---:|---:|---:|---:|---:|
| ECDSA | 2 | 2 | 2 | 2/2 | 0 | 718/781 | $0.013869 |
| ChaCha20 | 2 | 2 | 2 | 2/2 | 0 | 592/554 | $0.010086 |
| RC4 | 2 | 2 | 2 | 2/2 | 0 | 470/382 | $0.007140 |

Total estimated accounting is $0.031095 under the existing $3/M input and
$15/M output ledger convention. The route remains provider-attested
`claude-sonnet-4-6-free`; hosted model-weight identity is not independently
verified.

The observation strengthens the bounded statement that the corrected,
family-specific model-to-code path was reproduced on two additional seeds per
family. It does not estimate general capability, compare families causally,
identify a feedback effect, or establish robustness outside these qualified
fixtures and provider conditions. All raw responses, result records, events,
and per-family summaries remain in the three replication namespaces.
