# Prior-work review — ABC (NeurIPS 2025 Datasets and Benchmarks Track)

You are the `abc_prior` worker in a contribution audit. Root orchestrates and
verifies; you produce one independent assessment.

## Your comparator

**ABC: Establishing Best Practices for Building Rigorous Agentic Benchmarks.**
Zhu, Jin, Pruksachatkun et al. NeurIPS 2025 Datasets and Benchmarks Track.

Full-text snapshot (root-owned, read-only):
- `sources/abc_neurips2025.pdf` — 41 physical pages
- `sources/abc_neurips2025.txt` — `pdftotext -layout` extraction with form-feed
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

Read the **full** ABC paper and its relevant appendices. Then:

- Report **direct overlap**: where ABC already does what a candidate
  contribution proposes, with physical PDF page numbers and section/table
  anchors.
- Report **empirical and mechanistic distinctions**: what ABC does not do, or
  does differently, and whether that difference is a difference in kind or only
  in domain.
- Report **claims ABC anticipates**, **claims plausibly incremental** to the
  candidate contribution, and **what evidence would differentiate them**.
- Distinguish **domain-specific application** from **general methodological
  novelty**. A measured domain application can be valuable without being a new
  general principle.
- For any "ABC does not do X" claim, give the source coverage you actually
  inspected and state the uncertainty boundary. Do not define novelty by an
  arbitrarily narrow combination of familiar ingredients.

You may propose a minimal external study design that would separate your
comparator from the candidate contribution. **Do not launch it**, do not install
benchmarks, and do not invoke hosted models.

## Hard rules

- **No claims of superiority without a valid matched comparator.** ABC's
  benchmark and ours are different systems; say so rather than implying a
  head-to-head.
- The six-release documentary audit in our work is **not** external executable
  validation. Do not treat it as such.
- Quote only short compliant excerpts. Prefer paraphrase with anchors.
- Primary-source links are required for every factual claim about ABC.
- **Do not edit** the manuscript, any raw or frozen record, any protected lock,
  or any other worker's files. Write only inside `abc_prior/`.
- Preserve the source PDFs and all raw data unmodified.
- No further subagents. You are not alone in the codebase; never revert
  others' edits.

## Deliverables

Write into `abc_prior/` (create it):

- `REPORT.md` — the assessment, with exact source/claim anchors, evidence
  strength, and limitations.
- `claim_comparison.json` — a machine-readable matrix. One row per candidate
  contribution with fields: `id`, `claim`, `abc_overlap` (with anchors),
  `abc_distinction`, `novelty_type` (`general_method` |
  `domain_application` | `measurement_technique` | `none`), `evidence_strength`,
  `differentiating_evidence`, `limitations`.

The deliverable is an executed assessment, not an opinion. If the evidence does
not support a general contribution, say so plainly and state what the work
*does* support. Negative and partial results stay visible.