# ACTS-Attack — 72-Session Experimental Design Validity Audit

**Date:** 2026-10-18  
**Status:** Design audit — existing 72-session outcomes are preserved; no manuscript or result lock modified; no new provider calls made during this audit.

## Executive conclusion

The replacement campaign is **execution-valid but not sufficient to identify the intended representation-sensitivity question**. The recorded 24/24 C1, 22/24 C2, and 0/24 C0 outcomes are real terminal states of the repaired harness, but they do not justify treating the experiment as a clean causal test of cryptographic representation sensitivity.

The key distinction is:

- **Execution validity:** provider responses, candidate extraction, sandbox qualification, reference adjudication, and evidence validation completed as recorded.
- **Design validity:** the intervention, estimand, controls, model randomness, task difficulty, and schedule must isolate the scientific question. This condition is not yet met.

The current campaign should therefore remain a retained **diagnostic execution record**, not a definitive test that representation does or does not affect AI cryptographic exploit construction.

## 1. Reconstructed intervention

The actual replacement runner is `sp2027/analysis/run_contract_sound_agent_replacement_v1.py`.

For C1 and C2 it uses:

- the same task family;
- the same fixture seed and hidden target state;
- the same executor, parser, timeout, and maximum output token budget;
- zero oracle queries and no feedback channel;
- different public encodings;
- an explicit prompt field naming the condition (`Condition: C1` versus `Condition: C2`).

The task generator creates:

- ECDSA: `json-hex-v1` versus `base64-packed-v1`;
- ChaCha20: `json-hex-v1` versus `base64-packed-v1`.

Independent decoding confirms semantic equality for the declared zero-query interface. That establishes mathematical equivalence of the observations, but not equality of the agent-facing task or cognitive burden.

## 2. Confirmed design blockers

### Blocker D1 — The intervention is not representation-only

The prompt is not identical across C1 and C2. It contains both the condition label and a different serialized payload. Direct inspection for seed 1 showed:

| Family | C1 prompt length | C2 prompt length | Prompt equal? |
|---|---:|---:|---|
| ECDSA | 1150 bytes | 995 bytes | No |
| ChaCha20 | 864 bytes | 773 bytes | No |

The prompt explicitly says `Condition: C1` or `Condition: C2`. Therefore a result difference could arise from:

1. the representation itself;
2. the condition label;
3. tokenization/length differences;
4. base64-versus-hex parsing burden;
5. model strategy changes induced by the label.

The current experiment cannot identify which component caused a failure.

**Status:** unresolved causal confounding; primary blocker.

### Blocker D2 — Base64 versus hex is an encoding-complexity intervention

The alternative representation changes the serialization alphabet, decoding operation, byte-to-integer conversion burden, and prompt length. This is a legitimate intervention if the research question is “does this encoding contract affect end-to-end completion?”, but it is not a neutral representation intervention.

The paper cannot call the result a pure semantic-representation effect without an additional control separating:

- semantic serialization;
- encoding/decoding complexity;
- prompt length/tokenization;
- explicit condition labeling.

**Status:** construct-validity blocker.

### Blocker D3 — Ceiling effects make the tasks weak probes

Observed outcomes:

- ECDSA C1: 12/12.
- ECDSA C2: 10/12, with both failures occurring before cryptographic adjudication because of an unused forbidden `hashlib` import.
- ChaCha20 C1: 12/12.
- ChaCha20 C2: 12/12.

ChaCha20 provides no observable variation at all. ECDSA provides only two pre-execution contract failures and no cryptographic failures. The two primitives are short, well-known algebraic exercises with explicit output shapes and no adaptive interaction.

This creates a ceiling effect: the task set is too easy to expose a meaningful reasoning-level representation effect. A null contrast under these conditions is compatible with:

- no representation effect;
- an effect hidden by ceiling performance;
- an effect limited to harder or interactive cryptographic tasks;
- an effect masked by contract-compliance failures.

