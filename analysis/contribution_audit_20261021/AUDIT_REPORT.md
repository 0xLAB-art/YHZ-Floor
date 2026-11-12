# Contribution audit — final report

**Date:** 2026-10-21
**Scope:** the four authorised axes (admission mechanism, paired policy effects,
attribution evidence, closest prior work), executed against frozen inputs.
**Manuscript:** unmodified by this audit. All 26,181 frozen input files re-verified
unchanged after the run (`verify_freeze.py`: PASS), and no `.tex` file in the
manuscript tree has a modification time inside the audit window.

---

## 1. What was executed

| Component | Model / route | Output | Root verification |
|---|---|---|---|
| `policy_mechanism` | pre-existing (wave 1) | `policy_mechanism/REPORT.md`, `FULL_CENSUS.json`, `CASE_LEDGER.jsonl`, `VALIDATION.json` | 17 checks re-derived from the frozen records |
| `paired_effects` | pre-existing (wave 1) | `paired_effects/REPORT.md`, `results.json`, `contrasts.csv`, `preregistered_L3_reproduction.json` | 12 checks re-derived from the frozen records |
| `attribution_evidence` | pre-existing (wave 1) | `attribution_evidence/REPORT.md`, `recomputed_summary.json`, `claim_ledger.json`, `supplementary_census.json` | 14 checks re-derived from the frozen records |
| `abc_prior` | `minimax/minimax-m3.1-flash:free` | `abc_prior/REPORT.md`, `claim_comparison.json` | source identity verified against the PDF title page; anchors checked |
| `agentsuite_prior` | `minimax/minimax-m3.1-flash:free` | `agentsuite_prior/REPORT.md`, `claim_comparison.json` | source identity verified against the PDF title page; anchors checked |
| Root | — | `root_verify.py` (43/43), `SYNTHESIS_MATRIX.{md,json}`, `CENTRAL_CLAIM.md`, `VALIDATION_STUDY.md` | — |

`policy_mechanism` was incomplete when this session began: its scripts and a partial
run existed, but the finalizer had never run. `finalize.py` was executed and
validated (PASS: 852 rows, 128 derivatives, 15 tests, 7,670 input files unchanged).

**Root verification.** `root_verify.py` does not call any worker's analysis code.
It re-derives the headline numbers from the frozen H1-R3 records and compares
them to the worker artifacts: 43 independent checks, 43 passed. This covers the
legacy admission census, the v3 admission census, the population splits, the
cryptographic reproduction counts, the derivative intervention, the full paired
contrast at L3, the q-sign census, the preregistered L3 reproduction, and all five
attribution populations including an independent recount of the 11,256 mutation
evaluations.

**Anchor verification.** `verify_anchors.py` checks that every prior-work anchor
the synthesis cites actually appears on the physical PDF page it is cited for,
and that the seven attribution-related terms are absent from the full text of
both comparators: 28 checks, 28 passed. It also confirms the page mapping — the
`pdftotext` extraction of each PDF ends in one trailing blank block, so block N
is physical page N.

---

## 2. The consolidated verdict

| Claim | ABC | AgentSuite | Ours | Verdict |
|---|---|---|---|---|
| C1 three-way separation | anticipated (App. A p. 17; O.g.2 p. 6–7; T.5/T.10 p. 5) | structurally anticipated (Table 2 p. 3) | `measurement_technique` | Supported as a controlled procedure; **not** a new general principle. |
| C2 paired contrast + byte-fixed admission rule | shape anticipated (App. G p. 32; §5.3/Fig. 6 pp. 9–10) | conceptually anticipated (p. 8) | `measurement_technique` | **Strongest candidate.** Increment is a difference in kind: byte-fixed, instance-paired, policy-dependence estimand. |
| C3 independent predicate + fresh replay | vocabulary anticipated (T.7/T.9/O.d.1 pp. 5–6) | explicitly not generalised (App. A p. 12) | `domain_application` | Supported as a domain application with a rigour increment. |
| C4 attribution contract | **zero overlap** (41 pages) | **zero overlap** (20 pages) | `domain_application` | Strongest genuine increment, but the right comparators are provenance-aware works, not these two. |
| C5 integrated security-specific method | **contradicted** (abstract p. 1; §5.3 pp. 9–10) | **contradicted** (abstract p. 1; 5,086 tasks) | `domain_application` | Not supported as phrased. The generic half is prior work. |

**The headline: the contribution is a domain-specific instantiation with a new
measurement instrument and a new evidence contract, not a new general principle.**
ABC owns the validity taxonomy and the "flaws distort performance" finding with a
security case study; AgentSuite owns the component-wise decomposition and the
large-scale version of the same finding.

---

## 3. What the audit changed about the interpretation

Three findings from the wave-1 mechanism audit materially change how the paper's
strongest number should be read, and all three are *not* in the manuscript today.

