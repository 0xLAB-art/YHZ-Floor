# TOEEA-1 — Deviations Log

**Experiment:** `TOEEA-1` (Stage 1 end-to-end attribution)
**Tree:** `sp2027/analysis/acts_next_phase_20261019/stage1_attribution/`
**Log opened:** 2026-10-20, before the confirmatory run.

Every deviation is recorded here with: what was expected, what happened, why,
whether it could have changed a reported metric, and what was done. Nothing in
this log may be silently removed.

---

## Section A — Pre-confirmatory deviations (exploratory phase)

The first 27-case sweep was executed **before** this protocol and the integrity
manifest existed. It is therefore an **EXPLORATORY** run, not a confirmatory
one, and it is reported separately from the confirmatory pass. Four deviations
were found in it and were fixed before the freeze.

### D-01 — `R01` lenient contract was not wired to the shared replay ledger
* **Expected:** `s1_cases.py` declares `R01_replay_shared_ledger` to be
  `REJECT` under **both** the strict and the lenient contract.
* **Observed (exploratory):** strict ⇒ `REJECT` (correct); lenient ⇒
  `ATTRIBUTED_SUCCESS` (unexpected).
* **Cause:** implementation gap, not a scientific result. In `s1_runner.py` the
  shared-ledger re-evaluation was applied to `decisions["full"]` and to the
  three baselines, but not to `decisions["full_lenient"]`, which therefore
  retained the *first* (non-shared-ledger) evaluation and never saw the
  consumed replay slot.
* **Could it have changed a reported metric?** Yes — it produced one
  apparently unexpected case-level outcome. It does **not** change any metric
  *definition*, threshold or denominator.
* **Action taken:** the lenient variant now consumes the same shared ledger
  (second evaluation against one already-consumed `ReplayState`). This makes
  the implementation match the preregistration; it is a **wiring fix, not a
  metric change**. Recorded in `s1_runner.py` with a pointer to this log.
* **Disclosure:** the exploratory pass is reported alongside the confirmatory
  pass, and the confirmatory pass is stated to have (or not have) reproduced
  the exploratory outcome.

### D-02 — the B01 Stage01 mutation deleted a non-existent path
* **Expected:** the B01 Stage01 analogue ("missing execution trace") should
  exercise the frozen validator with a *missing declared evidence file*, which
  the frozen validator rejects with `missing-evidence`
  (`contract_sound_stage01_validator_v2.py:61-64`).
* **Observed (exploratory):** the frozen Stage01 pair returned `ACCEPTED` for
  B01.
* **Cause:** path-level harness bug. `s1_stage01_compat.build_stage01_certificate`
  appends its own `stage01` component to the directory it is given, so the
  evidence files were written to `case_dir/stage01/stage01/…`, while the
  runner's B01 mutation deleted `case_dir/stage01/execution_trace.json`
  (`unlink(missing_ok=True)` → a silent no-op). The frozen validator was
  therefore never actually exercised with a missing trace.
* **Could it have changed a reported metric?** Yes — it produced a spurious
  `ACCEPTED` in the Stage01 column for B01. The E0–E3 columns were unaffected.
* **Action taken:** the runner now passes `case_dir` (not `case_dir/"stage01"`)
  to `build_stage01_certificate`, so the evidence lands in `case_dir/stage01/`
  — the same directory the mutations delete from. A guard was added so that a
  Stage01 analogue whose mutation is supposed to remove a file **fails loudly**
  if the file it intended to remove is still present.
* **Disclosure:** the exploratory Stage01 column for B01 is void; only the
  confirmatory value is reported.

### D-03 — Stage01 certificate builder crashed on the B04 analogue
* **Expected:** B04 ("missing program source file") has a Stage01 analogue in
  which the declared `agent_artifact` file is absent.
* **Observed (exploratory):** `build_stage01_certificate` raised
  `FileNotFoundError` because it called `sha256_file()` on the deliberately
  deleted program.
