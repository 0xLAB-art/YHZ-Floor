# E1-E6 evidence-science integration

This integration preserves evidence science as a boundary on attack claims,
not as a substitute for attack experiments.

| Evidence family | Direct retained observation | What it changes | What it cannot establish |
|---|---|---|---|
| E1 release/source integrity | SHA-pinned release records; CVE-Bench and WebSP-Eval clone verification; remaining release limitations retained | Makes source version and inspectability claim-relative | Historical execution identity or complete run linkage for every release |
| E2 capture/key separation | Frozen cards, dual clocks, explicit statuses, break-tested oracles, escrow-separated secret comparison | Supports reconstruction of agent-to-oracle paths and secret authority | Total oracle independence or absence of every host-side escape path |
| E3 timing calibration | Warm pooled medians 0.761 ms and 2.350 ms; paired factor contrast -1.759 ms; distinct trial/cell/factor/bootstrap quantities | Prevents clock-definition substitutions and overprecise timing claims | Cross-host or general latency inference |
| E4 outcome/interpretation | Retained retrospective rescoring and failure/outage boundaries | Separates operational yield, conditional yield, and evaluator interpretation | A causal model-capability effect from retrospective labels |
| E5 protocol-bound cohort | E5 escrow commits, canonical 29-record reconstruction, R30 candidate/commitment match, and oracle identity discrepancy | Preserves verified candidate relation while downgrading unsupported provenance/security claims | Proof that every recorded oracle identity or environment boundary is correct |
| E6 annotation reliability | Four annotators, 30 frozen items, Fleiss kappa 0.418, raw agreement 0.594; six ties adjudicated | Exposes codebook ambiguity and keeps adjudication visible | Objective truth of labels or a replacement for raw attack/oracle evidence |

The combined rule is: an accepted cryptographic attack requires candidate/oracle
linkage; an evaluator or provenance result requires its own direct artifact;
and missing evidence remains a scope limitation rather than a negative attack
result. E1-E6 therefore refine the interpretation of the attack-centered
results but do not replace them.

Primary retained artifacts include `sp2027/ledger/E1_SHA_PINNING.md`,
`sp2027/ledger/E5_COMMITS.md`,
`sp2027/paper/split_rebuild_evidence_promotion/E5_ENVIRONMENT_AND_BENCHMARK_TRACE.md`,
`sp2027/paper/split_rebuild_evidence_promotion/E3_ESTIMATOR_CONSISTENCY_REPORT.md`,
and `sp2027/annotators/round1/ADJUDICATION_E6_R1.md`.
