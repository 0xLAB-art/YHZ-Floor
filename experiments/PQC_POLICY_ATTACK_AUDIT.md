# PQC and hybrid-policy attack audit

The canonical repository contains direct local protocol-policy evidence for
hybrid KEM downgrade behavior. This is separate from model-backed agent
capability and from the historical TLS/SSH agent trajectories.

## C2 hybrid-KEM downgrade demonstrations

`ACTS-ATTACK/data/C2_pqc_generality.json` records four tested targets:
X25519MLKEM768, SecP256r1MLKEM768, SecP384r1MLKEM1024, and a cross-curve
downgrade. Each recorded normal hybrid handshake and classical-only downgrade
completed, with ASR=1, six modified bytes, 28 lines of code, and mean TTE
0.022 seconds across the four targets. X448MLKEM1024 and HQC-128 were
unavailable in that OpenSSL/provider configuration.

The defensible interpretation is four recorded local target demonstrations of
an implementation/policy failure in the specified environment. The artifact
does not establish an ML-KEM break, all-deployment generality, or an
AI-driven attack.

## C2b policy control

`ACTS-ATTACK/data/c2b_hybrid_required_control.json` records 45 trace-backed
handshakes in nine cells, five repetitions per cell, with zero trace
disagreements. The central contrast is `S-allow` with a classical-only client:
5/5 classical completions, versus `S-require` with the same client: 5/5
rejections. Hybrid-positive and symmetric-reject controls also matched their
pre-registered outcomes 5/5.

This is a causal local configuration-enforcement result under the recorded
OpenSSL/liboqs environment, not a model result or an on-path downgrade claim.
Its environment differs from the pre-registered E3 environment, so the claim
remains environment-bounded.

## Independent artifact check

The archived C2b endpoint traces were copied to a temporary verification
directory and reparsed with the committed `harness/c2b_parse.py`. The fresh
parse reproduced all 45 records, all nine unanimous five-repetition cells,
zero endpoint disagreements, and the exact archived verdict-file digest. This
checks the trace-to-verdict transformation; it does not turn the deterministic
control into a model-backed result.

The family-level join is recorded in `PQC_FAMILY_RECONCILIATION.md` and keeps
`PQC_endpoint_policy`, `PQC_policy_control`, and `PQC_message_edit` separate.
