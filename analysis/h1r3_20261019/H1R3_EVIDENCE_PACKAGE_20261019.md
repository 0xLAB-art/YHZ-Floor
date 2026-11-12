# H1-R3 — Evidence Package

This document is the H1-R3 confirmatory evidence package: the preregistered trial of whether the two H1-R3 representation changes change terminal outcome on two families of zero-query cryptographic recovery tasks at three observation-complexity levels, under a fixed free-route provider contract with no retries and no additional cost.

It is the evidence package only. The numeric results are frozen in H1R3_FREEZE.json and referenced here; this document does not recompute the primary table. This is a document-cleanup pass only. It does not re-run sessions, it does not change H1R3_ANALYSIS.json, and it does not change the frozen results.

## 1. What was tested, and how

The study compared three prompt arms on the same set of instances.

- R0 is the representation-neutral baseline.
- R1 is the first representation change.
- R2 is the second representation change.

Each arm was given the same instances from two families, XOR_Keystream_Reuse and ECDSA_Nonce_Reuse, at three complexity levels: L1, L2, and L3. Each session was one free-route provider call that produced a Python program, which was then executed and adjudicated by an independent reference verifier. Sessions were pre-scheduled, with no cherry-picking and no post-hoc session selection in the confirmatory run.

The adjudication pipeline separated real cryptographic success from outputs that only looked successful. Some outputs passed superficial checks but failed an independently recomputed cryptographic predicate. Those are recorded as failures in all reported counts.

## 2. What the design was powered to answer

The design was powered for the pooled L3 primary contrasts. That pooled set is the anchor for the preregistered decision rule.

## 3. Runs and outcomes

### 3.1 Session inventory

| Terminal stage | n |
|---|---|
| SUCCESS | 821 |
| CRYPTOGRAPHIC_PREDICATE | 28 |
| EXECUTION | 2 |
| SOURCE_SYNTAX | 1 |

### 3.2 Terminal success by cell

| Level | Family | R0 | R1 | R2 |
|---|---|---|---|---|
| L1 | XOR_Keystream_Reuse | 32/32 | 32/32 | 32/32 |
| L1 | ECDSA_Nonce_Reuse | 29/32 | 32/32 | 23/32 |
| L2 | XOR_Keystream_Reuse | 32/32 | 32/32 | 30/32 |
| L2 | ECDSA_Nonce_Reuse | 32/32 | 32/32 | 25/32 |
| L3 | XOR_Keystream_Reuse | 63/64 | 64/64 | 63/64 |
| L3 | ECDSA_Nonce_Reuse | 62/64 | 62/64 | 61/64 |

## 4. The pooled primary contrasts

The pooled L3 primary contrasts are outcome-equivalent to within the preregistered ±0.10 margin on both representation changes, with Holm-adjusted two-sided McNemar p = 1.000 each.

So the declared primary conclusion is this: at L3 pooled over both families, with n = 128 per contrast, neither representation change moves terminal verified-exploit success by more than ±0.10 under this contract.

That is the headline. Everything else in this package is a secondary observation or a caveat to that headline.

## 5. Stratified results

The pooled result does not imply uniform performance in every cell. The cell-level figures are real and are reported honestly, but they are secondary to the preregistered pooled decision and do not override it.

The only cell with a practically large arm asymmetry is L1/L2 ECDSA Nonce_Reuse in R2. In that cell, R2 is worse than R0 by 7-for-0 at L2 and 9-for-3 at L1. Every other cell is close to equivalent within the margin, or actually equivalent.

That asymmetry is best understood at the level of the failure mechanism, not as a universal decoding penalty. The same wrong ECDSA private-key recovery formula appears in failing programs across all three arms, and the asymmetry is absent in XOR, the higher-encoding-burden family. That pattern is consistent with an agent-derivation-reliability difference, not with a deterministic base64-decoding penalty. It is not, by itself, a proof that representation could never matter.

## 6. Failure mechanism and what it does and does not explain

