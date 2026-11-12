# Master Progress Report

**Project:** ACTS-Attack  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/`  
**Date:** 2026-10-20  
**Scope:** Chronological record of work completed under this research phase (full EXP 100%)

---

## 1. Phase Overview

Research deliverables live in a separately versioned directory:
`sp2027/analysis/acts_next_phase_20261019_v2/research/deliverables/`

Four protected artifacts remain byte-identical (verified against expected hashes):
- Stage 1 e2a experiment files (`stage1_e2a/e2a/*`) edited only as needed; frozen `heb1_remediation_v1/` kept byte-identical.

Keys were generated on `/tmp` tmpfs due to fuseblk chmod being a no-op (files stuck at 0777; `load_private_key` requires 0600). `prepare.py` returns the effective `keys_dir`.

No model/provider calls were made without authorization. Network access and isolated installs were used only after the user explicitly authorized installation and continuation of the remaining work.

---

## 2. Work Completed (Chronological)

### 2.1 Stage 1 e2a Confirmatory Run (completed prior to this phase)

- Repaired Stage 1 e2a harness:
  - `e2a/remediation.py`: exported role constants from canonical.py; added `manifest_verifier()` using `_load`
  - `e2a/prepare.py`: fixed REPO_ROOT off-by-one (`parents[2]`→`parents[3]`); keys redirected to /tmp tmpfs; keys_dir returned in output
  - `e2a/runner.py`: fixed REPO_ROOT; added `swap_run` mkdir; added `candidate_output.json` copy from observer stdout before run_baseline
  - `e2a/observer.py`: fixed instance path to basename (cwd=case_dir not honored)
  - `e2a/aggregator.py`: fixed `parsed_candidate_sha256` read from `payload["parse"]` instead of payload level — root cause of false rejections on honest cases
- Preflight fail-closed verification: 38 files checked, 0 errors
- Confirmatory run executed: 22 cases, 6 ATTRIBUTED_SUCCESS, 12 REJECT, 4 INCONCLUSIVE, **0 false negatives, 0 false positives**
- Protected artifact hashes all match expected

### 2.2 Stage 0 — Repository Foundation (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| Repository inventory | `STAGE0_REPOSITORY_INVENTORY.md` | COMPLETE |
| Evidence ledger | `STAGE0_EVIDENCE_LEDGER.json` | COMPLETE |
| Reproduction report | `STAGE0_REPRODUCTION_REPORT.md` | COMPLETE |
| Resource gaps | `STAGE0_RESOURCE_GAPS.md` | COMPLETE |

### 2.3 Stage 1 Documentation (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| End-to-End Attribution Results | `END_TO_END_ATTRIBUTION_RESULTS.md` | COMPLETE |
| End-to-End Attribution Protocol | `END_TO_END_ATTRIBUTION_PROTOCOL.md` | COMPLETE |

### 2.4 Stage 2 — Real Provenance Baseline Comparison (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| In-toto/SLSA/Cosign baseline comparison | `REAL_PROVENANCE_BASELINE_COMPARISON.md` | COMPLETE — 22 cases; Cosign 128/128 authentic pass and 128/128 tamper rejection; native format gap documented |

### 2.5 Stage 3 — Boundary Test Across a Network Ingress (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| Boundary results | `STAGE3_BOUNDARY_RESULTS.md` | COMPLETE — 12 submissions over a loopback ingress; 1 positive control attributed, 11 non-control submissions refused, 0 unauthorized attributions |

### 2.6 Stage 4 — AI-Agent Matched Arm vs Scripted Arm (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| Matched-arm comparison | `STAGE4_AI_AGENT_COMPARISON.md` | COMPLETE — 14 provider calls per run, 22 cases, 18/22 decision agreement vs scripted, **22/22 agreement across two replicated runs**, 4 disagreements all explained; one contract gap (exit-status semantic) open |

### 2.7 Stage 12 — Novelty Prior-Art Matrix (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| Novelty / prior art matrix | `NOVELTY_PRIOR_ART_MATRIX.md` | COMPLETE |

### 2.8 Stage 13 — Scientific Validity Audit (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| Scientific validity audit | `SCIENTIFIC_VALIDITY_AUDIT.md` | COMPLETE |

### 2.9 HEB-2 — Contract V2 and Mechanized Soundness (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| Contract V2 results | `HEB2_CONTRACT_V2_RESULTS.md` | COMPLETE — two preregistered semantics, frozen and fail-closed; 11,256 mutation evaluations, 0 soundness violations |

### 2.10 Stage 5 — Live Campaign (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| Live campaign results | `STAGE5_LIVE_CAMPAIGN_RESULTS.md` | COMPLETE — the project's own containerised target exploited over a live network interface and attributed by the frozen contract; the model agent did not complete the exploit within the card's caps and was refused |

### 2.11 Stage 6 — Matched Translation (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| Matched translation results | `STAGE6_MATCHED_TRANSLATION_RESULTS.md` | COMPLETE (corrected after review) — a minimally configured in-toto promotes 16/16; in-toto **with its own rules and an independent inspection** reproduces the ACTS contract exactly (22/22 stateful); SLSA is NOT_COMPARABLE (stops at provenance acquisition) |

### 2.12 Mechanism Specification (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| Mechanism and prior-art delta | `MECHANISM_SPECIFICATION.md` | COMPLETE — minimal statement, checkable property, and the bounded novelty claim |

### 2.13 Cross-Cutting Deliverables (this phase)

| Deliverable | File | Status |
|-------------|------|--------|
| Repository and trust boundary map | `REPOSITORY_AND_TRUST_BOUNDARY_MAP.md` | COMPLETE |
| Resource and permission requests | `RESOURCE_AND_PERMISSION_REQUESTS.md` | COMPLETE |
| Final four objective determination | `FINAL_FOUR_OBJECTIVE_DETERMINATION.md` | COMPLETE |
| Master progress report | `MASTER_PROGRESS_REPORT.md` | COMPLETE (this file) |
| Manifest SHA-256 | `MANIFEST.sha256` | COMPLETE (see §4) |

---

## 3. Resource / Authorization Status

The following resource statuses apply (detailed in `STAGE0_RESOURCE_GAPS.md` and `RESOURCE_AND_PERMISSION_REQUESTS.md`):

| # | Resource | Status |
|---|----------|--------|
| 1 | heb1_remediation_v1 test suite re-run | **COMPLETED: 55 passed in 3.36s** |
| 2 | in-toto / SLSA Verifier / Sigstore-Cosign installation and Stage 2 run | **AUTHORIZED AND COMPLETED** |
| 3 | Stage 4 model route (`claude-sonnet-4-6-free` via https://api.apmix.ai) | **AUTHORIZED AND COMPLETED — 14-call matched arm, Stage 3 fixtures, and the Stage 5 live campaign; exact route, no fallback** |
| 4 | Authorized reachable ingress for Stage 3 | **RESOLVED — controlled loopback ingress constructed and exercised** |

No money spent, no services deployed, no external targets attacked, no provider restrictions bypassed. All provider calls used the single approved free route; total model calls across Stages 3 and 4: 42, all HTTP 200 on `claude-sonnet-4-6-free`, with no retry and no fallback.

---

## 4. Manifest

Generated `MANIFEST.sha256` covering all files in `research/deliverables/`. Hashes computed with `sha256sum`. See `MANIFEST.sha256` for the full listing.

---

## 5. Conclusion

All executable and authorized deliverables are complete. The four Stage 1 preregistered objectives (H1–H4) are supported and H0 is refuted on the 22-case inventory. Stage 2 executed a bounded comparison against Cosign, in-toto and SLSA Verifier. Stage 3 constructed a controlled loopback ingress and exercised the frozen contract across it with zero unauthorized attributions. Stage 4 ran an exact matched arm with model-authored producers — replicated at 22/22 decision agreement across two independent runs — with every disagreement mechanically explained and no attribution lacking an adjudicated positive predicate. The preregistered large representation effect was not met, so the strong novelty claim is rejected. No externally reachable gateway exists in this project.

**Stage 6 was corrected after methodological review and the superiority claim was withdrawn:** the earlier figures (16/16 in-toto, 6/6 SLSA) were a minimally-configured measurement and a trust-setup failure. Given its own artifact rules and an independent inspection, in-toto reproduces the contract's decisions exactly, so the supported finding is a division of labour — the frameworks supply the machinery, the adopter must supply the policy.

**One contract gap is open and is reported, not absorbed:** the preregistration does not state whether attribution requires a successful execution, and the frozen check order contains no execution-status check. Under the strict reading the model arm carries one false positive per run (`H_FAIL_CH_01`); under the output-based reading it is correct. The frozen component was not modified in place. A separately frozen contract amendment with an execution-status precondition, followed by a re-run of the inventory, is proposed as future preregistered work.

**Disclosure:** Stages 3 and 4 were **not preregistered**. They are developed-then-confirmed: a no-provider-call stub-arm fidelity check preceded each reported run, all earlier attempts are retained with their provider ledgers, and the reported numbers come only from the final run. Stage 1 alone was preregistered and hash-frozen (54 seconds before its run). **HEB-2, Stage 5 and Stage 6 were preregistered and hash-frozen** with fail-closed preflights.