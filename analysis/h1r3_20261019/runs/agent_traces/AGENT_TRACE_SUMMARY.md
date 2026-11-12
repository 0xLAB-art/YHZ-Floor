# Five-agent trace summary — H1-R3 defect analysis

All five traces are **artifact-only**. None of them started provider calls.

## Agents and scope

1. `trace_agent_01_original_h1_replacement_pilot`
   - Scope: original 72-session H1 replacement pilot artifacts
   - Found replay tables: PAIRED_C1_C2_REPLAY_TABLE.json and C0_AUDIT.json
   - Paired counts extracted: C1 executed 24, C2 executed 22, C1 reference accepted 24, C2 reference accepted 21
   - C0 audit: 24/24 rejected, 0 unexplained acceptances
   - Critical issues traced: 6

2. `trace_agent_02_executed_artifact_identity`
   - Scope: surrogate attempt-3 executed/archived identity mismatch
   - Evidence present: reconstructed candidate exists, replay results exist
   - Reconstructed source SHA-256: `a5e8ed514c5c769b3e4e2dbbdd51ea276c852d11d8145b2f344ca7184f78e399`
   - Critical issues traced: 2

3. `trace_agent_03_scorer_and_instrument_defects`
   - Scope: XOR scorer/contract defect and H1 V2 instrument/retention issues
   - Confirmed in report text: evaluator-contract defect language, 10/10 correct-mask rejection, 10/10 protected-plaintext acceptance, 0/20 retrospective recovery note
   - Critical issues traced: 3

4. `trace_agent_04_evaluator_boundary_proposal`
   - Scope: HEB-1 evaluator-boundary novelty proposal
   - Proposal exists and is design-stage only
   - No implementation, no provider calls, no completed experiment
   - Critical issues traced: 3

5. `trace_agent_05_tasks_seeds_budget_limits`
   - Scope: task difficulty, seed coverage, budget, model-identity limits
   - Sources used: scientific results report, evidence package, coverage audit, RQ evidence map
   - Critical issues traced: 5

## Consolidated critical-issue classes across agents

- Contrast not a clean single-variable intervention (prompt label, encoding, length, decoding burden co-varied)
- Source-qualification failures were pre-execution, not cryptographic oracle failures
- Sampling controls and model stochasticity not fully documented
- C0 used a different endpoint/predicate than C1/C2
- Global randomization and schedule structure were weak in the original design
- Executed candidate vs archived candidate mismatch (resolved via reconstruction + replay + live grading)
- Claim hash vs source hash identity must be kept separate
- XOR endpoint was a scorer/contract defect, not a capability result
- Some retained failure/refusal labels were semantically meaningless or defective
- Some descriptive prompt contrasts were misread as causal
- Strong successes are concentrated in relatively easy calibration families
- No pooled estimate exists; denominators are per-contract/per-namespace
- Model identity is provider-attested only
- V4 raw timing recomputability is not established
- Acquisition/host-isolation claims do not survive from E5-style results
- HEB-1 novelty track is still a proposal with open gates

## What this run did and did not do

- Did: trace five distinct defect/issue surfaces from retained records
- Did: write one JSON trace per agent under:
  - `sp2027/analysis/h1r3_20261019/runs/agent_traces/`
- Did: write a consolidated launcher and summary
- Did not: start any provider calls
- Did not: re-execute the defected experiments in this turn

If you want the rerun step next, tell me which specific defected experiment(s) you want re-run first and under which constraints, and I can prepare a controlled rerun agent for that one.
