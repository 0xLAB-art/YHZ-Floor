# Writing clarity and natural prose revision

## Section outline

- Abstract and introduction: the question behind an attack-success label,
  the measurements used to answer it, and the scope of the findings.
- Related work: cryptographic capability, evaluation validity, and execution
  provenance, with the contribution stated beside the relevant comparison.
- Design: task contracts, units, clocks, and the evidence each claim requires.
- Results: matched construction/admission, recovery requirements, target
  consequences, and execution-attribution tests.
- Discussion: what these separate populations establish together and where
  their coverage ends.
- Limitations and conclusion: distinguish retained, reconstructed, and
  recorded-only evidence without repeating the entire result narrative.

## Revised paragraph roles and reverse outline

`REVISED_PARAGRAPHS.md` contains changed prose blocks with explicit roles and
their exact revised LaTeX. `REVERSE_OUTLINE.md` lists the topic sentences of
the active source paragraphs. Roles are editorial annotations outside the
manuscript, not new headings in the paper. Figures, equations and tables
remain in the source; the prose export is not a replacement manuscript.

The key paragraph chain is opening question → independently checked
recovery → admission measurement → construction conditions → attribution
question → contribution and scope. The introduction now gives construction
and attribution their own paragraphs. The policy mechanism and cleanup
control are also separated into paragraphs with distinct purposes.

## Humanizer review

| Pattern or clarity issue | Location | Revision |
|---|---|---|
| Numbered reasoning in running prose | Introduction | Replaced mechanical first/second/third transitions with the actual subject of each finding |
| Summary before content | Design and results openings | Named the question or checked event before discussing section coverage |
| Disclaimer stacking and semicolon chains | Harness controls, policy results, limitations | Used complete sentences and attached each qualification to its relevant claim |
| Excessive parallelism and abstract noun phrases | Discussion and conclusion | Named the program, evaluator decision, or execution record instead of repeatedly listing abstract stages |
| Repeated conclusion | Introduction, discussion and conclusion | Gave each a separate role: introduce, interpret, and state what a reader can infer |
| Undefined study labels | Introduction | Introduced V4 as the prospective cohort and E5 as the escrow study |
| Ambiguous use of candidate | Reproducibility | Renamed the staged artifact candidate to a full package, reserving candidate for the checked value or artifact |
| Dense caption | Import-policy figure | Shortened prose while preserving all displayed numerical tokens |
| Mixed paragraph messages | Introduction and mechanism analysis | Split construction from attribution and import census from mechanism/cleanup |

Humanization here means clearer and more natural academic prose. No claim is
made about human authorship or passing an AI detector. The selected AIGPTZero
app opened an empty workspace; no manuscript was submitted by this revision,
no scan was started, and no score was obtained. The app leaves scanning to
the user. Its scores are not scientific validation of writing or authorship.

## Claim–evidence map

Claim: Cryptographic correctness, admission, and execution attribution can
support different conclusions about a run. | Evidence: fixed-program H1-R3
regrading; E5 committed match with open acquisition; constructed attribution
cases. | Status: supported within the tested settings.

Claim: The primary L3 representation contrasts lie within the pre-specified
margin. | Evidence: 128 matched pairs, retained family split and intervals in
`main_sections/04_capability.tex` and `supp_sections/S26_h1r3.tex`. | Status:
supported for the tested route, families, level, and margin.

Claim: The earlier source filter changes the apparent contrast from -0.8 to
-32.8 points on fixed programs. | Evidence: H1-R3 policy regrading and
`sp2027/analysis/h1r3_20261019/ADMISSION_RULE_PROVENANCE.json`. | Status:
supported as a local contract-mismatch counterfactual.

Claim: Output-preserving import cleanup changes the filtered contrast to
+3.9 points. | Evidence: existing policy-mechanism records and the control
described in Section 4. | Status: supported; the large negative gap disappears.

Claim: Supplied-operation feasibility differs from observed agent
construction. | Evidence: fixed-executor 12/12 and V4 8/12, with separate
contracts and denominators. | Status: supported as two observations, without
a causal estimate from their contrast.

