# Extended matched corrected-interface replication: seeds 5 and 6

Claude Sonnet 4.6 free was used through the existing provider-attested
`api.apmix.ai` route. This additive namespace extends, but does not overwrite,
the earlier unseen-seed 3/4 replication.

| family | new seeds | provider responses | programs executed | first-submission oracle acceptance | provider failures | input/output tokens |
|---|---:|---:|---:|---:|---:|---:|
| ECDSA nonce reuse | 5, 6 | 2 | 2 | 2/2 | 0 | 718 / 984 |
| ChaCha20 nonce reuse | 5, 6 | 2 | 2 | 2/2 | 0 | 592 / 577 |
| RC4 keystream reuse | 5, 6 | 2 | 2 | 2/2 | 0 | 470 / 505 |

The new total is 6/6 first-submission acceptance. Combined with the earlier
seeds 3/4 namespace, the qualified family-specific transition has 12/12
acceptances over four sampled unseen seeds per family. This remains bounded
reproducibility evidence: fixtures, prompts, provider route, and policy filter
are family-specific; the observations are not a pooled capability rate, a
family comparison, or a feedback-causality estimate.

Raw provider responses, prompt/public-input hashes, result rows, and event
records are retained in:

- `exploratory_code_feedback_ecdsa_replication_20261018_seeds56/`
- `exploratory_code_feedback_chacha20_replication_20261018_seeds56/`
- `exploratory_code_feedback_rc4_replication_20261018_seeds56/`

The provider route is attested metadata only; hosted model-weight identity is
not independently verified. Estimated accounting under the existing $3/M
input and $15/M output ledger convention is $0.036330 for this namespace.
