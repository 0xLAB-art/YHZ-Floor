# Mechanism Specification — the Minimal Claim, Its Property, and Its Prior-Art Delta

**Project:** ACTS-Attack  
**Date:** 2026-10-20  
**Status:** COMPLETE — the mechanism is stated minimally, its property is mechanically checked, and the delta against the searched prior art is stated in the strongest form the evidence supports

## 1. The mechanism, stated minimally

Let `P` be a producer (untrusted), `O` an observer, `R` a reference adjudicator, `A` an aggregator,
and `Φ` a task predicate decidable from a private target state.

A **bound attribution** is a decision `A(B) = ATTRIBUTED` over a bundle `B = (C, E_o, E_r)` — a
certificate `C` and two signed evidence envelopes — such that:

1. **Execution binding.** `E_o` is an observer-signed record over the *exact bytes executed*, and
   it pins the captured stdout digest.
2. **Independent recomputation.** `E_r` is a reference-signed record that recomputes `Φ` from
   the private target state against the **stdout pinned by `E_o`**, and reports the verdict.
3. **Context binding.** Both envelopes are signed over a context
   `(target_id, attempt_id, epoch, role, kind)` that equals the certificate's
   `(target_id, attempt_id, epoch)`, with each envelope's role and kind authorized by a policy.
4. **Cross-record consistency.** `E_r` names the digest of `E_o`, and the certificate's declared
   source and candidate digests equal `E_o`'s.
5. **Claim irrelevance.** `A` never reads the certificate's `claims` block when deciding.

**The property.** If `A(B) = ATTRIBUTED` then the executed bytes produced a candidate that `Φ`
holds for. The claimant's assertions are irrelevant; the producer cannot supply the digests the
decision depends on.

## 2. The property is mechanically checked, not asserted

Property S1 is stated clause by clause in `heb2_contract_v1/PREREGISTRATION.md` §4 and implemented
as an executable check (`heb2_contract_v1/contract.py`, `soundness_violations`).

| Check | Scale | Result |
|---|---|---|
| Seeded mutation corpus over the genuine bundles, both semantics | 4 corpora × 1,407 mutants × 2 arms = **11,256 evaluations** | **0 soundness violations** |
| The only mutation class that remains acceptable | claim-block mutation (`claims.attribution` set to either value) | by design — it *is* clause 5, confirmed empirically |
| Every genuine bundle | 4 corpora | 0 violations |
| Model-arm attribution safety | 2 independent matched-arm runs | 4/4 attributions predicate-backed; 0 false predicates attributed; 0 true predicates missed |
| Live campaign | 1 live containerised target, separate-process oracle | the positive control attributed; the model agent's failed attempt refused |

The corpus is a falsification attempt with a stated scope, not a formal proof.

## 3. What the mechanism is *not*

- It is not a new signature format: Cosign verified 128/128 authentic ACTS signatures and rejected
  128/128 tamper controls. The signature layer is ordinary.
- It is not a new provenance model: in-toto and SLSA have richer, more general metadata.
- It is not a new tri-state adjudication model: adjacent work has that.
- It is not a new sandbox, and it does not claim exploitability, reachability, or prevalence.

## 4. Does the mechanism exceed the known components? — **No**

This section answers the question directly, and the answer is negative.

Every clause of the mechanism in §1 maps to an ingredient the prior-art assessment already
identifies as known (`AGENT5_PRIOR_ART_NOVELTY_MATRIX.md` §2):

| Clause | Nearest known ingredient | Agent 5's verdict |
|---|---|---|
| 1. Execution binding | RFC 9334 attester / target split, in-toto materials–products | "the single most heavily precedented ingredient" — not a contribution |
| 2. Independent recomputation | differential validation, oracle fault-injection (arXiv:2610.16067) | established practice |
| 3. Context binding | claim-specific join predicates; SLSA per-field expectations | known |
| 4. Cross-record consistency | standard digest chaining | known |
| 5. Claim irrelevance | tri-state MISSING/CONTRADICTORY distinction; claim-level evidence mapping (arXiv:2606.04990 §3.2) | "the *principle* is a known general principle"; the tri-state contract is "a small, defensible engineering increment" |
| plus epoch + replay ledger | TUF | TUF is the reference implementation |
| plus signer role authorization | Sigstore / in-toto functionary keys | "NATIVE and, if anything, the *most* saturated ingredient. Not a contribution." |
| plus a final-claim aggregator that cannot overclaim | RFC 9334 §8.4, SLSA VSA, in-toto, llmsa | "NATIVE in RATS/SLSA/in-toto, and already *theorized* in the 2026 agent-governance literature. Not a contribution; and note that a theorem is a harder-to-beat baseline than a measured detection rate." |

