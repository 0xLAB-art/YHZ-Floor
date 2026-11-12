# HEB-1 Multiagent Adversarial Re-Audit

Date: 2026-10-19  
Mode: six independent read-only GPT-5.6 Luna subagents plus controller verification  
Network/provider calls: none  
New benchmark or frozen-experiment rerun: none

## Executive determination

The correct original HEB-1 target is a **bounded offline evidence-composition experiment**:

> Can an under-bound evaluator promote individually valid candidate, reference, and evidence records into an unsupported full attribution claim, and can explicit claim-specific joins prevent that promotion on the declared cases?

That bounded hypothesis was tested and the principal result survives independent recomputation:

- HEB-1 held-out: V0/V1 false promotion 36/36; V2 0/36.
- IAR-C attack cases: V2 10/28; V3-sig 14/28; V3-full 0/28.
- B2 held-out: digest-only 8 false promotions; digest-session 0; V3-full 0.
- B2-2: the unchanged Stage01 validator and reference verifier accepted the constructed candidate/execution mismatch; the external wrapper rejected it; the matching control was accepted.

The result is **false attribution/promotion, not false cryptographic success**. The candidate can be cryptographically valid while the credited execution did not produce it.

However, the previous conclusion that the experiments were simply “correct” is too broad. The raw counts are reproducible, but several procedural and implementation claims are wrong or incomplete. In particular, freeze verification, claimed pre-pass ordering, adjudicator integrity checks, B2-2 wrapper semantics, fixture key security, and downstream reachability were overstated or insufficiently tested.

The corrected scientific status is:

> HEB-1 establishes a bounded provenance/composition failure under constructed evidence contracts. It does not establish live exploitability, AI-agent-specific necessity, prevalence, superiority over actual complete provenance products, or a novel mechanism. Exact prior-art duplication remains unresolved/weak rather than fully proven either way.

## 1. Correct reconstruction of the original target

Primary sources:

- `sp2027/analysis/EVALUATOR_BOUNDARY_NOVELTY_PROPOSAL.md:21-44`
- `sp2027/analysis/heb1_crossboundary_20261019/HEB1_EXPERIMENT_PROTOCOL_20261019.md:10-20,36-77`
- `sp2027/paper/main.tex:121-130,200-252,881-888,967-973`

The original target was not a live ACTS campaign, a public submission gateway, or a complete provenance product. It was an offline synthetic evaluator boundary with V0 schema/reference checking, V1 hash-integrity checking, and V2 claim-specific binding. The adversary was a composer of public records who could select or rewrite evidence and recompute unsigned hashes. The frozen model did not include compromised signing keys, trust-anchor replacement, freshness epochs, deployed aggregation, or a network gateway.

The explicit six-claim ladder was:

1. artifact authorship;
2. execution identity;
3. target effect;
4. reference-oracle acceptance;
5. boundary enforcement;
6. final attribution.

The original success condition was bounded reduction of false full-attribution promotion while preserving clean full-attribution cases. Live impact, product superiority, universal provenance security, partial-claim support, and a new general security mechanism were not original frozen guarantees. They were later objectives or extensions.

## 2. What is independently supported

### 2.1 Core results

The following raw artifacts were independently parsed/recomputed without relying on report prose:

- `heb1_crossboundary_20261019/heldout/heldout_results.json`: 64 cases, 36 attack cases; V0/V1 36/36 FP and V2 0/36; clean B0 8/8 and C1 4/4.
- `experiment_b_20261019/iar_c/runs/20261019_121621/results.json`: 44 cases; V2 10/28 attack FP, V3-sig 14/28, V3-full 0/28; V2 rejects 14/16 honest partial cases.
- `experiment_b_20261019/b2/runs/20261019_140814/results.json`: held-out V2 16 FP, V3-sig 28, V3-full 0, digest-only 8, digest-session 0.
- `experiment_b_20261019/b2_2_stage01/B2_2_RESULTS.json`: five-case matrix; mismatch accepted by original validator/reference and rejected by external wrapper; matching control accepted.

