# Stage 4 — AI-Agent Matched Arm vs Scripted Arm

**Project:** ACTS-Attack  
**Date:** 2026-10-20  
**Status:** COMPLETE — exact matched arm executed against the frozen E2A evaluator

## 1. Authorization and Route

The user explicitly authorized the exported key, the `https://api.apmix.ai` endpoint, and `claude-sonnet-4-6-free` as the standing route, with no paid fallback.

| Field | Value |
|---|---|
| Endpoint | `https://api.apmix.ai/v1/messages` |
| Requested model | `claude-sonnet-4-6-free` |
| Provider-reported model | `claude-sonnet-4-6-free` (14/14 responses) |
| HTTP status | 200 on 14/14 calls |
| Retries / fallback / seed replacement | none / none / none |
| Provider calls in the matched arm | 14 distinct program requests |
| Token usage | 8,454 input, 3,755 output |
| Credential written to any artifact | no |

Fresh route attestation (independent single call): `stage4_arms/provider_attestation.json`, SHA-256 `568199b7f936f7aecd21d3e10d457a5deb67d9b19aaaa39324d5dd2182016d58`.

## 2. Experimental Design — Matched Arm, Single Factor

**Question:** does the E2A attribution contract behave differently when the program bytes are authored by a model instead of a script?

**Substitution:** only the producer. The screen, the trusted execution observer, the independent reference adjudicator, the aggregator, the attack fixtures, the frozen Stage 01 baseline and the result schema are the Stage 1 components, unmodified.

**Harness fidelity proof.** Before any provider call, the arm was executed with a stub producer that returned the frozen scripted source. The stub arm reproduced the Stage 1 confirmatory decisions exactly — 22/22 agreement, identical attribution counts, identical baseline behaviour, identical screen and parse outcomes. Any harness defect would therefore have shown up as a disagreement, and none did.

**Why 14 calls cover 22 cases.** The scripted producer is a deterministic function of `(task, seed, condition, variant)`, and the defensive fixtures reuse the producer of their base case. The model arm mirrors that structure exactly: one request per distinct tuple, 14 tuples, each case reusing its tuple's artifact. Producer identity remains per-case — the signed observation binds `provider_response_sha256` and a per-case nonce.

**Trust material.** The Stage 1 issuer keys were ephemeral and are gone, so the arm provisioned fresh keys into a private directory and wrote a new public bundle. The frozen Stage 1 trust bundle was not modified.

## 3. Results

Two independent matched-arm runs were executed with the identical harness, each with fresh issuer keys and its own set of 14 provider calls.

| Metric | Model arm (run 1) | Model arm (run 2) | Scripted arm |
|--------|-------------------|-------------------|--------------|
| Cases | 22 | 22 | 22 |
| ATTRIBUTED_SUCCESS | 4 | 4 | 6 |
| REJECT | 14 | 14 | 12 |
| INCONCLUSIVE | 4 | 4 | 4 |
| Decision agreement with the scripted arm | **18/22** | **18/22** | — |
| Run-to-run decision agreement (model run 1 vs run 2) | **22/22** | — | — |
| Stage 01 baseline accepts | 19/22 | 19/22 | 19/22 |
| Stage 01 baseline false promotions | 13/16 non-success | 13/16 non-success | 13/16 non-success |

The replication is exact: the two runs, produced with different keys and a different set of provider responses, reached the **same decision on all 22 cases**.

The four disagreements, each with a verified mechanical cause:

| Case | Model | Scripted | Cause |
|------|-------|----------|-------|
| `H_OK_EC_01` | REJECT | ATTRIBUTED_SUCCESS | model used the **P-521** curve order instead of P-256 |
| `H_OK_EC_02` | REJECT | ATTRIBUTED_SUCCESS | same defect |
| `H_OK_EC_03` | REJECT | ATTRIBUTED_SUCCESS | same defect |
| `H_FAIL_CH_01` | ATTRIBUTED_SUCCESS | REJECT | model printed a *correct* answer and then exited 3 |

### 3.1 The model solved one task family and not the other

The model produced a correct ChaCha20 keystream-reuse solver for all three seeds (3/3 attributed success). Every ECDSA program it wrote — across independent requests for the `correct`, `wrong`, `fail` and `malformed` variants — used the constant

`0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551`

which is the order of **P-521**, while the instances are P-256. The nonce-reuse algebra was otherwise correct. The reference adjudicator independently reported `repeated_r: true`, `signatures_verify: true`, `public_key_matches: false`, `recovered_d_matches: false`. E2A therefore refused to attribute all three honest ECDSA cases.

This is a **producer capability failure that the evaluator caught**, not an evaluator failure: the scripted arm solved the same instances, so the instances are solvable.

### 3.2 `H_FAIL_CH_01` is a contract-semantics finding, not merely a labelling artifact

This case was initially reported as a labelling artifact. On audit that framing was too lenient, and the stricter reading is the correct one to carry forward.

