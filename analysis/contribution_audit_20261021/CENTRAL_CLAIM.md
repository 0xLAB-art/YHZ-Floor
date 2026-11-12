# Central contribution — audit-bounded formulation

**Date:** 2026-10-21
**Derived from:** `SYNTHESIS_MATRIX.json` (claims C1–C5), the three wave-1 analyses,
and two independent full-text prior-work assessments of ABC (NeurIPS 2025 D&B) and
AgentSuite (ICML 2026). Every wave-1 number below was independently reproduced by
`root_verify.py` (43/43 checks) from the frozen records.

The manuscript was **not** modified by this audit. Everything below is a proposal.

---

## 1. The finding that should carry the paper

The strongest result is not the attribution machinery. It is the **artifact-level
admission counterfactual**, because it is the only result in the program that is
both (a) quantitatively large and (b) different in kind from what the two closest
prior works report.

> On 128 matched L3 instances with the program bytes and the historical
> cryptographic outcomes held fixed, changing only the source-admission rule moves
> the apparent R2−R0 representation contrast from **−0.78 pp** (125/128 versus
> 124/128) to **−32.81 pp** (100/128 versus 58/128). The policy change is
> **−32.03 pp**; 50 instances shift in the negative direction, 9 in the positive
> direction, and 69 do not change. The preregistered L3 verdict is unaffected:
> both contrasts remain `EQUIVALENT_WITHIN_MARGIN` with Holm-adjusted p = 1.000.

Two independent controls make this more than an arithmetic restatement:

- **The effect survives its strongest deflation.** A conservative transform that
  removes only eligible, whole, top-level unused import statements — leaving every
  mixed, used, nested, wildcard, aliased and dynamically-referenced import intact —
  was applied to 128 derivatives. All 128 produced byte-identical parsed JSON output
  under fresh execution. 104 then qualified under the legacy policy and **98 of
  those are cryptographically correct**. The shift does not disappear when unused
  imports are removed.
- **It is not an artefact of the qualifier's own classification.** The original
  contract's `unused_imports` test is not a semantic classifier; it subtracts AST
  name spellings from imported members, so `from typing import Tuple` can be
  reported unused while `Tuple[int, int]` is evaluated. Runtime tracing observed a
  genuine load of the imported object in **100 of the 101** sources with static
  legacy-disallowed references.

And one boundary that must be stated, because it changes the interpretation:

> **The legacy policy was legitimate under its own prompt.** All 205 of its import
> rejects concern modules the frozen prompt explicitly permitted. Under the v3
> contract actually in force, **zero of 852** sources were rejected for imports.
> The three pre-output failures are one syntax error and two runtime errors. These
> 205 programs are therefore **not** task-contract violations, and the result is
> **evaluator-policy dependence**, not evaluator error.

That last point is not a weakness to be minimised. It is the finding. It says that
even when every admission rule is legitimate under the contract that declared it,
swapping the rule on byte-identical programs changes reported capability by up to
47.7% and changes the apparent ordering of representation arms by up to 32 points.
A benchmark that reports a capability number without stating its admission rule
cannot tell a reader which part of the number is the agent's.

---

## 2. The defensible central claim

> **We give a controlled evaluation procedure for security-agent attack evaluation
> that separates three things a single success label conflates — whether the agent
> constructed a correct attack, whether the evaluator admitted that program, and
> whether the accepted outcome is attributable to a specific execution — and we
> quantify the middle one with an artifact-level counterfactual: re-admitting
> byte-identical programs under a changed admission rule moves an apparent
> representation contrast by up to 32 percentage points, with the program bytes and
> the cryptographic outcomes held fixed.**

Classification, after both prior-work assessments: **a domain-specific
instantiation with a new measurement instrument and a new evidence contract, not a
new general principle.**

### What the claim rests on, and what it explicitly does not

