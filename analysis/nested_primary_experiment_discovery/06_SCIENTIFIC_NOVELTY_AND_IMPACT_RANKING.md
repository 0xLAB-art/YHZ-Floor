# Scientific novelty and impact ranking

Ranking uses evidence strength, control quality, claim distinctiveness, and IEEE S&P relevance rather than success percentage alone.

| Rank | Finding | Evidence | Scientific value | Main reviewer concern |
|---:|---|---|---|---|
| 1 | C2b server-policy enforcement | PRIMARY_VERIFIED | Clean mechanism-level control separating allow versus require policy | single host/build; not a deployment study |
| 2 | Fixed-operation independent-oracle rerun | PRIMARY_VERIFIED | Demonstrates verifier authority, fresh secrets, paired timing, and implementation reachability | operation-only; no agent inference |
| 3 | Environment-gated timing separability | PRIMARY_BOUNDED | Shows why side-channel claims require environment qualification | no causal environment design or raw sample release |
| 4 | C2-T1 open wire-edit reproduction | PRIMARY_BOUNDED | Separates protocol-edit simplicity from AI/toolchain claims | `r2_verified=false`; summary-level record |
| 5 | Spread-Table exact recovery record | PRIMARY_BOUNDED | Potentially strong implementation-specific side-channel observation | no raw timing file or full run chain |
| 6 | Historical SP2-05 session evidence | HISTORICAL_LIMITED | Demonstrates why duplicates, mutable providers, and incomplete identity defeat pooling | not a clean independent cohort |
| 7 | B1 model response heterogeneity | PRIMARY_BOUNDED | Useful safety/behavioral observation outside the central measurement question | no independent behavioral oracle |
| 8 | Historical 21-run benchmark aggregate | HISTORICAL_LIMITED | Preserves project history and task families | aggregate lacks complete raw provenance |

## Promotion recommendations

- Promote C2b only as the bounded statement already supported: local hybrid TLS policy enforcement.
- Promote the fixed-operation rerun as a control/artifact result, not as agent performance.
- Retain A1 as a qualified environment-sensitivity result; do not promote a causal VM claim without controlled replication.
- Keep Spread-Table artifact-level unless raw sample lineage and an independent rerun are recovered.
- Keep C2-T1 as a bounded reproduction/negative control for AI necessity and toolchain claims.

The strongest attack-like records may be better treated as separate future work if broad security generality is desired; forcing them into this paper would weaken the claim-relative evidence-assessment identity.
