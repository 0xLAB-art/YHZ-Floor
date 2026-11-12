# Experiment B — Final Report

**Independent Adversarial Replication, Authenticated Provenance, and Historical Real-Defect Validation**

Date: 2026-10-19. Scope: Experiment B of the ACTS-Attack novelty-upgrade program,
governed by `EXPERIMENT_B_PROTOCOL.md` (design frozen before execution).
Status: **complete**. Everything in this report is offline (`$0` marginal spend;
no model or provider calls). No manuscript files were touched; nothing in this
repository has been committed. Experiment A (Freebuff) ran in parallel and was
not interfered with. HEB-1, IAR-A, H1, R0/R1, and P010 were not reopened; only
read-only archival inspection of historical records was performed, as the
protocol mandates.

This report answers the five protocol questions (§2 of the protocol) directly,
cites the authoritative per-part reports, records negative results and
deviations, and lists exact commands, files, and SHA-256 hashes.

---

## 1. Determination (executive summary)

**Overall: a mixed result — negative on novelty, positive on measurement.**

- **HEB-1 did not reveal a genuinely new failure mechanism.** The escaped
  pattern (cross-boundary composition survives hash/schema integrity) is a
  known provenance gap: composition validity is not implied by record
  authenticity. The principle is anticipated by RFC 9334/RATS, in-toto,
  TRAP/ReplayBench, and the `evidence.*` family. The earlier "genuinely new
  finding" claim was withdrawn in external review before this experiment
  (`HEB1_ADJUDICATION_RESPONSE_20261019.md`); Experiment B's job was to test —
  not defend — that withdrawal, and it confirms it.
- **Claim-specific verification adds a measurable, replicated benefit** in the
  tested synthetic setting. Signatures alone (V3-sig) still promote every
  inadmissible-but-individually-authentic composition to level 6; joins alone
  (V2) still accept forged-signature cases and false-reject honest partial
  claims; signatures + cross-record joins (V3-full) promoted **0** across both
  independently constructed test sets and accepted every honest claim at its
  adjudicated level (levels 1–5 included).
- **Historical real-defect validation found genuine evaluator-boundary
  failures — of the observation-validity class, not the false-promotion
  class.** The `free_v2` campaign (72 sessions) was rendered unusable by two
  raw-recomputable defects: a serialization crash that suppressed the
  reference verifier on all 72 sessions, and a source-qualification policy
  that contradicted the campaign's own declared interface on 72/72
  candidates. No inspected historical record contains a false promotion of
  unsupported attribution. This is reported as an honest negative for the
  historical arm of the mechanism question.
- **Nothing here is a defensible major (novel-mechanism) result.** The
  defensible contribution of this line is an **empirical measurement**:
  quantified false-promotability of composition-blind and authenticity-blind
  evaluator designs in AI-authored cryptographic-exploit evaluation, plus a
  first-class treatment of honest partial-claim acceptance. No paper
  integration or novelty-score inflation was performed or is authorized.

Numerical headline (all three passes; full tables in §3–§5):

| Set | n | V2 level-6 FP | V3-sig level-6 FP | V3-full level-6 FP | V2 false rejects | V3 false rejects |
|---|---|---|---|---|---|---|
| HEB-1 held-out | 64 | 0/36 attack | — | — | — | — |
| IAR-B dev | 54 | 16 | 24 | 0 | 10 | 0 |
| IAR-B held-out | 58 | 16 | 28 | 0 | 10 | 0 |
| IAR-C preserved | 44 | 10/28 | 14/28 | 0/28 | 14/16 | 0 |

---

## 2. Direct answers to the protocol questions

### A. Does the HEB-1/IAR-A composition failure survive a principled
authenticated provenance baseline (Ed25519 records + trusted anchor) and
cross-record binding?

**No for the full baseline (signatures + joins); yes for the signature half
alone.** V3-full — byte-frozen before its passes — produced 0 level-6 false
promotions and 0 overclaims on IAR-B dev (n=54), IAR-B held-out (n=58,
single blind pass after freeze), and IAR-C (n=44, independently constructed).
V3-sig (signatures, no joins) promoted every composition whose records were
individually authentic: 24 (dev) / 28 (held-out) / 14 (IAR-C, attack n=28)
level-6 false promotions. Authenticity of individual records does not imply
admissibility of their composition; only claim-specific joins closed the gap
in this design space. This replicates the HEB-1 finding structurally (the
failure moves from "no signatures" to "signatures without binding") rather
than eliminating the underlying lesson.

### B. Which attacker-capability class is required for the Stage01 (V2)
weakness to survive?