The `verify_iar_a.py` reproduction returned `75 PASS / 2 WARN / 0 FAIL`. The warnings concern archival A1b representation, not a verdict contradiction.

### 2.2 Stage01 gap

The real component gap is genuine but narrower than the original HEB V2 result:

- `contract_sound_stage01_validator_v2.py:13-16,57-85` checks five evidence kinds, outer evidence hashes, session/base-instance fields, effect, boundary, identity, and attribution. It does not require reference-acceptance evidence or bind execution to the candidate digest.
- `contract_sound_stage01_reference_verifier_v2.py:57-132` recomputes the cryptographic predicate and checks certificate integrity, but does not prove that the credited execution produced the candidate.
- `B2_2_RESULTS.json` demonstrates the semantic candidate/execution mismatch with all outer hashes valid.

This is a real acceptance-boundary weakness in the unchanged components. It is not evidence of a live campaign exploit because the campaign runners construct certificates internally.

## 3. Concrete errors and missing controls

Each item below is classified as independently reproduced from source/raw artifacts, source-code inference, or an untested hypothesis.

### 3.1 Claimed held-out pre-pass is not implemented

**Classification: independently reproduced implementation/report mismatch.**

`heldout/heb1_heldout_runner.py:161-175` invokes V0/V1/V2 before the adjudicator and only then computes `fixture_validation`. The retained runner contains no adjudicator-only pre-pass before system execution, despite the evaluation report/operator note claiming one. This does not invalidate the published FP counts, but the claimed execution ordering and contamination-control statement must be withdrawn or corrected.

### 3.2 HEB adjudicator does not validate public evidence integrity

**Classification: independently reproduced source finding; missing-control impact untested.**

`build/heb1_adjudicator.py:146-155,216-229` loads evidence and private target state but does not verify declared evidence hashes or compare the public target artifact against the private truth map. It can therefore produce adjudication truth from private state even when public evidence or target bytes are inconsistent. Existing fixtures do not expose this: fixture failures were zero. A tampered-public-target/evidence control is missing.

### 3.3 Held-out runner is absent from the HEB freeze manifests

**Classification: independently reproduced freeze-integrity defect.**

`freeze/HEB1_VALIDATOR_FREEZE.json` and `freeze/HEB1_CONFIG_FREEZE.json` freeze validators, helpers, and selected configuration, but not `heldout/heb1_heldout_runner.py`. The runner's own provenance list at `heldout/heb1_heldout_runner.py:310-317` also omits itself. Thus the held-out result is reproducible from current bytes but its metric/gate implementation was not protected by the declared freeze.

### 3.4 B2 freeze verification is incomplete

**Classification: independently reproduced source finding.**

`b2/b2_runner.py:128-159` checks module, label, trust, and case-count information, but does not verify all declared freeze fields, including frozen reference hashes, case-inventory hashes, protocol hash, and the IAR-B freeze hash. `B2-G5` checks protected files rather than the complete B2 freeze contract. The preserved result is internally useful, but the runner did not prove full frozen-input identity.

### 3.5 IAR-C does not verify its frozen case manifest

**Classification: independently reproduced source finding.**

`iar_c/eb_independent_runner.py:121-143` verifies executable components, labels, and trust, but not the frozen case-manifest hash declared in `IAR_C_FREEZE.json`. Case changes could therefore escape the pre-run component check.

### 3.6 B2-2 wrapper does not implement its protocol description

**Classification: independently reproduced protocol/code mismatch.**

`B2_2_PROTOCOL.md` describes a wrapper that first invokes the original validator and then performs the additional binding check. `external_candidate_binding_wrapper.py:35-76` never invokes the validator; it checks only the trace outer hash, candidate pointer hash, and optional semantic candidate hash. The runner invokes the original validator separately, so the paired five-case result remains interpretable, but the wrapper itself is not the complete wrapper specified by the protocol. It also verifies only the execution-trace outer hash, not every certificate evidence pointer.

### 3.7 IAR-A wording implies identical certificate bytes when they are not

