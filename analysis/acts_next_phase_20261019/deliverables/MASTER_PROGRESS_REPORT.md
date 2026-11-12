# Master Progress Report — ACTS-Attack, phase `acts_next_phase_20261019`

**Phase start:** 2026-10-19 · **Report date:** 2026-10-20
**Working tree:** `sp2027/analysis/acts_next_phase_20261019/` (new, separately versioned)
**Repository root:** `/mnt/nvme5/ACTS-Attack` (branch `master`, HEAD `4743d18`)

---

## 0. One-paragraph summary

This phase recovered the full research state, **reproduced** the prior team's
remediation test suite (55/55), **independently recomputed** the H1-R3
statistics and found six material reporting/provenance defects, **built and
frozen** a new end-to-end attribution experiment (TOEEA-1) with a genuine
trusted execution observer, **executed** it once after freezing (27 cases,
four contracts, plus the project's own frozen production Stage01 pair as a
non-strawman baseline), and produced a **source-verified negative result on
attacker reachability** and a **verbatim-quoted foreclosure of the novelty
category**. Two of the four objectives did not yield positive results; one of
them is foreclosed by prior art this phase identified.

---

## 1. Chronological record of stages and blockers

### Stage 0 — Repository recovery and reproducibility baseline — **COMPLETE**

| Step | Outcome |
|---|---|
| Locate and verify the repository | `/mnt/nvme5/ACTS-Attack`, git repo, branch `master`, HEAD `4743d18` |
| Record git state | Pre-existing dirty state (`.gitignore` modified, `ACTS-ATTACK` modified, `DEPOSIT_V1.1_STAGING/**` deleted) — **deliberately left untouched**; no reset, clean, amend, or unrelated commit |
| Verify the four protected artefact hashes | **All four match exactly, before and after this phase** |
| Locate the 28 mandatory historical documents | **28/28 found**, resolved paths recorded in `stage0/STAGE0_EVIDENCE_LEDGER.json` |
| Re-run the standalone remediation tests | **`55 passed in 17.13s` — the prior team's 55-PASS claim is INDEPENDENTLY REPRODUCED** |
| Identify missing sources / incompatible schemas / unverifiable assertions | 6 items in the ledger's `not_reproduced`; 12 material defects found (6 × H1-R3, 6 × HEB-1/B2) |
| Machine-readable evidence and artefact index | `stage0/STAGE0_EVIDENCE_LEDGER.json` |
| Current-state assessment before any intervention | `stage0/STAGE0_REPOSITORY_INVENTORY.md` §8 |

**Deliverables:** `STAGE0_REPOSITORY_INVENTORY.md`, `STAGE0_EVIDENCE_LEDGER.json`,
`STAGE0_REPRODUCTION_REPORT.md`, `STAGE0_RESOURCE_GAPS.md`.

### Stage 1 — Genuine end-to-end attribution (TOEEA-1) — **COMPLETE, executed once after freezing**

The highest-value feasible work in the phase. See
`deliverables/END_TO_END_ATTRIBUTION_PROTOCOL.md` and
`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md`.

1. **Preregistration** (`s1_protocol.md`): RQ, hypotheses H0–H4 with decision
   rules, the four contracts E0–E3, the eleven cross-record joins, the
   15-object evidence chain with the **trusted execution observer** named as
   the trusted component, the six-level ladder, the tri-state vocabulary and
   its precedence, the strict/lenient execution contracts, the frozen 27-case
   inventory, the metric definitions with denominators and Wilson CIs and a
   no-p-values rule, eight controls, an 8-step freeze-and-execute procedure,
   **ten declared threats to validity**, and the explicit relationship to the
   four objectives and to prior art.
2. **Case inventory frozen** (`s1_make_cases.py` → `s1_case_inventory/`,
   56 files; `s1_case_manifest.json`).
3. **Freeze** (`s1_freeze.py`): the vetted
   `heb1_remediation_v1/integrity/manifest_verifier.py` (unmodified) checks
   **77 files, 0 errors**; the run refuses to start unless the preflight
   passes.
4. **Test suite**: 17 tests, all passing.
5. **Confirmatory run** (once): 27 cases × 4 contracts + the frozen Stage01
   pair. **All 27 preregistered expectations matched** for E3 strict *and* E3
   lenient.
6. **Post-run re-verification** of the freeze: 77 files, 0 errors.
7. **Recomputation** (`s1_metrics.py`, `s1_summarize.py`): three metric sets.

**Headline result (attribution ground truth, n_success = 2, n_failure = 25):**
false attributions **13 → 11 → 6 → 0** across E0 → E1 → E2 → E3; false
rejections **0/2** for every contract; the frozen production Stage01 pair
**accepts 2 of the 25 non-successes** (C02, C03) and accepts **2 of the 2**
honest successes (so it is not a strawman).

### Stage 2 — Real provenance comparators — **ANALYSIS COMPLETE; EMPIRICAL PART BLOCKED**