* **Cause:** the builder assumed the credited program always exists.
* **Could it have changed a reported metric?** No — it aborted the B04 case
  before any measurement.
* **Action taken:** `s1_stage01_compat._sha256_or_absent(path)` returns the
  real digest when the file exists and a deterministic `"0" * 64` absent marker
  otherwise, so the frozen validator observes a *missing declared artifact*
  (the faithful analogue) instead of the harness crashing. The historical
  certificate still declares the artifact it expected.

### D-04 — summariser key map (tooling only)
* `s1_summarize.py`'s `counts()` built the key `success` but indexed it with
  `decision.lower()`, which yields `attributed_success` → `KeyError`. Fixed by
  an explicit decision→key map.
* **Effect on results:** none. The summariser is a pure function of
  `runs/results.json`; it performs no measurement.

### D-05 — key custody location (environment limitation, disclosed before the freeze)
* The repository filesystem is `fuseblk`, which reports every file as mode
  `0777` and ignores `chmod`. The vetted
  `protected_signing.load_private_key` **correctly refuses** to read a key
  whose mode bits are not `0600`, so a key stored in-tree could not be used
  without weakening a vetted check.
* **Action taken:** the three private keys are generated fresh and stored
  outside the repository (`/tmp/acts_s1_keystore`, or `$ACTS_S1_KEYSTORE` when
  set), with `0700` role directories and `0600` key files. Only the **public**
  bundle and the custody record live in the repository.
* **Consequence:** the private key material is not inside the frozen tree, so
  the freeze manifest covers the *public* trust material and the custody
  record, not the private keys. This is disclosed as a deviation from the
  ideal "freeze covers the trust root" and is consistent with the fact that
  private keys must never be frozen into a repository.

---

## Section B — During the confirmatory run

*(empty — no deviation has been recorded during the confirmatory pass.)*

---

## Section C — Post-hoc analysis notes

### D-06 — a second metric set (SET 2) added after the confirmatory run

The preregistered §5 metric (SET 1) measures false attribution against
`expected_crypto_success`, i.e. against the *cryptographic predicate* on the
presented output. After the confirmatory run it became clear that this ground
truth is **not** the same question as "was this bundle correctly attributed?":
for the contradiction family the predicate is true *by construction* (the
contradiction lies elsewhere — the credited program was not the executed one,
the output was never observed, the signature was tampered), while the correct
decision for those cases is REJECT. SET 1 therefore counts E3's **correct**
rejections of the contradiction family as "false rejections".

SET 2 was therefore added as a **post-hoc** metric whose ground truth is the
frozen case table's `expected_decision` (a bundle is a success iff the frozen
table says so). It is reported alongside, not instead of, the preregistered
metric. No threshold, no decision rule, no case expectation and no evaluator
was changed. Both sets are reported in `runs/summary.md` and
`runs/summary.json`, and SET 1's caveat is stated in the results report.

### D-07 — the exploratory pass overwrote the confirmatory raw results

The exploratory 27-case sweep (run before the freeze manifest existed) wrote
to `runs/results.json`, the same path the confirmatory pass uses. The
confirmatory pass was executed after the freeze with `rm -rf work runs`, so
`runs/results.json` now contains **only** the confirmatory pass. The
exploratory decision table was transcribed into the table below at the time it
was observed and is retained here as the pre-freeze record; it is not
reproducible from the current tree because the exploratory code state was
superseded by the frozen code state. The two tables agree on every case
except `R01` under the lenient contract, which is deviation D-01.

#### Exploratory (pre-freeze) decision table