**Classification: independently reproduced archival construction issue.**

`iar_a_stage01_transfer.py:145-174` creates a public certificate for the blind validator and modifies a private certificate for the reference verifier, including changing `reference_oracle_acceptance` to `ACCEPTED`. Therefore “both components accepted the same certificate” is technically imprecise. The acceptance-boundary finding still holds, but the exact claim must be stated as acceptance of paired certificates with the same relevant composition and different reference metadata.

### 3.8 Fixture signing keys are publicly derivable

**Classification: independently reproduced fixture property; production impact untested.**

`eb_fixtures.py:112-123` and `iar_c/eb_independent_gen.py:131-143` derive Ed25519 private keys from public session identifiers and constants. Re-derivation reproduced the published trust-anchor public keys for all inspected fixture sessions. This violates the stated “composer cannot obtain another run’s signing key” assumption inside the shipped fixture implementation. It does not prove a production exploit, because the mechanism is fixture-only, but it invalidates interpreting V3-full as a realistic secret-held issuer model.

### 3.9 Path confinement is absent in model verifiers

**Classification: independently reproduced path behavior; reachable impact is untested.**

`eb_v3_full.py:94-118`, `eb_independent_adj.py:153-168`, and `b2_prov_baselines.py:125-152` resolve evidence as `pub / rel` without rejecting absolute paths, `..`, or symlinks. An absolute path can escape the bundle directory. This matters only if an untrusted bundle is verified against a shared filesystem or archive extraction environment; no such gateway is present in the repository.

### 3.10 Missing operational provenance controls

**Classification: source-code inference; untested.**

V3-full and the B2 models lack several controls that a deployed multi-party evaluator would need:

- nonce/epoch/expiry/revocation and consumed-attempt state;
- signer role/purpose separation and key rotation;
- target ID/state binding inside effect and reference records;
- process/container/binary attestation beyond executor string equality;
- duplicate/conflicting-record policy (different components treat duplicates differently);
- signed evidence-kind/domain separation;
- trust-anchor authenticity and lifecycle;
- authenticated report/aggregation records.

Relevant code includes `eb_v3_full.py:94-210`, `eb_fixtures.py:148-162`, and `eb_adjudicator.py:207-264`. These are not demonstrated live attacks; they are untested hypotheses that become material only if a real external submission/aggregation boundary exists.

### 3.11 Candidate program/output binding is missing in the Stage01 path

**Classification: independently reproduced through B2-2; source-inferred generally.**

The model runner creates `candidate.py` and `candidate_output.json` (`run_contract_sound_agent_pilot.py:57-70`). The certificate binds the agent artifact to `candidate.py`, while the reference verifier evaluates the separate candidate output (`run_contract_sound_agent_pilot.py:87-100,164-170`; `contract_sound_stage01_reference_verifier_v2.py:110-132`). There is no candidate-program/output/trace chain. B2-2 is the preserved semantic mismatch demonstration.

### 3.12 Aggregation/reporting can conceal execution failures or overclaims

**Classification: source-code inference.**

`eb_runner.py:61-80,111-292` reduces malformed/non-JSON subprocess output to missing verdicts and does not retain full raw stderr in its final aggregate. IAR-C improves failure accounting, but still stores reduced per-case verdicts. The current reports do not demonstrate a downstream overclaim; the risk is at manual report synthesis or any future consumer that maps `ACCEPT` directly to “verified exploit completion” without respecting requested/supported levels.

## 4. Baseline fairness and V3-full

The comparison is fair for the primary level-6 question when systems receive the same public cases:

- V2/V3-sig/V3-full level-6 promotion rates are comparable on the same attack cases.
- Digest-only versus digest-session is a controlled design-class ablation.

It is not fair to treat V2's 14/16 IAR-C partial-claim rejects as a quality failure against V3-full: V2 is a full-attribution emitter and does not promise partial levels. Those cases are N/A for V2 under its declared contract.

