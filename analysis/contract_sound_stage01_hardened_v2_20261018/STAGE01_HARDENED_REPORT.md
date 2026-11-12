# ACTS-Attack Contract-Sound Exploitation — Hardened Stage 0/1 Report

**Date:** 2026-10-18  
**Protocol commit:** `4743d186bb64b07f5f81d5448bce3f2ab0237563`  
**Hardened output:** `sp2027/analysis/contract_sound_stage01_hardened_v2_20261018/`  
**Agent/provider execution:** none  
**Provider cost:** USD 0.00  
**Pilot decision:** **NO-GO — the 72-session agent pilot remains blocked pending explicit user approval.**

## Executive result

The targeted hardening pass replaced the previous label-reading reference verifier with an independent adjudicator that recomputes the cryptographic predicate from private target state and candidate bytes, then independently checks certificate evidence bindings. Stored labels are isolated from both the adjudicator input and the blind validator input.

The deterministic controls pass as an implementation milestone:

| Control | Result |
|---|---:|
| Independent Stage 0 zero-query instances | 24/24 |
| ECDSA C1/C2 full-interface equivalence | 12/12 |
| ChaCha20 C1/C2 full-interface equivalence | 12/12 |
| C0 ambiguity counterexamples | 24/24 |
| Clean valid controls | 10/10 accepted |
| Clean invalid controls | 10/10 rejected |
| Development defects | 20/20 rejected |
| Held-out defects | 20/20 rejected |
| Independent reference vs blind validator disagreement | 0/60 |
| Deliberately mislabeled fixture disagreements | 2/2 detected |
| Public-input forbidden-field cases | 0/60 |
| Protected manuscript/result-lock hashes changed | 0 |
| Model/provider/network calls | 0 |

These results establish deterministic infrastructure correctness under the declared fixture families. They do **not** establish representation sensitivity, agent capability, or generalization to unseen evaluator defects.

## 1. Commit and protocol-document verification

`git rev-parse 4743d18` resolved to the required full commit:

`4743d186bb64b07f5f81d5448bce3f2ab0237563`

The commit contains exactly the four approved documents:

- `docs/superpowers/specs/2026-10-18-contract-sound-exploitation-design.md`
- `sp2027/analysis/contract_sound_artifact_schema_v1.json`
- `sp2027/analysis/contract_sound_exploitation_preregistration_v1.md`
- `sp2027/analysis/contract_sound_prior_art_matrix_v1.md`

The hardening implementation is isolated in new uncommitted files and a new output directory. The committed protocol documents, manuscript, and prior Stage 0/1 output were not overwritten.

## 2. Independent reference adjudication

### Previous defect

The prior reference process returned a stored `expected_reference_verdict`. That established label agreement only and was not independent cryptographic adjudication.

### Hardened implementation

`contract_sound_stage01_reference_verifier_v2.py` now receives a bundle containing only:

- `target_state_path`;
- `candidate_path`;
- `certificate_path`;
- a case identifier.

The bundle contains no expected verdict, defect label, or stored truth label. The reference process:

1. recomputes ECDSA nonce-reuse validity from the public key, two signatures, and candidate `d/k`;
2. recomputes ChaCha20 nonce-reuse recovery as `C1 XOR C2 XOR P1 == P2`;
3. independently checks evidence hashes, session/base-instance bindings, verifier version, target-effect binding, boundary enforcement, and candidate artifact hash;
4. returns `ACCEPTED` only when both the cryptographic predicate and certificate-integrity predicate pass.

The reference source audit found no expected-label lookup, private-truth directory access, or blind-validator import.

### Mislabeled-fixture test

Two label files were deliberately flipped:

- `clean-01`;
- `wrong_field-01`.

The reference verifier does not receive these label paths. It recomputed its result and disagreed with both stored labels, proving that it does not copy the label field. The observed result was **2/2 deliberate label mismatches detected**.

The authoritative Stage 1 ground truth is therefore the recomputed reference result, not the stored fixture label.

