# R1: executable claim assessment and retained-case comparison

This is a retrospective addition responding to the simulated review of 15 October 2026. The cases and expected conclusions were selected after inspecting the evidence. They are not preregistered, blinded, independent human annotations, or a new model experiment.

## Scope and scientific object

The implementation's object is a proposition about specified retained executions under named trust assumptions. It does not assign one quality score to an entire benchmark. Its output is the proposition, assumptions, required links, source witnesses, decisive links and supported/unresolved/contradicted disposition. The demonstrated result is a reproducible separation of claims on the same records, including contradictory metadata and effort claims alongside an accepted candidate. It is not a new general theory of evidence, a demonstrated improvement over all benchmark auditing tools, or an estimate of future benchmark quality.

The project implementation is `ACTS-ATTACK/harness/evidence_claims.py`. `replay.py` loads primary evidence from the nested checkout and the outer uncommitted agent-evaluation directories. `INPUTS.json` pins all 35 input/source files before replay. Source drift or a changed input set stops replay. No retained file is repaired or overwritten. The replay writes only its own `REPLAY.json`.

## Decision rules

1. State an atomic proposition with a bounded execution set, observation unit and explicit measurement trust assumptions. A log-content proposition and an access-isolation proposition are different claims.
2. Name required links before evaluating the case. These are author-specified semantic requirements, not automatically discovered ground truth. The eight profiles below define the replay's complete scope.
3. Give each required link one state: established, missing, refuted, or conflict. Nonmissing states require an inspectable source witness and explanation. Absent required links become missing; arbitrary labels and unsupported nonmissing assertions are rejected.
4. An authoritative direct counterexample to a necessary condition yields contradicted. Otherwise a missing link or unresolved conflict yields unresolved. Support requires every declared link to be established. A conflict at a link is unresolved, not automatically refuted.
5. Apply only the chosen proposition's required links. A missing duration endpoint does not become an oracle rejection, and an unrelated verifier-hash defect does not negate a directly checked commitment match.
6. Byte hashes establish source identity. They do not establish historical execution, instrumentation honesty, semantic correctness of the author-selected requirement set, independent assessor reliability, or statistical independence of distinct run IDs.

`assess` consumes evidence states; it does not authenticate truth from an arbitrary caller. `replay.py` is the adapter that actually computes the stated primitive relations from pinned records. The trust boundary includes that adapter and recorder. Its source and assumptions are part of the inspected evidence.

## Case profiles and primitive checks

| Claim ID | Bounded proposition | Required links and computation | Disposition |
|---|---|---|---|
| clean_checked_count | Eight accepted submissions in the frozen 12-session cohort | 12 unique record IDs equal INDEX IDs; one terminal event per transcript; terminal and record verdict agreement; every accepted record has run.code, claim and an accepted run verdict | Supported |
| clean_all_succeed | All 12 terminal sessions have accepted candidates | Same cohort census and all accepted; four nonaccepted terminal sessions provide counterexamples | Contradicted |
| clean_duration_recomputation | All eight successful harness durations can be recomputed from raw monotonic endpoint pairs | Declared clock schema plus retained harness raw start/stop readings in each accepted record; elapsed differences and oracle spans are not substituted | Unresolved |
| r30_commitment | Submitted 128-bit candidate matches a pre-session secret commitment | Submitted candidate equals escrow candidate; recomputed digest equals escrow digest and original commitment; logged generation precedes first transcript event, which precedes verification | Supported |
| r30_no_logged_reveal | Retained R30 escrow log contains no reveal | Inspect every escrow event for op=reveal; explicitly a log-content claim | Supported |
| r30_retained_verifier_identity | Recorded verifier digest identifies retained V2 verifier source selected by launcher | Compare recorded digest to retained V2 source bytes; also identify matching older source; launcher selection is source-inspected, not historical runtime reconstruction | Contradicted |
| r30_tail_is_total | Terminal 2,000-entry array is total relay effort | Count retained entries and http_request_log eviction events under source-inspected one-entry eviction rule | Contradicted |
| r30_reconstructed_effort | Records reconstruct 8,714 relayed HTTP calls | 2,000 tail entries plus 6,714 one-entry evictions; not arbitrary host or provider requests | Supported |