1. **The legacy import policy was legitimate under its own prompt.** All 205 of its
   import rejects concern modules the frozen prompt explicitly permitted. Under
   the v3 contract actually in force, **zero of 852** sources were rejected for
   imports; the three pre-output failures are one syntax error and two runtime
   errors. The 205 programs are therefore **not** task-contract violations.
2. **The effect survives its strongest deflation.** A conservative transform that
   removes only eligible, whole, top-level unused imports was applied to 128
   derivatives; all 128 produced identical parsed JSON output under fresh
   execution, 104 then qualified under the legacy policy, and 98 of those are
   cryptographically correct. The shift does not disappear when unused imports
   are removed.
3. **The qualifier's own classification was not the cause.** Runtime tracing
   observed a genuine load of the imported object in 100 of the 101 sources with
   static legacy-disallowed references.

Together these turn "the evaluator made an error" into the stronger and more
defensible **"evaluator-policy dependence"**: even a rule that is legitimate
under the contract that declared it determines up to 47.7% of the programs
admitted, and up to 32 percentage points of the apparent representation contrast,
when it is swapped on byte-identical programs.

---

## 4. Two manuscript passages that need correcting on their own evidence

These are independent of how the contribution is framed. A careful reviewer would
make them.

**`main_sections/10_discussion.tex`, HEB-1 paragraph.** "composition-blind and
authenticity-blind baselines" is wrong: HEB1's three systems are the
schema/declaration and hash-integrity baselines, and **none of them authenticates
records**, so the wording implies authentication is the controlled contrast when it
is not. "join-only checks false-rejected 14/16 honest partial claims" is not a
comparative false-reject rate: the validator emits only full attribution, so it
rejected fourteen lower-level requests because it does not support them. That is
a functionality difference. The worker's own claim ledger (`claim_ledger.json`,
H01) already carries the corrected wording. A replacement paragraph is in
`CENTRAL_CLAIM.md` §3.

**`main_sections/11_limits.tex`, reproducibility paragraph.** It must now name
the newly recomputable set and state the boundary this audit established: the
legacy import policy is a counterfactual policy whose rejects were permitted by
the frozen prompt.

**One further item for the supplement**, from the attribution audit:
`supp_sections/S27c_attribution_compact.tex` says the property check "is harder
than a normal evaluation". That is narrower than a universal ordering — an empty
replay ledger removes replay rejection but does not test cross-submission
replay-state correctness. Prefer "each mutant is evaluated with an empty replay
ledger; this does not test cross-submission replay-state correctness."

---

## 5. What the audit does **not** establish

- No general methodological claim. ABC and AgentSuite already own the general
  principle; there is no matched comparator and no head-to-head is possible.
- No causal capability effect of representation. Representation arms are not model
  comparisons; the legacy contrast is an algebraic gate on fixed programs, not a
  fresh policy deployment. The interaction is confined to ECDSA at L1/L2 and
  ranges −21.88 to −42.19 pp by family weighting at L3.
- No prevalence estimate for attribution failure. The corpora are constructed
  cases, and IAR-C had already evaluated the same 44 case IDs during calibration,
  so the preserved corpus is a preserved replay rather than an untouched
  held-out test.
- No superiority over any provenance framework. The configured in-toto inspection
  reproducing 21/22 then 22/22 decisions is an implementation-agreement result.
- No external validation. The six-release documentary audit (0/6 satisfying all
  nine fields) is a 54-cell rubric over public material, not executable
  validation of anything.
- No equivalence claim beyond the tested contract. The preregistered L3 verdict is
  reproduced exactly, and the new contrasts are exploratory.

---

## 6. The one study that would settle it

`VALIDATION_STUDY.md` specifies it: re-grade a second benchmark's publicly
retained agent submissions under two admission rules with byte-identical
artifacts and paired instance-level contrasts, with a vacuous-rule null baseline
and four explicit falsification criteria (F1–F4). It needs no hosted model and no
new agent cohort; S0–S1 (rule construction and the admission census) need no
benchmark execution at all.

Either outcome is publishable. Leaving the question open while claiming generality
is not.

---

## 7. Deliverables

| File | Content |
|---|---|
| `SYNTHESIS_MATRIX.md` / `.json` | claim × evidence × closest-prior-work matrix, built by `build_matrix.py` from the worker artifacts |
| `CENTRAL_CLAIM.md` | the defensible contribution, the allowed/disallowed table, and the two manuscript corrections |
| `VALIDATION_STUDY.md` | the smallest study that settles generality, with falsification criteria and cost |
| `root_verify.py` | 43 independent recomputations from the frozen records |
| `verify_anchors.py` | 28 prior-work anchor and absence checks against the source PDFs |
| `build_matrix.py` | deterministic matrix builder |
| `verify_freeze.py` | input-freeze integrity check (26,181 files) |
| `abc_prior/`, `agentsuite_prior/` | the two prior-work assessments |
| `policy_mechanism/`, `paired_effects/`, `attribution_evidence/` | the three wave-1 analyses |