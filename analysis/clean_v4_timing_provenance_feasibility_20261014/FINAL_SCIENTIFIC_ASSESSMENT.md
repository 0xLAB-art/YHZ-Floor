# Final scientific assessment

## Terminal verdicts

**TIMING: CLEAN SUCCESS TIMINGS PARTIALLY VERIFIED — CLAIMS BOUNDED**

The eight SUCCESS rows carry explicit accepted task-specific oracle verdicts. The four ORACLE_FAIL rows carry explicit rejected verdicts in their retained session transcripts; the generic classifier has a fallback ORACLE_FAIL branch, but that branch is not needed to explain these four rows. Each successful record has a retained, source-defined harness duration and matching session-end event. Raw monotonic endpoint readings are absent, so all eight durations are supportable with qualification, not independently recomputable from raw clock endpoints. The individual timing values and task medians are in the companion CSV/JSON/summary.

**PROVENANCE: FEASIBLE WITH MATERIAL PROVIDER/IDENTITY LIMITATIONS — APPROVAL REQUIRED**

The unchanged H1 rule can be met by a networked real-agent runtime that binds local source, configuration, task, immutable OCI digest, execution identity and result. Provider egress means the runtime is not network-isolated; APMIX/hosted backend identity and weights remain externally mutable. H1 does not establish hosted-model reproducibility.

**SCIENTIFIC RECOMMENDATION: NARROW PROVENANCE PILOT JUSTIFIED — DO NOT EXECUTE WITHOUT APPROVAL**

A narrow pilot would test the unobserved joint claim that real-agent execution and a content-addressed local environment can be linked under H1. EXP-034 and EXP-035 establish the two sides separately, not jointly. Do not scale to n≥10 per task for this paper's current evidence-boundary claims; repetition would refine only within-task description.

## Required accounting and integrity answers

1. All 8 SUCCESS rows: explicit accepted task-specific oracle verdicts retained.
2. All 4 ORACLE_FAIL labels: explicit task-specific oracle rejections retained; no fallback-only failure row found.
3. Independently recomputable T_M from two raw monotonic endpoints: 0/8. Source-defined, session-bound recorded T_M values with qualification: 8/8.
4. Clean successful-agent medians: ChaCha20 n=2, CBC n=3, ECDSA n=3; exact individual values appear in `V4_SUCCESS_TIMING_SUMMARY.md` and `V4_SUCCESSFUL_AGENT_TIMINGS.csv`. RC4: 0 success, no median.
5. Clean V4 adds descriptive successful-agent CBC/ECDSA endpoints absent from the legacy cohort. It does not update the unmatched legacy sample or enable speed ratios.
6. Raw records modified: NO.
7. Proposed networked content-addressed runtime satisfies unchanged H1 in principle: YES, with local runtime digest and linkage captured; no such new execution is claimed.
8. External limitations: provider HTTP retries and token use absent from V4; backend/weights mutable; network egress must be disclosed and captured.
9. New real-agent H1 cohort: narrow pilot has a material distinct joint-provenance claim; approval required.
10. N=40+: not justified for current paper scope.
11. New provider requests: NO.
12. New experiments launched: NO.
13. Arm accounting unchanged: YES, 35 mapped + 1 historical =36.

## Population separation

Public E1 H1=0/54; EXP-034 H1=0/12; EXP-035 H1=3/3 remain distinct. Legacy conditional=10/19 and operational=10/47 remain separate from CLEAN V4's 8 SUCCESS and 4 ORACLE_FAIL labels over 12 retained records. No denominator is pooled.

