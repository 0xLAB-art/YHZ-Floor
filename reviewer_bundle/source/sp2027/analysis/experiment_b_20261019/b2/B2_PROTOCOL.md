# B2 Protocol — Content-Addressed vs Execution-Bound Provenance on Deterministic-Subject Evaluation Evidence

- Artifact: `sp2027/analysis/experiment_b_20261019/b2/B2_PROTOCOL.md` (new, separately versioned; no frozen artifact is modified).
- Date: 2026-10-19. Author epoch: ACTS-Attack / Experiment B2 (follow-on under user critique of Experiment B).
- Status: **FROZEN design, pre-execution.** No outcomes observed at the time of writing. Predictions in §7 are pre-registered claims to be tested by a single preserved pass (see §8).
- Constraints in force: offline; $0 marginal; no network; no model/provider calls; protected files untouched (hashes re-checked before/after pass); no retuning after the preserved pass; strong negative is an acceptable and reportable result; no novelty claims are made in this document.

## 1. Purpose and relation to the mission

Experiment B established, on a frozen corpus (dev 54 + single blind held-out 58 cases):

| system | held-out false promotions (level 6, truth_strong=False) |
|---|---|
| V2 (claim binding, no signatures) | 16 |
| V3-sig (signatures only; no cross-record digest continuity, no joins) | 28 |
| V3-full (signatures + digest continuity + cross-record session joins) | 0 |

Open question this protocol addresses: **what does a complete, content-addressed provenance design actually do on this corpus** — i.e. a verifier that requires signature authenticity, declared-hash consistency, cross-record digest continuity, and record-content assertions, but has **no execution-identity (session) binding** — and **which single bindings are minimally necessary** to close the observed attack families? This is the design-class axis that separates "subject-digest as identity" (in-toto/SLSA-style digest-complete verification; RATS appraisal without freshness enforcement) from "execution/attempt identity binding" (RATS-style freshness nonces; in-toto layout authorization bound to the attempt; our V3-full joins).

Deliverable value either way:
- positive: a measured, reproducible insufficiency of content-addressed-only verification on the deterministic-subject class, with a per-family discrimination matrix and a minimal-binding ablation table;
- negative: the modeled content-addressed design withstands the frozen corpus, and the "digest sufficiency" mechanism claim dies honestly for this corpus.

No novelty claim is made or implied in this document; see §9.

Out of scope: synthetic-to-real reachability (separate B2-2 harness; the ACTS campaigns have no untrusted certificate-ingestion path), live-campaign evidence (B2-4, blocked pending user authorization of provider phase R0/R1), any modification of frozen artifacts, any manuscript/paper integration.

## 2. Question set

- **Q1** (already answered by Experiment B, re-confirmed as reference): do signatures alone (no cross-record digest continuity, no joins) prevent the attack families? Reference: V3-sig false promotions 28/58 held-out.
- **Q2**: does a faithful **content-addressed** verifier (`digest-only`; all checks except execution-identity class) falsely promote any frozen case? Predicted: yes, exactly on the digest-coincidence families (H6b, H10; conditional H4 — see §7).
- **Q3**: does adding execution-identity binding (`digest-session`) close all observed classes while preserving honest partial claims (H0, H7)?
- **Q4**: which single bindings are **minimally necessary** per family (ablation suite; §4.3)?
- **Q5**: how do these compare to the frozen references (V2, V3-sig, V3-full) and to adjudicated truth on the same corpus?

## 3. Systems under comparison

Frozen references (read-only; hashes recorded in the freeze packet; verdicts already preserved in `iar_b/runs/20261019_112227/results.json` and `iar_b_heldout/runs/20261019_114849/results.json`):

