# IAR-C — Independent Adversarial Replication of the IAR-B Composition Result

Date: 2026-10-19. Status: complete (single preserved pass, frozen).

## 1. Question

IAR-B measured a 2×2 pattern on its own fixtures: signatures alone accept
cross-boundary compositions, joins alone accept forged/foreign records and
reject honest partial claims, and the pair prevents all unsupported promotions.
IAR-C asks whether that pattern survives replication on an **independently
constructed** adversarial set with a **separately written** truth adjudicator,
sharing only the wire format and the crypto primitive module with IAR-B.

## 2. Independence design (frozen before the preserved pass)

- Independent generator `iar_c/eb_independent_gen.py`: imports only
  `eb_crypto` + stdlib + `cryptography`; no import of `eb_fixtures`,
  `eb_adjudicator`, `eb_v3_*`, or any frozen HEB-1 module. Own case ids, own
  per-session key derivation (`sha256('eb-iar-c|key|'||session)`), own run
  builder, own scenario and truth model.
- Independent adjudicator `iar_c/eb_independent_adj.py`: separately written
  from `eb_adjudicator.py`; same import restriction; its supported-level
  contract (longest consecutive rung run r1…r6, authenticity per record's own
  session, malformed short-circuit, crypto predicate) was fixed before
  execution.
- Systems under test are byte-identical frozen IAR-B artifacts:
  V2 (joins only) `3585f876…`, V3-sig (signatures only) `6b17954b…`,
  V3-full (signatures + joins) `6c7d0d8b…` (hashes in §10).
- Wire format is the shared interface by necessity: certificate schema
  `heb1-signed/1`, six evidence kinds with `.sig` sidecars, trust anchor schema
  `eb-trust-anchor/1`.
- Single preserved pass after freeze; nothing modified afterwards.

## 3. Case set (44 cases / 54 anchors; seed `eb-iar-c-20261019`)

Families S1–S12 ×2 primitives (ecdsa/chacha) = 24, S13 (k=1..5) ×2 = 10,
S14 ×2, S15 (a–d) ×2 = 8. Truth labels and trust anchor generated together
with the cases; adjudicator–label fixture check on all 44 = 44/44 agreement.

| Family | Mechanism (truth) | Truth | n |
|---|---|---|---|
| S1 | clean success, full attribution | strong (6) | 2 |
| S2 | honest failure, no effect | level 2 | 2 |
| S3 | honest failure, wrong candidate | level 2 | 2 |
| S4 | cross-run splice (failed records + successful candidate) | level 0 | 2 |
| S5 | cross-condition relabel | level 5 | 2 |
| S6 | stale instance/target swap | level 5 | 2 |
| S7 | foreign authentic authorship | level 0 | 2 |
| S8 | foreign authentic reference acceptance | level 3 | 2 |
| S9 | forged trace signature | level 1 | 2 |
| S10 | forged authorship signature | level 0 | 2 |
| S11 | unsigned certificate executor rewrite | level 1 | 2 |
| S12 | unauthorized signer record | level 0 | 2 |
| S13 | incomplete-but-legitimate evidence k=1..5 | k | 10 |
| S14 | unsupported high claim over level-3 evidence | level 3 | 2 |
| S15 | malformed evidence (a del_candidate, b corrupt target_effect, c stale trace hash, d del_target) | malformed | 8 |

Honest families {S1, S2, S3, S13}; attack families {S4–S12, S14, S15}.
"Honest within evidence" = 16 cases (S1, S2, S3, S13) where the requested
level is ≤ the supported level.

## 4. Results

### 4.1 Calibration pass (pre-freeze wiring check)
`iar_c/runs/20261019_121420/results.json` sha256 `cb3df2b0…c185` — all gates
pass; FP level 6 (attack): V2 10, V3-sig 14, V3-full 0.

### 4.2 Preserved pass (the pass to cite)
`iar_c/runs/20261019_121621/results.json` sha256
**`7ad02c14f9328d82ccdfe3cdfbe7b0d0d88143b6f8393222701c7872187de785`**

All gates G-C1…G-C5 PASS. Numbers reproduce the calibration pass exactly:
0 fixture failures, 0 label deviations, 0 determinism mismatches (each system
invoked twice per case), 0 system failures; 8 frozen-component hashes verified
match; protected files byte-identical before/after; manifest model/provider/
network calls = 0.

