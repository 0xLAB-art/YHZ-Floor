# Prior-work assessment — AgentSuite (ICML 2026) vs. the five candidate contributions

Worker: `agentsuite_prior` · Date: 2026-10-21 · Audit root: `sp2027/analysis/contribution_audit_20261021/`

## 0. Source identity, coverage, and what this assessment is not

**Comparator identity (verified against the snapshot, not from a citation).**
`sp2027/analysis/contribution_audit_20261021/sources/agentsuite_icml2026.pdf`
SHA-256 `2c7c91f3aab411df69d8ae2255dab111cf3109547e36ed12c8c38923a1021dce`, which matches
`sources/SOURCES.md`. `pdfinfo` reports 20 pages, title *"AgentSuite: Toward More Reliable Agent
Evaluation with a Component-Based Benchmark Auditing Pipeline"*, subject *"Proceedings of the
International Conference on Machine Learning 2026"*, authors Suh, Ji, Lee, Khare, Khan, Kim, Zhang,
Srinivasan, Belcak, Diao, Molchanov, Lin, Dong. The title page (PDF p.1) prints *"Proceedings of the
43rd International Conference on Machine Learning, Seoul, South Korea. PMLR 306, 2026"* and the
GitHub release `github.com/Agent-Suite/AgentSuite` (p.1). Primary links: PMLR landing page
<https://proceedings.mlr.press/v306/suh26a.html>; PDF
<https://raw.githubusercontent.com/mlresearch/v306/main/assets/suh26a/suh26a.pdf>.

**Coverage actually inspected.** I read the *complete* extracted text of all **20 physical PDF
pages** — main body pp.1–9 (Abstract, Sec. 1, Sec. 2 incl. Tables 1–2, Sec. 3 incl. Eqs. 1–3 and
Figures 2, Sec. 4 incl. Tables 3–6 and Figures 3–5, Sec. 5, Sec. 6, Impact Statement), references
pp.10–11, and Appendices A (p.12), B.1/B.2 (p.13), Table 7 (p.14), C.1/C.2 + Table 8 (p.15),
D.1–D.2 prompt templates (pp.15–17), D.3 (p.18), D.4 + Table 9 and D.5 + Table 10 (p.19), and
Appendix E + Table 11 (p.20). Printed page numbers equal physical PDF pages throughout, so all
anchors below are usable as "PDF p.N". I also ran term searches over the whole 20-page text; the
zero-hit terms are reported explicitly in §4.

**Physical page mapping note.** `pdftotext -layout` output splits into 19 form-feed blocks because
one page boundary is not emitted as a form feed; the printed folios (1…20) confirm the 1:1
physical-to-printed mapping, so page anchors below are unambiguous.

**What this document is.** An independent prior-work assessment of *novelty and overlap only*.
It is **not** a validation of our experiments, and it is **not** a head-to-head comparison: the
AgentSuite benchmarks (BFCL V3/V4, ACEBench, CFB, DrafterBench, τ-bench, τ²-bench, NexusBench;
pp.2, 6, 7, 13) and the ACTS-Attack artifacts are different systems, and I ran no benchmark, no
released COBA code, and no hosted model. Where I say "AgentSuite would/would not have produced X",
that is an inference from the *published design* (Sec. 3.1–3.4, p.4–5), and I label it as such.
The six-release documentary audit in our work is a **documentary** audit and is **not** external
executable validation; I do not treat it as a differentiator against AgentSuite.

**Prior assessment status.** Per the brief, I did not treat any earlier novelty-GO document as
established fact; this assessment was formed from the primary source plus the current manuscript
text (`sp2027/paper/capability_revision_20261020/main_sections/01_intro.tex`, `04_capability.tex`,
`04_verification.tex`, `08_h1r3.tex`, `09_audit.tex`, `11_limits.tex`).

## 1. Executive verdict

**The evidence does not support a general methodological contribution *over AgentSuite*.** It
supports a **domain-specific instrument** for security-agent attack evaluation whose *mechanism*
differs from COBA in three identifiable places, while the *general moral* of each candidate is
already covered by AgentSuite and/or ABC.

