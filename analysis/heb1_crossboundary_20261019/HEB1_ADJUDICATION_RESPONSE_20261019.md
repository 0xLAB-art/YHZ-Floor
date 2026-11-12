# HEB-1 Adjudication Response and Independent Replication Protocol

**Date:** 2026-10-19
**Status:** external review recorded; pre-review novelty claim withdrawn; independent adversarial replication authorized (GO)
**Scope:** offline only; no model/provider calls; no changes to protected locks or frozen HEB-1 artifacts

## 1. Adjudication recorded

The external review confirmed the synthetic mechanism and the B5 held-out
result from `heldout/heldout_results.json`, and adjudicated:

| Item | Decision |
|---|---|
| Synthetic mechanism reproduction | **Confirmed** |
| B5 held-out result | **Verified in JSON** (6/6, both primitives, J2 only) |
| Novel relative to closest prior art | **Not established** |
| Real evaluator security impact | **Not demonstrated** |
| Further independent replication | **GO** |

The review's counts were independently recalculated from the supplied JSON:
64/64 held-out cases, 36/36 defect cases promoted by V0 and V1, 0/36 by V2;
V2 accepted B0 8/8 and C1 4/4; C2/C5 rejects are not evidence of zero false
rejection at weaker claim levels.

The pre-review sentence in `HEB1_EVALUATION_REPORT.md` §5 ("Genuinely new
finding — yes, with explicit scope") is **withdrawn as a novelty claim**. It
recorded the assessment made before RFC 9334, in-toto, the `evidence.*`
family, and TRAP/ReplayBench were considered. The experimental results
themselves are unchanged. A dated addendum now appears in the report.

## 2. Disposition of the four review issues

### 2.1 V1 is a weak baseline relative to real provenance practice

**Confirmed.** V0 checks schema plus declared level. V1 checks schema and
whole-file hash integrity but performs no cross-record joins. The real
ACTS-Attack stage01 blind validator
(`sp2027/analysis/contract_sound_stage01_validator_v2.py`) already enforces:

- `execution_trace.session_id == certificate.execution.session_id`
  (`execution-session-binding`);
- `task.base_instance_id == execution_trace.base_instance_id`
  (`task-session-binding`);
- evidence hash bindings, target-effect claim binding, boundary enforcement,
  and the identity/attribution claims.

Therefore the **unmodified B5 composition** (trace from session X, execution
certificate from session Y) is expected to be rejected by the real pipeline.
That is a concrete reason the "real evaluator impact" claim is not established
by HEB-1 as delivered.

The same inspection also shows what the real validator does **not** bind:

- the execution trace to the candidate/artifact: `execution_trace.json`
  contains no candidate hash, and `certificate.execution.trace_hash` is not
  re-checked against the trace file;
- the `agent_artifact.json` session to `certificate.execution.session_id`;
- `execution.executor_hash`, `environment_hash`, and `parser_hash` to
  any evidence;
- `target_effect.json` has no session field (its status is a
  candidate-derived predicate, not a per-session observation).

IAR-A targets these unbound references directly. If a real-pipeline bundle can
splice session X's trace with session Y's candidate and be accepted by both
the real blind validator and the real reference verifier, that is a
real-pipeline false-attribution result. If both reject it, the transfer fails
and is reported as a negative result. Neither outcome is assumed in advance.

### 2.2 Hash-chain validity is not authenticity; threat model was missing

**Confirmed.** The HEB-1 evidence bundles are unsigned JSON with sha256
linkage. The missing threat model is now explicit:

- **C0 - selection-only composer.** The composer may select among genuine
  records but cannot alter bytes. B5 is a C0 attack against validators that
  lack cross-record session joins (V0, V1, and any pipeline with the same
  gap).
- **C1 - metadata-rewriting composer.** The composer may rewrite unsigned
  public fields and recompute file hashes. No public-only, unauthenticated
  validator can then establish execution provenance. This is the
  RATS/in-toto boundary, not a new mechanism.
- **C2 - signature-forging composer.** Requires compromise of a signing key
  or trusted root; outside the current scope except where key custody is
  explicitly modelled.

V2's joins are computed only from public bytes; its mitigation is therefore
conditional on C0 and on the composer not rewriting session fields. IAR-B
implements an authenticated-provenance baseline and tests B5 and B5' (rewritten
metadata) against it. The expected honest result is that authentication
rejects the splice; if so, the novelty claim narrows to the empirical
measurement, not a new binding mechanism.

