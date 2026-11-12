# Matched corrected-interface replication design

Status: design-ready, not yet a capability estimate.

The ECDSA, ChaCha20, and RC4 lanes each produced a first-submission oracle
acceptance in two synthetic seeds, but their fixtures and prompts are
family-specific. The next experiment must test reproducibility of the
model-to-code transition without pooling families or turning the exploratory
observations into a rate.

## Design

For each family, retain the existing qualified public schema and independent
oracle, add two unseen deterministic seeds, and keep the same provider route,
turn budget, parser, policy filter, execution sandbox, and first-submission
verdict rule. Record one run ID per seed and retain raw responses, prompt and
public-input hashes, provider metadata, code digest, execution result, and
oracle event. The verifier-held truth remains local and absent from portable
manifests.

The primary endpoint is a stage vector per run:

`response -> parse -> policy -> generated program -> execution -> independent oracle`.

Secondary observations are code length, imports, retry count, runtime error
class, and cost. These are descriptive and family-stratified. A failed run is
not collapsed into a provider failure, an abstention, or an oracle failure.

## Discriminating contrasts

- **Opportunity contrast:** RC4 known-plaintext keystream reuse, ChaCha20
  same-nonce known-reference reuse, and ECDSA repeated-nonce recovery remain
  separate mechanism cards.
- **Interface contrast:** compare only within a family against the already
  qualified corrected schema; the defective ECDSA v1 cohort remains a harness
  diagnostic and is not a control arm.
- **Feedback contrast:** if a later arm is added, randomize feedback availability
  within family and seed before provider calls. Do not interpret the current
  two-turn scripts as a feedback effect because most runs succeeded on turn one.
- **Oracle contrast:** retain independent local truth and a separate verdict
  event. Never expose truth in feedback or infer acceptance from output shape.

## Stop and interpretation rules

This design does not authorize a blind repeat of H1 V2, a pooled cross-family
success rate, or a provider/model capability claim. If the new seeds fail, the
result is a bounded replication failure and a mechanism-localized observation.
If they succeed, the manuscript may state that the qualified transition was
reproduced on additional seeds per family, still without generalization beyond
the fixture, provider route, and sampled seeds. Any causal feedback claim
requires a separately preregistered matched feedback arm.
