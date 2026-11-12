# HEB-1 Prior-Art Assessment — Cross-Boundary Verdict Promotion

**Date:** 2026-10-19
**Artifact:** `sp2027/analysis/heb1_crossboundary_20261019/HEB1_PRIOR_ART_ASSESSMENT_20261019.md`
**Status:** FINAL for the novelty gate. Supersedes the preliminary conclusion in `PRIOR_ART_NOTES_20261019.md`.
**Scope:** Independent closest-prior-art verification for the HEB-1 novelty track (per `EVALUATOR_BOUNDARY_NOVELTY_PROPOSAL.md` §8 and `NOVELTY_REVIEW_RESPONSE_20261018.md` §4-§5, point 29: prior-art differentiation is a pre-implementation hard gate).
**Constraints honored:** offline; no model/provider calls; no modifications to the manuscript, result locks, or prior campaigns (H1, R0/R1, P010 untouched).

---

## 1. Claim under assessment

**HEB-1 hypothesis:** an evaluator that composes a candidate artifact + a reference-oracle verdict + an evidence-integrity verdict without enforcing candidate/run/condition/target/claim identity at every join can promote a cross-boundary verdict into a falsely attributed "verified exploit completion" claim; a claim-specific binding validator prevents this without unacceptable clean-case false rejection.

**Novelty filter — the proposal §8 five-element combination (all five required simultaneously):**
- **E1** Cross-object/run semantic binding (candidate, run, condition, target, executor, output, claim level).
- **E2** Weaker→stronger claim promotion (evidence valid only for a weaker claim class promoted to a stronger attributed claim).
- **E3** Independent cryptographic recomputation (ground truth recomputed from private target state; never read stored labels).
- **E4** Blind claim-specific validation (validator consumes only a public certificate view + public evidence; never private truth, reference output, or defect labels).
- **E5** Measurement against hash/schema baselines (false-attribution-promotion rates under B0–B4 conditions vs V0/V1 baselines, with clean controls).

---

## 2. Method

- **Direction of scan:** (a) agentic exploitation/cryptanalysis benchmarks; (b) agent-evaluation reliability / oracle integrity; (c) agent-runtime and governance-layer binding; (d) practice reports of AI cryptanalysis; (e) claim/evidence-binding audits.
- **Inclusion criterion:** any work touching at least one of E1–E5.
- **Evidence used:** in-repo prior-art matrix (`contract_sound_prior_art_matrix_v1.md`); web sweep (2026-10-19) with targeted deep checks: SimGlot README + paper page; NGCC ePrint 2026/2266 abstract; "Grounded but Wrong" abstract via OpenAlex record W7220980858; ReplayBench repository; full sweep notes in `PRIOR_ART_NOTES_20261019.md`.
- **Depth caveat:** several works classified from abstracts/READMEs rather than full texts (flagged in §7).

---

## 3. Closest works — element coverage

Legend: **–** not addressed; **P** partial/adjacent coverage.

| Work | Layer / domain | E1 | E2 | E3 | E4 | E5 |
|---|---|---|---|---|---|---|
| ExploitGym (arXiv:2605.11086) | exploitation benchmark (scale) | – | – | – | – | – |
| ExploitBench (arXiv:2605.14153) | exploitation benchmark | P | – | P | – | – |
| CryptanalysisBench (arXiv:2607.18538) | cryptanalysis benchmark | – | – | P | – | – |
| ReproBench (arXiv:2609.34450) | reproduction pipeline | P | – | – | – | P |
| SimGlot / "When Agent Evaluation Becomes Unreliable" (arXiv:2610.16067) | harness oracle integrity | P | – | – | – | P |
| TRAP / ReplayBench (arXiv:2610.16333) | agent runtime misbinding | P | – | – | – | – |
| Governing Dynamic Capabilities (arXiv:2603.14332) | governance-layer binding | P | – | P | – | – |
| NGCC first week (IACR ePrint 2026/2266) | practice report | – | – | – | – | – |
| Grounded but Wrong (preprints 202610.0322) | claim–computation binding audit (statistics) | – | – | – | P | P |

### Per-work notes

