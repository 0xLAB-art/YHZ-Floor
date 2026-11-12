# Novelty / Prior-Art Matrix — ACTS-Attack

**Phase:** `acts_next_phase_20261019`
**Date:** 2026-10-20
**Sources (both read in full or verified independently):**
`stage0/AGENT5_PRIOR_ART_NOVELTY_MATRIX.md` (363 lines) ·
`stage0/AGENT5B_PRIOR_ART_VERIFICATION.md` (1,199 lines) ·
independent re-reading of RFC 9334 by this agent
(`/tmp/opencode/rfc/rfc9334.txt`, 2437 lines).

Categories are the ones defined in the project brief:
**A** known general principle · **B** known mechanism in a new domain ·
**C** new empirical measurement methodology · **D** previously unrecognised
causal failure mechanism · **E** new defense with a measurable advantage over
a fair, technically appropriate baseline.

---

## 1. Headline determination

| Category | Determination | Confidence |
|---|---|---|
| **A** — known general principle | **SUPPORTED** (this *is* the contribution) | High — RFC 9334 §8.1/§12.3 quoted verbatim and independently re-read |
| **B** — known mechanism, new domain | **SUPPORTED**, but the domain is already occupied | High |
| **C** — new measurement methodology | **PARTIALLY SUPPORTED / not yet earned** | Medium |
| **D** — previously unrecognised mechanism | **NOT SUPPORTED — foreclosed. Abandon.** | High |
| **E** — new defense with a measurable advantage | **NOT SUPPORTED on current evidence** | Medium |

**Objective 1 (previously unknown security mechanism) is therefore
NOT_ESTABLISHED and, on the present evidence base, foreclosed.** The
cross-boundary / cross-environment evidence-confusion mechanism that the
programme set out to discover is *named* in the normative literature, and
RFC 9334 §8.1 says so in terms.

## 2. The decisive prior art (independently verified, not taken on trust)

### 2.1 RFC 9334 (RATS), IETF Informational, January 2023

Fetched `https://www.rfc-editor.org/rfc/rfc9334.txt` in this session and read
the relevant passages. **§8.1 "Evidence" (lines 1244–1247), verbatim:**

> Evidence needs to be securely associated with the Target Environment so that
> the Verifier cannot be tricked into accepting Claims originating from a
> different environment (that may be more trustworthy).

**§12.3 (lines ~1842–1844), verbatim** (introduced as a *confusion attack*):

> a Verifier can be tricked into accepting Evidence coming from a past epoch as
> fresh, while, in the meantime, the Attester has been compromised.

This is the ACTS-Attack cross-boundary promotion mechanism, described
normatively two years before the programme's first experiment, together with
its freshness/epoch variant. **Category D is foreclosed.**

### 2.2 The caveat that cuts the other way — and it matters

**RFC 9334 §8.4 (line 1299) specifies a BINARY verdict.** RFC 9334 is
therefore *not* prior art for the tri-state (REJECT / INCONCLUSIVE /
ATTRIBUTED_SUCCESS) adjudication that the Stage 1 contract introduces. Verified
in the RFC text: the "verdict" is pass/fail. A standard that cannot express
"the evidence is absent, so no opinion can be formed" does not anticipate a
contract that must.

**This is the single narrowest residual novelty claim the project can defend:**
*the tri-state adjudication of an evaluation-evidence chain, at the level of a
final attributed claim, is not anticipated by RFC 9334 because RFC 9334's
verdict space is binary.* It is a **B/C** claim (known tri-state idea in a new
domain + a measurement of it), **not** a D claim.

### 2.3 Other verified prior art

