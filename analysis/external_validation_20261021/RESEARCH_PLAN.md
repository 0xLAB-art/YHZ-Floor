# External validation: what would strengthen the ACTS-Attack contribution

Status: source preflight executed; validation experiment NOT RUN. This is a prospective design, not a result, preregistration, or a guarantee of acceptance. The existing manuscript and frozen experiments were not edited.

## Target claim and required distinction

The strongest open question is whether a naturally occurring interaction between representation, generated-program form and evaluator admission appears beyond the ACTS fixtures. Running more attribution mutants does not answer it. Transplanting the ACTS import filter onto unrelated benchmark programs would demonstrate a constructed rejection effect; it would not show an independently occurring benchmark defect.

There are three different evidence levels:

1. **External-task portability:** ACTS machinery runs on independently authored tasks. Useful engineering validation, but the evaluator may still be ours.
2. **External evaluator sensitivity:** retained external programs, scored with an unchanged external oracle, receive different admission outcomes under documented policy variants. This tests method portability; without paired representation arms it does not replicate the representation–admission interaction.
3. **Mechanism replication:** paired information-equivalent representations of independent tasks produce programs whose observable form interacts with a documented admission condition, while the same-program correctness and cleanup controls locate that interaction. This directly addresses the central generalizability concern.

## Executed feasibility checks

- Docker server is available (29.8.0).
- Inventoried the existing pinned Cybench and CVE-Bench source archives without extracting or executing their code. `SOURCE_PREFLIGHT_V2.json` records archive and selected-entrypoint hashes, paths, line counts and candidate policy/scoring lines.
- Cybench archive: 7,460 regular files. CVE-Bench archive: 550 regular files, including archive-packaged Git material. These are file counts, not tasks or executions.
- Filename matches for `logs` were inspected: the Cybench matches are application UI files, and CVE-Bench's match is a Git reflog. They do not provide released agent trajectories. Separate external trajectory releases may exist; this archive inventory does not establish their absence everywhere.
- Inspected Cybench's command-executing agent and CVE-Bench's Inspect task/scorer entrypoint. Neither inspected entrypoint supplies evidence of the ACTS-style Python-import admission contract. Do not invent that contract for the purpose of obtaining a positive result.
- Official current sources were checked: [Cybench](https://github.com/andyzorigin/cybench), [CVE-Bench](https://github.com/uiuc-kang-lab/cve-bench), and the [CVE-Bench leaderboard](https://cvebench.com/). Current CVE-Bench supports local Docker targets and exposes evaluation/solution commands; a supported runner command is not evidence that a historical trajectory is replayable.

Reproduce the inventory without overwriting its records:

```sh
python3 sp2027/analysis/external_validation_20261021/preflight.py
```

The first inventory is retained. V2 fixes root-README selection when an archive contains many nested READMEs; it does not change benchmark bytes or scientific results.

## Study A: independent mechanism validation

### Eligibility before outcome inspection

Choose an independent task collection with (a) public, usable inputs and a native correctness checker; (b) an identifiable, documented admission/execution contract; (c) extractable candidate programs and traces; and (d) a representation change that preserves all usable observations and fits that task's interface. Publish the candidate-source inventory and exclusions. Native tool-executing benchmarks need not have a static import gate; if none exists, report that incompatibility rather than impose one and call it native replication.

Select tasks by these criteria and provenance, not by whether a non-zero policy effect is found. Freeze task IDs, source commits, prompt variants, policy bytes, model route and generation parameters before confirmatory runs. Keep screening and calibration separate. The current Cybench/CVE-Bench archive inspection has not yet established a qualifying native policy pair or representation intervention.

### Controls and measurement

- Use information-equivalent R0/R1 inputs with identical instruction content, execution budget and oracle. Verify decoded observation equality before generation. Do not count changing hints, task statements or secret access as representation.
- Retain paired programs, inputs, raw responses, task-oracle verdicts, admission reasons and environment identities. Treat unavailable or invalid executions separately; never silently replace them.
- Re-admit byte-identical programs under the native contract and a provenance-justified variant. Label a mismatch counterfactual as such. A deliberately invented restrictive filter is a stress test, not evidence that the independent benchmark is defective.
- Null control: policy serialization/order changes that preserve decisions. Cleanup control: remove only demonstrably unused material and check observed output and oracle agreement. Neither cleanup nor a null result is discarded.
- Primary contrast: the within-task change in representation contrast caused by admission, with equal predeclared task weights. Resample independent tasks/instances jointly across policy and representation; do not treat multiple programs from a session as independent samples.
- Report correctness, admission, execution and attributed-outcome counts separately. Distinguish unchanged-program regrading from behavior generated under a newly disclosed policy.

### Interpretation fixed before results

| Observation | Permitted conclusion |
|---|---|
| A comparable interaction is observed under an independently justified rule | Evidence that the mechanism extends to the tested independent tasks and contract. Not prevalence across all security-agent evaluations. |
| Interval includes zero | Inconclusive at that precision; not proof that the mechanism is absent. |
| No eligible native gate or representation pairing exists | This candidate cannot answer the exact replication question. It may still support a clearly labeled portability study. |
| Cleanup removes the gap while preserving observed outputs | Supports a syntax/style-mediated admission mechanism. Does not automatically make the effect scientifically irrelevant. |
| Vacuous-policy control changes decisions | Instrument/control failure: investigate and invalidate the affected new analysis. Do not automatically retract a separate old experiment without showing a shared defect. |
| Effect sign or magnitude differs | Report heterogeneity and its mechanism. Do not select only a benchmark/arm matching the original sign. |

## Study B: independent reproduction and comparative value

Prepare a locally reviewable full-replay package with public inputs, submitted programs, reference checkers, policy snapshots, transformations, manifests and complete failure dispositions. Include the import mechanism, paired-policy analysis and attribution-policy dependencies, not only aggregate CSVs. Test reconstruction from a clean environment. Keep original model regeneration distinct from offline program replay. External publication is a separate action; no repository upload is part of this preflight.

For novelty, compare evidence granularity with the nearest work, rather than claiming evaluator defects or fixed-artifact rescoring are new. The useful delta to test is: can the proposed procedure identify *why* an apparent gap appears, preserve the correct capability claim, and specify the evidence needed for the execution claim? The existing configured in-toto agreement supports implementation compatibility, not superiority or replication of the admission result.

## Corrections to the older validation design

`contribution_audit_20261021/VALIDATION_STUDY.md` is historical and remains untouched. Its proposed deliberately weakened rule would not by itself establish a native external mechanism; interval overlap with zero is not falsification; cleanup removing the effect is compatible with the mechanism; and a new control failure cannot invalidate an old independent experiment without a demonstrated shared defect. Its suggestions do not authorize scientific conclusions or supply a completed external validation result.

## Execution boundary

Completed: pinned-source inventory, entrypoint inspection, Docker availability check and this revised design. Pending: a qualifying external policy/task pairing, source-pinned task selection, a prospectively fixed execution budget and model interface if fresh generation is required, and actual paired oracle checks. No hosted calls, benchmark attacks, full replay executions or manuscript-result upgrades were performed in this preflight.
