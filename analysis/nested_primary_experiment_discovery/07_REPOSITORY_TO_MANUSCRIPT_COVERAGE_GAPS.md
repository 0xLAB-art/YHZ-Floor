# Repository-to-manuscript coverage gaps

Coverage was checked after repository discovery against `sp2027/paper/split_rebuild_consistency_timing/` main sections, supplement sections, integration reports, and artifact maps.

| Discovered family/result | Coverage status | Evidence in current paper surface | Gap |
|---|---|---|---|
| C2b 45/45 local policy matrix | IN_SUPPLEMENT_ONLY, with bounded main-text mention | `supp_sections/S13_c2b.tex`; integration report; evidence gate | matrix details and trace pointers remain artifact-level |
| C2b smoke 9-cell matrix | ARTIFACT_ONLY | no named smoke cohort mapping | one-repetition control is not distinguished in current coverage |
| C2 original 4/4 PQC generality | NOT_MENTIONED | no named C2 JSON/result in manuscript sections | no result-level qualification or limitation |
| C2-T1 3/3 open pipeline | MENTIONED_WITHOUT_RESULT | integration report says excluded from main claims | numerical wire-format/TTE result is not presented |
| A1 WSL2/VMware | IN_SUPPLEMENT_ONLY / qualified | integration report explicitly says supplementary-only | raw measurement provenance remains bounded |
| B1 L1-L5 safety evaluation | MENTIONED_WITHOUT_RESULT outside manuscript | integration report says excluded | no result table or claim boundary |
| D1 Bernstein and Spread-Table | ARTIFACT_ONLY | integration report says artifact-only/excluded | exact observed contrast and raw-evidence limitation absent |
| historical 21-run aggregate | NOT_MENTIONED | no nested aggregate mapping found | no explicit separation from rerun cohorts |
| fixed-operation rerun 12/12 | ARTIFACT_ONLY | fixed executor discussed conceptually, exact nested result not mapped | no direct mapping of `results_rerun/` to E arms |
| SP2-05 v2/v3 74 sessions | IN_SUPPLEMENT_ONLY | `S16_sp205.tex` reports 74 sessions and duplicate limits | v2/v3 duplicate identity not stated |
| 54-row agent rerun plus 22 excluded | NOT_MENTIONED | current E2 uses a separate 54-row census | campaign identity and exclusion lineage need distinction |
| uncompleted target families | ARTIFACT_ONLY / UNRESOLVED | non-results section discusses halted campaigns generally | nested target-specific failures not named |

The strongest omission is not that every nested result must enter the paper. It is that the manuscript artifact map does not make the full nested inventory, deduplication, or exclusion rationale discoverable. The current selective exclusions are defensible, but they are not a complete project-to-paper map for this checkout.

The paper and existing arm/audit indexes also do not expose the Git-state split of retained data/results. In particular, the ignored v2 JSONL sessions, untracked v3 JSONL sessions, and untracked C2-T1 data file are not discoverable from a tracked-file-only artifact map. This is an artifact/provenance omission, not evidence of absent results.

The live-worktree reconciliation adds two further coverage findings. First, the 74-session V2/V3 population has 42 oracle-accepted `match=true` session verdicts and is `NOT_MENTIONED` as a result family; its duplicate-copy identity and provider/no-claim separation are not exposed in the paper. Second, untracked V4 is a wrapper-only provenance surface with no result, while ignored campaign logs contain summary-only historical outcomes that are also not mapped. Current README revisions display updated project-level numbers, but README text is documentation and does not substitute for raw-result coverage.

The outer `sp2027/agent-eval/` additions are a second major manuscript gap. The paper artifact map does not identify the 2026-10-14 contract-v3 qualification/regression controls, H1 V2 provenance control, stable-capture cohort, Claude 4.6 V3 partial cohort, or Claude 4.6 V4 12-row cohort. These should be classified separately as controls, partial campaigns, completed bounded operational evidence, and provider-failed schedules; they must not be silently pooled into E1/E2 capability denominators.
