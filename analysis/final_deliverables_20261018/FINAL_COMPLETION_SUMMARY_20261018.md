# Final Completion Summary — 2026-10-18

**Program:** ACTS-Attack completion program (post-freeze)
**Role:** completion summary for the six mandated deliverables
**Status:** original experimental program complete; all in-scope defects resolved; the one genuinely missing experiment executed, frozen, and analyzed
**Protected artifacts:** verified intact (Section 7)
**Marginal cost:** $0.00 (free route only; Section 7)

---

## 1. What was delivered

This summary closes the completion program. The six mandated deliverables are:

| # | Deliverable | Path | Status |
|---|-------------|------|--------|
| 1 | Complete experiment coverage audit | `sp2027/analysis/COMPLETE_EXPERIMENT_COVERAGE_AUDIT_20261018.md` + `sp2027/analysis/complete_experiment_coverage_audit_20261018.json` | DONE (G6 row updated to COMPLETED) |
| 2 | Corrected evidence package | `sp2027/analysis/final_deliverables_20261018/EVIDENCE_PACKAGE_20261018.md` | DONE |
| 3 | Scientific results report | `sp2027/analysis/final_deliverables_20261018/SCIENTIFIC_RESULTS_REPORT_20261018.md` | DONE |
| 4 | RQ to evidence map | `sp2027/analysis/final_deliverables_20261018/RQ_EVIDENCE_MAP_20261018.md` | DONE |
| 5 | Reproducibility package | `sp2027/analysis/final_deliverables_20261018/REPRODUCIBILITY_PACKAGE_20261018.md` | DONE |
| 6 | Final completion summary | this file | DONE |

Supporting artifacts created or completed during this program:

- New executed experiment: `sp2027/research_execution/info_contract_2x2_20261018/` (preregistered matched 2x2 intervention; section 3), with `REPORT.md`, `ANALYSIS.json`, `FINAL_FREEZE.json`, `hashes/all_artifacts.sha256`.
- Post-freeze integrity resolution dossier: `sp2027/analysis/postfreeze_integrity_resolution_20261018/` (candidate-identity defect; section 2).
- Canonical-population reference: `sp2027/analysis/CANONICAL_RUN_AUDIT_20261018.md`.
- Deliverables hash manifest: `sp2027/analysis/final_deliverables_20261018/DELIVERABLES_MANIFEST.json` (hashes the seven deliverable files listed above; self-excluded).

All six deliverables are new artifacts. No manuscript file was edited; no protected file was modified; no commits were made (the repository retains its pre-existing large uncommitted working tree).

## 2. What was wrong, and what was corrected

The completion program audited the full corpus (69 manifests, ~733 hash entries; 12 capability sessions; 90 H1 V2 responses; post-freeze novelty-program root trees) and found limited, clearly bounded defects. Each was investigated to root cause and corrected or documented; none was relabeled or hidden.

1. **Candidate-identity defect (surrogate attempt 3) — the only content-level defect on an executed artifact.** The executed agent's bytes (`a5e8ed51...`) diverged from the archived candidate file (`4fbd70a0...`, 248 lines, replacement mtime 08:20:57, after the 08:20:30 snapshot). The executed candidate was recovered verbatim from the execution transcript by hash match, bit-exact replay confirmed all 9,640 queries and the claim-object hash `919ca521...`, and live grading of the reconstructed candidate reproduces SUCCESS (9,619 oracle queries). Resolution documented in the dossier; canonical file is `evidence/executed_candidate_reconstructed.py`. Archived files were not edited.

2. **9,640 vs 20,480 query-figure attribution.** Confirmed correct in all documents: the 9,640-query arm is the model-generated solver; the 20,480-query exact control is prewritten by construction. The equality with the historical EXP-013 figure is by construction, not duplication. No document changes needed; attribution now explicit in every deliverable.

3. **XOR scorer wording.** A previously reported "XOR capability" result traces to a scorer artifact, not to capability; corrected to a control-grade statement (10/10 correct-mask rejection; 10/10 protected-plaintext acceptance; retrospective recovery 0/20).

4. **H1 V2 denominators.** "51/60" and "0/35" recomputed and stated with their true denominators (90 responses, 81 parser-valid; abstentions counted separately at 30/30). One retry-1 trace had a REFUSAL label defect; retained as recorded with a note.

5. **Blind-opportunity arm.** Superseded to descriptive-only status; its 0/2 blind seeds (7-8) are reported separately and never pooled with the 2x2 cells.

6. **Held-out arm admissibility.** Re-scoped to attempt-4-only (4/4, leak audit 50 files, 0 hits); other attempts retained as failures, not averaged.