| ID | Candidate (short) | Novelty type | Overlap with AgentSuite | Would COBA have found our finding? |
|---|---|---|---|---|
| C1 | Separate correctness / source admission / execution attribution | `domain_application` | **Strong, structural** — component-wise validity decomposition and an Evaluation-System defect category already exist | **No** (different unit of analysis), but the *template* is COBA's |
| C2 | Paired representation contrasts + admission rule on unchanged programs | `measurement_technique` | **Partial, conceptual** — "evaluation-side change moves reported capability" is established, incl. a null baseline | **No** (no execution, no byte-fixed counterfactual) |
| C3 | Independent cryptographic predicates + full fresh program replay | `domain_application` | **None mechanistically** (execution is explicitly *related work* for them, p.12) | **No** |
| C4 | Authenticated evidence + claim-specific joins for attribution | `domain_application` | **None** (no provenance/attribution content in 20 pages) | **No** |
| C5 | Integrated security-specific method vs. generic "flaws distort performance" | `domain_application` | **Direct and strong** — this *is* AgentSuite's headline result | **Partly yes** for the generic half |

Three statements I want on the record because they are the load-bearing ones:

1. **C1 and C5 are largely anticipated.** AgentSuite's contribution (1) is a *component-based issue
   taxonomy* (p.1, p.2, Table 2, p.3) and its contribution (3) is a *large-scale empirical analysis
   of benchmark flaws and their impact on agent evaluation* (p.1; Sec. 4.6, p.8). Our C1 template
   ("localize the source of measurement invalidity by separating evaluation components") and C5's
   generic half ("benchmark flaws distort performance") are the same two ideas in a security
   setting. C1's third class — *execution attribution* — and C4 are outside AgentSuite entirely.
2. **C2 and C3 are where our mechanics genuinely differ**, and the difference is in *kind* (an
   executable, byte-fixed counterfactual with an independent predicate) rather than domain: COBA
   never executes a candidate program, and Appendix A (p.12) places execution-based matching
   (SWE-Bench unit tests, SQL execution matching) in *related work*, describing it as task-specific
   and not generalizable — i.e. it is a deliberate non-goal for them, not an oversight.
3. **The correct framing is therefore "domain-specific application with a new measurement
   instrument and a new evidence contract", not "new general principle".** AgentSuite already
   owns the general principle; we own a security-attack instantiation whose estimator (byte-fixed
   admission counterfactual) and whose evidence layer (claim-specific attribution contract) have
   no counterpart in COBA.

## 2. What AgentSuite's pipeline actually does (the overlap baseline)

To be precise about "the closer comparator for the auditing half", this is the mechanism in its
own terms:

- **Unit of analysis = the benchmark task, judged as a static artifact.** Standardized
  representation `T = ⟨U, E, G, V⟩` = User, Environment, Ground Truth, Evaluation System
  (Sec. 3.1, Eq. 1, **p.4**). The annotation guideline requires "clear, observable evidence of a
  **benchmark-intrinsic** validity issue" (App. B.1, **p.13**) — the agent's own output is not the
  object of judgment.
- **Two stages.** (1) Deterministic structural filtering for explicit schema/role violations
  (Sec. 3.2, **p.4**); (2) taxonomy-guided LLM judgment producing `φ(T) → (y, c, r)` — flawed?,
  category, rationale (Sec. 3.1 Eq. 2 / Sec. 3.3, **pp.4–5**). Optional third stage: adversarial
  rebuttal by a second agent that may overturn a flag under three adjudication principles —
  Workaround, Semantic Equivalence, Derivability (Sec. 3.4, Eq. 3, **p.5**; prompt in App. D.3,
  **p.18**).
- **Component-aligned issue taxonomy (Table 2, p.3).** User: ambiguous instruction, user role
  confusion. Environment: incorrect tool-call responses, insufficient toolset, misleading tool
  design, incorrect system prompt. **Evaluation System: too lenient, too strict.** Ground Truth:
  malformed tool calls, incorrect tool calls, redundant/ungrounded tool calls.
- **Evidence base.** 5,086 tasks across six benchmarks (p.2), five graduate annotators,
  Cohen's κ = 0.824 (App. B.1, p.13), balanced-subset validation (10 %, min 30 tasks) and
  post-hoc validation of every flagged task (Sec. 4.1, **p.5**; Table 3, **p.6**); judge
  F1 0.791–0.874 (p.1, Table 3, p.6); post-hoc validation accuracy 72.1–92.0 % (Table 3, p.6);
  generalization to BFCL V4 and NexusBench (Table 4, **p.7**); judge-robustness ablation
  (Table 9, p.19); FP/FN failure taxonomy (Table 10, p.19); repair/retention analysis
  (Table 8, p.15).
