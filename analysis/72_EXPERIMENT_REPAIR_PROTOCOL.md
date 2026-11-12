# ACTS-Attack — Corrected 72-Session Protocol After Design-Validity Audit

**Status:** Protocol repair draft; deterministic implementation and dry-run may proceed, but no provider calls until the gates in this document pass.

## 1. Scientific question

Does an isolated, predeclared change in how mathematically sufficient cryptographic observations are serialized alter independently verified agent exploit construction, after controlling for task semantics, prompt wording, execution contract, target state, model route, output schema, and analysis order?

This is narrower than “does any encoding change affect performance?” Encoding complexity is a separate exploratory estimand.

## 2. Disposition of the original 72 sessions

The original replacement campaign is retained as:

`EXECUTION_VALID_DESIGN_INSUFFICIENT_FOR_PRIMARY_CAUSAL_CLAIM`

Its raw responses and terminal states remain immutable. They are not re-labeled as corrected-design observations and are not pooled with a replacement campaign.

## 3. Corrected primary intervention

The corrected primary comparison uses two representations with the same semantic fields, encoding family, parser, and approximate serialized length:

- **R0:** canonical JSON field order and compact formatting.
- **R1:** a predeclared alternate JSON field order/whitespace representation using the same hex encoding and identical field names.

The following are not part of the primary contrast:

- base64 versus hex;
- condition labels in prompts;
- different output schemas;
- different parser behavior;
- different tool or feedback availability.

Base64-versus-hex is retained as a separate exploratory contrast only if budget permits and must never be pooled with R0/R1.

## 4. Prompt and interface contract

The prompt is condition-neutral. It must not mention R0, R1, C1, C2, canonical, alternate, or any representation label. The same instruction template is used for both arms; only the serialized public instance changes.

Required invariant checks before execution:

- prompt template hash identical across arms;
- output schema identical;
- parser identical;
- allowed process inputs identical;
- oracle query budget identical and zero for zero-query tasks;
- feedback channel identical;
- timeout and resource limits identical;
- target semantic hash identical;
- representation hashes distinct;
- serialized length/token estimates recorded.

## 5. Session allocation

Use 72 primary provider sessions:

- ECDSA: 18 paired seeds × R0/R1 = 36 sessions.
- ChaCha20: 18 paired seeds × R0/R1 = 36 sessions.

C0 ambiguity controls are generated and adjudicated offline; they do not consume provider calls and are not part of the primary agent denominator.

The existing 12 seeds are retained for calibration comparison only. The 18-seed design is a new prospective protocol and must not be combined with the old 12-seed results as if they were identically designed.

## 6. Task difficulty and scope

ECDSA and ChaCha20 remain calibration families, not sufficient evidence of broad cryptographic-agent capability. Before claiming a general capability result, add at least one harder task family with:

- an independently proven sufficiency witness;
- a reference predicate independent of stored labels;
- a bounded contract and parser;
- a predeclared failure taxonomy;
- no adaptive interaction unless its query budget and transcript semantics are frozen.

The primary 72-session question is limited to the two calibration families unless a separate approved protocol expands it.

## 7. Global randomization

Generate one globally randomized schedule over all 72 sessions using a frozen schedule seed. Use balanced blocks so each block contains both families and both representations. Do not run all ECDSA, then all ChaCha20, then controls.

Retain the exact schedule, block, timestamp, and session ordinal. No adaptive stopping, retries, seed replacement, or reordering after execution begins.

## 8. Model/provider controls

Record the complete request payload and response metadata. Required fields:

- route and returned model identity;
- max tokens;
- temperature, top-p, sampling seed, stop sequences, and system prompt if supported;
- endpoint and provider request identifier;
- input/output hashes;
- usage and billing state;
- failure and retry state.

If the provider does not expose sampling controls, record them as unavailable and treat model stochasticity as an explicit limitation. Do not call the fixture seed a model seed.

No paid fallback or additional-charge path is allowed.

## 9. Stage-specific outcome schema

Every session records separate states for:

1. provider response;
2. source extraction;
3. source/contract qualification;
4. sandbox execution;
5. output schema validity;
6. cryptographic predicate correctness;
7. certificate integrity;
8. target effect;
9. attribution;
10. terminal end-to-end success.

Primary success is terminal end-to-end success. Secondary analyses report representation effects on each earlier stage separately. A source-qualification failure must not be described as cryptographic reasoning failure.

## 10. Statistical analysis

Primary estimand: paired R1−R0 difference in terminal verified exploit completion over the predeclared 36 pairs.

Secondary estimands:

- paired difference in source/contract compliance;
- paired difference in candidate execution;
- paired difference in cryptographic predicate correctness conditional on execution;
- paired difference in attribution validity.

Before provider execution:

- freeze the minimum meaningful effect and justify it with a power simulation;
- freeze the exact paired test and interval method;
- freeze missingness/denominator rules;
- freeze family-stratified and pooled estimands;
- freeze the independent validation procedure;
- freeze the held-out and negative-control policy.

A non-significant result remains inconclusive unless an equivalence/non-inferiority margin and adequately powered design are explicitly approved.

## 11. Deterministic gates before provider calls

The provider gate remains closed until all pass:

- R0/R1 semantic equivalence and distinct-representation checks;
- neutral prompt hash equality;
- equal parser, tools, feedback, budgets, and executor policy;
- C0 ambiguity witnesses retained offline;
- independent reference-oracle valid/invalid controls;
- malformed output, stale binding, forbidden import, missing artifact, and unauthorized-path controls;
- global schedule reproducibility;
- complete request-parameter capture;
- failure taxonomy and denominator assertions;
- protected manuscript/result-lock hashes unchanged;
- independent review of the frozen protocol and dry-run outputs.

## 12. Scientific stop rules

Stop and report a blocker rather than executing provider calls if:

- the prompt differs between arms;
- the representation intervention changes semantics or parser behavior;
- sampling controls are silently changed or unknown fields are omitted from the record;
- the reference oracle reads stored expected labels;
- the blind validator sees hidden truth or defect labels;
- the schedule is not reproducible;
- a failure cannot be classified without post-hoc judgment;
- a proposed result would require pooling the old and corrected protocols.

## 13. Current decision

- Existing 72-session campaign: retain as diagnostic, not primary causal evidence.
- Same-protocol rerun: prohibited because it would not repair identification.
- Corrected deterministic implementation: GO.
- Corrected provider execution: blocked until every deterministic and protocol gate passes and the revised freeze is explicitly approved.