- **ExploitGym** — measures agent capability to develop exploits at scale (898 vulnerabilities). No evidence binding, no promotion, no validation comparison. Not overlapping.
- **ExploitBench** — 16-flag exploit ladder; per-run randomized challenge-response binds artifacts to the run instance; differential execution against ground-truth binaries verifies flags. Binding is **within-run and artifact-level**; no cross-run/cross-condition composition, no claim-strength promotion, no blind claim-specific validator, no hash/schema baseline comparison for released attribution claims.
- **CryptanalysisBench** — 191 cryptanalysis tasks with independently verifiable attack criteria. Independent verification ≠ independent recomputation of an evaluation verdict; no promotion modeling, no blind-protocol measurement.
- **ReproBench** — six evidence-backed reproduction stages; artifact-grounded phase outcomes. Evidence discipline inside a reproduction pipeline; no cross-boundary promotions, no cryptographic recomputation, no claim-strength levels. Closest axis: evidence-backed decision gating (pipeline granularity).
- **SimGlot** (closest single-harness reliability study) — audits the τ-bench evaluation harness as software. Oracle defect: reward function resets the environment DB to build a ground-truth hash and never restores it; post-session scoring re-reads the polluted state → archived labels 4,194 database passes vs 2,883 under independent replay (94.3% → 65.5% success over 4,320 episodes). Audit: 8 checks (5 state-integrity invariants + 3 known-answer controls) + 7-defect-class fault-injection battery; 21 variants × 3 targets; detects 54/57; 4/8 checks load-bearing. Four gates: validity regression, order/cache counterexample, scoring regression, **source binding**. Scope: single-harness label integrity. **No cross-object/run verdict composition, no weaker→stronger promotion, no cryptographic recomputation, no hash/schema baselines.** Overlap: E1 partial (source binding / state integrity), E5 partial (measured sensitivity/specificity). Different in kind: it audits one harness's labels; HEB-1 concerns composition across run/condition boundaries in released verdicts.
- **TRAP / ReplayBench** — "tool-result misbinding": a real result consumed in an incompatible context → unsafe agent action; cross-task replay FSER 0.649. Runtime-execution layer; no evaluation-verdict promotion, no cryptographic recomputation, no claim-specific validation of released claims.
- **Governing Dynamic Capabilities (2603.14332)** — governance-layer cryptographic binding + reproducibility verification for agent tool use (capability-context separation; chain verifiability; bounded divergence; Ed25519/BBS+/Groth16). Binding is provable at the governance layer; no evaluation-attribution composition, no promotion measurement, no blind validator vs baselines.
- **NGCC ePrint 2026/2266** — practice report of the first week of AI cryptanalysis on 119 NGCC candidates; 191 findings for 89 candidates (78 Critical); 110 verified/disclosed by the authors' agentic workflow; describes workflow, review loop, classification ruleset, and observed failure modes — including "**Verification that does not verify**". Practice-level motivation that verification failure is real in agentic cryptanalysis; not a controlled mechanism study; no cross-boundary composition measurement; no baselines. Overlap: motivational only.
- **Grounded but Wrong (Oct 2026, Karamat)** — claim–computation binding audit: a deterministic instrument classifying whether each claim in an AI-generated analysis is bound to the executed tool call that produced its statistic (errored / variable-mismatch / stat-mismatch / clean). Setting: agentic statistical root-cause analysis (Six Sigma DMAIC Analyze phase). Findings: a no-LLM fill-in-the-blanks template scores 0.867 on a completeness rubric with verified-recall 0; on a pre-hardening DMAIC corpus (n=23 supported claims, 3 small open-weight models), 52.2% of claims (12/23) carry a binding defect although audit-ID provenance resolves 100%, and ~26% cite a real, audit-logged statistic that actually concerns different variables. Pre-registered ablation (180 runs; 45 pairs/contrast; hash-frozen scoring): the full 12-safeguard stack cuts the run-level defect rate from 28.9% to 2.2% (Holm-corrected p=0.0055); single-component contrasts not significant (effect is stack-level). Domain: statistical-analysis correctness, not cryptographic exploitation evaluation. **Closest work on the E4 axis (claim-specific binding) and E5 (pre-registered ablation with baselines), in a different domain and layer.** No cross-run/cross-condition composition, no promotion of a weaker verdict to a stronger claim, no cryptography.
- **Peripheral (motivational context only):** "The Independence Problem in AI-Assisted Cryptanalysis" (postquantum.com); ClaimArena-LLM (MDPI); BetterBench; arXiv:2510.07575.

---

## 4. Element-by-element findings

- **E1 (cross-object/run binding):** covered only partially and in adjacent layers — SimGlot (source binding gate; harness state integrity), TRAP/ReplayBench (runtime misbinding detection), 2603.14332 (governance-layer cryptographic binding), ExploitBench (within-run artifact binding), ReproBench (stage-grounded evidence). None bind **evaluation verdicts across run/condition boundaries** in cryptographic exploitation evaluation.
- **E2 (weaker→stronger promotion):** no found work models promotion across claim-strength levels (evidence valid for a weaker claim promoted to a stronger attributed claim). Closest thematic neighbors: TRAP's "misbinding → unsafe action" (runtime action, not claim promotion) and Grounded-but-Wrong's binding defects (form vs correctness, not promotion).
- **E3 (independent cryptographic recomputation):** no found work recomputes cryptographic predicates from private target state as the ground truth of an evaluation verdict under a blind protocol. ExploitBench's differential execution approximates effect verification but is not blind verdict recomputation.
- **E4 (blind claim-specific validation):** Grounded but Wrong is the closest (deterministic claim↔computation binding audit), but in statistical analysis and as an instrument applied to corpora, not as a blind validator of released evaluation claims under adversarial fixtures. SimGlot's known-answer controls are harness-internal, not claim-specific validators.
- **E5 (measurement vs hash/schema baselines):** SimGlot measures sensitivity/specificity (54/57) via fault injection; Grounded but Wrong uses pre-registered ablations vs artifact-hygiene baselines. Neither measures **false-attribution-promotion rates** of composed verdicts against hash-only/schema+reference baselines in exploitation evaluation.

