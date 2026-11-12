# Experiments index — every record directory, browsable

One row per record directory under [`experiments/`](.). "rows" is the exact line count of
the directory's append-only `results.jsonl` ("—" where the cohort records outcomes only in
per-slot or summary files). "§" is the section of the accompanying manuscript the record
backs — the manuscript itself travels through the venue's submission system and is not
served here. Registered cohorts, diagnostics, controls and superseded first passes all
appear; nothing is pooled and nothing is hidden.

| Directory | rows | What it is | § |
|---|---:|---|---|
| [`blind_opportunity_chacha20_20261018/`](blind_opportunity_chacha20_20261018/) | 2 | the ChaCha20 blind-opportunity diagnostic | §4 |
| [`blind_opportunity_ecdsa_20261018/`](blind_opportunity_ecdsa_20261018/) | 2 | the ECDSA blind-opportunity diagnostic | §4 |
| [`blind_opportunity_rc4_20261018/`](blind_opportunity_rc4_20261018/) | 2 | the RC4 blind-opportunity diagnostic | §4 |
| [`cvebench_census_20261024/`](cvebench_census_20261024/) | 1 | the CVE-Bench census — 40 web-CVE targets, zero crypto | §7 |
| [`diag_empty_20261103/`](diag_empty_20261103/) | — | the empty-diagnostic control | §5 |
| [`exploratory_code_feedback_20261017/`](exploratory_code_feedback_20261017/) | 2 | the exploratory code-feedback probe (pre-registered cohort era) | §8 |
| [`exploratory_code_feedback_20261017_v2/`](exploratory_code_feedback_20261017_v2/) | 2 | the second pass of the code-feedback probe | §8 |
| [`exploratory_code_feedback_chacha20_20261018/`](exploratory_code_feedback_chacha20_20261018/) | 2 | the ChaCha20 code-feedback probe | §8 |
| [`exploratory_code_feedback_chacha20_replication_20261018/`](exploratory_code_feedback_chacha20_replication_20261018/) | 2 | the ChaCha20 code-feedback replication | §8 |
| [`exploratory_code_feedback_chacha20_replication_20261018_seeds56/`](exploratory_code_feedback_chacha20_replication_20261018_seeds56/) | 2 | the ChaCha20 replication, seeds-56 variant | §8 |
| [`exploratory_code_feedback_ecdsa_replication_20261018/`](exploratory_code_feedback_ecdsa_replication_20261018/) | 2 | the ECDSA code-feedback replication | §8 |
| [`exploratory_code_feedback_ecdsa_replication_20261018_seeds56/`](exploratory_code_feedback_ecdsa_replication_20261018_seeds56/) | 2 | the ECDSA replication, seeds-56 variant | §8 |
| [`exploratory_code_feedback_rc4_20261018/`](exploratory_code_feedback_rc4_20261018/) | 2 | the RC4 code-feedback probe | §8 |
| [`exploratory_code_feedback_rc4_replication_20261018/`](exploratory_code_feedback_rc4_replication_20261018/) | 2 | the RC4 code-feedback replication | §8 |
| [`exploratory_code_feedback_rc4_replication_20261018_seeds56/`](exploratory_code_feedback_rc4_replication_20261018_seeds56/) | 2 | the RC4 replication, seeds-56 variant | §8 |
| [`exploratory_output_contract_20261017/`](exploratory_output_contract_20261017/) | 9 | the output-contract exploration probe (pre-registered cohort era) | §8 |
| [`external_admission_20261024/`](external_admission_20261024/) | 1 | the single-session external-admission qualification probe | §7 |
| [`external_admission_amend1_20261024/`](external_admission_amend1_20261024/) | 33 | the HTB grid cohort A — 31/37 vs 0/37 admission contrast | §7 |
| [`external_admission_amend2_20261025/`](external_admission_amend2_20261025/) | — | the Amend-2 first pass, superseded by the 20261029 qualification cohort | §7 |
| [`external_admission_amend2_20261029/`](external_admission_amend2_20261029/) | — | the Amend-2 registration + qualification arms | §7 |
| [`external_admission_amend3_20261105/`](external_admission_amend3_20261105/) | 168 | the NYU three-label panel cohort B — 282 programs, 0 oracle-correct, 18/282 regrade | §7 |
| [`external_admission_amend4_frontier_20261106/`](external_admission_amend4_frontier_20261106/) | 168 | the Amend-4 frontier panel on the damaged transport — superseded by the Amend-5 repanel | §7 |
| [`external_admission_amend5_transport_20261109/`](external_admission_amend5_transport_20261109/) | 36 | the Amend-5 frontier repanel on the visible-completion transport — 35/36 oracle-correct, 7/61 admission, 61/61 external | §7 |
| [`external_published_audit_20261110/`](external_published_audit_20261110/) | 60 | the M1 published-protocol audit — 60 sessions, the censoring finding, 20/50 → 28/50 | §7 |
| [`external_review_amend4_c1_20261107/`](external_review_amend4_c1_20261107/) | — | the blind 3-reviewer re-derivation of the headline counts | §7 |
| [`external_rule_admission_20261110/`](external_rule_admission_20261110/) | — | the external-rule admission read on the frozen windows | §7 |
| [`external_transfer_nondomain_20261109/`](external_transfer_nondomain_20261109/) | 16 | the out-of-domain premise witness — 8/8 vs 0/8, exact Fisher 7.77e-5 | §10.2 |
| [`h2_cbc_agency_20261023/`](h2_cbc_agency_20261023/) | 8 | the CBC agency probe cohort | §6 |
| [`h2_no_oracle_p025_20261103/`](h2_no_oracle_p025_20261103/) | 10 | the oracle-separation control — 0/10 with 256 probes | §6 |
| [`h2_pairs_extension_20261024/`](h2_pairs_extension_20261024/) | 20 | the 10-pair wrapper extension + the format-compliance reversal diagnosis | §6 |
| [`h2_pairs_powered_20261107/`](h2_pairs_powered_20261107/) | 64 | the powered 32-pair wrapper cohort — 0/32 each direction, ≤10.7% Wilson upper | §6 |
| [`info_contract_2x2_20261018/`](info_contract_2x2_20261018/) | 16 | the original 2×2 factorial that isolated the zero-reference premise | §5 |
| [`info_contract_2x2_rc4_20261024/`](info_contract_2x2_rc4_20261024/) | 16 | the saturated RC4 honest null — 4/4 | §5 |
| [`info_contract_aesctr_20261026/`](info_contract_aesctr_20261026/) | 64 | the AES-CTR boundary run — both withheld arms 0/16 | §5 |
| [`info_contract_aesgcm_20261102/`](info_contract_aesgcm_20261102/) | 65 | the AES-GCM cohort opening the modern-AEAD wave | §5 |
| [`info_contract_aesgcm_20261102__rerun_ar_20261103/`](info_contract_aesgcm_20261102__rerun_ar_20261103/) | 64 | the AgentRouter-transport rerun of the AES-GCM cohort opening the modern-AEAD wave | §5 |
| [`info_contract_aesgcm_apinex_20261102/`](info_contract_aesgcm_apinex_20261102/) | — | the APINEX-routed cohort — transport deviation disclosed, never pooled | §5 |
| [`info_contract_aesgcm_c2_floor8000_p026_20261103/`](info_contract_aesgcm_c2_floor8000_p026_20261103/) | 96 | the floor-sensitivity dose-response — 53.1% → 7.3% floor exhaustion, zero acceptance at both floors | §5 |
| [`info_contract_aesgcm_labels_20261102/`](info_contract_aesgcm_labels_20261102/) | — | the multi-label scheduling cohort | §5 |
| [`info_contract_aesgcm_labels_gpt_5_6_sol__rerun_ar_20261103/`](info_contract_aesgcm_labels_gpt_5_6_sol__rerun_ar_20261103/) | 62 | the multi-label scheduling rerun on the gpt-5.6-sol label (AgentRouter transport) | §5 |
| [`info_contract_aesgcm_labels_gpt_6_1_sol__rerun_ar_20261103/`](info_contract_aesgcm_labels_gpt_6_1_sol__rerun_ar_20261103/) | 62 | the multi-label scheduling rerun on the gpt-6.1-sol label (AgentRouter transport) | §5 |
| [`info_contract_aesgcm_p017_20261102/`](info_contract_aesgcm_p017_20261102/) | 64 | the P017 AES-GCM cohort | §5 |
| [`info_contract_aesgcm_p017_20261102__rerun_ar_20261103/`](info_contract_aesgcm_p017_20261102__rerun_ar_20261103/) | 93 | the AgentRouter-transport rerun of the P017 AES-GCM cohort | §5 |
| [`info_contract_aesgcm_p022a_20261102/`](info_contract_aesgcm_p022a_20261102/) | 96 | the P022a AES-GCM cohort | §5 |
| [`info_contract_aesgcm_p022a_20261102__rerun_ar_20261103/`](info_contract_aesgcm_p022a_20261102__rerun_ar_20261103/) | 96 | the AgentRouter-transport rerun of the P022a AES-GCM cohort | §5 |
| [`info_contract_aesgcm_p022b_20261102/`](info_contract_aesgcm_p022b_20261102/) | 96 | the P022b AES-GCM cohort — the transport-damaged first pass | §5 |
| [`info_contract_aesgcm_p022b_20261102__rerun_ar_20261103/`](info_contract_aesgcm_p022b_20261102__rerun_ar_20261103/) | 96 | the AgentRouter-transport rerun of the P022b AES-GCM cohort — the transport-damaged first pass | §5 |
| [`info_contract_aesgcm_p024a_20261103/`](info_contract_aesgcm_p024a_20261103/) | 96 | the truncation-reading closure — withholding makes every answer wrong | §5 |
| [`info_contract_aesgcm_p024b_20261103/`](info_contract_aesgcm_p024b_20261103/) | 96 | the printed boundary condition — consistent, under-powered at every coding | §5 |
| [`info_contract_aesgcm_p024b_20261103__rerun_ar_20261103/`](info_contract_aesgcm_p024b_20261103__rerun_ar_20261103/) | 96 | the AgentRouter-transport rerun of the printed boundary condition — consistent, under-powered at every coding | §5 |
| [`info_contract_aesgcm_random_20261102/`](info_contract_aesgcm_random_20261102/) | 96 | the first CSPRNG-sampled AES-GCM cohort | §5 |
| [`info_contract_aesgcm_random_20261102__rerun_ar_20261103/`](info_contract_aesgcm_random_20261102__rerun_ar_20261103/) | 102 | the AgentRouter-transport rerun of the first CSPRNG-sampled AES-GCM cohort | §5 |
| [`info_contract_aesgcm_random_p021_20261102/`](info_contract_aesgcm_random_p021_20261102/) | 385 | the P021 power cohort, first pass on the degraded transport | §5 |
| [`info_contract_aesgcm_random_p021ar_20261103/`](info_contract_aesgcm_random_p021ar_20261103/) | 384 | the 96-instance CSPRNG power cohort (repairs P021) — paired C1-vs-C4 96/0, Holm 4.04e-28 | §5 |
| [`info_contract_aesgcm_random_p021r_20261103/`](info_contract_aesgcm_random_p021r_20261103/) | 73 | the APINEX label probe — superseded, never pooled | §5 |
| [`info_contract_aesgcm_random_p023_20261103/`](info_contract_aesgcm_random_p023_20261103/) | 384 | the fresh-seed 96-instance cohort — paired 95/0 | §5 |
| [`info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103/`](info_contract_aesgcm_random_p023_20261103__rerun_ar_20261103/) | 384 | the AgentRouter-transport rerun of the fresh-seed 96-instance cohort — paired 95/0 | §5 |
| [`info_contract_chachapoly_random_20261102/`](info_contract_chachapoly_random_20261102/) | 96 | the ChaCha20-Poly1305 CSPRNG cohort | §5 |
| [`info_contract_chachapoly_random_20261102__rerun_ar_20261103/`](info_contract_chachapoly_random_20261102__rerun_ar_20261103/) | 96 | the AgentRouter-transport rerun of the ChaCha20-Poly1305 CSPRNG cohort | §5 |
| [`info_contract_confirmatory_c1_20261107/`](info_contract_confirmatory_c1_20261107/) | 64 | the m=3 confirmatory cohort on gpt-5.6-sol — bar NOT cleared, the observability axis's registered prediction | §5 |
| [`info_contract_ecdsa_20261026/`](info_contract_ecdsa_20261026/) | 66 | the observable-premise ECDSA control (nonce-reuse family) — 16/16 stated vs 32/32 withheld | §5 |
| [`info_contract_gcmsiv_random_20261102/`](info_contract_gcmsiv_random_20261102/) | 32 | the registered negative control — AES-GCM-SIV accepts nothing in any cell | §5 |
| [`info_contract_gcmsiv_random_20261102__rerun_ar_20261103/`](info_contract_gcmsiv_random_20261102__rerun_ar_20261103/) | 35 | the AgentRouter-transport rerun of the registered negative control — AES-GCM-SIV accepts nothing in any cell | §5 |
| [`info_contract_label2_20261025/`](info_contract_label2_20261025/) | 32 | the label-2 replication | §5 |
| [`info_contract_label2_20261025__rerun_ar_20261103/`](info_contract_label2_20261025__rerun_ar_20261103/) | 32 | the AgentRouter-transport rerun of the label-2 replication | §5 |
| [`info_contract_label3_20261029/`](info_contract_label3_20261029/) | 32 | the label-3 replication | §5 |
| [`info_contract_label3_n32_20261101/`](info_contract_label3_n32_20261101/) | 129 | the n=32 scale-up + its damaged first pass and clean rerun | §5 |
| [`info_contract_label3_n32_20261101__rerun_ar_20261103/`](info_contract_label3_n32_20261101__rerun_ar_20261103/) | 128 | the AgentRouter-transport rerun of the n=32 scale-up + its damaged first pass and clean rerun | §5 |
| [`info_contract_label4_20261030/`](info_contract_label4_20261030/) | 32 | the label-4 replication | §5 |
| [`info_contract_label4_20261030__rerun_ar_20261103/`](info_contract_label4_20261030__rerun_ar_20261103/) | 32 | the AgentRouter-transport rerun of the label-4 replication | §5 |
| [`info_contract_label5_20261030/`](info_contract_label5_20261030/) | 32 | the label-5 replication, first pass after quota exhaustion | §5 |
| [`info_contract_label5_20261030__rerun_ar_20261103/`](info_contract_label5_20261030__rerun_ar_20261103/) | 44 | the AgentRouter-transport rerun of the label-5 replication, first pass after quota exhaustion | §5 |
| [`info_contract_label5r_20261030/`](info_contract_label5r_20261030/) | 32 | the label-5 recovery rerun, disclosed per-label | §5 |
| [`info_contract_label5r_20261030__rerun_ar_20261103/`](info_contract_label5r_20261030__rerun_ar_20261103/) | 44 | the AgentRouter-transport rerun of the label-5 recovery rerun, disclosed per-label | §5 |
| [`info_contract_n16_20261026/`](info_contract_n16_20261026/) | 64 | the n=16 ChaCha20 cohort resolving the exact-test floor — paired 10/0 | §5 |
| [`info_contract_p010_driftcheck_20261026/`](info_contract_p010_driftcheck_20261026/) | 17 | the drift check on the P010 family | §5 |
| [`info_contract_powered_20261025/`](info_contract_powered_20261025/) | 32 | the powered information-contract cohort | §5 |
| [`info_contract_x1_gptoss_20261026/`](info_contract_x1_gptoss_20261026/) | 67 | the X1-family cohort on the gpt-oss label | §5 |
| [`paper_tables_20261103/`](paper_tables_20261103/) | — | the generator for the manuscript's registered tables |  |
| [`provider_health_20261023/`](provider_health_20261023/) | — | the provider-health calibration record (infrastructure, not a cohort) |  |

