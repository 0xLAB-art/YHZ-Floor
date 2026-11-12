# HEB-1 Experiment Protocol — Cross-Boundary Verdict Promotion (offline, frozen)

**Date:** 2026-10-19
**Directory:** `sp2027/analysis/heb1_crossboundary_20261019/`
**Status:** Protocol v1 — design freeze. Code+config freeze manifests produced after the development validation pass, before held-out generation.
**Constraints:** offline; no model/provider calls; no network; no manuscript/result-lock changes; separate versioned artifact; preserve all outcomes.

---

## 1. Question

Does cross-boundary composition of evaluation evidence — without candidate/run/condition/target/claim identity enforcement at every join — promote weaker cross-boundary verdicts into falsely attributed "verified exploit completion" claims? And does a claim-specific binding validator prevent this where schema+reference and hash-only baselines do not?

## 2. Fixture domain and composition conditions

Two cryptographic primitives (both offline, deterministic, pure Python):
- **ECDSA nonce reuse** — two signatures sharing nonce `k`; the exploit recovers `k` and the private key `d`. Recomputable predicate (native ECDSA math on secp256k1).
- **ChaCha20 keystream reuse** — `c1 ^ c2 ^ p1 == p2` structure; the exploit recovers `plaintext_2`.

Each case has: `request.json` (declared claim provenance: run_id, condition_id, base_instance_id, target hash set, `claim_level: attribution`), `candidate.json` (the artifact under evaluation), a bundle of public certificate + evidence files, and a private area (run registry, target states, composition ground truth).

**Conditions:**
- **B0 coherent** (8 = 4+4) — all joins coherent; candidate crypto-correct; evidence classes complete; strong claim supported.
- **B1 cross-run join** (8) — candidate from run A (faulty); bundle = run B's records with `agent_artifact` re-pointed to A's candidate (hash recomputed); request binds run A. Violated joins: J1 (`trace.candidate_sha256 ≠ hash(candidate)`), J6 (request session vs bundle session).
- **B2 cross-condition join** (8) — candidate bytes identical and valid; bundle records from a run under condition C1; request claims C0. Violated: J4 (condition binding). Crypto passes — detection is binding-only.
- **B3 stale target/instance** (8) — request binds newer target/base instance; bundle from older run/instance. Violated: J3/J5 (instance/target staleness).
- **B4 claim-strength escalation** (8 = 4 B4a + 4 B4b) — B4a: bundle lacks `execution_trace`, no artifact binding, but certificate declares `attribution: PROVEN`; B4b: effect record `NOT_OBSERVED` while certificate claims `OBSERVED`. Violated: claim ladder (supported < requested).

**Controls (5 types, 14 cases = 4+4+2+2+2):**
1. valid+valid → expect accept (true-accept test).
2. invalid+rejected → all reject.
3. valid+malformed certificate → reject.
4. valid+stale/mismatched run id (single run, packaging defect) → V2 reject.
5. reference-acceptance-without-attribution → strong claim must not be emitted.

## 3. Claim ladder (6 classes, ordered)

1. `artifact_authorship` — authorship record binds candidate.
2. `execution_identity` — trace binds executed artifact to a session/executor.
3. `target_effect` — effect record bound to same execution.
4. `reference_oracle_acceptance` — reference acceptance bound to same artifact/session.
5. `boundary_enforcement` — boundary record enforced.
6. `attribution` — composite; the requested strong claim.

## 4. Systems under test (blind public inputs only)

Inputs to all validators: `request.json`, public certificate, candidate file, public evidence files. No private truth, no labels, no reference output.