### 2.3 B5 proves false attribution more than false cryptographic success

**Confirmed.** In B5 the candidate satisfies the cryptographic predicate in
both runs; the hash chain is intact; the registry is internally consistent.
What is false is the attribution of success to the claimed execution session.
The finding statement is narrowed accordingly: **false attribution/promotion,
not false cryptographic success**. This is also the correct framing for the
real-pipeline transfer test.

### 2.4 Partial-claim acceptance was not measured

**Confirmed.** V2 is a full-attribution validator: it emits level 6 or
rejects. The C2/C5 rejects are not evidence-level false rejects under a
full-attribution request, but V2 cannot express partial support. IAR-C
measures, without modifying frozen V2:

- honest claims at levels 1–6;
- acceptance/rejection and emitted supported level at each requested level;
- overreach (emitted level > adjudicated level);
- false rejection of honest lower-level claims;
- agreement between stated and adjudicated supported level.

The earlier claim "zero false rejects" is retained only for B0 and C1 under
the full-attribution contract, and is explicitly not generalized.

## 3. Prior-art record update

The following works were missing from the pre-review five-element filter and
are now part of the closest-prior-art record:

| Work | Relevant principle |
|---|---|
| RFC 9334 (RATS Architecture) | Evidence must be bound to the intended attester/environment; a relying party must not accept evidence from a different context. |
| in-toto | Attestations bind each step to its materials, products, and functionary; verification follows the supply-chain layout. |
| `evidence.*` family (IETF Internet-Draft) | Session-bound, hash-chained, signed records for agent actions, independently verifiable; draft, not a final standard. |
| TRAP / ReplayBench | Reuse of valid execution results in an incorrect context; context-binding checks are the defence. |

Revised conclusion: the cross-record binding principle is anticipated. The
five-element combination does not establish mechanism novelty. The remaining
candidate contribution is the controlled empirical measurement of
false-attribution promotion in AI-authored cryptographic-exploitation
evaluation. Whether even that delta is novel is **not established** until
IAR-A/B/C are executed and compared against these works.

## 4. Independent adversarial replication (IAR) protocol

### Common rules

- Offline only; zero model/provider calls; zero marginal spend.
- No modification of `RESULTS_LOCK.json`, `RESULTS_LOCK_H1PC.json`,
  `paper/main.tex`, `paper/main.pdf`, the frozen HEB-1 components, or the
  stage01 campaign artifacts. New inputs live under
  `sp2027/analysis/heb1_crossboundary_20261019/iar/`.
- No reopening or rerunning of H1, R0/R1, or P010.
- One recorded pass per experiment; no retuning after observing results.
- All outcomes preserved, including validator errors and negative transfers.
- "Independent" means structurally independent: separate generator, spec-first
  construction, no imports from V2/adjudicator/fixtures. It is **not** a
  second human researcher or a separately authorized model; that limitation
  is disclosed in every IAR result.

### IAR-A - transfer to the actual stage01 pipeline

**A0. Read-only baseline.** Run the real blind validator and reference
verifier on an unmodified clean stage01 case; record ACCEPT/ACCEPTED and
hashes.

**A1. Trace-to-candidate splice.** Define two ground-truth runs for the same
task: X (trace/session X, artifact X) and Y (valid candidate/artifact Y). Build
a public stage01-format certificate that uses X's `execution_trace` evidence
record and execution session X, while the certificate's `agent_artifact`
pointer/`sha256`, the submitted candidate, and the `target_effect` belong to Y
(see `iar/iar_a_20261019/IAR_A_CONSTRUCTION_AND_GUARANTEES.md` §1–§2);
update every file hash; invoke the real blind validator (stdin) and the real
reference verifier (bundle JSON). Record both verdicts and all
`certificate_errors`.

- Both accept -> real-pipeline false attribution demonstrated; identify the
  exact unbound reference (trace has no candidate hash) and the minimal
  binding fix.
- Either rejects -> document the catching check; transfer failed.

**A2. Binding-coverage matrix.** Vary one unbound reference at a time
(`agent_artifact.session_id`, `execution.trace_hash`, `executor_hash`,
`environment_hash`, `parser_hash`) and record which variations change a
verdict. Only verdict-changing compositions count as evidence.