V3-full's zero is real but conditional. IAR-C improves generator/adjudicator separation and held-out discipline, but shares the target-domain module and six-rung vocabulary with the systems. The corpus does not test malicious authorized signers, public-key derivation as an adversary, trust-anchor replacement, replay epochs, duplicate conflicts, same-session target substitution, multi-party aggregation, or downstream claim consumption. B2 is a model of design classes, not an evaluation of actual in-toto/SLSA/RATS products.

The corrected statement is “zero observed promotions on the tested signed/session-joined synthetic contract,” not “complete provenance security.”

## 5. Reachability correction

The repository inspection supports only:

`NO_EXTERNAL_CERTIFICATE_COMPOSITION_INTERFACE_FOUND_IN_INSPECTED_REPOSITORY_PATHS`

The campaign runners construct certificates internally; the repaired runner can accept a candidate source but still constructs the certificate internally. The repository contains no verified external certificate gateway, webhook, upload, or aggregation endpoint connected to the Stage01 components. This is source-level negative evidence, not proof of universal impossibility. The component boundary is reachable by a local constructed composer; remote/deployed exploitability is unestablished.

## 6. Novelty determination

The broad principle—bind evidence to execution, artifact, target, signer, and freshness context—is established in provenance and attestation work. The local records do not prove that one cited work demonstrates the exact HEB-1 combination of cryptographic evaluation, claim-ladder promotion, cross-run composition, and Stage01 transfer. Therefore:

- “Fully anticipated by one prior work” is not proven.
- “Novel security mechanism” is also not proven.
- The exact AI-agent-specific contribution is unestablished because the demonstrated composer is scripted and the experiments do not show that an AI agent is necessary.

The prior novelty withdrawal was directionally correct, but should be worded as **unresolved/weak and requiring targeted comparison**, not as a proof that every exact combination is already known.

## 7. Single highest-value next experiment

Do not create another broad synthetic benchmark. The highest-value test is one small, authorized submission-boundary experiment against a real or separately authorized faithful gateway, with a common contract containing:

- candidate and execution-output digest;
- execution/session/attempt identity;
- target instance/state digest;
- effect and reference acceptance;
- signer identity, role, and authorized key;
- freshness epoch/nonce and replay state;
- final aggregation/reporting consumer.

Use matched producer arms: a scripted composer and an AI-agent composer. If the AI-agent arm is executed, use the requested `claude-sonnet-4-6-free` model only for that internal experiment, not for the audit controller or audit subagents.

Interpretation:

- both arms fail identically under the same complete contract: generic provenance issue, not AI-specific novelty;
- gateway rejects both: current result remains bounded synthetic evidence;
- scripted mixed bundles are accepted: realistic impact is established, but not necessarily novelty;
- only the AI-agent arm produces unsupported attribution under the same complete contract: candidate AI-agent-specific mechanism, subject to a new prior-art review.

This experiment remains unexecuted because no authorized gateway is currently present and the present work was restricted to offline audit.

## Final answer to the original audit questions

**A. Was HEB-1 tested correctly?** The bounded core was tested sufficiently to reproduce its principal counts, but freeze/pre-pass/integrity claims require correction.

**B. Did it test the intended property?** Yes for bounded false full-attribution promotion under the synthetic composer; no for live AI-agent evaluation or deployed provenance.

**C. Were baselines fair?** Level-6 comparisons were fair; V2 partial false-reject comparisons and product-superiority interpretations were not.

**D. Was a missed realistic failure found?** Several realistic future-gateway risks were found in code, plus fixture-key failure; none establishes a reachable live exploit in this repository.

**E. Is the mechanism fully anticipated?** The broad principle is anticipated; exact combined empirical novelty remains unresolved/weak.

**F. What survives?** The constructed false-attribution result, Stage01 component acceptance gap, and session-binding mitigation on tested cases. What fails: live reachability, universal/security-complete wording, product superiority, and unqualified PASS/freeze/independence claims.

**G. Highest-value experiment?** The small matched scripted-versus-Claude end-to-end submission-boundary test defined above, only after an authorized gateway is available.

No protected artifact, manuscript, frozen result, or prior audit artifact was modified by this re-audit.