* Inventory and guarantee analysis of **in-toto 3.1.0**, **slsa-verifier
  2.7.1**, **cosign 3.1.3**, **RFC 9334** — 653 lines, 40 cited URLs, with
  every row marked `N` / `[CUSTOM-INSPECTION]` / `—`.
* A fair common contract P1–P10 and a falsifiable prediction (P-1).
* **Not executed**, because installing in-toto requires approval that has not
  been granted (gap G-1, request R-1).
* `slsa-verifier` and `cosign` are **`NOT_COMPARABLE`**; RFC 9334 is an
  architectural target and is **not runnable**.

### Stage 3 — Operational boundary and reachable impact — **COMPLETE, NEGATIVE**

* Six-point qualifying test applied to **14 candidate ingresses**, re-derived
  independently; **0/14** pass "identifiable owner and authorisation".
* Finding token: **`NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED`** (plus 14
  further machine-readable fields).
* The decisive near-miss — the concurrent sibling tree's newly created
  `ingress_gateway.py` — is **excluded and documented**, so no reader mistakes
  it for a pre-existing ingress.
* The component-capability gap (Stage 1 C02/C03) is kept **strictly separate**
  from deployed reachability, with the structural reason.

### Stage 4 — AI-agent vs scripted producer — **NOT EXECUTED (blocked on authorisation)**

* Zero model calls, zero provider calls, zero network requests, zero
  credentials read, printed, or stored.
* All seven required confirmations are listed as MISSING with the specific
  question for each; the full matched-arm design, the four-cell interpretation
  matrix, and the nine mechanism-tracing requirements are specified in
  advance so the experiment is ready to run the moment authorisation exists.
* The binding rule from Stage 3 (identical transport for both arms) is carried
  over.

### Stage 5 — Novelty gate — **COMPLETE, FORECLOSES CATEGORY D**

* `deliverables/NOVELTY_PRIOR_ART_MATRIX.md`: categories A–E adjudicated.
  **A** supported, **B** supported (domain occupied), **C** partially
  supported / not yet earned, **D** **not supported — foreclosed**, **E** not
  supported on current evidence.
* The decisive evidence is **verbatim RFC 9334 §8.1 and §12.3 text**, fetched
  and read in this session, plus an independent verification pass over ten
  further prior-art claims (arXiv:2606.04990, `llmsa`, arXiv:2603.14332,
  arXiv:2605.14153, arXiv:2506.02548, arXiv:2610.16067, arXiv:2605.05379,
  preprints 202610.0322, in-toto's missing-vs-bad distinction, SLSA's verdict
  space).

---

## 2. What changed in the repository

**Nothing historical was modified.** All new work is in
`sp2027/analysis/acts_next_phase_20261019/`:

```
acts_next_phase_20261019/
├── stage0/          4 Stage-0 deliverables + 6 independent sub-reports
├── stage1_attribution/   the TOEEA-1 experiment (15 modules, 56 inventory
│                          files, 17 tests, frozen manifest, raw results)
├── stage2_provenance/    the comparator analysis
├── stage3_boundary/      the ingress analysis
├── stage4_arms/          the arm-status document
├── deliverables/         the 10 required deliverables
├── logs/                 run logs
└── MANIFEST.sha256       (in deliverables/)
```

