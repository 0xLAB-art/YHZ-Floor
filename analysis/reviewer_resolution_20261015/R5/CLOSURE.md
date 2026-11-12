# R5: claim-specific outcome eligibility

Disposition: **addressed**. Timing disagreement no longer removes four otherwise-valid terminal failures from primary outcome rates. The primary fractions are10/23 conditional success and10/51 eligible operational yield. The three relay-invalid sessions remain excluded for record validity. The full retained census is separately described as ten accepted outcomes among54 records. The original10/19 and10/47 timing-selected fractions remain historical sensitivities.

`outcome_eligibility_v2.py` reads all54 frozen migrated records, verifies each against the statistical correction lock, and checks that every embedded legacy payload equals the corresponding nested `ACTS-ATTACK/harness/rerun/results_rerun/agent/agent_records.jsonl` primary row. Its new outcome ledger retains each ID, task, status, relay defect, timing gate and eligibility decision. Give-up is not relabeled candidate rejection. Four restored outcome rows are all nonsuccesses.

Six tests pass for clock-disagreement failures, provider inclusion, relay invalidity, give-up authority, duplicate IDs and unknown statuses. Main framework/results and supplement populations/E4 use the new estimands; the source map points to the current analysis. Historical locks, old E4 software and time curves are not overwritten. Those curves retain their historical47-row timing-selected population and are explicitly distinguished from corrected outcome accounting.

The20-check reporting/preservation regression passes, including original input groups and frozen hashes. Builds remain13/5/18 pages without undefined or overfull warnings. This correction changes interpretation and eligibility, not the ten verified outcomes or the underlying records.
