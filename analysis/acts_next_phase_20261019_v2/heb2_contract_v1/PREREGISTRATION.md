# HEB-2 / Contract V2 — Preregistration

**Stage:** HEB-2 (Contract V2), `sp2027/analysis/acts_next_phase_20261019_v2/heb2_contract_v1/`
**Written:** 2026-10-20, **before** any Contract V2 execution.
**Supersedes:** nothing. The Stage 1 contract (V1) remains frozen and unmodified; V2 is an
additive, separately versioned contract that composes the same audited trusted components.

---

## 1. Why this stage exists

The Stage 1 preregistration defines attribution as a causal chain —

> program source bytes → execution event → captured runtime output → parsed candidate output →
> independent cryptographic predicate

— and states no rule about the **completion** of the execution. The frozen V1 check order is

```
presence → record_signature → kind_role → replay → context_binding →
cross_record_consistency → certificate_claim_consistency → reference_status → predicate
```

and contains no execution-status check; `aggregator.py` never reads `execution_status` or
`returncode`. The preregistered case table describes the `honest_execution_failure` family as
"Program raises → non-zero exit", and the frozen case note adds "Program exits with status 3
**before producing output**". The combination *non-zero exit **with** a valid candidate output*
is therefore covered by no case and specified by no rule.

The Stage 4 matched arm produced exactly that combination. V1 attributed it. Whether that is
correct is undetermined by the preregistration. This stage removes the ambiguity by **deciding the
semantic in advance** and measuring both readings on identical evidence.

---

## 2. Hypotheses

**H2-A (semantic sensitivity).** The choice of execution-completion semantic changes the
attribution decision for at least one case of the frozen 22-case inventory, and the change is
confined to cases whose observation records a non-zero exit status.

**H2-B (soundness).** Under either semantic, no bundle that violates the soundness property §4 is
ever granted an attribution. This is checked mechanically over a seeded mutation corpus, not by
assertion.

**H2-C (replication).** Under the output-based semantic, Contract V2 reproduces the Stage 1
confirmatory decisions on the frozen inventory.

---

## 3. The two arms (frozen before execution)

Both arms evaluate **the same certificate bundle** produced by the same trusted components. The
arms differ in exactly one precondition.

| Arm | Precondition | Meaning |
|---|---|---|
| `output` | *(none beyond V1)* | Attribution asserts: *the executed bytes produced a candidate output that the independent reference adjudicated as satisfying the predicate.* The program's own exit status is not part of the claim. |
| `completion` | The observation's `execution_status` must be `EXECUTED` (i.e. `returncode == 0`) | Attribution asserts the above **and** that the execution completed successfully. |

**Placement.** The completion precondition is evaluated immediately before the predicate step.
Because the predicate step is terminal in the V1 check order, evaluating the precondition on the
`ATTRIBUTED_SUCCESS` branch is exactly equivalent to evaluating it immediately before the
predicate step, and cannot mask any earlier check. The V1 aggregator is **not modified**; V2
composes it by subclassing.

**Precedence.** `completion` overrides `output` only at the attribution boundary. Every earlier
check (authenticity, kind/role, replay, context binding, cross-record consistency,
certificate-claim consistency, reference status) is unchanged, so the reason families for
non-success outcomes are identical between arms except where the completion precondition fires.

**Decision rule (frozen).** `completion` returns `REJECT` with reason `execution-not-completed`
and reason family `contradicted_by_evidence` when the precondition fails. No other reason string
or family is introduced.

---

## 4. The soundness property (mechanically checked)

**S1.** For any bundle B, if the contract returns `ATTRIBUTED_SUCCESS` then all of:

- **(a)** the observation and reference records verify under the trust bundle and issuer policy;
- **(b)** the signed contexts of both records bind to the certificate's
  `(target_id, attempt_id, epoch)` with the authorized role and kind;
- **(c)** the reference's `stdout_sha256` equals the observation's captured-stdout digest, and
  the reference's `candidate_digest` equals the observation's parsed-candidate digest;
- **(d)** the reference independently adjudicated `crypto_ok = true` with `verdict = ACCEPTED` on
  those bytes;
- **(e)** *(completion arm only)* the observation records `execution_status = EXECUTED`.

**Check.** A seeded mutation corpus is generated from the genuine per-case certificates. Every
mutant is evaluated under both arms. For every mutant that is accepted, S1 is re-verified
directly against the mutant's own contents. A violation is a hard failure of this stage.

**Mutation operators (frozen).** signature-byte corruption; `key_id` substitution; payload-field
corruption in the observation and the reference; certificate field corruption
(`target_id`, `attempt_id`, `epoch`, `agent_artifact.sha256`, `candidate_output.sha256`);
evidence-record deletion; cross-case splicing of observation and reference; claim-block
assertion changes; and evidence-order permutation. Corpus size and seed are frozen in
`soundness_check.py`.

---

## 5. Inventory, denominators and stopping rules

- **Inventory:** the frozen 22-case inventory (`stage1_e2a/frozen/cases/`), hash-pinned. It is
  unchanged by this stage.
- **Denominators:** 22 cases, of which 6 are `gt_success = True` and 16 are `gt_success = False`.
  Both denominators are reported for each arm.
- **Within-subject design:** each case yields two decisions (one per arm) over the *same*
  certificate, so the semantic contrast is paired.
- **One run.** No re-run with modified configuration. If a component crashes, the crash is the
  case outcome.
- **Integrity preflight.** The audited `heb1_remediation_v1/integrity/manifest_verifier.py` must
  verify `FREEZE.json` fail-closed before execution. A preflight failure aborts the stage.
- **Trust material.** Fresh issuer keys are provisioned per run into a private directory; the
  frozen Stage 1 trust bundle is not modified.
- **Reporting.** Both arms' decisions are reported for every case. The semantic difference is
  reported as a paired table, not as a headline rate.

## 6. Threats to validity (declared in advance)

1. **The inventory is constructed, not sampled.** Results characterise contract behaviour on these
   cases, not a population rate.
2. **The mutation corpus is not exhaustive.** It is a seeded sample of the reachable
   neighbourhood of the genuine bundles; it does not constitute a proof of S1 in the formal
   sense. It is a falsification attempt with a stated scope.
3. **The arms share one execution.** The two arms differ only in the precondition, so their
   difference is attributable to that precondition by construction; the cost is that the corpus
   shares any execution-specific artefact.
4. **The semantic is a decision, not a discovery.** V2 does not establish which reading is
   *correct*; it establishes what each reading implies, in advance, and how often they differ.
5. **The V1 contract is not superseded.** V1's results stand as recorded; V2 is additive.

## 7. Claims that V2 may not support

- That the `completion` semantic is the *correct* one.
- That S1 holds for all possible bundles (only the mutation corpus was tested).
- That any Stage 1 or Stage 4 result changes: the V1 decisions are historical facts.
- Any statement about prevalence, generalisation, or deployed systems.