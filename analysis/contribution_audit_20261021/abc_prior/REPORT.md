# Prior-work assessment — ABC (NeurIPS 2025 Datasets & Benchmarks Track)

**Worker:** `abc_prior` (independent assessment; no other worker's results assumed)
**Date:** 2026-10-21
**Comparator:** Yuxuan Zhu, Tengjun Jin, Yada Pruksachatkun, Andy Zhang, Shu Liu, Sasha Cui,
Sayash Kapoor, Shayne Longpre, Kevin Meng, Rebecca Weiss, Fazl Barez, Rahul Gupta, Jwala Dhamala,
Jacob Merizian, Mario Giulianelli, Harry Coppock, Cozmin Ududec, Jasjeet Sekhon, Jacob Steinhardt,
Antony Kellermann, Sarah Schwettmann, Matei Zaharia, Ion Stoica, Percy Liang, Daniel Kang.
*"Establishing Best Practices for Building Rigorous Agentic Benchmarks."* NeurIPS 2025 Track on
Datasets and Benchmarks.

**Primary source used (single):**
`https://proceedings.neurips.cc/paper_files/paper/2025/file/f316275b44ee2de533102913828a8107-Paper-Datasets_and_Benchmarks_Track.pdf`
(local snapshot `sources/abc_neurips2025.pdf`; SHA-256
`2485616a805951e0b3904a4229b97949263c8846b4bda8fcdf8a0582ed58080f`, **verified** to match
`sources/SOURCES.md`).

**Identity verification.** I read the PDF title page (physical p. 1) directly from the
`pdftotext -layout` extraction with form-feed page boundaries: the title reads *"Establishing Best
Practices for Building Rigorous Agentic Benchmarks"*, the author list and affiliations match the
SOURCES.md attribution, and the footer reads *"39th Conference on Neural Information Processing
Systems (NeurIPS 2025) Track on Datasets and Benchmarks"* (physical p. 1). Page count is 41
physical pages, matching SOURCES.md. No alternate version of the paper was consulted.

**Source coverage actually inspected (this is the uncertainty boundary for every absence claim
below).** Full text, all 41 physical pages, no section skipped:
main body pp. 1–10 (§1 Introduction, §2 Related Work, §3 Overview, §4 ABC checklist incl.
Fig. 2 task-validity items T.1–T.10, Fig. 3 outcome-validity items O.a–O.i, Fig. 4 reporting
items R.1–R.14, §5 Assessment incl. Table 1, Fig. 5, §5.2 findings, §5.3 Revising CVE-Bench and
Fig. 6, §6 Conclusion, §7 Limitations); pp. 11–16 (Acknowledgements + references [1]–[102]);
Appendices: **A** formal validity requirements (p. 17, Eq. 1–2), **B** benchmark collection +
Table 2 (pp. 17–19), **C** sources of checklist items + Table 4 (pp. 19–21), **D** difficulty
levels + Table 5 (p. 21), **E** assessment reports Tables 6–15 (pp. 21–28), **F** case studies
F.1–F.6 (pp. 28–32), **G** LLM-as-a-Judge validation experiment (p. 32), **H** rigorous-reporting
example + Table 16 (pp. 32–35), **I** NeurIPS paper checklist (pp. 35–41).
I additionally ran a case-insensitive keyword sweep over the complete extracted text for the terms
used in absence claims: `attribution`, `provenance`, `signature/signed`, `claim-specific`,
`cryptograph*`, `import`, `admission`, `source admission`, `predicate`, `paired`, `replay`,
`equivalence`, `margin`, `McNemar`, `bootstrap`, `sample size`, `trust`.
**Uncertainty boundary:** all "ABC does not do X" statements below are about *what this 41-page
paper reports*. ABC also ships code and a website (p. 3, footnotes 3–4) and a CVE-Bench artifact
I did not execute or read; a mechanism could in principle exist in their repository that is not
described in the paper. I make no claim about ABC's unexecuted artifacts, and I make no claim about
other work by the same authors.

---

## 0. One-paragraph summary of the comparator

ABC is a **checklist-and-audit paper**. It (i) formalises two validity requirements — *task
validity* (target capability ⇔ task success) and *outcome validity* (task success ⇔ positive
evaluator result) (Fig. 1, p. 3; Appendix A, p. 17, Eq. 1–2); (ii) turns them into an actionable
checklist with three parts — task validity (T.1–T.10, Fig. 2, p. 5), outcome validity
(O.a–O.i, Fig. 3, p. 6), benchmark reporting (R.1–R.14, Fig. 4, p. 7); (iii) audits ten
open-source agentic benchmarks with per-item scoring (Tables 6–15, pp. 21–28) and quantifies
benchmark flaws that distort reported agent performance by "up to 100% in relative terms"
(abstract, p. 1; §5.2, p. 9); and (iv) demonstrates remediation on the security benchmark
CVE-Bench, reducing performance overestimation by 33% in absolute terms (abstract p. 1, §5.3
pp. 9–10, Fig. 6). Its own four claimed contributions (p. 2) are: two validity requirements, the
checklist, the ten-benchmark assessment, and the CVE-Bench case study.

---

## 1. Candidate-by-candidate assessment

### C1 — Controlled separation of *attack correctness*, *source admission* and *execution attribution* as an evaluation procedure

**Direct overlap.**
- ABC's Appendix A (p. 17) already splits a benchmark verdict into two layers: `RT` (a
  task-completion flag that "often requires manual inspection") and `f_Eval` (the binary score
  returned by the automatic evaluator), with outcome validity defined as `RT = "success" ⇔
  f_Eval = 1` (Eq. 2). This *is* a correctness-versus-evaluator-output separation, in the abstract.
  Our "correctness" (an independent cryptographic predicate) and ABC's `RT` play the same
  structural role: the ground truth that the automatic score is supposed to reflect but may not.