| Metric (44 cases) | V2 (joins) | V3-sig (signatures) | V3-full (both) |
|---|---|---|---|
| Level-6 false promotions, attack families (n=28) | **10** | **14** | **0** |
| – by family | S7, S9, S10, S11, S12 (×2) | S4, S5, S6, S7, S8, S11, S14 (×2) | — |
| Overclaims (asserted > supported) | 10 | 14 | 0 |
| False rejects (honest, within evidence, n=16) | **14** | 0 | 0 |
| Agreement with adjudicator (where asserted) | 2/12 | 16/30 | 16/16 |
| Honest accepted at true supported level (n=16) | 2 | 16 | 16 |
| Malformed S15 handled (n=8) | 8/8 REJECT | 8/8 REJECT | 8/8 REJECT |

Family-level outcome table (n=2 per row unless noted; asserted level in
parentheses):

| Family | Truth | V2 | V3-sig | V3-full |
|---|---|---|---|---|
| S1 | 6 | 2×EMIT(6) | 2×ACCEPT(6) | 2×ACCEPT(6) |
| S2 | 2 | 2×REJECT | 2×ACCEPT(2) | 2×ACCEPT(2) |
| S3 | 2 | 2×REJECT | 2×ACCEPT(2) | 2×ACCEPT(2) |
| S4 | 0 | 2×REJECT | 2×ACCEPT(6) | 2×REJECT |
| S5 | 5 | 2×REJECT | 2×ACCEPT(6) | 2×REJECT |
| S6 | 5 | 2×REJECT | 2×ACCEPT(6) | 2×REJECT |
| S7 | 0 | 2×EMIT(6) | 2×ACCEPT(6) | 2×REJECT |
| S8 | 3 | 2×REJECT | 2×ACCEPT(6) | 2×REJECT |
| S9 | 1 | 2×EMIT(6) | 2×REJECT | 2×REJECT |
| S10 | 0 | 2×EMIT(6) | 2×REJECT | 2×REJECT |
| S11 | 1 | 2×EMIT(6) | 2×ACCEPT(6) | 2×REJECT |
| S12 | 0 | 2×EMIT(6) | 2×REJECT | 2×REJECT |
| S13 k=1..5 | 1..5 | 10×REJECT | 10×ACCEPT(1..5) | 10×ACCEPT(1..5) |
| S14 | 3 | 2×REJECT | 2×ACCEPT(6) | 2×REJECT |
| S15 a–d | malformed | 8×REJECT | 8×REJECT | 8×REJECT |

Mean per-case overhead: adjudicator 129.9 ms, V2 37.4 ms, V3-sig 49.5 ms,
V3-full 50.9 ms (single-process, local CPU; wall ~24 s, CPU ~42 s total pass).

## 5. Gates

| Gate | Criterion | Result |
|---|---|---|
| G-C1 | independent adjudicator == generator labels, all 44 | PASS (44/44) |
| G-C2 | determinism, frozen hashes, protected files, offline ($0) | PASS |
| G-C3 | V3-full level-6 false promotions on attack families == 0 | PASS (0/28) |
| G-C4 | V2 > 0 and V3-sig > 0 level-6 false promotions | PASS (10, 14) |
| G-C5 | V3-full 0 false rejects, 0 overclaims, agreement on every assertion | PASS |

## 6. Findings

1. **The IAR-B headline pattern replicates on independently built artifacts.**
   On 28 attack-family cases constructed by a different generator with a
   different truth model, V3-full promoted 0 to level 6; V3-sig promoted 14
   (all individually authentic records in inadmissible compositions: cross-run,
   cross-condition, stale-instance, foreign-authorship, foreign-reference,
   executor-rewrite, overclaim); V2 promoted 10 (every forged- or
   unauthorized-signature family: S7, S9, S10, S11, S12).
2. **The failure directions are complementary and persist under independent
   construction.** Authenticity without binding fails on composition
   (V3-sig, 14/28); binding without authenticity fails on provenance (V2,
   10/28). Neither single-axis policy is sufficient; the pair is.
3. **Honest partial-claim acceptance is a first-class outcome and V3-full
   passes it.** All 16 honest-within-evidence cases (levels 1–5, including all
   S13 partial fractions) were accepted at exactly the adjudicated level; V2
   rejected 14/16 (it accepts only fully evidenced S1).
