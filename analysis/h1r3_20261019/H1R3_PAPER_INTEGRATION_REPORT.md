# H1-R3 Paper Integration Report

## Status

H1-R3 has been integrated into a versioned manuscript candidate without modifying the protected current manuscript, result locks, B2 artifacts, or historical archives.

Candidate:
`sp2027/paper/h1r3_integration_candidate_20261019/`

## Evidence verified

- Confirmatory sessions: 852.
- Independent reference replays: 852/852.
- Reference disagreements: 0.
- Missing reference bundles: 0.
- Terminal counts: 821 SUCCESS, 28 CRYPTOGRAPHIC_PREDICATE, 2 EXECUTION, 1 SOURCE_SYNTAX.
- H1-R3 deterministic tests: 322/322 passed.
- Protected artifacts: unchanged; original `H1R3_INTEGRITY_AUDIT.json` confirms all expected hashes.
- Provider calls during integration: 0.

## Integrated scientific claims

The candidate adds H1-R3 as a separate confirmatory population. It does not pool H1-R3 with V4, H1 V2, or B2.

Primary pooled L3 contrasts:

- R1 versus R0: tau = 0.008; 95% CI [-0.023, 0.039]; Holm-adjusted exact McNemar p = 1.000; equivalent within +/-0.10.
- R2 versus R0: tau = -0.008; 95% CI [-0.047, 0.031]; Holm-adjusted exact McNemar p = 1.000; equivalent within +/-0.10.

The text explicitly limits this to the tested model route, zero-query task families, observation levels, execution contract, and margin. It preserves the inconclusive lower-level ECDSA R2 strata and explains that most failures were cryptographic-predicate algebra slips rather than decoding or sandbox failures.

## Candidate build

- Candidate `main.tex` SHA-256: `aad5e84d649524e64a88344cab484edeb90d7a59746f56d4388508d92b2b4f97`.
- Candidate `main.pdf` SHA-256: `eb3a732a80575b0556c8e7b7af6158db35a198593565680b3d21a65433e60569`.
- Candidate PDF pages: 13.
- Second-pass LaTeX diagnostics: no fatal errors, undefined references, or overfull-box diagnostics.

## Current protected manuscript

The existing authoritative source and PDF remain unchanged:

- `sp2027/paper/main.tex`: `51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461`
- `sp2027/paper/main.pdf`: `fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a`

Promotion of the candidate to the authoritative manuscript should be a separate release/lock operation, because the existing H1-R3 integrity audit deliberately treats those paths as protected.