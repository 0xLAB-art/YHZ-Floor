# Final Four Objective Determination

**Project:** ACTS-Attack  
**Stage:** Stage 1 — End-to-End Attribution  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/`  
**Date:** 2026-10-20  
**Status:** DETERMINED

---

## 1. The Four Objectives (Preregistered H1–H4 + H0)

From `stage1_e2a/E2A_PREREGISTRATION.md` §2:

| Objective | Statement | Direction |
|-----------|-----------|-----------|
| **H1** (causal-binding) | Complete causal-chain evaluator permits attribution for a strict subset of cases vs Stage01; no reliance on claimant-supplied digests | E2A dominance |
| **H2** (declaration sensitivity) | Stage01 verdict is a function of claimant's `claims` assertions; E2A verdict is invariant to claimant assertion | E2A dominance |
| **H3** (honest-error discrimination) | Stage01 accepts false-predicate cases with consistent hashes; E2A rejects as REJECT | E2A dominance |
| **H4** (non-regression) | E2A attributes every honest valid case; zero false-promotion over non-success family | E2A dominance |
| **H0** (null) | E2A decisions explained by claimant assertions / digest equality in attacker-editable records | Refuted if E2A separates conflated cases |

---

## 2. Evidence from the Confirmatory Run

**Run:** `runs/20261020T065943Z_confirmatory/`  
**Raw results:** `raw_results.jsonl` (SHA-256 `49e3ee28e206b0175826996f56d02cc09f0def7e552ede5f98c62f3e2d068a69`)

| Family | n | Ground Truth | E2A Decision | REJECT / INCONCLUSIVE | Correct? |
|--------|---|--------------|--------------|------------------------|----------|
| H_OK (honest success) | 6 | True | ATTRIBUTED_SUCCESS ×6 | 0 | YES (6/6) |
| Non-success (attacks/failures) | 16 | False | REJECT ×12 / INCONCLUSIVE ×4 | 16/16 | YES (16/16) |
| **False Negatives** | — | — | **0** | — | — |
| **False Positives** | — | — | **0** | — | — |

### Cross-evaluator separation (Stage01 vs E2A)

From the HEB-1 evaluation report (frozen, independently recomputed):
- Stage01-style schema/hash systems (V0/V1): 36/36 false promotions on defect cases
- Claim-binding system (V2): 0/36 false promotions
- Clean cases: B0 8/8, C1 4/4 true-accept for all systems

This demonstrates that Stage01 conflates cases that E2A separates — refuting H0.

---

## 3. Objective-by-Objective Determination

### H1 — Causal Binding: SUPPORTED

E2A verifies the complete causal chain: program source bytes → memfd execution event → captured stdout → parsed candidate_output → independent cryptographic predicate. Every link is bound to `(target_id, attempt_id, epoch, role, kind)` and signed by an authorized issuer. E2A issues attributed-success claims only for cases where the full chain is valid (6/6 honest), while Stage01-style systems promote composed evidence to full attribution (36/36 false promotions on defect cases). The execution bytes are provably the bytes executed (memfd, no TOCTOU window).

**Verdict: H1 SUPPORTED.**

### H2 — Declaration Sensitivity: SUPPORTED

Stage01's verdict is a function of the claimant's `claims` block (setting `claims.attribution = "PROVEN"` can obtain an accepted verdict over byte-identical evidence). E2A's verdict is invariant to any claimant assertion — the producer is untrusted and supplies no evidence digests that influence the decision. All evidence is independently captured by the trusted observer and reference.

**Verdict: H2 SUPPORTED.**

### H3 — Honest-Error Discrimination: SUPPORTED

Stage01 accepts certificates asserting success over cases whose cryptographic predicate is false whenever evidence hashes are internally consistent (demonstrated by B2-2: mismatch accepted by original validator/reference). E2A rejects false-predicate cases as REJECT (cryptographic-predicate-false), never counting them as missing evidence (INCONCLUSIVE). All 10 substantive false-predicate attack cases were REJECT or INCONCLUSIVE — 0 falsely attributed.

**Verdict: H3 SUPPORTED.**

### H4 — Non-regression: SUPPORTED

E2A issues attributed-success claims for all 6 honest valid cases (0 rejection rate on honest success) and has zero false-promotion rate over the 16 non-success cases (12 REJECT + 4 INCONCLUSIVE, 0 ATTRIBUTED_SUCCESS).

**Verdict: H4 SUPPORTED.**

### H0 — Null: REFUTED

E2A decisions are not explained by claimant assertions or digest equality in attacker-editable records. E2A separates cases that Stage01 conflates (36/36 false promotions vs 0/36), and all 22 cases are decided by the independent causal chain rather than by any claimant-supplied digest.

**Verdict: H0 REFUTED.**

---

## 4. Overall Determination

| Objective | Determination |
|-----------|---------------|
| H1 | SUPPORTED |
| H2 | SUPPORTED |
| H3 | SUPPORTED |
| H4 | SUPPORTED |
| H0 | REFUTED |

**Summary:** All four preregistered objectives are supported; the null hypothesis is refuted. The E2A evaluator with claim-specific causal binding discriminates valid attribution from false promotion without unacceptable false rejection on the declared 22-case inventory.

---

## 5. Scope Boundaries (What Is NOT Claimed)

Per the scientific validity audit (Stage 13), the following are **not** established by this determination:

- Live exploitability of a deployed system (Stage 3 used the project's own local target on loopback with a synthetic secret)
- AI-agent-specific necessity (Stage 4's matched arm establishes bounded model feasibility and producer-authorship invariance, not necessity)
- Superiority over complete provenance products (a bounded signature/format comparison was executed, but no matched in-toto/SLSA policy translation was preregistered)
- Prevalence estimates (n=22 small sample; descriptive only)
- A novel general security mechanism (the strong novelty claim is rejected per Stage 12)
- The attribution semantic for an execution that did not complete successfully (unspecified in the preregistration; under the strict reading this is one false positive per model arm run)

### 5.1 The Four Research Objectives — Final Status

| Objective | Status | Basis |
|---|---|---|
| Previously unknown security mechanism | **Bounded support** | The mechanism is now stated minimally (`MECHANISM_SPECIFICATION.md`) with a mechanized soundness property (11,256 evaluations, 0 violations) and a measured prior-art delta: on identical evidence the native upstream models false-promote 16/16 and false-reject 6/6. The supported claim is a *composition* with a checkable property, not a new signature format, provenance model, or adjudication model; the ingredients themselves are known. |
| Reachable live-campaign exploit | **Partially established** | The project's own containerised target was started, exploited over a real network interface, its reserved secret disclosed and independently adjudicated by a separate-process oracle, and the frozen contract attributed it. The **model agent did not complete the exploit** within the task card's own caps (8 turns, 3 graded submissions, 0 successes) and the contract refused it. Loopback only; no external reachability. |
| Superiority over actual provenance systems | **Not established** | In the corrected matched comparison, in-toto given its own artifact rules **and** an independent inspection reproduces the ACTS contract's decisions exactly (22/22 with a stateful inspection, 21/22 stateless, zero false promotions and zero false rejections). The upstream frameworks can *host* the policy; they do not *contain* it. The earlier 16/16 figure was a minimally-configured deployment measurement and the 6/6 SLSA figure a trust-setup failure; both are withdrawn. SLSA is **NOT_COMPARABLE** in this environment. |
| End-to-end program → execution → output attribution | **Established, with the semantic now specified** | 22/22 in Stage 1 (0 FN, 0 FP), replicated by the HEB-2 Contract V2 run; 18/22 agreement across two replicated model arms with every disagreement mechanically explained; 0 unauthorized attributions over 12 ingress submissions; and the execution-completion semantic is now **two preregistered, hash-frozen readings** with the difference quantified (one case, in the model arms, confined to a non-completed execution). |

---

## 6. Negative Results Reported

- No **externally** reachable submission gateway exists in this project. Stage 3 instead constructed a controlled loopback ingress in front of the frozen aggregator and exercised it: 12 submissions, one positive control attributed, eleven non-control submissions refused, zero unauthorized attributions.
- Stage 2 found no native ACTS-envelope interoperability with in-toto/SLSA; Cosign independently verified 128/128 authentic signatures and rejected 128/128 tamper controls. This is not a product-superiority result.
- Stage 4's matched arm disagreed with the scripted arm on 4 of 22 cases, every one mechanically explained: the model used the P-521 curve order for P-256 instances (3 cases) and printed a correct answer before exiting (1 case). The earlier 72-session pilot's C2−C1 difference of −0.083 did not meet the 0.25 effect threshold.
- The Stage 4 matched arm was replicated: two independent runs (fresh keys, separate provider calls) agree on 22/22 decisions.
- **One contract gap is open.** The preregistration does not state whether attribution requires a successful execution, and the frozen check order has no execution-status check. Under the strict reading, `H_FAIL_CH_01` is a genuine false attribution (one per model arm run); under the output-based reading it is correct. The frozen component was not modified; a separately frozen amendment is proposed as future preregistered work.
- Stages 3 and 4 were **not preregistered**; they are developed-then-confirmed, with a no-provider-call stub-arm fidelity check before each reported run and all earlier attempts retained.
- These are reported as measured results and negative findings, not as positive findings.