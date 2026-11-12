# ChaCha20 model-to-code exploration

Protocol: `P009-H1-EXP-CODE-FEEDBACK-CHACHA20-v1`.

The qualified local fixture used two 64-byte ChaCha20 ciphertexts made with
the same key and nonce. The second ciphertext encrypted an all-zero reference,
so the protected plaintext was recoverable from the public ciphertext pair by
the nonce-reuse relation. The verifier retained the plaintext and exposed only
an independent accept/reject verdict; it was not written to the public file.

Two synthetic seeds were run through the corrected top-level public-file
interface. Both provider responses arrived successfully, both generated
programs passed the static policy and local execution, and both were accepted
by the independent oracle on the first submission: 2/2 sessions, 2/2 oracle
acceptances, zero provider failures. The route was provider-attested as
`claude-sonnet-4-6-free`; the estimated accounting cost was $0.009921 on the
reported free route, with no invoice cost claimed.

This is a bounded, non-randomized exploratory observation. It is not a causal
feedback estimate, a general ChaCha20 capability rate, or a pooled result with
corrected H1 V2, ECDSA, V4, or deterministic controls.
