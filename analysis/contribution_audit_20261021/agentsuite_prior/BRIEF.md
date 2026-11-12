# Prior-work review — AgentSuite (ICML 2026)

You are the `agentsuite_prior` worker in a contribution audit. Root orchestrates
and verifies; you produce one independent assessment.

## Your comparator

**AgentSuite: Toward More Reliable Agent Evaluation with a Component-Based
Benchmark Auditing Pipeline.** Suh, Ji, Lee et al. ICML 2026, PMLR 306:116300–116319.

Full-text snapshot (root-owned, read-only):
- `sources/agentsuite_icml2026.pdf` — 20 physical pages
- `sources/agentsuite_icml2026.txt` — `pdftotext -layout` extraction with form-feed
  page boundaries

Bibliographic identity and primary-source URLs are in `sources/SOURCES.md`.
Verify the snapshot's identity yourself against the PDF title page.

## Why you exist

The author believes the existing experiments support a stronger methodological
contribution to Security Agent Evaluation than "a local evaluation case study."
Assess that hypothesis. **Do not assume the contribution must be general, and
do not assume it must be novel.** Root is running mechanism, paired-statistical
and attribution audits separately; do not wait for them and do not treat any
earlier novelty assessment as an established fact.

AgentSuite is the closer comparator for the *auditing* half of the claim, so
be precise about what its component-based pipeline already covers — especially
its treatment of **task validity**, **outcome validity**, **ground truth**,
**replay/counterfactual checks**, and **evaluation-component defects**. Read
its full paper and appendices, not just the abstract.

## The five candidate contributions to assess

1. A controlled separation of **attack correctness**, **source admission** and
   **execution attribution** as an evaluation procedure.
2. **Paired representation contrasts under a common executor**, followed by a
   changed admission rule applied to *unchanged* programs. This estimates
   evaluator-policy dependence under the tested contract — not model rankings
   and not a general causal capability effect.
3. **Independent cryptographic predicates** and full fresh program replay
   against retained public inputs.
4. **Complementarity of authenticated evidence and claim-specific joins** in
   bounded adversarial attribution tests, using existing provenance mechanisms.
5. An **integrated security-specific empirical method**, rather than generic
   discovery that benchmark flaws distort performance.

## What to produce

Read the **full** AgentSuite paper and its relevant appendices. Then:

- Report **direct overlap**: where AgentSuite already does what a candidate
  contribution proposes, with physical PDF page numbers and section/table
  anchors.
- Report **empirical and mechanistic distinctions**: what AgentSuite does not
  do, or does differently, and whether that difference is a difference in kind
  or only in domain.
- Report **claims AgentSuite anticipates**, **claims plausibly incremental** to
  the candidate contribution, and **what evidence would differentiate them**.
- Distinguish **domain-specific application** from **general methodological
  novelty**. A measured domain application can be valuable without being a new
  general principle.
- State explicitly whether AgentSuite's pipeline, applied to our setting,
  would have produced the same finding — and if not, why not. This is the
  decisive question for whether our contribution is a new method or a
  domain-specific application of an existing one.
- For any "AgentSuite does not do X" claim, give the source coverage you
  actually inspected and state the uncertainty boundary. Do not define novelty
  by an arbitrarily narrow combination of familiar ingredients.

You may propose a minimal external study design that would separate your
comparator from the candidate contribution. **Do not launch it**, do not install
benchmarks, and do not invoke hosted models.

## Hard rules

- **No claims of superiority without a valid matched comparator.** AgentSuite's
  benchmark and ours are different systems; say so rather than implying a
  head-to-head.
- The six-release documentary audit in our work is **not** external executable
  validation. Do not treat it as such.
- Quote only short compliant excerpts. Prefer paraphrase with anchors.
- Primary-source links are required for every factual claim about AgentSuite.
- **Do not edit** the manuscript, any raw or frozen record, any protected lock,
  or any other worker's files. Write only inside `agentsuite_prior/`.
- Preserve the source PDFs and all raw data unmodified.
- No further subagents. You are not alone in the codebase; never revert
  others' edits.

## Deliverables

Write into `agentsuite_prior/` (create it):

- `REPORT.md` — the assessment, with exact source/claim anchors, evidence
  strength, and limitations.
- `claim_comparison.json` — a machine-readable matrix. One row per candidate
  contribution with fields: `id`, `claim`, `agentsuite_overlap` (with
  anchors), `agentsuite_distinction`, `novelty_type` (`general_method` |
  `domain_application` | `measurement_technique` | `none`), `evidence_strength`,
  `differentiating_evidence`, `limitations`.

The deliverable is an executed assessment, not an opinion. If the evidence does
not support a general contribution, say so plainly and state what the work
*does* support. Negative and partial results stay visible.