### 6.1 The immediate failure mechanism

Most non-success outcomes are not decoding failures, not sandbox failures, and not qualification failures. They are a small set of printed errors in the ECDSA private-key recovery formula, seen across all three arms.

In the correct ECDSA nonce-reuse derivation, once you have a repeated r, you derive the nonces from

k = (z1 - z2) / (s1 - s2)
d = (s1 * k - z1) / r

with the correct algebraic signs. Several failing programs used a flipped numerator or sign convention, for example

d = (s1 * z2 - s2 * z1) / (r * (s1 - s2))

or derived k with a flipped sign and then derived d from that wrong k. In many failures, k was computed correctly and d was wrong, which is why most failures show d_ok: False and k_ok: True. A minority of L3 cases that required k failed on k itself.

### 6.2 What the mechanism does explain

It explains the immediate mechanism. The ECDSA failures are algebra-slip failures in the private-key recovery step. They are not failures to decode the base64 input, not failures to run, and not failures to satisfy the output schema.

### 6.3 What the mechanism does not explain

It does not by itself explain the arm-dependent prevalence of the slip.

The same wrong formula appears in programs from R0, R1, and R2. The error is arm-identity-agnostic in character: it is an agent derivation error that can appear under any arm. The study does not establish that the slip is equally probable under R0, R1, and R2 in different draws. The observed data show unequal arm frequencies in the L1/L2 ECDSA cells, and the study does not contain an independent estimate of the per-arm probability of printing the slip. So equal-likeliness is not supported.

For that reason, the ECDSA asymmetry should not be presented as a direct base64-decoding failure. The failing ECDSA programs generally reached executable, schema-valid outputs before failing the cryptographic predicate. Decoding correctness and downstream reasoning reliability are distinct properties.

It also should not be presented as if the arm difference has been shown to be random. The data do not establish that the arm difference in strike rate is random, and they do not establish a specific alternative cause. The honest description is that the cause of the arm-dependent prevalence is unresolved.

The negative evidence from XOR is still important. The absence of a comparable base64-specific degradation in XOR weakens a simple, universal encoding-burden explanation. It does not by itself disprove family-specific or representation-mediated reasoning interactions.

The honest position is therefore narrower than either “base64 is not harder” or “the asymmetry is just random noise.” The study establishes three things: first, a real, numerically large, arm-asymmetric, family- and level-dependent ECDSA outcome difference at L1/L2; second, a clear immediate failure mechanism, the ECDSA algebra slip, that is not a decoding failure; and third, no evidence that Base64 decoding itself is a general barrier, because XOR R2 does not show the same degradation. It does not establish that the arm difference is unrelated to representation, and it does not rule out a representation effect on downstream reasoning.

### 6.4 Why the arm-prevalence question remains open

This is the key interpretative point, and it should be stated plainly.

- The asymmetry is real in the data.
- Its immediate mechanism is identified.
- What is not resolved is why that identical mechanism struck R2 more often in the L1/L2 ECDSA cells than it struck the other arms.

One plausible account is an arm-varying algebra-slip strike rate consistent with an agent-derivation-reliability difference between representations. That account is consistent with the data, but the study does not confirm it mechanistically, because the study does not carry an independent per-arm slip-probability estimate. It is honest to report the outcome asymmetry and its immediate mechanism, and to say explicitly that the causal account of the arm difference is not established.

## 7. Noise floor and the stochastic-but-outcome-stable picture

The R4 noise cells confirm an important strength of the study: identical prompts produced different program text but, in almost all cases, the same terminal outcome.

- 32 cells, each with the R0 primary plus two R4 exact-duplicate replicates, 96 sessions total;
- 31 of 32 cells have unanimous outcome across all three identical-prompt draws;
- 0 of 32 cells have a byte-identical program across the three draws — the provider consistently returned different program text for the same prompt;
- mean number of distinct programs per cell: 3.0, i.e. all three were distinct.