- **Impact analysis.** Four issue-impact categories — inflation, deflation, unsolvable, noise
  (Sec. 4.6, **p.8**); ACEBench top-12 before/after cleaning (Table 6, p.8) with 18/30 models
  shifting (App. E, p.20); a **random-removal null baseline** over 100 trials: Kendall's τ = 0.871
  vs 0.960 (95 % CI 0.935–0.981), pairwise flip rate 5.75 % vs 1.50 % (p.8). And an explicit
  caveat: "Table 6 is based on a **single evaluation run per model** due to computational cost"
  (p.8).

This matters for C2 in particular: AgentSuite already knows how to show that an evaluation-side
change (here, task removal) moves reported capability, and already supplies the null-baseline
discipline and the single-run caveat that our own analysis would need.

## 3. Candidate-by-candidate assessment

### C1 — Controlled separation of *attack correctness*, *source admission*, and *execution attribution*

**Overlap (structural, strong).** AgentSuite's central methodological move is exactly a
*separation of measurement-invalidity sources by component*: `T = ⟨U,E,G,V⟩` (p.4, Eq. 1) and the
component-aligned taxonomy (Table 2, p.3). Two sub-parts of C1 are covered in substance:
- "evaluation criteria unfairly penalize semantically correct answers for minor deviations"
  (Evaluation System → *Too strict*, Table 2, p.3) is COBA's static counterpart of our
  *source admission* separation — a rule that rejects a correct artifact.
- "Ground-truth calls select the wrong function or parameters" (Table 2, p.3) is COBA's static
  counterpart of our *correctness* separation.
- Their impact categorization (inflation / deflation / unsolvable / noise, p.8) is an
  *interpretation layer* over the same separation we perform, and it is more developed than ours.

**Distinction (kind, on one axis only).** The three axes differ on the *object* being separated:
COBA separates **which benchmark component is broken** (design-time artifact); we separate **which
stage of the run produced the failure** (artifact correctness → source qualification → execution
evidence) for **agent-produced programs** in a security setting. Two consequences follow.
(a) COBA's unit of judgment is fixed by the annotation guideline (App. B.1, p.13: issues must be
"benchmark-intrinsic"); a program that is cryptographically correct but was rejected by an
import policy is, for COBA, a property of the *evaluation component* only if the rejection is
visible in the static task definition — in our case it is a property of the submitted source
bytes. (b) **Execution attribution has no counterpart in the four components**: it is a fifth,
runtime-evidence axis. COBA's *Ground Truth* component is a design-time reference trajectory
(Fig. 1, p.2), not runtime evidence about a specific run.

**Uncertainty boundary.** Absence claim: "no runtime-evidence/attribution component" is stated over
the full 20 pages; the terms *provenance*, *attribution*, *admission*, *replay*, *counterfactual*,
*signature* (as cryptographic), *security*, *attack* occur **0 times** in the extracted text, and
*execution* occurs once, in an Appendix-A related-work sentence (p.12). I did not inspect the
released AgentSuite repository, so I cannot exclude that the released code contains un-papered
runtime checks; the claim is about the paper's pipeline as specified in Sec. 3.

**Would COBA have produced the same finding?** **No.** COBA would produce a *task-side* audit of
our task cards (e.g. an "Evaluation System" label for a mis-specified oracle or an
underspecified task), but it cannot produce the three-way separation *over runs*, because (i) it
never executes the submitted program, so it cannot establish that a program was cryptographically
correct, and (ii) it has no axis for evidence binding a verdict to a specific execution. Note the
partial overlap direction: a COBA-style audit of our harness *could* label our admission rule as
an evaluation-component defect — but as a static label attached to the task, not as a byte-fixed
counterfactual on 852 sessions. So C1 is a **domain application with one genuinely new axis
(attribution)**, not a new general decomposition principle.

### C2 — Paired representation contrasts under a common executor, then a changed admission rule on unchanged programs

