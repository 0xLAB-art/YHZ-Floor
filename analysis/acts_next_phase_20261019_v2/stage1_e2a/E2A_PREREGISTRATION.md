# E2A — End-to-End Attribution with a Trusted Execution Observer

**Preregistration**
Version 1.0 — written 2026-10-20, before any confirmatory execution.
Version 1.1 — amended 2026-10-20, **before any confirmatory execution** and before
any case was run. The v1.0 body text below is left **verbatim**; every change is
recorded in **§12 (Amendment v1.1)** and cross-marked inline with
`[AMENDED IN v1.1 — §12.x]`. No v1.0 text was deleted or rewritten.
Working directory: `sp2027/analysis/acts_next_phase_20261019_v2/stage1_e2a/`

---

## 0. Status and scope

This document is frozen **before** the E2A runner is executed. It states the
hypotheses, the complete case inventory, the metric definitions, the analysis
rules, and the stopping rules. No metric may be redefined after inspecting any
outcome. Any deviation is recorded in `E2A_DEVIATIONS.md` and reported.

**This is a local, offline, authorized, constructed evaluation experiment.**
It measures the *discriminating power of evaluator contracts*. It is **not**
an exploit against a deployed service, **not** a live-campaign result, and
**not** evidence of deployed attacker reachability. No network egress, no
third-party target, and no model provider call occurs.

The prior multi-agent line concluded
`NO_EXTERNAL_CERTIFICATE_COMPOSITION_INTERFACE_FOUND_IN_INSPECTED_REPOSITORY_PATHS`.
This experiment does not attempt to overturn that; it operates strictly inside
the local evaluation boundary.

---

## 1. Problem statement

The Stage01 contract-sound pipeline (`sp2027/analysis/run_contract_sound_agent_pilot.py`)
produces a certificate whose `claims` block asserts attribution. The frozen
public validator (`contract_sound_stage01_validator_v2.py`) checks that the
assertion is *well-formed* and that the evidence files' digests match digests
**listed inside the same certificate**. The frozen reference verifier
(`contract_sound_stage01_reference_verifier_v2.py`) recomputes the
cryptographic predicate from the private target state and a *candidate output
file on disk*.

The historical correction ledger (`heb1_remediation_v1/scientific_corrections/HISTORICAL_CORRECTION_LEDGER.md`,
C-03) records the resulting gap: **no component binds the executed program
source to the runtime output that the cryptographic predicate consumed.** The
`agent_artifact` record names program source; the reference verifier consumes a
separate output file. Nothing in either component asserts that the second was
produced by executing the first.

This experiment asks a narrower, testable question than "is there a
vulnerability":

> Under a declared contract, **which claims does each evaluator permit to be
> promoted to a success attribution, and how much of that decision is
> determined by the underlying evidence rather than by the claimant's own
> assertion?**

---

## 2. Hypotheses

**H1 (causal-binding).** An evaluator that verifies a complete causal chain
(program source bytes → execution event → captured runtime output → parsed
candidate output → independent cryptographic predicate), with every link
bound to a single `(target_id, attempt_id, epoch, role, kind)` context and
signed by an authorized issuer, will issue an attributed-success claim for a
strict subset of the cases on which the Stage01 validator issues one, and
will do so without relying on any digest supplied by the claimant.

**H2 (declaration sensitivity).** The Stage01 validator's decision is a
function of the claimant's own `claims` assertions, not of the underlying
evidence. Two Stage01 certificates that reference **byte-identical evidence
files** and differ only in the claimant's `claims` block will receive
**different** verdicts, with the "accepted" verdict obtainable by setting
`claims.attribution = "PROVEN"`. The E2A evaluator's verdict is **invariant**
to the claimant's assertion for the same underlying evidence.

**H3 (honest-error discrimination).** The Stage01 validator accepts a
certificate asserting success over a case whose cryptographic predicate is
*false* whenever the evidence hashes are internally consistent. The E2A
evaluator rejects it, and classifies it as a contradiction (REJECT) rather
than as missing evidence (INCONCLUSIVE).

**H4 (non-regression).** The E2A evaluator issues an attributed-success claim
for every honest, complete, valid case (the H_OK family) — i.e. its rejection
rate on honest success is zero — while its false-promotion rate over the
non-success family is zero.

**H0 (null).** The E2A evaluator's decisions are explained by the
claimant's assertions and the equality of digests in attacker-editable
records, i.e. the added causal chain contributes no discriminating
information.