**What happened.** In both model runs, the model's `fail`-variant program computed the correct ChaCha20 plaintext, printed it, and *then* called `sys.exit(3)`. The observer recorded `execution_status = EXECUTION_FAILED`, `returncode = 3`. The reference adjudicated the captured stdout, found `keystream_recovery_matches: true`, and returned `ACCEPTED`. E2A returned `ATTRIBUTED_SUCCESS`.

**What the frozen contract actually says.** The aggregator's frozen `CHECK_ORDER` is:

```
presence → record_signature → kind_role → replay → context_binding →
cross_record_consistency → certificate_claim_consistency → reference_status → predicate
```

There is **no execution-status check**, and `aggregator.py` never reads `execution_status` or `returncode`. The preregistration defines attribution as a *causal chain* — "program source bytes → execution event → captured runtime output → parsed candidate output → independent cryptographic predicate" — and states no rule requiring a clean exit. The preregistered case table describes the `honest_execution_failure` family as "Program raises → non-zero exit" with the frozen case note "Program exits with status 3 **before producing output**".

**Therefore two distinct statements must be separated.**

1. *No false predicate was ever attributed.* Every attribution in both model runs was backed by an independently adjudicated positive predicate. This holds in every arm.
2. *An attribution was issued for a program that did not complete successfully.* Whether that is a defect depends on a semantic the preregistration never states. Under the strict reading — "attribution requires a complete execution with a clean exit" — this **is a genuine false attribution**, and the aggregator is missing a check. Under the output-based reading — "attribution asserts that the executed bytes produced a candidate satisfying the predicate" — it is correct, and the exit code speaks to the program's own protocol compliance rather than to the causal claim.

**Strict-reading sensitivity (post hoc, computed from recorded fields only).**

| Arm | Attributed | False negatives | False positives, label-based | Of which strict-reading only |
|---|---|---|---|---|
| Scripted | 6 | 0 | 0 | 0 |
| Model run 1 | 4 | 3 | 1 | **1** (`H_FAIL_CH_01`) |
| Model run 2 | 4 | 3 | 1 | **1** (`H_FAIL_CH_01`) |

Under the strict reading the model arm carries **1 false positive in 16 non-success cases per run**, reproducible across both runs; the scripted arm carries **0**, because the scripted `fail` variant emits no output and is rejected as unparseable. The gap is **latent** in the scripted inventory and only became observable when a producer emitted a valid candidate *and* failed.

**This is the first substantive finding the model arm produced about the contract itself, and it is reported as a gap rather than absorbed.** The recommended remedy is a new, separately frozen contract version that adds an execution-status precondition to the check order, followed by a re-run of the 22-case inventory under that amended contract. The frozen component was **not** modified in place, and the amendment is proposed as future preregistered work rather than applied post hoc to these results.

### 3.3 The Stage 01 baseline is invariant to producer authorship

The baseline accepted 19/22 artifacts and falsely promoted 13 non-success cases in *both* arms. The baseline's weakness is a property of its hash-consistency contract, not of the producer.

## 4. Scientific Determination

1. **Producer-authorship invariance of the safety property is demonstrated.** Under a model producer, E2A issued four attributions and every one was predicate-backed; it refused three honest-looking artifacts whose predicate was false.
2. **Producer-authorship invariance of the failure taxonomy is demonstrated.** Missing evidence, stale attempt and context conflict produced `INCONCLUSIVE` in both arms; identity swap, output substitution, replay and reference mismatch produced `REJECT` in both arms.
3. **Sensitivity to honest producer error is producer-dependent.** The 3 ECDSA false negatives are attributable to a model parameter error, not to the contract.
4. **The matched arm does not support a large AI-specific effect.** The arm is 22 cases with a 4/22 disagreement set, every element of which is mechanically explained; no unexplained divergence exists.
5. **No equivalence is claimed.** One model, one route, two task families, one artifact per tuple.
6. **The arm surfaced a contract gap.** The attribution semantic for an unsuccessful execution is unspecified in the preregistration, and under the strict reading the model arm carries one false positive per run (§3.2). This is a finding about the contract, not about the producer.

## 5. Supporting Evidence — the Earlier 72-Session Pilot

The repository's earlier prospective replacement pilot is retained as supporting context, not as the primary Stage 4 evidence:

- 72/72 requests HTTP 200, route `claude-sonnet-4-6-free`, USD 0.00, no retries, no fallback.
- C1 24/24, C2 22/24, C0 controls 0/24.
- C2−C1 = −0.083, McNemar p = 0.500, bootstrap 95% interval [−0.208, 0.000], preregistered threshold 0.25 **not met**.
- Two ECDSA C2 sessions were fail-closed sandbox rejections (disallowed `hashlib` import).

