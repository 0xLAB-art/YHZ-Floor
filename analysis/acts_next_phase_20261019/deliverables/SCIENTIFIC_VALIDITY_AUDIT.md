# Scientific Validity Audit — TOEEA-1 (Stage 1 end-to-end attribution)

**Auditor role:** independent, adversarial scientific auditor (subagent).
**Audit date:** 2026-10-20.
**Subject:** `sp2027/analysis/acts_next_phase_20261019/` — Stage 1 (TOEEA-1) end-to-end
attribution experiment, its preregistration, freeze, confirmatory run, and the five
deliverables that report its results.

---

## 0. Header

### 0.1 Scope

Audit of internal scientific validity only. Questions asked: was the freeze real; were
deviations honestly logged; are the reported numbers arithmetically correct; are the
denominators and statistics defensible; does each claim follow from the evidence; is the
trusted-observer design actually trusted; are the declared controls implemented; is the
Stage01 baseline a strawman.

**This audit does not attempt to re-derive the Stage 0 / Stage 2 / Stage 3 / Stage 4
claims** about the historical campaign, the H1-R3 statistics, RFC 9334, or in-toto /
SLSA / cosign behaviour (no network access was permitted; those are separate documents
with their own scope). Where a deliverable's claim depends on one of those, it is
adjudicated on the *internal* adequacy of its reasoning, and the dependency is recorded
in §8.

### 0.2 What I read

| Artefact | Path (relative to `sp2027/analysis/acts_next_phase_20261019/`) |
|---|---|
| Preregistration | `stage1_attribution/s1_protocol.md` (371 lines) |
| Deviations log | `stage1_attribution/s1_deviations.md` (184 lines) |
| Case table + labels | `stage1_attribution/s1_cases.py` (336), `s1_case_manifest.json` |
| Four contracts | `s1_attribution_evaluator.py` (410), `s1_baseline_evaluators.py` (209), `s1_verification.py` (214), `s1_reference_verifier.py` (140) |
| Trusted observer | `s1_trusted_observer.py` (320) |
| Measurement engine | `s1_runner.py` (767) |
| Support modules | `s1_common.py` (281), `s1_setup_trust.py` (162), `s1_stage01_compat.py` (242), `s1_freeze.py` (120), `s1_summarize.py` (129), `s1_metrics.py` (236) |
| Raw results | `stage1_attribution/runs/results.json` (27 records), `runs/summary.md` (74), `runs/summary.json` (505) |
| Integrity manifest | `stage1_attribution/s1_integrity_manifest.json` (77 files) |
| Test suite | `stage1_attribution/test_s1_attribution.py` (436) |
| Archived evidence | `stage1_attribution/work/<case>/` (27 bundles), `private/<case>/target_state.json` |
| Deliverables | `END_TO_END_ATTRIBUTION_RESULTS.md`, `END_TO_END_ATTRIBUTION_PROTOCOL.md`, `REPOSITORY_AND_TRUST_BOUNDARY_MAP.md`, `NOVELTY_PRIOR_ART_MATRIX.md`, `REAL_PROVENANCE_BASELINE_COMPARISON.md`, plus `FINAL_FOUR_OBJECTIVE_DETERMINATION.md`, `MASTER_PROGRESS_REPORT.md`, `RESOURCE_AND_PERMISSION_REQUESTS.md` |
| Other stages | `stage0/STAGE0_REPRODUCTION_REPORT.md`, `stage0/STAGE0_EVIDENCE_LEDGER.json`, `stage2_provenance/AGENT3_PROVENANCE_COMPARATOR_ANALYSIS.md`, `stage3_boundary/STAGE3_BOUNDARY_ANALYSIS.md`, `stage4_arms/STAGE4_ARM_STATUS.md` |
| Frozen historical components | `sp2027/analysis/contract_sound_stage01_validator_v2.py`, `contract_sound_stage01_reference_verifier_v2.py`, `run_contract_sound_stage01.py`, `run_contract_sound_agent_pilot.py` |
| Remediation components | `sp2027/analysis/heb1_remediation_v1/{signing,context,integrity}/` |

### 0.3 What I ran (all read-only; no repo file modified)

