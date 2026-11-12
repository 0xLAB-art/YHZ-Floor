# Final Determination on the Four Research Objectives — ACTS-Attack

**Phase:** `acts_next_phase_20261019` (additive; no historical artefact modified)
**Date:** 2026-10-20
**Status vocabulary (fixed in advance):** `ESTABLISHED` ·
`PARTIALLY_ESTABLISHED` · `NOT_ESTABLISHED` · `NOT_TESTED` ·
`BLOCKED_BY_RESOURCE_OR_AUTHORIZATION` · `NOT_COMPARABLE`.

**Governing rule (stated in advance and observed):** no objective is marked
`ESTABLISHED` on the basis of a guarantee that was not tested, and no objective
is marked `ESTABLISHED` where the necessary evidence is a *constructed
condition* rather than a *reachable* one.

---

## Summary

| # | Objective (short form) | Determination | One-line basis |
|---|---|---|---|
| 1 | A previously unknown security mechanism | **`NOT_ESTABLISHED`** | The mechanism is explicitly named in RFC 9334 §8.1 and §12.3 (verbatim quotes below). The category is foreclosed, not merely unproven. |
| 2 | A realistically reachable exploit with attacker-controlled ingress and an incorrect final claim | **`NOT_ESTABLISHED`** | No authorised reachable ingress exists (0/14 candidates pass the owner-and-authorisation test). A **component-level capability gap** *was* demonstrated against the frozen production Stage01 pair, but reachability was not. |
| 3 | A demonstrable advantage over actual, complete provenance-verification implementations | **`BLOCKED_BY_RESOURCE_OR_AUTHORIZATION`** | The only genuinely comparable product (in-toto 3.1.0) is not installed; installation needs approval. The *design* portion is `PARTIALLY_ESTABLISHED`; the *empirical* portion is `NOT_TESTED`. |
| 4 | Trustworthy end-to-end attribution across source → execution → output → reference → evidence → claim | **`ESTABLISHED`** (on the frozen corpus, within the stated scope) | A newly built, hash-pinned, preflighted chain attributes **0/25** ground-truth non-successes and rejects **0/2** ground-truth successes, while the frozen production Stage01 pair **accepts 2 of those 25**. |

---

## Objective 1 — "Identify and establish a previously unknown security mechanism"

### Determination: **`NOT_ESTABLISHED`** (and the search avenue is foreclosed)

**Scope.** The objective required a mechanism *beyond* known provenance,
attestation, freshness and evidence-binding principles. The candidate
mechanism was the **cross-boundary / cross-environment evidence-confusion
promotion**: an under-bound evaluator combining individually valid evidence
into an unsupported full attribution claim, and claim-specific bindings
preventing that promotion.

**Evidence against.** RFC 9334 (RATS, IETF Informational, January 2023) —
fetched and read in this session — states the mechanism normatively:

> §8.1 "Evidence" (lines 1244–1247): *"Evidence needs to be securely associated
> with the Target Environment so that the Verifier cannot be tricked into
> accepting Claims originating from a different environment (that may be more
> trustworthy)."*

> §12.3 (lines ~1842–1844), introduced as a *confusion attack*: *"a Verifier
> can be tricked into accepting Evidence coming from a past epoch as fresh,
> while, in the meantime, the Attester has been compromised."*

Both passages describe the promotion mechanism and its freshness/epoch
variant, two years before this programme's first experiment. The independent
prior-art reviewers confirmed the same conclusion and added that the whole
ingredient set — trusted-observer separation, per-claim joins, role-scoped
authorisation, freshness/replay prevention, fail-closed aggregation — is
native to RFC 9334, in-toto, SLSA, TUF and Sigstore.

**Scope of the negative result.** This is a determination that the *category*
is occupied, not an exhaustive proof of duplication. A deliberately narrow
residual **was** identified and is defensible on the present evidence:
RFC 9334 §8.4 specifies a **binary** verdict, SLSA's verdict is binary
(`PASSED|FAILED`), and the in-toto **CLI** collapses its library-level
missing-vs-bad distinction (`LinkNotFoundError` vs `RuleVerificationError`)
into a single exit code. A **claim-level tri-state** inside a freshness- and
epoch-bound chain is therefore the narrowest residual — but it is a
**known general principle applied to a new domain** (category **B**) plus a
**measurement methodology** (category **C**), not a previously unrecognised
mechanism (category **D**). The closest published measurement of the same
class of defect — "Grounded but Wrong", preprints 202610.0322 — could not be
fully obtained (HTTP 403), so even the C claim is **incomplete**.