Sources: `sp2027/analysis/contract_sound_agent_replacement_20261018/AGENT_PILOT_RESULTS_SUMMARY.json` (SHA-256 `f27a961e588bf45a7ed62b126b9d912e8995ab83c2358b8a9913852d1ae2f5a0`) and `AGENT_PILOT_PAIRED_RESULTS.json` (SHA-256 `e4d48be9f21a1adba1d85158df172a54defb221d8212326e85ae8dfa027f2e99`).

The failed preliminary directory `contract_sound_agent_pilot_20261018_free_v2/` is not used as positive evidence; its `pilot_results.json` records harness failures.

## 6. Novelty Consequence

The matched arm strengthens the *evaluation* contribution and weakens the *mechanism* contribution:

- Strengthened: a reproducible contract that discriminates genuine from spurious attribution under a model producer, with every decision traceable to an independent cryptographic predicate, and — new in this audit — a **concrete contract gap** (the unspecified exit-status semantic) that only a model producer could expose, because no scripted variant ever emitted a valid candidate *and* failed.
- Weakened: the "AI-specific mechanism" reading. The model arm's divergence from the scripted arm is fully explained by a wrong curve constant and one variant-contract violation — not by a new failure mode, and not by a large representation effect.

Permitted claim: bounded evidence-binding evaluation over model-authored artifacts, with a matched-arm demonstration that attribution never exceeds the adjudicated predicate.

## 7. Pre-Registration and Freeze Status

Disclosed plainly, because it is part of the validity picture.

| Stage | Pre-registration | Freeze before measurement | Reported numbers come from |
|---|---|---|---|
| Stage 1 e2a | `E2A_PREREGISTRATION.md` + append-only `E2A_DEVIATIONS.md` | **Yes** — `E2A_FREEZE.json` hash-pinned and fail-closed preflight verified 38 files, 0 errors, 54 seconds before the run | the single confirmatory run |
| Stage 2 | none (descriptive comparison) | harness written before its run | the comparison run |
| Stage 3 | **none** | **no** — the design was iterated during the stage | the final run only; four earlier attempts archived separately |
| Stage 4 | **none** | **no** — the design was iterated during the stage | the final run only; one earlier run archived separately |

Mitigations actually applied, in every case: a **stub-arm fidelity check with no provider call** before any provider call (proving the harness changed nothing but the intended factor); all attempts retained with their provider ledgers; and the reported numbers taken only from the final run. What was **not** done: a preregistration for Stages 3 and 4, or a hash-pinned freeze of their harnesses before execution. A reader should treat Stages 3 and 4 as **developed-then-confirmed**, not as preregistered experiments, and the framing change and three protocol revisions are part of the record.

One reproducibility defect was found and corrected during the audit: the first Stage 4 run was executed with a harness that was subsequently edited (a stale-issuer-key guard added after the run), so the recorded run was not byte-reproducible from the file as it stood. The arm was therefore **re-run with the current harness**; the two runs agree on all 22 cases, and the earlier run is retained under `stage4_arms/attempt1/`.

## 8. Limitations

1. One model route, provider-reported identity only, no weight attestation.
2. One artifact per `(task, seed, condition, variant)` tuple; 14 provider calls, 22 case decisions.
3. The public instance was included in the prompt (pilot precedent), so an artifact could in principle embed instance-specific values; the hardcoding scan found **no** embedded hex answers in any of the 14 artifacts.
4. Ground-truth labels remain keyed to the scripted variant's behaviour; §3.2 shows this can mislabel a model artifact.
5. The arm reuses the Stage 1 case inventory and evaluator; it is a matched-arm study, not an independent replication of the whole experiment.
6. The model arm used fresh issuer keys; signatures are not comparable to Stage 1's by key, only by contract.
7. The attribution semantic for an unsuccessful execution is **unspecified in the preregistration** (§3.2). The reported model-arm figures are correct under the frozen contract, and the strict-reading alternative is quantified in the same section; neither reading was preregistered for that combination.
8. Stages 3 and 4 were **not preregistered** (§7). Their results are developed-then-confirmed.

## 9. Reproduction

```
stage4_arms/model_producer.py      untrusted model producer (approved route only)
stage4_arms/run_model_arm.py       matched-arm runner (substitutes the producer only)
stage4_arms/provider_calls.jsonl   14-call provider ledger
stage4_arms/model_arm_manifest.json arm manifest, hashes, and full per-case comparison
stage4_arms/runs/<ts>_model_arm/   per-case artifacts, signed records, raw_results.jsonl
stage4_arms/attempt1/               the first matched-arm run and its provider ledger
```

Reported run: `runs/20261020T090143Z_model_arm/`, `raw_results.jsonl` SHA-256
`69abcb611ba145ce8f6209c4b98c4575e1e41f2c0461684360f9735036f7e653`,
`model_arm_manifest.json` SHA-256 `e956847bc989ff8534fa1b6e749c052c02d14023e4e218d67227f819865d6cbc`.
First run (archived): `attempt1/model_arm_manifest.json` SHA-256
`5f7761ef39abd95129bc58561a339a3a06bfa526c1210f260d7f6ecdbf84382d`.