| # | Command | Result |
|---|---|---|
| 1 | `sha256sum` on the four protected artefacts | **all four match the expected values — see §0.4** |
| 2 | `python3 s1_freeze.py --verify` | `{"checked_files": 77, "errors": [], "passed": true}`, exit 0 |
| 3 | `python3 -c "s1_freeze.build_manifest()"` compared to the on-disk manifest | **byte-identical** (see AV-01) |
| 4 | `python3 -m pytest -p no:cacheprovider -q test_s1_attribution.py` | **17 passed in 166.03 s** (matches the deliverable's "17 passed") |
| 5 | `python3 s1_summarize.py` (the *frozen* summariser) | prints SET-1 numbers; agrees with `s1_metrics.py` on every figure |
| 6 | `/tmp/opencode/audit_recompute.py` — my own recomputation from `runs/results.json` + `s1_case_manifest.json` only | **every reported number reproduced exactly** (§3) |
| 7 | `/tmp/opencode/audit_reevaluate.py` — re-ran the frozen evaluators over the **archived** `work/*/bundle.json` | **26/27 bundles re-evaluate to exactly the recorded decisions**; the 27th is R01 (see §3.3) |
| 8 | `stat` on every file in the freeze/result chain | **mtime ordering contradicts the freeze claim** (see AV-01) |
| 9 | `git ls-files` / `git status` on the phase and on the frozen components | the whole phase and all three frozen Stage01 components are **untracked** |
| 10 | Direct read of `contract_sound_stage01_validator_v2.py`, `context_validator.py`, `run_contract_sound_stage01.py` | used for §5 and §7 |

My scripts live in `/tmp/opencode/` and are **not** in the repository.

### 0.4 Protected-artefact hash verification

```
4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39  sp2027/analysis/RESULTS_LOCK.json
8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103  sp2027/analysis/RESULTS_LOCK_H1PC.json
51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461  sp2027/paper/main.tex
fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a  sp2027/paper/main.pdf
```

**All four match the expected values exactly.** No protected artefact was modified.
This claim in `stage0/STAGE0_EVIDENCE_LEDGER.json` is independently confirmed.

---

## 1. Verdict summary

| # | Audit area | Verdict | Severity |
|---|---|---|---|
| A | **Freeze discipline** | **FAIL.** The manifest is a pure hash of the *current* tree, is regenerable at will, and was last written **15 min 35 s after** the confirmatory results. The preflight is genuinely fail-closed *with respect to the manifest as it stands at run time*; it provides **no** protection against modification *before* the run. The phase has no version-control history. | **BLOCKER** (AV-01) |
| A | Freeze coverage | **FAIL.** The three `heb1_remediation_v1` components (signing, context/replay/path-confinement, and the preflight verifier itself) are **not** in the manifest and **not** digest-pinned anywhere. `s1_metrics.py` — the script that produced every reported metric — is **not** in the manifest and **not** named in the deviations log. | **MAJOR** (AV-02, AV-03) |
| B | **Deviations** | **PARTIAL FAIL.** D-01…D-05 and D-07 are substantively accurate. **D-02 claims a safety guard that does not exist in the code.** D-07's summary sentence is factually wrong. Three material items are **undisclosed**: a wrong ground-truth label in the frozen case table, a third contradictory ground-truth column, and a raw-results field that misdescribes the C03 observation. | **MAJOR** (AV-07, AV-08, AV-11, AV-12, AV-13) |
| B | Exploratory vs confirmatory honesty | **ACCEPTABLE, with an accuracy defect.** The exploratory sweep is clearly labelled exploratory, and I verified its transcribed decision table against the confirmatory run: it is faithful apart from the two differences D-01/D-02 describe. The raw exploratory output and the exploratory code state are unrecoverable, so the transcription is unfalsifiable. | MINOR (AV-08, AV-09) |
| C | **Independent recomputation** | **PASS.** My own script, written from `runs/results.json` + the frozen case table only, reproduces **every** number in `runs/summary.md`, `runs/summary.json`, `END_TO_END_ATTRIBUTION_RESULTS.md` and `FINAL_FOUR_OBJECTIVE_DETERMINATION.md` exactly — decision distribution, FA/FR/CA/CR under both metric sets, family decomposition, all Wilson intervals, and the Stage01 table. **Zero arithmetic discrepancies.** | — (PASS) |
| C | Raw-results ↔ archived-evidence consistency | **PASS (strong).** Re-running the frozen evaluators over the archived `work/` bundles reproduces 26/27 recorded decisions exactly; the 27th (R01) differs only because it is a *second* evaluation against a shared ledger. The results are internally sound. | — (PASS) |
| D | **Denominators / statistics** | **MIXED.** Wilson intervals are computed correctly and on the right denominators; no p-values; population claims are explicitly disclaimed. But the **preregistered** metric fails the preregistered success criterion (E3 FR = 19/21), and the **preregistered H1 chain fails** under it; the headline numbers, the hypothesis adjudications and the Objective-4 determination all come from the **post-hoc** metric, and this is not stated. n = 2 cannot support a rate claim. | **MAJOR** (AV-15, AV-16, AV-17, AV-18) |
| E | **Claims** | **MIXED.** The non-claims are exemplary: no live exploit, no novelty, no AI-specificity, no product-superiority result, no population rate. But there is an internal contradiction in the controls table, a wrong control count, a leftover "6 honest successes", a "deployed"/"production" adjective that overstates, and an Objective-4 `ESTABLISHED` determination that rests on the post-hoc metric while the document's own governing rule forbids exactly that. | **MAJOR** (AV-20, AV-21, AV-22, AV-28) + MINORs |
| F | **Threat model** | **MIXED.** The producer cannot influence the observer's input digest, the signature/context/replay layers are sound, and **no bypass of the `program_output` re-derivation check that yields a false attribution was found**. But the observer **asserts** rather than **measures** the executed bytes; the advertised "join #9" is tautological; and the replay ledger is per-evaluation, in-memory, and keyed on the *attempt* rather than the artefact. | **MAJOR** (AV-30, AV-31) + MINORs |
| G | **Controls** | **PARTIAL FAIL.** 8 of the controls are implemented and would fail if the guarded property broke (verified by reading each assertion). **Two declared controls are not implemented as executable checks** (negative controls; claim-invariance), and the "operational positive control" is not gated in code. The "nine controls declared in the protocol" claim is wrong three ways. | **MAJOR** (AV-21, AV-22, AV-32, AV-33) |
| H | **Stage01 baseline fairness** | **PASS, with a scoping caveat.** The Stage01 pair is **not** a strawman: the historical certificate format has **no field** in which the C02/C03 conditions can even be expressed (verified against the real pilot), so the pair is asked a question its format cannot answer. The C02/C03 result is **(b) a component capability gap only**. Caveat: the substituted artefacts are synthetic and mutually inconsistent, and two of the 13 table rows are harness verdicts, not frozen-component verdicts. | MINOR (AV-35…AV-38) |

**Overall:** the *measurement* is sound and independently reproducible; the *preregistration
and freeze* are not, and the *reporting* overstates the strength of the confirmatory
status in several places. None of the findings below invalidates the C02/C03 capability
gap, the 13→11→6→0 ablation, or the arithmetic. All of them weaken the claim that this
was a **preregistered, frozen, confirmatory** experiment, and several weaken the
Objective-4 `ESTABLISHED` determination as stated.

---

## 2. Detailed findings

### AV-01 — The "freeze" is a self-certifying hash of the current tree, and it post-dates the run — **BLOCKER**

**Evidence**

* `stage1_attribution/s1_freeze.py:77-100` — `build_manifest()` hashes the protocol, the
  runner, 18 components, the labels, the public trust bundle and every case-inventory
  file, all read from the *working tree at call time*.
* `stage1_attribution/s1_freeze.py:109-112` — without `--verify`, `s1_freeze.py`
  **overwrites** `s1_integrity_manifest.json` with a freshly built manifest.
* I ran `s1_freeze.build_manifest()` and compared it to the on-disk manifest:
  **`built == on_disk` → `True`**. The manifest in the tree is *exactly* "the current
  tree, hashed". It therefore carries **zero** information about the tree state at
  run time, and can be regenerated at any moment to match any modification.
* `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:186-187` documents the reproduce
  recipe as `python3 s1_freeze.py && python3 s1_freeze.py --verify` — i.e. the
  documented procedure **rewrites the manifest before the run**. A manifest that the
  reproduce recipe regenerates is not a freeze.
* `stage1_attribution/s1_freeze.py:114` — the verification step is `verify_manifest(...)`
  against that same regenerated file. The preflight is therefore fail-closed *only with
  respect to the manifest as it stands at the moment the run starts*.
* **mtime ordering** (the decisive evidence):

  ```
  2026-10-20 11:17:27  s1_case_manifest.json
  2026-10-20 11:29:29  trust/public_bundle.json  (also rewritten at run start)
  2026-10-20 11:29:39  runs/results.json           <-- CONFIRMATORY RUN
  2026-10-20 11:37:14  s1_metrics.py
  2026-10-20 11:37:14  runs/summary.md
  2026-10-20 11:42:22  s1_deviations.md            <-- D-06 / D-07 written
  2026-10-20 11:45:14  s1_integrity_manifest.json  <-- MANIFEST LAST WRITTEN
  ```

  The manifest was last written **15 min 35 s after** the results it certifies.
  Moreover, because the manifest hashes `s1_deviations.md` (whose current content
  includes the D-06 and D-07 sections written at 11:42), the manifest in the tree
  **cannot** be the artifact that gated the 11:29 run. A pre-run manifest either
  hashed an earlier deviations file (and was later overwritten) or did not exist.
  **No pre-run copy survives, and no attestation of its digest was published.**
* `git ls-files sp2027/analysis/acts_next_phase_20261019/` → **0 files**;
  `git status` → `?? sp2027/analysis/acts_next_phase_20261019/`. The entire phase,
  and the three frozen Stage01 components it depends on, are **untracked** working-tree
  files with no version history. (They are *not* gitignored — `git check-ignore` exits 1 —
  they are simply uncommitted.)

**What the problem is.** The protocol asserts (`s1_protocol.md:6-9`) that the protocol
"is hashed into the Stage 1 integrity manifest and the manifest is verified by the
audited remediation preflight **before** the confirmatory run is allowed to start", and
`s1_protocol.md:269-283` prescribes freeze → preflight → run → re-verify. The
*mechanism* is real: `s1_runner.py:763` calls `preflight_then_execute(...)` and the run
cannot start if the preflight fails. But the mechanism only detects modification
**during** the run. It cannot detect modification **before** it, because the manifest
is regenerated from whatever is on disk. With no git history, no archived pre-run
manifest and no external digest commitment, there is **no evidence** that the protocol,
case table, evaluators or runner were fixed before the confirmatory pass rather than
after it.

**Does it change a reported number or claim?** It does not change a number. It
invalidates the *epistemic status* of the experiment: the package repeatedly labels the
run "confirmatory" and "executed once after freezing"
(`deliverables/MASTER_PROGRESS_REPORT.md:14-16, 42, 64-67`;
`deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:185-191`;
`deliverables/END_TO_END_ATTRIBUTION_PROTOCOL.md:3` "verified … **before AND after the
run**"; `deliverables/REPOSITORY_AND_TRUST_BOUNDARY_MAP.md:147` "The measurement itself
is frozen"). Those claims are **not supported by the evidence in the tree**. The
honest statement is: *the run was gated by a fail-closed preflight over a manifest that
hashed the tree as it then stood; the tree as it then stood cannot be verified against
the tree that produced the results.*

---

### AV-02 — The three remediation components that implement the trust primitives are outside the freeze and unpinned — **MAJOR**

**Evidence**

* `s1_freeze.py:37-56` — the `COMPONENTS` dict covers 18 files. `grep -c heb1
  s1_integrity_manifest.json` → **0**. The manifest contains **no** path under
  `heb1_remediation_v1`.
* But `s1_common.py:40-44` imports them **by path** into `sys.path`, and they
  implement: `protected_signing.py` → `sign_record`, `verify_record`,
  `load_private_key`, `IssuerPolicy` (the role/kind authorisation, i.e. the whole of
  E1/E2's signature layer and the observer's signing); `context_validator.py` →
  `validate_signed_context`, `ReplayState`, `confine_bundle_path` (the whole of the
  context-binding, replay-ledger and path-confinement layer); `manifest_verifier.py` →
  the preflight that gates the run **and verifies the manifest**.
* `s1_common.py:60-65` pins digests for **only** the two Stage01 components
  (`FROZEN_STAGE01_VALIDATOR_SHA256`, `FROZEN_REFERENCE_VERIFIER_SHA256`). There is
  **no** pin for `protected_signing.py`, `context_validator.py` or
  `manifest_verifier.py` anywhere in the tree, and no test asserts their digests.

**What the problem is.** `s1_protocol.md:274-276` promises the freeze covers "every
component source file". The components that actually implement signature verification,
context binding, replay detection, path confinement and the preflight are excluded, and
unlike the Stage01 components they carry **no independent digest pin**. A silent edit
to `context_validator.py` between the freeze and the run would change the meaning of
every Stage 1 result (it could disable the replay ledger, weaken path confinement, or
weaken the preflight itself) without tripping any check. This is a self-defence gap:
the manifest cannot detect tampering with its own verifier.

**Changes a reported number or claim?** Not the numbers as reported. It removes the
guarantee that those numbers are attributable to the cited "unmodified vetted"
components (`deliverables/REPOSITORY_AND_TRUST_BOUNDARY_MAP.md:145, 156-158`;
`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:39`).

---

### AV-03 — `s1_metrics.py` — the script that produced every reported metric — is not frozen and not logged — **MAJOR**

**Evidence**

* `runs/summary.md:5` — "Computed by `s1_metrics.py` (post-hoc recomputation; no
  measurement)". `runs/summary.json` and `stage0/STAGE0_REPRODUCTION_REPORT.md:82-94`
  and `deliverables/MASTER_PROGRESS_REPORT.md:68` likewise credit `s1_metrics.py`.
* `s1_freeze.py:37-56` — `s1_metrics.py` is **absent** from `COMPONENTS`; it is not in
  the manifest.
* `s1_metrics.py:1-8` — its own docstring: "**This script is NOT part of the frozen
  measurement code.** It was written after the confirmatory run".
* `s1_deviations.md` — **never names `s1_metrics.py`**. D-04
  (`s1_deviations.md:79-84`) discusses `s1_summarize.py`, a *different* file that *is*
  frozen. `s1_metrics.py` is the file that actually defines SET 1 / SET 2 / SET 3 and
  the Wilson implementation used for every reported CI.
* mtime: `s1_metrics.py` = 11:37:14, i.e. **7 min 35 s after** `runs/results.json`
  (11:29:39) and before the manifest was rewritten (11:45:14).

**What the problem is.** The deviations log is declared to be the complete record
("Every deviation is recorded here", `s1_deviations.md:7-9`; "Nothing in this log may be
silently removed", `:9`). The introduction of the metric-defining script — including
the entire SET 2 ground-truth definition — is a post-hoc change to the analysis
apparatus that is disclosed in the deliverable's prose but **absent from the
deviations log**, and the script is outside the freeze. Note that `s1_metrics.py`
*does* declare itself post-hoc, and `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:8`
does name it — so this is a completeness failure in the deviations log, not a
concealment. (Mitigating: I reimplemented every metric independently — §3 — and the
arithmetic is correct.)

**Changes a reported number or claim?** No (my recomputation matches exactly). It
changes the *status* of SET 2 from "a disclosed post-hoc addition" to "a post-hoc
addition that escaped the disclosure ledger and the freeze."

---

### AV-04 — `trust/KEY_CUSTODY.json` is listed as a frozen artefact but is not frozen (and cannot be) — **MINOR**

* `s1_protocol.md:367` — the "Frozen artefacts" table lists "Trust custody record |
  `trust/KEY_CUSTODY.json` | key ids, modes, holders (no private material)".
* `s1_freeze.py:94` — only `trust/public_bundle.json` is hashed
  (`labels_trust: {labels, trust}`). `KEY_CUSTODY.json` is **not** in the manifest.
* It **cannot** be: `s1_runner.py:727` calls `setup_trust(force=False)` at the start
  of every run, and `s1_setup_trust.py:148` writes `KEY_CUSTODY.json` unconditionally.
  Freezing it would make every run fail its own preflight.
* **The protocol's frozen-artefact table is therefore inaccurate on this row.** The
  underlying disclosure (D-05, `s1_deviations.md:86-100`) is otherwise honest.

### AV-05 — The bundles actually evaluated are outside the freeze — **MINOR**

The manifest covers the case *inventory* (56 files) and the code, but not the
per-case `work/<case>/bundle.json` that was actually evaluated, nor the private target
states. I closed this gap myself: re-running the frozen evaluators over the archived
`work/` bundles reproduces 26/27 recorded decisions exactly (§3.3). So the *substance*
is fine; the *manifest* simply does not attest to it.

### AV-06 — The whole phase is untracked in git — **OBSERVATION**

`git ls-files sp2027/analysis/acts_next_phase_20261019/` → 0. The three frozen Stage01
components (`contract_sound_stage01_validator_v2.py`,
`contract_sound_stage01_reference_verifier_v2.py`, `run_contract_sound_stage01.py`) are
also untracked, but they **are** digest-pinned in `s1_common.py:60-65` and the pins
are verified at load time and by `test_s1_attribution.py:40-53` — that part of the
chain of custody is sound and I confirmed the pins resolve.

---

### AV-07 — D-02 claims a "fails loudly" guard that does not exist in the code — **MAJOR**

**Evidence**

* `s1_deviations.md:58-60` — "*A guard was added so that a Stage01 analogue whose
  mutation is supposed to remove a file **fails loudly** if the file it intended to
  remove is still present.*"
* `s1_runner.py:664-666` — `if mutation == "drop_kind:execution_observation":
  trace = stage01_dir / "execution_trace.json"; trace.unlink(missing_ok=True)`
* `s1_runner.py:667-668` — `if mutation == "delete_file:program_source":
  (stage01_dir / "agent_artifact.json").unlink(missing_ok=True)`

`unlink(missing_ok=True)` is **the exact silent-no-op pattern that D-02 itself
identifies as the original bug** (`s1_deviations.md:49-52`: "the runner's B01 mutation
deleted … (`unlink(missing_ok=True)` → a silent no-op)"). There is no guard, no
assertion, no `raise` on this path. `grep -n "unlink\|raise " s1_runner.py` shows the
only `raise`s are for unknown primitives, missing inventory files, instance/fixture
divergence, missing alt-program files, unknown mutations and a missing manifest —
none of which cover this case.

**What the problem is.** The deviations log asserts a safety mechanism that was never
implemented. This matters because the B01 Stage01 mutation is exactly the case where
the silent no-op produced a *spurious* `ACCEPTED` in the exploratory pass. With the
guard absent, the same silent no-op can recur silently in any future run; nothing in
the pipeline would announce that a Stage01 mutation did not take effect. The
confirmatory B01 value (`REJECTED`) is correct in fact — I re-evaluated the archived
B01 bundle and it does yield `REJECTED` under the frozen pair — so no reported number
is wrong. But the *claimed* protection is fictitious.

**Changes a reported number or claim?** No number. It removes a claimed safeguard and
is a false statement in the deviations log.

---

### AV-08 — D-07's summary sentence is factually wrong about the exploratory/confirmatory diff — **MINOR**

* `s1_deviations.md:141` — "*The two tables agree on every case except `R01` under the
  lenient contract, which is deviation D-01.*"
* But the exploratory table at `s1_deviations.md:155` records
  `B01_missing_observation | … | ACCEPTED (D-02)`, whereas the confirmatory value is
  `REJECTED` (verified in `runs/results.json`). That is a **second** difference, and it
  is on a different axis (the Stage01 column) than the one the sentence names.
* D-02 itself (`s1_deviations.md:61-62`) does disclose the B01 change, so this is an
  inaccurate summary sentence, not a concealment. I diffed the whole exploratory table
  (`s1_deviations.md:145-173`) against the confirmatory run: apart from R01-lenient
  and B01-Stage01, **the transcription is faithful**.

### AV-09 — The exploratory run's raw output and code state are unrecoverable — **MINOR**

`s1_deviations.md:131-142` discloses that the exploratory sweep wrote to the same
`runs/results.json` and was removed by `rm -rf work runs`. Deleting the exploratory
output is standard practice *provided the exploratory code is versioned*; here neither
the output nor the code state survives, so the D-07 transcription is **unfalsifiable**.
Acceptable given the disclosure, but it means the exploratory/confirmatory separation
rests on the author's assertion alone.

### AV-10 — D-01's "Action taken" understates the code change — **MINOR**

`s1_deviations.md:33-36` describes only the lenient variant being rewired. The code
also wires the **three baseline evaluators** to the shared ledger
(`s1_runner.py:623-628`), which is a larger change than described. Harmless: the
confirmatory E0/E1/E2 values on R01 are all `REJECT` and consistent with the frozen
expectation.

### AV-11 — The frozen case table's `expected_crypto_success` for C03 is factually wrong — **MAJOR, UNDISCLOSED**

**Evidence — three sources disagree with the label**

* `s1_cases.py:248-252` — C03 is declared with `expected_crypto_success = False`, while
  its own `notes` in the same record read: "*the submitted output is cryptographically
  accepted by a fresh reference verdict*".
* The archived bundle's own signed reference verdict,
  `work/C03_submitted_output_not_observed/reference_verdict.json`
  → `"verdict": "ACCEPTED"`, `"cryptographic_predicate": true`,
  `"crypto_details": {"recovered_d_matches": true, "recovered_k_matches": true,
  "public_key_matches": true, "repeated_r": true, "signatures_verify": true}`.
* The frozen manifest `s1_case_manifest.json` carries the same wrong label.

**What the problem is.** The cryptographic predicate **is** true on the presented
output of C03 — that is the whole point of the case construction (`swap_output`
presents a valid answer obtained from a different run). The label says otherwise. The
label is the *ground truth* for the preregistered metric SET 1.

**Effect on the reported numbers (my recomputation, §3.2)**

| contract | SET 1 as reported | SET 1 with C03 relabelled `true` |
|---|---|---|
| denominators | true n=21 / false n=6 | true n=22 / false n=5 |
| `digest_only` FA | 1/6 [0.030,0.564] | **0/5** [0.000,0.434] |
| `signed_digest_only` FA | 1/6 | **0/5** |
| `signed_context_only` FA | 1/6 | **0/5** |
| `full` FA | 0/6 [0.000,0.390] | 0/5 [0.000,0.434] |
| `full` FR | 19/21 [0.711,0.973] | **20/22** [0.722,0.975] |
| `full` CR | 6/6 | **5/5** |
| `full_lenient` FA | 0/6 | 0/5 |

**Why this matters beyond arithmetic.** Under the preregistered metric, the *only*
false attribution for E0/E1/E2 is C03 — and C03 is the case whose crypto label is
wrong. With the label corrected, **all four contracts have zero false attributions
under the preregistered metric** (on a 5-case denominator), and the entire
"13 → 11 → 6 → 0" ablation narrative is a property of the **post-hoc** ground truth
alone. The preregistered metric would then show *no* difference between the contracts
on false attribution. This is the single most consequential finding of the audit: it
removes the only quantitative separation the preregistered metric offers.

**Disclosed?** No. It appears in neither `s1_deviations.md` nor any deliverable.

**Changes a reported number?** **Yes.** The SET 1 table in
`runs/summary.md:11-15`, `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:97-101` and
`stage0/STAGE0_REPRODUCTION_REPORT.md` is computed from a mislabelled case.

---

### AV-12 — A third ground-truth column exists, contradicts `expected_decision`, and is undisclosed — **MINOR**

* The frozen manifest carries **three** truth-bearing columns per case:
  `expected_decision`, `expected_crypto_success` and **`ground_truth`**
  (`s1_cases.py:317-333`; `s1_cases.py:45-46`).
* `ground_truth` is `"attributable"` for A01, A02 **and A05**
  (`s1_cases.py:200-201`), while A05's `expected_decision` is `REJECT`
  (`s1_cases.py:201`). The two columns disagree on A05.
* `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:67` — "*Ground truth is recorded
  twice per case and the two are kept distinct*".
  `deliverables/END_TO_END_ATTRIBUTION_PROTOCOL.md:99` — "*Ground truth is recorded
  **twice** per case*". Both are wrong: it is recorded **three** times, and one pair
  disagrees.
* Using the third column as the SET 2 ground truth instead gives n_success = 3 and
  changes E3's false-rejection count from 0/2 to **1/3** (my recomputation, §3.2).

**Changes a reported number?** Not as reported (SET 2 uses `expected_decision`), but
it shows the frozen table is not self-consistent, and the deliverables' description of
it is inaccurate.

---

### AV-13 — `results.json`'s `observed` block misdescribes the C03 observation — **MINOR, UNDISCLOSED**

* `s1_runner.py:702-703` — the record's `observed` block is filled from
  `reference_out["verdict"]` and `reference_out["facts"]["cryptographic_predicate"]`,
  where `reference_out` is the verdict computed at `s1_runner.py:365-372`, i.e. **before**
  the `swap_output` mutation. The verdict actually written into the bundle is `fresh`
  (`s1_runner.py:477-486`).
* Consequently `runs/results.json` records for C03: `observed.reference_verdict =
  "REJECTED"`, `observed.cryptographic_predicate = false` — while the bundle's signed
  verdict says `ACCEPTED` / `true`.
* The raw results file therefore contains an "observed" field that does not describe
  the observed bundle. This is the mechanical root of AV-11: the wrong label was
  probably copied from the wrong verdict.

---

### AV-14 — `results.json.evaluator_names` omits `full_lenient` — **MINOR**

`runs/results.json` → `"evaluator_names": ["digest_only","signed_digest_only",
"signed_context_only","full"]` (4 names) while `decisions_detail` contains **5**
evaluators including `full_lenient`, on which a headline number depends
(`runs/summary.md:32`; `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:79`).
`EVALUATOR_NAMES` at `s1_runner.py:78` has the same 4-element list. Schema inconsistency
in the raw results.

### AV-15 — The headline, the hypothesis adjudications and the Objective-4 determination rest on a post-hoc metric, and the preregistered criterion's failure is not stated — **MAJOR**

This is the most consequential reporting finding.

**The preregistration's own success criterion** — `s1_protocol.md:350-355`:

> "**Objective 4** … Its success criterion: *the new evaluator justifies an attributed
> completion claim only when the complete required causal and cryptographic evidence
> chain supports it.* The predeclared test of that criterion is: **zero false
> attributions and zero false rejections on the frozen corpus**, plus the H4 capability
> gap against the frozen Stage01 pair."

**Under the preregistered metric (SET 1, `s1_protocol.md:212-237`)** — the only metric
defined before the run — the results are:

* `full` (strict): **FA 0/6, FR 19/21 [0.711, 0.973]**, CA 2/21, CR 6/6.

E3 rejects 19 of 21 cryptographically-true cases. The predeclared criterion ("zero
false rejections on the frozen corpus") is therefore **NOT met** under the metric the
protocol fixed. It is met only under SET 2, the ground truth added after the run
(D-06, `s1_deviations.md:112-129`).

**H1's preregistered prediction** — `s1_protocol.md:57-59`: "*E3's false-attribution
count < E2's < E1's ≤ E0's*". Under SET 1: E0 = 1, E1 = 1, E2 = 1, E3 = 0. The chain
**fails at the middle inequality** (E2 < E1 is false: 1 < 1). Under SET 2 it holds
(13 > 11 > 6 > 0). `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:109` reports H1 as
**SUPPORTED** with the evidence "13 → 11 → 6 → 0 across E0 → E1 → E2 → E3, monotone" —
SET 2 numbers — without stating that the preregistered metric fails the preregistered
prediction.

**H2's preregistered prediction** — `s1_protocol.md:61-63`: "*E3 false-rejection count
= 0 on the honest-success denominator*". Under SET 1, E3's FR is 19/21. Under SET 2 it
is 0/2. `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:110` reports H2 **SUPPORTED**
on the SET 2 number only.

**What is and is not disclosed.** `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:91-103`
does report SET 1 (§4.3) with the D-06 caveat, and §4.3 does show `full` FR = 19/21.
That is the single most important disclosure in the package and it is present. But:

* §4.1 is headed "**Primary metric**" and is the SET 2 table; SET 1 is demoted to
  §4.3.
* §4.4 reports H1/H2 as SUPPORTED with no mention that the preregistered metric
  contradicts them.
* §10 ("ESTABLISHED (on the frozen corpus, within the stated scope)") cites
  "0/25 false attributions, 0/2 false rejections" — SET 2 only — and does not say
  that the preregistered success criterion fails under the preregistered metric.
* `deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:9-12` states a governing rule
  "stated in advance and observed": "*no objective is marked `ESTABLISHED` on the basis
  of a guarantee that was not tested*". The "zero false rejections" guarantee **was**
  tested under the preregistered metric and **failed** there.

**Is the objection fair?** Partly, and I say so plainly. The preregistration's
`crypto_success` ground truth is *itself* defective for this question: `s1_protocol.md:203-208`
anticipated only A05 as "a cryptographically true case rejected for a non-cryptographic
reason", and did not anticipate the entire contradiction family being crypto-true-and-
correctly-rejected. A contract that rejects a tampered-signature case is not
"wrong" because the underlying signature happened to be cryptographically valid. So
SET 1 is a poorly-posed metric, and the author was right that SET 1 "is not the
interpretable one" (`s1_deviations.md:122-124`). **But** the honest handling is
therefore to state the preregistered criterion as **FAILED / NOT MET under the
preregistered metric** and the post-hoc metric as a *re-analysis*, not to designate
the post-hoc metric "primary" and let the preregistered failure sit in a
sub-section. As written, a reader of §4.1 and §10 alone would not learn that the
preregistered criterion failed.

**Changes a reported number?** No. **Changes a claim?** Yes — it changes the epistemic
status of the Objective-4 `ESTABLISHED` determination and of H1/H2.

---

### AV-16 — n = 2 does not support a rate claim; the Wilson upper bound is 0.658 — **MAJOR**

* The primary metric's success denominator is **2** (`A01`, `A02`). The
  "0/2 false rejection" claim has Wilson 95 % CI **[0.000, 0.658]**
  (`runs/summary.md:28-32`; I reproduce it). The data are compatible with a true
  false-rejection rate anywhere from 0 to **65.8 %**. "0/2" is a *demonstration that
  no false rejection occurred on these two cases*, not a bound and not a rate.
* `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:170` makes this point for the
  **false-attribution** rate ("the estimate of E3's *true* false-attribution rate is
  only bounded above by 13.3 % (95 %)") but **not** for the false-rejection rate.
  `deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:214-215` does state it ("The
  '0/2 false rejection' claim is a *demonstration of non-regression on these two
  cases*, **not** a rate").
* The corpus is balanced by construction (8 honest / 5 omission / 14 contradiction), so
  the 2:25 split is an artefact of the design, not a sample. This is disclosed
  (`s1_protocol.md:234-237, 326-328`; `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:169`).
* **PASS on the statistics themselves:** the Wilson implementation in
  `s1_metrics.py:47-54` and `s1_summarize.py:20-27` is the textbook score interval and
  I reimplemented it independently; every interval I computed matches to three
  decimals. Denominators are as declared. **No p-values are reported anywhere** in
  the Stage 1 outputs (I grepped). **No population-rate or prevalence claim is made**
  in the Stage 1 material.

### AV-17 — SET 2's ground truth is the frozen *expected output* of the evaluator under test — **MINOR**

SET 2's ground truth is `expected_decision` — i.e. what the E3 evaluator is expected to
output. `s1_cases.py:6-7` asserts "Ground truth is defined by the case *construction*,
not by any evaluator outcome", and for 26 of 27 cases the expectation is a
construction-level judgement (correct/incorrect answer, present/absent evidence,
contradictory/not), so this is not circular in the strict sense. But it means SET 2's
"correct rejection" and "false rejection" measure **agreement with the frozen
expectation table**, not an independently derived truth. A reader could reasonably
mistake "0/2 false rejections" for a measurement against an external oracle. It should
be stated that the oracle is the frozen table.

### AV-18 — SET 3's column header contradicts its cell content — **MINOR**

`runs/summary.md:43` — the column is headed "**A: non-success not promoted**" while the
cell reads "1 promoted" (`runs/summary.md:45-49`;
`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:83` uses the clearer "A: non-success
promoted (of 6)"). The `runs/summary.md` header is a mislabel.

---

### AV-19 — The Stage01 "false attributions 2/25" is measured on the post-hoc ground truth without saying so — **MINOR**

`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:156` — "**Stage01 false attributions =
2/25.**" The 25 is the SET 2 (post-hoc) non-success denominator. Under the
preregistered denominator (n=6 crypto-false) the Stage01 pair's false acceptances are
0 (C02/C03 are both crypto-true). The number is not wrong, but it silently adopts the
post-hoc denominator.

### AV-20 — The controls table contains a self-contradictory row — **MAJOR**

`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:118`:

```
| Positive control (6 honest successes must be attributed) | E3 attributes 2/2 |
```

There are **2** honest successes in the corpus (A01, A02), not 6 — the row's own
right-hand cell says "2/2". "6" is a leftover from an earlier corpus design (the
protocol itself mis-states the denominators as 14/13 at `s1_protocol.md:215`; the
actual split is 21/6 or 2/25 depending on the metric). Two different wrong corpus
sizes have propagated into the frozen protocol and the results report. A reader
checking the control would conclude the control failed.

### AV-21 — "Nine controls declared in the protocol and exercised" is wrong three ways — **MAJOR**

`deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:203-204`. The three documents
disagree:

| Document | Count | Location |
|---|---|---|
| The frozen protocol | **5** controls | `s1_protocol.md:246-266` (positive-operational :248, positive-baseline :251, negative :254, cross-implementation :257, claim-invariance :261) |
| The protocol deliverable | **8** controls | `deliverables/END_TO_END_ATTRIBUTION_PROTOCOL.md:109-118` |
| The results report | **9** rows | `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:114-126` |

The results report's nine rows are **not** the protocol's five: it adds source-policy
equivalence, observer-refusal and digest-pin (all real, all tested), and **omits** the
protocol's negative-controls and claim-invariance controls — the two that are not
implemented. So the sentence is wrong about the count, wrong about what was
"declared in the protocol", and wrong about "exercised" (two of the protocol's five
were not exercised). The substance of the *executed* controls is good (§6 below); the
summary sentence is not.

### AV-22 — Two declared controls are not implemented as executable checks — **MAJOR**

* **Negative controls** (`s1_protocol.md:254-256`): "*Family A's cryptographically-false
  members (A03, A04, A06, A07, A08) must not be promoted by any contract that is claimed
  to bind the reference result.*" — **No test asserts this.** `test_s1_attribution.py`
  has no such case. The condition also holds vacuously for E0/E1/E2 ("any contract that
  is claimed to bind the reference result" excludes them by definition), so the control
  reduces to "E3 must not promote A03/A04/A06/A07/A08" — which is true in fact (E3
  promotes none of them; its only family-A promotion is under the *lenient* variant, and
  that is A05, which is crypto-true) but is nowhere asserted.
* **Claim-invariance control** (`s1_protocol.md:261-265`): the protocol **explicitly
  states it is not constructed** ("Two Stage01 certificates over byte-identical
  evidence files that differ only in `claims` are **not constructed** in this
  experiment") and substitutes an *argument* ("the claims are not read by E3 at all").
  The argument is only half right: E3's bundle has no `claims` field, so the control
  is vacuous for E3; but the **frozen Stage01 validator does read `claims`** and
  *requires* specific values (`contract_sound_stage01_validator_v2.py:54-56, 79-84`),
  so the Stage01 pair is **not** claim-invariant. Neither `test_s1_attribution.py` nor
  the runner exercises anything here. This is the clearest instance of a
  **declared-but-unimplemented control**.

### AV-23 — "a real, frozen, deployed component" overstates — **MINOR**

`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:134` — "*What they establish is a
**component-level capability gap in a real, frozen, deployed component**, demonstrated
on a real execution*". The component is real, frozen and hash-pinned, and it *is* part
of the executed historical campaign path. But no C02/C03 input was ever produced by a
deployed system, and the gap was never observed in a deployment. "Deployed" invites the
reading that the pipeline was observed to fail. The same document's §0 (lines 14-22)
and `deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:109-111` are precise; the
adjective is the risk.

### AV-24 — "frozen **production** Stage01 pair" — **MINOR**

`deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:90, 177`; also
`deliverables/NOVELTY_PRIOR_ART_MATRIX.md:139`; `deliverables/MASTER_PROGRESS_REPORT.md:72-73`.
The pair is hash-pinned, unmodified, and part of the historical executed path — so
"production" is defensible in the sense of "the campaign's production code path". It
was, however, **run locally inside this experiment** on locally constructed bundles.
The deliverable never says so.

### AV-25 — The novelty matrix quotes SET 2 numbers without naming the metric — **MINOR**

`deliverables/NOVELTY_PRIOR_ART_MATRIX.md:141-142` — "*13 → 11 → 6 → 0 false
attributions out of 25 ground-truth non-successes*". These are the post-hoc SET 2
figures. A reader of the novelty document alone cannot tell that the preregistered
metric gives a different answer (see AV-15).

### AV-26 — "strictly stronger than in-toto" in §2 vs "NOT_ESTABLISHED" for superiority in §5 — **MINOR**

`deliverables/REAL_PROVENANCE_BASELINE_COMPARISON.md:50-54` — "*The four rows where the
Stage 1 contract is **strictly stronger** than in-toto are P6, P7, P9 and the CLI-level
half of P10*". The same document's §5 (lines 103-104) marks superiority
**NOT_ESTABLISHED** and `deliverables/NOVELTY_PRIOR_ART_MATRIX.md:154-156` lists
"Product superiority over in-toto/SLSA/Sigstore" as a **MAY NOT claim**. §2's wording
is a schema-level statement, but it is phrased as superiority and sits in tension with
the two normative statements. Recommend "covers guarantee classes that in-toto's
documented schema cannot express" instead of "strictly stronger".

### AV-27 — The Objective-4 `ESTABLISHED` determination violates the determination document's own governing rule — **MAJOR**

`deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:9-12` (the rule) vs `:23` and
`:134` (the determination) vs `s1_protocol.md:353-355` (the preregistered criterion).
See AV-15. The rule says no objective may be `ESTABLISHED` on the basis of a guarantee
that was not tested; the "zero false rejections" guarantee was tested and failed under
the preregistered metric. At minimum the determination must be re-worded to
`ESTABLISHED under the post-hoc attribution ground truth; the preregistered metric's
success criterion is NOT MET (E3 FR = 19/21)`.

### AV-28 — The determination document pre-cites an audit that did not exist — **OBSERVATION**

`deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:208` cites
"`deliverables/SCIENTIFIC_VALIDITY_AUDIT.md`" as an "independent adversarial audit".
The file did not exist when the document was written (the deliverable's mtime is
13:01; the audit is the file this report writes). The citation is now accurate, but at
writing time it was a forward reference to a non-existent artefact. A reader relying on
the citation before the audit existed would have been misled.

---

## 3. Independent recomputation tables

**Method.** `/tmp/opencode/audit_recompute.py` reads **only**
`stage1_attribution/runs/results.json` and `stage1_attribution/s1_case_manifest.json`.
It does not import `s1_metrics.py` or `s1_summarize.py`; it reimplements the Wilson
interval from the textbook formula. **No repo file was written.**

### 3.1 Decision distribution (n = 27) — my numbers vs reported

| evaluator | SUCCESS | REJECT | INCONCLUSIVE | my total | matches `runs/summary.md` / `s1_summarize.py`? |
|---|---|---|---|---|---|
| `digest_only` | 15 | 7 | 5 | 27 | ✔ |
| `signed_digest_only` | 13 | 9 | 5 | 27 | ✔ |
| `signed_context_only` | 8 | 14 | 5 | 27 | ✔ |
| `full` | 2 | 20 | 5 | 27 | ✔ |
| `full_lenient` | 3 | 19 | 5 | 27 | ✔ |

**All 5 × 3 = 15 cells match. Zero discrepancies.**

### 3.2 Metric sets — my numbers vs reported

**SET 1 (preregistered, `crypto_success` ground truth) — denominators true n=21 / false n=6**

| contract | FA | Wilson | FR | Wilson | CA | CR | reported? |
|---|---|---|---|---|---|---|---|
| `digest_only` | 1/6 | [0.030,0.564] | 7/21 | [0.172,0.546] | 14/21 | 5/6 | ✔ |
| `signed_digest_only` | 1/6 | [0.030,0.564] | 9/21 | [0.245,0.635] | 12/21 | 5/6 | ✔ |
| `signed_context_only` | 1/6 | [0.030,0.564] | 14/21 | [0.454,0.828] | 7/21 | 5/6 | ✔ |
| `full` | 0/6 | [0.000,0.390] | 19/21 | [0.711,0.973] | 2/21 | 6/6 | ✔ |
| `full_lenient` | 0/6 | [0.000,0.390] | 18/21 | [0.654,0.950] | 3/21 | 6/6 | ✔ |

*All SET 1 numbers match `runs/summary.md:11-15` and
`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:97-101` exactly.* The single FA case
for E0/E1/E2 is `C03_submitted_output_not_observed` — i.e. the mislabelled case
(AV-11).

**SET 1 variant — C03 relabelled `expected_crypto_success = true` (AV-11) — denominators true n=22 / false n=5**

| contract | FA | Wilson | FR | Wilson | CA | CR |
|---|---|---|---|---|---|---|
| `digest_only` | **0/5** | [0.000,0.434] | 7/22 | [0.164,0.527] | 15/22 | 5/5 |
| `signed_digest_only` | **0/5** | [0.000,0.434] | 9/22 | [0.233,0.613] | 13/22 | 5/5 |
| `signed_context_only` | **0/5** | [0.000,0.434] | 14/22 | [0.430,0.803] | 8/22 | 5/5 |
| `full` | 0/5 | [0.000,0.434] | **20/22** | [0.722,0.975] | 2/22 | 5/5 |
| `full_lenient` | 0/5 | [0.000,0.434] | 19/22 | [0.667,0.953] | 3/22 | 5/5 |

**Under the corrected preregistered label, all four contracts have ZERO false
attributions.**

**SET 2 (attribution ground truth, `expected_decision`) — denominators success n=2 / non-success n=25**

| contract | FA | Wilson | CA | FR | Wilson | CR | reported? |
|---|---|---|---|---|---|---|---|
| `digest_only` | 13/25 | [0.335,0.700] | 2/2 | 0/2 | [0.000,0.658] | 12/25 | ✔ |
| `signed_digest_only` | 11/25 | [0.267,0.629] | 2/2 | 0/2 | [0.000,0.658] | 14/25 | ✔ |
| `signed_context_only` | 6/25 | [0.115,0.434] | 2/2 | 0/2 | [0.000,0.658] | 19/25 | ✔ |
| `full` | **0/25** | [0.000,0.133] | 2/2 | **0/2** | [0.000,0.658] | **25/25** | ✔ |
| `full_lenient` | 1/25 | [0.007,0.195] | 2/2 | 0/2 | [0.000,0.658] | 24/25 | ✔ |

*All SET 2 numbers match `runs/summary.md:28-32`,
`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:75-79` and
`deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:160-164` exactly.*

**SET 2 variant — the manifest's *third* truth column `ground_truth == "attributable"`
(success n=3: A01, A02, A05; non-success n=24)**

| contract | FA | Wilson | FR | Wilson |
|---|---|---|---|---|
| `digest_only` | 12/24 | [0.314,0.686] | 0/3 | [0.000,0.561] |
| `signed_digest_only` | 10/24 | [0.245,0.612] | 0/3 | [0.000,0.561] |
| `signed_context_only` | 5/24 | [0.092,0.405] | 0/3 | [0.000,0.561] |
| `full` | 0/24 | [0.000,0.138] | **1/3** | [0.061,0.792] |
| `full_lenient` | 0/24 | [0.000,0.138] | 0/3 | [0.000,0.561] |

Not reported anywhere; shows the frozen table's internal inconsistency (AV-12) is
material.

### 3.3 Family decomposition (SET 3) and the frozen Stage01 table

| contract | A: success attributed | A: non-success promoted | B: INCONCLUSIVE | B: REJECT | C+R: REJECT | reported? |
|---|---|---|---|---|---|---|
| `digest_only` | 2/2 | 1 (A05) | 5/5 | 0/5 | 2/14 | ✔ |
| `signed_digest_only` | 2/2 | 1 (A05) | 5/5 | 0/5 | 4/14 | ✔ |
| `signed_context_only` | 2/2 | 1 (A05) | 5/5 | 0/5 | 9/14 | ✔ |
| `full` | 2/2 | 0 | 5/5 | 0/5 | 14/14 | ✔ |
| `full_lenient` | 2/2 | 1 (A05) | 5/5 | 0/5 | 14/14 | ✔ |

*All SET 3 numbers match `runs/summary.md:45-49` and
`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:85-89` exactly.*

**Stage01 pair — 13 applicable, 14 N/A; ACCEPTED: A01, A02, C02, C03; false
attributions 2/25 (C02, C03); false rejections 0/2; positive control 2/2 → not a
strawman.** ✔ Matches `runs/summary.md:53-73`,
`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:142-156` and
`deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:160-165` exactly.

**H1's preregistered chain "E3 < E2 < E1 ≤ E0" — my evaluation:**

| metric | E0 | E1 | E2 | E3 | chain holds? |
|---|---|---|---|---|---|
| SET 1 (preregistered) | 1 | 1 | 1 | 0 | **NO** — E2 < E1 is false (1 < 1) |
| SET 1 with C03 corrected | 0 | 0 | 0 | 0 | vacuous (all equal) |
| SET 2 (post-hoc) | 13 | 11 | 6 | 0 | yes |

### 3.4 Independent re-evaluation of the archived bundles — 26/27 exact match

`/tmp/opencode/audit_reevaluate.py` re-ran the four frozen evaluators (E0, E1, E2,
E3-strict, E3-lenient) over the **archived** `work/<case>/bundle.json` for all 27
cases, reconstructing the `RunExpectation` from `results.json` (and, for C09 — whose
`checks` block is empty because `load_bundle` short-circuits on a duplicate record
kind, `s1_verification.py:87-90` — reconstructing it from the runner's deterministic
rules).

```
bundles re-evaluated : 27/27
exact match          : 26
mismatches           : 1
   R01_replay_shared_ledger: {'signed_context_only': ('ATTRIBUTED_SUCCESS','REJECT'),
                               'full': ('ATTRIBUTED_SUCCESS','REJECT'),
                               'full_lenient': ('ATTRIBUTED_SUCCESS','REJECT')}
```

R01 is a **second** evaluation against a shared replay ledger; re-evaluating it with a
fresh ledger necessarily yields the first-evaluation result. The mismatch is
fully explained and is itself a confirmation that the shared ledger did its job in the
recorded run.

**Conclusion for §3: the reported arithmetic is correct. Every headline number in
`runs/summary.md`, `runs/summary.json`, `END_TO_END_ATTRIBUTION_RESULTS.md` and
`FINAL_FOUR_OBJECTIVE_DETERMINATION.md` was reproduced exactly from the raw results by
an independent script. The problems are with the labels, the denominators' provenance,
the freeze, and the framing — not with the arithmetic.**

---

## 4. Claim-by-claim adjudication of the deliverables

Legend: **S** = supported by the evidence · **P** = partially supported / needs the
stated qualifier · **O** = overreach · **N** = not established · **D** = disclosed and
correctly bounded (no finding).

### 4.1 `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md`

| # | Line | Claim | Adjudication |
|---|---|---|---|
| 1 | 14-22 | Not an exploit / not live / not reachability / not novelty / not AI-specific; C+R are synthetic fixtures | **D** — accurate and prominently placed. |
| 2 | 26-43 | The TEO "signs what it read — never what the producer asserted"; "No link in the chain is a digest supplied by the untrusted producer" | **P** — true of the *records*; but `observation.executed_program_sha256` is a copy of the pre-exec hash, not a measurement of the executed bytes (AV-31), and the bundle's `run` block is never verified (AV-33b). |
| 3 | 33 | "the evaluator checks the two agree" (input vs stdin digest) | **O** — the check is tautological; it cannot fail (AV-30). |
| 4 | 43 | "The cryptographic predicate is not re-implemented"; the source policy is "tested for equivalence" | **S** — I verified the historical `safe_source` at `run_contract_sound_agent_pilot.py:43-54` matches the reimplementation and the test's transcription. |
| 5 | 47-52 | E0-E2 are design classes, not products | **D** — correct, and consistently applied. |
| 6 | 56 | Strict/lenient were predeclared; A05 is the only sensitive case | **S** — confirmed by my recomputation. |
| 7 | 60-65 | 27 cases, 56 inventory files, family sizes 8/5/12/2 | **S** — verified. |
| 8 | 67 | "Ground truth is recorded twice per case" | **O** — it is recorded three times, and one pair disagrees (AV-12). |
| 9 | 71-79 | The primary metric table (SET 2) | **S** arithmetically; **P** on the "primary" designation, which silently demotes the preregistered metric (AV-15). |
| 10 | 83-89 | Family decomposition | **S** — exact match. |
| 11 | 91-103 | SET 1 and its caveat | **S** as a report. But the caveat states only that SET 1 "counts E3's *correct* rejections as false rejections"; it does **not** state that the preregistered success criterion consequently **fails** (AV-15), and it inherits the C03 mislabel (AV-11). |
| 12 | 109 | H1 SUPPORTED, "13 → 11 → 6 → 0 … monotone" | **P** — true under SET 2; **fails** under the preregistered metric (AV-15), which is not stated. |
| 13 | 110 | H2 SUPPORTED, "0/2 false rejections for E3" | **P** — under SET 1, E3 FR = 19/21 (AV-15). n=2 caveat is in §8.2 for FA but not FR (AV-16). |
| 14 | 111 | H3 SUPPORTED; Stage01 "rejected both omission cases it could express" | **S** — verified (B01, B04 REJECTED). |
| 15 | 112 | H4 SUPPORTED | **S** — verified; the Stage01 pair really does ACCEPT C02 and C03. |
| 16 | 116-126 | The nine control rows | **P/O** — see §6; the "6 honest successes" row is self-contradictory (AV-20); the "nine" count is wrong (AV-21). |
| 17 | 130-132 | The C02 / C03 narratives | **S** — I verified the mechanism directly from the archived bundles (AV-35, §7). Accurate. |
| 18 | 134 | "a component-level capability gap in a real, frozen, **deployed** component" | **O** (wording only) — AV-23. |
| 19 | 138-156 | The Stage01 table and "false attributions = 2/25" | **S** / **P** — numbers exact; the 25 denominator is the post-hoc one (AV-19). |
| 20 | 160-165 | A05 is the only contract-sensitive case | **S** — verified. |
| 21 | 169-178 | The ten limitations | **S** and genuinely thorough — constructed corpus, small denominator, byte-identity, residual TOCTOU, no namespace isolation, in-memory ledger, not a PKI, scripted producer, single run, baseline asymmetry. This section is the strongest part of the document. It is **not** sufficient to cover AV-01/AV-15, which it does not mention. |
| 22 | 184 | "17 passed" | **S** — I ran it: 17 passed in 166.03 s. |
| 23 | 195-197 | "**ESTABLISHED** (on the frozen corpus, within the stated scope)" | **O** — the word "frozen" is not supported (AV-01) and the establishment rests on the post-hoc metric (AV-15, AV-27). |

### 4.2 `deliverables/REPOSITORY_AND_TRUST_BOUNDARY_MAP.md`

| # | Line | Claim | Adjudication |
|---|---|---|---|
| 1 | 38-61 | Live-path trust map, 15 objects, 6 "No" bindings | **D** — outside this audit's scope; internally consistent and cited. |
| 2 | 65-76 | The attribution claim is producer-declared; the blind validator accepted 24/24 crypto-false C0 controls | **Not audited** (Stage 0 scope). |
| 3 | 87-94 | Two finding tokens, source-level negative evidence with an explicit "not a proof of universal impossibility" qualifier | **D** — well bounded. |
| 4 | 102-111 | The structural reason the C02/C03 gap is not live-reachable | **S** — and I independently confirm it (§7). This is the key honesty statement in the package. |
| 5 | 142-147 | The six trust properties | **P** — "Freshness / anti-replay … `context_validator.ReplayState`" reads stronger than the in-memory, per-evaluation reality (AV-32/F3); "The measurement itself is frozen" is **O** (AV-01). |
| 6 | 149-162 | Integrity anchors table | **P** — the three `heb1` components are listed with "—" (no digest) while the two Stage01 components have pins; the manifest does not cover any of the five (AV-02). |
| 7 | 164-176 | The six unsatisfied trust assumptions in the live path | **D** — accurate and appropriately scoped. |

### 4.3 `deliverables/NOVELTY_PRIOR_ART_MATRIX.md`

| # | Line | Claim | Adjudication |
|---|---|---|---|
| 1 | 23-33 | Category A supported, B supported-but-occupied, C partial, **D foreclosed**, E not supported | **D** — the package's strongest and most honest section. The prior-art verdicts are outside my scope; the *internal* adjudication is disciplined. |
| 2 | 57-68 | RFC 9334's verdict is binary ⇒ the tri-state is the narrowest residual | **Not audited** (network prohibition); internally consistent and explicitly quoted. |
| 3 | 74-83 | The verified prior-art table, including the **REFUTED** "chain claim" for arXiv:2606.04990 and the **material weakening** by `llmsa` and in-toto | **D** — reporting one's own prior art as *weakening* the project's claim is exactly the right behaviour. |
| 4 | 110-130 | "The AI-specificity claim is dead" | **D** — correct, and matches the protocol's own prohibition. |
| 5 | 134-148 | The three MAY-claim items | **P** — item 1 ("the frozen Stage01 **production** pair is measured to **accept** two attribution claims whose causal chain is broken") is accurate but inherits AV-24; item 2's "13 → 11 → 6 → 0 … out of 25" inherits AV-25 (metric unnamed). |
| 6 | 149-159 | The four MAY-NOT-claim items | **D** — exactly the right list, including "Product superiority" and "Any deployed-attacker or live-campaign exploit". |
| 7 | 161-173 | Incompleteness disclosure (one full text unobtainable; 4 `[UNVERIFIED]`, 3 `[ESTIMATE]`; no duplication proof) | **D** — exemplary. |

### 4.4 `deliverables/REAL_PROVENANCE_BASELINE_COMPARISON.md`

| # | Line | Claim | Adjudication |
|---|---|---|---|
| 1 | 9-13 | The empirical in-toto comparison **has not been executed**; blocked on approval (G-1) | **D** — and the status banner is at the very top. Excellent. |
| 2 | 19-24 | Only in-toto is comparable; SLSA/cosign are NOT_COMPARABLE; RATS is not runnable | **D** — with an explicit correction of a premise in the brief. |
| 3 | 37-48 | The P1-P10 table with the `N` / `[CUSTOM-INSPECTION]` / `—` marking | **D** — the "no laundering" rule (`§3`, lines 70-72) is the right mechanism. |
| 4 | 50-54 | "The four rows where the Stage 1 contract is **strictly stronger** than in-toto" | **O** (wording) — AV-26. |
| 5 | 58-72 | Predictions P-1 and P-2, falsifiable, with the "no laundering" rule | **D** — P-1 is stated as a *product* prediction with its corpus (58-case IAR-B) named, not this phase's 27-case corpus. |
| 6 | 74-91 | The executed/not-executed table | **D** — the "NOT DONE — approval required" entries are explicit. |
| 7 | 99-107 | Objective 3: NOT_TESTED (empirical), PARTIALLY_ESTABLISHED (design), superiority NOT_ESTABLISHED, overall BLOCKED | **D** — correct and appropriately weak. |
| 8 | 118-121 | "the C02/C03 finding does not depend on in-toto at all" | **S** — correct, and important: it correctly refuses to let an unexecuted comparison contaminate the Stage 1 result. |

### 4.5 `deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md` and `MASTER_PROGRESS_REPORT.md` (not in the original scope, but they carry the strongest claims)

| # | Line | Claim | Adjudication |
|---|---|---|---|
| 1 | 9-12 | Governing rule: no objective is `ESTABLISHED` on an untested guarantee | **D** as a rule; **O** as applied (AV-27). |
| 2 | 20 | Objective 1 NOT_ESTABLISHED, "foreclosed, not merely unproven" | **D**. |
| 3 | 21, 87-111 | Objective 2 NOT_ESTABLISHED, with the three requirements separated and the synthetic nature of C02/C03 stated | **D** — this is the correct and honest treatment. |
| 4 | 22, 117-128 | Objective 3 BLOCKED_BY_RESOURCE_OR_AUTHORIZATION; superiority NOT_ESTABLISHED | **D**. |
| 5 | 23, 134, 163 | Objective 4 **ESTABLISHED**, "0/25 … 0/2" | **O** — AV-15, AV-27, AV-01. |
| 6 | 185-191 | "Freeze in force before measurement … re-verified after the run, 77 files, 0 errors" | **O** — the preflight *is* wired in and *does* pass; the "freeze" claim is not evidenced (AV-01). |
| 7 | 192-199 | "17 unit tests, all passing" + the list | **S** — I ran them: 17 passed. The listed coverage matches `test_s1_attribution.py`. |
| 8 | 200-202 | "The baseline is not a strawman — accepted 2 of 2 successes and rejected all four crypto-false honest cases" | **S** — verified. Note it says *four*; there are five crypto-false family-A members (A03, A04, A06, A07, A08) but A08 is a C0 *underdetermined* case whose predicate is false for a different reason. Minor imprecision; the substance holds. |
| 9 | 203-204 | "Nine controls declared in the protocol and exercised" | **O** — AV-21, AV-22. |
| 10 | 205-208 | "An independent recomputation … by a script that does not share code with the summariser, plus an independent adversarial audit" | **P** — the recomputation claim is now independently confirmed by me; the audit citation is a forward reference (AV-28). |
| 11 | 212-230 | The nine binding limitations | **D** — accurate, and they cover AV-16 (n=2), AV-31/TOCTOU, F3, the scripted producer, and the synthetic C family. They do **not** cover AV-01 or AV-15. |
| 12 | MASTER 42, 64-67 | "COMPLETE, executed once after freezing"; "All 27 preregistered expectations matched for E3 strict *and* E3 lenient"; "Post-run re-verification of the freeze: 77 files, 0 errors" | **S** on the 27/27 expectation match (I verified: 0 mismatches). **O** on "executed once after freezing" (AV-01). |
| 13 | MASTER 14-16, 18-20 | "**built and frozen** … **executed** it once after freezing"; "produced a source-verified negative result" | **O** on "frozen" (AV-01). The negative result on reachability is Stage 3's scope, not audited here. |

### 4.6 Overreach categories specifically checked (per the task)

| Category | Verdict |
|---|---|
| (i) reads as a **live/deployed exploit** | **No** — every deliverable has an explicit "NOT an exploit against a deployed security service" banner, and Stage 3's class (a)/(b) separation is maintained throughout. The only residual risk is the adjectives "deployed" (AV-23) and "production" (AV-24). |
| (ii) a **novel security mechanism** | **No** — the package forecloses category D itself, on quoted RFC 9334 text, and lists "A previously unknown security mechanism" as a MAY-NOT-claim. |
| (iii) **product superiority** over in-toto/SLSA/Sigstore | **No** — the empirical comparison is declared NOT EXECUTED, superiority is NOT_ESTABLISHED, and the "no laundering" rule is stated. Only §2's "strictly stronger" phrasing needs softening (AV-26). |
| (iv) an **AI-specific result** | **No** — the scripted-producer prohibition is stated in the protocol, the results, the protocol deliverable, the novelty matrix §4 and the determination. No AI-specificity claim is made anywhere. |
| (v) a **population-level rate** | **No** — "characterisation of discrimination, not a population rate" appears in the protocol (§8.10), the results (§8.1), the protocol deliverable (§9) and the determination (§212-213). No p-values anywhere in Stage 1 output. **The one thing that is missing is the symmetric statement for the *false-rejection* rate (AV-16).** |
| (vi) a **PASS on a guarantee that was not tested** | **Yes, in one place** — Objective 4's `ESTABLISHED` and the H1/H2 `SUPPORTED` verdicts are adjudicated on the post-hoc metric, while the preregistered metric was tested and yields a different answer (AV-15, AV-27). This is the one substantive overreach I find. |
| (vii) a **control that was declared but not run** | **Yes** — negative controls and claim-invariance (AV-22, AV-33), plus the control-count error (AV-21) and the "6 honest successes" row (AV-20). |

---

## 5. Threat-model probe results (F1–F5)

### F1 — Can the producer's program write to the case directory before the observer hashes it? — **WINDOW EXISTS, DISCLOSED, NOT CLOSED**

**Code.** `s1_trusted_observer.py:210` hashes the program file; `:219-227` `subprocess.run`s
it; `:237` hashes it again. The child runs with `cwd = case_dir/execution` and the
program path is `case_dir/program/candidate.py`.

**Counter-example.** A concurrent writer that replaces
`work/<case>/program/candidate.py` between line 210 and line 219 gets *its* bytes
executed while the observer signs the digest of the *old* bytes. The post-exec hash
(`:237`) catches in-place modification but not a **swap-and-restore** race: restore the
original bytes before the exec returns and both hashes agree with the original, while
different bytes ran.

**Status.** The protocol discloses exactly this (`s1_protocol.md:302-308`: "*a write in
the window between the hash and the `exec` is not excluded by hashing alone … The
window itself is not closed; a `memfd`-based execution … would close it and is listed
as a follow-up, not claimed here*"), and the results repeat it
(`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:172`).

**In-harness reality.** No such writer exists in the experiment: the producer's bytes
are written by the harness at `s1_runner.py:250-251` *before* the observer runs
(`:341-348`), and the producer role only signs a record (`:353-360`). The candidate
program itself cannot write (the static policy blocks `open(` and `os.` —
`s1_trusted_observer.py:58-67`), but that is **policy, not isolation**
(`s1_protocol.md:309-311`).

**Verdict: disclosed limitation, faithfully stated. Not closed. Not tested.**

### F2 — Can the producer influence `input_sha256`? — **NO (but join #9 is tautological)**

**Code.** `s1_trusted_observer.py:211-213` — `input_bytes = input_path.read_bytes()`;
`input_sha = sha256_bytes(input_bytes)`; `stdin_sha = sha256_bytes(input_bytes)`. The
bytes are delivered on stdin at `:224` (`input=input_bytes`).

**Counter-example sought and not found.** `input_path` is the harness-supplied frozen
instance (`s1_runner.py:343` → `prepared["instance_path"]` → `s1_case_inventory/cases/*/public_instance.json`),
and the producer role does not write it. The evaluator's expectation is computed from
the same file by the harness (`s1_runner.py:384, 587`). The producer cannot influence
the input digest in this experiment.

**However — AV-30: the advertised "join #9" cannot fail.** The evaluator's check at
`s1_attribution_evaluator.py:293-298` compares
`obs_facts["stdin_sha256"] != obs_facts["input_sha256"]` and raises
`observer-stdin-delivery-mismatch`. But both fields are `sha256_bytes(input_bytes)` of
the **same variable** (`:212-213`), so the condition is identically false. The check is
**unreachable**, and `deliverables/END_TO_END_ATTRIBUTION_PROTOCOL.md:54` advertises it
as one of the eleven joins ("*the bytes delivered were the bytes hashed*"). A join that
cannot fire is not a join; it should be removed from the join list or replaced by a
real check (e.g. hashing what the child actually read).

**Secondary limitation.** The input file is **not in the bundle**
(`s1_runner.py:268-288` — the bundle contains program_source, program_output, stdout,
stderr and the three records, but not `public_instance.json`). An independent auditor of
a bundle therefore cannot re-derive the input binding at all; it is checkable only
against the harness-side `RunExpectation`. This is defensible (the harness is the
trust anchor for the question) but should be stated.

**Verdict: producer cannot influence the input digest. Join #9 is a no-op. Input not
independently auditable from the bundle.**

### F3 — Is the replay ledger per-evaluation or durable? — **PER-EVALUATION, IN-MEMORY, ATTEMPT-KEYED (disclosed)**

**Code.** `heb1_remediation_v1/context/context_validator.py:118-137` —
`ReplayState` is a plain dataclass holding `self._uses: dict[tuple, int]`;
`record()` raises `ContextValidationError("signed context replay limit exceeded")`
when `uses >= max_uses`. `validate_signed_context` calls `replay_state.record(context)`
at `:172-173`, **after** the signature and binding checks at `:164-165`.

**Findings**

1. **Not durable, not atomic, not process-shared.** The ledger lives in one Python
   process's heap. A verifier restart loses it. Disclosed at `s1_protocol.md:312-314`
   and `deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:223-224`.
2. **Effectively per-evaluation in this experiment.** `s1_runner.py:594-601` creates a
   **fresh** `ReplayState(max_uses=1)` for each of the five evaluators per case. Only
   `R01` shares one (`:603-628`). So in the 26 normal cases the replay ledger is
   exercised but never *binds* anything.
3. **The ledger's granularity is the attempt, not the artefact.** The key is
   `_context_key(context)` = the six context fields
   (`context_validator.py:73-74, 129-134`) — `kind, domain, target_id, attempt_id,
   epoch, role`. The bundle path and content are **not** in the key. Consequence: two
   *different* bundles signed under the same attempt context collide (conservative),
   and the *same* bundle re-presented under a *different* attempt is not caught by the
   ledger (it is caught instead by the context-to-expectation binding at
   `s1_verification.py:183-191`). This is a defensible design, but the deliverables
   describe the mechanism as "Freshness / anti-replay" without specifying the
   granularity.
4. **Correct behaviour worth noting:** `record()` is reached only after the signature
   and the six-field binding verify, so a forged record does not consume a replay slot.

**Verdict: as disclosed. The one gap is the unstated granularity (attempt, not
artefact) and the fact that the ledger is per-evaluator-instance in every non-R01
case.**

### F4 — Does the evaluator verify that the program file in the bundle is the file that was *executed*, or only that digests match each other? — **ONLY THAT DIGESTS MATCH EACH OTHER**

**This is AV-31, and it is a MAJOR finding.**

**Code.** The evaluator's check is
`s1_attribution_evaluator.py:259-262` — `obs_facts.get("program_source_sha256") !=
program_digest` → `observer-program-digest-mismatch`. `program_digest` is the digest of
the bundle's `program/candidate.py` (`s1_verification.py:126`). The other side of the
comparison is the **observer's signed assertion**.

**The observer does not measure the executed bytes.** `s1_trusted_observer.py:280` —
`"executed_program_sha256": program_sha_before` — is a **literal copy** of the
pre-exec hash from `:210`. It is not an independent measurement of what the kernel
executed (no `memfd`, no `fexecve`, no `/proc` re-read, no interpreter-level identity
check). Confirmed empirically on the C02 bundle: the observer's three program-digest
fields all carry the *original* program's digest, while the file on disk carries the
swapped program's digest.

**Consequence.** The protocol's evidence-chain table row 3
(`s1_protocol.md:127`: "*Exact executed program bytes | TEO | — | observation.program_source_sha256 +
program_source_sha256_after*") **overstates**: the TEO *asserts* the identity of the
executed bytes; it does not *measure* it. Everything downstream rests on
path-identity plus the observer's honesty, with the F1 swap-and-restore race as the
residual exposure. The protocol's §8.3 discloses the *race*; it does **not** disclose
that the executed bytes are never independently observed at all — which is a stronger
and more accurate statement of the same limitation.

**Verdict: digests-match-only, and the trust anchor is the observer's assertion, not a
measurement. The protocol's table row 3 and the deliverable's "hashes the program
bytes before *and* after execution" (`deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:144`)
should say "asserts the digest of the file it executed, before and after".**

### F5 — Can the `program_output` re-derivation check be bypassed? — **NOT FOUND (no bypass yielding a false attribution)**

**Code.** `s1_attribution_evaluator.py:310-321` — if both `program_output` and
`execution_stdout` are in the index, the evaluator re-parses the captured stdout with
the same `json-last-line-v1` rule and compares the resulting object to the stored
output artifact; mismatch → `output-not-parse-of-captured-stdout` (contradiction).

**Bypasses sought, and why each fails**

| Attempted bypass | Result |
|---|---|
| Omit `program_output` from the index | The observer's `output_file_present` would still be true → `observation-bundle-mismatch` contradiction (`s1_attribution_evaluator.py:246-249`). If the observer says no output, the ladder cannot reach success: L3 needs `output_digest is not None` (`:362-369`). **Blocked.** |
| Omit `execution_stdout` from the index | `KIND_EXECUTION_STDOUT` is in `ALWAYS_REQUIRED_KINDS` (`:90-97`) → absence → INCONCLUSIVE, and L3's `bound` requires `stdout_digest is not None`. **Blocked.** |
| Replace the output file with different *bytes* but the same JSON | The byte digest differs from the observer's signed `output_file_sha256` → `observer-output-digest-mismatch` (`:266-269`). **Blocked.** |
| Replace both the output file and the stdout file consistently | The observer's signed `output_file_sha256` and `stdout_sha256` are unchanged → both digest joins fire (`:266-269`, `:277-280`). **Blocked.** (This is exactly C03, and E3 rejects it.) |
| Make the re-derivation *pass* on a mismatched pair | The re-derivation is a *semantic* (dict) comparison, so it can pass on a byte-different but semantically-equal file — but the byte-digest join then fires. The two checks are complementary, not redundant. **Blocked.** |
| Exploit the exception path | `:319-321` catches any exception and appends to `result.missing` → INCONCLUSIVE, not REJECT. This **downgrades** a contradiction to an absence; it can never *promote* a bundle to `ATTRIBUTED_SUCCESS`. **Not a bypass to success.** |

**Minor observation.** The exception path's INCONCLUSIVE downgrade is a *classification*
asymmetry (a bundle whose stdout does not end in a JSON object, but which carries a
`program_output` file, would be INCONCLUSIVE rather than REJECT). Because the metric
counts INCONCLUSIVE as a false rejection on a truth-success, this cannot inflate any
headline. In practice it is unreachable, because the observer only sets
`output_file_present = True` when the last stdout line parses as a JSON object
(`s1_trusted_observer.py:251-258`).

**Also noted:** the reference verdict's own `candidate_sha256` field is never
cross-checked by the evaluator. It is redundant given the stdout binding
(`:271-284`), so this is a completeness note, not a gap.

**Verdict: NOT FOUND — no bypass of the re-derivation check that yields a false
attribution.**

---

## 6. Control implementation check

Declared in the frozen protocol `s1_protocol.md:246-266` (5 controls), the protocol
deliverable `deliverables/END_TO_END_ATTRIBUTION_PROTOCOL.md:109-118` (8), and the
results report `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:114-126` (9 rows).

| Declared control | Declared at | Implemented? | Where | Would it fail if the guarded property broke? | Verdict |
|---|---|---|---|---|---|
| **Positive control (operational)** — A01/A02 must be `ATTRIBUTED_SUCCESS` under E3, else NOT OPERATIONAL | `s1_protocol.md:248-250` | **Partially** | Fact: E3 = 2/2 (`runs/results.json`). But **no code gates on it** — nothing in `s1_runner.py` or `s1_metrics.py` aborts or flags the report if A01/A02 fail | **No** — it is a manual assertion, not a gate | **GAP** (AV-34). The control *holds in fact*. |
| **Positive control (baseline)** — the Stage01 pair must ACCEPT ≥1 honest case, else VOID | `s1_protocol.md:251-253` | **Yes** | `test_s1_attribution.py:392-436` (`test_frozen_stage01_pair_accepts_a_clean_case`) | **Yes** — asserts `reference_verdict == "ACCEPTED"`, `validator_decision == "ACCEPT"`, `stage01_final_decision == "ACCEPTED"`. Plus the in-run fact (A01, A02 ACCEPTED) | **PASS** |
| **Negative controls** — A03/A04/A06/A07/A08 must not be promoted by any contract binding the reference result | `s1_protocol.md:254-256` | **No** | — | n/a | **DECLARED BUT UNIMPLEMENTED** (AV-22). Also vacuous for E0–E2 by its own wording. |
| **Cross-implementation check** — E3's reference verdict vs the frozen Stage01 reference verdict must agree (same frozen predicate) | `s1_protocol.md:257-260` | **Yes, partially** | `test_s1_attribution.py:109-151` compares the new verifier's verdict against `frozen.ecdsa_valid` for one ECDSA case | **Yes** — asserts `frozen_ok is True`, `out["verdict"] == "ACCEPTED"`, `out["facts"]["cryptographic_predicate"] is True`, and that the bound `stdout_sha256` matches | **PARTIAL** (AV-35b): the **ChaCha** path (`chacha_valid`, exercised by A02/A04) is never cross-checked against the frozen predicate in any test. |
| **Claim-invariance control** | `s1_protocol.md:261-265` | **No** — the protocol states it "is **not constructed**" and substitutes an argument | — | n/a | **DECLARED BUT UNIMPLEMENTED** (AV-33). The argument is also half-wrong: the frozen Stage01 validator *does* read `claims` (`contract_sound_stage01_validator_v2.py:54-56, 79-84`) and is therefore not claim-invariant. |
| **Integrity preflight** (procedure §7, listed as a control in the results report) | `s1_protocol.md:269-283`; results `:122` | **Yes** | `s1_runner.py:719-724, 763` (`preflight_then_execute`); `test_s1_attribution.py:371-389` | **Yes** — the test asserts `report.passed is False` and `report.errors` for a tampered manifest. Note the test would pass for *any* rejection reason; it does not assert the specific failure | **PASS** (though AV-01 limits what the preflight buys) |
| **Replay control** (results report row) | results `:123` | **Yes** | `test_s1_attribution.py:339-365` | **Yes** — asserts `second.decision == DECISION_REJECT` **and** `any("replay" in r for r in second.reasons)`, which requires a replay-specific reason (the first evaluation of that bundle is already a non-success, so the decision alone would not discriminate) | **PASS** — the strongest control test in the suite |
| **Missing-evidence control** (results report row) | results `:124` | **Yes** | `test_s1_attribution.py:312-336` | **Yes** — removes the observation record and the index entry, asserts `DECISION_INCONCLUSIVE` | **PASS** (covers one of the five omission kinds) |
| **Observer control** (results report row) | results `:125` | **Yes** | `test_s1_attribution.py:190-206` | **Yes** — asserts `status == "REFUSED_SOURCE_POLICY"`, `returncode is None`, `output_file_present is False` | **PASS** |
| **Source-policy equivalence** (results report row; protocol deliverable control 4) | results `:121` | **Yes** | `test_s1_attribution.py:84-103`, 7 parametrised sources | **Yes** — compares the reimplementation against a transcription for `ok` / `disallowed-import` / `disallowed-boundary` / syntax error. **I independently verified the transcription against the historical `run_contract_sound_agent_pilot.py:43-54` — it matches exactly** | **PASS** |
| **Digest-pin control** (results report row; protocol deliverable control 8) | results `:126` | **Yes** | `test_s1_attribution.py:45-53` | **Yes** — `pytest.raises(RuntimeError, match="digest changed")` | **PASS** |

**Additional control finding — AV-33b: the bundle's `run` block is never verified.**
`s1_runner.py:291-299` writes a `run` block (`target_id, attempt_id, session_id, epoch,
input_sha256, target_state_sha256, program_source_sha256`) into every bundle, but
`grep` shows **no evaluator ever reads it** — `s1_verification.py`,
`s1_attribution_evaluator.py` and `s1_baseline_evaluators.py` contain no reference to
it. All binding checks use the harness-supplied `RunExpectation` instead. The `run`
block is therefore an **unverified, unauthenticated, decorative field** that a reader
of an archived bundle could mistake for authoritative. It is harmless (it is not used
in any decision) but it should either be verified against the expectation or removed.

**Summary: 8 of 10 declared-or-tabulated controls are implemented and would fail if the
guarded property broke. 2 are declared but not implemented (negative controls,
claim-invariance). 1 (the operational positive control) is a fact but not a gate.**

---

## 7. Baseline fairness — is the Stage01 comparison a strawman?

### 7.1 The historical certificate format has no field in which C02/C03 can be expressed

**The decisive evidence — the real pilot's evidence records**
(`sp2027/analysis/run_contract_sound_stage01.py:230-233`):

```python
"agent_artifact":   {"session_id": session_id, "artifact": "candidate.py", "producer": "deterministic-stage01"},
"execution_trace":  {"session_id": session_id, "base_instance_id": base_id, "executor": "stage01-executor-v1"},
"target_effect":    {"status": target_status, "predicate": "declared-target-predicate-v1"},
"verifier_metadata":{"verifier_version": verifier_version, "implementation": "reference-verifier-v1"},
```

The harness's compat stub (`s1_stage01_compat.py:106-127`) reproduces **the same field
set and shapes**. Critically:

* `execution_trace` carries **no** program digest, no command line, no output digest —
  only `session_id`, `base_instance_id` and an executor label. The frozen validator
  checks only `trace.session_id == execution.session_id`
  (`contract_sound_stage01_validator_v2.py:67-69`) and
  `task.base_instance_id == trace.base_instance_id` (`:70-71`).
* The certificate's `agent_artifact` names a path and a digest
  (`run_contract_sound_stage01.py:258`), and the validator checks only that the
  *evidence file* digests match (`:61-66`). It never compares the credited program to
  anything that was executed.
* The certificate's `claims` block is **required** to say `PROVEN`
  (`contract_sound_stage01_validator_v2.py:81-84`), so the validator validates the
  claim against itself.

**Therefore: the Stage01 pair was NOT handicapped.** It is not "the right answer given
a doctored input"; it is "a contract that has no way to state the question". The
harness did not remove any binding the real path produces — the real path produces
none either.

### 7.2 The C02 / C03 inputs are synthetic and mutually inconsistent

* **C02.** The observer executed P1 (the correct solver); the bundle then presents
  P2 (the `d = 0` program) as the credited artefact, re-signed by the producer, with
  the *unchanged* correct output O1 and a reference verdict over O1. The Stage01
  certificate declares `agent_artifact.sha256 = 2d4363f0…` (P2, verified on disk),
  `claims.artifact_authorship = "PROVEN"`, `claims.execution_identity = "PROVEN"`,
  `claims.attribution = "PROVEN"` — for a program the observer signed as
  `fd9b69cc…` (P1, the one actually run).
* **C03.** The observer executed the `d = 0` program and captured a *wrong* output;
  the bundle presents a *correct* output obtained from a different run, with the
  bundle digests refreshed and a fresh ACCEPTED reference verdict recomputed over the
  scratch stdout.

In both cases the Stage01 pair is handed a certificate asserting a program→output
relation that is **false and self-inconsistent**. A live deployment never produces
such a certificate: the certificate is assembled in-process from the very artefacts the
harness just produced
(`deliverables/REPOSITORY_AND_TRUST_BOUNDARY_MAP.md:102-111`;
`deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:89`). Stage 3's structural
argument is correct.

### 7.3 Plain answer to the question

> **The C02/C03 result is (b) a component capability gap only.**

**Justification.**

1. It is **not (a) a live vulnerability.** No live pipeline, deployed or otherwise,
   produced a C02- or C03-shaped certificate; Stage 3 established
   `NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED` (0/14 candidate ingresses pass the
   owner-and-authorisation test) and the certificate is assembled in-process from
   freshly produced artefacts, so the two artefacts are not separable at the point of
   certification. The Stage01 ACCEPT is a **counterfactual robustness measurement**:
   "if this class of inconsistency ever arose, the Stage01 contract could not detect
   it." That is a real and useful result, and it is exactly what the deliverables
   claim — but the wording "deployed component" (AV-23) should be softened to make
   clear that no deployed system was observed to fail.
2. It **is** (b), and the claim is *fair* because of §7.1: the Stage01 pair is not
   given a doctored or truncated input relative to what the real path produces. Its
   contract has no field for the relation in question. The gap is a **contract-design
   gap in the Stage01 certificate schema and blind validator**, demonstrated on a real
   execution with real frozen, hash-pinned components.
3. It is **not (c) something else** — it is not a strawman (§7.1), not an artefact of
   the harness's certificate builder (§7.1 shows the builder faithfully reproduces the
   historical shape), and not a mismeasurement (I re-evaluated the archived C02/C03
   bundles; the frozen pair's ACCEPT reproduces exactly).

### 7.4 Three fairness caveats to disclose

* **AV-37 — two of the thirteen Stage01 rows are not frozen-component verdicts.**
  For A06 and A07 the harness short-circuits with
  `ERROR_NO_CANDIDATE_ARTIFACT` **before invoking the pair**
  (`s1_runner.py:669-676`) and records `stage01_final_decision = "REJECTED"` as its
  own decision. The tables present these identically to genuine frozen verdicts
  (`runs/summary.md:62-63`; `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:146-147`).
  This does not flatter or penalise the baseline (a real deployment would also produce
  no candidate artefact), but the provenance of the verdict should be stated.
* **AV-38 — the compat stub does not reproduce the historical field *values*.**
  `s1_stage01_compat.py:109` writes `"producer": "model-authored"` where the real
  pilot writes `"producer": "deterministic-stage01"`; `:118` writes
  `"independent-task-cryptographic-predicate-v1"` vs `"declared-target-predicate-v1"`;
  `:122` writes `"stage01-reference-v1"` vs `"reference-verifier-v1"`; `:114` writes
  `"contract-sound-sandbox-v1"` vs `"stage01-executor-v1"`. **None of these is checked
  by the frozen validator**, so there is no metric impact — but `"model-authored"` is a
  misdescription in a package that elsewhere insists the producer arm is *scripted*,
  and none of this is in the deviations log.
* **AV-39 — the baseline is compared on 13 of 27 cases.** The 14 N/A cases are counted
  in neither direction, which is the correct treatment (a functionality mismatch is
  not a security failure — `s1_protocol.md:238-242`), and is stated. But it means the
  "2/25" figure has an effective denominator of **13 applicable cases**, not 25:
  Stage01's false-attribution *rate* on its applicable subset is 2/13 (15.4 %), not
  2/25 (8.0 %). The 2/25 framing is arithmetically the same two cases but the
  denominator is a *hypothetical* corpus-wide denominator that the baseline was never
  tested on.

---

## 8. What I could NOT verify, and why

| # | Item | Why not |
|---|---|---|
| 1 | **Whether the integrity manifest existed, in what form, and what it hashed at the moment of the confirmatory run** | No pre-run copy survives; the whole phase is untracked in git; the manifest is regenerable and its mtime is post-run (AV-01). The *current* manifest verifies (77 files, 0 errors) and is byte-identical to `build_manifest()` over the current tree — but that is precisely what makes it uninformative about the past. |
| 2 | **The exploratory pre-freeze run's actual decisions and code state** | Deleted by `rm -rf work runs`; the exploratory code was superseded. I verified the transcribed table (`s1_deviations.md:145-173`) against the confirmatory run and found it faithful apart from AV-08 — but the transcription itself is unfalsifiable. |
| 3 | **Whether the `heb1_remediation_v1` components changed between the freeze and the run** | Not covered by the manifest, not digest-pinned, not in git. Only mtimes (2026-10-19 20:01–20:16, i.e. the day before the run) are available; they are consistent with no change but do not prove it. |
| 4 | **Whether the private keys in `/tmp/acts_s1_keystore` are the ones used in the confirmatory run** | The keystore is outside the repository. Strong circumstantial evidence: the on-disk `trust/public_bundle.json` key ids match `trust/KEY_CUSTODY.json` and the archived bundles' signatures verify against the public bundle (my re-evaluation of all 27 archived bundles succeeded, which requires the public keys to match the signing keys). There is no timestamped attestation of key generation or of the keystore's use. |
| 5 | **Whether a re-run would reproduce the results bit-for-bit** | No. The observer uses `secrets.token_hex(32)` for `observer_nonce` (`s1_trusted_observer.py:173, 296`) and wall-clock timestamps, so the signed records differ on every run. The *decisions* would be the same (I re-derived them from the archived bundles). The raw `results.json` is therefore not byte-reproducible, and the deliverables do not claim it is — but `runs/results.json` is the "raw evidence" and it has no independent anchor. |
| 6 | **Whether the TOCTOU window (F1) is exploitable in practice** | I did not attempt an attack run. I established the window's existence and the absence of a measurement of the executed bytes (AV-31); exploiting it would require a concurrent writer, which the experiment does not model. |
| 7 | **The Stage 0 / Stage 2 / Stage 3 / Stage 4 substantive claims** | Out of this audit's scope and, for the network-dependent parts, impossible here: I did not re-fetch RFC 9334, the arXiv papers, the in-toto/SLSA/cosign documentation, or re-derive the H1-R3 statistics, the 58-case IAR-B corpus, the 14 candidate ingresses, or the 72/72 campaign. I adjudicated those deliverables on the adequacy of their internal reasoning and their scope discipline, not on their factual accuracy. |
| 8 | **The 24/24 C0 acceptance claim and the 72/72 campaign** | `deliverables/REPOSITORY_AND_TRUST_BOUNDARY_MAP.md:73-76` depends on
   `AGENT_PILOT_RESULTS_SUMMARY.json`, which I did not locate or verify. |
| 9 | **Whether `s1_metrics.py` and `s1_summarize.py` agree in all outputs** | I ran both; they agree on every number they print. `s1_summarize.py` prints only SET-1-style figures and the per-case table; `s1_metrics.py` prints SET 1/2/3 and the Stage01 table. `s1_metrics.py` is the one that wrote `runs/summary.md` / `runs/summary.json`. There is no automated cross-check between the two. |

---

## 9. Minimum corrections I would require before publication

Ranked. **Blocking** items must be fixed; **Required** items must be fixed or the
corresponding claim withdrawn; **Recommended** items are quality.

| Rank | ID | Required action |
|---|---|---|
| **1** | **AV-01** | **BLOCKING.** Withdraw or substantially qualify every "frozen", "confirmatory", "executed once after freezing", "verified before AND after the run" and "the measurement itself is frozen" claim (`END_TO_END_ATTRIBUTION_PROTOCOL.md:3`; `FINAL_FOUR_OBJECTIVE_DETERMINATION.md:185-191`; `MASTER_PROGRESS_REPORT.md:14-16, 42, 64-67`; `REPOSITORY_AND_TRUST_BOUNDARY_MAP.md:147`; `s1_protocol.md:6-9`). Replace with the accurate statement: *"the run was gated by a fail-closed preflight over a manifest hashing the tree as it then stood; the tree state at run time cannot be independently verified because the manifest is regenerable and the phase is not under version control."* Then **fix the mechanism**: commit the phase (or at least the manifest and the protocol) to git, publish the pre-run manifest's SHA-256 externally, and make `s1_freeze.py` refuse to overwrite an existing manifest without an explicit `--force` plus a recorded prior digest. |
| **2** | **AV-11** | **BLOCKING.** Correct `expected_crypto_success` for `C03_submitted_output_not_observed` to `true` (it is contradicted by the bundle's own signed verdict and by the case's own notes), add a deviations-log entry, and **republish SET 1**. Note the consequence: with the corrected label, **all four contracts have 0 false attributions under the preregistered metric** (0/5), so the preregistered metric no longer separates the contracts. |
| **3** | **AV-15 / AV-27** | **BLOCKING.** State in the results report and the determination that the **preregistered** Objective-4 success criterion is **NOT MET** under the preregistered metric (E3 FR = 19/21, and — with AV-02 corrected — FA = 0 for all contracts), that **H1's preregistered chain fails** under it (E2 < E1 is false: 1 < 1), and that **H2 is contradicted** by it. Re-word the Objective-4 determination to `ESTABLISHED under the post-hoc attribution ground truth; the preregistered success criterion is NOT MET` — or downgrade it. Do not leave SET 1 in a sub-section while §4.1 and §10 carry the SET 2 numbers unqualified. |
| **4** | **AV-07** | **REQUIRED.** Either implement the guard D-02 claims (`s1_runner.py:664-668` must raise if the file it intends to remove is still present) or delete the claim from the deviations log. A deviations log that asserts a non-existent safeguard is worse than one that admits a gap. |
| **5** | **AV-02** | **REQUIRED.** Add the three `heb1_remediation_v1` components to `s1_freeze.py:COMPONENTS` and pin their digests in `s1_common.py` alongside the two existing pins, with a test in the style of `test_s1_attribution.py:45-53`. |
| **6** | **AV-22 / AV-21** | **REQUIRED.** Implement the negative-control and claim-invariance controls as executable tests, **or** state in the protocol deliverable and the determination that they were not exercised, and correct the control count everywhere (5 / 8 / 9 → one number). Correct `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:118` ("6 honest successes" → 2). |
| **7** | **AV-03** | **REQUIRED.** Add `s1_metrics.py` to the deviations log (D-08) and to the freeze — noting that the freeze of a post-hoc script cannot restore confirmatory status, only make the change auditable. |
| **8** | **AV-13 / AV-14** | **REQUIRED.** Fix `s1_runner.py:702-703` to report the verdict actually present in the bundle, and add `full_lenient` to `EVALUATOR_NAMES`. Re-emit `runs/results.json`. |
| **9** | **AV-31** | **REQUIRED.** Re-word `s1_protocol.md:127` and
   `deliverables/FINAL_FOUR_OBJECTIVE_DETERMINATION.md:144` to say the observer *asserts*
   the digest of the file it executed (before and after) rather than implying it
   *records the exact executed bytes*, and state plainly that the executed bytes are
   never independently observed. If the `memfd` observer in the sibling tree can be
   adopted, adopt it and close F1 at the same time. |
| **10** | **AV-12 / AV-30** | **REQUIRED.** Reconcile the three ground-truth columns in the frozen case table (or delete the redundant `ground_truth` column) and correct "recorded twice" in `END_TO_END_ATTRIBUTION_RESULTS.md:67` and
   `END_TO_END_ATTRIBUTION_PROTOCOL.md:99`. Remove the tautological "join #9"
   (`stdin_sha256 == input_sha256`, `s1_trusted_observer.py:212-213`) from the join list
   at `END_TO_END_ATTRIBUTION_PROTOCOL.md:54`, or replace it with a check that can fire. |
| **11** | **AV-16 / AV-19 / AV-18** | **REQUIRED.** Extend the §8 "small denominator" caveat to the false-rejection rate (Wilson upper bound 0.658) and state that SET 2's oracle is the frozen expectation table. Fix the `runs/summary.md:43` column header. |
| **12** | **AV-23 / AV-24 / AV-25 / AV-26 / AV-28** | **RECOMMENDED.** Replace "deployed component" with "component of the executed historical campaign path, run locally here"; add "run locally in this experiment" where "production Stage01 pair" appears; name the metric set wherever "13 → 11 → 6 → 0" appears; soften
   `REAL_PROVENANCE_BASELINE_COMPARISON.md:50-54`; and remove or date the forward
   reference to the audit at `FINAL_FOUR_OBJECTIVE_DETERMINATION.md:208`. |
| **13** | **AV-33b / AV-37 / AV-38 / AV-39** | **RECOMMENDED.** Either verify the bundle's `run` block against the expectation or remove it; mark the A06/A07 Stage01 rows as harness-attributed; align the compat stub's field values with the historical pilot (especially `"producer": "model-authored"` → `"deterministic-stage01"`); and state Stage01's effective denominator as 13 applicable cases alongside the 2/25 figure. |
| **14** | **AV-05 / AV-08 / AV-09 / AV-10 / AV-35b** | **RECOMMENDED.** Extend the manifest to cover the evaluated bundles; correct D-07's summary sentence to name both differences; preserve the exploratory code state (e.g. under `s1_case_inventory/exploratory/`) so the D-07 transcription becomes falsifiable; state D-01's action as covering the baselines too; add a ChaCha predicate cross-check to the test suite. |

---

## Appendix A — Independent verification log (commands run by this audit)

```
sha256sum sp2027/analysis/RESULTS_LOCK.json sp2027/analysis/RESULTS_LOCK_H1PC.json \
          sp2027/paper/main.tex sp2027/paper/main.pdf
  -> 4b152f18…  8221cb86…  51f97748…  fd9a5889…   ALL FOUR MATCH

cd .../stage1_attribution && python3 s1_freeze.py --verify
  -> {"checked_files": 77, "errors": [], "passed": true}   exit 0

cd .../stage1_attribution && python3 -c "import s1_freeze, json; \
  print(s1_freeze.build_manifest() == json.load(open('s1_integrity_manifest.json')))"
  -> True          <-- AV-01: the manifest is exactly the current tree, hashed

cd .../stage1_attribution && python3 -m pytest -p no:cacheprovider -q test_s1_attribution.py
  -> 17 passed in 166.03s

python3 /tmp/opencode/audit_recompute.py
  -> every reported number reproduced exactly (see §3)

python3 /tmp/opencode/audit_reevaluate.py
  -> 26/27 archived bundles re-evaluate to the recorded decisions exactly;
     R01 differs only because it is a second evaluation against a shared ledger

stat -c '%y %n' <freeze chain>
  -> s1_integrity_manifest.json 11:45:14  >  runs/results.json 11:29:39   <-- AV-01

git ls-files sp2027/analysis/acts_next_phase_20261019/   -> 0 files
git status --porcelain  ->  ?? sp2027/analysis/acts_next_phase_20261019/
```

No repository file was modified by this audit. The only file written is this report.