---

## 5. Determination

**No found work demonstrates the exact five-element combination simultaneously.** The failure *family* is recognized in adjacent layers — oracle unreliability (SimGlot), provenance spoofability (Grounded but Wrong), tool-result misbinding (TRAP), verification-practice gaps (NGCC) — but the specific composition targeted by HEB-1 (cross-boundary verdict promotion in AI-authored cryptographic exploitation evaluation, measured under independent cryptographic recomputation with blind claim-specific validation and hash/schema baselines) is not established.

**Decision: GO (provisional, evidence-gated) — proceed to the frozen offline evaluation.**
The novelty gate clears only because the mechanism's empirical establishment in this exact composition is absent from prior art. The determination "genuinely new security finding" remains contingent on the offline evaluation exhibiting the mechanism (§6). If the evaluation fails to exhibit it, the outcome is NO-GO and must be documented with exact evidence — including negative results.

---

## 6. Falsification conditions for the offline evaluation

- **F1:** If baselines (V0/V1) produce no false promotions on the B1–B4 suites → mechanism not exhibited → NO-GO.
- **F2:** If V2 yields no measurable reduction in false-promotion rate vs V1 → mitigation not distinct → NO-GO.
- **F3:** If clean controls show V2 false-rejection beyond threshold (or V2 effectively all-rejects) → invalid measurement → NO-GO / redesign.
- **F4:** If post-freeze held-out patterns do not reproduce the mechanism or V2's advantage → bounded/negative result, reported as such.
- **Success criterion discipline:** empirical evidence of the failure mechanism — not passing unit tests, not additional documentation, not perfect detection on self-designed faults alone.

---

## 7. Threats to validity

- Search coverage: naming variation and a fast-moving (2026) area; the sweep is not exhaustive.
- Depth: NGCC (PDF 403) and Grounded-but-Wrong (full text blocked; abstract via OpenAlex) were classified at abstract level; SimGlot at README + abstract level.
- Recency: SimGlot and Grounded-but-Wrong are very recent; their framing may evolve.
- Scope discipline: no historical campaign (H1, P010, R0/R1) is reused as novelty evidence — their role is bounded to historical motivators/labeled controls only.

---

## 8. Next steps (build plan, per proposal gates)

1. Build the frozen offline evaluation in `sp2027/analysis/heb1_crossboundary_20261019/`: fixtures B0–B4 across two cryptographic primitives (ECDSA nonce-reuse; ChaCha20 keystream reuse), reusing hardened-v2 formats; independent adjudicator (recompute from private target state); validators V0/V1/V2; clean controls (5 types incl. reference-acceptance-without-attribution); historical motivators labeled outside blind input.
2. Freeze V2 + configuration (hashes) BEFORE held-out generation; held-out must include at least one composition pattern unused in V2 development.
3. Single evaluation pass; preserve all outcomes (including failures and unexpected false acceptances).
4. Final determination artifact + concise report.

---

## Appendix A — Sources consulted

- `sp2027/analysis/EVALUATOR_BOUNDARY_NOVELTY_PROPOSAL.md` (§8 five-element filter)
- `sp2027/analysis/NOVELTY_REVIEW_RESPONSE_20261018.md` (§4-§5)
- `sp2027/analysis/contract_sound_prior_art_matrix_v1.md`
- `sp2027/analysis/heb1_crossboundary_20261019/PRIOR_ART_NOTES_20261019.md`
- arXiv:2605.11086 (ExploitGym); arXiv:2605.14153 (ExploitBench); arXiv:2607.18538 (CryptanalysisBench); arXiv:2609.34450 (ReproBench); arXiv:2610.16067 (SimGlot paper); github.com/JunjieChen0/SimGlot; arXiv:2610.16333 (TRAP/ReplayBench); github.com/Phitooo/Replaybench; arXiv:2603.14332 (Governing Dynamic Capabilities); eprint.iacr.org/2026/2266 (NGCC); doi.org/10.20944/preprints202610.0322.v1 (Grounded but Wrong; OpenAlex W7220980858).
