# Experiments index — every registered cohort, browsable

Each directory is a registered cohort: its frozen registration, per-session `results.jsonl` rows,
analyses, and the sweep/summary outputs. The paper's §7.1 table (registered session inventory) counts
3,562 retained sessions across 33 cohorts; the M1 published-protocol audit is a separate 60-session population, never pooled.

| Directory | rows | artifacts | what it is (paper section) |
|---|---|---|---|
| [`blind_opportunity_chacha20_20261018/`](blind_opportunity_chacha20_20261018/) | 2 | results.jsonl,summary.json |  |
| [`blind_opportunity_ecdsa_20261018/`](blind_opportunity_ecdsa_20261018/) | 2 | results.jsonl,summary.json |  |
| [`blind_opportunity_rc4_20261018/`](blind_opportunity_rc4_20261018/) | 2 | results.jsonl,summary.json |  |
| [`cvebench_census_20261024/`](cvebench_census_20261024/) | 1 | results.jsonl,summary.json |  |
| [`diag_empty_20261103/`](diag_empty_20261103/) |  |  |  |
| [`exploratory_code_feedback_20261017/`](exploratory_code_feedback_20261017/) | 2 | results.jsonl,summary.json |  |
| [`exploratory_code_feedback_20261017_v2/`](exploratory_code_feedback_20261017_v2/) | 2 | results.jsonl,summary.json |  |
| [`exploratory_code_feedback_chacha20_20261018/`](exploratory_code_feedback_chacha20_20261018/) | 2 | results.jsonl,summary.json |  |
| [`exploratory_code_feedback_chacha20_replication_20261018/`](exploratory_code_feedback_chacha20_replication_20261018/) | 2 | results.jsonl,summary.json |  |
| [`exploratory_code_feedback_chacha20_replication_20261018_seeds56/`](exploratory_code_feedback_chacha20_replication_20261018_seeds56/) | 2 | results.jsonl,summary.json |  |
| [`exploratory_code_feedback_ecdsa_replication_20261018/`](exploratory_code_feedback_ecdsa_replication_20261018/) | 2 | results.jsonl,summary.json |  |
| [`exploratory_code_feedback_ecdsa_replication_20261018_seeds56/`](exploratory_code_feedback_ecdsa_replication_20261018_seeds56/) | 2 | results.jsonl,summary.json |  |
| [`exploratory_code_feedback_rc4_20261018/`](exploratory_code_feedback_rc4_20261018/) | 2 | results.jsonl,summary.json |  |
| [`exploratory_code_feedback_rc4_replication_20261018/`](exploratory_code_feedback_rc4_replication_20261018/) | 2 | results.jsonl,summary.json |  |
| [`exploratory_code_feedback_rc4_replication_20261018_seeds56/`](exploratory_code_feedback_rc4_replication_20261018_seeds56/) | 2 | results.jsonl,summary.json |  |
| [`exploratory_output_contract_20261017/`](exploratory_output_contract_20261017/) | 9 | results.jsonl,summary.json |  |
| [`external_admission_20261024/`](external_admission_20261024/) | 1 | results.jsonl,summary.json |  |
| [`external_admission_amend1_20261024/`](external_admission_amend1_20261024/) | 33 | results.jsonl,summary.json | the HTB grid cohort A — 31/37 vs 0/37 admission contrast (paper §7) |
| [`external_admission_amend2_20261025/`](external_admission_amend2_20261025/) |  | summary.json |  |
| [`external_admission_amend2_20261029/`](external_admission_amend2_20261029/) |  |  |  |
| [`external_admission_amend3_20261105/`](external_admission_amend3_20261105/) | 168 | results.jsonl | the NYU three-label panel cohort B — 282 programs, 0 oracle-correct, 18/282 regrade (paper §7) |
| [`external_admission_amend4_frontier_20261106/`](external_admission_amend4_frontier_20261106/) | 168 | results.jsonl |  |
| [`external_admission_amend5_transport_20261109/`](external_admission_amend5_transport_20261109/) | 36 | results.jsonl,freeze | the frontier repanel cohort C — 35/36 oracle-correct, 7/61 admission, 61/61 external (paper §7) |
| [`external_published_audit_20261110/`](external_published_audit_20261110/) | 60 | results.jsonl,freeze | the M1 published-protocol audit — 60 sessions, censoring finding, 20/50→28/50 (paper §7, abstract) |
| [`external_review_amend4_c1_20261107/`](external_review_amend4_c1_20261107/) |  |  | the blind 3-reviewer re-derivation of the headline counts (paper §7) |
| [`external_rule_admission_20261110/`](external_rule_admission_20261110/) |  |  |  |
| [`external_transfer_nondomain_20261109/`](external_transfer_nondomain_20261109/) | 16 | results.jsonl | the out-of-domain premise witness — 8/8 vs 0/8, Fisher 7.8e-5 (paper §10.2) |
| [`h2_cbc_agency_20261023/`](h2_cbc_agency_20261023/) | 8 | results.jsonl,summary.json |  |
| [`h2_no_oracle_p025_20261103/`](h2_no_oracle_p025_20261103/) | 10 | results.jsonl,summary.json | the oracle-separation control — 0/10, 256 probes (paper §6) |
| [`h2_pairs_extension_20261024/`](h2_pairs_extension_20261024/) | 20 | results.jsonl,summary.json | the 10-pair extension + the format-compliance reversal diagnosis (paper §6) |
| [`h2_pairs_powered_20261107/`](h2_pairs_powered_20261107/) | 64 | results.jsonl,summary.json | the powered 32-pair wrapper cohort — 0/32 each direction, ≤10.7% Wilson (paper §6) |
| [`info_contract_2x2_20261018/`](info_contract_2x2_20261018/) | 16 | results.jsonl,summary.json |  |
| [`info_contract_2x2_rc4_20261024/`](info_contract_2x2_rc4_20261024/) | 16 | results.jsonl,summary.json | the saturated RC4 honest null — 4/4 (paper §5) |
| [`info_contract_aesctr_20261026/`](info_contract_aesctr_20261026/) | 64 | results.jsonl,summary.json | the AES-CTR boundary run — both withheld arms 0/16 (paper §5) |
| [`info_contract_aesgcm_20261102/`](info_contract_aesgcm_20261102/) | 65 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_20261102__rerun_ar_20261103/`](info_contract_aesgcm_20261102__rerun_ar_20261103/) | 64 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_apinex_20261102/`](info_contract_aesgcm_apinex_20261102/) |  |  |  |
| [`info_contract_aesgcm_c2_floor8000_p026_20261103/`](info_contract_aesgcm_c2_floor8000_p026_20261103/) | 96 | results.jsonl,summary.json | floor-sensitivity dose-response: 53.1%→7.3% floor-exhaustion, zero acceptance at both floors (paper §5) |
| [`info_contract_aesgcm_labels_20261102/`](info_contract_aesgcm_labels_20261102/) |  |  |  |
| [`info_contract_aesgcm_labels_gpt_5_6_sol__rerun_ar_20261103/`](info_contract_aesgcm_labels_gpt_5_6_sol__rerun_ar_20261103/) | 62 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_labels_gpt_6_1_sol__rerun_ar_20261103/`](info_contract_aesgcm_labels_gpt_6_1_sol__rerun_ar_20261103/) | 62 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_p017_20261102/`](info_contract_aesgcm_p017_20261102/) | 64 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_p017_20261102__rerun_ar_20261103/`](info_contract_aesgcm_p017_20261102__rerun_ar_20261103/) | 93 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_p022a_20261102/`](info_contract_aesgcm_p022a_20261102/) | 96 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_p022a_20261102__rerun_ar_20261103/`](info_contract_aesgcm_p022a_20261102__rerun_ar_20261103/) | 96 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_p022b_20261102/`](info_contract_aesgcm_p022b_20261102/) | 96 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_p022b_20261102__rerun_ar_20261103/`](info_contract_aesgcm_p022b_20261102__rerun_ar_20261103/) | 96 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_p024a_20261103/`](info_contract_aesgcm_p024a_20261103/) | 96 | results.jsonl,summary.json | the truncation-reading closure — withholding makes every answer wrong (paper §5) |
| [`info_contract_aesgcm_p024b_20261103/`](info_contract_aesgcm_p024b_20261103/) | 96 | results.jsonl,summary.json | the printed boundary condition — consistent, under-powered at every coding (paper §5) |
| [`info_contract_aesgcm_p024b_20261103__rerun_ar_20261103/`](info_contract_aesgcm_p024b_20261103__rerun_ar_20261103/) | 96 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_random_20261102/`](info_contract_aesgcm_random_20261102/) | 96 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_random_20261102__rerun_ar_20261103/`](info_contract_aesgcm_random_20261102__rerun_ar_20261103/) | 102 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_random_p021_20261102/`](info_contract_aesgcm_random_p021_20261102/) | 385 | results.jsonl,summary.json |  |
| [`info_contract_aesgcm_random_p021ar_20261103/`](info_contract_aesgcm_random_p021ar_20261103/) | 384 | results.jsonl,summary.json | the 96-instance CSPRNG power cohort (repairs P021) — paired C1-vs-C4 96/0, Holm 4.04e-28 (paper §5, Table 3) |
| [`info_contract_aesgcm_random_p021r_20261103/`](info_contract_aesgcm_random_p021r_20261103/) | 73 | results.jsonl |  |
| [`info_contract_aesgcm_random_p023_20261103/`](info_contract_aesgcm_random_p023_20261103/) | 384 | results.jsonl,summary.json | the fresh-seed 96-instance cohort — paired 95/0 (paper §5) |
| [`info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103/`](info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103/) | 384 | results.jsonl,summary.json |  |
| [`info_contract_chachapoly_random_20261102/`](info_contract_chachapoly_random_20261102/) | 96 | results.jsonl,summary.json |  |
| [`info_contract_chachapoly_random_20261102__rerun_ar_20261103/`](info_contract_chachapoly_random_20261102__rerun_ar_20261103/) | 96 | results.jsonl,summary.json |  |
| [`info_contract_confirmatory_c1_20261107/`](info_contract_confirmatory_c1_20261107/) | 64 | results.jsonl,summary.json | the m=3 confirmatory cohort on gpt-5.6-sol — bar NOT cleared, the observability axis's prediction (paper §11) |
| [`info_contract_ecdsa_20261018/`](info_contract_ecdsa_20261018/) |  |  | the observable-premise ECDSA control — 32/32 withheld null (paper §5) |
| [`info_contract_ecdsa_20261026/`](info_contract_ecdsa_20261026/) | 66 | results.jsonl,summary.json |  |
| [`info_contract_gcmsiv_random_20261102/`](info_contract_gcmsiv_random_20261102/) | 32 | results.jsonl,summary.json | the registered negative control — accepts nothing in any cell (paper §5) |
| [`info_contract_gcmsiv_random_20261102__rerun_ar_20261103/`](info_contract_gcmsiv_random_20261102__rerun_ar_20261103/) | 35 | results.jsonl,summary.json |  |
| [`info_contract_label2_20261025/`](info_contract_label2_20261025/) | 32 | results.jsonl,summary.json |  |
| [`info_contract_label2_20261025__rerun_ar_20261103/`](info_contract_label2_20261025__rerun_ar_20261103/) | 32 | results.jsonl,summary.json |  |
| [`info_contract_label3_20261029/`](info_contract_label3_20261029/) | 32 | results.jsonl,summary.json |  |
| [`info_contract_label3_n32_20261101/`](info_contract_label3_n32_20261101/) | 129 | results.jsonl,summary.json | the n=32 scale-up + its damaged first pass and clean rerun (paper §5) |
| [`info_contract_label3_n32_20261101__rerun_ar_20261103/`](info_contract_label3_n32_20261101__rerun_ar_20261103/) | 128 | results.jsonl,summary.json |  |
| [`info_contract_label4_20261030/`](info_contract_label4_20261030/) | 32 | results.jsonl,summary.json |  |
| [`info_contract_label4_20261030__rerun_ar_20261103/`](info_contract_label4_20261030__rerun_ar_20261103/) | 32 | results.jsonl,summary.json |  |
| [`info_contract_label5_20261030/`](info_contract_label5_20261030/) | 32 | results.jsonl,summary.json |  |
| [`info_contract_label5_20261030__rerun_ar_20261103/`](info_contract_label5_20261030__rerun_ar_20261103/) | 44 | results.jsonl,summary.json |  |
| [`info_contract_label5r_20261030/`](info_contract_label5r_20261030/) | 32 | results.jsonl,summary.json |  |
| [`info_contract_label5r_20261030__rerun_ar_20261103/`](info_contract_label5r_20261030__rerun_ar_20261103/) | 44 | results.jsonl,summary.json |  |
| [`info_contract_n16_20261026/`](info_contract_n16_20261026/) | 64 | results.jsonl,summary.json |  |
| [`info_contract_p010_driftcheck_20261026/`](info_contract_p010_driftcheck_20261026/) | 17 | results.jsonl,summary.json |  |
| [`info_contract_powered_20261025/`](info_contract_powered_20261025/) | 32 | results.jsonl,summary.json |  |
| [`info_contract_x1_gptoss_20261026/`](info_contract_x1_gptoss_20261026/) | 67 | results.jsonl,summary.json |  |
| [`paper_tables_20261103/`](paper_tables_20261103/) |  |  |  |
| [`provider_health_20261023/`](provider_health_20261023/) |  |  |  |

## Top-level records

| File | What it carries |
|---|---|
| [`ACTS_ATTACK_FINAL_EVIDENCE_INDEX.csv`](ACTS_ATTACK_FINAL_EVIDENCE_INDEX.csv) | campaign-level record |
| [`ACTS_ATTACK_FINAL_SCIENTIFIC_SYNTHESIS.md`](ACTS_ATTACK_FINAL_SCIENTIFIC_SYNTHESIS.md) | campaign-level record |
| [`ACTS_MULTITIER_LOCAL_RECONCILIATION.md`](ACTS_MULTITIER_LOCAL_RECONCILIATION.md) | campaign-level record |
| [`ARCHIVE_JOIN_AUDIT_20261018.json`](ARCHIVE_JOIN_AUDIT_20261018.json) | campaign-level record |
| [`ARCHIVE_PROVENANCE_MATRIX.csv`](ARCHIVE_PROVENANCE_MATRIX.csv) | campaign-level record |
| [`BACKLOG.md`](BACKLOG.md) | campaign-level record |
| [`BLIND_OPPORTUNITY_CONTRAST_20261018.json`](BLIND_OPPORTUNITY_CONTRAST_20261018.json) | campaign-level record |
| [`BLIND_OPPORTUNITY_CONTRAST_20261018.md`](BLIND_OPPORTUNITY_CONTRAST_20261018.md) | campaign-level record |
| [`BUDGET_LEDGER.jsonl`](BUDGET_LEDGER.jsonl) | campaign-level record |
| [`C3_SERVICE_RELAY_QUALIFICATION_20261018.md`](C3_SERVICE_RELAY_QUALIFICATION_20261018.md) | campaign-level record |
| [`C3_TARGET_QUALIFICATION_20261018.md`](C3_TARGET_QUALIFICATION_20261018.md) | campaign-level record |
| [`CENSUS_P_PROVIDER_20261103.json`](CENSUS_P_PROVIDER_20261103.json) | campaign-level record |
| [`CENSUS_P_PROVIDER_20261103.md`](CENSUS_P_PROVIDER_20261103.md) | campaign-level record |
| [`CENSUS_P_PROVIDER_20261103_CORRECTED.json`](CENSUS_P_PROVIDER_20261103_CORRECTED.json) | campaign-level record |
| [`CLAIM_MATRIX_AUDIT.json`](CLAIM_MATRIX_AUDIT.json) | campaign-level record |
| [`CLAIM_MATRIX_AUDIT.md`](CLAIM_MATRIX_AUDIT.md) | campaign-level record |
| [`COMMIT_MESSAGE_P021_P022.txt`](COMMIT_MESSAGE_P021_P022.txt) | campaign-level record |
| [`COMPARISON_P021_P023.json`](COMPARISON_P021_P023.json) | campaign-level record |
| [`COMPARISON_P021_P023.md`](COMPARISON_P021_P023.md) | campaign-level record |
| [`COMPARISON_P021_P023_by_position.csv`](COMPARISON_P021_P023_by_position.csv) | campaign-level record |
| [`COMPARISON_P022_P024.json`](COMPARISON_P022_P024.json) | campaign-level record |
| [`COMPARISON_P022_P024.md`](COMPARISON_P022_P024.md) | campaign-level record |
| [`CROSS_FAMILY_STAGE_ANALYSIS.csv`](CROSS_FAMILY_STAGE_ANALYSIS.csv) | campaign-level record |
| [`CROSS_FAMILY_STAGE_ANALYSIS.json`](CROSS_FAMILY_STAGE_ANALYSIS.json) | campaign-level record |
| [`CROSS_FAMILY_STAGE_ANALYSIS.md`](CROSS_FAMILY_STAGE_ANALYSIS.md) | campaign-level record |
| [`DECISION_LOG.md`](DECISION_LOG.md) | campaign-level record |
| [`EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md`](EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md) | campaign-level record |
| [`EVIDENCE_SCIENCE_INTEGRATION.md`](EVIDENCE_SCIENCE_INTEGRATION.md) | campaign-level record |
| [`EXPERIMENT_INDEX.csv`](EXPERIMENT_INDEX.csv) | campaign-level record |
| [`FINAL_RECOVERY_20261103.log`](FINAL_RECOVERY_20261103.log) | campaign-level record |
| [`H1_V2_FAILURE_STAGE_AUDIT.md`](H1_V2_FAILURE_STAGE_AUDIT.md) | campaign-level record |
| [`H1_V2_FAILURE_STAGE_MATRIX.csv`](H1_V2_FAILURE_STAGE_MATRIX.csv) | campaign-level record |
| [`H1_V2_FAILURE_STAGE_SUMMARY.json`](H1_V2_FAILURE_STAGE_SUMMARY.json) | campaign-level record |
| [`KIMI_FINISH_20261103.log`](KIMI_FINISH_20261103.log) | campaign-level record |
| [`KIMI_SEQUENTIAL_20261103.log`](KIMI_SEQUENTIAL_20261103.log) | campaign-level record |
| [`MANUSCRIPT_ARTIFACT_REPRO_STATUS.md`](MANUSCRIPT_ARTIFACT_REPRO_STATUS.md) | campaign-level record |
| [`MATCHED_REPLICATION_DESIGN.md`](MATCHED_REPLICATION_DESIGN.md) | campaign-level record |
| [`MATCHED_REPLICATION_EXTENDED_20261018.md`](MATCHED_REPLICATION_EXTENDED_20261018.md) | campaign-level record |
| [`MATCHED_REPLICATION_EXTENDED_SUMMARY.json`](MATCHED_REPLICATION_EXTENDED_SUMMARY.json) | campaign-level record |
| [`MATCHED_REPLICATION_REPORT.md`](MATCHED_REPLICATION_REPORT.md) | campaign-level record |
| [`MATCHED_REPLICATION_SUMMARY.json`](MATCHED_REPLICATION_SUMMARY.json) | campaign-level record |
| [`MISSION.md`](MISSION.md) | campaign-level record |
| [`NEXT_RUN.md`](NEXT_RUN.md) | campaign-level record |
| [`NOVELTY_FULLTEXT_REVIEW.md`](NOVELTY_FULLTEXT_REVIEW.md) | campaign-level record |
| [`NOVELTY_MATRIX.json`](NOVELTY_MATRIX.json) | campaign-level record |
| [`NOVELTY_MATRIX.md`](NOVELTY_MATRIX.md) | campaign-level record |
| [`P018_PARALLEL.log`](P018_PARALLEL.log) | campaign-level record |
| [`PAPER_CLAIM_MATRIX.csv`](PAPER_CLAIM_MATRIX.csv) | campaign-level record |
| [`PAPER_EVIDENCE_20261103.json`](PAPER_EVIDENCE_20261103.json) | campaign-level record |
| [`PAPER_EVIDENCE_20261103.md`](PAPER_EVIDENCE_20261103.md) | campaign-level record |
| [`PARALLEL_WAVE_20261103.log`](PARALLEL_WAVE_20261103.log) | campaign-level record |
| [`PHASES_1_3_SUMMARY_20261024.md`](PHASES_1_3_SUMMARY_20261024.md) | campaign-level record |
| [`POLICY_ATTACK_TRAJECTORY_AUDIT.md`](POLICY_ATTACK_TRAJECTORY_AUDIT.md) | campaign-level record |
| [`POLICY_ATTACK_TRAJECTORY_MATRIX.csv`](POLICY_ATTACK_TRAJECTORY_MATRIX.csv) | campaign-level record |
| [`POLICY_SIDECHANNEL_BINARY_PQC_CONTEXT.md`](POLICY_SIDECHANNEL_BINARY_PQC_CONTEXT.md) | campaign-level record |
| [`POSITION_CLUSTER_P021_P023.json`](POSITION_CLUSTER_P021_P023.json) | campaign-level record |
| [`POSITION_CLUSTER_P021_P023.md`](POSITION_CLUSTER_P021_P023.md) | campaign-level record |
| [`POSITION_MATRIX_P021.csv`](POSITION_MATRIX_P021.csv) | campaign-level record |
| [`POSITION_MATRIX_P023.csv`](POSITION_MATRIX_P023.csv) | campaign-level record |
| [`PQC_FAMILY_RECONCILIATION.md`](PQC_FAMILY_RECONCILIATION.md) | campaign-level record |
| [`PQC_POLICY_ATTACK_AUDIT.md`](PQC_POLICY_ATTACK_AUDIT.md) | campaign-level record |
| [`RECOVERY_20261103.log`](RECOVERY_20261103.log) | campaign-level record |
| [`REMAINING_EXPERIMENTS_PLAN_20261023.md`](REMAINING_EXPERIMENTS_PLAN_20261023.md) | campaign-level record |
| [`RERUN_QUEUE_20261103.log`](RERUN_QUEUE_20261103.log) | campaign-level record |
| [`RERUN_SPECS_20261103.json`](RERUN_SPECS_20261103.json) | campaign-level record |
| [`RERUN_VS_ORIGINAL_20261103.json`](RERUN_VS_ORIGINAL_20261103.json) | campaign-level record |
| [`RERUN_VS_ORIGINAL_20261103.md`](RERUN_VS_ORIGINAL_20261103.md) | campaign-level record |
| [`RESEARCH_STATE.json`](RESEARCH_STATE.json) | campaign-level record |
| [`RESUME_20261103.log`](RESUME_20261103.log) | campaign-level record |
| [`SCIENCE_LEDGER.jsonl`](SCIENCE_LEDGER.jsonl) | campaign-level record |
| [`SEMANTIC_CLOSURE_STATUS.md`](SEMANTIC_CLOSURE_STATUS.md) | campaign-level record |
| [`SEMANTIC_JOIN_STATUS.md`](SEMANTIC_JOIN_STATUS.md) | campaign-level record |
| [`V4_TRAJECTORY_AUDIT.md`](V4_TRAJECTORY_AUDIT.md) | campaign-level record |
| [`V4_TRAJECTORY_MATRIX.csv`](V4_TRAJECTORY_MATRIX.csv) | campaign-level record |
| [`V4_TRAJECTORY_SUMMARY.json`](V4_TRAJECTORY_SUMMARY.json) | campaign-level record |
| [`WAVE2_20261103.log`](WAVE2_20261103.log) | campaign-level record |
| [`WAVE3_20261103.log`](WAVE3_20261103.log) | campaign-level record |
| [`WORK_GRAPH.json`](WORK_GRAPH.json) | campaign-level record |
| [`_shard_worker.py`](_shard_worker.py) | campaign-level record |
| [`amend3_full_stdout_rescan.json`](amend3_full_stdout_rescan.json) | campaign-level record |
| [`analysis_info_contract_2x2.py`](analysis_info_contract_2x2.py) | campaign-level record |
| [`analyze_code_feedback_exploration.py`](analyze_code_feedback_exploration.py) | campaign-level record |
| [`analyze_initial_evidence.py`](analyze_initial_evidence.py) | campaign-level record |
| [`analyze_random_cohort.py`](analyze_random_cohort.py) | campaign-level record |
| [`analyze_rerun_vs_original.py`](analyze_rerun_vs_original.py) | campaign-level record |
| [`analyze_v4_trajectories.py`](analyze_v4_trajectories.py) | campaign-level record |
| [`apmix_entitlement_20261102.json`](apmix_entitlement_20261102.json) | campaign-level record |
| [`apmix_entitlement_20261102.py`](apmix_entitlement_20261102.py) | campaign-level record |
| [`append_budget_p014.py`](append_budget_p014.py) | campaign-level record |
| [`append_budget_to_ledger.py`](append_budget_to_ledger.py) | campaign-level record |
| [`audit_claim_matrix.py`](audit_claim_matrix.py) | campaign-level record |
| [`audit_scale_inventory.py`](audit_scale_inventory.py) | campaign-level record |
| [`build_cross_family_stage_analysis.py`](build_cross_family_stage_analysis.py) | campaign-level record |
| [`build_p024_registration.py`](build_p024_registration.py) | campaign-level record |
| [`build_paper_evidence_20261103.py`](build_paper_evidence_20261103.py) | campaign-level record |
| [`census_p_provider.json`](census_p_provider.json) | campaign-level record |
| [`census_p_provider.py`](census_p_provider.py) | campaign-level record |
| [`census_p_provider_corrected.py`](census_p_provider_corrected.py) | campaign-level record |
| [`chain_compare_p021_p023.log`](chain_compare_p021_p023.log) | campaign-level record |
| [`chain_compare_p022_p024.log`](chain_compare_p022_p024.log) | campaign-level record |
| [`chain_p018_p020.log`](chain_p018_p020.log) | campaign-level record |
| [`chain_p021.log`](chain_p021.log) | campaign-level record |
| [`chain_p022.log`](chain_p022.log) | campaign-level record |
| [`chain_p023.log`](chain_p023.log) | campaign-level record |
| [`chain_p024.log`](chain_p024.log) | campaign-level record |
| [`chain_position_cluster.log`](chain_position_cluster.log) | campaign-level record |
| [`compare_p021_p023.py`](compare_p021_p023.py) | campaign-level record |
| [`compare_p022_p024.py`](compare_p022_p024.py) | campaign-level record |
| [`final_synthesis_validation.jsonl`](final_synthesis_validation.jsonl) | campaign-level record |
| [`fixtures_aead_modern.py`](fixtures_aead_modern.py) | campaign-level record |
| [`h1_campaign.py`](h1_campaign.py) | campaign-level record |
| [`labels_probe_20261102.json`](labels_probe_20261102.json) | campaign-level record |
| [`leakscan_info_contract_2x2.py`](leakscan_info_contract_2x2.py) | campaign-level record |
| [`p023_parallel.log`](p023_parallel.log) | campaign-level record |
| [`parallelize_cohort.py`](parallelize_cohort.py) | campaign-level record |
| [`position_cluster_p021_p023.py`](position_cluster_p021_p023.py) | campaign-level record |
| [`preflight_info_contract_2x2.py`](preflight_info_contract_2x2.py) | campaign-level record |
| [`probe_labels_20261102.py`](probe_labels_20261102.py) | campaign-level record |
| [`probe_p024_failures.jsonl`](probe_p024_failures.jsonl) | campaign-level record |
| [`probe_p024_floor.json`](probe_p024_floor.json) | campaign-level record |
| [`probe_p024_floor.py`](probe_p024_floor.py) | campaign-level record |
| [`provider_adapter_agentrouter.py`](provider_adapter_agentrouter.py) | campaign-level record |
| [`provider_adapter_agentrouter_p016_floor2800.py`](provider_adapter_agentrouter_p016_floor2800.py) | campaign-level record |
| [`provider_adapter_agentrouter_p017.py`](provider_adapter_agentrouter_p017.py) | campaign-level record |
| [`provider_adapter_agentrouter_p023.py`](provider_adapter_agentrouter_p023.py) | campaign-level record |
| [`provider_adapter_agentrouter_p024.py`](provider_adapter_agentrouter_p024.py) | campaign-level record |
| [`provider_adapter_agentrouter_p024b_floor8400.py`](provider_adapter_agentrouter_p024b_floor8400.py) | campaign-level record |
| [`provider_adapter_agentrouter_p026_floor8000.py`](provider_adapter_agentrouter_p026_floor8000.py) | campaign-level record |
| [`provider_adapter_apinex.py`](provider_adapter_apinex.py) | campaign-level record |
| [`provider_adapter_apinex_l6.py`](provider_adapter_apinex_l6.py) | campaign-level record |
| [`provider_adapter_apinex_l6_paced.py`](provider_adapter_apinex_l6_paced.py) | campaign-level record |
| [`provider_adapter_apinex_p021.py`](provider_adapter_apinex_p021.py) | campaign-level record |
| [`recover_transport_rows.py`](recover_transport_rows.py) | campaign-level record |
| [`recovery_p016a.log`](recovery_p016a.log) | campaign-level record |
| [`recovery_p017.log`](recovery_p017.log) | campaign-level record |
| [`refamily_info_contract.py`](refamily_info_contract.py) | campaign-level record |
| [`register_instance_seeds.py`](register_instance_seeds.py) | campaign-level record |
| [`rerun_ar_clone.py`](rerun_ar_clone.py) | campaign-level record |
| [`rerun_ar_cohort.py`](rerun_ar_cohort.py) | campaign-level record |
| [`rerun_ar_queue.sh`](rerun_ar_queue.sh) | campaign-level record |
| [`rerun_p016_arm.py`](rerun_p016_arm.py) | campaign-level record |
| [`resume_all_after_quota.sh`](resume_all_after_quota.sh) | campaign-level record |
| [`route_probe2_20261102.json`](route_probe2_20261102.json) | campaign-level record |
| [`route_probe2_20261102.py`](route_probe2_20261102.py) | campaign-level record |
| [`route_probe_20261102.json`](route_probe_20261102.json) | campaign-level record |
| [`route_probe_20261102.py`](route_probe_20261102.py) | campaign-level record |
| [`run_code_feedback_chacha20.py`](run_code_feedback_chacha20.py) | campaign-level record |
| [`run_code_feedback_exploration.py`](run_code_feedback_exploration.py) | campaign-level record |
| [`run_code_feedback_exploration_v2.py`](run_code_feedback_exploration_v2.py) | campaign-level record |
| [`run_code_feedback_rc4.py`](run_code_feedback_rc4.py) | campaign-level record |
| [`run_final_recovery.sh`](run_final_recovery.sh) | campaign-level record |
| [`run_info_contract_2x2_aesctr.py`](run_info_contract_2x2_aesctr.py) | campaign-level record |
| [`run_info_contract_2x2_aesgcm.py`](run_info_contract_2x2_aesgcm.py) | campaign-level record |
| [`run_info_contract_2x2_chacha20.py`](run_info_contract_2x2_chacha20.py) | campaign-level record |
| [`run_info_contract_2x2_ecdsa.py`](run_info_contract_2x2_ecdsa.py) | campaign-level record |
| [`run_kimi_finish.sh`](run_kimi_finish.sh) | campaign-level record |
| [`run_kimi_sequential.sh`](run_kimi_sequential.sh) | campaign-level record |
| [`run_modern_aead_cohort.py`](run_modern_aead_cohort.py) | campaign-level record |
| [`run_output_contract_exploration.py`](run_output_contract_exploration.py) | campaign-level record |
| [`run_parallel_wave.sh`](run_parallel_wave.sh) | campaign-level record |
| [`run_recovery_after_recharge.sh`](run_recovery_after_recharge.sh) | campaign-level record |
| [`run_wave2_after_queue.sh`](run_wave2_after_queue.sh) | campaign-level record |
| [`run_wave3_after_resume.sh`](run_wave3_after_resume.sh) | campaign-level record |
| [`schedule_chain_p018_p020.sh`](schedule_chain_p018_p020.sh) | campaign-level record |
| [`schedule_compare_p021_p023.sh`](schedule_compare_p021_p023.sh) | campaign-level record |
| [`schedule_compare_p022_p024.sh`](schedule_compare_p022_p024.sh) | campaign-level record |
| [`schedule_p021.sh`](schedule_p021.sh) | campaign-level record |
| [`schedule_p022.sh`](schedule_p022.sh) | campaign-level record |
| [`schedule_p023.sh`](schedule_p023.sh) | campaign-level record |
| [`schedule_p024.sh`](schedule_p024.sh) | campaign-level record |
| [`schedule_position_cluster.sh`](schedule_position_cluster.sh) | campaign-level record |
| [`score_output_contract_exploration.py`](score_output_contract_exploration.py) | campaign-level record |
| [`seeds_random_20261102T104901Z.json`](seeds_random_20261102T104901Z.json) | campaign-level record |
| [`seeds_random_20261102T105650Z.json`](seeds_random_20261102T105650Z.json) | campaign-level record |
| [`seeds_random_20261103T080050Z.json`](seeds_random_20261103T080050Z.json) | campaign-level record |
| [`seeds_random_p020_20261102T1057Z.json`](seeds_random_p020_20261102T1057Z.json) | campaign-level record |
| [`seeds_random_p021_20261102T182345Z.json`](seeds_random_p021_20261102T182345Z.json) | campaign-level record |
| [`seeds_random_p022_20261102T183823Z.json`](seeds_random_p022_20261102T183823Z.json) | campaign-level record |
| [`seeds_random_p024_20261103.json`](seeds_random_p024_20261103.json) | campaign-level record |
| [`selftest_modern_aead.py`](selftest_modern_aead.py) | campaign-level record |
| [`shard_base_main.py`](shard_base_main.py) | campaign-level record |
| [`smoke_p023_failures.jsonl`](smoke_p023_failures.jsonl) | campaign-level record |
| [`smoke_p023_transport.json`](smoke_p023_transport.json) | campaign-level record |
| [`smoke_p023_transport.py`](smoke_p023_transport.py) | campaign-level record |
| [`sweep_label5.log`](sweep_label5.log) | campaign-level record |
| [`verify_final_synthesis.py`](verify_final_synthesis.py) | campaign-level record |
