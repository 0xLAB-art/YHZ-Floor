# IAR-B — Authenticated Provenance vs. Cross-Boundary Composition

Status: executed; single deterministic dev pass and single blind held-out pass;
frozen bytes re-verified pre-pass; no retuning after the held-out pass.
Date: 2026-10-19
Authority: `EXPERIMENT_B_PROTOCOL.md` (design freeze). Everything here is
synthetic/offline; no model, provider, or network calls were made.

## 1. Question

Does the HEB-1/IAR-A cross-boundary failure survive *authenticated provenance*,
and which mechanism is actually load-bearing — signatures, cross-record joins,
or both? The comparison is a 2x2 over (signatures) x (cross-record joins):

| System | Signatures | Cross-record joins | Notes |
|---|---|---|---|
| V2 | no | yes | frozen HEB-1 claim-binding validator, byte-identical (`heb1_crossboundary_20261019/build/heb1_v2_claim_binding.py`) |
| V3-sig | yes | no | per-record Ed25519 authenticity + structural/hash checks; supported level = declared ladder |
| V3-full | yes | yes | V3-sig + rung ladder l1–l6 with session/executor/candidate/effect/reference/boundary/metadata joins |
| adjudicator | — | — | independent generator-side truth (private registry + target state); never visible to the three systems |

## 2. Trust model (frozen in protocol)

- Per-run Ed25519 issuer keys are generated in the fixture harness; the
  verification anchor (`trust/*.json`) maps `session_id -> public key` and is
  outside the adversarial composer's control; its SHA-256 is pinned.
- Every evidence record is signed over
  `sha256(canonical_json(record))` (detached `.sig` sidecar).
- Composer capabilities: C1 = assemble certificates + re-hash files from
  authentic records; C2 = rewrite unsigned metadata. C3 (signature forgery /
  key compromise) is out of scope and is never used to "demonstrate" anything.
- No claim about any live ACTS-Attack campaign; this is a constructed-input
  acceptance-boundary evaluation of verifier designs.

## 3. Case families

Each family exists for both primitives (ECDSA nonce reuse; ChaCha20 keystream
reuse); dev and held-out use disjoint opaque ids and disjoint keys.