The family itself is not new either. Agent 5 locates the cross-boundary promotion mechanism in at
least five independent works and names it: it is the **confused-deputy / evidence-substitution**
pattern, "which is decades old". The assessment's own summary of the contribution is that ACTS is
"at best, a *re-domained instance* of a known pattern and a *new measurement* of its rate in one
domain", and that the union of ingredients is "fully established" by RFC 9334, in-toto, TUF,
Sigstore and llmsa.

**Accordingly: the mechanism does not exceed the known components, and this project does not claim
that it does.** The prior-art assessment is the controlling document on this question, and it also
notes that the closest 2026 work supplies a *theorem* — a harder-to-beat baseline than any measured
detection rate this project can produce.

## 5. What the project does add, and how far that goes

What the searched prior art does not exhibit is a **matched measurement**: the same evidence, the
same corpus, and the same question, put to the native upstream models and to this contract. The
delta is in the evidence, not in the mechanism:

| Evidence | Result |
|---|---|
| Stage 6, identical evidence through a **minimally configured** in-toto deployment (no rules, no inspection) | **16 of 16** non-attributable cases false-promoted — a default-configuration measurement, not an in-toto limitation |
| Stage 6, in-toto **with its own artifact rules and an independent inspection** | **22/22** agreement with the ACTS contract once the inspection is stateful (21/22 stateless) — the upstream model *can* host the policy |
| Stage 6, SLSA | **NOT_COMPARABLE** — verification stops at provenance acquisition (Rekor), before any policy stage |
| Stage 1 and HEB-2, the ACTS contract | **0** false promotions over 16 non-attributable cases, replicated across three independent executions and two model arms |

The corrected comparison changes this materially. The upstream models do **not** decide wrongly
when they are given the policy: in-toto, with its own artifact rules and an independent inspection,
reproduces this contract's decisions exactly. So the claim cannot be "the upstream models decide
wrongly". What the evidence supports is narrower and sharper:

> The **policy** is not part of the upstream frameworks. The frameworks supply authenticity, authority,
thresholds and artifact rules; the attribution policy — causal binding, an independently recomputed
predicate, a per-case signed context, and a cross-case replay ledger — must be written and operated
by the adopter. This project contributes that policy, a specification of it, a mechanized check of
its soundness, and the measurements above.

## 6. The honest limit of the novelty claim

"Previously unknown" cannot be established exhaustively, and no finite search proves absence. More
importantly, **the prior-art assessment already answers the question against the strong reading**:
the mechanism's components are known, the union is established, the family is decades old, and the
closest work provides a formal theorem. A composition of known parts, even a new arrangement of
them, is not a new mechanism.

The supported statement is therefore the narrow one the prior art permits:

> A **matched measurement and a checkable reference contract** for the confused-deputy /
> evidence-substitution pattern in AI-agent evaluation: the same 22-case evidence run through the
> native upstream models and through this contract, showing 16/16 and 6/6 misdecisions by the
> native models against 0/16 by the contract; a mechanized soundness check of the contract
> (11,256 evaluations, 0 violations); a replicated matched arm under a model producer; a boundary
> demonstration over a network ingress; and a live campaign against the project's own containerised
> target. The *mechanism* is a re-domained instance of a known pattern; the *contribution* is the
> measurement, the contract, and the reproducible artifacts — and it is explicitly weaker than the
> existing Chain Verifiability Theorem.

This is what `NOVELTY_PRIOR_ART_MATRIX.md` now states, and it is consistent with Agent 5's
assessment rather than a softer version of it.

## 7. What would falsify the contribution

- A prior-art system that, on the *same* 22-case evidence, refuses all 16 non-attributable cases
  **without** delegating the attribution policy to an external verifier. (The corrected Stage 6 run
  shows in-toto reaches this only with a full policy inspection, so the search must look for the
  *policy*, not for the framework.)
- A counterexample to S1 reachable within the mutation corpus's neighbourhood, or any accepted
  bundle that violates S1 in a broader search.
- A prior-art system that, on the same evidence, attributes exactly the 6 attributable cases with
  no external policy component.

None of these was found in the searched literature, and the second is now tested mechanically over
11,256 evaluations.

## 8. Where the evidence lives

| Claim | Evidence |
|---|---|
| the property | `HEB2_CONTRACT_V2_RESULTS.md`, `heb2_contract_v1/soundness_*.json` |
| the differential against native models | `STAGE6_MATCHED_TRANSLATION_RESULTS.md`, `stage6_matched_translation/translation_results.json` |
| the live reachability of the contract | `STAGE5_LIVE_CAMPAIGN_RESULTS.md`, `stage5_live_campaign/runs/` |
| producer-authorship invariance | `STAGE4_AI_AGENT_COMPARISON.md`, `stage4_arms/model_arm_manifest.json` |
| the prior-art delta and the "does not exceed the known components" verdict | §4 here, and `NOVELTY_PRIOR_ART_MATRIX.md` (and the Agent 5 work it rests on) |