Claim: A supplied AES-CTR chain releases the protected payload. | Evidence:
the retained accepted composition attempt and its target predicate. | Status:
supported as scaffolded execution, not autonomous chain discovery.

Claim: Correct candidates, intact records, or signatures alone may leave
attribution unsupported. | Evidence: E5 and HEB-1/IAR-B/IAR-C cases. | Status:
supported under the stated trust model, not a prevalence estimate.

Claim: The attribution policy has no observed violation in 11,256 bounded
mutation evaluations. | Evidence: recorded property-check corpora and the
attribution section. | Status: supported as bounded testing, not proof or a
new run during this revision.

Claim: Configured in-toto provides another implementation of the policy. |
Evidence: recorded 21/22 agreement, 22/22 with shared replay state. | Status:
supported as configuration/implementation agreement; SLSA remains incomparable.

Claim: The construction and attribution evidence broadens coverage across
interfaces or implementations. | Evidence: the coverage table and existing
scope matrix. | Status: supported with the listed dependencies; independent
benchmark replication of the admission magnitude is not established.

## Five-dimension adversarial self-review

| Dimension | Question | Answer and disposition |
|---|---|---|
| Contribution | Can a reader identify the measured increment without assuming a new general theory? | Yes: fixed-program contrasts, recovery diagnostics, and an evaluated attribution policy. External transfer remains bounded. |
| Writing clarity | Does each revised paragraph have a readable subject and identifiable role? | Reviewed through the reverse outline; split mixed paragraphs and defined study labels before reuse. Technical notation remains intact. |
| Experimental strength | Does polished prose imply causal gains or independent samples that were not tested? | No: V4/explicit/CLI cohorts stay separate, cleanup removes the negative gap, and mutation counts remain bounded test evaluations. |
| Evaluation completeness | Are missing evidence and external replication hidden by the revision? | No: the coverage table, shared constructors/policy assumptions, and partial public replay remain explicit. Writing does not close these scientific limits. |
| Method design soundness | Can the reader distinguish checked output, admission, acquisition, and attribution? | The definitions, policy estimator, E5 account, and attribution checks now state the object of each decision more directly. |

## Consistency edits that affect interpretation

The Checkpoint 009 diagnostic previously presented the original XOR null as
a recovery endpoint without its scorer qualification and described instructed
abstention too strongly. It now links to the already-existing H1 V2 scorer
account in `sec:h1` and identifies abstention as explicitly instructed.
Recorded numbers are unchanged. No raw record was rescored.

The policy-regrading paragraph now says it does not revise the pre-specified
L3 analysis under the declared rule. It no longer suggests that the much
larger counterfactual contrast itself passed the original equivalence margin.
The underlying analyses and numerical results are unchanged.

## Verification and provenance

`before/` and `baseline.json` preserve all 14 active source files before this
pass. `writing_revision.patch` is the exact before/after diff.
`surface_checks.json` records per-file comparisons; `SUMMARY.json` records
their aggregate. Numeric-token multisets, citation arguments, labels, and
displayed equations are preserved. The only added cross-reference points the
Checkpoint 009 account to `sec:h1`.

Research-Paper-Writing and humanizer guidance was applied to the active
LaTeX sources; ARS supplied revision and claim-drift guidance. This is a
local source revision with a before/after record, not a certified ARS
Markdown patch-protocol run or an independent peer-review decision.

Final verification comprises two-pass main and combined LaTeX builds,
reference/warning checks, and inspection of rendered pages. No experiment,
provider call, PoC execution, oracle replay, or evidence reevaluation is part
of this writing pass. Scientific limitations remain those of the completed
experiments.

Final build: 13 main pages including references, 18 pages with the five-page
supplement, US Letter. Final second-pass logs contain no undefined-reference,
LaTeX-warning, or overfull-box messages. The versioned PDF is
`sp2027/paper/capability_revision_20261020/submission_main_plus_supplement_clarity_20261021.pdf`.
