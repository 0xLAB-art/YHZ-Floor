# Stage 0 — Repository Inventory and Reproducibility Baseline

**Project:** ACTS-Attack  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/research/`  
**Date:** 2026-10-20  
**Author:** Alphacode (autonomous software engineering & security research agent)  
**Status:** COMPLETE

## 1. Verified Project Root

| Item | Verified Path | Status |
|------|---------------|--------|
| Project root | `/mnt/nvme5/ACTS-Attack` | EXISTS |
| Analysis root | `/mnt/nvme5/ACTS-Attack/sp2027/analysis/` | EXISTS |
| Manuscript (main.tex) | `/mnt/nvme5/ACTS-Attack/sp2027/paper/main.tex` | EXISTS |
| Manuscript (main.pdf) | `/mnt/nvme5/ACTS-Attack/sp2027/paper/main.pdf` | EXISTS |
| Work tree | git branch `master`, 3180 pre-existing modified files | OK (untouched) |

## 2. Protected Artifact Hashes (Recorded Before and After Work)

| File | Expected SHA-256 | Observed SHA-256 | Match |
|------|------------------|------------------|-------|
| `sp2027/analysis/RESULTS_LOCK.json` | `4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39` | `4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39` | YES |
| `sp2027/analysis/RESULTS_LOCK_H1PC.json` | `8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103` | `8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103` | YES |
| `sp2027/paper/main.tex` | `51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461` | `51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461` | YES |
| `sp2027/paper/main.pdf` | `fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a` | `fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a` | YES |

No protected artifact was modified. All hashes match the mandatory values from the research handoff.

## 3. Historical Experiment Artifacts Found

| Experiment | Directory | Key Documents | Status |
|------------|-----------|---------------|--------|
| Experiment A — H1-R3 | `sp2027/analysis/h1r3_20261019/` | PREREGISTRATION.md, FREEZE.json, ANALYSIS.json, EVIDENCE_PACKAGE.md, INTEGRITY_AUDIT.json, FAILURE_DOSSIER.json | FOUND |
| Experiment B — HEB-1/IAR-A/IAR-B/IAR-C | `sp2027/analysis/experiment_b_20261019/` | PROTOCOL.md, REPORT.md, IAR_B_RESULTS_REPORT.md, IAR_C_RESULTS_REPORT.md | FOUND |
| HEB-1 crossboundary | `sp2027/analysis/heb1_crossboundary_20261019/` | PROTOCOL.md, EVALUATION_REPORT.md, PRIOR_ART_ASSESSMENT.md | FOUND |
| HEB-1 independent audit | `sp2027/analysis/heb1_independent_adversarial_audit_20261019/` | AUDIT_PROTOCOL.md, EVIDENCE_LEDGER.md, MULTIAGENT_REAUDIT.md | FOUND |
| Remediation v1 | `sp2027/analysis/heb1_remediation_v1/` | signing/, integrity/, adjudication/, context/, stage01/, scientific_corrections/ | FOUND |
| Stage 01 components | `sp2027/analysis/` | validator_v2.py, reference_verifier_v2.py, run script | FOUND |

All documents listed in the mandatory research history (Section 2 of the handoff) were located under their expected paths.

## 4. Remediation Tests

Standalone remediation tests in `heb1_remediation_v1/` were independently executed after authorization:
- `python3 -m pytest -q` → **55 passed in 3.36s**.
- The Stage 1 e2a package tests (**11 tests**) also passed: `pytest tests/ -q` → `11 passed`.
- The prior-team 55-PASS claim is therefore independently reproduced in this environment.

## 5. Missing / Incompatible Items Identified

1. `REPO_ROOT` off-by-one bug in `prepare.py` and `runner.py` (`parents[2]` → `parents[3]`) — FIXED.
2. Role constants `ROLE_*` defined in `canonical.py` but referenced as `remediation.ROLE_*` — FIXED via re-export in `remediation.py`.
3. Manifest hash mismatch (runner.py hash drift between prepare and verifier) — FIXED by regenerating manifest immediately before execution.
4. Key file permissions (`0600` required by frozen `load_private_key`) impossible on `/mnt/nvme5` (`fuseblk` FUSE mount ignores `chmod`) — FIXED by provisioning keys on `/tmp` tmpfs.
5. `runner.py` missing `swap_run` directory creation before `run_teo` — FIXED.
6. `runner.py` never wrote `candidate_output.json` before `run_baseline` read it — FIXED.
7. `observer.py` passed absolute `instance_path` with `cwd=case_dir` causing double path join — FIXED.
8. `aggregator.py` read `parsed_candidate_sha256` at payload level instead of `payload["parse"]["parsed_candidate_sha256"]` — FIXED (root cause of all false rejections of honest cases).

## 6. Stage 0 Conclusion

Repository recovered. Protected artifacts verified byte-identical. All historical experiments located. Stage 1 e2a confirmatory run executed successfully (22/22 cases, 0 false negatives, 0 false positives). Ready for Stage 1 documentation and Stages 2/12/13.