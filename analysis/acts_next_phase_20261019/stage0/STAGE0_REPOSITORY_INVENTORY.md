# Stage 0 — Repository Inventory and Current-State Assessment

**Repository:** `/mnt/nvme5/ACTS-Attack`
**Git branch:** `master` · **HEAD:** `4743d18` — *"preregister contract-sound exploitation novelty study"*
**Stage 0 executed:** 2026-10-19 → 2026-10-20 (local, offline)
**Working tree for all new work:** `sp2027/analysis/acts_next_phase_20261019/` (newly created; it did not exist before this phase)

> This is a continuation of an existing research programme, not a new project. Everything below records the state that was *found*, not a reconstruction from reports.

---

## 1. Protected artefacts — hash verification

All four read-only artefacts were hashed **before** and **after** the work. All four match the expected SHA-256 exactly. No protected artefact was modified, reset, cleaned, amended, or committed.

| Artefact | Expected SHA-256 | Observed (pre-work) | Observed (post-work) | Status |
|---|---|---|---|---|
| `sp2027/analysis/RESULTS_LOCK.json` | `4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39` | identical | identical | **UNCHANGED** |
| `sp2027/analysis/RESULTS_LOCK_H1PC.json` | `8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103` | identical | identical | **UNCHANGED** |
| `sp2027/paper/main.tex` | `51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461` | identical | identical | **UNCHANGED** |
| `sp2027/paper/main.pdf` | `fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a` | identical | identical | **UNCHANGED** |

Verification command (reproducible):

```
cd /mnt/nvme5/ACTS-Attack
sha256sum sp2027/analysis/RESULTS_LOCK.json sp2027/analysis/RESULTS_LOCK_H1PC.json \
          sp2027/paper/main.tex sp2027/paper/main.pdf
```

## 2. Pre-existing working-tree state (NOT ours)

`git status --porcelain` showed a dirty tree **before** this phase began. It consists of a modified `.gitignore`, a modified `ACTS-ATTACK` entry, and a large set of `D` (deleted) paths under `DEPOSIT_V1.1_STAGING/**`. These are pre-existing user work. **They were deliberately not reset, cleaned, restored, or committed.** No git write operation of any kind was performed during this phase.

## 3. Mandatory historical documents — all located, none missing

Every document named in the task brief was resolved. All 28 exist at the stated paths. Two documents are recorded at the *component* level rather than as standalone reports, and both are noted below.

### 3.1 Experiment A — H1-R3 (852 model sessions)

| Document | Path | Status |
|---|---|---|
| Preregistration | `sp2027/analysis/h1r3_20261019/H1R3_PREREGISTRATION.md` | present |
| Freeze | `sp2027/analysis/h1r3_20261019/H1R3_FREEZE.json` | present |
| Freeze amendment 01 | `sp2027/analysis/h1r3_20261019/H1R3_FREEZE_AMENDMENT_01.json` | present |
| Freeze amendment 02 | `sp2027/analysis/h1r3_20261019/H1R3_FREEZE_AMENDMENT_02.json` | present (additional) |
| Analysis (JSON) | `sp2027/analysis/h1r3_20261019/H1R3_ANALYSIS.json` | present |
| Analysis (MD) | `sp2027/analysis/h1r3_20261019/H1R3_ANALYSIS.md` | present |
| Evidence package | `sp2027/analysis/h1r3_20261019/H1R3_EVIDENCE_PACKAGE_20261019.md` | present |
| Integrity audit | `sp2027/analysis/h1r3_20261019/H1R3_INTEGRITY_AUDIT.json` | present |
| Failure dossier | `sp2027/analysis/h1r3_20261019/H1R3_FAILURE_DOSSIER.json` | present |
| Raw confirmatory results | `sp2027/analysis/h1r3_20261019/runs/confirmatory/results.jsonl` | present (852 lines) |

