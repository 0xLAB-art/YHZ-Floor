# The smallest validation study that would settle the contribution

**Date:** 2026-10-21
**Status:** DESIGN ONLY — not run, not started. No hosted model call, no benchmark
installation, no new agent cohort is authorised by this document.

---

## 1. The decision this study settles

Both independent prior-work assessments converge on the same gap, and it is not a
gap in our evidence. It is a gap in *generality*:

- **ABC** already varies the evaluation rule on fixed agent artifacts (App. G,
  p. 32; §5.3/Fig. 6, pp. 9–10) and reports the resulting score movement on a
  security benchmark.
- **AgentSuite** already shows that evaluation-side changes move reported
  capability, with a null baseline and a single-run caveat (p. 8).

What neither does is apply a **changed rule to byte-identical programs and measure
the paired instance-level change**. That is the single mechanic our contribution
rests on, and it has been demonstrated on one harness.

So the question this study answers is narrow and binary:

> **Does the admission-policy effect reproduce on a benchmark we did not build?**

- If **yes**, the central claim upgrades from *a local measurement technique* to
  *a portable evaluation method*, and the paper's contribution statement becomes
  defensible in general form.
- If **no**, the honest statement is that the effect is a property of our
  harness's historical import policy, the paper's contribution stays a
  cryptographic case study, and the manuscript should say exactly that.

Either outcome is publishable. What is not publishable is leaving the question
open while claiming generality.

---

## 2. Design

**Prefer a benchmark with publicly retained agent submissions and a documented
admission rule.** Candidates, in order of preference:

1. **CVE-Bench** artifacts (ABC's own security case study, §5.3, pp. 9–10) — the
   retrieved submissions and the fixed evaluator make the two-rule comparison
   immediate, and it maximises comparability with ABC's headline security result.
2. **SWE-bench Verified** model submissions, where the container/network policy is
   an explicit, documented admission rule.
3. **KernelBench** generations released by Lange et al., which ABC already re-scored
   (F.6, pp. 31–32).

**Protocol.**

1. Freeze the candidate artifacts and the reference task instances before
   inspecting any outcome. Record SHA-256 for every artifact.
2. Implement the benchmark's admission rule **as documented**, and a second,
   deliberately weaker variant that differs in exactly one declared dimension
   (for example: an allow-list of permitted imports, or a resource ceiling).
3. For each candidate, decide admission under **both** rules. Both decisions are
   made from the artifact bytes alone; no candidate is re-executed to decide
   admission, and no model is called.
4. Evaluate each admitted candidate under the benchmark's **own unchanged**
   scorer. This is the part that needs the benchmark's environment; it is where
   the compute goes, and it is the same in both arms.
5. Report, per matched candidate:
   - the paired outcome difference between the two admission rules;
   - the per-instance shift census (negative / positive / unchanged);
   - a paired interval at the instance level and, if a representation-like factor
     is available, the interaction with an equivalence margin;
   - the McNemar discordance counts.

**Controls.**

- A **null baseline** in the style of AgentSuite's random-removal control (p. 8):
  apply a rule change that is semantically vacuous (for example, re-ordering an
   allow-list) and show the paired difference is zero. If a vacuous rule change
  produces a shift, the measurement instrument is wrong, not the benchmark.
- A **shrinkage control**: re-run the same comparison with a rule change
  restricted to candidates that the original rule rejected for a *single* declared
  reason, so the mechanism is identified rather than pooled.
- Report the **denominator discipline** ABC's checklist requires (R.1–R.14,
  §4.3, p. 7): which artifacts were admitted, which were excluded, and why.

**Pre-registration.** Fix the primary contrast, the exclusion rules, the
equivalence margin and the interval method **before** looking at outcomes. The
L3 result of this audit is the model: a preregistered margin with the verdict
reproduced exactly, and the new contrasts marked exploratory.

---

## 3. Falsification criteria

The contribution claim is **falsified** if any of the following holds.

| # | Criterion | Consequence |
|---|---|---|
| F1 | The paired admission-rule effect does not reproduce on the second benchmark (interval spans zero, or the shift census is dominated by positive shifts). | The effect is a property of our harness's legacy policy. The paper must report it as such and drop the generality claim. |
| F2 | The **vacuous-rule null baseline** produces a non-zero paired difference. | The measurement instrument is invalid. The counterfactual claim is withdrawn entirely, including the −32.03 pp figure, which would then be an artefact of the harness rather than a property of the programs. |
| F3 | The effect reproduces but **disappears when unused or unnecessary artifacts are cleaned**, on the second benchmark as well as on ours. | The effect is a benign-hygiene artefact, not evaluator-policy dependence. The claim reduces to "clean your imports", which is not a contribution. |
| F4 | The admission-rule effect reproduces, but the **preregistered equivalence verdict for the primary representation contrast changes** under it. | The paper's central capability result is contingent on an unstated evaluator rule. The framing must become "reported equivalence is rule-relative", and the L3 equivalence claim must be reported under both rules. |

F2 and F3 are the serious ones, and **our own evidence already speaks to both**:
the conservative cleanup control (128/128 identical outputs, 104 newly qualifying,
98 correct) and the 100-of-101 observed-runtime-load finding are the reason we
believe F2 and F3 do not hold here. The second benchmark is what would show that
those controls generalise rather than being local facts about our harness.

---

## 4. What this study does **not** need

- **No hosted model.** Every artifact is already generated; only the rule and the
  scorer change. This is the same discipline as the audit's own derivative
  execution.
- **No new agent cohort.** No model is asked to attack anything.
- **No claim of superiority over ABC or AgentSuite.** Their benchmarks and ours
  are different systems with different task contracts; there is no head-to-head
  and none is possible. The study tests *transferability of our own measured
  effect*, nothing else.
- **No new general principle.** If the effect transfers, what transfers is a
  *measurement procedure*, and the paper should say so.

---

## 5. Cost and sequence

| Stage | Work | Cost |
|---|---|---|
| S0 | Artifact selection and freeze; write the admission-rule pair and the vacuous null variant; preregister the contrasts, exclusions, margin and interval method. | Low. No compute. **Do this first.** |
| S1 | Implement the two admission decisions and the null variant; run the admission census only (no scoring). | Low. Minutes. |
| S2 | Score admitted candidates under the benchmark's unchanged scorer, both arms. | The only real cost. Dominated by environment setup, not inference. |
| S3 | Paired analysis, interval, McNemar, null-baseline check, shrinkage control. | Low. |
| S4 | Falsification table against F1–F4; update the contribution statement accordingly. | Low. |

**S0–S1 require no benchmark execution and no model.** If S1 shows the two rules
admit materially different candidate sets, the study is worth running. If they do
not, it is not, and that is itself worth knowing — it would bound our own
contribution before a reviewer does.

---

## 6. What to write in the paper in the meantime

The paper does not need to wait for this study. It needs the contribution stated
at the level the evidence supports, and the boundary stated plainly. Concretely,
`CENTRAL_CLAIM.md` §2 gives the claim as it should be written, and §3 gives the
two manuscript passages that must be corrected on their own evidence regardless of
framing: the HEB-1 baseline naming and the 14/16 comparative false-reject rate.

Those corrections are the ones a careful reviewer would make, and making them
before submission is strictly better than having them made.