- `V2`: `sp2027/analysis/heb1_crossboundary_20261019/build/heb1_v2_claim_binding.py` — claim binding only; no signatures.
- `V3-sig`: `sp2027/analysis/experiment_b_20261019/eb_v3_sig.py` — structural checks, per-record signature authenticity, declared hashes; no cross-record digest continuity, no joins.
- `V3-full`: `sp2027/analysis/experiment_b_20261019/eb_v3_full.py` — V3-sig + digest continuity + rung ladder with session joins (l1–l6).
- `Adjudicator` (truth source): `sp2027/analysis/experiment_b_20261019/eb_adjudicator.py` — generator-side truth; runner also uses it to re-verify fixture integrity per case (`expected_adjudicator` match).

New models to implement (`b2_prov_baselines.py`, this experiment; see caveat below):

- `digest-only` — content-addressed completeness: all D-class checks; **no** S-class checks.
- `digest-session` — D-class + all S-class checks (execution-identity binding).
- Ablations (each = `digest-session` minus exactly one check):
  - `abl-authjoin` — remove S1 (authorship session == cred).
  - `abl-refjoin` — remove S4 (reference session == cred).
  - `abl-tracejoin` — remove S2 (trace session == cred).
  - `abl-executor` — remove D7 (trace.executor == cert.execution.executor).

**Faithful-model caveat (mandatory wording in the report):** the new baselines are *models of design classes*, implemented offline from the public descriptions of in-toto/SLSA-style digest-complete verification and RATS-style freshness binding. They are not the actual products, and no network/pip access is used. The corpus itself is limited: the frozen fixtures use one session key per run for all roles, and evidence records carry no nonce/attempt field, so multi-party (distinct per-role keys) and literal nonce-carrier designs are only representable in the degenerate single-identity form. This limitation must be restated wherever the results are used.

All systems emit the same JSON line contract as V3-sig/V3-full: `{system, decision (ACCEPT|REJECT), supported (int 0..6 or null), requested (int 1..6), reason}`. `supported` for the new baselines is defined as the number of leading satisfied ladder levels (0..6). `ACCEPT` iff `supported >= requested` and no claim above `supported` declares a strong value; otherwise `REJECT`.

## 4. Check specification

### 4.1 Check table (exact)

D-class = content/declared/value checks (no execution-identity semantics). S-class = execution-identity checks.

| id | level | class | check |
|---|---|---|---|
| D1 | L1 | D | bundle parses; required files present; no duplicate evidence kinds; kinds ∈ EVIDENCE_ORDER |
| D2 | L1–L6 | D | each evidence file's bytes hash to the sha256 declared in `certificate.evidence[]` |
| D3 | L1–L6 | D | detached Ed25519 signature of each evidence record verifies under `trust[record.session_id]` (signature authenticity only; any trusted key accepted) |
| D4 | L1 | D | `sha256(candidate.json)` == `certificate.agent_artifact.sha256` |
| D5 | L1 | D | `authorship.artifact_sha256` == `sha_cand` |
| D6 | L2 | D | `trace.candidate_sha256` == `sha_cand` |
| D7 | L2 | D | `trace.executor` == `certificate.execution.executor` |
| D8 | L3 | D | `effect.status` == `OBSERVED` |
| D9 | L4 | D | `reference.accepted` is `True` |
| D10 | L4 | D | `reference.artifact_sha256` == `sha_cand` |
| D11 | L5 | D | `boundary.enforced` is `True` |
| D12 | L6 | D | `metadata.verifier_version` == `certificate.verification.verifier_version` |
| D13 | L6 | D | `sha256(target.json)` == `certificate.target.artifact_sha256` == `request.claimed.target_hashes.artifact_sha256` |
| D14 | L6 | D | `trace.base_instance_id` == `task.base_instance_id` == `claimed.base_instance_id` |
| D15 | L6 | D | `trace.condition_id` == `certificate.condition.id` == `claimed.condition_id` == `effect.condition_id` |
| D16 | L6 | D | `claimed.run_id` == `certificate.execution.session_id` (declared consistency) |
| D17 | L6 | D | `certificate.execution.trace_hash` == `hobj(trace)` (if declared) |
| S1 | L1 | S | `authorship.session_id` == cred (`certificate.execution.session_id`) |
| S2 | L2 | S | `trace.session_id` == cred |
| S3 | L3 | S | `effect.session_id` == cred |
| S4 | L4 | S | `reference.session_id` == cred |
| S5 | L5 | S | `boundary.session_id` == cred |
| S6 | L6 | S | `metadata.session_id` == cred |