**Status:** primary construct blocker.

### Blocker D4 — Model sampling was not fully frozen or observed

The provider request contains only:

```json
{"model": "claude-sonnet-4-6-free", "max_tokens": 1800, "messages": [...]}
```

The retained metadata has no `temperature`, `top_p`, `seed`, system prompt, or stop-sequence fields. All 72 rows show these fields as absent. The protocol therefore did not freeze or record the model sampling state beyond the route and max-token limit.

The fixture seed is a target-data seed, not a provider sampling seed. It cannot be treated as a model-randomness control.

**Status:** reproducibility and variance-control blocker.

### Blocker D5 — Randomization is only within pair and task blocks are ordered

The schedule randomizes C1/C2 order within each seed pair, but places:

1. all ECDSA primary pairs first;
2. all ChaCha20 primary pairs second;
3. all C0 controls last.

This leaves the campaign exposed to temporal provider drift, quota behavior, route changes, or workload-dependent effects correlated with family and condition. It is not equivalent to a globally randomized blocked design.

**Status:** secondary causal and operational confound.

### Blocker D6 — C0 is not a same-predicate negative control

C0 changes the agent objective and output shape to:

```json
{"status":"UNDERDETERMINED","reason":"..."}
```

C0 therefore tests whether the agent abstains when a decisive observation is absent. It does not test the same exploit-completion predicate as C1/C2 under a representation intervention.

The C0 result is useful as an information-theoretic control, but it cannot calibrate false cryptographic exploit completion for the primary C1/C2 comparison.

**Status:** interpretation blocker for pooled 72-session claims.

### Blocker D7 — The primary success state conflates distinct failure mechanisms

The current primary endpoint requires an end-to-end accepted result, but a C2 failure can arise from:

- provider failure;
- parser/extraction failure;
- source qualification failure;
- sandbox execution failure;
- malformed candidate output;
- cryptographic predicate failure;
- certificate-integrity failure;
- attribution/evidence failure.

The two observed C2 failures are source-qualification failures, not cryptographic reasoning failures. Aggregating them into one binary success endpoint prevents a causal interpretation of representation effects on cryptographic construction.

**Status:** estimand blocker.

### Blocker D8 — Statistical power is inadequate for strong conclusions

The paired design has 24 pairs, so the marginal difference is resolved in increments of `1/24 = 0.0417`. The prespecified meaningful effect is 0.25, but the exact McNemar evidence depends on the unknown discordance structure.

Offline simulation with 24 pairs and a true marginal effect of 0.25 gave approximate exact-McNemar power of:

| Assumed discordance probabilities | Approximate power |
|---|---:|
| C1-only 0.25, C2-only 0.00 | 57.7% |
| C1-only 0.30, C2-only 0.05 | 43.1% |
| C1-only 0.35, C2-only 0.10 | 33.8% |
| C1-only 0.50, C2-only 0.25 | 22.7% |

These are planning diagnostics, not estimates of the agent effect. They show that failure to cross the threshold is not strong evidence of no effect. The observed result `2 versus 0` yields an absolute difference of only 0.0833 and exact p=0.5, but the experiment is underpowered for the intended claim.

**Status:** inferential limitation; primary null interpretation must be “not identified/not supported,” never “equivalent.”

## 3. What the current 72 sessions can support

The campaign supports only the following bounded statements:

1. Under the exact frozen contract, the repaired pipeline recorded 24/24 C1 and 22/24 C2 primary terminal outcomes accepted by the independent reference process.
2. Two ECDSA C2 candidates were rejected before execution because of an unused forbidden import.
3. The deterministic Stage 0 analysis shows semantic equivalence of the C1/C2 public observations for the declared zero-query interface.
4. The selected tasks were easy enough that C1 and ChaCha20 C2 reached a ceiling.
5. The experiment did not establish representation sensitivity, representation equivalence, or a general cryptographic-agent capability estimate.

