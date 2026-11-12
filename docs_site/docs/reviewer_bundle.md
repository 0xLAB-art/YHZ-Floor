# The reviewer bundle

The `reviewer_bundle/` directory in the repository is the curated offline projection (24,023 manifest files). Its own README, reproduced below, describes its contents, verification commands, and exclusion boundaries.

---
# Anonymous reviewer candidate (2026-11-11)

Locally prepared for anonymous review; not uploaded or published. This is an explicitly reduced anonymous projection of the private full candidate, not the entire full package.

The H1-R3 component includes 852 retained sessions and the original sandboxed execute_replay.py. Its retained programs, fixture state, prompts and outputs are byte-preserving copies. Executing retained programs checks outputs; it does not regenerate model responses. See the component README for execution requirements and commands. No experimental evaluation was run while preparing this projection.

The experiment_b, crossboundary/build and heb1_remediation trees retain the anonymous ablation evidence and original policy implementations. These constructed cases establish bounded policy behavior, not deployed failure prevalence or independent benchmark replication.

The external-boundary wave evidence (Amendment-1 regrade lab, Amendment-3/4/5 admission records, the C1 confirmatory review, and the M1 published-protocol audit under namespace external_published_audit_20261110) ships as byte-preserving copies of the frozen per-session records: results.jsonl rows, per-session prompts and raw provider responses, the registered preregistrations, amendments, the ERRATUM_accepted_c2 record, and M1_FINAL_RESULTS. These are the records behind Section 7's external-boundary numbers and the allowance-dependence finding; they are retained observations, not a fresh execution.

The fixed-executor operation_records.jsonl contains the historical twelve recorded successes whose executor clock medians match the manuscript: RC4 0.214196 ms, ChaCha20 0.131647 ms, CBC 1981.556789 ms, ECDSA 6.956233 ms. These are recorded observations, not freshly verified operations. A different later file with the same basename has different clocks and is deliberately not pooled with this cohort.

Identifying signed RQ3 property certificates, their observation records, original provider/archive wrappers, declared-author LaTeX sources and identifying in-toto runner sources remain in the separate private full candidate. Their exclusion preserves signed originals without redaction or re-signing. This projection therefore does not independently reproduce all property-check and in-toto claims. Synthetic fixture truth and synthetic test keys included here are evaluation materials.

COPY_LINEAGE.json preserves copied payload hashes. MANIFEST.json describes this projection independently of original nested manifests. Inspect without executing experiments:

    python3 -B offline_checks.py verify