**Directional predictions.** H1, H2, H3, H4 predict E2A dominance. H0 is
refuted if E2A separates cases that Stage01 conflates.

---

## 3. System under test (SUT)

### 3.1 E2A evaluator (new, this experiment)

Four components, each a separate process where the trust boundary matters:

| Component | Role | Trust assumption |
|---|---|---|
| `e2a/observer.py` | **Trusted Execution Observer (TEO)** | Trusted to observe execution. Writes the program bytes, executes them, captures stdout/stderr, parses the candidate output **from its own capture**, and emits a signed observation record. |
| `e2a/reference.py` | Independent reference adjudicator | Trusted to hold private target state and to recompute the cryptographic predicate. Consumes the *captured stdout* pinned by the TEO's signed digest — never an unreferenced output file. |
| `e2a/aggregator.py` | Final claim adjudicator | Trusted to aggregate. Verifies signatures, role/kind/context authorization, the full causal chain, and the replay ledger; then issues the final claim. |
| `e2a/producers.py` | **Untrusted producer** | Not trusted. Emits a program source. May not be trusted with any evidence, digest, or claim. |

**Source-execution binding.** The TEO creates an anonymous in-memory file
(`memfd`), writes the program bytes into it, computes SHA-256 over exactly
those bytes, and executes the interpreter against `/proc/self/fd/<n>` with
the descriptor inherited (`pass_fds`). The bytes that are hashed are
therefore provably the bytes that are executed; the path-based
write-then-hash-then-execute TOCTOU window of the production runner is
removed. This is verified by an explicit test
(`tests/test_e2a.py::test_memfd_execution_binds_hashed_bytes`).

**Isolation.** Execution uses `python -I` (isolated mode: no user site, no
`PYTHON*` env vars, `sys.path[0]` removed), a minimal environment
(`PATH`, `PYTHONHASHSEED=0`, `PYTHONIOENCODING=utf-8`), an empty working
directory containing only the program and the public instance, a timeout, and
no network namespace isolation (residual risk documented in §9).

**Signed evidence.** All evidence records are Ed25519-signed with
role/kind/context authorization, reusing the audited remediation primitives
at `heb1_remediation_v1/signing/protected_signing.py` (fresh random keys,
`O_EXCL` creation, 0600 private key files, no symlinks, `IssuerPolicy`
authorization of role → (kind, context)). Three issuer roles are used:
`execution_observer`, `reference_verifier`, `aggregator`.

**Replay.** The aggregator consults an explicit in-memory `ReplayState`
(the remediation `context_validator.ReplayState`), keyed on the six-field
context. Replay protection is therefore present exactly where the caller
supplies it, and its presence is asserted, not assumed.

### 3.2 Baseline (frozen, unmodified)

* `sp2027/analysis/contract_sound_stage01_validator_v2.py` — invoked
  exactly as production invokes it (certificate JSON on stdin, verdict JSON on
  stdout). **Not modified, not re-implemented, not re-derived.** The file is
  hashed into the freeze manifest and re-verified after the run.

The baseline is a *full-attribution-only* validator: it accepts only
certificates asserting `claims.attribution == "PROVEN"`. Every case in this
study asserts a full-attribution claim, so the baseline is **directly
comparable** on this case set; the historical unfairness of counting
rejected partial claims against a full-attribution validator does not apply
here.

### 3.3 Comparability statement

The two evaluators do **not** implement the same contract. That is the object
of study, not a confound to be hidden. The comparison is therefore framed as:

> Given the same underlying facts, **how many of the ground-truth
> non-success cases does each contract permit to be promoted to a success
> attribution?**

Each evaluator is given its **best-case valid input** for every case. For
the baseline this means the certificate is fully well-formed, all evidence
digests are internally consistent, and the claimant asserts success — i.e.
the baseline is never handicapped by malformed input. Any observed difference
is a difference in *contract coverage*, not in input quality.

---

## 4. Case inventory (frozen, 22 cases)

Ground truth is fixed by the case **definition** in `e2a/cases.py` before
execution, and is independently re-derived after execution by
`e2a/adjudicate.py` from the case definition plus an *objective* semantic
recomputation (the program is re-read from the retained artifacts and its
claimed solution is checked against the private target state using an
implementation independent of both evaluators).