7. **"18/18" phrasing.** Is 18 successes across 6 runs per family, not a rate; never to be read as an estimate of per-attempt probability.

8. **V4 aggregation units.** 12 capability sessions (31 nested programs), not 31 independent programs; 4 oracle failures retained; Wilson interval [39.1, 86.2]% computed at the session level.

9. **E5 phrasing.** Records candidate-versus-commitment behavior on host-executed, unauthenticated handlers (1/14 graded; R30 commitment match; 8,714 calls); it does not demonstrate enforced acquisition, and is not reported as such.

10. **Freeze-window / escrow wording.** Verified resolved in both current manuscript builds; no residual inconsistency.

Integrity sweep v2 (69 manifests, ~733 entries): global classes were MATCH 718 + 1 duplicate, SELF_STALE 3, MISMATCH 4, MISSING 6, EMPTY_AT_SNAPSHOT 1. All 13 flagged anomalies reduce to snapshot convention, ordering, or the single attempt-3 defect above; zero genuinely missing files. Attempt-4 secret-hash differences and manifest ordering (`ba52ba8c...` to `1f1f811a...`) were resolved as value-hash-strip convention and benign finalizer ordering, respectively.

## 3. What was genuinely missing, and was executed

The coverage audit found exactly one evaluable gap in the causal tier: no matched intervention that changes only the *information frame* while preserving observations, target, seeds, budget, solver interface, provider route, and success predicate (audit gap G6; synthesis Section 12 "indispensable" list).

This program ran that intervention: `P010-INFO-CONTRACT-2X2-CHACHA20-v1`, a preregistered 2x2 crossing naming (the gap is named / unnamed) with reference disclosure (the reference plaintext is disclosed / withheld), on the ChaCha20 feedback lane, seeds 41-44, one provider session per cell.

Results (all recorded in `info_contract_2x2_20261018/`):

- 16 sessions, 22 provider responses, 0 provider failures.
- Cells: C1 (named + disclosed, i.e. the historical default frame byte-for-byte) 4/4; C2 (fully blind) 4/4 (6 submissions; two recoveries only after feedback); C3 (named + no disclosure statement) 4/4; C4 (named + "a 64-byte reference is used", content unstated) 0/4 (8 submissions).
- Marginals: reference-disclosure effect (C1+C3 vs C2+C4) 8/8 vs 4/8; Fisher exact one-sided p = 0.03846, two-sided 0.07692 (descriptive); naming effect 1.0 (no signal at n=4 per cell).
- Discordance C1>C4 was 4-0 (two-sided binomial 0.125).
- Falsifiers: F1 (C4 at least as good as C1) false; F2 (naming drives outcomes) false; F3 (explicit all-zero sentence necessary) triggered under the derive-it frame.
- Mechanism is code-grounded: C4 failures are construction-level (reference-content guesses; turn-2 algebra printing `c1`-derived values) plus one parse error; a single near-correct turn-2 recovery (seed 43) is flagged as an interpretation, not proof.
- Leak scan: 149 files, 0 prompt hits; 12 stdout hits are accepted candidates' own output (benign).
- Final freeze: manifest `hashes/all_artifacts.sha256` covers 152 entries, sha256 `7c9cf717769674c73462e0caedd41e25bfa8351551da5985ca03dfc81350dc76`, `sha256sum -c` 152/152 OK; `FINAL_FREEZE.json` records protocol, execution summary, integrity block, identity limits, and reproduction commands. The earlier 150-entry snapshot (`68945c20...`, referenced in `STATUS_INFO_CONTRACT.json` as `files_hashed=150`) is documented as superseded.

Bounded conclusion carried into the deliverables: withholding a reference and framing an asymmetry are different interventions; under this frame the explicit disclosure sentence was necessary for first-turn success in the affected cell, but the frame (deriving the reference from the task) can substitute for the explicit sentence - the 2x2 supports a mechanism-identification reading, not a universal rate.

## 4. How the evidence changes

Before this program: the corpus supported descriptive information-contrast results and capability evidence, with the causal-tier question open and several provenance defects unresolved.

After this program:

- The causal-tier gap (G6) is closed at the mechanism-identification standard: one preregistered, matched, frozen intervention isolates the information-frame variable with recorded falsifiers.
- All provenance questions raised by the audit are resolved (candidate identity; 9,640/20,480 attribution; sweep anomalies; freeze/escrow wording). The corpus hash record is internally consistent (zero genuinely missing files; the single executed-artifact defect resolved by reconstruction plus replay plus live grading).
- The RQ-to-evidence map (deliverable 4) now resolves RQ1-RQ4 separately: RQ1 has a supported-with-limits causal cell (R1.4); RQ2 excludes feedback causality (gap G7 remains, and is not claimed); RQ3 retains the acquisition claim only in weakened candidate-correctness form and the timing claim as unsupported; RQ4 is bounded to the ChaCha20 feedback lane with n=4 per cell.
- Net effect: the evidence base is now eligible for *bounded* manuscript finalization per the synthesis stopping rule. It is not submission-ready on strength of this program alone (Section 5).

No negative result was suppressed: failed runs, oracle failures (5 total in the 2x2 accounting; 4 in V4), parse failures, the superseded manifest snapshot, and the attempt-3 defect are all retained in the record.

## 5. Remaining uncertainty and limitations

Blocked externally (documented, not repaired):
- G1 WebSP semantic join and G2 Cybench semantic join: source materials unavailable; both recorded as M-BLOCKED.
- G3 hosted-model weight identity: provider-attested label only (`claude-sonnet-4-6-free`); no independent weight verification possible.

Missing, documented, not claimed:
- G4 V4 raw timing recomputability: 0/8 endpoint pairs recomputable; timing numbers are raw-recorded only.
- G5 E5 enforced-acquisition isolation: a different design would be needed; current records show candidate-vs-commitment behavior only.
- G7 no-feedback baseline: optional; no causal feedback claim is made without it.
- G8 human annotation of traces: not collected.

Statistical and design limits:
- 2x2 cells are n=4; per-cell intervals are wide (e.g. 4/4 approximates [0.398, 1]); no alpha was preregistered for this lane; Fisher values are descriptive.
- Single experimenter, single provider route, single environment (Python 3.12.3, stdlib only); no cross-family generalization is claimed from the 2x2.
- One near-correct C4 turn-2 recovery is reported as interpretation, not proof.
- Historical cohorts are not pooled with the new lane (no relabeling, no pooling of incomparable cohorts).

## 6. Verification checklist

A verifier can reproduce every claim in the deliverables:

1. Check the four protected hashes (Section 7) - all must match exactly.
2. `cd sp2027/research_execution/info_contract_2x2_20261018 && sha256sum -c hashes/all_artifacts.sha256` - expect 152/152 OK.
3. Compare manifest sha256 against `7c9cf717...` (recorded in `FINAL_FREEZE.json`).
4. Replay the surrogate candidate: dossier `evidence/executed_candidate_reconstructed.py` + `replay_results.json` (9,640 queries, 0 divergences; live grading SUCCESS).
5. Re-run the post-freeze sweep script referenced in deliverable 5, Section 1 - expect the documented class counts.
6. Optionally re-execute the 2x2 pipeline (deliverable 5, Section 3.1; note the fixed output directory - copy before rerun). Seeds 41-44, one session per cell; expect 16 sessions, 22 responses; outcomes as tabulated.
7. The coverage audit JSON parses and its G6 row reads COMPLETED; the completion mapping (a)-(h) is fully resolved.
8. Deliverable integrity: run the `sha256sum_lines` from `final_deliverables_20261018/DELIVERABLES_MANIFEST.json` (from `sp2027/analysis/`) - expect 7/7 OK.

## 7. Protected artifacts, budget, and compliance

Protected files verified intact at completion (full sha256):

- `sp2027/analysis/RESULTS_LOCK.json` - `4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39`
- `sp2027/analysis/RESULTS_LOCK_H1PC.json` - `8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103`
- `sp2027/paper/main.tex` - `51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461`
- `sp2027/paper/main.pdf` - `fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a`

Compliance:
- Authorized route only: free `claude-sonnet-4-6-free` via `https://api.apmix.ai`; API key never logged; no paid fallback was used.
- Marginal cost of the new experiment and this program: $0.00 (historical logged estimate remains $0.357648; the $50 alert and $200 hard stop were never approached).
- No manuscript edits; no commits; new findings live only in separately versioned artifacts; failures retained.

## 8. Closing statement

The original experimental program is complete. The audit found the corpus sound apart from one executed-artifact identity defect and several documentation-level issues; all are resolved and recorded. The single genuinely missing experiment (the matched information-contract 2x2) was executed on the authorized route, frozen, and analyzed with preregistered falsifiers; it closes the last causal-tier gap at the mechanism-identification standard. The evidence now supports bounded manuscript finalization: claims are separated into supported, supported-with-limits, weakened, and unsupported in deliverable 4, and every number is re-derivable through deliverable 5. The remaining uncertainty is enumerated above: it is external, documented, and not misrepresented as resolved.
