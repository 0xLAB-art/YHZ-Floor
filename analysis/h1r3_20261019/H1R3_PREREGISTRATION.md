# H1-R3 — Preregistered Confirmatory Protocol

**Status:** frozen before the confirmatory provider campaign.
**Date:** 2026-10-19
**Supersedes for causal inference:** the H1 72-session replacement pilot
(`EXECUTION_VALID_DESIGN_INSUFFICIENT_FOR_PRIMARY_CAUSAL_CLAIM`). That campaign is
retained unchanged and is never pooled with H1-R3.

---

## 0. Why the previous experiment cannot answer H1

The 72-session pilot is retained as a diagnostic record. Five defects prevent it
from identifying the question it was meant to answer:

| Defect | Evidence | Consequence |
|---|---|---|
| Confounded intervention | C1 vs C2 differed in an explicit `Condition:` label, in encoding family, in prompt length, and in decoding burden | no single causal factor is identified |
| Saturation | 24/24 C1, 22/24 C2, 0/24 C0; ChaCha20 showed no variation | a null contrast is uninformative |
| No noise floor | no repeated identical-prompt sessions | the observed 8.3 pp difference cannot be compared to sampling variation |
| Aggregated endpoint | one binary endpoint mixed qualification, execution, schema, and cryptographic correctness | the two "failures" were an unused forbidden `hashlib` import, not cryptanalysis |
| Underpowered | 24 pairs, exact McNemar p = 0.500, CI [-20.8 pp, 0] | neither an effect nor equivalence is established |

H1-R3 repairs each of these by construction, not by reanalysis.

---

## 1. Primary hypothesis

**H1-R3.** For a fixed cryptographic instance and a fixed execution contract, a
*predeclared, semantics-preserving change in the serialization of the public
observation* does not change the probability of independently verified exploit
completion by a code-writing model, beyond a predeclared margin.

Operational form (paired, per instance $i$):

$$\tau_{A} \;=\; P(Y_{i}^{A}=1) - P(Y_{i}^{R0}=1), \qquad H_0:\ |\tau_A| \ge \delta,\quad H_1:\ |\tau_A| < \delta$$

with $\delta = 0.10$. The substantive claim under test is **non-inferiority /
equivalence**, because calibration established that the tasks are at or near
ceiling for the only available model; a superiority test would be uninformative.

A rejection of $H_0$ in favour of equivalence is *not* a claim that no
representation effect exists anywhere. It is a bounded claim at the tested
complexity levels, task families, model, and contract (§9).

---

## 2. What is manipulated, and what is held fixed

Every instance is cloned across arms. The hidden target state, the auxiliary
inputs, the required output schema, the parser, the executor, the sandbox, the
timeout, the token budget, and the model route are identical in every arm.

| Arm | Payload serialization | Instruction block |
|---|---|---|
| **R0** reference | sorted keys, compact JSON, lowercase hex field values | identical template |
| **R1** serialization-only | fixed alternate key order, `indent=2` pretty printing, **same field names, same values, same hex alphabet** | identical template |
| **R2** encoding | sorted keys, compact JSON, **base64** field values | identical template |
| **R4** noise replicate | byte-identical prompt to **R0** | identical |

The R0↔R1 contrast is the clean representation intervention: the same characters
appear in the same alphabet with the same field names; only key order and
whitespace change. R0↔R2 isolates encoding and decoding burden, which the
original C1/C2 contrast entangled with the condition label. R4 measures the
model's own sampling variability on an unchanged prompt.

Condition labels (`C1`, `C2`, `R0`, …) never appear in any prompt. The
instruction block is byte-identical across arms and is verified as such.

### 2.1 Mathematical equivalence (checked, not assumed)

For every instance and every arm, the harness decodes the rendered payload back
to semantic bytes and asserts equality across arms (`semantic_equality`), asserts
that the three serializations are textually distinct, and asserts that the C0
variant is underdetermined. This is a deterministic pre-provider gate
(`h1r3_gate.py`), not an argument.

### 2.2 Sufficiency (witnessed, not asserted)

Each instance carries a constructive recovery witness computed by the generator,
and the independent reference verifier **recomputes** that witness from the public
observation alone and checks it against the private state. The reference
adjudicator re-implements curve arithmetic and payload decoding; it imports
nothing from the fixture generator and reads no stored expected verdict.

### 2.3 C0 is not on the primary scale

The C0 abstention block uses a different predicate (correct abstention on a
provably underdetermined observation). It is reported separately and is never
pooled with the representation contrast. This directly repairs audit defect D6.

---

## 3. Observation-complexity ladder

The cryptographic predicate is identical at every level of a family. Only the
number of observations and the amount of decoding and bookkeeping required to
apply that predicate changes.