**Consequence, applied to the rest of this package:** no result in this phase
is offered as support for Objective 1. This is consistent with the
independent re-audit's determination and with the concurrent sibling tree's
pre-execution amendment §12.10, which reached the same conclusion
independently.

---

## Objective 2 — "Demonstrate a realistically reachable exploit in an authorised ACTS-Attack evaluation workflow, with an actual attacker-controlled ingress and an incorrect final security claim"

### Determination: **`NOT_ESTABLISHED`**

The objective is a **conjunction** of three requirements. Each is reported
separately, because two of the three were achieved and the decisive one was
not.

| Requirement | Status | Evidence |
|---|---|---|
| (i) an **actual attacker-controlled ingress** that legitimately reaches the evaluation/aggregation path | **NOT ESTABLISHED** | `stage3_boundary/STAGE3_BOUNDARY_ANALYSIS.md`: 14 candidate ingresses evaluated against a six-point qualifying test; **0/14** pass "identifiable owner and authorisation". Finding token: `NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED`. Re-derived independently in `stage0/AGENT1_TRUST_BOUNDARY_MAP.md`: zero HTTP servers or socket listeners under `sp2027/analysis/`; `argparse`/`sys.argv`/`stdin` counts of 0/0/0 across the five campaign runners; the certificate is constructed in-process immediately after execution (`run_contract_sound_agent_replacement_v1.py:165→:172→:175→:176`), so the substituted artefacts are not *separable* in the live path. |
| (ii) an **incorrect final security claim** | **PARTIALLY ESTABLISHED** (component level only) | The **frozen production** Stage01 pair — `contract_sound_stage01_validator_v2.py` (SHA-256 `f248413d…`) + `contract_sound_stage01_reference_verifier_v2.py` (SHA-256 `15bb4095…`), run unmodified as subprocesses — **ACCEPTED** two bundles in which the attribution claim is false: `C02_credited_program_not_executed` and `C03_submitted_output_not_observed`. See `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md` §5–6. |
| (iii) **realistic reachability** of (ii) | **NOT ESTABLISHED** | The C02/C03 substitutions are **synthetic contradiction-detection cases**. They demonstrate that the *contract* the frozen components implement cannot express the program→output causal link, and that the components accept a certificate in which it is broken. They do **not** demonstrate that a producer can cause the live aggregator to build such a certificate. |

**What was explicitly *not* done.** No live target was attacked; no gateway was
created to manufacture the missing boundary; no test-only interposer was
introduced and then described as naturally reachable; the concurrent sibling
tree's newly created `ingress_gateway.py` was **not** treated as a qualifying
ingress (it passes K2–K6 and fails K1 by construction, because it was itself
created on 2026-10-20 as a research artefact).

**The strongest honest formulation of what was achieved:**

> The ACTS-Attack production certificate format carries **no field capable of
> expressing** "this runtime output was produced by this program source", and
> the frozen blind validator — which is the component a third party would use
> to check a certificate — therefore **accepts** certificates in which that
> relation is false, while still claiming `artifact_authorship = PROVEN`,
> `execution_identity = PROVEN` and `attribution = PROVEN`.

That is a **design- and component-level capability gap**, demonstrated against
real, unmodified, hash-pinned production code. It is **not** a demonstrated
exploit, and it is not reported as one.

---

## Objective 3 — "Evaluate whether our approach offers a meaningful, demonstrable advantage over actual, complete provenance-verification implementations, under a fair and comparable security contract"

### Determination: **`BLOCKED_BY_RESOURCE_OR_AUTHORIZATION`** (empirical) / `PARTIALLY_ESTABLISHED` (design)