**Overlap (conceptual, partial).** AgentSuite already demonstrates that *evaluation-side choices
change reported capability*, with disciplined controls: before/after cleaning on ACEBench
(Table 6, p.8; full leaderboard App. E, p.20), a random-removal null (Kendall's τ 0.871 vs 0.960,
flip rate 5.75 % vs 1.50 %, p.8), and the single-run-per-model caveat (p.8). They also report
that a trivial "do-nothing" model passes 38 % of τ-bench tasks (p.3, p.13) — a direct instance of
*evaluation criteria admitting wrong artifacts*. So the general claim "an evaluator's rule can
manufacture or destroy reported success" is **anticipated by AgentSuite**, and our own related-work
section already says as much (`02_related.tex`: "These works already establish that evaluator
behavior can distort measured capability").

**Distinction (kind, in the estimator).** The two designs measure different contrasts.
- AgentSuite varies the **task set** and re-runs models → a *between-set* comparison whose unit is
  (model, task) and whose output is a leaderboard.
- Ours varies **one admission rule while holding the generated program bytes fixed** → a
  *within-artifact* counterfactual, paired at the instance level, with a preregistered ±10 pp
  equivalence margin for the representation contrasts and a rejection rate of 6.2 %–47.7 % across
  arms (Fig. 2 and `04_capability.tex`, "Evaluator-policy sensitivity"). Program bytes are fixed
  *between policy evaluations*; they are not fixed across representation arms.
This is a genuine estimator difference, not a relabelling: no artifact-level counterfactual of
this shape exists in AgentSuite, and COBA's design cannot produce one (no execution, no
per-artifact rule re-application). It is also a *narrower* claim than AgentSuite's: we claim
nothing about model rankings (explicitly, `08_h1r3.tex`, `11_limits.tex`).

**Would COBA have produced the same finding?** **No**, for the byte-fixed part — COBA has no
mechanism to execute a program and re-decide it under an alternative rule. But note the sharp
asymmetry: **if we had framed our result as "removing flawed tasks changes reported capability /
rankings", AgentSuite would have produced that finding first, with a much larger evidence base
(5,086 tasks, 30 models, expert-validated F1 0.791–0.874) than our 852 sessions and one route.**
Our defensible framing is the narrow one we already use.

**Uncertainty boundary.** The "no artifact-level counterfactual" claim rests on the pipeline
description in Sec. 3.1–3.4 (pp.4–5) plus the full-text term search (no *replay*, *counterfactual*);
it is an inference about the *published* pipeline, not an executed test of the released code.

### C3 — Independent cryptographic predicates and full fresh program replay against retained public inputs

**Overlap (essentially none, mechanistically).** COBA's two stages are rule-based structural
filtering and LLM judgment (Sec. 3.2–3.3, p.4); the pipeline **never executes a candidate program
and never recomputes a task predicate**. Execution-based checking is named in Appendix A (p.12) as
*related work* — "unit-test augmentation in SWE-Bench … or execution-based matching in SQL
benchmarks … rely on deterministic semantics and executable environments, limiting their
applicability beyond narrow domains" — i.e. it is a stated non-goal. The closest conceptual
neighbour in AgentSuite is their observation that BFCL V4 ground truths "may additionally become
stale as external information changes, highlighting a maintenance challenge" (p.8) — a *staleness*
observation without any replay mechanism. Our replay of admitted programs against retained public
inputs (852/852 reference-replay agreement; the staged full candidate re-executing 851 admitted
programs, per `11_limits.tex`) is a mechanism COBA does not have.

**Distinction (kind).** Ours introduces executable ground truth into a setting whose artifact is a
*program* and whose ground truth is a *cryptographic relation*; theirs is explicitly designed
around static artifacts and semantic judging. This is the candidate with the largest *mechanistic*
distance from the comparator.

**Would COBA have produced the same finding?** **No** — it has no execution stage; and even its
structural filter is aimed at *tool-call schemas*, not at program source semantics.

**But: do not oversell it as a general method.** Execution-based validation of agent outputs and
replay-based verification are long-established ideas in the neighbouring literature (SWE-Bench unit
tests, SQL execution matching — the very papers AgentSuite cites on p.12). What is new here is
their application to *security attack programs* with an *independent cryptographic predicate* and
to a *benchmark of our own*, plus the honesty discipline that the replay is of *retained* programs
and is explicitly **not** fresh model generation (stated in `01_intro.tex` and `11_limits.tex`).
Classification: `domain_application` / measurement instrument — *not* `general_method`.

### C4 — Complementarity of authenticated evidence and claim-specific joins in bounded adversarial attribution tests