Additional H1-R3 documents found in the same directory: `H1R3_POWER_ANALYSIS.json`, `REPAIR_MISSION_PLAN.json`, `H1R3_CAPABILITY_MERGE_INTEGRATION_REPORT.md`, `H1R3_PAPER_INTEGRATION_REPORT.md`, `H1R3_AMENDMENT_01.md`, `EVIDENCE_PACKAGE_APMIX_README.md`.

### 3.2 Experiment B — HEB-1 / IAR-A / IAR-B / IAR-C

| Document | Path | Status |
|---|---|---|
| Novelty proposal | `sp2027/analysis/EVALUATOR_BOUNDARY_NOVELTY_PROPOSAL.md` | present |
| HEB-1 protocol | `sp2027/analysis/heb1_crossboundary_20261019/HEB1_EXPERIMENT_PROTOCOL_20261019.md` | present |
| HEB-1 report | `sp2027/analysis/heb1_crossboundary_20261019/HEB1_EVALUATION_REPORT.md` | present |
| HEB-1 held-out results | `sp2027/analysis/heb1_crossboundary_20261019/heldout/heldout_results.json` | present |
| IAR-A verifier | `sp2027/analysis/heb1_crossboundary_20261019/iar/verify_iar_a.py` | present |
| Experiment-B protocol | `sp2027/analysis/experiment_b_20261019/EXPERIMENT_B_PROTOCOL.md` | present |
| Experiment-B report | `sp2027/analysis/experiment_b_20261019/EXPERIMENT_B_REPORT.md` | present |
| IAR-B report | `sp2027/analysis/experiment_b_20261019/IAR_B_RESULTS_REPORT.md` | present |
| IAR-C report | `sp2027/analysis/experiment_b_20261019/iar_c/IAR_C_RESULTS_REPORT.md` | present |
| IAR-C raw results | `sp2027/analysis/experiment_b_20261019/iar_c/runs/20261019_121621/results.json` | present |
| B2-2 Stage01 report | `sp2027/analysis/experiment_b_20261019/b2_2_stage01/B2_2_STAGE01_REPORT.md` | present |

**Component-level note.** The B2-2 "frozen Stage01 components" are not a report but two executable modules, both present and both hash-pinned in this phase:

* `sp2027/analysis/contract_sound_stage01_validator_v2.py` — SHA-256 `f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a`
* `sp2027/analysis/contract_sound_stage01_reference_verifier_v2.py` — SHA-256 `15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b`

The first digest is independently corroborated: it is the value the remediation wrapper `heb1_remediation_v1/stage01/external_binding_wrapper.py` pins as `FROZEN_VALIDATOR_SHA256` (line 21) and re-checks at line 154. The wrapper's pin is therefore **correct**. The second digest was not previously pinned anywhere in the tree and is newly recorded here.

### 3.3 Independent audit lineage

| Document | Path | Status |
|---|---|---|
| Audit protocol | `sp2027/analysis/heb1_independent_adversarial_audit_20261019/AUDIT_PROTOCOL.md` | present |
| Evidence ledger | `sp2027/analysis/heb1_independent_adversarial_audit_20261019/EVIDENCE_LEDGER.md` | present |
| Independent audit | `sp2027/analysis/heb1_independent_adversarial_audit_20261019/HEB1_INDEPENDENT_ADVERSARIAL_AUDIT.md` | present |
| Six-agent re-audit | `sp2027/analysis/heb1_independent_adversarial_audit_20261019/HEB1_MULTIAGENT_REAUDIT_20261019.md` | present |

### 3.4 Remediation v1

`sp2027/analysis/heb1_remediation_v1/` — 41 files. Substantive components:

```
signing/protected_signing.py           (8037 B)   protected Ed25519 issuance
signing/README.md
context/context_validator.py           (7036 B)   signed context + replay ledger + path confinement
context/README.md
integrity/manifest_verifier.py         (8490 B)   fail-closed preflight
integrity/README.md
adjudication/audit_recompute.py       (13910 B)   metric recomputation
adjudication/AUDIT_NOTES.md                       adjudicator methodology
stage01/external_binding_wrapper.py    (7855 B)   wrapper around the frozen Stage01 validator
stage01/README.md
scientific_corrections/HISTORICAL_CORRECTION_LEDGER.md   (10513 B)
```

