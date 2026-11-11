# HEB1 Stage01 bounded remediation

`external_binding_wrapper.py` is a new external boundary, not a replacement or
edit of either frozen Stage01 component. It verifies the pinned SHA-256 of
`contract_sound_stage01_validator_v2.py`, invokes that validator before its
additional checks, and retains its complete raw subprocess record in
`raw_verdict`.

After the original validator runs, the wrapper requires exactly the declared
Stage01 evidence kinds, rejects malformed or duplicate evidence entries and
paths, verifies every declared evidence digest, and verifies the
`agent_artifact` artifact pointer and digest. It then compares
`execution_trace.candidate_sha256` with that artifact digest. A missing trace
binding is `INCONCLUSIVE`; a malformed or conflicting binding is `REJECT`.

The synthetic B2-2 cases use the artifact pointer as a candidate-output
artifact. Live model-backed Stage01 may instead point `agent_artifact` at
program source while the bundle carries a separate candidate output. This
wrapper only proves declared artifact/trace consistency; it does not classify
the bytes or establish the live program-source-to-candidate-output chain. That
chain remains unresolved.

Historical compatibility permits arbitrary local evidence paths. This is not
path confinement or untrusted-bundle safety: the frozen validator runs first
and may read those paths before the wrapper's additional checks.

Focused tests use copied tiny evidence fixtures in pytest temporary
directories. They do not rerun a frozen campaign.
