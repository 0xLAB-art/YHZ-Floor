# Real Provenance Baseline Comparison — ACTS-Attack

**Phase:** `acts_next_phase_20261019`
**Date:** 2026-10-20
**Underlying analysis:** `stage2_provenance/AGENT3_PROVENANCE_COMPARATOR_ANALYSIS.md`
(653 lines, 40 cited URLs, 16 `[CUSTOM-INSPECTION]` tags, 4 `[UNVERIFIED]`,
3 `[ESTIMATE]`).

**Status of this document:** the *analysis* and the *comparability contract*
are complete; the *empirical* comparison against the one genuinely comparable
product (in-toto) **HAS NOT BEEN EXECUTED**, because installing it requires
approval that has not been granted in this session (gap **G-1**,
`stage0/STAGE0_RESOURCE_GAPS.md`).

---

## 1. Which real products are even candidates

| Product | Upstream version considered | Can it act as a *verdict comparator* for an ACTS-Attack attribution claim? | Reason |
|---|---|---|---|
| **in-toto** | 3.1.0 | **YES — the only genuinely comparable product.** | Fully offline by design; natively covers artifact-digest equality, signer identity + role authorisation, signature validity/key binding, and **step-to-step causal joins** (`MATCH ... FROM <step>`, `MODIFY` requiring a digest change). Partially covers inspections and typed exceptions. |
| **slsa-verifier** | 2.7.1 | **NOT_COMPARABLE** as a verdict comparator. | Verifies only SLSA-generator GHA/GCB provenance. `verify-artifact` requires `--source-uri`. Trust material is Sigstore TUF/Rekor (network). The project is "no longer actively maintained". v2.7.1 parses only v0.2/v1.0 predicates while SLSA is now v1.2. **Narrow exception:** `verify-vsa` is offline and *is* a native "a second party signs PASSED over a subject digest" mechanism — usable as a **mechanism-level** comparator on the second-party-signature row only, with the semantic stretch disclosed. |
| **cosign** | 3.1.3 | **NOT_COMPARABLE** | A transport-and-signature layer. No step, no join, no inspection, no claim ladder, no attempt, no target-state concept. |
| **RFC 9334 (RATS)** | Jan 2023 Informational | **Architectural target only — not runnable.** | The brief's premise was inaccurate: an exhaustive search of the RFC text returns **zero** hits for `Rekor`, `DSSE`, `transparency`, `in-toto`, `SLSA`, `Sigstore`. Its "thresholds" are freshness **time** thresholds, not signature-count thresholds. |

## 2. The fair common contract (P1–P10)

Every guarantee is marked:

* **`N`** — natively provided by the product (a verdict difference here is a
  genuine *product* result);
* **`[CUSTOM-INSPECTION]`** — provided only because *we* wrote the custom
  inspection; a verdict difference here is **not** a product result and must be
  labelled as such;
* **`—`** — not provided by the product.

| # | Guarantee | in-toto 3.1.0 | slsa-verifier 2.7.1 | cosign 3.1.3 | Stage 1 `full` (E3) |
|---|---|---|---|---|---|
| P1 | Artifact digest equality | **`N`** | `N` (artifact digest) | **`N`** | `N` |
| P2 | Signer identity + role authorisation | **`N`** | `N` (identity, not role) | **`N`** (identity) | `N` |
| P3 | Signature validity / key binding | **`N`** | `N` | **`N`** | `N` |
| P4 | Step-to-step causal join | **`N`** (`MATCH`/`MODIFY`) | — | — | `N` (11 joins) |
| P5 | Inspection of an executed step | **partial** (`[CUSTOM-INSPECTION]`) | — | — | `N` (TEO) |
| P6 | Freshness / epoch / replay | — (no attempt field) | — | — | `N` |
| P7 | Target / task-state binding | — (no target digest) | — | — | `N` |
| P8 | Second-party cryptographic verdict | **partial** (`[CUSTOM-INSPECTION]`) | `N` (`verify-vsa`, mechanism-level) | — | `N` |
| P9 | Claim aggregation to a final attributed claim | — | — | — | `N` |
| P10 | Typed exceptions (missing vs bad) | **partial** — library distinguishes `LinkNotFoundError` vs `RuleVerificationError`; the **CLI collapses both to exit 1** | — (hard error) | — | `N` (tri-state) |

**The four rows where the Stage 1 contract is strictly stronger than in-toto
are P6, P7, P9 and the CLI-level half of P10** — freshness/epoch, target
binding, claim aggregation, and a tri-state verdict. P6 and P7 are exactly the
rows in-toto cannot express because **its link format has no attempt/session
field, and `byproducts`/`environment` are unverified by the specification**.