**Overlap (none).** Across all 20 pages there is no content on runtime evidence binding: *provenance*
0 hits, *attribution* 0 hits, *signature* (cryptographic) 0 hits, *signed* occurs only as "assigned";
*claim* occurs once and in an unrelated sense. COBA's *Ground Truth* component is a design-time
reference trajectory; the *adversarial rebuttal* stage (Sec. 3.4, p.5; App. D.3, p.18) and the
*issue-guided repair* traces (App. C, p.15) are about **repairing benchmark artifacts**, not about
**binding an observed execution to a claim**. The overlap is at the level of the *goal* (reliable
evaluation), not of mechanism.

**Distinction (kind).** Our C4 is a *claim-specific attribution policy* (observer-signed record over
exact executed bytes and captured stdout + reference-signed recomputation of the task predicate from
private target state, with role authorization, digest agreement, and a replay policy; the claimant's
own `claims` block is excluded from the decision), validated by bounded mechanized testing
(1,407 mutants × 2 readings = 11,256 evaluations, no observed soundness violation), plus live-target
and loopback-ingress exercises against fabricated claims, and an in-toto inspection reproducing
21/22 decisions (22/22 with a shared replay ledger) — see `09_audit.tex`. This is a *policy and its
validation*, not a new signing, logging, or isolation primitive, and the manuscript already says so
(`09_audit.tex`; `02_related.tex`).

**Would COBA have produced the same finding?** **No** — nothing in COBA's component model or
pipeline touches runtime evidence. This is therefore the candidate with the *least* overlap with
the comparator. But note two honest caveats: (i) the *mechanisms* are not ours (in-toto, SLSA are
existing), so C4 is a domain application of established provenance machinery with a new policy and
a new test regime; (ii) our evidence for C4 includes a **documentary** six-release audit
(0/6 satisfy a nine-field rubric) which the brief and `09_audit.tex` both correctly state is **not**
external executable validation — it must not be presented as a benchmark-validation result that
AgentSuite lacks.

### C5 — An integrated security-specific empirical method, rather than generic discovery that benchmark flaws distort performance

**Overlap (direct, strong — this candidate's generic half is AgentSuite's headline).** AgentSuite
states: "Our analysis shows that benchmark flaws are widespread and materially affect evaluation
outcomes" (abstract, p.1); issues affect "on average 27 % of tasks" (p.2); removing flawed tasks
"alters 60 % of the model rankings in ACEBench" (p.1, and 18/30 in App. E, p.20); the pipeline
achieves F1 0.791–0.874 against experts (p.1, Table 3, p.6) and generalizes to unseen benchmarks
(Table 4, p.7). It also already *cites ABC* as the design-level counterpart of this same genre
(App. A, p.12). So the "generic discovery" half of C5 is not ours to claim: it is established,
with stronger evidence than ours, and it is the explicit third contribution of the prior paper
(p.1).

**Distinction (domain, plus two mechanism items).** The security-specific instantiation is not
covered: the 20 pages contain no security or attack content (*security* 0 hits, *attack* 0 hits);
the audited artifacts are agent benchmarks (tool-calling, conversational, function-calling), not
attack programs, and the evidence machinery is absent (C3, C4). Our increment for C5 is therefore
*the integration in the security-attack setting*, not the discovery that benchmark flaws matter.

**Would COBA have produced the same finding?** **Partly yes, for the generic claim** — if we
restated C5 as "benchmark flaws distort performance", COBA would have produced that finding, with a
larger sample. For the *security-specific* integration, no.

## 4. Absence-claim ledger (coverage and confidence)

