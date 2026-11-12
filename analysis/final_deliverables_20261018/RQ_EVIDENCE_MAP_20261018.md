# RQ → Evidence Map — ACTS-Attack — 2026-10-18

**Deliverable #4 of the ACTS-Attack completion program.**
**Research questions:** the three defensible RQs adopted in `ACTS_ATTACK_FINAL_SCIENTIFIC_SYNTHESIS.md` §10, plus the causal-intervention question of §12 (executed this session) and the two completion-program questions resolved this session.
**Status vocabulary:** SUPPORTED (evidence adequate under stated limits) / SUPPORTED-WITH-LIMITS / WEAKENED (evidence narrows the claim) / UNSUPPORTED (no admissible evidence) / RESOLVED (completion-program question closed by artifact analysis).
**Cross-reference:** evidence row IDs are from `COMPLETE_EXPERIMENT_COVERAGE_AUDIT_20261018.md` (§A–§H) and `EVIDENCE_CHAIN_COVERAGE_MAP_20261018.md` (EC-01…EC-11).

---

## RQ1 — Which attacker-visible relations and interfaces support the recorded successful cryptographic constructions, and which apparent failures arise before a valid recovery task is administered?

| Sub-claim | Evidence | Status | Limits / forbidden inference |
|---|---|---|---|
| R1.1 Successful constructions are bounded to specific exposed relations: RC4/ChaCha20 keystream/relation exposure, ECDSA nonce algebra, interactive CBC oracle | EC-01…EC-04; A1 (V4 8/12, per-family: RC4 0/3, ChaCha20 2/3, CBC 3/3, ECDSA 3/3); A2 (18/18 bounded reproduction); A4 (held-out 4/4); A6 (surrogate, hash-proven bytes) | SUPPORTED-WITH-LIMITS | Local disclosed fixtures; hosted weights provider-attested; no cross-family generalization; no universal rate |
| R1.2 The composition fixture is execution of a supplied chain, not discovery | A5 (composition attempt2: SUCCESS, `oracle_queries=1`, scaffolded) | SUPPORTED (as negative characterization) | Must not be cited as chain discovery; provider-unavailable base retained |
| R1.3 Some apparent failures arise **before** a valid recovery task is administered (evaluator/instrument/information artifacts, not model incapacity) | B1 (H1 V2: 51/60 candidate-bearing; 0/35; 30/30 instructed abstention); B2 (XOR scorer wrong-truth defect, 10+10 control; retrospective 0/20); B3 (reduced-prompt multi-dimensional change); E-INVALID rows (H1 v1, code-feedback v1 schema defect, V4-01) | SUPPORTED | The former "universal incapability from H1" reading is rejected, not replaced by a capability rate; scorer defect characterized, not repaired in place |
| R1.4 The information **frame** itself (not just information quantity) can determine whether a valid recovery task is administered | B4 (matched 2×2): stated premise → C1 4/4, C3 4/4 first-turn (8/8); derive-it frame → C2 4/4 at higher cost (6 submissions); named-but-unstated reference → C4 0/4 with all 8 construction-level failures retained | SUPPORTED-WITH-LIMITS | Single fixture (ChaCha20 nonce reuse), n=4/cell, one provider-attested model label, descriptive exact statistics (no alpha); no pooling with H1 V2/V4/blind cohorts |

**RQ1 summary:** supported, with the sharpest new element (R1.4) from the preregistered 2×2: "withholding" and "framing a gap" are different interventions, and the zero-reference premise is the load-bearing disclosure in this fixture.

## RQ2 — Where do traces distinguish first-submission construction, revision-associated recovery, and persistent failure?

