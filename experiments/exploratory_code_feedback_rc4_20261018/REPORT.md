# RC4 model-to-code exploration

Protocol: `P009-H1-EXP-CODE-FEEDBACK-RC4-v1`.

The qualified local fixture used a known plaintext/ciphertext pair and a target
ciphertext produced with the same RC4 keystream. The verifier retained the
target plaintext and exposed only an independent accept/reject verdict; it was
not written to the public file.

Two synthetic seeds were run through the corrected top-level public-file
interface. Both provider responses arrived successfully, both generated
programs passed the static policy and local execution, and both were accepted
by the independent oracle on the first submission: 2/2 sessions, 2/2 oracle
acceptances, zero provider failures. The route was provider-attested as
`claude-sonnet-4-6-free`; the estimated accounting cost was $0.006840 on the
reported free route, with no invoice cost claimed.

This is a bounded, non-randomized exploratory observation. It is not a causal
feedback estimate, a general RC4 capability rate, or a pooled result with
corrected H1 V2, ECDSA, ChaCha20, V4, or deterministic controls.