With the real frozen V2 (joins, no signature checks) exercised in IAR-B and
IAR-C:

- **C1 (certificate re-issuance + re-hash from authentic records) suffices**
  for the splice/relabel/stale-instance/split-half families and the
  foreign-authentic families: V2 accepted none of the splice families in
  IAR-C (S4–S6 rejected) but **promoted the forged-signature families**
  (S7, S9, S10, S11, S12 ×2 = 10 level-6 FP) because it never verifies
  provenance at all — the accepted records need not even be authentic.
- **C2 (unsigned metadata rewrite)** is what IAR-A already demonstrated
  against V2 (`execution-session-binding` catches only the session-ID
  mismatch form; relabeling passes because records are unsigned).
- Against **V3-sig**, C1 alone is sufficient: all 14 IAR-C V3-sig promotions
  (S4, S5, S6, S7, S8, S11, S14) reference records that are individually
  signed or unsigned-metadata-dependent, and none required forged signatures.
- C3 (signature forgery / key compromise) was never used to demonstrate
  anything, in accordance with the protocol.

### C. Can claim-specific validation preserve legitimate lower-level findings
(levels 1–5) without unsupported promotion to level 6, and without false
rejection of honest lower claims?

**Yes in the tested setting, and this is the strongest positive result of
Experiment B.**

- IAR-B: V3-full accepted H0 at 6 and every honest partial H7 case at exactly
  its requested/adjudicated level k=1..5, with **0 false rejects** and 0
  level-6 emissions above supported, on both dev and held-out passes. V2
  false-rejected all 10 honest partial-evidence cases (it accepts only fully
  evidenced bundles).
- IAR-C (independent construction): V3-full accepted all 16
  honest-within-evidence cases (S1, S2, S3, S13 k=1..5 at exactly the
  adjudicated levels) with 0 false rejects and 0 overclaims; V2 rejected
  14/16 (accepted only the 2 fully-evidenced S1 cases); V3-sig also accepted
  16/16 but overclaimed to level 6 on 14/28 attack cases.
- Honest partial-claim acceptance is treated as a first-class metric (a
  validator that rejects all partial evidence is not a correct
  claim-specific evaluator). Both the raw outcomes and the denominators are
  preserved; see §4–§5 and the per-part reports.

### D. Are any observed errors genuinely novel relative to strong prior art
(RFC 9334/RATS, in-toto, TRAP/ReplayBench, evidence.* family)?

**No.** No observed error is novel relative to the listed prior art; the
composition-vs-authenticity separation is an established principle (this
matches the HEB-1 external-review disposition in
`HEB1_ADJUDICATION_RESPONSE_20261019.md`). Experiment B adds no new binding
mechanism and makes no such claim. What is specific to this line of work is
the measured object: false promotion in AI-authored cryptographic-exploit
evaluation pipelines with the HEB-1/IAR evidence shape, and the quantified
2×2 comparison of evaluator designs. That framing was fixed before execution
and is unchanged by any result.

### E. Does Experiment B contribute a defensible major result, or a bounded
empirical demonstration of known provenance principles?

**A bounded empirical demonstration, with two calibrated properties.** The
defensible content is: (1) a replicated, cross-construction measurement that
(b) signatures alone are insufficient, (c) joins alone are insufficient in
the opposite direction, and (d) the pair preserves honest partial claims with
zero false promotion, on two independently built case sets with a
separately-written truth adjudicator and a single blind held-out pass after
freeze; plus (2) a small, fully-documented historical real-defect finding
(observation-validity class) demonstrating why such evaluation layers need
independent audit. No major (novel-mechanism) claim is supported, and none is
made.

---

## 3. Input: HEB-1 closure (pre-existing, cited)

- HEB-1 synthetic evaluation: 64-case held-out single pass — V0/V1 baselines
  false-promoted 36/36; frozen V2 rejected 36/36 and accepted all clean and
  C1 controls. Results sha256
  `4bda7b8f4183b577d1b6ab6dd998d7147e086e70ee2e1f202b7eb3726d1f7265`
  (`heb1_crossboundary_20261019/heldout/heldout_results.json`).
- External-review disposition recorded in
  `HEB1_ADJUDICATION_RESPONSE_20261019.md` (sha256 `d0ab76e110d9786b2729d1ea276cb8dc2d969d22420b8e74b9ed410741564ac1`):
  synthetic mechanism confirmed at the implementation level; novelty **not**
  established; real impact **not** demonstrated; IAR protocol (A/B/C) GO.