| Claim | Coverage inspected | Confidence |
|---|---|---|
| COBA never executes candidate programs / recomputes a task predicate | Full text pp.1–20; *execution* appears once, App. A, p.12 | High for the paper; the released code was not run |
| COBA has no provenance/attribution/evidence-binding component | Full text; *provenance*, *attribution*, *signature*, *counterfactual*, *admission* = 0 hits | High |
| COBA has no artifact-level policy counterfactual | Full text; Sec. 3.1–3.4 (pp.4–5) design; no *replay*/*counterfactual* | High for the paper |
| COBA's unit of analysis is the benchmark task, not agent output | Sec. 3.1 (p.4); App. B.1 annotation guideline (p.13) | High |
| COBA's "representation" is the *standardized task representation*, not prompt/encoding manipulation | Sec. 3.1 (p.4) and all 25 occurrences of "represent*" | High |
| COBA's "policy" occurrences refer to benchmark system policies (τ-bench/τ²-bench), not evaluator import policies | all 8 occurrences, pp.3, 12–13 | High |
| COBA's "equivalence" is a rebuttal adjudication principle, not statistical equivalence | Sec. 3.4 (p.5), App. D.3 (p.18) | High |
| COBA contains no security/attack content | Full text; 0 hits for *security*, *attack*, *cryptograph* | High |

**Uncertainty boundary for all rows above:** the assessment is of the *published artifact*. The
released `github.com/Agent-Suite/AgentSuite` code and the benchmark artifacts were not executed or
inspected, and no hosted model was invoked. Every "would have produced" statement is a design
inference, not a measured result, and no such statement is a superiority claim.

## 5. Decisive question, answered explicitly

> *Would AgentSuite's pipeline, applied to our setting, have produced the same finding?*

**Not the same finding — but the same *lesson*, at lower evidentiary strength and higher
generality.** Decomposed:

- C1 (separation over runs, with an attribution axis): **No.** COBA audits the benchmark; ours
  audits agent-produced programs and runtime evidence. The template is COBA's; the unit is ours.
- C2 (byte-fixed admission counterfactual): **No.** Not producible without execution and
  per-artifact re-decision.
- C3 (predicate + full fresh replay): **No.** No execution stage exists; execution is cited as
  related work they deliberately do not generalize (p.12).
- C4 (authenticated evidence + claim-specific joins): **No.** No evidence/provenance content in
  20 pages.
- C5 (generic "flaws distort performance"): **Yes — AgentSuite already has this**, with 5,086
  tasks, expert-validated F1 0.791–0.874, and a measured 18/30 rank shift.

Therefore: **our contribution is a domain-specific application with a new measurement instrument
(C2+C3) and a new evidence contract (C4), not a new general method.** The honest, publishable
formulation is a *security-attack instantiation* of the component-based auditing idea in which the
evaluation unit is extended from the benchmark task to the **submitted program and its execution
evidence** — and the *demonstrable consequence* is that (a) an evaluator's source-admission rule,
applied to already-correct programs, changes reported success by 6.2 %–47.7 % across
representation arms, and (b) the *attribution* of an accepted outcome requires evidence that no
component of the prior taxonomy covers. If the author wants a general-method claim, the evidence
does not currently support it, and the closest prior work would need to be cited as establishing the
general principle.

## 6. Minimal differentiating study design (PROPOSED — NOT RUN)

**Question.** Does a COBA-style audit of our artifacts, given the same task cards and the same
released pipeline, flag the same defects that our executable counterfactual exposes — and can it
produce an artifact-level counterfactual at all?

**Design (single-benchmark, single-judge minimal version).**
1. **Inputs (all from our existing retained artifacts; no new generation, no hosted model beyond
   the judge's own API usage):** the H1-R3 and V4 task cards; the standardized mapping
   `T = ⟨U,E,G,V⟩` for each card; the retained submitted programs; the executor verdicts; the
   import-policy decisions; the attribution-contract corpus.
2. **Arm A (COBA-as-published).** Map our task cards into `T` (the paper says this mapping is
   "the only benchmark-dependent step", p.4), then run the released COBA pipeline: deterministic
   structural filters + taxonomy-guided LLM judge (Sec. 3.1–3.3, pp.4–5) **on the task cards
   only**, blinded to program bytes, verdicts, and policy decisions.
3. **Arm B (generic-critique control).** The same inputs with the App. D.2 generic prompt
   (p.17) — tests whether the *taxonomy* is what matters or the LLM alone.
4. **Arm C (judge-robustness control).** Repeat Arm A with a second judge, per App. D.4 (p.19).
5. **Arm D (adversarial rebuttal).** Apply the Sec. 3.4 / App. D.3 (p.18) rebuttal stage to any
   flags in Arm A.
6. **Read-out.** For each of our three headline findings — admission-policy rejections
   (6.2 %–47.7 %), the verified-recovery rate, and the attribution-contract cases — record:
   (i) did COBA flag the *task* as defective, and in which component category? (ii) does the flag
   localize the defect to the *Evaluation System* component? (iii) **can COBA produce a per-program
   counterfactual?** (expected: no — this is the load-bearing test of the distinction) (iv) for the
   attribution corpus, does any component category correspond to "evidence does not bind the
   claimed execution"?

**Decision rules (fixed before running).**
- If Arm A flags the admission-rejected tasks at the task level **and** the flag localizes to
  Evaluation System → our C2 increment is *reproducible in kind by a static audit*, and C2 must be
  demoted to a domain application (with COBA credited for the general principle).
- If Arm A cannot flag them (or only flags them at the *program* level, which is outside its unit
  of analysis) → the byte-fixed, execution-based counterfactual is confirmed as mechanistically
  distinct from COBA, and C2 + C3 support a **measurement-technique** claim in the security domain.
- If no Arm-A/D category corresponds to evidence binding → C4 stands as un-anticipated by the
  comparator, but it must be positioned against the provenance literature (in-toto, SLSA,
  ORTHRUS, PROV-AGENT), which is *outside* this worker's scope and was not audited here.

**Explicitly out of scope for this study (and therefore not claimed):** any superiority claim,
any model ranking, any hosted-model regeneration, and any statement about the 851-program
re-execution being independent of our earlier results.

**Constraint compliance:** this design is *proposed only*. Nothing was launched; no benchmark was
installed; no hosted model was invoked; no manuscript, raw/frozen record, protected lock, or other
worker's file was modified.

## 7. Limitations of this assessment

1. **Design inference, not execution.** "COBA would not have produced X" is inferred from the
   published pipeline (Sec. 3.1–3.4) and the full-text term search; the released code and
   benchmark artifacts were not run or read. If the released AgentSuite repository contains
   execution-based or runtime-evidence modules not described in the paper, the corresponding
   absence claims would need revision. This is the single largest uncertainty in the document.
2. **No matched comparator.** AgentSuite's benchmarks and our artifacts are different systems. No
   head-to-head is possible or claimed, and no number in this report compares the two
   quantitatively.
3. **Scope.** Only AgentSuite was assessed here. C4's closest prior work lies in the provenance and
   trajectory-audit literature (which our manuscript already cites), and ABC (assigned to a
   different worker) was not assessed by me; cross-worker conclusions are root's to synthesize.
4. **Our own claim strength is not re-litigated here.** In particular, the six-release documentary
   audit is not external executable validation, and the staged full re-execution is not a fresh
   model generation; both caveats belong to the paper and are carried into this assessment.
5. **Terminology collision.** AgentSuite uses "representation" (standardized task representation),
   "policy" (benchmark system policy), and "equivalence" (a rebuttal adjudication principle) in
   senses that differ from ours. Any claim-comparison wording must use our terms, not theirs, to
   avoid implying overlap that does not exist.
6. **Volatility of the comparator.** AgentSuite is ICML 2026 with a released artifact; the pipeline
   may evolve. Any novelty statement should carry the snapshot hash recorded in §0.

## 8. Bottom line

- **C1** — `domain_application`. Template overlaps strongly with AgentSuite (component taxonomy,
  Table 2, p.3); the *attribution* axis is genuinely outside it. COBA would not have produced our
  run-level three-way separation.
- **C2** — `measurement_technique`. The general moral is anticipated (p.8, Table 6, random-removal
  null); the *byte-fixed estimator* is not producible by COBA. Do not claim model-ranking novelty.
- **C3** — `domain_application` (instrument). No overlap; execution is their stated non-goal
  (p.12). Do not claim to have invented execution-based verification.
- **C4** — `domain_application`. No overlap at all across 20 pages; but the mechanisms are
  pre-existing, so the novelty is the policy plus its test regime, and the documentary six-release
  audit is not external validation.
- **C5** — `domain_application`, with the generic half **owned by AgentSuite**; only the
  security-attack instantiation is ours.

**Strongest genuine increment over AgentSuite:** the byte-fixed admission-policy counterfactual
evaluated by an independent cryptographic predicate with full program replay (C2+C3) — the only
part of the paper that a static, task-level, LLM-judged audit pipeline structurally cannot
produce.
**Strongest overlap:** the component-based separation-of-validity-sources template (C1, Table 2,
p.3) and the generic "flaws distort performance" empirical result (C5, pp.1, 8).
**Single most important open differentiator:** whether an adapted COBA audit of our *task cards*
can flag the same admission-policy and attribution defects — i.e. whether our increment is a
*new measurement modality* (execution-based, artifact-level counterfactual + evidence binding) or
merely a *domain transplant*. The §6 study is the minimal way to decide this, and it should be run
before the manuscript claims a methodological (as opposed to domain-specific) contribution.