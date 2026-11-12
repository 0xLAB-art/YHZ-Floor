# Restart memo

Read in order:

1. `MISSION.md`
2. `RESEARCH_STATE.json`
3. `WORK_GRAPH.json`
4. `H1_V2_FAILURE_STAGE_AUDIT.md` and `V4_TRAJECTORY_AUDIT.md`
5. `DECISION_LOG.md`

Current runnable commands:

```bash
python sp2027/research_execution/analyze_initial_evidence.py
python sp2027/research_execution/analyze_v4_trajectories.py
python3 ACTS-ATTACK/harness/v3/service_relay_pilot.py
```

Completed current branch: the additive `blind-opportunity-v1` Claude contrast
was audited and integrated. ECDSA and RC4 each had 2/2 accepted sessions;
ChaCha20 had 0/2 accepted sessions with 3/3 rejected candidate verdicts; no
provider failures occurred. This is mechanism evidence only.

Highest-value next branch: resolve the remaining WebSP/Cybench semantic joins
only to their evidence ceiling, and reconcile the located earlier ACTS
multi-tier source with local historical records and corrected H1 V2. The PQC
family join and C3 service-relay qualification are recorded in
`PQC_FAMILY_RECONCILIATION.md` and
`C3_SERVICE_RELAY_QUALIFICATION_20261018.md`. Compare corrected-interface ECDSA,
ChaCha20, and RC4 by public opportunity, model inference, generated code,
execution, oracle verdict, and cost only as separate exploratory cohorts. Keep
the current results exploratory and separate; do not claim a pooled success
rate, relaunch the 90-call H1 matrix, or pool deterministic controls with model
outcomes.

The full-text novelty register now includes the earlier ACTS multi-tier source.
Audit every manuscript novelty sentence against the expanded register. Do not
promote the contribution candidate to a “first” or unique claim.

The authoritative manuscript is `sp2027/paper/main.tex`; compile from
`sp2027/paper/` with two `pdflatex -halt-on-error` passes after any manuscript
edit. Current build: 17 letter pages; the current hashes are recorded in
`RESEARCH_STATE.json`.