## 3. Stage 0: independent full-interface equivalence

Scope is deliberately limited to the declared zero-query contracts for:

- ECDSA repeated-nonce recovery;
- ChaCha20 nonce reuse.

CBC padding-oracle and RC4 adaptive-query claims are not made.

For each of 12 seeds per task, the hardening runner independently decoded C1 and C2 rather than calling the original decoder and checked:

- semantic observation equality;
- distinct representation versus equal semantic hashes;
- equal provision/process input semantics;
- equal allowed oracle-query sets;
- equal query budgets, including byte/time budgets;
- equal feedback semantics, including no stderr channel and single-claim stdout parsing;
- equal timeout behavior;
- constructive witness retention;
- two distinct C0 ambiguity counterexamples.

Result: **24/24 independent checks passed**. The generated records retain the witness and ambiguity objects in `stage0/` and `stage0_summary.json`.

This is a deterministic contract result. It is not evidence that an agent performs equally under C1 and C2.

## 4. Schema and runtime validation

All generated full certificate instances were validated against the committed Draft 2020-12 schema. Additional negative cases were executed:

| Case | JSON Schema | Runtime integrity |
|---|---:|---:|
| Valid certificate | accepted | accepted |
| Missing mandatory `evidence` | rejected | rejected |
| Invalid condition identifier `C9` | rejected | rejected by schema |
| Mismatched evidence hash | schema-valid | rejected |
| Invalid verifier-version binding | schema-valid | rejected |
| Missing mandatory boundary evidence kind | schema-valid | rejected |
| Stale execution/session binding | schema-valid | rejected |

This preserves the required distinction between structural schema validation and semantic/runtime integrity validation.

## 5. Blind-validator boundary

The blind validator is `contract_sound_stage01_validator_v2.py`. It receives only the public certificate view and public evidence paths. The public view removes `raw_verdict`, `reference_verdict`, and `validator_verdict`; it also normalizes the reference-oracle claim to `NOT_ESTABLISHED` so the validator cannot consume a trusted oracle answer.

The validator source does not reference private target-state paths or reference-input bundles. A data-flow audit found:

- forbidden verdict/truth fields in public inputs: **0/60**;
- private target state supplied to validator: **0 cases**;
- defect labels supplied to validator: **0 cases**;
- stored expected labels supplied to validator: **0 cases**;
- trusted reference verdict supplied to validator: **0 cases**.

Claims remain untrusted declarations. The validator checks their consistency with retained public evidence and bindings; it does not treat them as cryptographic ground truth.

## 6. Fault-injection evaluation

The deterministic fixture set contains:

- 10 clean valid cases;
- 10 clean invalid candidate cases;
- 5 defect families;
- 4 development variants per family;
- 4 held-out variants per family;
- 60 total cases.

Defect families:

1. wrong-field comparison;
2. stale artifact/run binding;
3. replay/cross-session binding;
4. verifier-version mismatch;
5. interface/transport contamination.

The validator was hashed and frozen after development fixtures and before held-out generation. The recorded freeze check is in `controls/HELDOUT_FREEZE_CHECK.json`; the validator SHA-256 was unchanged before and after held-out evaluation.

| Measure | Result |
|---|---:|
| Clean valid accepted | 10/10 |
| Clean invalid rejected | 10/10 |
| All development defects rejected | 20/20 |
| All held-out defects rejected | 20/20 |
| Reference/validator disagreements | 0/60 |
| Public forbidden-field cases | 0/60 |

Per-family totals were 8/8 rejected for every family, with held-out performance 4/4 per family. These are held-out variants within the predeclared defect families, not unseen defect mechanisms. The report therefore does not claim open-world generalization.

Validation overhead measured by subprocess wall time over the 60 cases:

- independent reference adjudicator mean: approximately **89.34 ms**;
- blind validator mean: approximately **40.87 ms**.

## 7. Frozen paired statistical analysis