The raw endpoint absence is scoped to the declared harness schema and existing endpoint audit. This is not a claim that no conceivable timestamp can be recovered from any future source. The effort reconstruction assumes complete retained eviction events and the pinned recorder's eviction semantics. The source adapter does not prove those assumptions independently.

The cases are related propositions on two evidence settings, not eight independent experiments. The outcomes 4/1/3 are software replay dispositions, not performance rates, accuracy estimates or confidence intervals. Expected outcomes are author-derived regression expectations; matching them is not independent semantic validation.

## Same-case application of prior guidance

The baseline is an author application of selected relevant [ABC checklist items](https://arxiv.org/html/2507.02825v1), not a full ABC score and not a run of its original authors' evaluation. ABC already addresses tool/API availability, ground-truth separation, frozen environments and interpretation of results. No absence of those concerns in prior work is claimed.

| Retained case | Relevant ABC items and author application | Executable assessment on the same evidence | Difference demonstrated |
|---|---|---|---|
| Clean cohort | T.6: immutable runtime unresolved. R.11: elapsed durations require qualification. Task outcomes remain inspectable. | Candidate count supported; universal success contradicted; raw duration reconstruction unresolved. | Preserves separate execution-level decisions and their exact witnesses rather than collapsing them into a benchmark-wide deficiency. This is a reporting representation, not superior error detection. |
| R30 accepted candidate and actual launch path | T.5: protected ground-truth isolation not demonstrated by host execution and unauthenticated delivery. T.6: victim digest alone does not freeze the complete runtime. | Commitment relation supported; retained-verifier-digest proposition contradicted; no-logged-reveal supported only as log contents. | A supported correctness relation coexists with a demonstrably wrong metadata link and an unresolved stronger attribution claim. ABC is compatible with the same conclusions. |
| R30 effort record | R.11: distinguish log coverage from effort accounting when interpreting a reported count. | Tail-as-total contradicted; 8,714 relay calls supported under source-inspected eviction semantics. | Computes the corrected quantity and retains both the refuted proposition and supporting event witnesses. No claim that ABC could not motivate this calculation. |

The minimal single-status alternative loses these distinctions: rejecting the entire R30 record for its wrong metadata would discard a directly checked candidate relation; accepting every claim because its terminal status is SUCCESS would retain a false verifier identity and a false effort count. This is an explicit representation counterexample, not an experiment claiming an existing auditor makes either mistake.

[BenchJack](https://arxiv.org/html/2605.12673v1) is a closer precedent for identifying answer-access and isolation mechanisms and constructing reward hacks. This work does not reproduce that pipeline or compare hack-finding rates. [AgentSuite/COBA](https://proceedings.mlr.press/v306/suh26a.html) is a closer precedent for component-level issue diagnosis. This work does not reproduce its expert-alignment evaluation. The retained-case replay supplies execution-specific proposition witnesses; it is complementary to both approaches. Their omission of this exact repository adapter is not evidence that the representation is scientifically novel.

## Reproduction

From the outer project root:

```bash
python -m unittest discover -s ACTS-ATTACK/harness -p test_evidence_claims.py -v
python sp2027/analysis/reviewer_resolution_20261015/R1/replay.py
```

The first execution uses `--freeze-inputs` exactly once to create INPUTS.json with exclusive creation. Subsequent replay must use the existing pins. Do not regenerate the input manifest merely to make changed evidence pass. The output does not expose candidate secrets.

## What this resolves and what it cannot resolve

This addition supplies the missing executable decision rule, witness-bearing output, retained-case replay and same-case analytic comparison requested by R1. It makes a concrete, bounded contribution reviewable. It does not establish that the contribution is sufficiently novel or significant for S&P. That is a scientific judgment requiring critical evaluation; no unit test, self-review or wording change can certify it at 100%.

R1 must remain open if the closure condition is proof of sufficient research novelty rather than completion of these concrete revision requirements. Later findings must not be marked resolved or silently started on the basis of this engineering result. In particular, this work has not corrected E3, changed old denominators, hardened escrow, or altered historical records.

## Subsequent contribution decision

After the user delegated the direction with “do the best,” the manuscript
was revised as an empirical audit with the checker as supporting tooling.
`CLOSURE.md` records the resulting R1 disposition and its scope. The earlier
open-status discussion above documents the decision point; it is not a claim
that a software replay proved a sufficiently novel general auditing method.