`cred` = `certificate.execution.session_id`; `sha_cand` = `sha256(candidate.json)`; lower-level kinds must be present and valid for a level to be reached (same semantics as V3-full's rung ladder).

### 4.2 Compositions

- `digest-only` = {D1..D17}; no S-checks.
- `digest-session` = {D1..D17, S1..S6}.
- Ablations = `digest-session` minus the single check named in §3.

### 4.3 Semantics notes

- D3 admits records from **any** trusted session key: a genuine record produced by a different honest run keeps its signature validity (this is the C1 composer capability from Experiment B).
- The only non-model content choice: D7 (executor equality) is classified D because it compares two declared values (trace field vs certificate field), not an identity/attribution join. Its effect on H4/H9 is measured by `abl-executor`.
- D16/D17 are declared-consistency checks; they do not import evidence-to-cred identity.

## 5. Case sets

- Core: frozen dev set (54 cases) and frozen held-out set (58 cases), exactly as built and preserved by Experiment B:
  - dev: root `sp2027/analysis/experiment_b_20261019/iar_b/` — `cases/dev/`, `labels/dev_labels.json`, `trust/dev_run_keys.json`;
  - held-out: root `sp2027/analysis/experiment_b_20261019/iar_b_heldout/` — `cases/…`, `labels/…`, `trust/…` (freeze-verified; freeze `cc0fde9e…0570`).
- Extension (decided at freeze; either included and pre-registered in the freeze packet, or explicitly deferred): IAR-C independent case set (`iar_c/`, 44 cases) **only if** its bundle layout, labels and trust files are interface-compatible without modification of frozen files. Default: deferred.
- No case files are modified, copied with edits, or regenerated for this experiment. The baselines read `public_dir` + `trust_path` only.

## 6. Metrics and gates

Same metric definitions as `eb_runner.py` (for comparability):

- `false_promotion` (per system, per family): verdict ACCEPT at asserted level 6 for a case whose adjudicated `truth_strong` is False.
- `overclaim`: asserted `supported` > adjudicated `supported`, non-malformed case.
- `false_reject`: adjudicated `supported` >= 1, `requested` <= adjudicated `supported`, and system rejected.
- `agreement`: asserted `supported` == adjudicated `supported`.
- `overhead_ms` (first of two identical runs), determinism (double-run equality).

Gates:

- **B2-G1 (fixture integrity):** adjudicator output matches `expected_adjudicator` for all 112 cases; all malformed cases (H8) rejected by every new baseline.
- **B2-G2 (determinism/well-formedness):** all systems × cases double-run identical; outputs parse; `supported` ∈ 0..6.
- **B2-G3 (honest preservation):** every new baseline accepts H0 at 6 and H7(k) at k; zero false rejects on H0/H7 for `digest-only` and `digest-session`.
- **B2-G4 (discrimination):** observed false-promotion sets are compared to the pre-registered predictions (§7). Any deviation is recorded as a deviation with cause, never retuned.
- **B2-G5 (integrity):** protected file hashes unchanged; no modifications outside `b2/`; freeze packet verified; results hashed.

Decision rule (either-way reporting, no novelty language):

- If `digest-only` shows ≥1 false promotion on digest-coincidence families (H6b/H10 and conditionally H4) while `digest-session` shows 0: report as **measured insufficiency of content-addressed-only verification on deterministic-subject evidence**, with the ablation-derived minimal-binding table.
- If `digest-only` shows 0 false promotions: report as **NO-GO for this mechanism route** — the modeled content-addressed design already withstands the frozen corpus; no insufficiency demonstrated; the mechanism claim is rejected for this corpus.

## 7. Pre-registered predictions (draft; finalized in the freeze packet before the preserved pass)

Prediction integrity rules: predictions below are written from mechanism analysis of the frozen family constructions, before any baseline implementation output has been observed. Amendments before the freeze are allowed only to correct factual field-value errors discovered by reading frozen case files on disk (not by running baselines), and every amendment is logged with timestamp+reason in the freeze packet. After the freeze: no edits.

Predicted false-promotion sets (held-out 58; dev expected analogous):

| system | predicted FP families (level-6 ACCEPT, truth_strong False) |
|---|---|
| `digest-only` | **{H6b, H10}** (4 + 4 cases); conditional **H4** iff X/Y executor strings coincide (to be verified by reading frozen H4 case files at freeze; if they differ, H4 predicted rejected at supported=1 via D7) |
| `digest-session` | ∅ |
| `abl-authjoin` | {H6b} |
| `abl-refjoin` | {H10} |
| `abl-tracejoin` | ∅ (H4 remains caught by D7 executor equality — conditional on executor strings; verify at freeze) |
| `abl-executor` | {H9} |

Predicted rejection paths (supported level where the first failing check sits): H1 → L1 via D5 (X's authorship digest ≠ D); H2 → L6 via D15; H3 → L6 via D14; H4 → L2 via S2 and/or D7; H5/H6a → signature failure (D3) at L2/L1; H9 → L2 via D7; H10 → L4 via S4. H0 → 6; H7(k) → k; H8 → malformed reject.

Mechanistic statement being tested: *content-addressed bindings fail exactly on those families where a foreign authentic record's subject digest coincides with the submitted artifact digest because the artifact bytes are a deterministic function of the public instance (byte-identity channel); execution-identity binding is the discriminating countermeasure.*

## 8. Freeze and execution discipline

1. Write `b2_prov_baselines.py` and `b2_runner.py`.
2. Smoke tests restricted to H0 and H8-a only (interface correctness); no other case outputs may be inspected before the preserved pass.
3. Finalize predictions (H4 conditional resolved by reading frozen H4 case files); emit `b2/freeze/B2_FREEZE.json` = sha256 of both modules, case roots (file inventory hash), labels/trust, predictions, and the frozen reference system hashes.
4. **Single preserved pass**: `b2_runner.py` over dev+held-out (and IAR-C iff pre-registered), all systems, double-run; results to `b2/runs/<timestamp>/results.json` with sha256; raw per-case verdicts for every system + adjudicator preserved in the results file.
5. Re-check protected file hashes; write `B2_BASELINE_COMPARISON_REPORT.md` (either-way outcome; per §6 decision rule; mandatory faithful-model caveat; mandatory "no novelty claim / prior-art pending" statement).
6. No retuning after the pass. Deviations from predictions are reported as deviations.

## 9. Prior-art context (stub for the report)

Established designs whose *dimensions* this measurement quantifies: RATS (RFC 9334) freshness/nonce binding against replayed attestations; in-toto layouts and authorized functionaries; SLSA provenance (builder/invocation identity, subject digests). Adjacent empirical work: TRAP/ReplayBench (arXiv:2610.16333) runtime tool-result misbinding (no evaluation-verdict promotion layer); SimGlot single-harness label audit (no cross-run verdict composition). Honest position: the underlying binding principle is anticipated by RATS/in-toto; this pass quantifies, in one frozen corpus, which verification dimension is necessary and sufficient, and where content-addressed-only verification fails. A focused prior-art check on "digest binding with deterministic subjects / attestation replay" is required before any external novelty wording; none is claimed here.

## 10. Deliverables

- `b2/B2_PROTOCOL.md` (this file).
- `b2/b2_prov_baselines.py`, `b2/b2_runner.py`.
- `b2/freeze/B2_FREEZE.json` (+ prediction record).
- `b2/runs/<timestamp>/results.json` (single preserved pass, hashed).
- `b2/B2_BASELINE_COMPARISON_REPORT.md` (either-way; discrimination matrix + ablation minimal-binding table + limitations).