**A3. Metadata-rewriting composer (C1).** Rewrite the trace session to match
the claimed execution session and re-hash. The unsigned pipeline cannot
distinguish this; record it as the authenticity boundary and hand the case to
IAR-B.

**A4. Reference-verifier independence.** Confirm the reference verifier
recomputes the crypto predicate and certificate integrity, and record that it
does not consult a per-session run registry. This determines whether it can
catch a semantically false but internally consistent certificate.

### IAR-B - authenticated-provenance baseline V3

Specification, written before implementation:

- Each run has an offline Ed25519 key. The signed record binds
  `session_id`, `task.base_instance_id`, `candidate_sha256`, `condition_id`,
  `effect_status`, and `boundary_enforced`.
- A registry anchors each run's public key and signed record, following the
  RATS evidence/environment binding and in-toto step/functionary binding
  principles.
- The certificate carries the signatures; the verifier checks signatures,
  registry anchors, all session/instance/condition/candidate joins, and the
  recomputed crypto predicate.
- Variants: **V3-sig** (signatures only) and **V3-full** (signatures plus
  joins).

Test set: B0, B1–B5, C1–C5, plus B5' (rewritten metadata). Expected:
V3-sig rejects B5' by signature mismatch; V3-full rejects all mixed
compositions and accepts B0/C1. If B5 or B5' evades V3-full, that is a
candidate new finding and the exact gap must be stated. If not, the
novel-mechanism claim is NO-GO.

### IAR-C - independent generation and partial-claim acceptance

- New generator written from the protocol and the prior-art principles; it
  does not import the frozen fixtures, adjudicator, or V2.
- Cases include coherent runs, success/failure combinations, compositions,
  and honest claims at levels 1–6.
- Metrics: false-attribution promotion at each requested level; emitted-level
  overreach; false rejection of honest lower-level claims; stated-vs-
  adjudicated level agreement; per-mechanism counts.
- Opaque ids; labels isolated; single pass; no retuning.
- The generator's truth model is its own, not the frozen adjudicator's; any
  disagreement between the two must be investigated and reported rather than
  silently resolved.

## 5. Decision rule

1. **Real impact:** demonstrated only if IAR-A produces a false splice
   accepted by both the actual blind validator and the actual reference
   verifier, with a verdict effect.
2. **Novel mechanism:** demonstrated only if IAR-B's faithful, principled
   authenticated baseline is fooled by a composition not covered by
   RATS/in-toto-style binding, or if IAR-A exposes a gap that those principles
   do not close. A real-pipeline defect that is already covered by the known
   principle is impact evidence, not mechanism novelty.
3. **If IAR-A rejects the splice and IAR-B rejects B5/B5':** conclusion
   remains **novelty not established**; HEB-1 is retained as a bounded
   empirical demonstration of false-attribution promotion under missing
   provenance binding, with the reviewer's decision as the authoritative
   adjudication.
4. **No overgeneralization:** no claim about deployed evaluators, open-world
   coverage, or a universal mitigation. All results remain scoped to the
   tested formats and threat model.

## 6. Implementation availability and shared-assumption risk

The frozen implementations are available for independent checking:

- `build/heb1_adjudicator.py` (sha256 `be77b017...e2a3fc6`)
- `build/heb1_v0_schema_reference.py` (sha256 `74ae7c74...d7533faf`)
- `build/heb1_v1_hash_integrity.py` (sha256 `9e73e83c...3c3ebef3`)
- `build/heb1_v2_claim_binding.py` (sha256 `3585f876...55194c53d`)
- `build/heb1_common.py`, `build/heb1_fixtures.py`, `build/heb1_crypto_lib.py`
- `freeze/HEB1_CONFIG_FREEZE.json`, `freeze/HEB1_VALIDATOR_FREEZE.json`

The adjudicator and V2 share an author. That is a shared-assumption risk: V2's
joins were designed alongside the adjudicator's joins. IAR-C's separate truth
model is the intended control; it does not eliminate the risk, and the report
must say so. The frozen result is not evidence that an independent researcher
would have designed the same joins.

## 7. Status of artifacts

- `HEB1_EVALUATION_REPORT.md`: adjudication addendum added; §5 novelty sentence
  marked superseded.
- `heldout/heldout_results.json`: unchanged (sha256 `4bda7b8f...1f7265`).
- No H1/R0/R1/P010 artifacts touched; protected locks unchanged.
- IAR design frozen in this document; execution begins with A0/A1.
- No commit made.