| | Status |
|---|---|
| Controlled three-way separation with an independent cryptographic predicate | **Supported.** 852 sessions, stage-resolved denominators, independent predicate, 852/852 reference-replay agreement. |
| Artifact-level admission counterfactual with paired instance-level inference | **Supported.** −32.03 pp over 128 matched instances; survives conservative cleanup; preregistered verdict unchanged. |
| Claim-specific attribution contract with bounded mechanized evidence | **Supported as an application.** 274 bundles, 1,096 invocations, zero disagreements; 11,256 evaluations of 1,407 mutants, no observed soundness violation; in-toto 21/22 then 22/22. |
| Release-evidence rubric (0/6 satisfy all nine fields) | **Supported as documentary evidence only.** It is not external executable validation and must not be described as such. |
| A new general principle about benchmark validity | **Not supported.** ABC owns the validity taxonomy (App. A, p. 17) and the "flaws distort performance" finding with a security case study (abstract p. 1; §5.3 pp. 9–10); AgentSuite owns the component-wise decomposition (Table 2, p. 3) and the large-scale version of the same finding (5,086 tasks, p. 2; 60% of ACEBench rankings altered, p. 2; 18 of 30 models shifted, App. E p. 20). |
| A causal capability effect of representation | **Not supported.** Representation arms are not model comparisons; the legacy contrast is an algebraic gate on fixed programs, not a fresh policy deployment; the effect is confined to ECDSA at L1/L2 and ranges −21.88 to −42.19 pp by family weighting at L3. |
| Prevalence of attribution failure, or superiority over a provenance framework | **Not supported.** The attribution corpora are constructed cases, not empirical attacks; IAR-C had already been evaluated during calibration. |

---

## 3. Where the paper currently over- or under-claims

The attribution audit found two statements in the current manuscript that its own
recomputed evidence does not support as written. These need correcting regardless
of how the contribution is framed.

**`main_sections/10_discussion.tex`, the HEB-1 paragraph.** It currently says
"composition-blind and authenticity-blind baselines". The HEB1 systems are the
**schema/declaration** and **hash-integrity** baselines; none of HEB1's three
systems authenticates records, so the current wording implies authentication is the
controlled contrast in HEB1 when it is not. The same paragraph's
"join-only checks false-rejected 14/16 honest partial claims" is a comparative
false-reject rate computed against a validator whose contract emits only full
attribution: it rejected fourteen lower-level requests because it does not support
them. That is a **functionality difference**, not a comparative false reject.

Suggested replacement, retaining only reproduced evidence:

> On 36 constructed HEB1 heldout defect bundles, the schema/declaration and
> hash-integrity baselines emitted unsupported full attribution in all cases; the
> join validator emitted none. In IAR-C's preserved corpus, join-only,
> signature-only, and combined checks promoted 10/28, 14/28, and 0/28
> attack-family cases. IAR-C used a separately written generator and adjudicator
> but had already evaluated the same cases during calibration. On the separate
> IAR-B heldout corpus the corresponding counts were 16/44, 28/44, and 0/44. The
> combined validator accepted all sixteen honest IAR-C requests at their
> supported claim level. V2's rejection of fourteen lower-level requests reflects
> its full-attribution-only contract. These constructed cases demonstrate
> complementary authenticity and claim-specific consistency requirements under the
> stated trust model.

**`main_sections/11_limits.tex`, the reproducibility paragraph.** It should now
name the newly recomputable set (the 74-session census with its per-task split, the
fixed-executor 12/12 with its per-condition medians, and the study's timing,
cache-timing, policy-matrix, wire-edit, hybrid-configuration and safety-probe
figures) and should state the boundary this audit established: the legacy import
policy is a counterfactual policy, and the 205 programs it rejects were permitted
by the frozen prompt.

---

## 4. Why this answers the reviewer's objection

The reviewer was right that the artifact fix strengthens the reliability of the
evidence without widening the contribution. That remains true. What this audit
changes is that the contribution can now be **stated accurately and positioned**,
instead of being either under-claimed (a local case study) or over-claimed (a
general discovery).

The defensible statement is narrow and specific: *the unit of analysis for
evaluation auditing is the submitted program and its execution evidence, not the
benchmark task; and on that unit, admission policy is a first-order determinant of
reported capability that can be measured with a byte-fixed counterfactual.* ABC
and AgentSuite audit the benchmark. This work audits what a submitted program did,
whether it was admitted, and whether the acceptance is attributable — and it shows,
with a paired counterfactual, how much of a reported number the evaluator's own
rule determines.

That is a real contribution, it is not ABC's or AgentSuite's, and it is honest
about being demonstrated once.