| case | E0 | E1 | E2 | E3 strict | E3 lenient | expected | Stage01 |
|---|---|---|---|---|---|---|---|
| A01_ecdsa_correct | SUCCESS | SUCCESS | SUCCESS | SUCCESS | SUCCESS | SUCCESS | ACCEPTED |
| A02_chacha_correct | SUCCESS | SUCCESS | SUCCESS | SUCCESS | SUCCESS | SUCCESS | ACCEPTED |
| A03_ecdsa_wrong_answer | REJECT | REJECT | REJECT | REJECT | REJECT | REJECT | REJECTED |
| A04_chacha_wrong_answer | REJECT | REJECT | REJECT | REJECT | REJECT | REJECT | REJECTED |
| A05_nonzero_exit_valid_output | SUCCESS | SUCCESS | SUCCESS | REJECT | SUCCESS | REJECT/SUCCESS | REJECTED |
| A06_malformed_stdout | REJECT | REJECT | REJECT | REJECT | REJECT | REJECT | REJECTED |
| A07_empty_stdout | REJECT | REJECT | REJECT | REJECT | REJECT | REJECT | REJECTED |
| A08_underdetermined_c0 | REJECT | REJECT | REJECT | REJECT | REJECT | REJECT | REJECTED |
| B01_missing_observation | INCONCL | INCONCL | INCONCL | INCONCL | INCONCL | INCONCLUSIVE | ACCEPTED (D-02) |
| B02_missing_reference_verdict | INCONCL | INCONCL | INCONCL | INCONCL | INCONCL | INCONCLUSIVE | N/A |
| B03_missing_artifact_record | INCONCL | INCONCL | INCONCL | INCONCL | INCONCL | INCONCLUSIVE | N/A |
| B04_missing_program_source_file | INCONCL | INCONCL | INCONCL | INCONCL | INCONCL | INCONCLUSIVE | REJECTED |
| B05_missing_stdout_entry | INCONCL | INCONCL | INCONCL | INCONCL | INCONCL | INCONCLUSIVE | N/A |
| C01_producer_digest_mismatch | SUCCESS | SUCCESS | SUCCESS | REJECT | REJECT | REJECT | REJECTED |
| C02_credited_program_not_executed | SUCCESS | SUCCESS | SUCCESS | REJECT | REJECT | REJECT | ACCEPTED |
| C03_submitted_output_not_observed | SUCCESS | SUCCESS | SUCCESS | REJECT | REJECT | REJECT | ACCEPTED |
| C04_context_attempt_conflict | SUCCESS | SUCCESS | REJECT | REJECT | REJECT | REJECT | N/A |
| C05_target_substitution | SUCCESS | SUCCESS | SUCCESS | REJECT | REJECT | REJECT | N/A |
| C06_stale_epoch | SUCCESS | SUCCESS | REJECT | REJECT | REJECT | REJECT | N/A |
| C07_tampered_signature | SUCCESS | REJECT | REJECT | REJECT | REJECT | REJECT | N/A |
| C08_unauthorized_signer | SUCCESS | REJECT | REJECT | REJECT | REJECT | REJECT | N/A |
| C09_conflicting_duplicate_record | REJECT | REJECT | REJECT | REJECT | REJECT | REJECT | N/A |
| C10_stale_bundle_digest | REJECT | REJECT | REJECT | REJECT | REJECT | REJECT | N/A |
| C11_stale_attempt | SUCCESS | SUCCESS | REJECT | REJECT | REJECT | REJECT | N/A |
| C12_observation_output_absent_from_bundle | SUCCESS | SUCCESS | SUCCESS | REJECT | REJECT | REJECT | N/A |
| R01_replay_shared_ledger | SUCCESS | SUCCESS | REJECT | REJECT | SUCCESS (D-01) | REJECT | N/A |
| R02_prior_attempt_observation_replayed | SUCCESS | SUCCESS | REJECT | REJECT | REJECT | REJECT | N/A |

---

## Section D — Standing prohibitions observed in this experiment

* No model / provider call was made. The producer arm is scripted.
* No network request was made to any third party. No package was installed.
* No historical file was modified, reset, cleaned, amended, or committed.
* The four protected artefacts were hash-verified before and after the work.
* No metric, threshold, denominator, decision rule or case expectation was
  changed after the confirmatory run began.