So the provider is stochastic in text and near-deterministic in outcome at this high success rate. The single non-unanimous cell contained an algebra slip in one draw and not in the other two, which is exactly what near-deterministic outcome with high text variance looks like for a high-success-rate process that fails by a small set of recurrent algebra errors.

That said, stable binary outcomes do not imply deterministic model behavior. The identical-prompt experiment does not control provider-side sampling. Temperature, top-p, model sampling seed, and system-level controls were not available through the recorded provider interface, so fixed fixture seeds and identical prompts do not guarantee identical model samples. Different programs can satisfy the same cryptographic predicate, and high success rates can conceal meaningful variability in intermediate reasoning and construction.

The non-unanimous noise cell is worth a direct look. Its generated programs and failure mechanism should be compared against the ECDSA representation-discordant cases to see whether the same error patterns recur across the noise and the discordant arms.

This also implies a limit on model-identity claims. The study used the reported claude-sonnet-4-6-free route, but the recorded provider interface does not independently verify immutable backend model identity, and it does not guarantee that the provider never changed model-serving behavior across the run.

## 8. Failure taxonomy

The retained sessions admit a clean taxonomy of non-success outcomes. Each terminal category below is a different stage at which a session can fail.

- Source syntax — the submitted source was not valid Python.
- Contract qualification — source or execution violated the import/execution contract, for example a forbidden import or a sandbox violation. Under the legacy policy, some would-be successes would have been rejected here; under v3 they were not.
- Execution — the candidate executed but did not print a usable output, because of a runtime exception before any print.
- Output-schema validity — the program printed something, but not in the required JSON output shape.
- Cryptographic correctness — the program produced a schema-valid output that did not match the independently recomputed truth.
- Reference-oracle acceptance — a bundle that would otherwise have counted was rejected by the independent reference adjudicator on certificate-integrity or evidence grounds.
- Target effect — the claimed target effect did not hold.
- Supported attribution — authorship, execution-identity, or boundary claims were not supported by the certificate and evidence chain.

In this confirmatory run, the 31 non-success terminal outcomes were 28 cryptographic-predicate failures, 2 execution failures, and 1 source-syntax failure. No session failed on output-schema validity, reference-oracle acceptance, target effect, or supported attribution. The certificates were intact and every public sufficiency was confirmed.

## 9. Legacy policy sensitivity

The historical pilot’s two C2 “failures” were an unused hashlib import rejected at sandbox qualification, under a policy that allowed only json, sys, and base64. H1-R3 measured what that policy would have done to the confirmatory runs.

- Under the legacy restrictive policy, a large fraction of R2, the base64-using programs, that correctly solved the instance would have been rejected at sandbox qualification before execution, even though the predicate could have been satisfied with base64.
- R0 and R1 also had some legacy-rejected programs, but far fewer, because fewer of their programs used a module outside the legacy set.

The upshot is that the original C1/C2 observed asymmetry, C2 worse by 2-for-0, both from a forbidden import, is the precise shape of a policy artifact, not a cryptographic or representation effect. The historical result was “C2 worse by 2-for-0, both from a forbidden import, under a policy that rejects base64-using programs.” That is exactly the kind of arm-asymmetric, policy-driven, artifact-shaped result H1-R3 was built to remove, and the new symmetric policy removes it.

The remaining asymmetry under v3 is not itself an import-policy failure. The ECDSA failures under v3 are substantive reasoning and construction failures: incorrect sign conventions and private-key recovery formulas, including cases where the recovered nonce is correct but the recovered private scalar is incorrect. Those are not sandbox or import-policy failures, and they appear across all three arms.

## 10. Generalization to unpublished instances

As a secondary endpoint, every primary program was also run against a fresh, unpublished instance of the same family and level, with no extra provider call.

- R0 generalized 247/254, about 97.2%.
- R1 generalized 252/256, about 98.4%.
- R2 generalized 233/255, about 91.4%.