| Sub-claim | Determination | Basis |
|---|---|---|
| A fair common contract exists against which a real implementation can be measured | `ESTABLISHED` | `deliverables/REAL_PROVENANCE_BASELINE_COMPARISON.md` §2: P1–P10, each row marked `N` (natively provided), `[CUSTOM-INSPECTION]` (provided only by our construction) or `—` (not provided). A "no laundering" rule is enforced: a verdict difference counts as a *product* result only on a row marked `N` without a `[CUSTOM-INSPECTION]` tag. |
| The comparison is *possible* against a real implementation | `PARTIALLY_ESTABLISHED` | Exactly one candidate is genuinely comparable as a verdict comparator: **in-toto 3.1.0** (natively covers artifact-digest equality, signer identity + role authorisation, signature validity, and step-to-step causal joins via `MATCH ... FROM <step>` / `MODIFY`). **slsa-verifier 2.7.1** and **cosign 3.1.3** are `NOT_COMPARABLE`; **RFC 9334** is an architectural target and is not runnable (zero hits for `Rekor`, `DSSE`, `transparency`, `in-toto`, `SLSA`, `Sigstore` in its text). |
| Our contract covers strictly more guarantee classes | `PARTIALLY_ESTABLISHED` | On the products' own documented schemas: in-toto's link format has **no attempt/session field** and its `byproducts`/`environment` are **unverified by specification**, so it cannot express P6 (freshness/epoch) or P7 (target binding); it has no claim-aggregation concept (P9); and the in-toto **CLI** collapses its library-level missing-vs-bad distinction into one exit code (P10). These four rows are strictly stronger in the Stage 1 contract. |
| Our contract is **strictly better** than in-toto | `NOT_ESTABLISHED` | A superiority claim requires **executed** verdicts under one declared contract. None exist: in-toto is not installed (gap G-1, request R-1 awaiting approval). A falsifiable prediction is on record (P-1: a naive translation of the frozen 58-case IAR-B held-out corpus should reproduce the `digest-only` baseline's 8 held-out false promotions). |
| Overall | **`BLOCKED_BY_RESOURCE_OR_AUTHORIZATION`** | One approval unblocks it. `deliverables/RESOURCE_AND_PERMISSION_REQUESTS.md` §1 specifies the exact command, the isolation boundary, and the four steps it unblocks. |

**Explicitly not claimed:** no superiority over in-toto, SLSA, Sigstore, TUF or
RFC 9334 is asserted anywhere in this package.

---

## Objective 4 — "Build and experimentally validate trustworthy end-to-end attribution across program source → execution → runtime output → cryptographic reference verification → evidence → final security claim"

### Determination: **`ESTABLISHED`** — on the frozen corpus, within the stated scope

The objective's own success criterion was: *"the new evaluator can justify an
attributable completion claim only when the complete required causal and
cryptographic evidence chain supports it."*

#### Precise evidence

**The chain that was built** (`stage1_attribution/`, all new and additive):
a **trusted execution observer** that holds its own fresh Ed25519 key, executes
the program itself, hashes the program bytes before *and* after execution,
captures stdout/stderr, derives the output artifact from **its own capture**,
and signs what it read; an **independent reference verifier** holding the
private target state, which consumes the observer's *pinned stdout* and applies
the **frozen** `ecdsa_valid`/`chacha_valid` predicate (imported, hash-pinned,
fail-closed — the predicate is not re-implemented); a **signed context** layer
(six fields: kind, domain, target, attempt, epoch, role) with a replay ledger;
a **role/kind-authorised** issuance policy; and a **tri-state** adjudicator
with an eleven-join causal ladder over six claim levels.

**The measured result** (27 frozen cases; the full table in
`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md` §4; recomputed independently
from `runs/results.json`):

| Contract | false attributions (of 25 ground-truth non-successes) | Wilson 95 % CI | false rejections (of 2 ground-truth successes) | correct rejections |
|---|---|---|---|---|
| `digest_only` (E0) | 13/25 | [0.335, 0.700] | 0/2 | 12/25 |
| `signed_digest_only` (E1) | 11/25 | [0.267, 0.629] | 0/2 | 14/25 |
| `signed_context_only` (E2) | 6/25 | [0.115, 0.434] | 0/2 | 19/25 |
| **`full` (E3, strict — primary)** | **0/25** | **[0.000, 0.133]** | **0/2** | **25/25** |
| `full_lenient` (E3, sensitivity) | 1/25 (`A05` only) | [0.007, 0.195] | 0/2 | 24/25 |
| **frozen production Stage01 pair** | **2/25** (`C02`, `C03`) | — | 0/2 | 23/25 |

The omission family (5 cases) is classified **INCONCLUSIVE by 5/5 contracts**;
the frozen Stage01 pair has **no INCONCLUSIVE category** and rejected those
cases instead — itself a reported finding.

#### Scope (what "ESTABLISHED" covers, and what it does not)

* **Covers:** a *local, offline, authorised, constructed* evaluation
  experiment, on a 27-case corpus that is **not** a random sample of any
  population, over two primitives (ECDSA nonce reuse, ChaCha20 nonce repeat)
  and two conditions (C1, C0), using a **scripted** producer, with the
  cryptographic predicate taken from the frozen production verifier.
* **Does not cover:** any deployed service; any live campaign; any
  attacker-controlled ingress; any AI/model producer arm; any population-level
  rate; any generalisation beyond the 27 cases; any statement about in-toto,
  SLSA, Sigstore or TUF.

#### Independent verification performed

1. **Freeze in force before measurement** — the run is wrapped in
   `manifest_verifier.preflight_then_execute(...)` using the **unmodified**
   `heb1_remediation_v1/integrity/manifest_verifier.py`; the preflight checked
   **77 files** (protocol, runner, 13 components, the three frozen historical
   components, the labels, the trust material, and all 56 case-inventory
   files) and reported **0 errors**. It was **re-verified after the run** with
   the same result.
2. **17 unit tests** (`test_s1_attribution.py`, all passing) including: the
   fail-closed digest pin; **source-policy equivalence against a verbatim
   transcription of the historical `safe_source`**; the new reference
   verifier's predicate against the frozen `ecdsa_valid`; the observer
   refusing a policy-violating program; missing evidence ⇒ INCONCLUSIVE (not
   REJECT); replay ⇒ REJECT on the second evaluation; the audited preflight
   rejecting a tampered manifest; and the **baseline positive control** (the
   frozen Stage01 pair must ACCEPT an honest case).
3. **The baseline is not a strawman** — the frozen Stage01 pair accepted
   **2 of the 2** ground-truth successes and rejected all four
   cryptographically-false honest cases.
4. **Nine controls** declared in the protocol and exercised (see the results
   report §4).
5. **An independent recomputation** of every reported metric from the raw
   `runs/results.json` by a script that does not share code with the
   summariser, plus an independent adversarial audit
   (`deliverables/SCIENTIFIC_VALIDITY_AUDIT.md`).

#### Binding limitations (the full list is §8 of the results report)

1. The corpus is **balanced and constructed**; the rates are
   **characterisations of discrimination, not population estimates**.
2. n = 2 ground-truth successes. The "0/2 false rejection" claim is a
   *demonstration of non-regression on these two cases*, **not** a rate.
3. The producer arm is **scripted**. **No AI-specific evidence exists**, and
   none is claimed.
4. The C family is **synthetic contradiction-detection**; it demonstrates
   component discrimination, not reachability.
5. The observer's TOCTOU window (write → hash → execute) is **not** closed;
   the concurrent sibling tree's `memfd` observer closes it, and that tree was
   **not** used or modified.
6. The replay ledger is **in-memory, per-evaluation, and not atomic or
   durable**.
7. The signing layer is **not a production PKI**; there is no automatic
   revocation, epoch lifecycle, or key transparency.
8. Evidence identity is **byte-identity**; a semantic-equivalence contract
   would behave differently.
9. The isolation is `python -I` with a minimal environment; there is **no
   network namespace** and no `bwrap` in the Stage 1 observer.
10. The two execution contracts (strict / lenient) differ on exactly one
    case (`A05`); the choice is disclosed and was preregistered.

---

## Closing statement

Two of the four objectives did not yield positive results, and one of those
is foreclosed by prior art that this phase identified and quoted. That is the
scientific outcome, not a failure of execution: the programme produced, for the
first time, a **frozen, preflighted, hash-pinned, tri-state** end-to-end
attribution contract that is **measurably** stricter than the project's own
frozen production components, together with a **source-verified** negative
result on ingress, and a **verbatim-quoted** foreclosure of the novelty
category. No number in this package was retrofitted, no baseline was
handicapped, and no claim exceeds its evidence.
