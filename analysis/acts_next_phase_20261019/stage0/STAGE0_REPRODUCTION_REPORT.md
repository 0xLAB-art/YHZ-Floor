# Stage 0 — Reproduction Report

**What was reproduced, what was recomputed from raw data, and what could not be verified.**

All work below was performed locally and offline in `/mnt/nvme5/ACTS-Attack`. No network request was made to any third party, no package was installed, and no model/provider call was made.

---

## 1. Reproduced: the remediation v1 test suite (the prior team's "55 PASS")

The prior team reported 55 passing remediation tests. That figure was **user-reported** until reproduced here.

```
cd /mnt/nvme5/ACTS-Attack/sp2027/analysis/heb1_remediation_v1
python3 -m pytest -p no:cacheprovider -q
```

**Result: `55 passed in 17.13s`** — the claim is independently reproduced in this environment.

Collection confirms 55 tests spread over `integrity/test_manifest_verifier.py`, `signing/test_protected_signing.py`, `context/test_context_validator.py`, `stage01/test_external_binding_wrapper.py` and `adjudication/test_audit_recompute.py`.

## 2. Reproduced: the protected artefact hashes

All four match exactly, before and after the work. See `STAGE0_REPOSITORY_INVENTORY.md` §1.

## 3. Reproduced: H1-R3 reference replay and test suite

Reported by the H1-R3 forensic sub-agent (AGENT4B) and re-executed against the retained raw artefacts:

* the 852-line reference replay re-runs with **852/852 agreement, 0 disagreements**;
* the H1-R3 test suite: **322/322 pass**;
* `H1R3_ANALYSIS.md` is **byte-reproducible** from the raw `results.jsonl`.

## 4. Recomputed independently: H1-R3 headline statistics

Recomputed from `h1r3_20261019/runs/confirmatory/results.jsonl` (852 JSONL records), not copied from any report:

| Quantity | Value | Note |
|---|---|---|
| Sessions | 852 | — |
| Terminal stage `SUCCESS` | 821 | — |
| Terminal stage `CRYPTOGRAPHIC_PREDICATE` | 28 | — |
| Terminal stage `EXECUTION` | 2 | — |
| Terminal stage `SOURCE_SYNTAX` | 1 | — |
| **`terminal_success == 1`** | **801** | 20 C0 abstention records are `terminal=SUCCESS` but `terminal_success=0`. **No historical report states 801.** |
| Route string | `claude-sonnet-4-6-free` for all 852 | the provider URL `https://api.apmix.ai` appears **only** in `EXECUTION_MANIFEST.json` and the runner source, never in `results.jsonl` |
| Arms | R0 276, R1 256, R2 256, R4 64 | plus 20 C0 records filed under arm R0 |
| L3 pooled R0 | 125/128 | — |
| L3 pooled R1 | 126/128 | τ(R1−R0) = +0.0078, CI [−0.0234, +0.0391], b=2 c=3 |
| L3 pooled R2 | **124/128** | τ(R2−R0) = −0.0078, CI [−0.0469, +0.0312], b=4 c=3 — both inside the ±10 pp equivalence margin |
| L2 ECDSA R2 vs R0 | 25/32 vs 32/32 | b=7 c=0, τ = −0.2188, CI [−0.3750, −0.0938], p = 0.0156 — exploratory, as the brief states |
| Crypto failure taxonomy | 19 d-wrong/k-right, 5 both-wrong, 2 k-only, 2 XOR content | ECDSA-algebra share 19/28 = 67.9 % (24/28 = 85.7 % counting d-wrong) |

### 4.1 Material defects found by independent recomputation

These are reported, not repaired: `sp2027/paper/main.tex` is a protected artefact and may not be edited.