Target instances: `ECDSA_Nonce_Reuse` and `ChaCha20_Nonce_Repeat`,
generated by the frozen generator `run_contract_sound_stage01.py`
(`make_ecdsa` / `make_chacha`), seeds 1–3. These are the same synthetic
primitives as the historical campaign, so the cryptographic predicates are
real (real curve arithmetic, real ChaCha20) and fully reproducible.

| # | case_id | Class | Ground truth | Construction |
|---|---|---|---|---|
| 1 | `H_OK_EC_01` | honest_success | attributable | Correct solver for ECDSA seed 1 |
| 2 | `H_OK_EC_02` | honest_success | attributable | Correct solver for ECDSA seed 2 |
| 3 | `H_OK_EC_03` | honest_success | attributable | Correct solver for ECDSA seed 3 |
| 4 | `H_OK_CH_01` | honest_success | attributable | Correct solver for ChaCha seed 1 |
| 5 | `H_OK_CH_02` | honest_success | attributable | Correct solver for ChaCha seed 2 |
| 6 | `H_OK_CH_03` | honest_success | attributable | Correct solver for ChaCha seed 3 |
| 7 | `H_BAD_EC_01` | honest_crypto_failure | not attributable | Runs cleanly, prints well-formed but **cryptographically wrong** `d`/`k` |
| 8 | `H_BAD_EC_02` | honest_crypto_failure | not attributable | Wrong `d`/`k`, seed 2 |
| 9 | `H_BAD_CH_01` | honest_crypto_failure | not attributable | Well-formed but wrong `plaintext_2` |
| 10 | `H_BAD_CH_02` | honest_crypto_failure | not attributable | Wrong `plaintext_2`, seed 2 |
| 11 | `H_FAIL_EC_01` | honest_execution_failure | not attributable | Program raises → non-zero exit |
| 12 | `H_FAIL_CH_01` | honest_execution_failure | not attributable | Program raises → non-zero exit |
| 13 | `H_MALFORMED_EC_01` | honest_malformed_output | not attributable | Prints non-JSON text |
| 14 | `H_UNDET_EC_01` | honest_underdetermined | not attributable | Correctly reports `UNDERDETERMINED` (no unique target) |
| 15 | `M_MISSING_OBS` | missing_evidence | not attributable | Observer evidence record removed before aggregation |
| 16 | `M_MISSING_REF` | missing_evidence | not attributable | Reference evidence record removed before aggregation |
| 17 | `X_IDENTITY` | identity_mismatch | not attributable | Certificate's `agent_artifact` names a **different program** than the one executed; all digests internally consistent |
| 18 | `X_OUTPUT_SWAP` | output_substitution | not attributable | The candidate output consumed by the reference is a file from a **different run**; certificate digests updated to match |
| 19 | `X_STALE_ATTEMPT` | stale_attempt | not attributable | Evidence from attempt A presented under attempt B; attempt/epoch fields made internally consistent |
| 20 | `X_CONTEXT_CONFLICT` | context_conflict | not attributable | Observer record signed for a different `(target, attempt, epoch, role)` than the claim it is used to support |
| 21 | `X_REPLAY` | replay | not attributable | A previously consumed observation record is replayed under a new claim |
| 22 | `X_REF_MISMATCH` | reference_mismatch | not attributable | Reference record reports predicate true but pins a *different* stdout digest than the observer recorded |

**Case-class semantics.** Cases 15–22 are **constructed defensive test
fixtures** for the evaluator. They are *not* claims about a deployed
attacker capability, and they are *not* routed through any live campaign
path. Their role is to measure whether each contract can distinguish the
underlying facts. This framing is fixed here, before execution, and will not
be revised after seeing results.

**[AMENDED IN v1.1 — §12.1] Class count.** The v1.0 text did not state a
total class count. The realized inventory contains **12 distinct
ground-truth classes**, not 9:
`honest_success`, `honest_crypto_failure`, `honest_execution_failure`,
`honest_malformed_output`, `honest_underdetermined`, `missing_evidence`,
`identity_mismatch`, `output_substitution`, `stale_attempt`,
`context_conflict`, `replay`, `reference_mismatch`.
The class *set* above is the one frozen in `e2a/cases.py` and is
authoritative.

**Denominators.**
* `n_success` = 6 (cases 1–6) — denominator for false-rejection rate.
* `n_non_success` = 16 (cases 7–22) — denominator for false-promotion rate.
* Sub-denominators are reported per class, and always with the class
  definition restated.