| Level | XOR keystream reuse | ECDSA nonce reuse |
|---|---|---|
| **L1** | 2 ciphertexts, one full crib, 64-byte target | 2 signatures, both share the nonce |
| **L2** | 4 ciphertexts, 3 crib sources covering the target, 128-byte messages, 1 decoy crib | 6 signatures, exactly one repeated-`r` pair |
| **L3** | 8 ciphertexts, 7 crib sources, 256-byte messages, 192-byte target, 3 decoy cribs | 16 signatures, exactly one repeated-`r` pair, `d` and `k` required |

The ladder deliberately does **not** escalate cryptanalytic depth. Escalating
depth (lattices, truncated nonces) would measure model capability, not
representation sensitivity, and would confound the estimand. The ladder instead
escalates the *observation-processing surface*, which is where the hypothesized
mechanism (parsing and decoding behaviour) lives.

Calibration (46 exploratory sessions, §7) showed that this ladder did **not**
break the ceiling. That is reported as a result: observation complexity is not a
sufficient difficulty lever for this model in this range. The confirmatory design
therefore targets precision, not power against an unknown effect.

---

## 4. Execution contract

Two changes relative to the historical pilot, both symmetric across arms and both
frozen before any confirmatory call:

1. **Import policy.** The historical policy allowed only `json`, `sys`, `base64`.
   Two of the two historical C2 failures were unused `hashlib` imports rejected
   before execution. H1-R3 uses policy **v3**, which admits computationally inert
   standard-library modules (`hashlib`, `math`, `struct`, `itertools`, …) and
   continues to reject every process, network, and filesystem capability. This
   removes an artificial failure mode without weakening isolation.
   The historical (legacy) policy is still evaluated **offline** on the identical
   generated source, so the sensitivity of the result to the policy change is
   measured rather than assumed.
2. **Generalization check (secondary endpoint).** The identical artifact is also
   executed on a fresh, unpublished instance of the same family and level, with
   no additional provider call. This separates genuine algorithmic construction
   from answer hardcoding. The prompt states, identically in every arm, that the
   program may be executed on other instances.

Isolation is unchanged: bubblewrap with an empty network namespace, read-only
host mount, one writable per-case directory, `python -I`, and CPU / address-space
/ file-size / file-descriptor limits. Sandbox unavailability aborts the run
rather than degrading isolation.

---

## 5. Outcome taxonomy

Each session receives exactly one terminal stage, in order:

1. `PROVIDER_FAILURE`
2. `EXTRACTION_EMPTY`
3. `SOURCE_SYNTAX`
4. `SOURCE_QUALIFICATION`
5. `EXECUTION` (runtime failure or timeout)
6. `OUTPUT_SCHEMA`
7. `CRYPTOGRAPHIC_PREDICATE`
8. `EVIDENCE_INTEGRITY`
9. `SUCCESS`

`terminal_success = 1` only at stage 9. A source-qualification failure is never
described as a cryptographic failure. This repairs audit defect D7.

Secondary endpoints: per-stage success; `legacy_would_reject`; generalization
success; source length; output tokens; exact-source agreement across R4
replicates.

---

## 6. Sample size, allocation, and precision

Prospective analysis is in `H1R3_POWER_ANALYSIS.json`, produced by
`h1r3_power.py` before the campaign.

Predeclared design:

| Block | Families | Arms | Instances per family | Sessions |
|---|---|---|---:|---:|
| L3 primary | 2 | R0, R1, R2 | 64 | 384 |
| L1 ceiling anchor | 2 | R0, R1, R2 | 32 | 192 |
| L2 ladder anchor | 2 | R0, R1, R2 | 32 | 192 |
| L3 noise replicates (R4) | 2 | R0 duplicate ×2 | 16 | 64 |
| L3 C0 abstention | 2 | R0-C0 | 10 | 20 |

Primary analysis set: **L3, pooled over families, n = 128 paired instances per
contrast**.

Justification:

- With **zero** discordant pairs, the exact one-sided 95% upper bound on the
  discordance rate is $1-0.025^{1/N}$. At $N=128$ this is **2.3 pp**, at $N=64$
  it is 4.6 pp. The pooled L3 allocation is sized to make a null result
  informative under an equivalence reading, which the historical 24-pair design
  could not do.
- Under 5% discordance the expected 95% CI half-width is 3.9 pp; under 10% it is
  5.5 pp. Both are inside the 10 pp margin.
- Power against a *superiority* alternative is deliberately not the sizing
  criterion, because calibration showed ceiling performance. Exact-McNemar power
  at $N=128$ against a 10-vs-2 pp harm is 0.71; against 5-vs-1 pp it is 0.31.
  This is disclosed rather than hidden.