- ABC's check **O.g.2** ("Ground truth includes all states achievable after success"; "Checks
  relevant and irrelevant states for the challenge", Fig. 3, p. 6; §4.2, p. 7) explicitly
  anticipates the *execution-attribution* idea in one of its forms: the ground truth must be able
  to detect "whether agents affect the environment outside the target scope" (p. 7).
- ABC's **T.10** ("Implementation is free of vulnerabilities that could be exploited to pass
  evaluations without completing tasks", Fig. 2, p. 5) anticipates the *admission/shortcut* axis in
  the environment/implementation sense, and **T.5** (agent isolated from ground truth) is an
  environment-side admissibility condition.

**Mechanistic / empirical distinction.**
- ABC's taxonomy is **two-layer** (capability / success / score). It has **no source-admission
  layer**: nowhere does ABC distinguish "the artifact was not admitted into evaluation" from "the
  artifact was admitted and failed". Keyword sweep: `admission`, `source admission`, `import`
  (as a policy concept) and `predicate` have **zero** occurrences in the 41-page text
  (`import` occurs only inside "important").
- ABC's method is a **static, human-performed audit with a scoring rubric** ("We assigned 1 point
  to each satisfied item and 0 otherwise", p. 4), followed by *designed experiments per identified
  issue* (§5.2, p. 9). It is not a **controlled procedure that decomposes one observed result into
  three separately measured causes**.
- ABC quantifies *flaw-induced* score distortion (e.g. KernelBench 31% absolute overestimation,
  p. 9; CVE-Bench time-based SQLi 32.5%, p. 10). Our procedure quantifies a *different* object:
  the share of results that would flip under a **different admission rule applied to byte-identical
  programs** (46/256, 16/256, 122/256 rejections across arms; 6.2%–47.7%).

**Assessment.** The *taxonomy* half of C1 is **anticipated by ABC** (Appendix A) and by the
O.g.2 / T.10 checks. The *procedure* half — a controlled, per-outcome decomposition with
byte-identical re-admission and a stage-resolved denominator — is **not** in ABC and is a
difference in kind of evidence (intervention vs. audit), not only of domain. But the evidence for
it in our work is **single-domain and single-fixture**; the decomposition is demonstrated on one
cryptographic study, not on a second benchmark. Therefore C1 is *not* supported as a general
methodological contribution on ABC-comparison grounds alone; it is supported as a
**measurement technique** with a domain application.

---

### C2 — Paired representation contrasts under a common executor, then a changed admission rule applied to *unchanged* programs