## 3. The decisive testable prediction (and why it matters)

> **Prediction P-1.** A *naive* translation of the **frozen** 58-case IAR-B
> held-out corpus into in-toto links and layouts should reproduce the
> `digest-only` baseline's **8 held-out false promotions** (families H6b/H10),
> because in-toto's native guarantees cover P1–P4 and *not* P6/P7 — and the
> attempt id cannot be bound without a **custom construction** (encoding the
> attempt id into the artifact *path*), which must be labelled
> `[CUSTOM-INSPECTION]` and must not be counted as a product result.

This is a *product* prediction, not a model prediction, and it is falsifiable.

**Prediction P-2.** Adding the attempt id to the artifact *path* closes the
promotion gap for in-toto, but the closure is a property of *our* construction,
not of in-toto. The document enforces a **"no laundering" rule**: a verdict
difference counts as a *product* result only on a row marked `N` without a
`[CUSTOM-INSPECTION]` tag.

## 4. What was and was not executed

| Step | Status | Evidence |
|---|---|---|
| Inventory of the real tools and their documented guarantees | **DONE** | `AGENT3_PROVENANCE_COMPARATOR_ANALYSIS.md` (40 cited URLs) |
| Common contract P1–P10 with the `N` / `[CUSTOM-INSPECTION]` / `—` marking | **DONE** | §2 above; the analysis document tags every row |
| Compatibility analysis of the frozen IAR-B held-out corpus against in-toto's schema | **DONE (design)** | §3 above |
| `pip install in-toto==3.1.0` into an isolated venv | **NOT DONE — approval required (G-1)** | `stage0/STAGE0_RESOURCE_GAPS.md` |
| Translate the frozen 58-case corpus into in-toto links/layouts | **NOT DONE** | needs in-toto installed to validate the translation |
| Execute `in-toto verify` offline on the translated corpus | **NOT DONE** | needs the above |
| Compare in-toto's verdict with the frozen Stage01 verdict and the Stage 1 `full` verdict under one declared contract | **NOT DONE** | needs the above |
| `go install slsa-verifier@v2.7.1` for the `verify-vsa` mechanism demo | **NOT REQUESTED** | slsa-verifier is `NOT_COMPARABLE` as a verdict comparator; the mechanism demo is optional and lower value than G-1 |
| cosign binary | **NOT REQUESTED** | cosign is `NOT_COMPARABLE`; a binary would only be needed for the publication direction, which is not a comparison |

**No package was installed. No network request was made to any package index
or to any third party other than the RFC text and the public documentation
URLs listed in the analysis document. The project's own dependencies were not
modified.**

## 5. Objective 3 determination

> **Objective 3 — "Evaluate whether our approach offers a meaningful,
> demonstrable advantage over actual, complete provenance verification
> implementations, under a fair and comparable security contract."**

| Sub-claim | Determination |
|---|---|
| The comparison has been executed against a real provenance implementation | **NOT_TESTED** (in-toto not installed — G-1) |
| The comparison is *possible* against a real implementation at all | **PARTIALLY_ESTABLISHED** — exactly one candidate (in-toto 3.1.0) is genuinely comparable; slsa-verifier and cosign are `NOT_COMPARABLE` for a verdict comparison, and RFC 9334 is not runnable |
| Our contract covers strictly more guarantee classes than in-toto | **PARTIALLY_ESTABLISHED** on the basis of the products' own documented schemas (P6/P7/P9 and the CLI-level part of P10), **not** yet on the basis of executed verdicts |
| Our contract is *strictly better* than in-toto | **NOT_ESTABLISHED** — a superiority claim requires executed verdicts under one declared contract, and none exist |

**Overall for Objective 3: `BLOCKED_BY_RESOURCE_OR_AUTHORIZATION`** for the
empirical part, with the design portion `PARTIALLY_ESTABLISHED`.

## 6. Honest statement of what would change the answer

If, after in-toto is installed, the translated corpus shows that in-toto's
native `MATCH`/`MODIFY` joins close the promotion gap on P-1, then the
residual Stage 1 advantage narrows to P6 (freshness/epoch), P7 (target
binding), P9 (claim aggregation) and the claim-level tri-state — i.e. a
**narrow** advantage over a real product, on four rows, on a 58-case corpus
with no CIs as a population estimate. If in-toto reproduces the 8 false
promotions, the Stage 1 advantage is broader but still confined to those rows
plus the tri-state. Either way, the **C02/C03 finding does not depend on
in-toto at all** — it is a comparison against the project's own *frozen
production* Stage01 pair, and that comparison has already been executed
(`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md` §6).
