# HEB-1 Independent Adversarial Scientific Audit

**Date:** 2026-10-19
**Scope:** HEB-1, IAR-A/B/C, B2-1, B2-2
**Disposition:** completed; read-only; offline; no new benchmark

## Executive determination

The previous work established a real and reproducible **constructed evidence-
composition failure**. It did not establish a live campaign exploit, defeat an
actual complete provenance product, or a previously unrecognized security
mechanism.

However, the previous conclusion also needs correction:

1. “V2 false rejects” on partial claims are not a fair baseline-quality result.
   Frozen V2 is a level-6/full-attribution emitter, not a general partial-claim
   validator. IAR-C's 14 false rejects are therefore out-of-scope functionality
   failures, not evidence that V3-full is more accurate on a common contract.
2. The local prior-art record establishes that execution/provenance binding,
   freshness, replay resistance, and claim/evidence binding are known principles.
   It does **not** prove that the exact empirical combination “cross-run verdict
   promotion in AI-cryptographic evaluation + blind adjudicated measurement” is
   already demonstrated in one prior work. The defensible novelty status is
   **unresolved/weak, not fully settled either way**.
3. B2's digest-only result is a valid counterexample to the implemented
   **digest-only model**, not to in-toto, SLSA, RATS, or any actual complete
   product. The report correctly states this limitation; any stronger summary is
   unsupported.

## A. Was the original hypothesis tested correctly?

**Answer: mostly yes for the bounded synthetic hypothesis.** The protocol froze a
specific hypothesis, six claim classes, B0-B4 defect families, clean controls,
an independent adjudicator, a held-out B5 composition, and a single pass. The
raw HEB-1 held-out file independently recomputes to 64 cases with 36/36 baseline
false promotions and 0/36 V2 promotions. IAR-A independently reruns the real
Stage01 components and confirms A1.

The scope is narrower than the researcher's exceptional objective. HEB-1 tests a
constructed certificate composer under an explicit adversary capability. It does
not test an actual submission service, a model-generated certificate, or a
deployed evaluator.

## B. Did it test the intended security property?

**Yes, for the explicit full-attribution property.** A1 is not a cryptographic
false positive: the Y candidate is valid and the reference verifier correctly
accepts it. The unsupported proposition is that X's credited execution produced
that candidate. The raw A1 registry says X's candidate hash differs from Y's and
X's target effect is `NOT_OBSERVED`; both real components nevertheless accept the
assembled certificate.

This is a security-relevant claim-consumption failure only when a composer can
select records across runs. The original campaign runners do not expose that
composer boundary. Thus the evidence proves acceptance logic, not deployed
operational impact.

## C. Are the comparisons fair?

### Fair part

For level-6 attack cases, V2, V3-sig, V3-full, digest-only, and digest-session
receive the same public case contract and are compared against independently
recomputed truth. The level-6 false-promotion contrast is meaningful:

- HEB-1 held-out: V0/V1 36/36, V2 0/36.
- IAR-C: V2 10/28 attack FP, V3-sig 14/28, V3-full 0/28.
- B2 held-out: digest-only 8 FP, digest-session 0, V3-full 0.

### Unfair or non-comparable part

V2's source (`heb1_v2_claim_binding.py:4-7, 154-192`) emits only when all joins
and the six-rung chain reach level 6. It has no partial-claim acceptance mode.
IAR-C nevertheless places it beside V3-sig/V3-full on honest levels 1-5 and
counts 14 rejections as false rejects. That metric asks V2 to satisfy a stronger
functionality than it implements. The corrected comparison is:

- compare all systems on level-6 requested claims for false promotion; and
- compare partial-claim preservation only among systems whose declared contract
  supports partial claims.

Under that correction, V3-full's zero observed level-6 promotions survives, but
the claimed comparative advantage in partial-claim preservation is not a
V2-versus-V3 result.

## D. Is there an overlooked realistically reachable mechanism?

### Confirmed mechanism