**Direct overlap — and this is the strongest overlap in the whole assessment.**
- **ABC Appendix G (p. 32)** performs the same *move* as the second half of C2: it takes
  **unchanged historical agent artifacts** (AgentOccam trajectories), varies the evaluator
  (LLM-as-a-Judge, GPT-5, ten independent rounds, majority vote), and measures the outcome
  against **manually verified ground truth**, reporting judge accuracy 80.0% and self-consistency
  99.2%. In other words, ABC already demonstrates *"vary the evaluation rule on fixed agent
  outputs and measure the effect"*.
- **ABC §5.3 / Fig. 6 (pp. 9–10)** performs a *before/after* comparison on CVE-Bench (Cy-A,
  Aut, T-Ag arms; zero-day/one-day; Success@1 and Success@5) after changing the evaluation
  design/implementation, reporting a 32.5% overestimation removal for time-based SQL injection and
  a 10% success-rate drop after denying the ungated outbound server. This is a *changed rule →
  changed reported score* contrast on a security benchmark.
- **ABC KernelBench case study (F.6, pp. 31–32)** re-scores **previously generated kernels**
  (Lange et al.'s generations) against newly generated test cases, obtaining a 31% overestimation
  estimate — i.e. ABC re-grades retained artifacts with a strengthened evaluator.

**Distinction.**
- ABC's contrasts are **between evaluation regimes or against external ground truth, not paired at
  the instance level**: no matched instance units, no paired test, no equivalence margin, no
  preregistration, no variance statement. ABC's own statistics are descriptive percentages, and
  its Appendix H confidence intervals are a *normality-based interval for ground-truth noise*
  (Eq. 3, p. 34) — a different quantity from a paired policy contrast. The NeurIPS checklist
  answer to Q7 states all reported numbers are deterministic and therefore carry no error bars
  (p. 38), which is incompatible with the paired-inference style of C2.
- ABC varies the **outcome-grading** rule (state matching, substring/whole-string matching, judge
  configuration) — it never varies a **source-admission** rule (whether the submitted program is
  admitted at all). Keyword sweep: `admission` — 0 occurrences; `paired` — 0 occurrences;
  `McNemar`/`bootstrap`/`margin` — 0 occurrences.
- ABC's Appendix G varies a *judge* (a fuzzy-matching component over text answers); C2's second
  half varies an *admission gate* over *generated source programs*, with the estimand being
  **evaluator-policy dependence** (which outcomes depend on the rule rather than on the program).
- ABC does **not** manipulate **representation** as an independent variable at all: `representation`
  appears in ABC only in the sense of an LLM's output format.

**Assessment.** The *shape* of C2's second half is anticipated by ABC (App. G, Fig. 6, F.6). The
*specific* combination — paired representation contrast under a common executor, then the same
byte-identical programs re-admitted under a changed rule — is not in ABC, and the *estimand*
(policy dependence, not model ranking, not a general causal capability effect) is not something ABC
frames or measures. C2 is therefore **plausibly incremental** on the policy-sensitivity half and
**unprecedented in ABC** on the paired-representation half, but the increment is a
**measurement technique** whose generality is demonstrated on one study; it is not a new general
benchmark-auditing method, and the manuscript's own framing ("bounded measurements, not a new
general benchmark-auditing method", `main_sections/10_discussion.tex` ll. 26–30) is the correct
one.

---

### C3 — Independent cryptographic predicates and full fresh program replay against retained public inputs

**Direct overlap.**
- ABC requires, as checklist items, that ground truth be **independently verified** (**T.7**
  "Annotated ground truth is verified for correctness", Fig. 2, p. 5) and that there be an
  **oracle** (**T.9** "Benchmark includes an Oracle solver that can automatically solve all
  challenges", Fig. 2, p. 5; §4.1, p. 5), and it requires **test-case verification** for
  code-generation benchmarks (**O.d.1**, Fig. 3, p. 6). The *concept* of an independent correctness
  oracle is fully part of ABC's best-practice vocabulary.
- ABC's **KernelBench** case study (F.6, pp. 31–32) re-grades retained generations with
  independently produced test cases, and ABC's **T.6** requires the environment setup to be
  "fully reproducible and frozen at the time of benchmark release" (p. 5) — the frozen-environment
  precondition for replay.
- ABC's Appendix H (pp. 32–35) provides a worked template for *quantifying* ground-truth error
  and its effect on reported success rates (11.65% incorrect ground-truth queries → confidence
  intervals → revised rank intervals, Table 16, p. 34).

**Distinction.**
- "Cryptographic predicate" is a **domain-specific instantiation**: keyword sweep shows
  `cryptograph*` has **0** occurrences in the 41-page text, and ABC's assessed benchmarks contain
  no cryptographic task (Table 1, p. 8; Table 3, p. 19). The closest security items are
  answer-matching on Cybench (Table 8, p. 23) and the CVE-Bench state-matching flaws (§5.3).
- "**Full fresh program replay against retained public inputs**" is a *rerecording* discipline.
  Keyword sweep: `replay` has **0** occurrences in ABC; ABC has no notion of re-executing
  retained agent programs, and its Appendix H example of verification is a *sampling* verification
  of ground truth (500 of N tasks, p. 33), not a replay of retained submissions.
- ABC's KernelBench re-scoring is *not* a replay either: it applies **new** tests to **old**
  outputs; it does not re-execute old programs against **old, retained** inputs.

**Assessment.** C3 is a **domain application** with a modest **measurement-technique** increment
(the fresh-replay discipline and its denominator discipline). The independent-predicate half is
anticipated in spirit by T.7/T.9/O.d.1 and is domain-specific in execution; the fresh-replay half
is genuinely not in ABC but is a reproducibility/rigour practice that sits close to the general
reproducibility literature that ABC cites (R.1–R.5, R.8; §4.3, p. 7). C3 does **not** support a
general-method claim on ABC-comparison grounds.

---

### C4 — Complementarity of authenticated evidence and claim-specific joins in bounded adversarial attribution tests, using existing provenance mechanisms

**Direct overlap.**
- **Essentially none.** Keyword sweep over the full text: `attribution` — 0 occurrences;
  `provenance` — 0; `signature`/`signed` — 0 as cryptographic concepts (`designed` only);
  `claim-specific` — 0; `trust` — only in "can be trusted" (p. 1) and in reference titles.
  ABC's **T.5** (agent isolated from ground truth, Fig. 2, p. 5) and **O.c.2** ("Is designed to
  resist adversarial inputs and reward hacking", Fig. 3, p. 6) concern *attacks by the agent on
  the benchmark*, not *the authenticity of the evaluator's own evidence chain*. **R.8** ("Describes
  steps taken to prevent, identify, and correct flaws", Fig. 4, p. 7) is a *reporting* obligation.
- The nearest conceptual cousins in ABC are **T.9** (an oracle that establishes correctness) and
  the formal separation in Appendix A between `RT` and `f_Eval` (p. 17) — ABC separates *what
  happened* from *what the score says*, but supplies no mechanism for *proving which happened*.

**Distinction.**
- ABC supplies **no** attribution machinery, no trust model, no signed-record design, no
  claim-scoping, and no mutation-based testing of an evaluation decision. Its unit of analysis is
  the *benchmark*, not the *claim about one execution*.
- C4 is therefore **not anticipated by ABC**. But note: the manuscript itself already concedes that
  "configured provenance mechanisms can implement the tested policy, so the contribution is its
  measured application to cryptographic attack claims rather than a new signing, logging or
  isolation primitive" (`main_sections/02_related.tex` ll. 47–50; `09_audit.tex` ll. 66–72).
  ABC is simply the *wrong* comparator for the question "is this attribution policy new?" — ABC
  provides no anticipation, but neither does it provide a validation baseline. ABC's role here is
  only to show that the attribution axis is *not* something ABC's checklist covers either
  (a checklist gap, not a competitive overlap).

**Assessment.** C4 has the **strongest genuine increment over ABC** — and also the **weakest
matched-comparator support**, because ABC cannot validate or calibrate it. Its novelty must be
argued against provenance-aware comparators (in-toto/SLSA/in-toto policy, and the manuscript's own
cited CTF-ABACUS / ORTHRUS / PROV-AGENT), not against ABC. The claim that can be supported is
"a tested, claim-specific attribution policy with bounded mutation evidence, applied to security
claims" — a **domain application with a general-purpose evaluation design**, not a general
methodological contribution.

---

### C5 — An integrated security-specific empirical method, rather than generic discovery that benchmark flaws distort performance

**Direct overlap — and this is where the candidate's framing is directly contradicted by ABC.**
- ABC's core thesis *is* generic discovery that benchmark flaws distort performance ("we show that
  many agentic benchmarks have issues in task setup or reward design… Such issues can lead to
  under- or overestimation of agents' performance by up to 100% in relative terms", abstract, p. 1;
  §5.2, p. 9). It is not a security paper and does not claim to be one.
- ABC has **already performed the security-domain application** that C5 claims as its differentiator:
  §5.3 "Revising CVE-Bench" (pp. 9–10) audits and fixes a cybersecurity benchmark, and the
  headline result — "When applied to CVE-Bench… ABC reduces performance overestimation by 33%" in
  absolute terms (abstract, p. 1; p. 2; p. 10) — is a *security-specific* case study with
  *domain-specific* checks (naive state matching for time-based SQL injection; an ungated outbound
  server reachable from the same Docker network, "creating a shortcut", p. 10). ABC reports the
  result was "confirmed by cybersecurity experts" (p. 2).
- ABC's checklist items that carry the security case study are literally the two we would cite:
  **O.g.1** (ground truth must include all achievable states) and **T.9** (oracle solver) —
  ABC's CVE-Bench fix is described as satisfying T.9 and O.g.1 (p. 10).

**Distinction.** The only defensible differences are: (i) our case study is *cryptographic* and
*constructive* (agent-written attack programs against a declared task contract) rather than
*web-exploitation state matching*; (ii) our case study *integrates* a paired contrast and a
policy-sensitivity contrast that ABC's single-case CVE-Bench narrative does not contain; (iii)
our case study adds an *attribution* layer (E5) that ABC has no analogue for. Differences (i)–(iii)
are incremental and domain-level, not a new general method.

**Assessment.** C5 as phrased ("integrated security-specific empirical method, *rather than* generic
discovery that benchmark flaws distort performance") is **not supported** against ABC, because ABC
is the generic discovery work *and* has already delivered the security-domain application.
A defensible narrowing: "an integrated *cryptographic* case study that adds a policy-sensitivity
contrast and an attribution layer to the ABC-style audit." That narrowing is a **domain
application**, and it should not be presented as a general methodological contribution.

---

## 2. Claims ABC anticipates / claims plausibly incremental / differentiating evidence

| Candidate | Anticipated by ABC | Plausibly incremental | Not supported by ABC-comparison |
|---|---|---|---|
| C1 | Yes — Appendix A two-layer validity (p. 17); O.g.2 (p. 6–7); T.5/T.10 (p. 5) | The **three-way** separation and the *intervention* (byte-identical re-admission) as an evaluation procedure | Generality of the procedure beyond one cryptographic study |
| C2 | Partly — App. G (p. 32) varies the evaluator on fixed artifacts; §5.3/Fig. 6 (p. 9–10) changes the rule; F.6 (p. 31–32) re-grades retained outputs | Paired instance-level contrasts, preregistered equivalence margin, and admission-rule as the varied factor | A general causal capability or model-ranking claim; transfer beyond the tested contract |
| C3 | Partly — T.7/T.9/O.d.1 (p. 5–6), T.6 freeze (p. 5), App. H template (pp. 32–35) | Fresh re-execution of retained programs against retained public inputs with an explicit denominator | Any general-method framing; the cryptographic predicate is domain-specific |
| C4 | **No** — no attribution/provenance/signing/trust/claim content in 41 pages | The whole candidate, including the claim-specific join policy and its mutation evidence | Any competitive claim: ABC is not a valid comparator for it; provenance-aware work is |
| C5 | **Yes, largely** — generic discovery thesis (p. 1, p. 9) and the CVE-Bench security case study with a 33% overestimation reduction (p. 1, 9–10) | Only a narrowed "cryptographic case study with policy-sensitivity and attribution layers" | The contrastive framing "rather than generic discovery" |

**Differentiating evidence that would be required (proposed, not run).**
1. *C1/C2 (external, matched to ABC's own claim type).* Take a benchmark with **publicly retained
   agent submissions** and a **documented admission rule** — e.g. CVE-Bench artifacts, SWE-bench
   Verified model submissions, or the KernelBench generations Lange et al. released — and
   re-grade the **byte-identical programs** under two admission rules, reporting paired
   instance-level contrasts with an equivalence margin. This is the experiment that would
   separate "a changed rule changes reported performance" (ABC, Fig. 6) from "the same programs
   flip under a changed rule, and by how much" (C2). It needs no hosted model: the artifacts are
   already generated, and only the evaluator changes.
2. *C1 generality.* Apply the three-way separation to a **second, non-cryptographic** benchmark's
   harness to show the decomposition is recoverable from a third party's artifacts, not only from
   our own capture-first records. Without this, C1 remains a local technique.
3. *C4 (matched comparator, and ABC cannot serve).* Implement the claim-specific-join policy
   against a **public provenance-carrying agent-security benchmark** (e.g. CyberGym, CTF-ABACUS
   traces) with an in-toto/SLSA baseline arm, and report false-promotion and false-rejection
   counts under the same bounded mutation protocol. This is the only study that can support C4 as
   more than a local application.
4. *C5 (falsification).* If the policy-sensitivity contrast does not replicate on a second
   benchmark (study 1), the "integrated security-specific method" claim reduces to the ABC-style
   single-case audit and should be reported as such.

---

## 3. Domain-specific application vs. general methodological novelty

| Candidate | Novelty type (best supported) | Why not a general method |
|---|---|---|
| C1 | `measurement_technique` (with `domain_application` component) | Demonstrated on one cryptographic study/fixture; ABC already owns the validity taxonomy |
| C2 | `measurement_technique` | Single study, single contract; the estimand is explicitly scoped to the tested contract; no transfer evidence |
| C3 | `domain_application` (+ small `measurement_technique` for the fresh-replay discipline) | Independent predicates and replay are domain/rigour practices; the predicate is cryptographic |
| C4 | `domain_application` (design is general-purpose; the demonstrated instance is not) | No matched comparator; mechanism deliberately reuses existing provenance tooling |
| C5 | `domain_application` (narrowed) | The contrastive framing is contradicted by ABC; only the cryptographic instantiation is new |

**What the work DOES support (stated plainly).**
It supports a **bounded, security-domain empirical method** that (a) decomposes a reported attack
outcome into correctness, admission and attribution, (b) measures evaluator-policy dependence with
byte-identical programs and paired contrasts under a preregistered equivalence margin, and
(c) specifies a tested attribution policy for security claims, with a nine-field release-evidence
rubric as documentary context. It supports **no** general methodological claim relative to ABC:
ABC already provides the general validity framework, the general checklist, the general
"flaws distort performance" finding, and a security-domain case study (CVE-Bench).

**What the work does NOT support.**
- No superiority over ABC is claimed or claimable: ABC's benchmark (CVE-Bench, web exploitation,
  state matching) and our artifact (cryptographic construction, predicate-based) are different
  systems with different task contracts. There is no head-to-head and none is possible.
- The six-release documentary audit is **not** external executable validation; it is a
  54-cell documentary rubric over public material (0/6 releases satisfy all nine fields; removing
  the published-outcome field still leaves 0/6) and it is kept separate from the executed attack
  families. It must not be described as independent benchmark validation.
- The reference replays (852/852 agreement) are re-executions of retained programs; they are not
  fresh model generations and they add no independent model session.

---

## 4. Absence-claim ledger (source coverage + uncertainty boundary)

Every row was checked against the **complete** 41-page text (main body + Appendices A–I), using
both reading and a case-insensitive keyword sweep. "Absent" = the term/concept does not occur in
this paper; it does **not** mean the ABC authors or their artifacts never considered it.

| Claim | Coverage | Result | Uncertainty boundary |
|---|---|---|---|
| ABC has no source-admission axis | full text + sweep (`admission`, `import`, `predicate`) | Absent | ABC's unexecuted code/website not inspected; a gate could exist there |
| ABC has no attribution/provenance/signing/claim-scoping concept | full text + sweep (`attribution`, `provenance`, `signature`, `claim-specific`, `trust`) | Absent | same |
| ABC has no cryptographic task or predicate | full text + sweep (`cryptograph*`); Tables 1, 3, 8 | Absent | Cybench is cyber but answer-matching (Table 8, p. 23); CVE-Bench is web exploitation |
| ABC contains no paired/equivalence/matched-instance analysis | sweep (`paired`, `equivalence`, `McNemar`, `margin`) | Absent | ABC's App. H CI (p. 34) is a normality-based interval for ground-truth noise — not a paired contrast |
| ABC contains no replay of retained agent programs | sweep (`replay`) | Absent | KernelBench F.6 re-scores retained outputs with *new* tests; different from replay |
| ABC varies an evaluator on fixed artifacts | read App. G (p. 32), §5.3/Fig. 6 (pp. 9–10) | **Present** | — |
| ABC separates true task success from the automatic score | read App. A (p. 17, Eq. 1–2) | **Present** | — |
| ABC has no representation manipulation | full text | Absent | `representation` occurs only as an LLM output-format notion |
| ABC's per-issue quantification is deterministic by the authors' own account | read NeurIPS checklist Q7 (p. 38) | **Present** | — |
| ABC's security case study is CVE-Bench with a 33% absolute overestimation reduction | read abstract p. 1, p. 2, §5.3 pp. 9–10, Fig. 6 | **Present** | ABC does not decompose *why* the CVE-Bench numbers moved beyond the two named flaws |

---

## 5. Limitations of this assessment

1. **Single comparator.** This assessment covers ABC only. The AgentSuite comparator
   (`agentsuite_prior/`) and the manuscript's other cited works (CTF-ABACUS, ORTHRUS, PROV-AGENT,
   BenchJack, AgentRewardBench) are where C4's novelty must actually be argued; conclusions here
   are not transferable to them.
2. **Static text only.** No ABC code, no ABC website, no CVE-Bench harness was executed or read.
   Absence claims are bounded by §4.
3. **No matched comparator exists.** I did not attempt, and do not claim, any head-to-head.
4. **The manuscript was read, not modified.** I inspected
   `paper/capability_revision_20261020/main_sections/{01_intro,02_related,04_verification,08_h1r3,09_audit,10_discussion}.tex`
   to ground the candidate claims; I edited nothing, ran no experiment, installed no benchmark and
   invoked no hosted model. The proposed studies in §2 are designs only.
5. **I did not read the other audit workers' outputs** (policy_mechanism, paired_effects,
   attribution_evidence) and make no claim about their results; where I cite manuscript numbers
   (6.2%–47.7%, 852/852, 11,256 mutation evaluations, 0/6, 21/22 → 22/22) I quote the manuscript
   as written, unverified by me.