- Allocation is unequal across levels on purpose: L3 receives twice the instances
  because it is the only level at which calibration observed any failure, and
  because the primary estimand is defined at L3. L1 and L2 are anchors for the
  complexity-interaction analysis, not primary.

Seeds are drawn from a fresh range disjoint from every historical study
(`5001+`, `6001+`, `7001+` used for calibration; confirmatory uses `10001–10064`
and `20001–20032`). No previously observed instance is reused.

---

## 7. Exploratory calibration (reported separately, never pooled)

46 sessions on seeds 5001–5002, plus 10 sanity sessions on seed 7001.

Observed: 44/46 and 10/10 terminal success; one ECDSA L1/R2 arithmetic error
(`k` correct, `d` wrong); one ECDSA L3/R0 syntax error; ladder produced no
difficulty gradient; exact-duplicate prompts produced **distinct** programs, so
the provider is stochastic but outcome-level ceiling hides it; all 34 replayed
artifacts generalized to fresh instances.

Calibration determined the *allocation* (more instances at L3) and the
*interpretation* (precision study rather than superiority test). It did not
determine the hypothesis, the margin, or the primary estimand.

An earlier calibration attempt was aborted after 9 sessions because the sandbox
passed a relative path to `bwrap`; the raw record is retained under
`runs/calibration_aborted_harness_path_bug/` and is classified
`HARNESS_INVALID`, excluded from all analysis.

---

## 8. Analysis plan (frozen)

**Primary.** For each contrast $A \in \{R1, R2\}$ at L3, pooled over families:

- paired risk difference $\hat\tau_A$ with a 95% paired percentile bootstrap
  interval over instances (20,000 resamples, seed 20261019);
- exact two-sided McNemar on discordant counts, Holm-adjusted across the two
  contrasts;
- if the discordant count is zero, report the exact one-sided 95% upper bound on
  the discordance rate instead of a degenerate interval.

**Decision rules (fixed in advance).**

Convention: $\tau_A = P(Y^{A}=1) - P(Y^{R0}=1)$, so positive means the treatment
arm completed more often.

| Condition | Reported conclusion |
|---|---|
| 95% CI fully inside $[-\delta, +\delta]$ | `EQUIVALENT_WITHIN_MARGIN` (bounded non-inferiority at $\delta=0.10$) |
| 95% CI lower bound $> \delta$ | `MEANINGFULLY_BETTER_THAN_REFERENCE` |
| 95% CI upper bound $< -\delta$ | `MEANINGFULLY_WORSE_THAN_REFERENCE` |
| otherwise | `INCONCLUSIVE` |

A non-significant McNemar test is never reported as equivalence. Equivalence is
reported only from the interval rule above.

**Secondary (predeclared, no alpha).**

- family-stratified estimates;
- per-stage discordance tables (which stage, if any, moves);
- legacy-policy sensitivity: how many successes would have been lost under the
  historical import policy, by arm;
- generalization success by arm;
- exact-duplicate replicate agreement (outcome and source-level);
- representation × complexity interaction via a cluster-robust logistic model,
  explicitly descriptive.

**Denominator rules.** Every scheduled session is retained. `PROVIDER_FAILURE`
and `EXTRACTION_EMPTY` are reported but do not enter the paired denominator
(no observation exists). All other stages enter the denominator as failures.
This rule is fixed before execution.

---

## 9. Scope of inference

Established if the study succeeds:

- the direction and magnitude of the effect of these two representation changes on
  verified exploit completion, for two synthetic zero-query recovery families at
  three observation-complexity levels, one model route, one execution contract;
- which *stage* any effect acts on;
- whether the historical `hashlib` failures were policy artefacts.

Not established, by construction:

- generalisation to other models, providers, or interactive oracle tasks;
- that representation cannot matter for cryptographic tasks the model cannot
  already solve reliably;
- that zero discordance implies zero effect at any difficulty beyond the tested
  ceiling;
- immutable backend model identity (the provider returns a route name, not a
  proof of weights);
- novelty. A formatting effect alone is not a security finding. A security
  finding would require a demonstrated consequence such as a change in which
  exploits are *attributable*, not merely which are *emitted*.

---

## 10. Integrity constraints

- No historical result, denominator, lock, or manuscript file is modified.
- No retries, seed replacement, adaptive stopping, or paid fallback.
- The confirmatory schedule is generated once from a frozen seed and its hash is
  recorded before the first call.
- Implementation hashes for every `h1r3_*.py` file are recorded in the run
  manifest.
- Raw prompts, raw provider responses, generated source, execution traces,
  candidate outputs, reference verdicts, and blind-validator decisions are all
  retained per session.