| Family | Mechanism | Adjudicated support |
|---|---|---|
| H0 | clean coherent success run | 6 |
| H1 | cross-run C1 splice (X authorship/trace, Y candidate/effect) | 0 |
| H2 | cross-condition relabel (authentic records, claimed condition differs) | 5 |
| H3 | stale instance + target swap | 5 |
| H4 | split-half (X's trace inside Y's successful bundle) | 1 |
| H5 | C2 forged trace signature | 1 |
| H6a | C2 forged authorship signature | 0 |
| H6b | C1 foreign authentic authorship record (X's, cred = Y) | 0 |
| H7(k) | honest partial claims, levels k = 1..5 | k |
| H8 | malformed/missing controls (missing candidate/target, stale hash, corrupt JSON) | malformed |
| H9 | C2 unsigned executor rewrite in certificate | 1 |
| H10 | reference replay: Z's authentic reference record inside Y's bundle (held-out only, dev-unseen) | 3 |

## 4. Results

### 4.1 Dev pass (54 cases) — `iar_b/runs/20261019_112227/results.json`

sha256 `032c93bedb65fec8cadd80d1ec2b0af5e6bb1e30ac4e30e6d105eb14eebcdf15`.
fixture_failures 0; label_deviations 0; gates G-B1..G-B5 all true.

| Metric | V2 | V3-sig | V3-full | adjudicator |
|---|---|---|---|---|
| level-6 false promotions (attack families) | 16 | 24 | 0 | — |
| level-6 false promotions (H1–H4) | — | — | 0 | — |
| overclaim (emitted > adjudicated) | 16 | 24 | 0 | — |
| false rejects of honest partial claims | 10 | 0 | 0 | — |
| agreement with adjudicated level | 4 | 14 | 14 | — |
| mean overhead (ms) | 49.0 | 67.5 | 64.0 | 158.4 |

Per-family decisions (dev): V2 promotes H0, H5, H6a, H6b, H9 to level 6 and
rejects H1(0)/H2(5)/H3(5)/H4(1)/H7/H8; V3-sig accepts every family except
H5/H6a/H8; V3-full rejects H1–H4, H6b, H9 and accepts H0 (6) and H7 (k = 1..5).

### 4.2 Held-out blind pass (58 cases) — `iar_b_heldout/runs/20261019_114849/results.json`

sha256 `be08433db0da8ded6bed2c5edc1730b11b204b828660c3775c0340c2b818f640`.
Built from seed `eb-iar-b-heldout-20261019`; labels sha256
`fd00498ea704af8568e3c3580ad71af0bc51ecfc097a5977aa364fc94053a504`; trust sha256
`f2dd785c807897b4a0b80cfb0af1b5de827b05be6e569e5fa52c42353925195b`.
fixture_failures 0; gates G-B1..G-B5 all true (see §6); label_deviations 4 (§5).

| Metric | V2 | V3-sig | V3-full | adjudicator |
|---|---|---|---|---|
| level-6 false promotions (attack families) | 16 | 28 | 0 | — |
| level-6 false promotions (H1–H4) | — | — | 0 | — |
| overclaim (emitted > adjudicated) | 16 | 28 | 0 | — |
| false rejects of honest partial claims | 10 | 0 | 0 | — |
| agreement with adjudicated level | 4 | 14 | 14 | — |
| mean overhead (ms) | 36.8 | 49.4 | 50.3 | 132.5 |

Promotion sets: V3-sig level-6 false promotions = H1, H2, H3, H4, H6b, H9,
H10 (7 families x 4 = 28). V2 promotions = H5, H6a, H6b, H9 (4 x 4 = 16).
V3-full promoted nothing; it accepted H0 at level 6 and every honest H7 case
at its requested/adjudicated level k, with zero false rejects. The adjudicator
matched all 58 labels (registry+private-state truth model).

## 5. Recorded label deviations (post-pass documentation, no retune)

Exactly four deviations, all on H10 and all on V2, expected
`{REJECT, level 3}` vs actual `{REJECT, level 5}`
(cids eb-190e22557b, eb-818c4158e6, eb-aea73f76f0, eb-c081a76535).

Cause (verified from the registry): the recovered secret is
instance-determined, so H10's two success runs ("z", "y") produce *identical
candidate bytes* — the registry shows the same `candidate_sha256`
(e.g. `620830f8cb4b074f...`) for both roles. V2's reference join therefore
fails only on the session field (ref.session_id SZ != cred SY), not on the
artifact hash, so its ladder stops at level 5 rather than 3. V3-full and the
adjudicator still stop at level 3 because their l4 explicitly requires
`ref.session_id == cred`. Decisions and all aggregate metrics are unaffected.
The H10 label was a pre-pass expectation imprecision; it is preserved as-is
and disclosed here rather than retuned after the blind pass.

## 6. Gates

| Gate | Condition | Result |
|---|---|---|
| G-B1 | V3-full level-6 false promotions on H1–H4 == 0 | PASS (0 both passes) |
| G-B2 | V3-sig level-6 false promotions on attack families > 0 | PASS (24 dev / 28 held-out) |
| G-B3 | H5/H6a: V2 promotes while V3-sig and V3-full reject | PASS |
| G-B4 | H0/H7: zero false rejects; honest levels accepted; no unsupported promotion | PASS |
| G-B5 | determinism (double run identical), protected hashes unchanged, manifest zeros | PASS |

## 7. Findings

1. **Signatures alone do not prevent cross-boundary promotion.** V3-sig
   accepted every C1/C2 composition whose signatures were individually
   authentic (H1–H4, H6b, H9, and the new held-out H10), i.e. 28/28 held-out
   attack-family promotions at level 6. Authenticity of individual records
   does not imply validity of their composition.
2. **Joins alone fail in the opposite direction.** V2 detected the session/
   trace splices (H1–H4, H10) but promoted forgeries and foreign-but-authentic
   records (H5, H6a, H6b, H9) because it never verifies provenance; it also
   rejected all honest partial-evidence cases (10 false rejects).
3. **Signatures + cross-record joins prevent all unsupported promotions.**
   V3-full: 0/58 level-6 false promotions, 0 overclaims, 0 false rejects on
   honest partial claims, while accepting all H0/H7 honest cases at their
   adjudicated levels.
4. **Claim-specific evaluation is feasible.** H7 showed both V3 systems can
   accept honest claims at levels 1–5 at exactly those levels; V2 cannot
   (missing-evidence rejection), which is a soundness/utility trade-off
   difference, not merely sensitivity.
5. **H10 generalizes the mechanism** to a dev-unseen reference-replay pattern
   and confirms the 2x2 interpretation: authenticity without joins is
   insufficient; joins without authenticity are insufficient; the pair
   catches every constructed composition while preserving honest partial
   claims.

Novelty framing (unchanged): the binding principle is anticipated by
RFC 9334 (RATS) and in-toto; the contribution here is the empirical
measurement of false promotability in AI-authored cryptographic-exploit
evaluation and the claim-specific evaluator comparison, not a new binding
mechanism.

## 8. Integrity and limitations

- Frozen bytes verified before both passes (`freeze/HEB_IARB_FREEZE.json`,
  sha256 `cc0fde9e750b84baea80fe3d9bf58f6ca88ae53370b769b74508856de59e0570`).
- Protected files unchanged before/after both passes
  (`RESULTS_LOCK.json 4b152f18…`, `RESULTS_LOCK_H1PC.json 8221cb86…`,
  `paper/main.tex 51f97748…`, `paper/main.pdf fd9a5889…`).
- Manifest: model_calls 0, provider_calls 0, network none; $0 spend.
- Integrity note: the held-out tree was wiped by a crashed generator run
  *before* the blind pass (build wipes the tree before constructing cases); the
  generator's `F` global-name bug was fixed pre-pass. The generator is not part
  of the freeze; frozen bytes were re-verified OK on every run.
- H10 was appended to the reporting attack-family set for G-B2 only (broadens
  the measured set; thresholds unchanged). Documented pre-post comparison.
- Limitations: synthetic fixtures, self-designed faults, one deterministic
  pass per stage, trust model assumes keys/anchor outside composer control;
  external validity limited to systems with this evidence shape.

## 9. Reproduction

```
cd sp2027/analysis/experiment_b_20261019
python3 eb_fixtures.py                     # dev set (54 cases)
python3 eb_runner.py                       # dev pass
python3 heldout/eb_iar_b_heldout.py        # held-out set (58 cases)
python3 heldout/eb_iar_b_heldout_runner.py # single blind held-out pass
```

## 10. Artifact hashes

| Artifact | sha256 |
|---|---|
| freeze/HEB_IARB_FREEZE.json | `cc0fde9e750b84baea80fe3d9bf58f6ca88ae53370b769b74508856de59e0570` |
| eb_crypto.py | `9243529ef019cd899023600cf29c1c585d712bd04048501010a70fdae4027a4c` |
| eb_fixtures.py | `9c9645273bd0990171a542a4822b33a309c9ee3703ce85e6994e35ab8febee55` |
| eb_v3_sig.py | `6b17954b0441dcf7ef0973d7e9c755df9707658119290a9d4e4bb5db64727329` |
| eb_v3_full.py | `6c7d0d8b564e0d0bdeace6ba59be90cd03cb9a8700df7649d6366a97ff280670` |
| eb_adjudicator.py | `c7c6a62cd6e288a4e1f92d910ed70eceafa621d8c3389eb09242c3e0f893425e` |
| eb_runner.py | `a7c9031ea27f886456d37751d161f1dcefca0fc838ea7d6acca54d5c4d8238a3` |
| dev labels | `1a7f440077e7f1ce8dad64fd9ba69f8563a726f7cd20e99a209b4fc0d05f66be` |
| dev results | `032c93bedb65fec8cadd80d1ec2b0af5e6bb1e30ac4e30e6d105eb14eebcdf15` |
| held-out results | `be08433db0da8ded6bed2c5edc1730b11b204b828660c3775c0340c2b818f640` |