| Sub-claim | Evidence | Status | Limits |
|---|---|---|---|
| R2.1 First-submission construction occurs and is traceable | V4 per-session records (first-turn successes incl. 2×2 C1/C3 8/8; explicit lanes predominantly first-submission); EC-02/EC-04 | SUPPORTED | Denominators per contract; not a first-try rate across cohorts |
| R2.2 Revision-associated recovery occurs and is traceable | V4 revision trajectories (31 nested submissions); 2×2 C2 two second-turn recoveries via `c1 ⊕ c2` collapse; CBC intermediate programs rejected then recovered; EC-05 | SUPPORTED (descriptive) | Revisions accompany recovery; **no feedback-causality claim** (matched no-feedback baseline not run — gap G7) |
| R2.3 Persistent failure is distinguishable from the above and classifiable by stage | V4 4 oracle-failed sessions; 2×2 C4 0/4 (7 oracle + 1 parse); blind/reduced ChaCha 0/2+0/2; failure taxonomy (deliverable #2 §7, results report §6) | SUPPORTED | Stage classification is not automatic cryptanalytic incapacity; refusal labels in retry1 partially defective (1 trace) |
| R2.4 The three categories can be compared across families only as claim-types, not pooled | EC-11; canonical audit denominators | SUPPORTED (as a rule) | Cross-family synthesis is analytical only; no merged denominator |

**RQ2 summary:** supported as a descriptive stage taxonomy; feedback causality remains explicitly outside the evidence.

## RQ3 — Which claims about recovery, acquisition, workload, and generality survive independent verification and provenance reconstruction?

| Sub-claim | Evidence | Status | Limits / forbidden inference |
|---|---|---|---|
| R3.1 **Recovery** claims survive where generated code, run identity, target invocation, and oracle verdict are retained | V4 8/12; explicit 18/18 (18 distinct run IDs); held-out attempt4 4/4 (integrity-gated); surrogate 9,640-query success on hash-recovered executed bytes (`a5e8ed51…`, bit-exact replay, live re-grade) | SUPPORTED-WITH-LIMITS | Contract-bounded; attempt3 excluded; composition scaffolded |
| R3.2 **Acquisition** claims (who received or could access the secret) do **not** survive reconstruction | E5 canonical (29 records / 14 graded; 1/14 descriptive; R30 exact commitment match; 8,714 calls); E5 host-execution, unauthenticated handlers, verifier-identity mismatch; EC-09 | WEAKENED → candidate-correctness only | No enforced-acquisition, host-isolation, or authority claim from candidate equality; future work requires authenticated role-separated interfaces |
| R3.3 **Workload** claims survive only in their recorded units | 31 nested programs (submissions); adaptive 8/39 target queries; E5 8,714 reconstructed calls; CBC query counts | SUPPORTED-WITH-LIMITS | Not a cross-family effort ranking; tails not total work |
| R3.4 **Timing** claims are not independently recomputable for V4 | 0/8 raw monotonic endpoint pairs; T_op/T_M medians retained as recorded | UNSUPPORTED (as recomputation) | Reported elapsed fields are recorded evidence only (rule A4) |
| R3.5 **Generality** survives only in bounded forms | 18/18 family-stratified reproduction; held-out attempt4 2/2 dev + 2/2 held-out; Wilson illustration for V4 only | SUPPORTED-WITH-LIMITS | No cross-family generalization, no universal rate, no pooled estimate anywhere |
| R3.6 **Model identity / provenance** is partially reconstructed | E1 0/54 strict H1; EXP-034 0/12 immutable environment; provider-attested labels only | WEAKENED | Provider labels are not immutable weights identity; single experimenter/environment |

**RQ3 summary:** recovery survives bounded; acquisition and strict provenance are narrowed; workload survives per-unit; timing and universal generality do not survive in their strong forms.

## RQ4 (synthesis §12 causal-tier question) — Does changing **only** the information frame change construction outcomes?

| Sub-claim | Evidence | Status | Limits |
|---|---|---|---|
| R4.1 Stating the reference premise yields immediate robust construction | B4: C1 4/4 + C3 4/4, all first-turn, 4 submissions per cell | SUPPORTED-WITH-LIMITS | n=4/cell; one fixture; provider-attested model |
| R4.2 The premise is not a simple gate | B4: C2 4/4 under full withholding (6 submissions; 2 after feedback); F3 TRUE | SUPPORTED-WITH-LIMITS | Higher cost is a recorded difference; cost ratio is not a rate |
| R4.3 A partial frame (named family, unstated reference) is the worst condition observed | B4: C4 0/4 (8 construction-level failures); F1 FALSE; C1-vs-C4 discordance 4–0 (p=0.125) | SUPPORTED-WITH-LIMITS | Descriptive exact statistics; no alpha; mechanism reading (priming hypothesis) is bounded interpretation |
| R4.4 Historical fully-withheld blind run (seeds 7–8, 0/2) corroborates but is not poolable | B3/A9 | SUPPORTED as separate bounded observation | Different seeds and wording; explicitly not pooled |

**RQ4 summary:** the single causal-tier gap identified in the synthesis is now closed **to the mechanism-identification standard it was preregistered under** — not to a rate-estimation standard. This is the only lane in the corpus whose cells were designed to differ in exactly one manipulation of information, and its conclusion is stated in those terms.

## Completion-program questions (user §3.5 and defect register)

| Question | Resolution | Where |
|---|---|---|
| 9,640 vs 20,480 query-figure attribution | **RESOLVED, correct in all documents.** The surrogate arm (model-generated solver) cost 9,640 queries; the prewritten exact control costs 20,480 by construction; the equality between the control figure and EXP-013 is by construction, not duplication | canonical audit; coverage audit C6/C7; synthesis §7 |
| Candidate-identity discrepancy (attempt3 executed bytes vs archived file) | **RESOLVED.** Executed candidate `a5e8ed51…` recovered byte-exactly from the generator transcript; bit-exact replay (9,640 queries, 0 divergence); live grading SUCCESS at 9,619; archived `4fbd70a0…` is a post-run replacement and is not used as executed bytes | `sp2027/analysis/postfreeze_integrity_resolution_20261018/` |
| Integrity-sweep anomalies (69 manifests) | **RESOLVED.** 718 MATCH + 1 dup; 13 anomalies all explained (1 content-level, 12 bookkeeping); 0 missing files | same dossier |
| Freeze-window / escrow wording inconsistencies | **VERIFIED RESOLVED** in both current manuscript builds | completion-program reconciliation pass |

## Manuscript claim status (synthesis §11 decision table, condensed)

| Manuscript material | Evidence status |
|---|---|
| V4 task outcomes + representative revisions | Admissible (V-PRIMARY); exact per-task breakdown |
| Corrected code exploration/replication | Admissible; no causal interface effect claimed |
| H1 V2 (qualified result + XOR counterexample) | Admissible as instrument/contract evidence; 51/60 wording verified in builds |
| Reduced-prompt ChaCha | Descriptive only (family-blinding reading removed) |
| CBC 400 vs 4,096 budgets | Kept distinct; control-qualification framing |
| C2b | Admissible policy contrast (not ML-KEM break) |
| C2-T1 | Negative endpoint contrast; never "completed MITM" |
| D1 + lineage | Context; no new agent attribution implied |
| E5 R30 | Candidate/acquisition case with stated enforcement limits (8,714 calls) |
| E1/E3/E4/E6 | Measurement paper material; independent contribution preserved |
| All-family score plots | Forbidden; no pooled denominator exists anywhere in the record |
| NEW: 2×2 information-frame lane | Admissible as bounded mechanism identification; supplements the information-contract narrative |

**Bottom line:** each of the three adopted RQs has an explicit supported core with stated limits; the two flanking questions (causal information frame; completion-program attributions) are closed at their preregistered standards; and every direction in which the corpus does **not** support a claim (acquisition, feedback causality, timing recomputation, universal generality, immutable model identity, external joins) is recorded above rather than smoothed over.