- IAR-A: the real stage01 validator v2 + reference verifier v2 accepted an
  assembled certificate pairing run X's execution identity with run Y's
  candidate/effect; rejected the session-mismatch variant via
  `execution-session-binding`. Independent verifier `verify_iar_a.py`:
  75 PASS / 2 WARN / 0 FAIL. Trust-model caveat preserved in all reporting:
  both ACTS-Attack campaigns are trusted-issuer harnesses; this is an
  acceptance-boundary weakness under constructed C1/C2 inputs, **not** a
  live-campaign exploitation.

---

## 4. IAR-B — authenticated provenance vs. composition (2×2)

Authority: `IAR_B_RESULTS_REPORT.md` (sha256
`e5a988fbfcf5a7505575a48534304afbe41594b31678bdf98f5dea40fe0e770a`).

Design: 2×2 over (signatures) × (cross-record joins): V2 = frozen HEB-1
claim-binding validator (byte-identical, joins only); V3-sig = per-record
Ed25519 authenticity + structural checks, supported level = declared ladder;
V3-full = V3-sig + rung ladder joins J1–J9; generator-side adjudicator as
independent truth (never visible to the systems under test).

### 4.1 Dev pass (54 cases)
`iar_b/runs/20261019_112227/results.json` sha256
`032c93bedb65fec8cadd80d1ec2b0af5e6bb1e30ac4e30e6d105eb14eebcdf15`;
fixture failures 0; label deviations 0; gates G-B1..G-B5 all true.

| Metric | V2 | V3-sig | V3-full |
|---|---|---|---|
| level-6 false promotions (attack) | 16 | 24 | 0 |
| overclaim | 16 | 24 | 0 |
| false rejects (honest partial) | 10 | 0 | 0 |
| agreement with adjudicated level | 4 | 14 | 14 |
| mean overhead (ms) | 49.0 | 67.5 | 64.0 |

### 4.2 Held-out blind pass (58 cases)
`iar_b_heldout/runs/20261019_114849/results.json` sha256
`be08433db0da8ded6bed2c5edc1730b11b204b828660c3775c0340c2b818f640`;
single pass after freeze; gates G-B1..G-B5 all true; 4 documented label
deviations (§6.1).

| Metric | V2 | V3-sig | V3-full |
|---|---|---|---|
| level-6 false promotions (attack) | 16 | 28 | 0 |
| overclaim | 16 | 28 | 0 |
| false rejects (honest partial) | 10 | 0 | 0 |
| agreement with adjudicated level | 4 | 14 | 14 |
| mean overhead (ms) | 36.8 | 49.4 | 50.3 |

Promotion sets: V3-sig = H1, H2, H3, H4, H6b, H9, H10 (7 families × 4 = 28);
V2 = H5, H6a, H6b, H9 (4 × 4 = 16). V3-full promoted nothing and accepted H0
at 6 and all H7 cases at their adjudicated k=1..5, zero false rejects. The
adjudicator matched all 58 labels.

### 4.3 Gates

| Gate | Condition | Result |
|---|---|---|
| G-B1 | V3-full level-6 FP on H1–H4 == 0 | PASS (0 both passes) |
| G-B2 | V3-sig level-6 FP on attack families > 0 | PASS (24 dev / 28 held-out) |
| G-B3 | H5/H6a: V2 promotes while V3 rejects | PASS |
| G-B4 | H0/H7: zero false rejects; no unsupported promotion | PASS |
| G-B5 | determinism, protected hashes unchanged, manifest zeros | PASS |

---

## 5. IAR-C — independent adversarial replication

Authority: `iar_c/IAR_C_RESULTS_REPORT.md` (sha256
`7f9c7ecbd78c38e3898a49057e40dc14b6462608a54d5bec134dc44d0956ea02`).

Independence (frozen before the preserved pass): new generator
(`eb_independent_gen.py`) and new adjudicator (`eb_independent_adj.py`) import
nothing from `eb_fixtures`, `eb_adjudicator`, `eb_v3_*`, or frozen HEB-1
modules (only `eb_crypto` + stdlib + `cryptography`); own case ids, own
per-session key derivation, own truth model. Wire format (`heb1-signed/1`,
`.sig` sidecars, `eb-trust-anchor/1`) is the shared interface by necessity.
Systems under test are the byte-identical frozen IAR-B artifacts.

Case set: 44 cases / 54 anchors; families S1–S12 ×2 primitives, S13
(k=1..5) ×2, S14 ×2, S15 (a–d) ×2. Fixture check: independent adjudicator ==
generator labels, 44/44, first execution, zero label corrections needed.