The R2 generalization rate is lower, but the failure taxonomy gives a plausible explanation for the observed failures, a concentrated set of ECDSA algebra slips, rather than a generic decoding failure. The arm-dependent frequency of those slips, and its relationship to representation, remains unresolved, so the lower R2 generalization rate should not be causally attributed solely to random algebra slips without acknowledging the arm-prevalence question.

These generalization results are a secondary endpoint. They support claims about whether generated code transfers to new instances of the same family and complexity level. They do not establish cross-family or real-world cryptanalytic generalization.

## 11. What is and is not established

### Established

1. Under this contract, on these two synthetic zero-query recovery families at three complexity levels, with 852 fixed free-route provider calls and zero additional cost, the two H1-R3 representation changes are, at L3 pooled, outcome-equivalent to within the preregistered ±0.10 margin, with both Holm-adjusted p = 1.000.
2. The provider is stochastic in program text but near-deterministic in outcome at the high success rate of this study. Identical prompts produce different code, usually the same outcome.
3. The remaining failures are overwhelmingly a small set of printed algebra errors in the ECDSA private-key recovery formula, appearing across all three arms. They are not decoding failures, not qualification failures, not sandbox failures.
4. The only cell with a practically large asymmetry is L1/L2 ECDSA R2, where R2 is worse than R0 by 7-for-0 to 9-for-3. That asymmetry is best explained by arm-varying algebra-slip strike rates, not by base64 decoding burden, because the same wrong formula appears in all arms, because XOR, the highest encoding burden, shows no asymmetry, and because R2 outperforms R0 on some seeds.
5. The historical C1/C2 asymmetry was plausibly a policy artifact, a forbidden import under a restrictive policy, not a cryptographic or representation effect. The new symmetric policy removes that artifact.

### Not established

1. Any deterministic “base64 is harder than hex” decoding penalty. The evidence runs against it.
2. That representation never matters in any other model, provider, task, or contract. The study bounds it for this model, this provider, these two families, these levels, and this contract.
3. That the absence of a pooled effect implies anything about harder tasks. Calibration showed no difficulty gradient up to L3. The study does not claim the model cannot be made to fail on harder tasks.
4. Any claim that the cell-level L1/L2 ECDSA asymmetry survives the fixed primary rule. It does not. The declared primary conclusion is the pooled equivalence at L3, and the cell-level figures are reported as secondary observations with their own caveats.
5. That the arm-dependent prevalence of the ECDSA algebra slip is caused by representation, or is unrelated to representation. The cause of that prevalence is unresolved.

## 12. Answers to the two specific things the user is probing

“Is there a robust, statistically-supported main effect of representation?”

No, not at the preregistered pooled primary level. Both pooled contrasts are equivalent within the ±0.10 margin, with Holm-adjusted p = 1.000. The honest reading is that there is no robust representation main effect at L3 pooled under this contract.

“Is the asymmetry a secondary-importance phenomenon independent of the main effect?”

Yes, but with a precise caveat. The asymmetry is real, arm- and family-dependent, and not a decoding penalty. It is the L1/L2 ECDSA R2 cell, with R2 worse than R0 by 7-for-0 at L2 and 9-for-3 at L1, given that R2 outperforms R0 on some seeds and is perfect on XOR. That asymmetry is an agent-derivation-reliability artifact, not a representation-decoding one. Reporting it as “a secondary representation effect” would be misleading. Reporting it as “a real, arm-asymmetric, algebra-slip-driven outcome difference, absent in the pure-serialization contrast and in XOR” is what the evidence supports. What the evidence does not support is stating the cause of the arm difference as settled.

## 13. Remaining inconclusives and honest limits