4. **Malformedness handling is uniform.** All three systems cleanly reject the
   8 S15 variants (missing candidate/target, corrupt JSON, stale hash); no
   system emitted an unsupported level on malformed input.
5. **No label retuning was needed.** The generator's expected labels required
   no pre-freeze or post-freeze correction; the adjudicator matched them on
   first execution (44/44), and all system deviations from labels were exactly
   the false promotions/false rejects that are the object of measurement.

Novelty framing (unchanged from IAR-B and the HEB-1 adjudication): the binding
principle is anticipated (RFC 9334/RATS, in-toto, TPM-style event logs); the
contribution of this line is the **empirical measurement of false promotability
in AI-authored cryptographic-exploit evaluation and the claim-specific
evaluator comparison**, not a new binding mechanism.

## 7. Integrity and limitations

- Frozen before the preserved pass: `iar_c/freeze/IAR_C_FREEZE.json`
  sha256 `a2145de564c1781b9463a0a9cd6ed1c908a5de16dc240b67ac196a29bacb7ff8`;
  case manifest (762 files) `d2640d40…0faf`.
- All 8 frozen component hashes re-verified inside the preserved pass
  (generator, adjudicator, runner, V2, V3-sig, V3-full, labels, trust).
- Protected files unchanged before/after: `RESULTS_LOCK.json 4b152f18…`,
  `RESULTS_LOCK_H1PC.json 8221cb86…`, `paper/main.tex 51f97748…`,
  `paper/main.pdf fd9a5889…`.
- Offline: no network, model, or provider calls; marginal spend $0.
- Limitations (declared pre-pass): same-author construction (structural, not
  socio-technical independence); shared `eb_crypto` primitive module and wire
  format; scenario taxonomy S1–S15 mirrors IAR-B with independent
  implementations and parameters; synthetic fixtures; one deterministic pass;
  trust model assumes the anchor and signing keys are outside composer control.
  External validity is limited to systems with this evidence shape.

## 8. Reproduction

```
cd sp2027/analysis/experiment_b_20261019
python3 iar_c/eb_independent_gen.py                  # build 44-case set + labels + trust
python3 iar_c/eb_independent_runner.py               # calibration/preserved run
# fixture check: adjudicator vs labels (inside runner) — 44/44
```

The runner writes `iar_c/runs/<timestamp>/results.json`; the preserved pass is
`iar_c/runs/20261019_121621/`.

## 9. Artifact hashes

| Artifact | sha256 |
|---|---|
| iar_c/freeze/IAR_C_FREEZE.json | `a2145de564c1781b9463a0a9cd6ed1c908a5de16dc240b67ac196a29bacb7ff8` |
| iar_c/freeze/IAR_C_CASE_MANIFEST.json | `d2640d40988611e0fc65e228ae31c33cb6e06324ec6743f590caa7baaa6c0faf` |
| iar_c/eb_independent_gen.py | `dba82edd4fd3d60b27d471a28cf0ba9ae0126bb578440a8bd24d62c1c37aa948` |
| iar_c/eb_independent_adj.py | `528dcb43657e99a898f8de543cabf167f1c35f22b68ca11f66fa234b5f3d2b73` |
| iar_c/eb_independent_runner.py | `d9aebb8d93fd8c7322368842f1e8307a6c17f59bb2c3b862b559f6407a905de4` |
| iar_c/data/labels/iar_c_labels.json | `75776db2e9f2eea454c59a7db785633701537dd9859f0c8cc5adeee7a2291fa7` |
| iar_c/data/trust/iar_c_run_keys.json | `d4629a4aa477f0bdb001bb2624d4ddef8a81f2dc0d6beef76a1057d4a9283952` |
| eb_v3_sig.py (frozen) | `6b17954b0441dcf7ef0973d7e9c755df9707658119290a9d4e4bb5db64727329` |
| eb_v3_full.py (frozen) | `6c7d0d8b564e0d0bdeace6ba59be90cd03cb9a8700df7649d6366a97ff280670` |
| heb1_v2_claim_binding.py (frozen) | `3585f876a39d136eb550db1cccb04a4b23f30e4b46a5bb2e6d97efb55194c53d` |
| calibration results | `cb3df2b0a6668812990536dd3f6bc8b24a0b334ea04403cc4b7b0c1e7b79c185` |
| preserved pass results | `7ad02c14f9328d82ccdfe3cdfbe7b0d0d88143b6f8393222701c7872187de785` |