IAR-A/B2-2 establish an overlooked **implementation boundary** in the real
Stage01 components: candidate integrity and cryptographic correctness are bound,
but candidate-to-execution provenance is not. The mismatch case has valid outer
hashes, a true cryptographic predicate, and an original ACCEPT/ACCEPTED result;
the external wrapper rejects only after adding a semantic candidate hash to the
trace.

### Not established as reachable

The composer is synthetic. The five campaign runners create certificates
internally. The extended read-only search found no external certificate/bundle
gateway, importer, API, webhook, or aggregator that accepts an untrusted bundle.
The corrected reachability conclusion is therefore source-scoped, not a claim
that no deployment could ever have such a path.

### Additional source-level concern

`run_contract_sound_agent_pilot*.py` sets `target_status` from candidate execution
status before reference adjudication (`run_contract_sound_agent_pilot_free_v2.py:
164-170`). The public validator can consequently accept an execution/effect/
attribution declaration even when the independent reference later rejects the
candidate. Current reporting retains both results and its primary-success logic
requires reference acceptance, so this is an **untested downstream-consumer
hazard**, not an observed campaign false promotion.

## E. Does prior art fully anticipate the mechanism?

**The broad defense principle is anticipated; exact empirical novelty is not
resolved by the repository's prior-art procedure.** The local assessment covers
RATS, in-toto-style provenance, TRAP/ReplayBench, SimGlot, ReproBench, and
claim-computation audits. It correctly identifies session/context binding and
freshness as adjacent or direct ingredients. It also admits that several sources
were classified from abstracts/READMEs rather than full text and that the sweep
is not exhaustive.

The strongest honest wording is:

> HEB-1 supplies an independently reproducible empirical instance of a known
> provenance/binding class in a cryptographic-agent evaluation evidence shape.
> The repository does not establish either exact prior-art duplication or a new
> mechanism beyond that class.

The previous categorical “novelty not established because the exact principle is
already known” should be replaced by this bounded unresolved determination.

## F. V3-full zero-error audit

The zero is real on the preserved cases, but conditional:

- IAR-C uses an independently written generator, adjudicator, IDs, keys, and
  labels; this is meaningful replication evidence.
- The adjudicator and evaluated systems still share the same six-rung claim
  contract, evidence field vocabulary, and `eb_crypto` target-domain module.
- The attack families mostly exercise the same known join dimensions that
  V3-full was designed to enforce. The generator-side adversary can select
  authentic records, but does not model compromised signers, malicious trust
  anchors, key rotation/epoch confusion, freshness nonce reuse, duplicate or
  conflicting records, aggregator retries, target-state substitution with valid
  signatures, or a real multi-party ingestion protocol.
- B2 explicitly says it models design classes, not literal in-toto/SLSA/RATS
  products, and has no nonce-bearing field or multi-party layout.

Therefore V3-full's result is “zero on the tested authenticated session-join
contract,” not “complete provenance systems are superior” or “all signed valid
evidence is safe.”

## G. Signed evidence and realistic aggregation

The existing results do prove that signatures alone are insufficient for the
tested composition: V3-sig false-promotes 28/58 held-out cases while V3-full
does not. But the signer model is favorable to V3-full: the expected defense is
session equality, and the records are generated with keys that the adjudicator
also understands. No preserved case tests a malicious or wrongly authorized
signer producing a valid statement for the wrong run, a replay across trust
epochs, or a consumer that aggregates multiple individually valid attestations
with a different join policy.

That is a missing threat-model dimension, not evidence that such an attack works.

## H. Concrete implementation/reporting findings

