# Stage 12 — Novelty Prior-Art Matrix

**Project:** ACTS-Attack  
**Stage:** Stage 12 — Novelty Validation / Prior-Art Gate  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/`  
**Date:** 2026-10-20  
**Status:** COMPLETE (read-only analysis; no external fetches)

---

## 1. Method

Per the research handoff §12, novelty is classified into:

- **A.** Known general principle.
- **B.** Known mechanism applied to a new domain.
- **C.** New empirical measurement methodology.
- **D.** Previously unrecognized causal failure mechanism.
- **E.** New defense with a measurable advantage over a fair, technically appropriate baseline.

Only **D**, or an exceptionally substantive and independently established **E**, could support an exceptional-mechanism contribution. The prior-art comparison below is **evidence-gated**: where full texts were not available, the comparison is marked incomplete rather than declaring full duplication or novelty.

No external fetches were performed (offline per handoff). All prior-art references are from in-repo documents and the research handoff.

---

## 2. Prior Art Covered (Element-by-Element)

The following works were assessed against the five-element composition filter (E1–E5) from `HEB1_PRIOR_ART_ASSESSMENT_20261019.md`:

| Work | Domain | E1 cross-object binding | E2 weaker→stronger promotion | E3 indep. crypto recomputation | E4 blind claim-specific validation | E5 hash/schema baselines | Overlap Risk |
|------|--------|------------------------|------------------------------|--------------------------------|-----------------------------------|--------------------------|--------------|
| ExploitGym (arXiv:2605.11086) | Exploitation benchmark (898 vulns) | – | – | – | – | – | Working agent exploits + scale insufficient |
| ExploitBench (arXiv:2605.14153) | Exploitation ladder, 16 flags, differential execution | P (within-run) | – | P (effect verification) | – | – | Capability decomposition already established |
| CryptanalysisBench (arXiv:2607.18538 v2) | Cryptanalysis tasks, 191 tasks | – | – | P | – | – | Task coverage / known attacks insufficient |
| ReproBench (arXiv:2609.34450) | Firmware reproduction pipeline | P (stage-grounded) | – | – | – | P | Staged artifacts insufficient alone |
| SimGlot / "When Agent Evaluation Becomes Unreliable" (arXiv:2610.16067) | Harness oracle integrity | P (source binding) | – | – | – | P (fault injection 54/57) | Single-harness label integrity, not cross-boundary composition |
| TRAP / ReplayBench (arXiv:2610.16333) | Agent runtime misbinding | P (runtime misbinding) | – | – | – | – | Runtime action, not verdict promotion |
| Governing Dynamic Capabilities (arXiv:2603.14332) | Governance-layer binding | P (cryptographic binding) | – | – | – | – | Governance layer, not evaluation-attribution |
| NGCC ePrint 2026/2266 | AI cryptanalysis practice report | – | – | – | – | – | Motivational context only |
| Grounded but Wrong (Karamat, Oct 2026) | Claim–computation binding audit (statistics) | – | – | – | P (claim↔computation binding) | P (pre-registered ablation) | Closest on E4/E5, but different domain & layer |

**Legend:** – = not addressed; P = partial/adjacent coverage.

### Key finding (per HEB-1 prior art assessment §5)

**No found work demonstrates the exact five-element combination simultaneously.** The failure *family* is recognized in adjacent layers (oracle unreliability, provenance spoofability, tool-result misbinding, verification-practice gaps), but the specific composition — cross-boundary verdict promotion in AI-authored cryptographic exploitation evaluation, measured under independent cryptographic recomputation with blind claim-specific validation and hash/schema baselines — is **not established** in prior art.

**Novelty determination (as originally issued): GO (provisional, evidence-gated).** Clears the pre-implementation hard gate only because the mechanism's empirical establishment in this exact composition is absent from prior art. The determination "genuinely new security finding" remains contingent on the offline evaluation exhibiting the mechanism.

**Novelty determination (final, after Stages 3–6): NO-GO for a novel-mechanism claim, and NO-GO for a strong composition claim. GO only for a matched measurement, a checkable reference contract, and reproducible artifacts.** The mechanism's components are known, their union is established, the family (confused deputy / evidence substitution) is decades old, and the closest 2026 work supplies a theorem — a harder-to-beat baseline than a measured detection rate. What survives is the *measurement* (identical evidence, native upstream models 16/16 and 6/6 misdecisions vs the contract's 0/16), the contract itself, and the artifacts. See `MECHANISM_SPECIFICATION.md` §4–§6.

---

## 3. Stage 1 Results vs Prior Art Claims

The Stage 1 e2a confirmatory run exhibited the mechanism:

| Claim | Prior art covers? | Stage 1 evidence |
|-------|-------------------|------------------|
| Cross-boundary composed evidence can promote unsupported attribution | Partially (SimGlot, TRAP, Grounded-but-Wrong adjacent) | **Yes** — V0/V1-style schema/hash systems promote; claim-binding rejects (HEB-1: V0/V1 36/36 FP, V2 0/36) |
| Claim-specific binding prevents promotion without unacceptable false rejection | Partially (Grounded-but-Wrong E4 adjacent) | **Yes** — 6/6 honest accepted, 0/16 negative controls falsely promoted |
| Independent cryptographic recomputation as ground truth | Not established | Stage 1 reference recomputes predicate from private target state (never reads stored labels) |
| False attribution promotion measured vs hash/schema baselines | Not established | Stage 1 measures 0 false positives, 0 false negatives across 22 cases |

---

## 4. What Is NOT Novel (Must Not Be Claimed)

Per `contract_sound_prior_art_matrix_v1.md` contribution boundary:

| Not sufficient alone | Reason |
|----------------------|--------|
| A certificate format | Generic; prior art covers evidence structures |
| A larger task list | CryptanalysisBench already covers task count |
| An additional metric | Not a contribution by itself |
| A generic warning about oracle integrity | SimGlot already covers harness oracle defects |
| Benchmark size or generic exploit success | ExploitGym/ExploitBench already established |
| 6/6 honest acceptance alone | Expected; not novel |

---

## 5. What Could Be Novel (Contingent on Evidence)

The following **could** support a distinct contribution **only if** all conditions from `contract_sound_prior_art_matrix_v1.md` §"Contribution boundary" are met:

1. C1 and C2 proven equivalent and sufficient over the complete agent-accessible interface.
2. Agent outcome differs reproducibly under the representation intervention, OR the validator discovers a cryptographic-specific held-out failure mechanism not captured by baselines.
3. The effect is not a prompt/parser/transport/oracle/environment/budget confound.
4. Independently replayable artifacts with explicit claim boundaries.
5. Negative and inconclusive outcomes retained.

**Observed status after Stage 4:** conditions 4 and 5 are satisfied. Two independent bodies of evidence were collected.

*The matched arm (the stronger evidence).* The only substituted factor was the producer: the model authored program bytes that the **frozen** E2A evaluator then screened, executed, adjudicated and decided, exactly as the scripted arm. The model arm and the scripted arm agreed on 18/22 cases, and all four disagreements were mechanically explained (the model used the P-521 curve order for P-256 instances in three cases; in one case it printed a correct answer and then exited non-zero). Every attribution the evaluator issued was backed by an independently adjudicated positive predicate, and no artifact with a false predicate was ever attributed.

*The earlier 72-session pilot.* C1 24/24 and C2 22/24, a paired difference of −0.083 (95% bootstrap interval [−0.208, 0.000], McNemar p=0.500), below the preregistered 0.25 meaningful-effect threshold.

Thus condition 2's reproducible representation-effect branch is **not supported**, and no new cryptographic-specific held-out mechanism survived the Agent 4 audit. The strong exceptional-mechanism novelty route does not clear.

**Stage 3 contribution.** A controlled loopback ingress in front of the frozen aggregator was constructed and exercised against the project's own local target: 12 submissions, one positive control attributed, eleven non-control submissions refused, zero unauthorized attributions, including five model-authored forgery fixtures.

**Stage 5 contribution (live campaign).** The project's own containerised target was started, exploited over a real network interface, its reserved secret disclosed and independently adjudicated by a separate-process oracle, and the frozen contract attributed it. The model agent did not complete the exploit within the task card's own caps, and the contract refused it.

**Stage 6 contribution (matched translation, corrected).** The identical evidence was run through the upstream models under three distinct configurations. A **minimally configured** in-toto deployment (no artifact rules, no inspection) accepts all 22 and promotes 16 of 16 non-attributable cases — a default-configuration measurement, not an in-toto limitation. Given in-toto's own artifact rules **and** an independent inspection, in-toto reproduces the ACTS contract's decisions exactly (22/22 with a stateful inspection, 21/22 stateless, zero false promotions and zero false rejections). SLSA is **NOT_COMPARABLE** here: verification stops at provenance acquisition, before any policy stage. The finding is therefore not a superiority claim but a *division of labour*: the frameworks supply the machinery, the adopter must supply the policy.

**HEB-2 contribution (mechanism and property).** The mechanism is now stated minimally with an executable soundness property, checked over 11,256 mutation evaluations with **0 violations**; the only mutation class that remains acceptable is the deliberately-ignored claim block. See `MECHANISM_SPECIFICATION.md`.

---

## 6. Conclusion

No full-text prior art was found that establishes the exact five-element composition (E1–E5) simultaneously, but Stage 4 did not demonstrate the preregistered large representation effect and the relevant provenance/binding ingredients are established in adjacent work. The correct disposition is **NO-GO for a strong novel-mechanism claim; GO only for a narrow empirical measurement/benchmark contribution**.

**Permitted claim:** an *operationalisation* of a known pattern (confused deputy / evidence substitution) into a specified, checkable contract for claim-sound cryptographic-agent evaluation: a mechanized soundness check (11,256 evaluations, 0 violations), a matched-arm demonstration under a model producer, a boundary demonstration over a network ingress, a live campaign against the project's own containerised target, and a corrected matched comparison showing that the upstream frameworks supply the machinery while the **policy** is the adopter's responsibility. **Not** permitted: claiming invention of provenance, causal binding, tri-state adjudication, a new security mechanism, a large AI-specific representation mechanism, **any superiority over provenance systems**, or model exploitability in general.