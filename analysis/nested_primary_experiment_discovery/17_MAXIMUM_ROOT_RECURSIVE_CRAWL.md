# Maximum recursive crawl of the complete ACTS-Attack outer root

## Scope closure

This pass recursively enumerated every regular file under the absolute root `/mnt/nvme5/ACTS-Attack`, including hidden directories, nested release packages, `vendor/`, the nested `ACTS-ATTACK/` checkout, and the full outer `.git` directory. It did not execute code, experiments, attack harnesses, providers, or archived scripts.

| Surface | regular files | bytes | review mode |
|---|---:|---:|---|
| complete outer root | 19,729 | 30,713,782,442 | recursive metadata crawl, no read errors |
| outer `.git` | 5,258 | 23,250,397,097 | object/pack and history inspection |
| non-`.git` tree | 14,131 | 7,462,336,842 | full SHA-256 hashing; structured parsing |
| nested `ACTS-ATTACK` checkout | 805 | 5,564,098 | full file reads and Git-state inspection |
| `vendor/` | 223 | 2,164,598 | full CAS/hash and structured inspection |

The non-`.git` hash pass completed with zero read errors. It found 7,950 unique file contents, 6,181 duplicate file placements, and 1,749 duplicate-content groups. The duplicates are release/package/migration copies and are not independent observations. The largest repeated result-bearing groups include sixteen copies of the 5,591,167-byte E3 full sample stream and fifteen copies of each retained E5 session JSON across artifact/reviewer/submission packages.

## Complete structured-data pass

Across the complete non-`.git` tree, 6,020 structured/result candidates were read:

- 4,038 valid JSON files;
- 1,710 valid JSONL files containing 655,424 nonblank JSON records;
- 112 valid CSV files;
- 3 valid TSV files;
- 156 other manifest/ledger/result-like files read as text;
- one explicitly malformed JSON: `sp2027/agent-eval/contract_regression_v3_20261014_01/malformed.json`.

Content-hash reduction leaves 2,346 unique structured contents. This is a filesystem-wide parse count, not a claim that every structured record is an independent experiment.

## Recovered indexed experiment inventory

The retained `artifacts/experiment_inventory.json` contains 33,746 indexed records, generated 2026-10-04, with source paths and observation hashes preserved. Its own declared coverage limit excludes semantic inspection of every source file and recovery of overwritten executions; therefore it is used as an index and reconciled against raw files below.

| Family | records | retained status distribution | evidence role |
|---|---:|---|---|
| `E3-full` | 32,000 | status `UNKNOWN` in the index | validation |
| `E3-shakedown` | 800 | status `UNKNOWN` | pilot |
| `runs_e2_r230_opencode_01` | 230 | 95 SUCCESS; 45 ORACLE_FAIL; 48 TOOL_FAILURE; 23 HARNESS_ERROR; 13 MODEL_REFUSAL; 5 TIMEOUT; 1 AGENT_GIVEUP | audit-only replay/campaign |
| `fault_20261004_01` | 180 | 70 SUCCESS; 30 ORACLE_FAIL; 80 PROVIDER_UNAVAILABLE | benign control |
| `runs_e2_r230_full_01` | 48 | 28 SUCCESS; 16 HARNESS_ERROR; 1 ORACLE_FAIL; 3 TOOL_FAILURE | audit-only replay/campaign |
| `legacy-agent-loop` | 206 | historical/staging mixed: 20 success, 10 SUCCESS, 24 no_claim, 42 driver_error, 58 gateway_unavailable, 28 PROVIDER_UNAVAILABLE, 12 AGENT_GIVEUP, 8 failure, 4 ORACLE_FAIL | historical/staging |
| `results_c2b_pq` | 90 | 30 classical; 40 hybrid; 20 reject | validation/staging |
| `E5-escrow` | 58 | 2 SUCCESS; 18 ORACLE_FAIL; 8 TOOL_FAILURE; 30 PROVIDER_UNAVAILABLE | validation/staging |
| `runs_e2_r230` | 35 | 25 SUCCESS; 4 ORACLE_FAIL; 6 TOOL_FAILURE | audit-only replay/campaign |
| `runs_e2` | 32 | 19 SUCCESS; 3 HARNESS_ERROR; 1 ORACLE_FAIL; 9 TOOL_FAILURE | audit-only replay/campaign |
| `fixed-executor` | 24 | 24 success | validation/staging |
| `W2-pilot` | 20 | 1 SUCCESS; 1 TIMEOUT; 1 TOOL_FAILURE; 17 PROVIDER_UNAVAILABLE | pilot |
| `results_c2b_h1b` | 10 | 10 classical | pilot/staging |
| `results_c2b_smoke` | 9 | 7 classical; 2 reject | pilot |
| `local_20261004_01` | 4 | 4 PROVIDER_UNAVAILABLE | benign control |

The index records 548 populated run IDs but 33,746 rows because E3 physical observations and JSONL rows have no run ID. It reports 167 duplicate run-ID/identical-observation locations, including historical and release copies. Its 32,409 B-class, 1,330 C-class, and 7 D-class labels are index classifications, not the evidence grades in this audit. Every indexed record is marked `can_enter_primary_population_analysis=false`; this is consistent with the requirement not to merge heterogeneous denominators.

## Previously under-reported raw E3 timing experiment

The raw files are directly retained at:

- `sp2027/analysis/e3_rig/samples_full.jsonl` — **32,000 observations**, 16 cells, 2,000 observations per cell;
- `sp2027/analysis/e3_rig/samples_shakedown.jsonl` — **800 observations**, pilot;
- `trial_order_full.csv`, `trial_order_shakedown.csv`;
- `e3_rig_results_full.json`, `e3_analyze_results.json`, `e3_bootstrap_correction_v1.json`, `e3_block_sensitivity.json`, `gate_verdict.json`, and `e3_rig_env.json`.

The full run records seed 20261025, SMT on/off blocks, vulnerable T-table and constant-time-control builds, warm/cold cache, and two timer families. It records a PASS negative-control gate with n_fix=60, n_rand=60, p_ct=0.6768910193567681, Welch t=0.41670934340370563, and canary p=0.0. The environment record identifies a Dell Precision 7740, kernel 7.0.0-34-generic, no hypervisor flag, GCC 13.3.0, SMT toggled and restored, and a single-host scope.

The retained analysis reports the following bounded full-run contrast:

- eight paired build contrasts over 32,000 observations;
- observed median-difference effect: **-1.695593 ms**;
- block-bootstrap 95% interval: **[-1.912816, -1.589729] ms**;
- Welch t=-12.113617911612334, df=31997.583239339092, p=8.94593894773284e-34;
- warm-cache contrast: -1.75883675 ms, CI [-1.77907271875, -1.7448239375], p recorded as 0.0;
- cold-cache contrast: -1.695593 ms, CI [-2.0857916, -1.58121680625], p=4.61772442493777e-16;
- SMT-on and SMT-off within-block contrasts were both retained as significant, but the analysis explicitly treats SMT as a split-plot factor.

The correction record is especially important: it reports lag-1 autocorrelation as high as 0.956 in cold cells, half-split median drift, and states that trial-level pairing and independent SMT blocks must not be assumed. Moving-block sensitivity at block sizes 10, 50, 100, and 250 leaves the primary estimator near -1.70 ms, with intervals spanning approximately -2.09 to -1.33 ms. The strongest supported claim is a one-host, observed factorial timing contrast under the recorded build/cache/timer conditions. It is not a population estimate, cross-host result, or causal SMT claim.

## Other newly closed result families

The full-root crawl confirms that the experiment repository surface is materially larger than the nested checkout and the 35-arm registry. In particular, `runs_e2_r230_opencode_01` is a 230-record campaign, not a small appendix; `fault_20261004_01` is a 180-row benign control; and the E3 physical timing stream contributes 32,800 observations that were not agent runs. `artifacts/experiment_inventory.json`, its snapshot, and the package copies are evidence indexes and provenance surfaces; their duplicated copies are not new runs.

## Evidence classification

| Surface | grade | bounded scientific statement |
|---|---|---|
| E3 full factorial | PRIMARY_BOUNDED | one bare-metal host retained a controlled 32,000-observation timing contrast with a passed negative-control gate and dependence-aware sensitivity analysis |
| E3 shakedown | REPRODUCIBLE_CONTROL | 800 pilot observations establish the pilot surface, not confirmatory evidence |
| E2 campaign families | HISTORICAL_LIMITED / PRIMARY_BOUNDED by subcampaign | retained run identities and outcomes exist, but campaign roles and provenance differ; no pooled ASR is valid |
| 180-row fault control | PRIMARY_BOUNDED | retained benign-control outcomes exist, with provider-unavailable rows separated from oracle outcomes |
| artifact/reviewer/submission copies | ARTIFACT_ONLY | content-identical migration/release copies, not independent observations |
| malformed JSON | UNRESOLVED | one named file cannot be parsed and must not be used numerically |

## Remaining gaps after this crawl

This pass is a maximum recursive filesystem and structured-data crawl, but not a claim that every binary archive member was manually interpreted. Archive internals, Git-LFS payload pointers, encrypted/sealed files, and source code remain metadata/provenance surfaces unless their result content was separately parsed. The project status therefore remains **PARTIAL DISCOVERY — NAMED EVIDENCE GAPS**, while the raw filesystem count and structured-data counts above are now closed for this snapshot.

## Nested live-worktree reconciliation added after the outer crawl

The nested checkout’s current status was independently rechecked after the maximum root crawl. It contains 232 tracked status changes, 99 nonignored untracked paths, and 133 ignored paths. Git blob comparison shows 231 tracked changes are mode-only and only `README.md` has content drift from nested `HEAD`. The ignored V2 and untracked V3 directories each retain the same 74 JSONL sessions; all 74 corresponding file hashes match, so the deduplicated population is 74 sessions, not 148. The population contains 42 oracle-accepted `match=true` sessions, 2 terminal errors, 12 no-claim outcomes, 3 unresolved terminals, and 15 provider/gateway failures. Untracked V4 contains three wrappers and no result files. This closes the specific committed/uncommitted/ignored-file blind spot without changing the outer-root closure counts. See `18_COMMITTED_UNCOMMITTED_WORKTREE_RECONCILIATION.md` and R37–R40.

The current outer worktree also contains 1,473 files under `sp2027/agent-eval/` that require campaign-level reconciliation beyond the 2026-10-04 generated inventory. Direct parsing found new contract-v3 qualification/regression controls, an H1 V2 3/3 provenance control, an 8-row stable capture, Claude 4.6 V3 9/12 partial capture, Claude 4.6 V4 12/12 capture with 8 SUCCESS and 4 ORACLE_FAIL, and provider-failed/incomplete branches. These records are now documented in `19_OUTER_AGENT_EVAL_UNTRACKED_CAMPAIGNS.md` and R41–R50.