- **V0 — schema + reference:** schema-valid + declared `claims.reference_oracle_acceptance` / `attribution` accepted → emit declared level.
- **V1 — hash integrity:** structural checks + all evidence hashes match files + candidate hash ↔ `agent_artifact.sha256` → emit `min(requested, declared)`. No identity/condition/target/claim-level joins.
- **V2 — claim-specific binding:** V1 hash checks plus joins:
  - J1 `trace.candidate_sha256 == sha256(candidate)`
  - J2 `trace.session_id == cert.execution.session_id == effect.session_id`
  - J3 `trace.base_instance_id == cert.task.base_instance_id == request.base_instance_id`
  - J4 condition binding: `request.condition_id == cert.condition.id == trace.condition_id`
  - J5 target binding: request target hashes == cert.target hashes
  - J6 `request.run_id == cert.execution.session_id`
  - J7 reference-acceptance artifact/session binding (when claimed)
  - J8 boundary enforced (when claimed)
  - Ladder: supported level < requested → REJECT `claim-overreach`; else emit strong claim.

## 5. Independent adjudication

`build/heb1_adjudicator.py` — inputs: private run registry, private target states, candidate, full certificate, request. **Never reads labels.** Own secp256k1 code path (independent of validator code). Output: truth = strong claim supported iff (a) bundle joins coherent, (b) crypto recomputed true on (target state, candidate), (c) claimed level ≤ supported level. Registry cross-check recorded.

## 6. Metrics

- **Primary:** false-promotion rate per system per condition on B1–B4 (system emits strong claim while truth = unsupported).
- **Secondary:** any-positive false acceptance; true-accept on B0 / control-1; false-reject; per-mechanism breakdown; validator–adjudicator agreement; overhead ms.
- Reporting: per condition × primitive; labeled totals; no unjustified pooling.

## 7. Frozen decision gates

- **N1 (mechanism exhibited):** `max(FP(V0), FP(V1))` on B1–B4 dev ≥ 0.5 (expected ≈ 1.0). Else documented NO-GO.
- **N2 (mitigation valid):** `FP(V2) ≤ 0.10` on B1–B4 dev AND V2 true-accept ≥ 7/8 on B0 AND control-1 = 4/4. Else mitigation invalid.
- **N3 (held-out, single pass):** V0/V1 FP ≥ 0.5 and V2 FP ≤ 0.15 on held-out defect suites. Failure → bounded result, reported honestly.
- **N4:** any failed gate is reported as a negative/partial finding; no retuning after the single pass.

## 8. Held-out protocol

1. Run and validate dev pass.
2. Freeze: sha256 of V0/V1/V2 + config → `freeze/HEB1_CONFIG_FREEZE.json`, `freeze/HEB1_VALIDATOR_FREEZE.json`.
3. Write `heldout/heb1_heldout_gen.py` with ≥ 1 composition pattern unused in V2 development (planned: split-half composition — trace from run X, effect/acceptance from run Y; detection J2), opaque public case ids (no mechanism names).
4. Generate ≥ 6 cases per new pattern + ≥ 6 per dev family + ≥ 4 controls.
5. Single evaluation pass, no retuning; freeze results to `heldout/heldout_results.json`.

## 9. Historical motivators (labeled; outside the blind evaluation; motivation only)

- wrong-field comparison (hardened-v2 `wrong_field` family; wrong-field audit findings).
- label-reading reference-verifier (mislabeled-fixture detection requirement; 2/2 detected).
- stale binding/order defects (`stale_binding`; deterministic gate ordering).
- source-policy/contract mismatch (`interface_contamination`; contract/representation mismatch).

Explicitly **not** part of the blind evaluation denominator; no relabeling of H1/R0/R1/P010; no reuse of their numbers as HEB-1 evidence.

## 10. Safeguards and audit

- Protected hashes before/after the pass (RESULTS_LOCK.json, RESULTS_LOCK_H1PC.json, main.tex, main.pdf).
- No network; stdlib (+ jsonschema) only; run manifest records model_calls = 0, provider_calls = 0.
- Forbidden-field audit on all validator inputs; private-path audit (no `private/` path in any public input).
- 2 deliberate label flips in dev to verify label isolation machinery.
- All outcomes preserved; anomalies logged; no case dropped.

## 11. Non-goals / anti-overclaim

Synthetic controlled fixtures only; success = mechanism exhibited + bounded mitigation (not perfect detection); strong negative acceptable; self-designed-fault detection alone is not novelty; external validity limited and stated in the report.
