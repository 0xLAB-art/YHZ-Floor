# C3 service-relay qualification: 2026-10-18

The existing bounded `ACTS-ATTACK/harness/v3/service_relay_pilot.py` was run
against the local service/oracle harness. This is a qualification artifact,
not a model arm and not a new frozen cohort.

## Observed outcomes

| scenario | expected | observed |
|---|---|---|
| parsing success | `SUCCESS` | `SUCCESS` |
| parsing wrong claim | `ORACLE_FAIL` | `ORACLE_FAIL` |
| crypto misuse | `SUCCESS` | `SUCCESS` |
| TLS policy hybrid | `SUCCESS` | `SUCCESS` |

Additional gates passed: service requests were audited, container lifecycle
was recorded, reserved markers (`service_spec`, `TOKEN_KEY_HEX`,
`WEAK_PRIV_HEX`, `SERVER_PRIV_HEX`) were absent from the portable transcript
checks, and the generated pilot corpus passed `sp2027/schema/acts_audit.py`.

The run produced a local temporary corpus at
`/tmp/acts_relay_pilot_686uu72i/`. Its raw transcripts contain verifier-held
secrets and are intentionally not copied into the portable research package.
The qualification therefore records the result and source path, while the
raw local corpus remains non-portable and separate from frozen historical
results.

This establishes that the relay can carry a model-shaped code submission to a
real local service and an independent oracle with both positive and negative
verdicts. It does not establish model capability, a provider result, causal
feedback benefit, or frozen-card equivalence for a new C3 campaign.