## 4. Corrected 72-session design requirement

A valid replacement must change the design, not merely rerun the same runner.

### 4.1 Primary estimand

Use:

> The causal effect of a predeclared, isolated agent-facing representation intervention on independently verified cryptographic exploit construction, conditional on identical task semantics, execution contract, model route, and analysis protocol.

Report separate stage outcomes:

1. source/contract compliance;
2. candidate execution;
3. output validity;
4. cryptographic predicate correctness;
5. evidence/attribution validity;
6. terminal end-to-end success.

### 4.2 Correct intervention

Use a neutral prompt template with no `C1`/`C2` labels. Randomize only one representation factor at a time. Recommended arms:

- **R0:** canonical JSON hex.
- **R1:** semantically identical JSON with controlled key/order/whitespace transformation but identical encoding complexity.
- **R2:** base64-packed representation, explicitly labeled as a separate encoding-complexity intervention.

R0 versus R1 tests representation formatting. R0 versus R2 tests encoding burden. They must not be pooled into one effect.

### 4.3 Task difficulty

Retain ECDSA and ChaCha20 only as calibration tasks. Add harder, independently specified tasks before treating the study as a capability probe, such as:

- a bounded multi-step cryptographic protocol task;
- a controlled ECDSA variant with ambiguity in field naming but identical mathematical sufficiency;
- an authenticated-encryption misuse task with a nontrivial output predicate;
- one interactive task only if the query interface can be frozen and independently audited.

The harder tasks require their own sufficiency proofs and reference predicates. Do not silently expand the current estimand.

### 4.4 Session allocation

For a fixed 72-call budget, the minimum defensible design is:

- 2 families;
- 18 paired seeds per family;
- 2 primary representation arms per seed;
- 72 primary sessions total;
- C0 deterministic controls outside the provider budget.

If three representation arms are required, the study must explicitly become a three-arm exploratory design; it cannot retain the old 24-pair McNemar analysis.

### 4.5 Randomization and provider controls

- Globally randomize all sessions using a frozen seed.
- Balance family, representation, and time blocks.
- Use the same neutral prompt template.
- Record all provider request parameters, including temperature/top-p/seed if supported.
- If the provider does not expose sampling controls, state this as a design limitation and use repeated paired blocks or a larger session count to estimate stochastic variance.
- Never describe the fixture seed as a model seed.

### 4.6 Statistical analysis

Before any new calls:

- predefine the primary contrast;
- specify the estimand and valid denominator;
- define stage-specific missingness;
- simulate power under realistic discordance structures;
- choose a meaningful effect threshold based on power, not convenience;
- use global randomized order;
- retain all scheduled sessions;
- distinguish confirmatory from exploratory task families;
- do not call a non-significant result equivalence.

## 5. Disposition of the existing 72-session data

Do not delete or rewrite the current records. Reclassify them as:

- `EXECUTION_VALID_DESIGN_INSUFFICIENT_FOR_PRIMARY_CAUSAL_CLAIM`.

They remain useful for:

- harness integrity evidence;
- source-qualification failure taxonomy;
- prompt/encoding confound demonstration;
- ceiling-effect diagnosis;
- planning the corrected design;
- motivating the need for staged success accounting.

They must not be silently reanalyzed as if the corrected design had been used.

## 6. Current decision

- **Existing 72-session results as proof of H1:** NO-GO.
- **Existing 72-session results as useless:** NO; retain as diagnostic evidence.
- **Rerun the same protocol:** NO-GO; it would reproduce the identification flaw.
- **Design a corrected 72-session protocol:** GO.
- **Provider calls under corrected protocol:** blocked until the revised protocol, power plan, neutral prompt design, randomization, and provider sampling controls are frozen and independently checked.

This audit confirms the user's objection: the previous conclusion was too strong if it treated harness success as experimental adequacy.