The concurrent sibling tree `acts_next_phase_20261019_v2/` (a different
session's Stage 1, `stage1_e2a/`) was **found, documented and not touched**. It
is authored but **not frozen and not executed**; its `memfd` observer closes
the TOCTOU window that the Stage 1 observer leaves open, which is recorded as
a limitation of this phase's implementation.

---

## 3. Blockers and their exact status

| ID | Blocker | Blocks | Status |
|---|---|---|---|
| **G-1 / R-1** | `in-toto` not installed | Objective 3 (empirical) | **Awaiting user approval.** Exact command and isolation boundary specified; no credential, account, third-party service, or out-of-tree write is needed. |
| **G-4 / R-2** | Model-provider authorisation | Stage 4, any AI-specific claim | **Awaiting user decision.** Seven specific confirmations listed. |
| **G-5** | No authorised submission gateway | Objective 2 (the decisive conjunct) | **Not requested by design.** Requesting one would mean asking to create the artefact the study is looking for; the brief forbids it. Documented as a finding instead. |
| **G-2** | The working tree is on fuseblk: every file reports 0777 and `chmod` is ignored | The vetted `protected_signing.load_private_key` correctly refuses such a key | **Resolved** (deviation D-05): the private keystore lives outside the repository at `/tmp/acts_s1_keystore` (0700 dirs, 0600 keys); only the public bundle and custody record are in-tree. |
| **G-7** | `preprints.org` 202610.0322 returns HTTP 403 | Full text of the closest published measurement | **Not a permission problem.** Reported as an incompleteness in the novelty comparison. |
| **G-3, G-6, G-8** | `slsa-verifier`/`cosign` absent; `latexmk` absent; `secp256k1`/`ecdsa` absent | — | **Not blocking.** The first two are `NOT_COMPARABLE`; the third is not needed (the frozen verifier implements the arithmetic itself); `latexmk` is irrelevant because the manuscript is a protected artefact that is not rebuilt. |

---

## 4. The twelve material defects found in the historical record

These are documented, not fixed in place (the affected files are protected or
historical). Full evidence in `stage0/STAGE0_REPRODUCTION_REPORT.md` §4–§5.

**H1-R3 (6):**
1. The manuscript states the L3 pooled R2 arm as **123/128**; the raw
   `results.jsonl` gives **124/128**, in six places — contradicting the
   manuscript's own τ = −0.008.
2. `terminal_success == 1` for **801** of 852 sessions, not the 821 that the
   terminal-stage counts imply; the 20 C0 abstention records are
   `terminal=SUCCESS, terminal_success=0`. Neither report states 801.
3. The on-disk `h1r3_run.py` (`6605cf7a…`) differs from the frozen copy
   (`b0ba8cc2…`); the post-campaign edit **relaxes** the provider health gate
   and is unrecorded.
4. The freeze covers 14 files and excludes `results.jsonl`, the session
   bundles, the analysis outputs and `provider_adapter.py`.
5. "The same wrong formula appears in R0, R1 and R2" is **literally false**
   (R1: 0, R2: 0 occurrences).
6. The preregistration §7 contradicts the raw records on four counts.

**HEB-1 / Experiment B / B2 (6):** the dual denominator for the same IAR-C
numerator (10/28 vs 10/20); "10 eligible partial claims" is a hard-coded
family whitelist, not a data property (14 exist in the raw data); HEB-1's
"36/36" under-reports the held-out total (40); B2 publishes bare counts with
no denominators and its "held-out" set is IAR-B's held-out set, not an
additional draw; the IAR-A "75/2/0" artefact lives **outside the repository**;
and the two B2-2 reports give **opposite dispositions** for the same non-event
(`NOT_COMPARABLE` vs `PASS`).

**None of these changes the primary H1-R3 statistics** — the L3 pooled
contrasts and the L2 ECDSA contrast both recompute exactly and remain inside
their preregistered margins. The defects are in provenance and reporting.

---

## 5. The five deviations of this phase

Recorded in `stage1_attribution/s1_deviations.md`:
**D-01** the R01 lenient variant was not wired to the shared replay ledger
(implementation gap; fixed so the code matches the preregistration);
**D-02** the B01 Stage01 mutation deleted a non-existent path, so the frozen
validator was never exercised with a missing trace (fixed; a loud guard
added); **D-03** the B04 case crashed the certificate builder (`_sha256_or_absent`
added); **D-04** a summariser key-map bug (tooling only);
**D-05** key custody moved outside the repository because of the fuseblk mode
behaviour; **D-06** a second metric set (SET 2) added post-hoc, with the
preregistered SET 1 still reported; **D-07** the exploratory pre-freeze sweep
wrote to the same results path and was deleted, so the exploratory table is
transcribed into the log and is not reproducible from the current tree.

**No deviation changed a metric, a threshold, a denominator, or a decision
rule.**

---

## 6. Standing prohibitions observed

No third-party target was attacked; no unauthorised network request was made;
no provider credential was printed, transmitted to an unrelated system, or
stored; no model call was made without authorisation; no package was installed
without approval; no existing experiment file was modified in place; no
historical freeze was retrofitted; no success metric was redefined after
inspecting outcomes; fixture-private keys derived from public constants were
not treated as confidential issuer keys; file-hash integrity was not equated
with trusted execution provenance; source inspection was not presented as
exhaustive proof of deployment reachability; simulated baseline designs were
not presented as real products; and no success against any third-party system
was claimed.

---

## 7. How to reproduce this phase

```bash
cd /mnt/nvme5/ACTS-Attack/sp2027/analysis/acts_next_phase_20261019/stage1_attribution

python3 s1_setup_trust.py                 # fresh Ed25519 keys per role (keystore outside the repo)
python3 s1_make_cases.py                  # materialise the 56-file frozen case inventory
python3 -m pytest -q test_s1_attribution.py   # 17 tests
python3 s1_freeze.py                      # write + verify the integrity manifest (77 files)
rm -rf work runs && python3 s1_runner.py  # the single confirmatory run
python3 s1_freeze.py --verify             # re-verify the freeze after the run
python3 s1_summarize.py                   # decision tables
python3 s1_metrics.py                     # the three metric sets -> runs/summary.{md,json}
```

The remediation suite (historical, reproduced in this phase):

```bash
cd /mnt/nvme5/ACTS-Attack/sp2027/analysis/heb1_remediation_v1
python3 -m pytest -p no:cacheprovider -q   # 55 passed
```
