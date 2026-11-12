# Checkpoint 007C — Amendment 1 and execution plan

Created: 2026-10-17T17:29:25Z
Root: /mnt/nvme5/ACTS-Attack/sp2027/analysis/checkpoint007_active_experiments
Out: /mnt/nvme5/ACTS-Attack/sp2027/analysis/checkpoint007_active_experiments/runs_007c

## Frozen documents
Preserved byte-for-byte: True

- 01_PREREGISTERED_HYPOTHESES.md: preserved=True manifest_sha=bcf1ba3c54f9... actual_sha=bcf1ba3c54f9...
- 02_MATCHED_ARM_REGISTRY.csv: preserved=True manifest_sha=38f7eaae21ac... actual_sha=38f7eaae21ac...
- 03_TARGET_AND_INFORMATION_CONTRACTS.md: preserved=True manifest_sha=c5905fd72564... actual_sha=c5905fd72564...
- 04_POWER_COST_STOP_RULES.md: preserved=True manifest_sha=da20fee0afc5... actual_sha=da20fee0afc5...

## Fixtures
- __init__.py: resolved=True manifest_sha=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 actual_sha=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- cbc_oracle.py: resolved=True manifest_sha=38a67887b8744c943af78907253c456e2f9cab7a10f4ff91fe50eba80eb59e60 actual_sha=38a67887b8744c943af78907253c456e2f9cab7a10f4ff91fe50eba80eb59e60
- truth_gate_test.py: resolved=True manifest_sha=62ca895add64b78cc02522e20ee3522890260f563c0b5d507102401d75668ced actual_sha=62ca895add64b78cc02522e20ee3522890260f563c0b5d507102401d75668ced

## CBC feasibility
CBC padding-oracle recovery of one 16-byte block:
- Average queries: 2048
- Worst-case queries: 4096
- Registered CBC model budget: 400

CBC model confirmatory arms feasible under frozen budget: False

CBC control arm B_CBC_FIXED:
- tier: instrument_control_NEVER_POOLED
- max_model_turns: 0
- oracle_query_budget: 400
- success_predicate: recovered plaintext equals reserved plaintext (feasibility only)
- failure_statuses: TOOL_FAILURE

CBC feasibility decision: DISALLOW_CBC_CONFIRMATORY_UNDER_REGISTERED_BUDGET

## CBC pilot truncation
- P002: truncated mid-code, end_turn, 1024 output tokens
- P003: truncated mid-code, end_turn, 1024 output tokens
Both are reported and preserved; neither is scored as a completed attack.

## Arm dispositions
- A_RC4_NAMED          exp=007A  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- A_RC4_UNNAMED        exp=007A  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- A_RC4_UNDET          exp=007A  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- A_ECDSA_NAMED        exp=007A  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- A_ECDSA_UNNAMED      exp=007A  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- A_ECDSA_UNDET        exp=007A  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- A_XOR_NAMED          exp=007A  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- A_XOR_UNNAMED        exp=007A  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- A_XOR_UNDET          exp=007A  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- B_CBC_INTERACTIVE    exp=007B  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- B_CBC_ONESHOT        exp=007B  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- B_CBC_FIXED          exp=007B  tier=instrument_control_NEVER_POOLED disposition=CONTROL_NEVER_POOLED                executed=False reason=deterministic control; feasibility probe only; see cbc budget decision
- C_CBC_BINARY         exp=007C  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- C_CBC_ENRICHED       exp=007C  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- E_GRADER_MAP         exp=007E  tier=confirmatory_offline      disposition=CONFIRMATORY_OFFLINE_DRY_RUN_ONLY   executed=False reason=offline confirmatory structure dry-run only; not a live model comparison in this checkpoint
- E_EXEC_CONTRACT      exp=007E  tier=confirmatory_offline      disposition=CONFIRMATORY_OFFLINE_DRY_RUN_ONLY   executed=False reason=offline confirmatory structure dry-run only; not a live model comparison in this checkpoint
- E_TRANSCRIPT_SCAN    exp=007E  tier=instrument_gate           disposition=INSTRUMENT_GATE_LOCAL_ONLY          executed=False reason=instrument gate; local synthetic artifacts only; not evidence for model hypotheses
- E_ANNOTATION         exp=007E  tier=confirmatory              disposition=CONFIRMATORY_ELIGIBLE_FOR_LOCAL_CBC_TRIAL executed=False reason=CBC model confirmatory; not executed because cbc budget is infeasible under frozen protocol
- F_FAULT_INJECT       exp=007F  tier=instrument_control        disposition=INSTRUMENT_CONTROL_LOCAL_ONLY       executed=False reason=local instrument-control; not assigned a scored CBC model result in this checkpoint
- F_CLOCK_CALIB        exp=007F  tier=instrument_control        disposition=INSTRUMENT_CONTROL_LOCAL_ONLY       executed=False reason=local instrument-control; not assigned a scored CBC model result in this checkpoint
- D_DEFERRED           exp=007D  tier=deferred_with_reason      disposition=DEFERRED                            executed=False reason=deferred by design; no results invented

## CBC model arms not executed in 007c
- A_RC4_NAMED
- A_RC4_UNNAMED
- A_RC4_UNDET
- A_ECDSA_NAMED
- A_ECDSA_UNNAMED
- A_ECDSA_UNDET
- A_XOR_NAMED
- A_XOR_UNNAMED
- A_XOR_UNDET
- B_CBC_INTERACTIVE
- B_CBC_ONESHOT
- C_CBC_BINARY
- C_CBC_ENRICHED
- E_ANNOTATION

## Deferred arms not executed
- D_DEFERRED: deferred_with_reason; reason: deferred_with_reason in registry; no results invented

## Required amendments before CBC confirmatory execution
1. CBC task budget or instance size or oracle strength must be amended and versioned before any CBC confirmatory model arm can be executed.
2. CBC instrument finalization notes already require final wording fixes before confirmatory CBC arms; those fixes must be versioned, not silently applied.
3. run_loop.py persistence model must be replaced with append-only durable logging before live confirmatory runs.
4. __init__.py is currently missing according to earlier report; restore/verify it against frozen empty-file hash before any fixture-dependent run.

## Runner status
- Previous: run_loop.py
- Behavior: writes single-event dict via Path.write_text; not append-only durable over multiple arms
- Required: append-only crash-resumable run loop with per-arm manifests
- Provided in 007c: scaffold + deterministic feasibility control + disposition ledger; live API arm execution withheld pending feasibility and runner readiness

## Completion gate
NOT CLAIMED: CONFIRMATORY_EXPERIMENTS_COMPLETE=true

Status: PARTIAL_EXECUTION
Completed_in_007c: deterministic CBC feasibility probe + full 21-arm disposition ledger + amendment 1 + frozen-document/fixture preservation verification
Blocked: live CBC confirmatory model execution pending budget/instance/oracle amendment and append-only runner readiness