**Balanced-design note.** 6 vs 16 is not a hypothesis about prevalence; the
cases exist to characterize *discrimination*, not to estimate a population
false-promotion rate. No population-level rate is claimed from these
denominators.

---

## 5. Metric definitions (frozen)

For each case *c* and evaluator *E*:

* `decision(c, E) ∈ {ATTRIBUTED_SUCCESS, REJECT, INCONCLUSIVE}`.
* `gt_success(c) ∈ {true, false}` — from the frozen case definition.

| Metric | Definition | Denominator |
|---|---|---|
| **False promotion (FP)** | `decision = ATTRIBUTED_SUCCESS` and `gt_success = false` | `n_non_success` = 16 |
| **Correct attribution (CA)** | `decision = ATTRIBUTED_SUCCESS` and `gt_success = true` | `n_success` = 6 |
| **False rejection (FR)** | `gt_success = true` and `decision ∈ {REJECT, INCONCLUSIVE}` | `n_success` = 6 |
| **Correct refusal (CR)** | `gt_success = false` and `decision ∈ {REJECT, INCONCLUSIVE}` | `n_non_success` = 16 |

`REJECT` and `INCONCLUSIVE` are reported separately **and** combined:

* `REJECT` — the retained evidence **contradicts** the claim (e.g. the
  cryptographic predicate is false; a digest does not match).
* `INCONCLUSIVE` — required evidence is **absent or unverifiable** (e.g. a
  required record is missing, its signature does not verify, or its context
  does not match). Per the remediation adjudication rule, missing evidence is
  **never** recorded as a zero-failure; it is INCONCLUSIVE and is excluded
  from the contradiction count.

**Secondary metrics.**

* **S1 — Declaration sensitivity.** For each of the 6 `H_OK` cases and a
  matched set of non-success cases, the baseline is evaluated twice on
  **byte-identical evidence files**: once with `claims.attribution =
  "PROVEN"` and once with `claims.attribution = "NOT_ESTABLISHED"`. The
  metric is the number of cases whose verdict changes solely because the
  claimant changed the assertion. The same pair is evaluated for the E2A
  evaluator, where the claimant's assertion is not an input at all (the
  aggregator derives the claim); the E2A expected result is **0 changes**
  and a non-zero value falsifies H2.
  **[AMENDED IN v1.1 — §12.2]** S1 is evaluated over **all 22 cases**, for
  both the baseline and the E2A evaluator (a superset of the v1.0
  "6 `H_OK` + matched set").
