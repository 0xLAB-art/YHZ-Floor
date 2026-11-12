# P010L4 rerun — REPORT (clean transport, canonical record)

The first pass (info_contract_label4_20261030) lost 14 of 32 sessions to
provider no-body responses on a degrading route. This registered rerun — same
seeds 211-218, label gpt-5.6-sol, fixture, prompts, oracle, 2800-token floor —
completes the design: 32/32 sessions, 0 transport failures.

## Outcome (frozen analyzer, ANALYSIS.json)

- Per cell: C1 8/8, C2 2/8, C3 8/8, C4 0/8 accepted.
- The 14 non-acceptances are EMPTY_RESPONSE floor-exhaustions in the withheld
  arms (6 C2 + 8 C4): model-side reasoning length under the floor, not
  transport (EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md). One C4 session
  (seed 211) submitted once before exhausting.
- Premise marginal 16/16 vs 2/16 (Fisher 2.5e-7 / 5.1e-7); CMH chi2=19.6,
  p=9.5e-6; naming 8/16 vs 10/16 (p=0.72); paired C1-vs-C4 8/0, p=0.0078125.
- Fingerprint audit: 19/19 raw responses echo gpt-5.6-sol, 0 mismatches.
- The two C2 acceptances the damaged pass glimpsed are real on this label;
  C4's rejection degree is measured, not unmeasured.
