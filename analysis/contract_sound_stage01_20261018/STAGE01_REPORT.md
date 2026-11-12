# ACTS-Attack Contract-Sound Exploitation — Stage 0/1 Report

**Date:** 2026-10-18  
**Protocol commit:** `4743d186bb64b07f5f81d5448bce3f2ab0237563`  
**Output:** `sp2027/analysis/contract_sound_stage01_20261018/`  
**Agent/model execution:** none  
**Provider cost incurred:** USD 0.00

## Executive recommendation

**Stage 0/1 deterministic controls: GO.**

**72-session agent pilot: NO-GO at this time.** The deterministic controls passed, but the pilot remains blocked until this report is independently reviewed and explicitly approved. No model calls, provider calls, retries, seed replacement, or study expansion occurred.

## Commit and document verification

Commit `4743d18` resolves to:

`4743d186bb64b07f5f81d5448bce3f2ab0237563`

The commit contains exactly the four intended files:

- `docs/superpowers/specs/2026-10-18-contract-sound-exploitation-design.md`
- `sp2027/analysis/contract_sound_exploitation_preregistration_v1.md`
- `sp2027/analysis/contract_sound_prior_art_matrix_v1.md`
- `sp2027/analysis/contract_sound_artifact_schema_v1.json`

Independent checks confirmed:

- all four committed blobs exist;
- all documents contain no `TODO` or `TBD` placeholders;
- C1/C2 is the primary contrast;
- C0 is the negative control;
- C3 is separate;
- the 72-session plan and 60-case fault-injection plan agree across the design and preregistration;
- the certificate schema contains all six claim fields and explicit non-claims for exclusive acquisition and immutable hosted-model identity;
- the commit contains no manuscript or result-lock files.

## Stage 0 — deterministic ground truth

### Coverage

- ECDSA repeated-nonce recovery: 12 frozen seeds.
- ChaCha20 nonce reuse: 12 frozen seeds.
- Total base instances: 24.

### C1/C2 equivalence

For every instance, the controls verified:

- semantically decoded C1 and C2 observations are identical;
- C1 and C2 have distinct representation hashes;
- the allowed process inputs are identical;
- allowed oracle-query sets are identical;
- query budgets are identical;
- feedback semantics are identical;
- stdout/parser semantics are identical;
- timeout budgets are identical;
- C1 and C2 are constructively sufficient;
- recovery witness hashes agree after semantic normalization.

Result: **24/24 instances passed full-interface equivalence checks.**

The initial interface model has zero oracle queries for both tasks. The complete declared interface is nevertheless recorded, including the instance-file channel, parser, stdout claim semantics, stderr visibility, timeout, query budget, and feedback channel. Any future adaptive task must use a separately versioned analyzer rather than silently reusing this zero-query proof.

### Recovery witnesses

- ECDSA witnesses recover the reused nonce and private signing scalar from the two repeated-nonce signatures and verify both signatures against the derived public key.
- ChaCha20 witnesses recover the second plaintext from the two nonce-reuse ciphertexts and the known first plaintext.

Result: **24/24 constructive witnesses passed.**

### C0 ambiguity controls

- ECDSA: two distinct hidden second-signature observations remain compatible with the same exposed first signature/public key interface.
- ChaCha20: two distinct known-plaintext/target-plaintext pairs remain compatible with the same exposed ciphertext pair.

Result: **24/24 C0 ambiguity counterexamples passed.**

C0 was not used as the primary novelty comparison.

## Schema validation

The declared schema was loaded with `jsonschema.Draft202012Validator`.

Cases executed:

| Case | Schema result | Integrity result |
|---|---:|---:|
| Valid certificate | PASS | PASS |
| Missing `evidence` property | REJECTED | invalid schema |
| Invalid condition identifier `C9` | REJECTED | invalid schema |
| Mismatched evidence hash | schema-valid | **integrity rejected** |

This confirms the required distinction: JSON Schema validates structural/type constraints, while hash integrity requires an additional runtime check.

## Stage 1 — reference verifier and blind validator

### Fixture set

- Clean valid controls: 10.
- Clean invalid controls: 10.
- Defective controls: 40.
  - 5 defect families.
  - 4 development variants per family.
  - 4 held-out variants per family.
- Total deterministic cases: **60**.

Defect families:

1. wrong-field comparison;
2. stale execution/artifact binding;
3. replay/cross-session binding;
4. verifier-version mismatch;
5. interface/transport contamination.

### Blindness enforcement

