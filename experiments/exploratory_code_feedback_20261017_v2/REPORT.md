# Model-to-code feedback exploration, v2

Protocol: `P009-H1-EXP-CODE-FEEDBACK-v2`.

The v1 schema defect was corrected prospectively by writing the same public
ECDSA fields at the top level of the instance file. Two qualified synthetic
instances were run through the same bounded model-generated-code path. Both
provider responses arrived successfully; both generated programs passed the
static policy, executed locally, produced candidates, and were accepted by the
independent verifier on the first submission: 2/2 sessions, 2/2 oracle
acceptances, 0 provider failures.

This is a small exploratory observation, not a causal estimate and not a
replacement for corrected H1 V2. It supports a sharper mechanism hypothesis:
the earlier one-shot H1 construct had a severe interface/agency limitation;
when the model could author executable code against an explicit public-file
interface, the ECDSA construction crossed to verified recovery. No verifier
scalar was placed in the model-visible file or portable summary. Estimated
accounting cost was $0.013953 on the provider's reported free route; no invoice
cost is claimed.