Preserved pass (the pass to cite): `iar_c/runs/20261019_121621/results.json`
sha256 `7ad02c14f9328d82ccdfe3cdfbe7b0d0d88143b6f8393222701c7872187de785`;
all gates G-C1..G-C5 PASS; 0 fixture failures, 0 label deviations, 0
determinism mismatches, 0 system failures; 8 frozen-component hashes
verified; protected files byte-identical before/after; manifest
model/provider/network calls = 0. (Calibration pass
`iar_c/runs/20261019_121420/results.json` sha256
`cb3df2b0a6668812990536dd3f6bc8b24a0b334ea04403cc4b7b0c1e7b79c185`
produced identical numbers.)

| Metric (44 cases) | V2 (joins) | V3-sig (signatures) | V3-full (both) |
|---|---|---|---|
| level-6 false promotions, attack n=28 | **10** | **14** | **0** |
| — by family | S7, S9, S10, S11, S12 (×2) | S4, S5, S6, S7, S8, S11, S14 (×2) | — |
| overclaims | 10 | 14 | 0 |
| false rejects, honest-within-evidence n=16 | **14** | 0 | 0 |
| agreement (where asserted) | 2/12 | 16/30 | 16/16 |
| honest accepted at true level n=16 | 2 | 16 | 16 |
| malformed S15 handled n=8 | 8/8 REJECT | 8/8 REJECT | 8/8 REJECT |

Mean per-case overhead: adjudicator 129.9 ms, V2 37.4 ms, V3-sig 49.5 ms,
V3-full 50.9 ms (wall ~24 s for the whole pass, single process, local CPU).

| Gate | Criterion | Result |
|---|---|---|
| G-C1 | adjudicator == labels, all 44 | PASS (44/44) |
| G-C2 | determinism + frozen hashes + protected + offline | PASS |
| G-C3 | V3-full attack-family level-6 FP == 0 | PASS (0/28) |
| G-C4 | V2 > 0 and V3-sig > 0 | PASS (10, 14) |
| G-C5 | V3-full 0 false rejects, 0 overclaims, full agreement | PASS |

Replication statement: the IAR-B headline pattern reproduces on independently
constructed artifacts with a separately written truth adjudicator — V3-sig
promoted 14/28 (all individually authentic records in inadmissible
compositions, including the overclaim family S14), V2 promoted 10/28 (every
forged/unauthorized-signature family), V3-full promoted 0/28 while accepting
all 16 honest-within-evidence cases at exactly their adjudicated levels.

---

## 6. Recorded deviations and negative results (preserved, not retuned)

### 6.1 IAR-B H10/V2 label deviations (4 cases, disclosed post-pass)
Expected `{REJECT, level 3}` vs actual `{REJECT, level 5}` on four held-out
H10 cases (cids `eb-190e22557b`, `eb-818c4158e6`, `eb-aea73f76f0`,
`eb-c081a76535`). Cause verified from the registry: the recovered secret is
instance-determined, so H10's two success runs produce **identical candidate
bytes** (same `candidate_sha256` for both roles); V2's reference join then
fails only on the session field, stopping its ladder at 5 rather than 3.
V3-full and the adjudicator correctly stop at 3 (their l4 requires
`ref.session_id == cred`). All aggregate metrics are unaffected; the
imprecision is disclosed rather than retuned. H10 was appended to the
reporting attack-family set for G-B2 only (thresholds unchanged).

### 6.2 IAR-B integrity note
The held-out tree was wiped by a crashed generator run *before* the blind
pass (the builder wipes its tree first); a generator global-name bug was
fixed pre-pass. The generator is not part of the freeze; frozen bytes were
re-verified OK on every run.

### 6.3 Historical arm — honest negatives
- No inspected historical record contains a false promotion of unsupported
  attribution. The defects found are observation-validity defects (§7).
- Canonical-audit candidate C-3 (held-out attempt 3 integrity failure): only
  the archival label exists in the inspected records; not independently
  inspected case-by-case in this pass (classification: archival-label-only).
- Canonical-audit candidate C-2 (H1 "V2 instrument" XOR scorer defect): the
  raw corpus was located and counted (90 files = 9 arms × 10;
  `H1_V2_FAILURE_STAGE_SUMMARY.json` sha256
  `5a74c53f4d22db246c52f1377dc99a46dfa2275c97aa0e8e3535910a03b4a64b`:
  81/90 strict-JSON parseable, 35/60 sufficient-condition submissions, 0
  oracle recoveries, 30/30 correct underdetermination), but the scorer
  predicate itself was **not** recomputed this pass. Classification:
  raw-evidence-exists, predicate not recomputed (limitation).