| ID | Finding | Class | Consequence |
|---|---|---|---|
| F-01 | Stage01 `REQUIRED` omits `reference_acceptance`; `claims.reference_oracle_acceptance` is not bound to evidence | IR/source | A consumer trusting public validator ACCEPT can accept an unsupported oracle claim; A2 reproduces this |
| F-02 | Stage01 does not bind execution trace or authorship record to candidate hash/session | IR | A1 false attribution accepted by both real components |
| F-03 | Stage01 `execution.trace_hash` is declared but not checked | IR | A2 trace-hash rewrite/zero is accepted |
| F-04 | V2 partial false-reject denominator is functionality-mismatched | IR/source | Correct as an observed rejection, invalid as comparative quality evidence |
| F-05 | B2 digest-only/digest-session are design-class models, not actual products | Report limitation confirmed | No product-superiority claim follows |
| F-06 | V3-full attack model omits signer/anchor/epoch/aggregation attacks | SCI | Zero is conditional and incomplete |
| F-07 | B2-2 reachability scan was initially only a regex over five runners | SCI, corrected by this audit | Downgrade absolute wording to inspected-source scope |
| F-08 | IAR-A stored archive omits an A1b result row although the memo records it | IR warning | Reproducibility package is complete enough to rerun, but archival denominator/reporting is not perfectly self-contained |
| F-09 | Stage01 runner derives `target_status` from execution before reference result | SCI | Downstream consumers could overclaim if they use validator/effect only; current readiness predicate avoids this |

## I. Corrected answers A–F

- **A:** Yes, the bounded synthetic HEB-1 hypothesis was tested correctly; the
  exceptional live/deployed hypothesis was not.
- **B:** Yes for full-attribution false promotion; no for universal attribution
  soundness or deployed impact.
- **C:** Level-6 comparisons are fair; V2 partial false rejects are not.
- **D:** A real-component acceptance gap exists, but no reachable campaign
  ingestion path was found in the inspected repository.
- **E:** The broad binding/freshness principle is known. Exact empirical novelty
  is not proven absent or present by the local review.
- **F:** Survives: A1 acceptance, HEB-1/V3-sig/B2 digest-only measurements,
  V3-full zero on the tested contract, and the no-live-path limitation. Correct:
  V2 partial-FR interpretation, absolute reachability wording, and any claim of
  complete-product superiority.

## J. Single highest-value new experiment

Do **not** run another large synthetic benchmark. The decisive experiment is a
small, end-to-end **authorized submission-boundary test** against a real gateway
or a separately authorized faithful gateway implementation that is not part of
the current campaign:

1. Freeze a common contract with candidate, execution session, target instance,
   effect, reference acceptance, signer identity, freshness/attempt nonce, and
   claim level.
2. Submit one clean bundle and one bundle assembled from two authentic sessions.
3. Test four consumers: the current Stage01 validator, a digest-only model, a
   session-bound verifier, and the gateway's production aggregation/reporting
   path.
4. Include a malicious-signer/authorized-key distinction and a replay across two
   freshness epochs.
5. Require raw gateway request, accepted bundle, downstream report, and private
   adjudication artifacts. A false promotion must survive the gateway and final
   reporting path; otherwise it is only a component-boundary defect.

Decision rule:

- If a real gateway accepts the composed bundle and reports attributable exploit
  completion while the private adjudicator rejects attribution, HEB-1 has a
  realistic security-impact result; novelty still requires full prior-art work.
- If no gateway accepts external composition, or it rejects at the session/freshness
  boundary, stop calling the result operationally reachable.
- If only digest-only accepts, the contribution remains a bounded empirical
  demonstration of a known under-binding design class.

This experiment requires explicit authorization and an in-scope local or client-
provided gateway. It is not executable under the current offline/no-provider
constraints, so it remains a single unexecuted discriminating hypothesis.

## Final scientific determination

**HEB-1 is a valid bounded empirical security measurement, not the exceptional
result originally sought.** The evidence is stronger than “mere synthetic
certificates” because IAR-A reaches the unchanged real Stage01 components, but it
still lacks an untrusted ingestion boundary and a deployed/complete-provenance
comparison. The honest current claim is:

> Under a constructed composer and the tested evidence contracts, individually
> valid cryptographic evidence can be composed into an unsupported attribution
> claim; explicit cross-record execution binding prevents the observed cases.

No claim of live exploitability, exact novelty, prevalence, or superiority over
actual complete provenance systems is justified by the preserved evidence.
