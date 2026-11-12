# Outer ACTS-Attack project evidence discovery

Audit date: 2026-10-15. Scope: /mnt/nvme5/ACTS-Attack. The nested primary checkout is /mnt/nvme5/ACTS-Attack/ACTS-ATTACK.

## Scope correction

The nested checkout is not the complete ACTS-Attack evidence universe. The outer workspace contains retained experiment campaigns, result capsules, frozen snapshots, human-audit packets, benchmark evidence, manuscript artifact copies, and submission-release copies. These were outside the prior 465-file nested working-tree manifest.

## Measured outer evidence surfaces

| Surface | Files | Bytes | Structured content |
|---|---:|---:|---|
| entire outer tree, excluding system/tooling directories | 10,458 | 7,407,385,264 | 3,983 JSON; 1,710 JSONL; 112 CSV; 3 TSV |
| nested ACTS-ATTACK checkout | 465 non-Git files | 4,515,595 | 17 JSON; 181 JSONL |
| sp2027/agent-eval | 1,473 | 36,454,342 | 626 JSON; 682 JSONL |
| artifacts | 147 | 126,103,198 | 129 JSON |
| artifact/clean_analysis_capsule_v1 | included in artifact total | included | 195 JSON; 58 JSONL |
| frozen_snapshots | 28 | 3,237,114,225 | content-addressed frozen evidence and bundles |
| human_audit | 70 | 3,219,526,145 | sealed packets, source archives, audit records |
| evaluations | 19 | 495,616 | evaluation records |
| submission_release | 696 | 42,582,109 | release copies and evidence artifacts |
| manuscript | 275 | 13,386,683 | manuscript/artifact copies |

The two multi-gigabyte surfaces are not negligible archives: frozen_snapshots contains content-addressed evidence objects up to 1.59 GB, and human_audit contains source-freeze archives up to 1.59 GB. They require provenance/hash treatment and must not be treated as absent because they are not under the nested checkout.

## Newly discovered retained experiment families

### E2 agent campaigns

Exact campaign surfaces under sp2027/agent-eval include:

- runs_e2: 38 indexed sessions: 22 SUCCESS, 3 HARNESS_ERROR, 2 ORACLE_FAIL, 10 TOOL_FAILURE, 1 AGENT_GIVEUP.
- runs_e2_r230: 35 sessions: 25 SUCCESS, 6 TOOL_FAILURE, 4 ORACLE_FAIL.
- runs_e2_r230_full_01: 48 sessions: 28 SUCCESS, 16 HARNESS_ERROR, 3 TOOL_FAILURE, 1 ORACLE_FAIL.
- runs_e2_r230_opencode_01: 230 sessions: 95 SUCCESS, 45 ORACLE_FAIL, 48 TOOL_FAILURE, 23 HARNESS_ERROR, 13 MODEL_REFUSAL, 5 TIMEOUT, 1 AGENT_GIVEUP.
- runs_e2_clean_primary_20261006_01: 15 sessions, predominantly TOOL_FAILURE.
- runs_e2_backend_qual_20261006_02: 6 sessions, 4 ORACLE_FAIL and 2 TOOL_FAILURE.
- runs_e2_clean_requal_20261006_02: 12 PROVIDER_UNAVAILABLE sessions.
- runs_e2_contract_v3_20261014_01: 12 PROVIDER_UNAVAILABLE sessions.
- runs_e2_stable_capture_20261014_01: 8 sessions, 4 SUCCESS and 4 TOOL_FAILURE.
- runs_r1_clean_capture_first_claude46_20261014_03: 9 sessions, 6 SUCCESS and 3 ORACLE_FAIL.
- runs_r1_clean_capture_first_v4_claude46_20261014_02: 12 sessions, 8 SUCCESS and 4 ORACLE_FAIL.
- runs_r1_clean_capture_first_v4_claude46_20261014_01: 11 sessions, 10 HARNESS_ERROR and 1 SUCCESS.
- runs_w2_pilot: 20 sessions, 17 PROVIDER_UNAVAILABLE.

Across canonical run JSON objects in sp2027/agent-eval, 545 records were found: 209 SUCCESS, 75 ORACLE_FAIL, 90 TOOL_FAILURE, 53 HARNESS_ERROR, 14 AGENT_GIVEUP, 7 TIMEOUT, 84 PROVIDER_UNAVAILABLE, and 13 MODEL_REFUSAL. Task counts include RC4 132, CBC 115, ChaCha20 98, ECDSA 73, parsing-overflow 38, SSH 13, and 11 each for auth-flaw, crypto-misuse, known-vulnerable, and TLS-hybrid. These are campaign populations, not one clean denominator.

Primary paths: sp2027/agent-eval/runs_e2_r230_opencode_01/INDEX.jsonl; sp2027/agent-eval/runs_e2_r230/INDEX.jsonl; sp2027/agent-eval/runs_e2_r230_full_01/INDEX.jsonl; corresponding run JSON and transcript directories.

### E5 AES key-recovery campaign

This is a critical result family absent from the nested checkout inventory. The exact primary retained records are under sp2027/agent-eval/runs_e5/:

- 29 canonical e5_aes_key_recovery/T1_known run records.
- Statuses: 15 PROVIDER_UNAVAILABLE, 9 ORACLE_FAIL, 4 TOOL_FAILURE, 1 SUCCESS.
- The single accepted record is e5_R30__e5_aes_key_recovery__T1_known__rep1.
- The accepted record reports oracle success true and a separate reserved-key oracle.
- Other canonical examples retain separate-process oracle outcomes, service requests, model identity, request timing, transcript paths, and provenance.