Test files: `signing/test_protected_signing.py`, `context/test_context_validator.py`, `integrity/test_manifest_verifier.py`, `stage01/test_external_binding_wrapper.py`, `adjudication/test_audit_recompute.py`.

---

## 4. Environment as found

| Component | Version / state |
|---|---|
| Python | 3.12.3 (`/usr/bin/python3`) |
| pytest | 9.1.1 |
| `cryptography` | 50.0.2 |
| `jsonschema` | 4.10.3 |
| `PyNaCl` | 1.6.2 |
| `pycryptodome` | 3.23.0 |
| `secp256k1`, `ecdsa` | **not installed** (not required — the frozen Stage01 reference verifier implements secp256k1 itself) |
| `in-toto` | **not installed** |
| `slsa-verifier` | **not installed** |
| `cosign` | **not installed** |
| `latexmk` | **not installed** (`pdflatex` and `pandoc` are present) |
| `git`, `jq`, `sha256sum`, `pandoc`, `pdflatex` | present |
| Filesystem of the repository | `fuseblk` — reports mode `0777` for every file and **ignores `chmod`** (see Stage 0 gap G-2) |
| Available model route | `openrouter/minimax/minimax-m3.1-flash:free` (the `gpt-5.6-luna` model named in the brief does **not** exist in the provider catalogue; `openai/gpt-6-luna` and `openai/gpt-5.4-nano` are rejected by the provider for insufficient credit) |

---

## 5. Independent Stage 0 sub-reports produced in this phase

| Report | Path | Contents |
|---|---|---|
| AGENT1 — trust-boundary map | `stage0/AGENT1_TRUST_BOUNDARY_MAP.md` | 641 lines. Execution/stdout capture site, certificate construction, validator invocation, downstream claim consumers, repository-wide ingress/egress sweep, trusted-execution-observer audit, candidate/execution join location. |
| AGENT2 — HEB-1/B2-2 forensic extraction | `stage0/AGENT2_HISTORY_FORENSIC_EXTRACTION.md` | 63 KB. Independent recomputation of every published HEB-1 / IAR-C / B2 / IAR-A figure plus 6 denominator/scope discrepancies (D1–D6). |
| AGENT4B — H1-R3 forensic extraction | `stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md` | 78 KB. Recomputation from the raw 852-line `results.jsonl`, arm counts, L3/L2 contrasts, failure taxonomy, freeze-contract coverage, and 6 material defects. |
| AGENT5 — prior-art / novelty matrix | `stage0/AGENT5_PRIOR_ART_NOVELTY_MATRIX.md` | 69 KB. Mechanism-level matrix over RATS, in-toto, SLSA, TUF, Sigstore and the AI-agent evaluation literature; category A–E assessment. |
| AGENT5B — prior-art verification | `stage0/AGENT5B_PRIOR_ART_VERIFICATION.md` | 96 KB, 1,199 lines. Independent full-text verification of every Agent-5 citation, with VERIFIED / REFUTED / NOT-OBTAINABLE per claim. |
| AGENT3 — provenance comparator analysis | `stage2_provenance/AGENT3_PROVENANCE_COMPARATOR_ANALYSIS.md` | 84 KB, 653 lines, 40 cited URLs. Guarantees, install requirements, and comparability of in-toto 3.1.0 / slsa-verifier 2.7.1 / cosign 3.1.3 / RFC 9334. |

---

## 6. Concurrent sibling tree (not ours)

A second, independent Stage 1 implementation exists at `sp2027/analysis/acts_next_phase_20261019_v2/stage1_e2a/` (created 2026-10-19 23:55 by a concurrent session). It contains a 607-line preregistration, a 159-line deviations log, ~2,900 lines of `e2a/*.py` components, and a 137-line test suite — but **no freeze manifest, no case inventory, no trust material, and no run output**. It is authored but not frozen and not executed.