- Canonical-audit candidate C-4 (original paid pilot): all 72 rows are
  `PROVIDER_FAILURE` HTTP 401 with `estimated_cost_usd 0.0` — a
  provider-access failure, excluded from evaluator-defect claims.

---

## 7. Historical real-defect validation (read-only)

Authority: `historical/HISTORICAL_VALIDATION_NOTES.md` (sha256
`1f40cc390efa1df46987312a90a8aa9e0ea5a547375d2689dcb1b8f5f95cea45`).
Rules applied: read-only inspection; a case is "independently demonstrated"
only if the underlying raw evidence exists and the predicate is recomputable
from immutable records; no synthesized replacements; no pooling of
incompatible cohorts; explicit evidence classes.

### 7.1 RV-1 — `free_v2` serialization crash (raw-recomputable; recomputed)
Campaign `contract_sound_agent_pilot_20261018_free_v2` (72 sessions,
2026-10-18 18:53; driver sha256
`7c81945d3e6d26bc75f9ddb66eb47f875f86b10d02bbfea5b5bc03ead62b53b0`). All 72
`session_result.json` records: `{"status":"HARNESS_FAILURE","error":"TypeError:
Object of type PosixPath is not JSON serializable", ...}`. Root cause
reproduced exactly: the driver passes the `PosixPath` `bundle` variable to
`invoke_json(REFERENCE, bundle)` (line 196), whose `json.dumps(payload)`
raises before the subprocess starts (line 194 writes the dict to that path —
a variable misuse). Consequence: the reference verifier and validator never
executed on any of the 72 sessions in the original run, and the terminal
record does not state that the candidate was policy-rejected and never
executed — an **incomplete execution provenance at the terminal-record
layer**. The audit's `reference_invoked: true` for ordinal 1 traces to a
manual forensic re-run at 19:02, whose stderr shows the reference verifier
crashing on the missing `candidate_output.json`. The repaired pipeline
(`contract_sound_repaired_pipeline.py` sha256
`5d264dd19d692626079712607b16172ac64b1f11d6d80434377b7b791cf89a9b`)
passes `str(bundle_path)` and returns structured `FAILED/INVALID_OUTPUT`
records instead of raising; its tests
(`test_contract_sound_repaired_pipeline.py` sha256
`e64f8f1efddbea286f57e9dc7fee2dbf97cbfd7632ac8990a172dcff2a6cdd7c`)
assert no `PosixPath` leaks into serialization.