| # | Severity | Finding |
|---|---|---|
| 1 | **MATERIAL** | The manuscript candidate states the L3 pooled R2 figure as **123/128** in six places; the true value recomputed from raw is **124/128**. The stated τ = −0.008 is consistent with 124/128, not with 123/128. The error is **absent** from `H1R3_ANALYSIS.md` and from the evidence package. |
| 2 | **MATERIAL (provenance)** | The on-disk `h1r3_run.py` hashes to `6605cf7a…` while the freeze manifest records `b0ba8cc2…`. The post-campaign (14:11 UTC) edit is unrecorded and **relaxes** the provider health gate from `all(checks)` to probe-only. The frozen semantics were recovered from the retained `.pyc`. |
| 3 | MATERIAL (freeze coverage) | The freeze contract covers 14 files. It does **not** cover `results.jsonl`, the session bundles, the analysis outputs, or `provider_adapter.py`. |
| 4 | MATERIAL (claim) | The evidence package states that "the same wrong formula appears in R0, R1, and R2". Literally false: the quoted flipped-numerator text occurs in 3 of 26 failing programs (R0 2, R4 1, **R1 0, R2 0**). |
| 5 | MATERIAL (preregistration) | Prereg §7 contradicts the raw records: the sanity run is **9/10, not 10/10**; "aborted after 9 sessions" corresponds to **17** retained bundles; "34 replayed artifacts generalized" corresponds to **0** attempts; the L3/R0 "syntax error" is labelled `OUTPUT_SCHEMA`. |
| 6 | Minor (scope) | The failure dossier reports 30/27 against the run's 31/28, silently scoped to `kind == "primary"`. |

**Interpretation.** The primary statistics are sound. The problems are provenance and reporting, not measurement.

## 5. Recomputed independently: HEB-1 / IAR-C / B2 / IAR-A figures

Recomputed by AGENT2 from the retained raw artefacts; **all seven checked numeric claims reproduced exactly** and **all 23 quoted artefact hashes verified**. The discrepancies found are about denominators, scope, retention and framing — not about the measurements:

* **D1** — IAR-C's "10/28" and "10/20" use the same numerator with different denominators (20 substantive + 8 malformed vs substantive only). The raw `results.json` stores only the numerator; the denominator 28 lives solely in `eb_independent_runner.py:57`. IAR-C is the only headline rate in the tree that includes malformed cases.
* **D2** — "10 eligible partial claims" is a hard-coded family whitelist (`audit_recompute.py:18`, `PARTIAL_FAMILIES = {"S13"}`), not a data property. The raw data contain **14** honest partial-claim cases (S13 = 10, S2 = 2, S3 = 2). Widened, V2's raw partial rejection is 14/14 and V3-full's partial acceptance is 14/14. `AUDIT_NOTES.md` does not disclose the exclusion.
* **D3** — HEB-1's "36/36" under-reports the held-out false-promotion total: the artifact's own `any_positive_gt_truth` is **40**. The four extras are control family C4. 36/36 is attack-family-scoped and defensible, but it is not the held-out total.
* **D4** — B2 publishes bare counts with **no denominators**; its "held-out" set **is** IAR-B's held-out set (identical 58 case IDs and identical v3-full decisions). B2 adds baselines; it is not an additional held-out draw.
* **D5** — The IAR-A "75 PASS / 2 WARN / 0 FAIL" artifact lives **outside the repository** (`/tmp/opencode/iar_a_verify/verify_report.json`). The committed `iar_a_results.json` has no A1b entry; that behaviour survives only via B2-2's `raw_subprocess/a1b_reproduction.json`.
* **D6** — The two B2-2 reports give **opposite dispositions** for the same non-event: v1 says `v3_full_comparison.status = "NOT_COMPARABLE"`, v2's gate table says "PASS as read-only baseline". Both agree it was never run.

## 6. Recomputed independently: Stage 1 confirmatory metrics (this phase)

Produced by `stage1_attribution/s1_metrics.py` from the frozen raw results `runs/results.json` and the frozen case table `s1_case_manifest.json`. No measurement is performed by the metric script.

Attribution ground truth (a bundle is a success iff the frozen case table says so): n_success = 2 (A01, A02), n_non_success = 25.

| contract | false attribution | Wilson 95 % CI | correct attribution | false rejection | correct rejection |
|---|---|---|---|---|---|
| `digest_only` (E0) | 13/25 | [0.335, 0.700] | 2/2 | 0/2 | 12/25 |
| `signed_digest_only` (E1) | 11/25 | [0.267, 0.629] | 2/2 | 0/2 | 14/25 |
| `signed_context_only` (E2) | 6/25 | [0.115, 0.434] | 2/2 | 0/2 | 19/25 |
| **`full` (E3, strict)** | **0/25** | [0.000, 0.133] | 2/2 | **0/2** | 25/25 |
| `full_lenient` (E3, lenient) | 1/25 (A05 only) | [0.007, 0.195] | 2/2 | 0/2 | 24/25 |