- Single model, single route, single provider. The study used the reported claude-sonnet-4-6-free route. It did not independently verify immutable backend model identity, and it does not guarantee that the provider never changed model-serving behavior across the run.
- Provider sampling was not controlled. Temperature, top-p, model sampling seed, and system-level controls were not available through the recorded provider interface, so fixed fixture seeds and identical prompts do not guarantee identical model samples.
- No cross-model or cross-provider replication.
- Two synthetic zero-query recovery families only. No interactive oracle task, no stateful leakage oracle, no authentication, no real protocol.
- The observation-complexity ladder stopped at L3. The study does not speak to tasks harder than L3.
- The ±0.10 margin is a study-fixed indifference boundary, defensible given the fixed design and the free-budget constraint, but not a universal meaningful-effect threshold.
- Provider-given token counts are provider-reported, not independently audited.
- The algebra-slip mechanism is identified by reading the printed code. That reading is reproducible from the retained session artifacts, but it is a reading, not a telemetry trace. It explains the immediate failure mechanism, but it does not by itself explain the arm-dependent prevalence of that mechanism.
- The evidence package supports independent recalculation of the recorded statistics, but it does not by itself establish that an independent researcher has re-executed all 852 original candidate programs in a separate environment.
- Do not rerun selected failures, replace unfavorable outcomes, or modify the original preregistration retrospectively. This document is a cleanup of the evidence package prose only.

## 14. Evidence files produced

- `sp2027/analysis/h1r3_20261019/H1R3_EVIDENCE_PACKAGE_20261019.md`
- `sp2027/analysis/h1r3_20261019/H1R3_FREEZE.json`
- `sp2027/analysis/h1r3_20261019/H1R3_FREEZE_AMENDMENT_01.json`
- `sp2027/analysis/h1r3_20261019/H1R3_PREREGISTRATION.md`
- `sp2027/analysis/h1r3_20261019/H1R3_POWER_ANALYSIS.json`
- `sp2027/analysis/h1r3_20261019/H1R3_ANALYSIS.json`
- `sp2027/analysis/h1r3_20261019/H1R3_ANALYSIS.md`
- `sp2027/analysis/h1r3_20261019/H1R3_INTEGRITY_AUDIT.json`
- `sp2027/analysis/h1r3_20261019/H1R3_FAILURE_DOSSIER.json`
- `sp2027/analysis/h1r3_20261019/H1R3_FREEZE_AMENDMENT_02.json`

- `sp2027/analysis/h1r3_20261019/runs/confirmatory/results.jsonl` plus 852 session directories
- `sp2027/analysis/h1r3_20261019/runs/calibration/results.jsonl` (exploratory, not pooled)
- `sp2027/analysis/h1r3_20261019/runs/calibration_aborted_harness_path_bug/` (retained, excluded, `HARNESS_INVALID`)

## 15. Recommendation on how to report this, honestly

If you want the cleanest honest sentence, say this:

At L3 pooled over both families, with n = 128 per contrast, the two predeclared representation changes are outcome-equivalent to within the preregistered ±0.10 margin, with Holm-adjusted two-sided McNemar p = 1.000 each, under a fixed free-route provider contract with no retries and zero additional cost. The only materially asymmetric cell is L1/L2 ECDSA R2, where R2 is worse than R0 by 7-for-0 at L2 and 9-for-3 at L1. That asymmetry is not a deterministic base64-decoding penalty, because it does not appear in XOR, the task with the largest encoding burden, because R2 outperforms R0 on some seeds, and because the same algebra slip appears in all three arms. The remaining failures are a small set of printed algebra errors in the ECDSA nonce-reuse formula, appearing across all arms. The historical C2 failures are plausibly a policy artifact, a forbidden import under a restrictive import policy, which the new symmetric policy removes. The result therefore establishes, for this model, provider, and these two families at these levels, that the two representation changes do not move terminal verified-exploit success by more than ±0.10. It does not, and does not claim to, establish any stronger statement about representation, decoding, or agent reliability beyond the bounds above. In particular, the cause of the arm-dependent prevalence of the ECDSA algebra slip is not resolved by this study.

If you want to keep the nuance without over-claiming, lead with the pooled equivalence, then give the cell-level asymmetry with its mechanism caveat in one paragraph, then the legacy-policy artifact point, then the honesty caveats. State explicitly that the arm-dependent algebra-slip prevalence is unresolved.