Exact accepted-result path:

sp2027/agent-eval/runs_e5/session_r30/runs/e5_R30__e5_aes_key_recovery__T1_known__rep1.json

Related raw transcript/result path:

sp2027/agent-eval/runs_e5/session_r30/runs/transcripts/e5_R30__e5_aes_key_recovery__T1_known__rep1/transcript.jsonl

Evidence classification: PRIMARY_BOUNDED for one retained accepted E5 operation, not a general key-recovery rate. The 1/29 campaign outcome is not a clean capability estimate because 15 sessions were provider-unavailable and the remaining failures include oracle/tool failures. The claim supported is that one recorded session reached the retained E5 oracle success condition. Independent reproduction, generality, and model capability remain unproven.

### Contract and qualification controls

contract_regression_v3_20261014_01 contains 111 files, including 108 JSONL records and RESULTS.json. The control result reports malformed-input rejection, missing-argv rejection, freshness success, stale-hardcode rejection, terminal-status matching, and identity checks. This is a reproducible harness/contract control, not an attack result.

### Artifact and frozen evidence populations

artifacts/experiment_inventory.json is a 54,170,064-byte inventory with catalog, records, corpus reports, parse errors, duplicate-run locations, and identical-observation locations. artifacts/inventory_snapshots/experiment_inventory_v1.json is a 54,169,904-byte related snapshot. These are high-value index/provenance artifacts and were not part of the nested 465-file crawl.

artifacts/E2_CLEAN_REQUAL_20261006_02_RESULTS.json records 12 scheduled, 12 launched, 12 retained, 12 unique run IDs with schema, identity, and provenance gates PASS. artifacts/E5-CONTROLLED-2026-10/DETERMINISTIC_CONTROL_RUN_FROZEN_V2.json records a deterministic local control with zero network/provider calls and no raw grading secrets written. These are controls and frozen campaign evidence, not substitutes for raw independent observations.

frozen_snapshots/evidence_manifest.json and frozen_snapshots/evidence_content_addressed/ contain content-addressed copies of evidence. human_audit/source_freeze_20261005/archives/ contains benchmark/source archives; human_audit/reaudit_campaign_20261005 and its v2 packet contain blinded/reviewer audit records. These surfaces must be deduplicated by hashes and lineage, not counted as new experiments merely because they are copied into multiple capsules.

## Parsing result for the outer scope

Across the outer non-system scope, 3,982 JSON files parsed and one intentionally malformed file was identified at:

sp2027/agent-eval/contract_regression_v3_20261014_01/malformed.json

All 655,424 nonblank JSONL records parsed successfully in the outer scan. This count includes duplicated transcript/session representations and therefore is not an observation denominator.

## Outer Git-state and duplicate-lineage reconciliation

The outer non-system crawl was SHA-256 hashed file by file: 10,459 files including the newly created audit report, 4,536 unique content hashes, and 5,923 duplicate file instances. The high duplicate count is expected from frozen capsules, manuscript release copies, transcript/result dual representations, and repeated paper builds; those copies are not independent observations.

| Surface | Files | tracked | untracked nonignored | ignored |
|---|---:|---:|---:|---:|
| ACTS-ATTACK nested path as seen by outer Git | 465 | 0 | 0 | 0 |
| sp2027/agent-eval | 1,473 | 368 | 1,039 | 66 |
| artifacts | 147 | 126 | 14 | 7 |
| artifact | 315 | 314 | 0 | 1 |
| frozen_snapshots | 28 | 28 | 0 | 0 |
| human_audit | 70 | 52 | 17 | 1 |
| evaluations | 19 | 19 | 0 | 0 |
| submission_release | 696 | 0 | 664 | 32 |

The nested checkout is a separate Git repository, so outer Git state reports its directory as untracked/opaque; nested Git state must be read from the nested repository itself. This is why the two repository inventories cannot be silently merged.

Examples of content-addressed duplicates include the E2 trial-order CSV repeated across the clean capsule and paper lock replays, pre-registration cards repeated across 16 release/capsule locations, and E5 attack code repeated across 32 session directories. By contrast, the 29 E5 canonical run records and their transcript/result pairs require run-ID and lineage deduplication rather than filename-only deduplication.

## Corrected status

The outer Git object database was subsequently crawled separately. Its approximately 22 GiB contains one complete normal pack, 30 small dangling blobs, and 27 temporary pack files totaling 18.54 GiB. Byte-level comparison established that the temporary files are partial-write prefixes of two complete reachable benchmark blobs under `frozen_snapshots/evidence_content_addressed/`, not unrelated data. The complete blobs contain 29,126 and 9,734 tar members respectively and must be retained as benchmark/data inputs, while not being counted as independent ACTS result observations without run/oracle linkage. See `13_OUTER_GIT_OBJECT_DATABASE_CRAWL.md` for the reconstruction evidence.

The complete source-freeze archives were then crawled internally. This exposed archive-contained benchmark data, 614 Incalmo action-log records plus a retained result with 50 infected hosts and 48 exfiltrated files, and five CyBench Git-LFS pointer outputs totaling 292,150 declared bytes whose payload objects are not currently present. See `14_ARCHIVE_CONTAINED_DATA_AND_RESULTS_CRAWL.md`.

The nested checkout inventory remains verified as a separate repository inventory. The project-wide ACTS-Attack inventory is not yet complete because the newly discovered outer surfaces require full file-level provenance, deduplication, and manuscript mapping. Until that work is incorporated, the correct status is:

PARTIAL DISCOVERY — NAMED EVIDENCE GAPS