Frozen Stage01 pair: 13/27 cases have a direct analogue; 14 are N/A. ACCEPTED on `A01`, `A02` (honest — the baseline positive control, so the baseline is not a strawman), `C02_credited_program_not_executed` and `C03_submitted_output_not_observed`. **Stage01 false attributions = 2/25.**

## 7. Not reproduced / not verifiable

| Item | Status | Reason |
|---|---|---|
| H1-R3 live provider re-run | **NOT ATTEMPTED** | Out of scope by instruction (852 calls must not be re-run) and would require provider authorisation that has not been granted. |
| The `acts_next_phase_20261019_v2/stage1_e2a/` tree | **NOT EXECUTED** | It has no freeze manifest, no case inventory, no trust material and no run output. It is authored but not frozen. Not executed, not imported, not modified by this phase. |
| in-toto / slsa-verifier / cosign behaviour | **NOT EXECUTED** | Not installed. Installing requires explicit user approval that has not been granted in this session. The *documented* behaviour is analysed statically in `stage2_provenance/AGENT3_PROVENANCE_COMPARATOR_ANALYSIS.md`. |
| "Grounded but Wrong" (preprints 202610.0322) full text | **NOT OBTAINABLE** | preprints.org returns HTTP 403. The abstract and headline numbers were verified via OpenAlex (`W7220980858`, HTTP 200) but the full text was not obtained; the novelty comparison is therefore **incomplete** for that work. |
| Deployed attacker reachability | **NOT TESTABLE** | No authorised ingress exists (source-verified). |
| `latexmk` | **MISSING** | `pdflatex` and `pandoc` are present; `main.tex` and `main.pdf` are protected and were not rebuilt. |

## 8. Independent verification of the prior-art claims

The prior-art matrix (Agent 5) was itself audited by a second agent (Agent 5B), which fetched full texts and reported VERIFIED / REFUTED / NOT-OBTAINABLE per claim. Key outcomes:

* **RFC 9334 §§8.1 / 8.5 / 10 / 12.2 / 12.3** — VERIFIED EXACT, with line numbers. Independently re-fetched and re-read in this session.
* **RFC 9334 §8.4** — the verdict is **binary**; therefore RFC 9334 is *not* prior art for tri-state adjudication. This cuts in favour of a narrow residual novelty claim and is reported as such.
* **arXiv:2606.04990** — exists, but the "chain" claim is REFUTED: it is a gap-finding survey, not a system that occupies the domain.
* **`llmsa` (`LLM-Supply-Chain-Attestation`)** — VERIFIED, stronger than claimed (`internal/verify/result.go` defines `ExitMissing=10`, `ExitSignatureFail=11`, `ExitDigestMismatch=12`; ADR-0007 gives the rationale). Caveats: 2 stars, unpublished, no transparency log, and the tri-state is stage-level rather than claim-level.
* **in-toto** — a native library-level missing-vs-bad distinction exists (`LinkNotFoundError` vs `RuleVerificationError`), but the CLI collapses it to exit code 1; there is no tri-state verdict object.
* **SLSA** — "inconclusive" appears zero times; a VSA's `verificationResult` is `PASSED|FAILED`; unsupported provenance yields a hard error.

## 9. Reproducibility commands

```
# protected hashes
cd /mnt/nvme5/ACTS-Attack && sha256sum sp2027/analysis/RESULTS_LOCK.json \
  sp2027/analysis/RESULTS_LOCK_H1PC.json sp2027/paper/main.tex sp2027/paper/main.pdf

# remediation suite
cd sp2027/analysis/heb1_remediation_v1 && python3 -m pytest -p no:cacheprovider -q

# Stage 1 unit tests
cd sp2027/analysis/acts_next_phase_20261019/stage1_attribution && python3 -m pytest -q test_s1_attribution.py

# Stage 1 materialise the frozen corpus
python3 s1_make_cases.py

# Stage 1 freeze (writes + verifies the audited integrity manifest)
python3 s1_freeze.py && python3 s1_freeze.py --verify

# Stage 1 confirmatory run (refuses to start unless the preflight passes)
rm -rf work runs && python3 s1_runner.py

# Stage 1 metrics (recomputation only)
python3 s1_metrics.py
```