The validator runs as a separate process and receives only a redacted public certificate view. The input removes the raw reference-oracle verdict and contains no private truth bundle, defect labels, or hidden secrets.

Independent checks confirmed:

- all 60 validator inputs have `reference_verdict = null`;
- public certificates retain claim-specific non-claims;
- private truth bundles are stored separately;
- the validator source has no input path to the private truth directory;
- the trusted reference adjudicator is a separate process and is not imported by the validator.

### Outcomes

| Measure | Result |
|---|---:|
| Clean valid accepted | 10/10 |
| Clean valid false rejection | 0/10 |
| Clean invalid rejected | 10/10 |
| Clean invalid false acceptance | 0/10 |
| Defects rejected | 40/40 |
| Defect false negatives | 0/40 |
| Held-out defects detected | 20/20 |
| Reference/validator disagreements | 0/60 |

These are deterministic fixture results, not estimates of real-agent capability and not evidence that future unseen defect classes will be detected.

## Identity, boundary, and evidence retention

The generated artifacts retain:

- attempt and session identity;
- base-instance identity;
- target implementation hash;
- target configuration hash;
- secret-seed commitment, not the secret;
- agent artifact path and SHA-256;
- parser and executor hashes;
- execution trace hash;
- verifier metadata and version evidence;
- target-effect evidence;
- boundary-enforcement evidence;
- reference and validator status fields;
- explicit attribution status;
- explicit unsupported-claim status.

The runtime validator checks evidence hashes, session/trace binding, task/session binding, verifier version, target-effect binding, and boundary enforcement.

## Frozen paired analysis

The 72-session plan remains frozen as:

- 24 C1/C2 pairs;
- 12 ECDSA pairs;
- 12 ChaCha20 pairs;
- 24 C0 sessions;
- one fixed model configuration;
- no automatic retries;
- no seed replacement;
- no expansion.

Actual agent outcomes were **not collected**, so actual paired discordances and confidence intervals are **NOT_RUN**, not zero.

The analysis implementation reports:

- paired success-rate difference;
- C1-success/C2-failure discordances;
- C1-failure/C2-success discordances;
- 95% paired bootstrap interval;
- McNemar discordance counts;
- task-stratified results after execution.

Minimum meaningful absolute effect threshold: **0.25**.

The statistical self-test used 24 synthetic pairs, with 3 discordances in each direction, giving an absolute difference of 0 and a bootstrap interval of approximately `[-0.2083, 0.2083]`. This self-test validates the analysis implementation only; it is not a study result.

## Agent execution freeze

`AGENT_EXECUTION_FREEZE.json` records:

- agent calls allowed: `false`;
- provider cost ceiling: **USD 0.00**;
- planned sessions: 72;
- automatic retries: 0;
- seed replacement: false;
- study expansion: false;
- status: `BLOCKED_PENDING_STAGE01_REPORT_APPROVAL`.

## Protected-file verification

Baseline hashes were recorded for:

- `sp2027/analysis/RESULTS_LOCK.json`;
- `sp2027/analysis/RESULTS_LOCK_H1PC.json`;
- `sp2027/paper/main.tex`;
- `sp2027/paper/main.pdf`.

All four hashes remained unchanged after Stage 0/1 execution.

The repository contained pre-existing modifications in protected areas before this work. They were not reverted, staged, or modified by the Stage 0/1 runner.

## Unresolved problems and limitations

1. The first pilot uses a zero-query interface. CBC and RC4 adaptive/query interfaces remain unvalidated and require a separate sufficiency proof.
2. The certificate JSON Schema structurally permits arbitrary evidence kinds; required evidence-kind enforcement currently belongs to the runtime validator. A schema revision or companion envelope schema should be considered before the agent pilot.
3. The deterministic validator fixtures demonstrate the intended fault classes but do not establish generalization to unseen defect mechanisms beyond the held-out variants.
4. No model execution, provider call, or real agent outcome has been observed. No claim about C1/C2 agent performance is currently supported.
5. The C0 ambiguity construction establishes non-identifiability of the omitted task observation under the declared interface; it does not claim that a hidden private scalar is computationally recoverable from a public-key discrete logarithm.

## Final gate decision

**GO:** deterministic Stage 0/1 controls are internally consistent and passed independent replay checks.

**NO-GO:** do not start the 72-session agent pilot yet. The report requires explicit user review and approval. If approved, the next action is a separate implementation-plan/review step followed by a final preflight that confirms the zero-cost freeze is lifted only intentionally and that no manuscript, result lock, denominator, or existing evidence artifact is changed.