* **S2 — Discrimination index.** The number of distinct ground-truth classes
  that the evaluator separates (i.e. produces different verdicts for cases
  with different ground truth). Maximum = 9 classes present in the case set.
  **[AMENDED IN v1.1 — §12.3]** "Maximum = 9 classes" is **superseded**: the
  realized class count is **12** (§12.1). The v1.0 sentence is also
  ill-defined for classes containing a single case, because a single case
  cannot exhibit "different verdicts" within its class. S2 is therefore
  **operationalized** as: (a) number of ground-truth classes on which the
  evaluator's decision is **uniform**; (b) number of classes on which the
  decision is uniform **and** correct (i.e. the uniform decision matches the
  class's ground truth); (c) number of classes that are **non-uniform**; plus
  the full per-class contingency table (class × decision). "Discriminates
  correctly" is read as: uniform **and** correct on every class.
* **S3 — Chain-completeness coverage.** The number of the 15 required
  objects in §6 that the evaluator's contract *can* bind, counted by
  inspection of the evaluator source, with file:line evidence.

**Confidence intervals.** Wilson score intervals at 95% are reported for all
four primary rates per evaluator. With n = 6 and n = 16 these intervals are
wide and are reported as such; **no inferential claim is made beyond these
finite case sets.** No p-value is reported for a rate difference, because the
cases are not a random sample of any population.

---

## 6. Required objects (frozen list of 15)

The E2A contract binds, and records a digest for, each of:

1. producer identity (scripted producer label + producer nonce)
2. exact program source bytes + SHA-256
3. exact executed program bytes (identical to 2 by construction; enforced)
4. invocation command + arguments
5. execution environment identity + interpreter version/digest
6. input / public-instance digest
7. target identity + target state digest
8. execution attempt id + epoch
9. actual captured stdout + stderr
10. parsed candidate output + its digest
11. trusted execution-observer record (signed)
12. independent cryptographic reference result (signed)
13. signed evidence records with explicit issuer identity + role
14. aggregated certificate
15. final attributed-success claim

The **trusted component** is the TEO (§3.1). No chain link is a digest
supplied by the untrusted producer.

---

## 7. Procedure (frozen)

1. Write this preregistration; hash it.
2. Write the case inventory; hash it.
3. Write the evaluator, runner, and adjudicator source; hash all of it.
4. Write the freeze manifest (`E2A_FREEZE.json`) covering: protocol,
   preregistration, case inventory, all component source, the baseline
   validator (hash-pinned to the frozen file), the adjudication script, the
   trust material, and the expected case inventory contents.
5. Run the **integrity preflight** using the audited remediation component
   `heb1_remediation_v1/integrity/manifest_verifier.py` (fail-closed). A
   preflight failure aborts the run; the preflight report is retained.
6. Execute the case set. Every attempted case is preserved, including
   failures. Raw stdout/stderr/return codes are retained per case.
7. Run the **independent adjudicator** (`e2a/adjudicate.py`) over the raw
   artifacts only, computing the frozen metrics.
8. Re-verify the freeze manifest after execution and confirm no declared
   file changed. Record the post-run verification report.
9. Write the results report from the adjudicated metrics only.

**No step may be repeated with a different configuration.** There is one
run. If a component crashes, the crash is recorded as the case outcome; it
is not re-run with a patch.

---

## 8. Controls

* **Positive control** — the 6 `H_OK` cases must yield `ATTRIBUTED_SUCCESS`
  from E2A. If they do not, the E2A evaluator is not operational and the run
  is reported as failed rather than as a negative result.
* **Negative controls** — the honest-error family (7–14) must not be
  promoted.
* **Cross-implementation check** — the E2A reference predicate and the frozen
  Stage01 reference predicate must agree on every case where both are
  computable. Disagreement is reported as a validity failure, not silently
  reconciled.
* **Positive control for the baseline** — the baseline must return `ACCEPT`
  on at least one honest case; if it never accepts, the comparison is void
  (the baseline would be measuring nothing).
* **Claim-invariance control** — the E2A aggregator's decision must be
  invariant to the claimant's assertion (S1).

---

## 9. Threats to validity (declared in advance)

1. **Constructed cases.** The case set is authored, not sampled. Results
   characterize *contract discrimination*, not a population rate.
2. **No deployed reachability.** Nothing here shows an attacker can reach
   this path in a live campaign. The historical negative finding stands.
3. **Residual TOCTOU on the interpreter.** The program bytes are bound
   exactly (memfd), but the *interpreter binary* and the public instance
   file are hashed, not executed-from-memory. The instance is written by the
   TEO into the case directory and re-hashed after execution; a residual
   window remains and is stated, not hidden.
4. **No namespace isolation.** Execution has no network namespace and no
   resource limits beyond a wall-clock timeout. The TEO restricts the
   program's *interface* (argv, minimal env, cwd) and the program is
   statically screened for disallowed imports/attributes, but a hostile
   program is not sandboxed as a hostile program would be in production.
   This experiment does not test sandbox escape.
5. **In-memory replay ledger.** Not durable and not atomic across processes.
   The aggregator is single-process in this study; cross-process replay
   resistance is NOT tested.
6. **Not a production PKI.** Keys are local files; there is no revocation,
   epoch rollover, or transparency log.
7. **The producer arm is scripted, not a model.** Stage 4 (AI vs scripted) is
   a separate, conditional stage. This stage isolates the *evaluator*.
8. **Baseline asymmetry.** The baseline lacks fields the E2A contract
   requires. The comparison is framed as contract coverage, not as a
   head-to-head score.

---

## 10. Stopping and reporting rules

* One run. No re-runs with modified configuration.
* All cases, including unexpected outcomes, are reported.
* If the positive controls fail, the stage is reported as **NOT OPERATIONAL**
  and no comparative claim is made.
* If the baseline never accepts an honest case, the comparison is reported as
  **VOID** and no comparative claim is made.
* Negative results are reported as negative results, with the same
  prominence as positive ones.

---

## 11. Analysis rules (frozen)

* The adjudicator reads **only** retained artifacts. It must not import
  evaluator-internal state or reuse the runner's in-memory objects.
* Every reported number must be traceable to a case-level row in
  `raw_results.jsonl` and, for crypto outcomes, to an independent
  recomputation.
* Exploratory observations discovered during analysis are labeled
  **exploratory** and are not confirmatory.
* The raw results file is append-only and is the authoritative record.

---

## 12. Amendment v1.1 (2026-10-20, pre-execution)

**Status.** This amendment was written **before** the E2A runner was executed
and before any case was run. It records (a) corrections to v1.0 wording, and
(b) a re-scoping decision forced by an independent prior-art review completed
before the run. No v1.0 text was deleted or silently rewritten; superseded
sentences are marked inline with `[AMENDED IN v1.1 — §12.x]`.

### 12.1 Class-count correction

The realized inventory contains **12** distinct ground-truth classes, not the
"9" stated in the v1.0 S2 definition. Authoritative list (frozen in
`e2a/cases.py`):

`honest_success`, `honest_crypto_failure`, `honest_execution_failure`,
`honest_malformed_output`, `honest_underdetermined`, `missing_evidence`,
`identity_mismatch`, `output_substitution`, `stale_attempt`,
`context_conflict`, `replay`, `reference_mismatch`.

Case count (22), class assignment, and ground-truth labels are **unchanged**
from v1.0.

### 12.2 S1 evaluated over all 22 cases

S1 (declaration sensitivity) is computed for **both** the baseline and the E2A
evaluator over **all 22 cases**, superseding the v1.0 scope ("6 `H_OK` cases
and a matched set of non-success cases"). This is a superset of the v1.0
scope, not a substitution, and it makes the two evaluators directly
comparable on the same denominator.

### 12.3 S2 operationalization

The v1.0 definition ("produces different verdicts for cases with different
ground truth", maximum 9) is **ill-defined** for classes containing a single
case: a one-case class cannot exhibit within-class verdict variation, and
"separated" does not specify the required direction. S2 is therefore reported
as a **class-level contingency summary**:

* **S2a** — number of ground-truth classes on which the evaluator's decision
  is **uniform** (all cases in the class receive the same decision);
* **S2b** — number of classes on which the decision is uniform **and correct**
  (the uniform decision is the decision the ground truth requires for that
  class);
* **S2c** — number of classes that are **non-uniform**;
* **S2-table** — the full class × decision contingency table, per evaluator.

The headline discrimination statement is "uniform **and** correct on every
class" (S2b = 12). S2a/S2b/S2c are **descriptive**, and S2 alone is **not**
evidence of superiority; superiority requires the primary FP/CA/FR/CR metrics
in §5 together with S1 and S3.

### 12.4 Replay classification declared in advance

A replayed record is classified **REJECT** (reason family `stale_evidence`),
not INCONCLUSIVE. The aggregator's fixed check order evaluates the replay
ledger **before** context binding, so a record whose signed context has
already been consumed is rejected as contradicted-by-evidence (the ledger
contains positive proof of prior consumption) rather than as unverifiable.
This classification is declared here, before execution, precisely so that the
choice cannot be made after seeing the outcome.

### 12.5 Secondary baseline metric

In addition to the Stage01 **validator-only** metric, a second baseline
metric `baseline_stage01_end_to_end` is reported: the frozen validator returns
ACCEPT **and** the frozen reference verifier returns ACCEPTED for the same
case. This is a *stricter* baseline, and reporting it prevents the comparison
from being accused of strawmanning the historical system by ignoring the
reference verifier it ships with. The primary comparison in §5 remains the
validator-only metric (the component the campaign actually gates on); the
end-to-end metric is the robustness check.

### 12.6 Representation fixed to C1

All cases use the canonical **C1** representation, except `H_UNDET_EC_01`,
which uses **C0** (the partially-ambiguous encoding) because that case
exists to exercise the underdetermined-reporting path. Representation
transformation was already shown to be equivalent at Stage 0 and is
orthogonal to the attribution question. S1, S2, and S3 are all computed over
the full 22-case set.

### 12.7 Strict output rule ablation is uninformative in this run

E2A uses a strict output rule (exactly one non-empty stdout line parsing as
a JSON object). The historical last-line rule is retained in the code and
reported as an ablation, but **no case in the 22-case set produces
multi-line output**, so the ablation cannot discriminate. This is declared as
a **limitation of this run, not a finding**. A discriminating ablation would
require a multi-line-output case, which is not in the frozen inventory and
will not be added post hoc.

### 12.8 Replay-state cloning for the S1 pair

The S1 pair is executed with an aggregator whose replay ledger is a
**snapshot clone** of the stateful aggregator's ledger, obtained by copying
the audited `ReplayState._uses` mapping (documented internal state of that
dataclass) and by supplying no ledger path, so the clone never writes to the
`replay_ledger.jsonl` audit trail. The clone exists only so the S1 pair is
evaluated under the same ledger state as the primary evaluation; the
snapshot itself is not a claim about the primary case.

### 12.9 Deviations log is part of the frozen artifact set

`E2A_DEVIATIONS.md` is created in this directory **before** the freeze
manifest is written and is included in the manifest's `components` map, so
its content is hash-pinned by the audited manifest verifier. It is placed at
the stage root, **not** inside `frozen/cases/`, because the audited
`manifest_verifier` rejects unexpected files in the case-inventory root and
rejects any file that overlaps a declared component.

### 12.10 Re-scoping forced by an independent prior-art review (MATERIAL)

An independent prior-art/novelty review was completed **before** the E2A run
and is recorded in full in the Stage 0 deliverable
`../stage0/AGENT3_PRIOR_ART_NOVELTY_REVIEW.md` (deliverable package:
`NOVELTY_PRIOR_ART_MATRIX.md`). Its material findings, verified against
primary sources, are:

* The "previously unknown security mechanism" framing is **foreclosed**.
  The mechanism (evidence binding to target/attempt/epoch/role/kind, freshness
  and replay prevention, role-scoped authorization, fail-closed aggregation)
  is specified with normative language in published specifications — RFC 9334
  (RATS Architecture) §8.1/§10/§12, in-toto Specification v1.0.0, SLSA v0.2
  and v1.0, TUF Spec v1.0.37, Sigstore/cosign. The composition failure mode
  is **named** in RFC 9334 §8.1 (Jan 2023) and as TUF's "mix-and-match"
  goal, and is **measured** in the agent runtime by TRAP/ReplayBench
  (arXiv:2610.16333).
* The closest published measurement baselines are TRAP/ReplayBench,
  "When Agent Evaluation Becomes Unreliable" (arXiv:2610.16067), and
  RewardHackingAgents (arXiv:2603.11337) — **not** a self-constructed
  V0/V1 ladder.

**Consequence for this experiment, declared before execution.** E2A is
**not** run to support a novelty claim. It is run to support a
**measurement** claim (Class C): whether a *defined* false-attribution-
promotion rate, measured under an explicitly declared and fair contract
against a *complete* shipped baseline, distinguishes the E2A contract from
the Stage01 contract on a frozen, replayable, per-instance-labelled corpus.
The E2A result will be reported as evidence about **contract coverage under
a declared contract**, and specifically **not** as evidence of a new
mechanism, of a new principle, or of superiority over provenance
implementations that were not executed (see §12.11 and Stage 2).

Accordingly, the pre-registered claims are restated as:

* **H1 (causal binding)** — supported, if and only if E2A binds program
  bytes → invocation → runtime output → reference verdict → claim, and the
  binding is *demonstrably* load-bearing (a tampered case changes the
  verdict). This is a **property of the E2A contract**, not a novelty claim.
* **H3 (honest-error discrimination)** — supported if E2A separates honest
  failure modes that the baseline conflates.
* **H4 (non-regression)** — supported if E2A does not introduce false
  rejections of genuine successes relative to the baseline on the same
  22-case set.
* **Objective 1 of the master programme** is assessed as **NOT_AVAILABLE** on
  the basis of the prior-art review, independently of any E2A outcome. E2A
  results are **not** admissible as support for Objective 1, and no amount
  of E2A success may be reported as evidence of a previously unknown
  mechanism.

### 12.11 The Stage01 baseline is *not* a provenance-implementation baseline

The Stage01 validator + reference verifier pair is the **frozen shipped
baseline of this system**, and it is the only baseline this experiment
executes. It is **not** a stand-in for in-toto, SLSA, TUF, or Sigstore. The
§3.3 comparability statement is therefore **strengthened** by this amendment:
the E2A-vs-Stage01 comparison measures contract coverage between two
implementations of *this* system under one declared contract, and supports
**no** claim about in-toto/SLSA/TUF/Sigstore, which are compared in Stage 2
under their own common contract and are explicitly not executed in Stage 1.

### 12.12 Amendment is itself frozen

This amendment, `E2A_DEVIATIONS.md`, the case inventory, the trust material,
the manifest, and the runner source are all hashed by the audited
`manifest_verifier` before the run. The run refuses to start if the
preflight fails.