---

## 6. Bottom line for the contribution audit

- **C1** — *measurement_technique*, partially anticipated (Appendix A taxonomy, O.g.2, T.5/T.10);
  the increment is the three-way decomposition **as a controlled procedure**, demonstrated once.
- **C2** — *measurement_technique*; the "vary the evaluator on fixed artifacts" **shape** is
  anticipated by ABC Appendix G and §5.3, the **admission-rule** variable and the paired/equivalence
  analysis are not; ABC provides no matched contrast and no competitor for the estimand.
- **C3** — *domain_application*; independent-predicate practice anticipated by T.7/T.9/O.d.1,
  fresh replay genuinely absent from ABC, cryptographic predicate domain-specific.
- **C4** — *domain_application* (design general-purpose, instance domain-bound); **no ABC overlap
  and no ABC-based validation** — the only candidate with a clean absence, and also the one whose
  novelty must be argued elsewhere.
- **C5** — *domain_application*, and the stated contrastive framing ("rather than generic
  discovery") is **contradicted** by ABC, which is the generic discovery work and already owns a
  security-domain case study.

**Strongest genuine increment over ABC:** C4's claim-specific attribution contract — the only
candidate for which the 41-page primary source provides no anticipation of any kind.

**Strongest overlap:** C2's second half versus ABC Appendix G (p. 32) and §5.3/Fig. 6 (pp. 9–10),
which already vary the evaluation rule on fixed agent artifacts and report the resulting score
movement in a security benchmark.

**Single most important open differentiator:** whether a *second*, non-cryptographic benchmark's
**retained agent programs** can be re-graded under two admission rules with byte-identical
artifacts and paired contrasts (proposed study 1). If it can, C1/C2 upgrade from a local
technique to a portable evaluation method, and C5's framing becomes defensible in narrowed form.
If it cannot, the paper's honest claim is a well-instrumented security-domain case study that
extends ABC's audit with a policy-sensitivity contrast and an attribution layer — valuable, and
not a new general principle.