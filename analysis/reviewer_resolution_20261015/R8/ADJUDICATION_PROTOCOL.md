# Current semantic adjudication protocol

This is the current procedure for the empirical audit. The frozen RUBRIC.md
and first-pass worksheets remain historical evidence. Their planned second
auditor/external annotator steps are not evidence those steps occurred.
No independent human reliability or validated general-method accuracy is claimed.

1. Define the atomic proposition, execution/population, observation unit,
   snapshot and trust model before assigning a disposition. Candidate
   correctness, autonomous acquisition, duration reconstruction and source
   identity are separate propositions. Distinct IDs establish distinct
   recorded executions, not statistical independence.
2. Choose necessary links from the proposition, not a universal all-fields
   conjunction. A duration claim needs a defined clock/window and endpoints;
   a candidate-relation claim needs candidate, reserved relation and verdict;
   a yield claim needs census, terminal statuses and eligibility; historical
   attribution needs linked generating components. Record the selection and
   its rationale. Claims outside these profiles require explicit new rules.
3. Keep semantic status, applicability and source provenance separate.
   An explicit domain-inapplicability note is not missing implementation
   evidence. No note is not affirmative applicability. Do not regrade the
   frozen matrix merely by extracting its notes.
4. Prefer direct source/event/byte relations to a later summary for the
   same narrow proposition. A digest mismatch refutes an exact byte-identity
   claim; it does not automatically refute a different candidate relation.
   Disagreement between equally applicable primary records remains a conflict
   unless a documented authority rule resolves it. Never choose the more
   favorable value merely to obtain support.
5. Require witnesses and explanations for established, refuted and conflicting
   links. A direct counterexample to a necessary condition contradicts the
   proposition. Otherwise missing/conflicting necessary evidence leaves it
   unresolved. All declared links must be established for support. N/A links
   may be omitted only with an applicability rationale; they cannot be counted
   as passing evidence. The checker implements the state reduction, not the
   semantic sufficiency of an author's chosen profile.
6. Preserve original verdicts, summaries, raw data and frozen rubric labels.
   Correct interpretations through separately versioned outputs and exact
   source witnesses. Do not promote source behavior to historical occurrence,
   a fixture to deployed enforcement, or AI agreement to human ground truth.

## Applicability sidecar

`e1_applicability.py` extracts54 existing release/field judgments without
changing summary.csv or RUBRIC.md. It separates three explicit worksheet
domain-N/A notes: AgentHarm F5 generated artifacts, AgentHarm F6 weakness
attribution, and WebSP-Eval F6 weakness attribution. Other51 cells are marked
not separately adjudicated for applicability, not silently assumed applicable.
The semantic Y/P/N display remains the frozen historical matrix; no revised
aggregate quality score is computed. A clock-domain note in AgentHarm's
evidence remains visible but is not silently upgraded to a new N/A rating.

## Reliability and evaluation scope

The R1 replay validates primitive relations and implementation outcomes on
author-selected retained cases; it is not independent annotation. The
published-work inspection remains a bounded source-linked case investigation.
Independent assessor agreement is unmeasured and is not needed to claim the
reproduced byte/count relations, but would be needed to assert reliable
general application of semantic judgments. The manuscript uses the narrower
empirical scope rather than claiming that validation has been performed.
