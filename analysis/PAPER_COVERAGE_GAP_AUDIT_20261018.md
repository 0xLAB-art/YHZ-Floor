# ACTS-Attack Paper Coverage Gap Audit

**Purpose.** This is a claim-relative audit of the R01–R50 evidence ledger against the active authoritative manuscript source. It is not a pooled experiment table and does not treat inventory rows, archive members, or duplicate copies as new observations. No new model or provider experiment was run.

## Direct denominator resolutions

- **E5:** raw retained JSON gives 29 canonical records: 14 graded = 1 accepted + 9 oracle failures + 4 tool failures, and 15 provider-unavailable. Therefore initial graded = **0/4**, extension graded = **1/10**, all graded = **1/14**; provider-unavailable launches are separate and not attack failures.
- **V4:** raw retained JSON gives **8/12** with RC4 **0/3**, ChaCha20 **2/3**, CBC **3/3**, ECDSA **3/3**. The older ledger row R46 had ChaCha20/ECDSA transposed; the active manuscript is consistent with the raw cohort.

## Coverage counts

- `COVERED_MAIN_AND_SUPP`: 14
- `COVERED_SUPP_ONLY`: 9
- `COVERED_AS_AUDIT_ARTIFACT`: 3
- `PARTIAL_RECONCILED`: 2
- `OMITTED_NONSCIENTIFIC_SCOPE`: 2
- `PARTIAL_SUPP_ONLY`: 2
- `OMITTED_NONRESULT`: 2
- `OMITTED_ARTIFACT_CONTROL`: 1
- `OMITTED_OUT_OF_SCOPE`: 1
- `OMITTED_UNRESOLVED`: 1
- `OMITTED_HISTORICAL_LINEAGE`: 1
- `DUPLICATE_COVERED_BY_R04_R05`: 1
- `DUPLICATE_COVERED_BY_R02`: 1
- `DUPLICATE_COVERED_BY_R01`: 1
- `DUPLICATE_COVERED_BY_R03`: 1
- `DUPLICATE_COVERED_BY_R07`: 1
- `DUPLICATE_COVERED_BY_R08`: 1
- `OMITTED_PROVENANCE_ONLY`: 1
- `DUPLICATE_COVERED_BY_R12`: 1
- `COVERED_SUPP_AS_INVENTORY`: 1
- `PARTIAL_SUPP_OR_OMITTED`: 1
- `DUPLICATE_COVERED_BY_R10`: 1
- `COVERED_MAIN_AND_SUPP_CORRECTED`: 1

## What is already integrated strongly

- V4 prospective construction: 12 sessions, 31 submitted programs, per-task outcomes, feedback/revision traces, and the accepted/rejected terminal statuses.
- Fixed-executor 12/12: correctly framed as an upstream reachability control, not agent capability.
- Explicit-observation cohorts: 6/6 per family and 18 total first-submission acceptances, with the ECDSA interface defect separated.
- C2/C2b/C2-T1/C3 target families: policy, wire-edit, negotiation, and toolchain boundaries are separated rather than pooled.
- A1/D1/E3: positive and negative timing/leakage observations are present with host/fixture limits.
- E5: R30 candidate/commitment match and the corrected 29-record denominator partition.
- Historical 74-session census, H1 V2, qualification/regression controls, adaptive XOR, composition, and held-out fixture are represented as bounded evidence rather than universal capability rates.

## Material gaps or weak integrations to fix before freeze

1. **Make the run-level evidence chain visible in the main paper.** The manuscript names many families, but a reader still has to reconstruct which run IDs close which stages. Add one compact table with columns: stage, canonical population, run IDs/path, oracle authority, tier, accepted/failed/non-result, and unproven boundary.
2. **Promote omitted high-value bounded results, not the entire inventory.** The strongest candidates are C2 4/4 target generality, C2-T1 3/3 wire-valid edits with `r2_verified=false`, D1 16/16 versus 2/16 sibling result, E3 32,000 one-host observations, and the 54-row legacy status crosswalk. Most are present somewhere, but their evidence-chain role is not sufficiently explicit.
3. **Reconcile the legacy 54-row status vocabulary.** The paper reports normalized 10 success / 12 give-up / 4 oracle-fail after relay-invalid exclusions, while the older ledger reports 10 success / 4 failure / 12 no-claim / 28 gateway-unavailable. These may be different normalization layers; the paper must show the mapping or avoid implying they are identical fields.
4. **Separate coverage from provenance.** R12/R31 historical 21/21, R17/R18/R21/R30 inventory/archive/CAS surfaces, and R20 missing LFS payloads should remain provenance or unresolved notes, not attack outcomes.
5. **Expose incomplete cohorts as non-results with paths.** Stable gpt-oss, partial Claude V3, invalid V4-01, contract-v3 provider outage, clean-primary, R230/R230-full/OpenCode, E3 shakedown, and C2b smoke should be listed in one non-result/qualification crosswalk so omission is not confused with absence.
6. **Retain duplicate lineage rules beside every historical number.** R22–R27 and R37–R38 are copies or lineages of already counted populations. The paper should state “mapped duplicate / no added execution” at the point of use.

## Results that should not be promoted to the main attack claim

- Archive member counts, recursive file counts, Git/CAS counts, inventory row counts, and missing LFS payloads.
- Historical Incalmo and unrelated benchmark records.
- Ignored log summaries that conflict with canonical JSON/JSONL records.
- Provider-unavailable or harness-error rows as attack failures or successes.
- Any pooled rate across V4, explicit-observation, legacy, historical, E5, or post-freeze fixtures.

## Recommended evidence-chain table for the next manuscript pass

| Stage | Canonical evidence | What it establishes | What it does not establish |
|---|---|---|---|
| Opportunity / relation | C2/C2b; RC4, ChaCha20, CBC, ECDSA task cards and fixtures | Named weakness/interface is reachable | Not agent construction or deployment prevalence |
| Construction | V4 12 sessions / 31 programs; explicit 18/18 cohorts | Model-authored artifacts can cross the code-to-oracle boundary under their contracts | Not causal information effect or immutable model identity |
| Target execution | C2b, C3, C2-T1, composition, held-out, E5 R30 | Selected artifacts produce specified local effects or candidate matches | Not one synthetic end-to-end attack population |
| Independent verification | Task oracles, commitment check, fixed executor, H1/qualification controls | Predicate acceptance and contract behavior | Not acquisition path, host isolation, or provenance by itself |
| Boundary / attribution | E5 verifier mismatch, V4 missing raw monotonic endpoints, duplicate/historical lineage | Where interpretation stops | Not proof that accepted candidates were wrong or that agents used an undeclared channel |

## Decision

The paper is not weak because it lacks every inventory row; it is weak because the manuscript does not make the **canonical run-level chain and its stopping points auditable enough in the main narrative**. The next edit should be targeted: add the evidence-chain table, reconcile the 54-row status vocabulary, expose the strongest omitted bounded results, and preserve all provenance/non-result material in the supplement. Do not add a pooled capability score or run new provider experiments.
