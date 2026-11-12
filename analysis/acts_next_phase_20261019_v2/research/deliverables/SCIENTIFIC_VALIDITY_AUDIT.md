# Stage 13 — Scientific Validity Audit

**Project:** ACTS-Attack  
**Stage:** Stage 13 — Independent Audit of Denominators, Freezes, Claims, and Limitations  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/`  
**Date:** 2026-10-20  
**Status:** COMPLETE

---

## 1. Method

This audit independently recomputes key metrics from raw retained artifacts and reviews the multiagent re-audit corrections, historical correction ledger, freeze discipline, denominators, positive/negative controls, and causal interpretation. Read-only; no network/provider calls; no benchmark or gateway execution.

Sources:
- `heb1_independent_adversarial_audit_20261019/HEB1_MULTIAGENT_REAUDIT_20261019.md`
- `heb1_remediation_v1/scientific_corrections/HISTORICAL_CORRECTION_LEDGER.md`
- `heb1_crossboundary_20261019/HEB1_EVALUATION_REPORT.md`
- `heb1_crossboundary_20261019/heldout/heldout_results.json`
- `experiment_b_20261019/iar_c/runs/20261019_121621/results.json`
- `experiment_b_20261019/b2/runs/20261019_140814/results.json`
- Stage 1 e2a confirmatory run: `runs/20261020T065943Z_confirmatory/raw_results.jsonl`

---

## 2. Denominator Corrections (IAR-C)

Per the re-audit and correction ledger, the original IAR-C counts were recomputed with corrected denominators:

| Metric | Original (reported) | Corrected (recomputed) | Correction |
|--------|---------------------|------------------------|------------|
| IAR-C substantive attacks | 28 | 20 | Malformed controls separated from substantive attacks |
| V2 false promotion rate | 10/28 = 35.7% | 10/20 = 50% | Denominator reduced to substantive attacks only |
| V3-sig false promotion rate | 14/28 | 14/20 = 70% | Same denominator correction |
| V3-full false promotion rate | 0/28 | 0/20 = 0% | Same denominator correction |
| Honest partial cases eligible | — | 10 | Only 10 eligible partial-claim cases |
| V2 honest partial rejection | "14 false rejects" | Functionality mismatch, not false rejection | N/A treated as functionality mismatch |

**Audit finding:** The original "14 false rejects" claim was invalid — V2's partial functionality is N/A (functionality mismatch), not a false rejection. The corrected denominator is 20 substantive attacks, not 28. V2 false promotion is 50%, not 35.7%.

---

## 3. Freeze Discipline Audit

| Freeze item | Status | Finding |
|-------------|--------|---------|
| HEB freeze manifest included held-out runner | ❌ NOT included | Re-audit issue #2 confirmed — held-out runner absent from HEB freeze manifests |
| B2 freeze verification | ⚠ Partial | Checked only part of declared freeze contract (re-audit issue #3) |
| IAR-C case-manifest identity check | ❌ Not complete | Did not check every frozen case-manifest identity (re-audit issue #4) |
| Stage 1 e2a freeze manifest | ✅ Complete | All components, cases, labels, trust material, manifest hash-pinned; fail-closed preflight PASSED (38 files, 0 errors) |

**Audit finding:** Historical freezes had gaps; Stage 1 e2a freeze is complete and verified. Do not retro-fit historical freezes.

---

## 4. Multiagent Re-Audit Corrections (Incorporated)

| # | Correction | Impact on Stage 1 |
|---|-----------|-----------------|
| 1 | Claimed adjudicator-only held-out pre-pass not implemented | Does not invalidate FP counts; execution-ordering claim withdrawn |
| 2 | Adjudicator does not validate public evidence integrity | Missing-control impact untested; no fixture exposed it |
| 3 | Held-out runner absent from freeze manifests | Historical freeze gap; Stage 1 freeze complete |
| 4 | IAR-C did not check every case-manifest identity | Historical gap; Stage 1 checks all |
| 5 | Adjudicator did not establish public/private evidence correspondence | 118/118 checked in remediation v1 adjudication |
| 6 | Fixture signing keys derivable from public session IDs | Threat-model mismatch; fixture does not model secret-held issuers |
| 7 | B2-2 wrapper did not implement entire protocol | Wrapper limitation documented |
| 8 | IAR-A public/private certificates not always identical | Historical inconsistency noted |
| 9 | Provenance comparisons initially modeled, not executed | Stage 2 later executed a bounded comparison: Cosign 128/128 authentic pass and 128/128 tamper rejection; no matched in-toto/SLSA policy translation |
| 10 | Unfairly counted rejected partial claims against V2 | Corrected: V2 partial functionality = N/A |
| 11 | Duplicate-evidence overstated | V3-full already rejects duplicate evidence kinds |
| 12 | Stage01 lacks source→runtime→trace causal binding | Real but narrower gap; not a live exploit |
| 13 | No AI-agent exploitation or deployed attacker reachability established in Stage 1 | Stage 4 later supplied bounded model-authored artifacts, and Stage 3 exercised a live local target; still no deployed reachability |

**Audit finding:** All 13 corrections incorporated. No overconfident claims repeated. Stage 1 does not claim live exploitability, AI-agent-specific necessity, or superiority over provenance products.

---

## 5. Agent 4 Findings (H1-R3 Re-examination)

From the independent statistical and scientific audit (Agent 4):

| Finding | Status |
|---------|--------|
| H1-R3 primary statistics reproduce exactly | ✅ Confirmed |
| ECDSA failure-mechanism narrative refuted | ✅ Refuted — 20/25 are wrong-curve-constant errors |
| ECDSA errors concentrated in base64 (14.1%) vs hex (0.8%/0.8%) | ✅ Confirmed |
| k_ok vacuous at L1/L2 | ✅ Confirmed |
| IAR-C denominator corrected to 20 (not 28) | ✅ Confirmed |
| V2 false promotion 50% (not 35.7%) | ✅ Confirmed |
| V2 "14 false rejects" = functionality mismatch | ✅ Confirmed |
| 13/13 audit corrections confirmed | ✅ Confirmed |
| Forged Ed25519 signature from public session id | ✅ Confirmed |

**Audit finding:** Historical H1-R3 statistics are reliable; the failure-mechanism narrative and denominator claims are corrected. Stage 1 results build on this corrected foundation.

---

## 6. Stage 1 e2a Validity Audit

| Validity aspect | Result |
|-----------------|--------|
| Positive controls (6 honest success) | 6/6 ATTRIBUTED_SUCCESS — 0 false negatives |
| Negative controls (16 attack/failure) | 12 REJECT + 4 INCONCLUSIVE — 0 false positives |
| Missing evidence → INCONCLUSIVE (not zero failure) | ✅ Correct per audit correction |
| Denominator: 22 total cases | ✅ Explicitly declared |
| Confidence intervals | Not computed (n=22 small; descriptive only) |
| Preflight fail-closed | ✅ PASSED (38 files, 0 errors) |
| Manifest hash-pinned | ✅ All components pinned |
| No metric redefined after outcomes | ✅ Decision rule preregistered |
| Negative/inconclusive retained | ✅ All 22 cases preserved |

**Audit finding:** Stage 1 e2a results are internally valid: 0 false negatives, 0 false positives, correct handling of missing evidence, preregistered decision rule, complete freeze. Sample size n=22 is small; results are descriptive for this bounded experiment, not generalizable prevalence estimates.

---

## 7. Stage 3 and Stage 4 Validity Audit

| Aspect | Result |
|--------|--------|
| Stage 3 harness fidelity (stub arm, before any provider call) | Reproduced the expected decisions exactly; a harness defect would have shown as a disagreement |
| Stage 3 positive control | Live HTTP exchange with the project's own local target, independently adjudicated positive, attributed over the ingress |
| Stage 3 adversarial submissions | 11 non-control submissions, **0 attributions**; every family refused with the frozen taxonomy reason |
| Stage 3 model-authored fixtures | 5/5 valid fixtures, all refused, each with the same reason as its harness-authored control |
| Stage 3 network replay | Refused by the aggregator's replay ledger |
| Stage 4 harness fidelity (stub arm, before any provider call) | 22/22 decision agreement, identical arm statistics, identical baseline behaviour |
| Stage 4 replication | Two independent runs (fresh keys, separate provider calls) agree on **22/22** decisions |
| Stage 4 provider behaviour | 14/14 HTTP 200 per run, exact route `claude-sonnet-4-6-free`, no retry, no fallback, no embedded instance-specific answers |
| Stage 4 attribution safety | 4/4 attributions predicate-backed; 0 artifacts with a false predicate attributed; 0 true predicates missed |
| Stage 4 **contract-semantics gap** | The attribution semantic for an unsuccessful execution is unspecified in the preregistration; the frozen check order has no execution-status check. Under the strict reading the model arm carries **1 false positive per run** (`H_FAIL_CH_01`, `EXECUTION_FAILED` / rc 3); the scripted arm carries 0 because its `fail` variant emits no output. Reported as a gap, not absorbed. |
| Stage 4 disagreements | 4/22, every one mechanically explained (P-521 curve order ×3; print-then-exit ×1) |
| Stage 4 label limitation | Ground-truth labels are keyed to the scripted variant's behaviour, which can mislabel a model artifact |
| Stage 3 / Stage 4 preregistration | **None.** Both stages were developed-then-confirmed: a no-provider-call stub-arm fidelity check preceded the reported runs, all earlier attempts are retained with their provider ledgers, and the reported numbers come only from the final run. Stage 1 alone was preregistered and hash-frozen. |
| HEB-2 Contract V2 | **Preregistered and hash-frozen** before execution, with a fail-closed preflight (37 files, 0 errors) and two preregistered semantics evaluated on identical evidence |
| HEB-2 soundness check | 11,256 mutation evaluations over four corpora, **0 violations**; two corrections made during the stage are disclosed in `HEB2_CONTRACT_V2_RESULTS.md` §6 |
| Stage 5 live campaign | Preregistered and hash-frozen with a fail-closed preflight; the model arm's negative result and the control's positive result are both reported; three earlier protocol attempts retained |
| Stage 6 matched translation | Preregistered; one published translation; the native arms' misdecisions are measured on the identical evidence, and the delegation cost is quantified (37-line adapter over a 270-line frozen policy) |

**Audit finding:** Both new stages are internally valid. Each was preceded by a no-provider-call stub-arm check that proved the harness changed nothing but the intended factor, each retained every attempt and every provider response, and each reported its negative outcomes — the model author's P-521 curve-order error, the model's print-then-exit variant violation, the model author's safety refusals under the first framing, and the provider-side response truncations.

---

## 8. Claims That Must NOT Be Repeated

Per the corrections, the following overstated claims are withdrawn and must not appear in any deliverable:

- "HEB-1 establishes live exploitability" — NOT established (bounded offline experiment only)
- "HEB-1 establishes AI-agent-specific necessity" — NOT established; Stage 4 confirms bounded feasibility, not necessity
- "HEB-1 establishes superiority over actual complete provenance products" — NOT established (bounded signature/format comparison is not a matched product comparison)
- "V2 has 14 false rejects" — INVALID (functionality mismatch, N/A)
- "IAR-C denominator is 28" — INVALID (corrected to 20 substantive attacks)
- "Duplicate evidence kinds are unhandled in V3-full" — INVALID (V3-full rejects duplicates)
- "AI-only outcome implies novel AI-specific mechanism" — INVALID (outcome contrast ≠ mechanism)
- "Fixture keys model secret-held issuers" — INVALID (fixture keys derivable from session IDs)
- "E2A attributes a live network effect at a deployed gateway" — NOT established (loopback only, synthetic secret, one target)
- "The model exploited the live target" — NOT tested (the live exploit program was harness-authored)
- "Stage 3 shows the contract is secure against adversarial network attackers" — NOT established (12 instrumented submissions, one ingress)
- "Stage 4 shows the model is equally capable at both tasks" — REFUTED (0/3 honest ECDSA cases succeeded, P-521 curve order)
- "E2A produces no false attribution under any producer" — QUALIFIED: no false *predicate* was ever attributed, but the exit-status semantic is unspecified and one attribution per model run would be refused under the strict reading (see §7)
- "Stages 3 and 4 were preregistered" — INVALID (neither was; they are developed-then-confirmed with retained attempts)

---

## 9. Conclusion

The scientific validity audit confirms:

1. **H1-R3 primary statistics reproduce exactly** — reliable foundation.
2. **IAR-C denominators corrected** — 20 substantive attacks, not 28.
3. **Stage 1 e2a freeze is complete and verified** — unlike historical freezes with gaps.
4. **Stage 1 results are internally valid** — 0 false negatives, 0 false positives, 22-case denominator explicitly declared.
5. **All 13 multiagent re-audit corrections incorporated** — no overconfident claims repeated.
6. **Strong novelty is not supported** — Stage 4 C1/C2 difference was −0.083, below the 0.25 threshold (p=0.500; interval includes zero); retain only a narrow empirical measurement/benchmark contribution.
7. **The contract holds across a network ingress** — Stage 3 produced 0 unauthorized attributions over 11 non-control submissions, including 5 model-authored forgery fixtures.
8. **Producer authorship does not change the contract's safety property** — Stage 4's matched arm produced 0 false promotions and 0 unexplained disagreements, replicated exactly across two runs.
9. **The exit-status gap is now specified rather than open** — HEB-2 freezes two readings and quantifies the difference (one case per model run, confined to a non-completed execution). The choice between them remains a decision, not a discovery.
10. **The mechanism's soundness property is mechanically checked** — 11,256 evaluations, 0 violations; the only acceptable mutation class is the deliberately-ignored claim block.
11. **The live campaign's model arm is a negative result** — 0 successful claims within the task card's own caps; the contract refused it, and the control run shows the attribution path works when the evidence supports it.

The experiment is scientifically defensible within its bounded scope. It does not support broader claims beyond what the evidence shows.