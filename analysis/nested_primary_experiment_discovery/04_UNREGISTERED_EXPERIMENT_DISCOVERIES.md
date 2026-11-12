# Unregistered experiment discoveries

The corrected repository-first scan covers all 465 non-Git files in the nested `ACTS-ATTACK` working tree. It found a wider evidence surface than the named 35-arm paper registry and did not restrict discovery to `data/`, `results/`, or `results_rerun/`.

1. **C2b 3x3 hybrid-policy control.** This is not merely a summary: it has 45 handshakes, 90 endpoint traces, 9 complete cells, five repetitions per cell, zero trace disagreements, an independent verdict parser, and a causal contrast where only the server `-groups` policy changes. It supports local policy enforcement, not an ML-KEM break.
2. **C2b smoke control.** `harness/results_c2b_smoke/` retains a separate one-repetition 9-cell matrix with 9 records, 7 classical outcomes, 2 rejects, and zero trace disagreements. It is a control/smoke cohort, not a second 45-run replication.
3. **Fixed-operation rerun with oracle ownership.** `results_rerun/` retains 12 fresh-secret operations, 3 per cryptographic task, with executor and independent-oracle spans. Every operation is accepted 3/3. This is stronger evidence for implementation/oracle validity than the historical aggregate, but it is not an agent-capability cohort.
4. **C2-T1 toolchain-diversity reproduction.** The record retains three open-pipeline runs with 3/3 wire-format validity and 3/3 ASR, plus a comparison to the original pipeline. The record explicitly says `r2_verified=false`; it supports a protocol-edit reproduction, not complete binary-analysis reproduction.
5. **Historical aggregate and agent rerun families.** The nested checkout retains a 21-run aggregate, a 54-row mixed-provider agent rerun, 22 excluded rows, and a 74-session historical tree. These are not interchangeable. The v2 and v3 trees are exact copies: 74/74 filenames and SHA-256 hashes match, so they are one historical population, not 148 runs.
6. **Separate A1/D1/B1 records.** The repository retains both negative and positive A1 timing environments, a partial Bernstein recovery (2/16), an exact Spread-Table result (16/16 against a known key), and a four-model L1-L5 safety evaluation. These were parsed directly from JSON records.

## Non-results retained as evidence

AUTH_FLAW, KNOWN_VULN, SSH_WEAK_ALGO, TLS_POLICY_HYBRID, and subsets of CBC/ECDSA appear in session output trees, but many terminate in provider, parser, no-claim, or relay errors. They are retained execution history, not completed campaigns. Provider-unavailable, no-claim, and harness-defect states must remain separate from attack failures.

## Deduplication decisions

- The two C2-T1 JSON filenames contain the same experiment/result content and are one result.
- v2 and v3 contain identical bytes for all 74 JSONL files and are one historical population.
- C2, C2b, C2-T1, fixed-operation rerun, historical aggregate, and agent rerun are distinct cohorts even when task names overlap.
- Summaries, copies, and migrated transcripts are not counted as new physical observations.

## Git-state discoveries that must not be omitted

The result inventory was reconciled against Git in addition to walking the filesystem. \`data/c2t1_toolchain_diversity_repro.json\` is an untracked, nonignored data result. \`harness/v2/results/e2/_loop_out/\` contains 74 ignored JSONL session files, while \`harness/v3/results/e2/_loop_out/\` contains 74 untracked, nonignored JSONL session files. Tracked \`results/\`, \`results_rerun/\`, the C2b smoke/PQ/H1B result directories, and \`harness/rerun/results_rerun/\` were included as well.

The v2 and v3 74-file session sets have identical per-file hashes, so they do not provide 148 independent observations. They do provide distinct retained directory/Git-state lineage. Ignored or untracked status is a provenance limitation, not evidence that the experiment did not occur. The complete per-file state is in \`02_COMPLETE_RAW_EXPERIMENT_INVENTORY.csv\`.

7. **V3/V2 multi-condition session population.** The tracked-file index alone hides 74 JSONL session files: 74 ignored under `harness/v2/` and 74 untracked under `harness/v3/`. After byte-level deduplication, they retain 42 oracle-accepted `match=true` sessions across RC4, ChaCha20, crypto-misuse, and parsing-overflow conditions, alongside provider failures, no-claim terminals, and errors. This is a historical/session-level result family, not a clean capability estimate.
8. **V4 wrapper lineage.** The untracked `harness/v4/` directory is a three-file wrapper around V3 and contains no result records. It is a provenance/configuration artifact, not a completed benchmark.

9. **Outer agent-evaluation campaign branches.** The current outer worktree contains a newer `sp2027/agent-eval/` surface with contract-v3 qualification/regression, H1 V2 provenance control, stable capture, Claude 4.6 V3/V4 clean-capture cohorts, and provider-failed continuation branches. The strongest newly discovered completed capability-like record is the Claude 4.6 V4 12-row cohort (8 SUCCESS, 4 ORACLE_FAIL); the strongest control records are contract-v3 and H1 V2. These were not present as result-level entries in the earlier nested/35-arm discovery and must remain separate from older E2 populations.
