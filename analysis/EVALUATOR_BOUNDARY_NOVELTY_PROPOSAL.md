# ACTS-Attack Evaluator-Boundary Novelty Proposal

**Date:** 2026-10-18  
**Status:** DESIGN ONLY — no new provider/model calls, no implementation campaign, no manuscript change  
**Relationship to H1:** Separate follow-on direction; the preregistered C1/C2 H1 result remains NOT SUPPORTED.

## 1. Motivation and boundary

The completed 72-session pilot establishes a reliable negative/inconclusive result for the prespecified representation intervention. It does not establish a new evaluator-security mechanism. The next direction must therefore be narrower than “oracle integrity is important” and must produce a falsifiable security consequence beyond a generic warning that evaluators can be wrong.

The existing prior-art matrix identifies the relevant overlap:

- **ExploitGym:** realistic executable exploit benchmark scale and defenses; scale and working exploits are not the proposed contribution.
- **ExploitBench:** capability ladders, deterministic oracles, differential execution, and harness ablations; staged evaluation and oracle use are not sufficient novelty.
- **CryptanalysisBench:** cryptanalysis task coverage and independently verifiable attacks; more cryptographic tasks are not sufficient novelty.
- **ReproBench:** evidence-backed reproduction stages; artifact staging alone is not sufficient novelty.
- **When Agent Evaluation Becomes Unreliable:** oracle-integrity audits, replay/ablation analysis, and evaluator-fault measurement; generic evaluator unreliability is already known.

The proposal must therefore test a specific failure mode caused by **composition across claim boundaries**, not simply repeat a fault catalogue.

## 2. One primary falsifiable hypothesis

### HEB-1 — Cross-boundary verdict promotion

> When a cryptographic exploitation evaluator composes a candidate artifact, a reference-oracle verdict, and an evidence-integrity verdict without enforcing the identity of the candidate, run, condition, target instance, and claim scope at every join, a **cross-boundary verdict-promotion** failure can produce an attributable “verified exploit completion” claim for a candidate that did not itself produce the reference-verified target effect. A claim-specific binding validator will detect these promotions while preserving clean valid and invalid outcomes with bounded overhead.

This is intentionally narrower than “evaluators can be unreliable.” It predicts a concrete semantic security failure: a valid cryptographic verdict from one evidence object can be promoted to a stronger attribution claim about a different artifact or execution when the composition boundary is under-specified.

The hypothesis is falsified if, under a predeclared family of cross-run/cross-condition joins, the simpler baseline validators never produce the stronger false attribution claim, or if the claim-specific validator cannot reduce false promotion without unacceptable clean-case false rejection/overhead.

The proposal does **not** claim that this mechanism is novel yet. Novelty remains conditional on a closest-prior-art review and an independently reproduced result showing that the failure mechanism and measured consequence are not already established.

## 3. Security property and claim separation

The evaluation must keep the following claims separate:

1. **Artifact authorship:** the candidate file is the artifact emitted by the recorded producer/session.
2. **Execution identity:** the recorded executor ran the bound candidate under the declared boundary.
3. **Target effect:** the bound candidate caused the declared target-side effect.
4. **Reference-oracle acceptance:** the independently recomputed cryptographic predicate accepted the candidate output.
5. **Boundary enforcement:** the execution and data-flow restrictions were actually enforced.
6. **Attribution:** the evidence supports the claim that this candidate, in this run and condition, produced this verified effect.

Hashes can support integrity and identity bindings under stated trust assumptions. They do not prove exclusive acquisition, private reasoning, absence of unrecorded channels, or immutable hosted-model identity.

## 4. Matched experimental design

### Fixed elements

For every case, hold fixed:

- Candidate source artifact.
- Target state and synthetic secret.
- Public cryptographic instance.
- Declared cryptographic predicate.
- Input/output schema.
- Executor and resource limits.
- Provider response, if a model-authored artifact is used.
- Prompt, model route, and budget, if model calls are later authorized.
- Independent reference adjudicator.

The primary causal intervention is evaluator-boundary composition, not candidate quality or cryptographic difficulty.

### Evaluation conditions

- **B0 — Clean composition:** correctly bound candidate, target, run, condition, certificate, and reference result.
- **B1 — Cross-run join:** candidate from run A is paired with a reference-accepted output/certificate from run B while the cryptographic target is held fixed or deliberately distinguishable.
- **B2 — Cross-condition join:** C1/C2 or valid/invalid condition metadata is changed while the candidate and target artifacts remain fixed.
- **B3 — Stale-artifact replay:** a prior valid output is attached to a new candidate/run identifier.
- **B4 — Claim-strength escalation:** evidence sufficient for “reference accepted” is presented to a baseline as if it proved “this candidate executed and caused the target effect.”

The first confirmatory contrast should use **one** intervention, selected before fixture generation. B1 is the recommended primary contrast because it directly tests verdict promotion while leaving the cryptographic truth unchanged.

### Validator arms

- **V0 — Simple baseline:** checks schema and a reference verdict but does not enforce complete cross-object bindings.
- **V1 — Hash-only baseline:** checks selected hashes but not complete semantic identity/claim relationships.
- **V2 — Claim-specific boundary validator:** validates run, candidate, target, condition, executor, certificate, reference verdict, and claim-strength bindings; rejects evidence that supports only a weaker claim than the requested output claim.

The blind validator must not receive defect labels, hidden secrets, expected verdict labels, or reference-oracle outputs that are unavailable under its declared trust model. The independent adjudicator is a separate process that recomputes the cryptographic predicate from immutable target state and candidate output; it must not read stored expected labels.

## 5. Controls and held-out evaluation

### Clean controls

Include balanced clean cases:

- Valid candidate with valid target effect.
- Invalid candidate with independently rejected cryptographic output.
- Valid candidate with malformed certificate.
- Valid candidate with stale or mismatched run identifier.
- Valid candidate whose evidence supports reference acceptance but not attribution.

Clean controls establish false-rejection behavior and prevent a validator from obtaining a high score by rejecting everything.

### Historical motivating cases

Reuse real ACTS-Attack defects only as motivating, labeled outside the blind validator's input. At minimum, retain the wrong-field comparison, label-reading reference-verifier design, stale binding/order defects, and the source-policy/contract mismatch as distinct historical cases. Historical cases must not be the only evaluation set.

### Held-out generation

Freeze V2 and its configuration before an independently written generator creates held-out cross-boundary variants. The generator must not expose defect labels or mechanism names to V2. Held-out variants should include at least one composition pattern not used during V2 development, subject to feasibility and a predeclared generator specification.

A single evaluation pass is required after the freeze. No validator edits, seed replacement, outcome-based exclusions, or adaptive stopping are permitted after held-out results are observed.

## 6. Independent ground truth and endpoints

The reference adjudicator recomputes the cryptographic predicate from the immutable target instance, candidate output, and declared target-effect condition. It must be tested with intentionally mislabeled fixtures and must disagree with the stored label when the label is wrong.

Primary endpoint:

- **False attribution-promotion rate:** fraction of boundary-mismatch cases for which a validator emits the stronger attributable exploit-completion claim even though the independently bound candidate did not produce the reference-verified target effect.

Secondary endpoints:

- False acceptance of invalid or mismatched evidence.
- False rejection of clean valid cases.
- Detection precision, recall, and per-mechanism confusion matrix.
- Agreement between the validator and the independent adjudicator on the claim actually requested.
- Added validation latency and resource cost.
- Sensitivity to each binding field: run ID, candidate hash, target ID, condition, executor identity, output hash, and claim level.

Raw oracle acceptance must never be treated as attribution. Report the two separately.

## 7. Evidence certificate requirements

Each case should retain:

- Case/run/condition identifiers.
- Candidate source hash and extraction hash.
- Target instance hash and public-input hash.
- Candidate-output hash and schema version.
- Executor version, boundary configuration, and resource limits.
- Reference-verifier version and recomputed predicate details.
- Blind-validator version and accessible input manifest.
- Claim-specific evidence status for all six claim classes.
- Failure stage, stderr/stdout references, and missing-evidence markers.

The certificate should state exactly which claim is supported and which stronger claims remain unresolved. It must never infer exclusive acquisition or hosted-model identity from hashes alone.

## 8. Prior-art differentiation test

Before implementation, perform a focused review of the closest oracle-integrity and agent-evaluation papers for the exact combination of:

1. cross-object/run semantic binding,
2. promotion from a weaker cryptographic verdict to a stronger attribution claim,
3. independent recomputation of the cryptographic predicate,
4. blind claim-specific validation, and
5. measurement against simpler hash/schema baselines.

If an existing paper already demonstrates this same composition failure and mitigation, HEB-1 is not a novelty contribution and should be rejected or narrowed. If prior work discusses the ingredients separately but does not establish this failure mechanism and consequence, the planned experiment may be justified—but only after independent reproduction.

## 9. Risks and anti-overclaim rules

- A synthetic injected mismatch can be too artificial; include at least one naturally occurring historical defect and explain external validity limits.
- A validator may reject all ambiguous evidence; clean valid controls and claim-level scoring are mandatory.
- The reference adjudicator may be independent of labels but still share implementation assumptions; use separate code paths and mislabeled-fixture tests.
- A cryptographic verdict may be valid while attribution is invalid; this is the intended distinction, not a contradiction.
- A cross-run case must not accidentally change the cryptographic target or candidate semantics; all join operations need explicit invariants.
- Do not claim a new security mechanism from a certificate schema, hash list, or perfect performance on self-generated fixtures alone.
- Do not use the two C2 `hashlib` failures as evidence for HEB-1; they are exploratory contract-compliance observations from H1.

## 10. Resource estimate and approval gates

This is a design estimate, not an authorization to execute:

1. Prior-art and protocol freeze: 1–2 researcher-days.
2. Independent adjudicator and binding-case generator: 2–4 researcher-days.
3. Baseline and V2 implementation: 2–3 researcher-days.
4. Clean, historical, and held-out fixture construction: 1–2 researcher-days.
5. Offline deterministic validation and independent reproduction: 1–2 researcher-days.
6. Optional model-authored artifact extension: only after deterministic gates pass and separately approved; provider budget must be explicitly frozen.

GO to implementation only if:

- The prior-art review finds no direct duplicate of HEB-1.
- The independent adjudicator recomputes truth and defeats mislabeled fixtures.
- V0/V1/V2 inputs and trust boundaries are fully documented.
- The primary contrast is frozen before held-out generation.
- Clean controls, historical cases, and held-out cases are specified.
- The expected false-promotion endpoint and minimum meaningful effect are preregistered.
- No manuscript or existing result lock is changed.

NO-GO if any of the following holds:

- The proposed mechanism is already demonstrated by closest prior art.
- The “novel” outcome is only validator agreement with stored labels.
- The experiment cannot distinguish cryptographic correctness from attribution.
- The blind validator can access hidden truth or defect labels.
- Held-out generation is not independent of validator development.
- The result would rely on post-hoc case selection or a changed claim.

## 11. Current recommendation

**GO for protocol review and prior-art verification.**  
**NO-GO for implementation, provider calls, new model sessions, or manuscript incorporation until the gates above are explicitly approved.**

The proposal is a falsifiable research direction, not a claimed discovery. The only currently supported scientific conclusion remains the locked H1 disposition in `H1_FINAL_DISPOSITION.md`.