| Work | Verified? | What it establishes | Bearing on this project |
|---|---|---|---|
| **arXiv:2606.04990** *"From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents"* (Wang et al., 3 Jun 2026) | **Exists — but the "chain claim" is REFUTED.** The survey's own headline is a *gap finding*: none of the surveyed systems attests the complete provenance chain, and no benchmark covers it. "evaluator" and "under-bind" appear **0 times**; there is no reference-verification or cryptographic-evidence stage in it. | The domain is surveyed and found **empty**, not occupied. | Supports B/C: the domain is surveyed and found empty, not occupied. |
| **`llmsa` / `LLM-Supply-Chain-Attestation`** | **VERIFIED, stronger than Agent 5 claimed.** `internal/verify/result.go` L4–9 defines `ExitMissing=10 / ExitSignatureFail=11 / ExitDigestMismatch=12`; ADR-0007 L13: *"A simple pass/fail (0/1) exit code loses information about what went wrong."* Caveats: 2 stars, unpublished, no transparency log; the tri-state is *stage*-level, not claim-level. | The tri-state idea is **in code, with a written rationale**. | **Materially weakens** the tri-state residual. It is no longer "unclaimed"; it is claimed at stage granularity by an unpublished 2-star project. |
| **arXiv:2603.14332** | VERIFIED/REFINED. Thm 1 `ϵ ≤ 1 − α1/n`, Thm 2 L624 — but both concern **model-execution reproducibility**, not evaluation attribution. §8.2/§8.8 concede the trilemma is open. | An agent-governance layer with formal results, on a different problem. | Not prior art for this mechanism. |
| **arXiv:2605.14153 (ExploitBench)**, **arXiv:2506.02548 (CyberGym)** | VERIFIED for the *differential-oracle* property only: the oracle "depend[s] on the behavior of the ground-truth binary, not on anything the agent reports". The oracle is the harness, not an attested third party. | Independent-oracle design for exploit verification. | Adjacent, not identical: no attestation, no signed chain, no tri-state. |
| **arXiv:2610.16067** *"When Agent Evaluation Becomes Unreliable"* | VERIFIED for **method** (L556–7: "the full suite detects 54 of 57") but its terminology is **sensitivity/specificity**, not FAR/FRR. | The measurement method class the project uses. | Supports C (methodology), not D. |
| **preprints.org 202610.0322 "Grounded but Wrong"** | **PARTIALLY VERIFIED** via OpenAlex `W7220980858` (HTTP 200, full abstract): "cuts the run-level binding-defect rate from 28.9% to 2.2% (Holm-corrected p=0.0055)". **"Blind" REFUTED** (keyed ground-truth benchmark); **FAR/FRR REFUTED** (none reported); the real title's third clause is "in Agentic Statistical Analysis" (Six Sigma DMAIC, not security). Full text still **NOT OBTAINABLE** (preprints.org 403 ×5). | A binding-defect measurement in an adjacent domain, with a *different* metric and a *keyed* (not blind) ground truth. | The closest published measurement of the same *kind* of defect. Directly threatens C as well. **Comparison incomplete for the full text.** |
| **Partial Evidence Bench (arXiv:2605.05379)** | VERIFIED. L142–151: *"The headline failure occurs when the system returns a complete-seeming answer for a materially incomplete task without emitting a correct gap report"*, with `unsafe_completeness_rate` and `blocked_when_safe_to_answer_rate`. | A "complete-seeming but unsupported answer" metric in an AI-evaluation context. | **The nearest published analogue to the project's false-attribution metric.** |
| **in-toto** | **PARTIALLY VERIFIED / REFRAMED.** "unfulfilled" = 0 hits; there is no `in_toto/in_toto.py`; but `exceptions.py` L30 `LinkNotFoundError` (missing, `verifylib.py:168`) vs L17 `RuleVerificationError` (bad, `verifylib.py:949,981`) is a **native library-level missing-vs-bad distinction**. The **CLI collapses it** (`in_toto_verify.py` L22: "1 if an exception occurred"). There is no tri-state verdict object. | The missing-vs-bad distinction exists at library level in a real product. | Another material weakening of the tri-state residual at the *library* level (though not at the claim level, and not in the CLI). |
| **SLSA** | **VERIFIED / CORRECTED.** "inconclusive" = **0 hits on every SLSA page**; VSA `verificationResult: PASSED\|FAILED`; unsupported provenance ⇒ **hard error**; v1.0 "Status: Retired", v1.2 current; `slsa-verifier` has no `--max-age`/expiry flag. | SLSA has a binary verdict and no freshness parameter. | Confirms that neither in-toto nor SLSA provides the tri-state or the epoch binding. |
| **TUF v1.0.37, Sigstore/cosign** | Verified by the prior-art reviewers. TUF's "mix-and-match" goal and Sigstore's role/keyless binding cover the freshness and role-binding ingredients. | Prior art for the per-record ingredients. | Confirms A. |

### 2.4 Real prior work on AI-agent evaluation provenance

Verified set: **Partial Evidence Bench (arXiv:2605.05379)**, CXI (3-way
authority join to one manifest), CAVA, HCP, ACE, Agent-Sentry, WeClawArena,
`llmsa`. **Best single-work coverage: 4 of the 6 ingredients. No work covers
(c) tri-state adjudication and (d) freshness/epoch jointly.**

## 3. The six-ingredient coverage matrix

The six ingredients are the ones the project itself identified as its
distinguishing design (from `AGENT5_PRIOR_ART_NOVELTY_MATRIX.md`):

