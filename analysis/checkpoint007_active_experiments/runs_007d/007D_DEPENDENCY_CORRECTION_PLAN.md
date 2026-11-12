# Checkpoint 007D — Dependency-corrected plan

Created: 2026-10-17T17:36:12Z
Root: /mnt/nvme5/ACTS-Attack/sp2027/analysis/checkpoint007_active_experiments
Out: /mnt/nvme5/ACTS-Attack/sp2027/analysis/checkpoint007_active_experiments/runs_007d

## Fixture evidence from current filesystem
- __init__.py: exists=True size=0 sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 manifest_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 matches_manifest=True
- cbc_oracle.py: exists=True size=536 sha256=38a67887b8744c943af78907253c456e2f9cab7a10f4ff91fe50eba80eb59e60 manifest_sha256=38a67887b8744c943af78907253c456e2f9cab7a10f4ff91fe50eba80eb59e60 matches_manifest=True
- truth_gate_test.py: exists=True size=1074 sha256=62ca895add64b78cc02522e20ee3522890260f563c0b5d507102401d75668ced manifest_sha256=62ca895add64b78cc02522e20ee3522890260f563c0b5d507102401d75668ced matches_manifest=True

## CBC instrument note
- CBC_INSTRUMENT_FINALIZED_NOTES.txt exists: True
- Wording fixes pending per that note: True

## Dependency audit highlights
- 007A RC4/ECDSA/XOR: non-CBC; own prerequisites assessed independently
- 007B/007C CBC model arms: CBC dependent; held pending versioned CBC qualification
- B_CBC_FIXED: CBC feasibility control; not executable as completed without a real deterministic run record
- 007E: offline/gate tasks; own prerequisites; not CBC blocked
- 007F: local controls; own prerequisites; not CBC blocked
- D_DEFERRED: deferred by design

## Corrected disposition summary
- CBC blocked: ['B_CBC_INTERACTIVE', 'B_CBC_ONESHOT', 'C_CBC_BINARY', 'C_CBC_ENRICHED', 'B_CBC_FIXED']
- Non-CBC confirmatory eligible: ['A_RC4_NAMED', 'A_RC4_UNNAMED', 'A_RC4_UNDET', 'A_ECDSA_NAMED', 'A_ECDSA_UNNAMED', 'A_ECDSA_UNDET', 'A_XOR_NAMED', 'A_XOR_UNNAMED', 'A_XOR_UNDET', 'E_ANNOTATION']
- Offline eligible: ['E_GRADER_MAP', 'E_EXEC_CONTRACT']
- Local control/gate: ['E_TRANSCRIPT_SCAN', 'F_FAULT_INJECT', 'F_CLOCK_CALIB']
- Deferred: ['D_DEFERRED']

## CBC control status
- B_CBC_FIXED is not executed as completed here; arithmetic estimate is not an actual deterministic run.

## Runner
Required: {"append_only_log": true, "per_arm_manifest": true, "immutable_source_receipt": true, "secret_exclusion_check": true, "provider_usage_accounting": true, "budget_enforcement": true, "crash_resumable": true, "no_invented_results": true, "cbc_hold_respected_until_versioned_qualification": true}
Provided in this plan pass: design/constraint specification only; not yet implemented and tested.

## Status
PARTIAL_EXECUTION
Completed in 007D plan pass: dependency graph, corrected dispositions, fixture evidence reconciliation, CBC block rule correction, runner requirements.
Blocked: live run execution pending runner implementation+test and CBC versioned qualification for CBC arms/control.