No agent data were collected. Actual C1/C2 paired discordances and confidence intervals are therefore **NOT_RUN**, not zero.

The frozen analysis self-test used 24 synthetic pairs only to validate the implementation:

- C1 rate: 0.75;
- C2 rate: 0.75;
- C1-success/C2-failure discordances: 6;
- C1-failure/C2-success discordances: 6;
- absolute difference: 0.00;
- 95% paired bootstrap interval: approximately `[-0.2917, 0.2917]`;
- minimum meaningful absolute effect threshold: **0.25**.

The self-test is not a capability estimate and must not be presented as an agent result.

## 8. Certificate claims and retained evidence

The hardened artifacts retain separate fields for:

- artifact authorship;
- execution identity;
- target effect;
- reference-oracle acceptance;
- boundary enforcement;
- attribution;
- explicit non-claims for exclusive acquisition and immutable hosted-model identity.

Each generated case retains run/session identity, base-instance identity, candidate hash, evidence hashes, verifier version, execution trace, target effect, and boundary evidence. The private reference bundle retains target state and candidate paths for adjudication but is not passed to the blind validator.

Hashes establish byte and binding integrity under the declared trust model. They do not establish exclusive acquisition, private reasoning, absence of an unrecorded information channel, or immutable hosted-model identity.

## 9. Trust-boundary diagram

See `STAGE01_HARDENED_DATA_FLOW.md` in this directory. The essential separation is:

```mermaid
flowchart LR
    T[Private target state] --> R[Independent reference adjudicator]
    C[Candidate artifact] --> R
    F[Private certificate + evidence] --> R
    L[Stored fixture label] -. not supplied .-> R
    R --> RV[Recomputed reference verdict]

    P[Public certificate view] --> V[Blind validator]
    E[Public evidence files] --> V
    S[Hidden target state] -. inaccessible/not supplied .-> V
    L -. inaccessible/not supplied .-> V
    RV -. inaccessible/not supplied .-> V
    V --> VD[Evidence-consistency decision]

    RV --> M[Stage 1 metric comparison]
    VD --> M
```

## 10. Protected files and execution freeze

Before/after hashes were identical for:

- `sp2027/analysis/RESULTS_LOCK.json` — `4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39`;
- `sp2027/analysis/RESULTS_LOCK_H1PC.json` — `8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103`;
- `sp2027/paper/main.tex` — `51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461`;
- `sp2027/paper/main.pdf` — `fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a`.

The new execution freeze records:

- `agent_calls_allowed: false`;
- `provider_cost_ceiling_usd: 0.00`;
- `provider_calls_observed: 0`;
- `network_calls_observed: 0`;
- automatic retries: 0;
- seed replacement: false;
- study expansion: false;
- planned sessions: 72;
- status: `BLOCKED_PENDING_USER_APPROVAL`.

## 11. Unresolved problems and limitations

1. The independent reference verifier is now computationally independent of stored labels, but it remains a trusted local adjudicator under its declared implementation and private-target-state assumptions.
2. Held-out defects are new variants within known families, not open-world unseen defect classes.
3. Stage 0 covers only zero-query ECDSA and ChaCha20 contracts. No sufficiency conclusion is made for CBC or RC4 adaptive interfaces.
4. No model execution occurred. There is no evidence yet for C1/C2 representation sensitivity or a novelty-producing agent effect.
5. The current deterministic controls validate infrastructure and contract soundness; they do not justify changing the manuscript or existing result locks.

## Final gate decision

**GO:** Stage 0/1 deterministic hardening is complete and the independent reference/validator controls pass the declared bounded tests.

**NO-GO:** Do not run the 72-session agent pilot yet. Explicit user review and approval remain required. If approved later, perform one final preflight against the frozen protocol and cost ceiling, then run exactly the preregistered sessions with no retries, seed replacement, or study expansion.

**Promotion status:** No result is promoted into ACTS-Attack, and no manuscript or existing evidence lock is modified.