| Ingredient | RFC 9334 | in-toto | SLSA | TUF | Sigstore/cosign | `llmsa` | Partial Evidence Bench | **This project's Stage 1** |
|---|---|---|---|---|---|---|---|---|
| (a) trusted execution observer separated from the producer | RATS archetype | partial (functionary) | no | no | no | partial | no | **yes** (TEO holds a secret key) |
| (b) per-claim cross-record joins | §8.1 yes | **yes** (MATCH/MODIFY) | partial | partial | no | yes (typed deps) | no | **yes** (11 joins) |
| (c) tri-state adjudication (REJECT / INCONCLUSIVE / SUCCESS) | **no** (§8.4 binary) | library-level only (CLI collapses) | no (binary) | no | no | **yes** (stage-level) | no | **yes** (claim-level) |
| (d) freshness / epoch / replay | **yes** (§12.3) | no | no | **yes** | partial | partial | no | **yes** (epoch + ReplayState) |
| (e) role-authorized issuance | §8.2 | **yes** | yes | yes | **yes** | yes | no | **yes** (IssuerPolicy) |
| (f) non-concealing final aggregation | §8.4 binary | no | no | no | no | partial | **yes** (unsafe_completeness_rate) | **yes** (levels + reasons) |

**(c) × (d) jointly is covered by no verified work.** That intersection — a
claim-level tri-state *inside* a freshness- and epoch-bound chain — is the
narrowest defensible residual, and it is a **B/C** claim, not a D claim.

## 4. The AI-specificity claim is dead

The historical experiment's composer was **scripted**. The Stage 1 composer is
**also scripted** (`s1_runner.py` writes the contradictions directly). The
H1-R3 campaign's producer arm was a model, but it never composed certificates.

Consequently:

* An AI-only outcome difference would be an **arm-specific outcome under a
  given prompt/model/search setup**, not an AI-specific mechanism.
  (Historical correction C-04 in `HISTORICAL_CORRECTION_LEDGER.md`.)
* The multi-agent re-audit already recorded that the composer was scripted,
  and `AGENT5_PRIOR_ART_NOVELTY_MATRIX.md` accepts this correction.
* The nearest published work — Partial Evidence Bench — measures
  `unsafe_completeness_rate` in an AI-evaluation context. Even a *successful*
  AI-vs-scripted arm difference would land next to a published metric, not in
  empty space.

**No AI-specific mechanism claim is made in this phase, and none is
supportable on the current evidence base.** Stage 4 is additionally blocked on
authorisation (`stage4_arms/STAGE4_ARM_STATUS.md`), so no arm data exists.

## 5. What the project may still claim, and what it may not

**MAY claim (Category A / B / thin C):**

1. An end-to-end, *causally grounded* attribution contract for an agentic
   exploitation-evaluation campaign, in which the trusted execution observer is
   a distinct key holder, and in which the frozen Stage01 production pair is
   measured to **accept** two attribution claims whose causal chain is broken.
2. A **measurement** of how much of the false-promotion surface each
   verification layer closes: 13 → 11 → 6 → 0 false attributions out of 25
   ground-truth non-successes as signatures, then signed context, then causal
   joins are added.
3. A **tri-state** adjudication of an evaluation-evidence chain that
   distinguishes *absent* from *contradictory* evidence — the part that RFC
   9334's binary verdict, SLSA's binary verdict, and the in-toto CLI's exit
   code cannot express.

**MAY NOT claim:**

1. A previously unknown security mechanism (Category D) — foreclosed by
   RFC 9334 §8.1 and §12.3.
2. A novel *concept*; the binding/freshness/role principle is A.
3. Product superiority over in-toto/SLSA/Sigstore — Stage 2 is
   `NOT_COMPARABLE` for SLSA and cosign and, for in-toto, is blocked on one
   permission (G-1) and has not been executed.
4. Any deployed-attacker or live-campaign exploit — Stage 3 found
   `NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED`.
5. Any AI-specific mechanism — the composer was scripted; Stage 4 is blocked.

## 6. Incompleteness disclosure

* The full text of **preprints 202610.0322 "Grounded but Wrong"** could not be
  obtained (preprints.org returned HTTP 403 on five attempts; OpenAlex gave
  metadata and the abstract only). The novelty comparison is therefore
  **incomplete for that work**. It is the single most consequential omission,
  because it is the closest published measurement of the same class of defect.
* Four `[UNVERIFIED]` and three `[ESTIMATE]` tags remain in
  `AGENT3_PROVENANCE_COMPARATOR_ANALYSIS.md`; the Stage 2 document marks
  every row that rests on them.
* No exhaustive-duplication proof was attempted or achieved. The claim made
  here is "the mechanism is named in prior art", which is *sufficient* to
  foreclose D and is supported by verbatim text.