## Top-level records (not cohort directories)

The remaining entries at this level are campaign-level records and runners. The notable ones:

| File | What it is |
|---|---|
| [`BUDGET_LEDGER.jsonl`](BUDGET_LEDGER.jsonl) | per-call cost estimates for the whole campaign (3,494 rows) |
| [`ACTS_ATTACK_FINAL_SCIENTIFIC_SYNTHESIS.md`](ACTS_ATTACK_FINAL_SCIENTIFIC_SYNTHESIS.md) | the campaign-level scientific synthesis record |
| [`ACTS_ATTACK_FINAL_EVIDENCE_INDEX.csv`](ACTS_ATTACK_FINAL_EVIDENCE_INDEX.csv) | the final evidence index (machine-readable) |
| [`PAPER_EVIDENCE_20261103.json`](PAPER_EVIDENCE_20261103.json) | the evidence-to-manuscript mapping ledger |
| [`CENSUS_P_PROVIDER_20261103.json`](CENSUS_P_PROVIDER_20261103.json) | the provider-side census (with its CORRECTED variant) |
| [`CROSS_FAMILY_STAGE_ANALYSIS.json`](CROSS_FAMILY_STAGE_ANALYSIS.json) | the cross-family stage analysis |
| [`NOVELTY_FULLTEXT_REVIEW.md`](NOVELTY_FULLTEXT_REVIEW.md) | the prior-art full-text review record |

The other 180 files are run artifacts of the waves above: cohort runners (`run_*.py`),
sweep/summary outputs, per-wave logs and resume scripts — retained verbatim as part of the
frozen record, safe to ignore when reading a specific cohort.

---

*Regenerated by [`tools/build_experiments_index.py`](../tools/build_experiments_index.py) from
the frozen tree — re-run it after adding a cohort.*