### 7.2 RV-2 — `free_v2` source-qualification policy contradicts the declared interface (raw-recomputable; recomputed)
The campaign's `boundary.json` declares `allowed_interface:
"argv-instance-json; restricted-python-subset; no-network-declared"`, and the
official prompt instructs candidates to read the instance from `argv[1]`
(`python -I candidate.py public_instance.json`). The old `safe_source`
qualification (driver lines 42–53) rejects any call text containing
`open(` — with an import allowlist of `{json, sys, base64}` there is no other
way to read a file, so **the official prompt and the official policy are
mutually unsatisfiable for any compliant solution**. Recomputation with the
verbatim-copied rule over all 72 retained candidates: **72/72 rejected**
(71 × `disallowed-boundary` on `open(`; 1 × `disallowed-import` — session
`contract-sound-005-1f13f6e4cd6e`, line 3 `from hashlib import sha256`).
Consequence: zero candidates ever executed; `target_effect` always
NOT_OBSERVED; even a perfect solution was unscoreable. The repaired
qualification rule accepts **71/72** (the residual rejection is the same
`hashlib` import, defensible under the declared restricted subset). Every
on-disk `candidate.py` reproduces its `provider_raw.json` first-python-fence
extraction hash (72/72), and the forensic matrix
(`contract_sound_agent_forensic_matrix_20261018/FORENSIC_CLASSIFICATION_MATRIX.json`
sha256 `d4cfc1a224b15eb3fe453fc5e76039acf7eeb7be9913a265f92ca188010d77b9`)
records all 72 as `HARNESS_SERIALIZATION_BEFORE_ORACLE` (its mixed taxonomy
string `disallowed-boundary;disallowed-import-from` on session 005 is a
labeling artifact of the matrix generator; the verbatim recompute is
authoritative). Campaign-wide outcome: **0/72 evaluator outcomes**, lost to a
policy false-rejection (D2) plus a masking crash (D1) — not a false
promotion.

### 7.3 RV-3 — repair deterministic-gate failed→passed pair (partially recomputable)
- Passed record `contract_sound_72_repair_deterministic_20261018/REPAIR_DETERMINISTIC_GATE.json`
  sha256 `63aeca2ab9157987ce9e2d69ed7cd3c1cacdf5719a8a39597d139cf2eed67b0f`;
  status PASS_DETERMINISTIC_GATE; 36/36 pair checks; provider/network calls 0.
  Independently re-executed offline from the current validator revision
  (`validate_72_repair_deterministic.py` sha256
  `27987d6ec093fafb0e908ef248c5178a8a6ac3857a02f238c109eb6d0a79becb`):
  **byte-identical JSON output** (same sha256).
- Preserved failed record `..._gate-failed-raw-order-check/REPAIR_DETERMINISTIC_GATE.json`
  sha256 `da4cddf9e34238817d525d9d07cb0a22ef9b831c8cf28407ad67dd1aaa506eee`;
  status FAIL_DETERMINISTIC_GATE; 36/36 pairs fail exactly
  `checks.raw_representation_distinct`; all other fields byte-identical to
  the passed run. The pre-fix revision was not retained, so the exact failing
  binary is not rerunnable; the failure predicate is fully recomputable from
  the current revision (its reorder makes the order-sensitive raw
  serialization differ by construction).
- Classification: a **construction-QA defect** (the representation knob
  initially produced identical raw order in all 36 pairs), caught by the
  campaign's own deterministic gate, fixed, and re-verified byte-identically.
  It is not an evaluator-boundary false-attribution defect; it supports the
  repair-process integrity story.

### 7.4 Other canonical-audit candidates
- **C-1 E5 escrow**: census (`E5_RAW_RUN_CENSUS_20261018.json` sha256
  `bccd7a5dbd0648cbb37b6fa3820e0143c7a3ccde70c320d6e7aa6ac9cee7e8a8`)
  counts 29 retained records {ORACLE_FAIL 9, PROVIDER_UNAVAILABLE 15, SUCCESS
  1, TOOL_FAILURE 4}; 14 graded, 1/14 accepted; 15 provider-unavailable not
  counted as attack failures. Record-level verification performed: the single
  SUCCESS record recomputes exactly to the census hash
  (`0fc09afb2798353158fcc24264c168f8320ceb8eb2bfecaa8611ed032679f1f4`). The
  audit's full defect characterization (verifier-hash/launcher metadata
  defect; host-executed code; missing caller authentication) is
  code-architectural beyond the retained record — classification:
  raw-evidence-exists (record level), defect predicate partially recomputed;
  limitation stated.
- **C-3 held-out attempt 3**: archival-label-only in the inspected records;
  not further inspected this pass.
- **C-4 paid pilot**: provider-access failure (72/72 HTTP 401), excluded.

**Historical bottom line:** the genuine evaluator-boundary failures found are
observation-validity class (a policy false-rejection that contradicts the
declared interface, plus a serialization crash that masked the true terminal
state). No historical false-promotion instance was found. The HEB-1/IAR
composition mechanism is measured under constructed synthetic conditions, not
observed as an exploitation in any historical campaign — a limitation that is
preserved verbatim in every report of this line.

---

## 8. Limitations (complete list)

1. **Same-author construction** for all case sets (IAR-C is a structural, not
   socio-technical, independent replication).
2. **Shared `eb_crypto` module and wire format** between generator sides;
   independent implementations elsewhere.
3. **Synthetic fixtures, self-designed faults**; one deterministic preserved
   pass per stage (calibration + preserved for IAR-C; dev + held-out for
   IAR-B). No retuning after any held-out or preserved evaluation.
4. **Trust model assumes** per-session keys and the trust anchor are outside
   the composer's control; C3 (key compromise) is out of scope by design.
5. **External validity** limited to evaluators with this evidence shape
   (signed per-record evidence, session-scoped keys, claim ladder).
6. **Historical arm**: no false-promotion instance exists in the inspected
   archives; the found defects are observation-validity class; C-1/C-2
   predicates partially recomputed; C-3 not inspected; the failed gate
   revision is not retained (recomputable predicate only).
7. **No live-campaign claim**: both ACTS-Attack campaigns are trusted-issuer
   harnesses; IAR-A/IAR-B/IAR-C results are constructed-input evaluations.
8. **Novelty**: none established (RFC 9334/RATS, in-toto, TRAP/ReplayBench,
   `evidence.*` anticipate the principles); no novelty-score inflation.

---

## 9. Integrity and compliance

- **Protected files unchanged before/after every pass** (verified inside each
  pass): `RESULTS_LOCK.json` `4b152f18…`, `RESULTS_LOCK_H1PC.json`
  `8221cb86…`, `paper/main.tex` `51f97748…`, `paper/main.pdf` `fd9a5889…`.
- **Offline**: no model, provider, or network calls in any pass or
  recomputation; marginal spend $0; provider key never used or logged.
- **Frozen bytes**: all component hashes re-verified inside each preserved
  pass (8 checks IAR-C; full set IAR-B) and reproduced identically in this
  report's manifest (§10).
- **No retuning**: the only post-freeze correction anywhere is the
  pre-freeze H7/H8 label convention fix in IAR-B (documented pre-freeze) and
  the post-pass H10 deviation disclosure (§6.1); no metric, threshold, or
  frozen byte was changed after any held-out/preserved pass.
- **History preserved**: nothing committed, reset, or cleaned; the repo's
  large pre-existing uncommitted work is untouched; all outputs live under
  `sp2027/analysis/experiment_b_20261019/` except scratch work in
  `/tmp/opencode/`. Freebuff's Experiment A tree was not touched.
- **Deliverables per protocol §11**: protocol (frozen); `eb_crypto.py`; IAR-B
  set/systems/runner/passes/freeze/results; IAR-C generator/adjudicator/
  runner/set/freeze/preserved pass/results; historical validation notes with
  evidence classes; this report.

---

## 10. Reproduction (exact commands) and artifact manifest

### 10.1 Commands

```bash
# IAR-B (dev + held-out)
cd sp2027/analysis/experiment_b_20261019
python3 eb_fixtures.py                      # build dev set (54 cases)
python3 eb_runner.py                        # dev pass -> iar_b/runs/<ts>/results.json
python3 heldout/eb_iar_b_heldout.py         # build held-out set (58 cases)
python3 heldout/eb_iar_b_heldout_runner.py  # single blind held-out pass

# IAR-C
python3 iar_c/eb_independent_gen.py         # build 44-case set + labels + trust
python3 iar_c/eb_independent_runner.py      # preserved pass -> iar_c/runs/<ts>/results.json

# Historical recomputations (read-only)
python3 - <<'EOF'   # verbatim old safe_source / repaired qualify_source over the 72 candidates
...                 # (as executed 2026-10-19; see HISTORICAL_VALIDATION_NOTES.md §RV-2)
EOF
python3 validate_72_repair_deterministic.py # re-executes the deterministic gate (patched OUT dir)
```

### 10.2 Artifact hashes (sha256)

| Artifact | sha256 |
|---|---|
| EXPERIMENT_B_PROTOCOL.md | `f44218172f43177498ee30090ee999a6c3c8e132332c153bc07737020557fe2b` |
| eb_crypto.py | `9243529ef019cd899023600cf29c1c585d712bd04048501010a70fdae4027a4c` |
| eb_fixtures.py | `9c9645273bd0990171a542a4822b33a309c9ee3703ce85e6994e35ab8febee55` |
| eb_v3_sig.py | `6b17954b0441dcf7ef0973d7e9c755df9707658119290a9d4e4bb5db64727329` |
| eb_v3_full.py | `6c7d0d8b564e0d0bdeace6ba59be90cd03cb9a8700df7649d6366a97ff280670` |
| eb_adjudicator.py | `c7c6a62cd6e288a4e1f92d910ed70eceafa621d8c3389eb09242c3e0f893425e` |
| eb_runner.py | `a7c9031ea27f886456d37751d161f1dcefca0fc838ea7d6acca54d5c4d8238a3` |
| freeze/HEB_IARB_FREEZE.json | `cc0fde9e750b84baea80fe3d9bf58f6ca88ae53370b769b74508856de59e0570` |
| IAR-B dev results | `032c93bedb65fec8cadd80d1ec2b0af5e6bb1e30ac4e30e6d105eb14eebcdf15` |
| IAR-B held-out results | `be08433db0da8ded6bed2c5edc1730b11b204b828660c3775c0340c2b818f640` |
| IAR_B_RESULTS_REPORT.md | `e5a988fbfcf5a7505575a48534304afbe41594b31678bdf98f5dea40fe0e770a` |
| iar_c/eb_independent_gen.py | `dba82edd4fd3d60b27d471a28cf0ba9ae0126bb578440a8bd24d62c1c37aa948` |
| iar_c/eb_independent_adj.py | `528dcb43657e99a898f8de543cabf167f1c35f22b68ca11f66fa234b5f3d2b73` |
| iar_c/eb_independent_runner.py | `d9aebb8d93fd8c7322368842f1e8307a6c17f59bb2c3b862b559f6407a905de4` |
| iar_c/freeze/IAR_C_CASE_MANIFEST.json | `d2640d40988611e0fc65e228ae31c33cb6e06324ec6743f590caa7baaa6c0faf` |
| iar_c/freeze/IAR_C_FREEZE.json | `a2145de564c1781b9463a0a9cd6ed1c908a5de16dc240b67ac196a29bacb7ff8` |
| iar_c preserved pass results | `7ad02c14f9328d82ccdfe3cdfbe7b0d0d88143b6f8393222701c7872187de785` |
| iar_c calibration results | `cb3df2b0a6668812990536dd3f6bc8b24a0b334ea04403cc4b7b0c1e7b79c185` |
| iar_c labels / trust | `75776db2e9f2eea454c59a7db785633701537dd9859f0c8cc5adeee7a2291fa7` / `d4629a4aa477f0bdb001bb2624d4ddef8a81f2dc0d6beef76a1057d4a9283952` |
| IAR_C_RESULTS_REPORT.md | `7f9c7ecbd78c38e3898a49057e40dc14b6462608a54d5bec134dc44d0956ea02` |
| historical/HISTORICAL_VALIDATION_NOTES.md | `1f40cc390efa1df46987312a90a8aa9e0ea5a547375d2689dcb1b8f5f95cea45` |
| HEB-1 held-out results | `4bda7b8f4183b577d1b6ab6dd998d7147e086e70ee2e1f202b7eb3726d1f7265` |
| HEB1_EVALUATION_REPORT.md | `fb7993a4e8d3d67c99efee5dddac2a57c4ab73611b55f09f0cfea3415008db1b` |
| HEB1_ADJUDICATION_RESPONSE_20261019.md | `d0ab76e110d9786b2729d1ea276cb8dc2d969d22420b8e74b9ed410741564ac1` |
| frozen heb1_v2_claim_binding.py | `3585f876a39d136eb550db1cccb04a4b23f30e4b46a5bb2e6d97efb55194c53d` |
| run_contract_sound_agent_pilot_free_v2.py | `7c81945d3e6d26bc75f9ddb66eb47f875f86b10d02bbfea5b5bc03ead62b53b0` |
| contract_sound_repaired_pipeline.py | `5d264dd19d692626079712607b16172ac64b1f11d6d80434377b7b791cf89a9b` |
| test_contract_sound_repaired_pipeline.py | `e64f8f1efddbea286f57e9dc7fee2dbf97cbfd7632ac8990a172dcff2a6cdd7c` |
| FORENSIC_CLASSIFICATION_MATRIX.json | `d4cfc1a224b15eb3fe453fc5e76039acf7eeb7be9913a265f92ca188010d77b9` |
| free_v2 pilot_results.json | `44ca08103e134b676e84b3e48f255b9bd9149610915d0398be497ad6e3951aea` |
| paid pilot_results.json | `4d9c38729ea49be12671f1171cef9baa1806663568e5edb7364a02d915d1c86a` |
| validate_72_repair_deterministic.py | `27987d6ec093fafb0e908ef248c5178a8a6ac3857a02f238c109eb6d0a79becb` |
| repair gate PASSED | `63aeca2ab9157987ce9e2d69ed7cd3c1cacdf5719a8a39597d139cf2eed67b0f` |
| repair gate FAILED | `da4cddf9e34238817d525d9d07cb0a22ef9b831c8cf28407ad67dd1aaa506eee` |
| CANONICAL_RUN_AUDIT_20261018.md | `d568dd13af322188c2e21542c1aefe151180303aac05152147e967af925beaa1` |
| E5_RAW_RUN_CENSUS_20261018.json | `bccd7a5dbd0648cbb37b6fa3820e0143c7a3ccde70c320d6e7aa6ac9cee7e8a8` |
| H1_V2_FAILURE_STAGE_SUMMARY.json | `5a74c53f4d22db246c52f1377dc99a46dfa2275c97aa0e8e3535910a03b4a64b` |
| E5 success record | `0fc09afb2798353158fcc24264c168f8320ceb8eb2bfecaa8611ed032679f1f4` |
| free_v2 session-001 session_result.json | `dec7b40252579524e1c3b2ba7204d555518983889e74d93ccd9e89f3bfb09c8a` |
| contract_sound_stage01_validator_v2.py | `f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a` |
| contract_sound_stage01_reference_verifier_v2.py | `15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b` |

---

## 11. Status and next decision

Experiment B is complete: protocol executed as frozen; all gates passed as
specified; all negative results, deviations, and limitations preserved;
nothing committed. **The commit decision is left to the user** (the
repository contains large pre-existing uncommitted work from earlier
campaigns, and this report does not presuppose how it should be grouped).
No manuscript integration is proposed or performed; per the standing
instruction, no novelty-score inflation is claimed.