That tree was **not modified, executed, or imported by this phase.** It is treated here as an *independent pre-execution commitment* whose predictions are checked against this phase's confirmatory results (§7), and as a cross-session reproducibility observation. Its `e2a` components use a `memfd`-based observer (program bytes executed from an anonymous in-memory file), which removes the write-then-hash-then-execute TOCTOU window that this phase's observer leaves open (see Stage 1 threat T-2).

---

## 7. Current-state assessment (written before any new experimental intervention)

1. **The historical programme is real and internally documented, but several of its published aggregates are scope-ambiguous.** Independent recomputation reproduces the headline numbers, and simultaneously shows that at least three of them are published against more than one denominator (IAR-C 10/28 vs 10/20; HEB-1 36/36 vs a raw 40; "10 eligible partial claims" vs a raw 14). None of these is a measurement error; all are reporting-scope problems. Any new claim must state its denominator explicitly and must declare whether malformed controls are inside it.

2. **The historical evidence chain is not cryptographically bound end-to-end.** The certificate is unsigned, the fixture signing keys are derivable from public constants, `execution_trace.json` is producer-authored and carries no program digest, argv, environment, stdout digest, or signer identity, and `claims.attribution = "PROVEN"` is set by the producer *before* any verifier has run. The frozen Stage01 blind validator is a consistency checker, not a truth gate.

3. **The "no external ingress" conclusion is now independently confirmed from source**, not merely asserted. A repository-wide sweep found no HTTP server, socket listener, upload endpoint, or `argparse`/`stdin` certificate-composition path under `sp2027/analysis/`. The corrected reachability statement stands: `NO_EXTERNAL_CERTIFICATE_COMPOSITION_INTERFACE_FOUND_IN_INSPECTED_REPOSITORY_PATHS`. This is source-level negative evidence, not a proof of impossibility.

4. **The remediation v1 components are real, and their own test suite passes.** 55/55 reproduced independently in this environment. They are standalone utilities, not an integrated replacement evaluator, and their own READMEs say so.

5. **Objective 1 (previously unknown mechanism) is foreclosed by prior art.** RFC 9334 §8.1 states the cross-environment evidence-confusion mechanism in normative prose (verified verbatim from the RFC text in this session), and §12.3 states the stale-epoch confusion attack. The six ingredients of the proposed design are all specified in RFC 9334, in-toto, SLSA, TUF and Sigstore. What may still be claimed is a **measurement contribution** (a false-attribution-promotion rate for evaluation-evidence contracts, with a reproducible corpus and a tri-state adjudication metric), not a new mechanism. RFC 9334 §8.4 does, however, specify a *binary* verdict, so tri-state adjudication over an evaluation-evidence chain is not itself anticipated by that document.

6. **Objective 2 (a realistically reachable exploit) is not achievable in the current authorised environment.** There is no attacker-controlled ingress, and the pipeline's own aggregator constructs the certificate internally. This is now a source-verified negative, not an open question. What *is* achievable, and was achieved in Stage 1, is a **component-level capability gap demonstrated against the real frozen Stage01 pair**: the frozen pair ACCEPTS a bundle whose credited program was never executed, and a bundle whose credited output was never observed.

7. **Objective 3 (advantage over a real provenance product) is blocked on one permission.** The analysis is complete (Agent 3). The only genuinely comparable product is in-toto 3.1.0, which is offline by design; `slsa-verifier` and `cosign` are NOT_COMPARABLE for the ACTS-Attack contract. Installing `in-toto==3.1.0` into an isolated virtual environment requires explicit user approval, which has not been granted in this session.

8. **Objective 4 (trustworthy end-to-end attribution) is achievable and was the right thing to build.** Stage 1 implements a trusted execution observer, an independent reference verifier that consumes only the observer's signed stdout capture, a signed-context/replay layer, a fail-closed integrity preflight, and a tri-state adjudicator, and validates them against a frozen 27-case corpus with a frozen historical baseline.

---

*Next: `STAGE0_EVIDENCE_LEDGER.json`, `STAGE0_REPRODUCTION_REPORT.md`, `STAGE0_RESOURCE_GAPS.md`.*
