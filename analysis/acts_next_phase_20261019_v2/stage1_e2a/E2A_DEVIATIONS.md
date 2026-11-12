# E2A — Deviations Log

**Stage:** Stage 1 (E2A), `sp2027/analysis/acts_next_phase_20261019_v2/stage1_e2a/`
**Opened:** 2026-10-20, **before** the E2A runner was executed.
**Rule:** this log is append-only. Every deviation from `E2A_PREREGISTRATION.md`
is recorded here with (a) what changed, (b) when it was recorded relative to
execution, (c) whether it could have been outcome-informed. Deviations
discovered **after** execution began are recorded in a clearly separated
section and are marked as **post hoc** — they are reported, never silently
absorbed.

This file is hashed into `E2A_FREEZE.json` and verified by the audited
`heb1_remediation_v1/integrity/manifest_verifier.py` before the run.

---

## Section A — Pre-execution deviations (recorded before any case was run)

### A.1 — Class count in the S2 definition: 9 → 12

* **What.** v1.0 §5 defined S2 with "Maximum = 9 classes present in the case
  set". The realized frozen inventory in `e2a/cases.py` contains **12**
  distinct ground-truth classes.
* **When.** 2026-10-20, before any case was run. Detected by an explicit
  assertion in `tests/test_e2a.py` (case inventory == 22 cases / 6 success /
  16 non-success / 12 classes).
* **Outcome-informed?** No. The class set was frozen in `e2a/cases.py` before
  this amendment and has not changed; only the prereg's *description* of it
  was wrong.
* **Effect on results.** None on any case, label, or metric. The S2
  operationalization is separately amended in §12.3 of the prereg.

### A.2 — S2 re-operationalized (class-level contingency summary)

* **What.** The v1.0 S2 wording ("produces different verdicts for cases with
  different ground truth") is ill-defined for single-case classes. S2 is now
  reported as S2a (uniform classes), S2b (uniform-and-correct classes),
  S2c (non-uniform classes), plus the full class × decision contingency table.
* **When.** 2026-10-20, before any case was run.
* **Outcome-informed?** No.
* **Effect on results.** S2 becomes descriptive rather than a scalar
  discrimination score. The primary metrics (FP/CA/FR/CR) are unchanged.

### A.3 — S1 scope expanded to all 22 cases

* **What.** v1.0 scoped S1 to "the 6 `H_OK` cases and a matched set of
  non-success cases". S1 is now computed for both evaluators over all 22
  cases.
* **When.** 2026-10-20, before any case was run.
* **Outcome-informed?** No. The scope is a superset of v1.0's; it is
  widened so the two evaluators share an identical denominator.
* **Effect on results.** S1 denominators become 22/22 for both evaluators.

### A.4 — Replay classified as REJECT (declared in advance)

* **What.** A replayed record yields `REJECT` with reason family
  `stale_evidence`, not `INCONCLUSIVE`. This is implemented by fixing the
  aggregator's check order so the replay ledger is consulted **before**
  context binding.
* **When.** 2026-10-20, before any case was run.
* **Outcome-informed?** No. The classification was fixed by the semantic
  argument that a consumed context is positive evidence of contradiction, not
  of absence — the same argument used in the HEB-1 remediation adjudication
  notes.
* **Effect on results.** Affects exactly one case (`X_REPLAY`).

### A.5 — Secondary baseline metric `baseline_stage01_end_to_end` added

* **What.** In addition to the validator-only baseline metric, the frozen
  reference verifier's verdict is reported for every case, and a combined
  "validator ACCEPT **and** reference ACCEPTED" metric is published.
* **When.** 2026-10-20, before any case was run.
* **Outcome-informed?** No.
* **Effect on results.** Adds one reported metric; does not alter the primary
  comparison. Purpose: prevent the comparison from being accused of
  strawmanning the baseline by ignoring the reference verifier Stage01 ships
  with.

### A.6 — Representation fixed to C1 (C0 only for the underdetermined case)

* **What.** All cases use the canonical C1 representation; `H_UNDET_EC_01`
  uses C0.
* **When.** 2026-10-20, before any case was run.
* **Outcome-informed?** No.
* **Effect on results.** None. Representation equivalence was already
  established at Stage 0 and is orthogonal to the attribution question.

### A.7 — Strict output rule ablation declared uninformative for this run

* **What.** E2A's strict output rule (exactly one non-empty stdout line
  parsing as a JSON object) is compared against the historical last-line rule
  as an ablation, but the 22-case inventory contains no multi-line output, so
  the ablation cannot discriminate.
* **When.** 2026-10-20, before any case was run.
* **Outcome-informed?** No. The absence of multi-line output is a property
  of the frozen producer variants, fixed before the run.
* **Effect on results.** The ablation is reported as **uninformative in this
  run**, explicitly as a limitation and explicitly not as a finding. A
  discriminating case was **not** added post hoc.

### A.8 — Replay-state snapshot cloning for the S1 pair

* **What.** The S1 pair runs against an aggregator whose replay ledger is a
  snapshot clone of the primary aggregator's ledger, taken by copying the
  audited `ReplayState._uses` mapping and by passing no ledger path so the
  clone never appends to `replay_ledger.jsonl`.
* **When.** 2026-10-20, before any case was run.
* **Outcome-informed?** No.
* **Effect on results.** S1 pair evaluated under the same ledger state as the
  primary evaluation.

### A.9 — `E2A_DEVIATIONS.md` included in the freeze manifest

* **What.** This file is declared as a hashed component of `E2A_FREEZE.json`
  so its content is pinned by the audited manifest verifier. It is placed at
  the stage root and **not** inside `frozen/cases/`, because the audited
  `manifest_verifier` rejects unexpected files in the case-inventory root and
  rejects any file that overlaps a declared component.
* **When.** 2026-10-20, before the manifest was written.
* **Outcome-informed?** No.

### A.10 — Re-scoping of Objective 1 following the independent prior-art review

* **What.** An independent prior-art/novelty review completed before the run
  determined that the "previously unknown security mechanism" framing is
  **foreclosed** by published specifications (RFC 9334 §8.1/§10/§12, in-toto
  v1.0.0, SLSA v0.2/v1.0, TUF v1.0.37, Sigstore/cosign) and by published
  measurements (TRAP/ReplayBench arXiv:2610.16333; arXiv:2610.16067;
  RewardHackingAgents arXiv:2603.11337). The E2A experiment is accordingly
  scoped to a **Class C measurement** claim, not a novelty claim. Objective 1
  of the master programme is assessed **NOT_AVAILABLE** independently of any
  E2A outcome, and E2A results are inadmissible as support for it.
* **When.** 2026-10-20, before any case was run.
* **Outcome-informed?** No. The review was conducted on published literature
  and did not depend on any E2A measurement.
* **Effect on results.** Changes the *claim* the experiment may support, not
  the measurements it produces. Recorded in full in prereg §12.10.

### A.11 — Baseline scope clarification (Stage01 is not a provenance baseline)

* **What.** The comparison is between two contracts implemented inside this
  system. It supports **no** claim about in-toto, SLSA, TUF, or Sigstore,
  which are not executed in Stage 1.
* **When.** 2026-10-20, before any case was run.
* **Outcome-informed?** No.
* **Effect on results.** Narrows the reportable inference; recorded in
  prereg §12.11.

---

## Section B — Deviations discovered during the run

*(none yet — the run has not started)*

---

## Section C — Post hoc deviations (discovered after execution began)

*(none yet)*
