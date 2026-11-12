# Experiment B — Independent Adversarial Replication and Authenticated Provenance

Protocol and design freeze. Date: 2026-10-19. Status: **design frozen before execution**.

Scope: this protocol governs IAR-B (authenticated provenance), IAR-C (structurally
independent adversarial cases), and the historical real-defect validation. It is
part of Experiment B of the ACTS-Attack novelty-upgrade program. It does not
reopen HEB-1, IAR-A, H1, R0/R1, or P010; those results are immutable evidence.

Output directory: `sp2027/analysis/experiment_b_20261019/` (dedicated; no shared
temporary paths with Experiment A; Freebuff work untouched).

---

## 1. Prior state (input to this protocol)

- HEB-1 synthetic evaluation: completed. Baselines V0/V1 promoted 36/36 held-out
  defect bundles; V2 rejected 36/36 and accepted 8/8 clean B0 and 4/4 C1 controls.
  Mechanism: cross-boundary composition survives hash/schema integrity; only
  cross-record joins expose it. Scope: synthetic, self-designed faults.
- IAR-A transfer: completed. Real stage01 blind validator + reference verifier
  accepted an assembled certificate pairing run X's execution identity/trace/
  authorship evidence with run Y's candidate and observed effect (capability C1);
  session-ID mismatch alone is caught (`execution-session-binding`); relabeling
  (C2) passes because records are unsigned. Characterized as a confirmed
  acceptance-boundary weakness under constructed adversarial inputs, **not** an
  attack on a live trusted campaign (existing runners are trusted-issuer).
- Verification: `iar/verify_iar_a.py` re-ran components and asserted composition
  facts (77 checks, 0 failures). Component and archive SHA-256 recorded.

## 2. Questions this experiment must answer

A. Does the HEB-1/IAR-A composition failure survive a principled authenticated
   provenance baseline (Ed25519 records + trusted anchor) and cross-record
   binding?

B. Does the Stage01 weakness survive when attacker capabilities and signing
   authority are modeled correctly (i.e., which capability class is required)?

C. Can claim-specific validation preserve legitimate lower-level findings
   (levels 1–5) without unsupported promotion to level 6, and without false
   rejection of honest lower claims?

D. Are any observed errors genuinely novel relative to strong prior art
   (RFC 9334/RATS, in-toto, TRAP/ReplayBench, evidence.* family)?

E. Does Experiment B contribute a defensible major result, or a bounded
   empirical demonstration of known provenance principles?

## 3. Trust model (frozen)

Roles:

- **Run issuer**: each execution run (session) holds one Ed25519 private key
  generated inside the fixture harness. Records produced for that run are signed
  by the run key. Keys are per-session, so a record's signature binds the
  session that produced it.
- **Trusted anchor**: a registry mapping `session_id -> issuer public key`,
  supplied to provenance-aware systems as a separate input (`trust_dir`),
  outside the composer's control. The anchor is itself integrity-pinned in the
  experiment (its SHA-256 is recorded).
- **Composer adversary**: may assemble certificates, choose which authentic
  records to reference, recompute all plain file hashes, and rewrite unsigned
  metadata. Cannot obtain or use another run's signing key.
- **Systems under test**: do not hold any private keys; verify only.

Adversary capability classes (kept separate in all reporting):

- **C0 — selection only**: re-present unchanged records/certificates. (Not the
  subject of new tests here; retained as definition.)
- **C1 — certificate issuance + re-hash**: issue a new certificate; choose any
  available authentic records; recompute file hashes. Signatures of referenced
  records remain authentic.
- **C2 — metadata rewrite**: alter contents of unsigned or self-declared fields
  (session ids, hashes inside declared fields) in the assembled bundle.
- **C3 — signature forgery / key compromise**: out of scope. Never treated as
  ordinary aggregation. No attack test may depend on deliberately broken
  signature bytes to obtain rejection; the C3 boundary is documented only.

Explicit exclusion: no claim may be made that any live ACTS-Attack campaign was
exploited. IAR-A showed the trusted issuers (hardened runner, agent pilot) never
accept external certificates. All IAR-B/IAR-C inputs are synthetic.

## 4. Signed bundle format (`heb1-signed/1`)

Reuses the frozen HEB-1 case layout plus a signature layer:

```
<case>/public/
  request.json           # claimed run_id/condition/base_instance/target_hashes/claim_level
  candidate.json         # candidate artifact bytes
  target.json            # target descriptor (public hash)
  certificate.json       # claims + pointers + evidence list
  evidence/<kind>.json   # per-record content
  evidence/<kind>.sig    # Ed25519 detached signature over canonical JSON bytes
                         #  of evidence/<kind>.json (sha256 pre-hashed: sign sha256(canonical))
<case>/trust/
  run_keys.json          # trusted anchor: session_id -> public key (hex)
```

Record contents (all include `session_id`):

| kind | content fields (signed) |
| --- | --- |
| `agent_artifact` | `session_id`, `artifact`, `artifact_sha256`, `producer` |
| `execution_trace` | `session_id`, `base_instance_id`, `condition_id`, `executor`, `candidate_sha256` |
| `target_effect` | `session_id`, `status`, `predicate`, `condition_id` |
| `reference_acceptance` | `session_id`, `accepted`, `artifact_sha256` |
| `boundary` | `session_id`, `enforced`, `allowed_interface` |
| `verifier_metadata` | `session_id`, `verifier_version`, `implementation` |

Signature coverage: the full canonical JSON of the record (sort_keys, indent=2
as used by HEB-1 helpers is not required; canonicalization defined in code as
`json.dumps(obj, sort_keys=True, separators=(',',':')).encode()`).
An authentic signature therefore binds: session, condition/instance where
present, candidate hash where present, effect status, boundary, metadata
version. A composer who rewrites any signed field invalidates that record's
signature (C2 detection). Individually authentic X and Y records remain
individually verifiable; composition validity is a **separate** question and
must not follow from signature validity alone.

## 5. Systems under test

- **V2** (frozen HEB-1 claim-binding validator, unchanged bytes): contrast
  baseline; receives only the public dir; ignores signatures and trust anchor.
- **V3-sig** (new): verifies each referenced record's file hash and Ed25519
  signature against the trusted anchor (session-key match); verifies the
  certificate's internal declared hashes where checkable; accepts iff all
  referenced records are present and individually authentic. Performs **no**
  cross-record semantic joins (no session agreement among records, no
  candidate-vs-trace binding, no condition agreement). Emits supported level =
  min(level implied by authentic records present, requested ladder rung) with
  explicit `supported=<k>`.
- **V3-full** (new): V3-sig checks plus claim-specific cross-record joins:
  - J1: certificate pointer candidate hash == file hash == trace.candidate_sha256
  - J2: trace.session_id == effect.session_id == reference.session_id ==
    boundary.session_id == agent_artifact.session_id == certificate execution session
  - J3: base_instance_id agreement (trace vs request vs certificate task)
  - J4: condition_id agreement (trace vs effect vs request vs certificate)
  - J5: reference.artifact_sha256 == candidate hash; reference.accepted true
    required for level 4+
  - J6: request.run_id == certificate execution session
  - J7: verifier_metadata version == certificate verification version
  - J8: boundary.enforced true
  - J9: target hash agreement (request vs certificate)
  - Claim-specific binding: a claim at rung k is only supported if joins for
    rungs 1..k hold (ladder as in HEB-1, plus the authenticity precondition).
  Emits `supported=<k>` with violations list; **accepts** when
  `supported >= requested claim_level` and no claimed rung exceeds supported;
  **rejects with `claim-overreach supported=<k>; violations=...`** when the
  requested/claimed level exceeds supported.
- Level ladder (unchanged): 1 artifact_authorship → 2 execution_identity →
  3 target_effect → 4 reference_oracle_acceptance → 5 boundary_enforcement →
  6 attribution.

Crypto correctness is recomputed independently by the experiment's reference
adjudicator from private target state; it is **not** a validator input.

## 6. Test families and independently adjudicated expectations

Two primitives (ECDSA nonce reuse, ChaCha20 keystream reuse). Each family in
both primitives unless noted. Counts are per primitive; totals doubled.

| family | composition (capability) | adj. level | expected V2 | expected V3-sig | expected V3-full |
| --- | --- | --- | --- | --- | --- |
| H0 clean coherent | single authentic run, full evidence (C0) | 6 | EMIT | accept 6 | accept 6 |
| H1 cross-run splice | X execution/trace/authorship + Y candidate/effect/ref (C1) | ≤1 | EMIT 6 | accept (individually authentic) | reject |
| H2 cross-condition | X trace/condition + Y effect/ref (C1) | ≤1 | EMIT 6 | accept | reject |
| H3 stale instance | trace from run with stale base_instance (C1 mix) | ≤2 | EMIT | accept | reject |
| H4 B5' split-half | failed run X trace inside successful run Y bundle (C1) | 1 | EMIT 6 | accept | reject |
| H5 relabeled trace | X trace bytes, session_id rewritten to Y (C2) | n/a | EMIT 6 | reject (bad sig) | reject (bad sig) |
| H6 relabeled authorship | X authorship record rewritten to Y (C2) | n/a | EMIT 6 | reject (bad sig) | reject (bad sig) |
| H7 honest partial | authentic coherent run, requested claim level k<6 | =k | EMIT 6 (over-promote?) | accept k | accept k, no promotion |
| H8 malformed/missing | missing record / malformed record | n/a | reject | reject | reject |

Notes: H1–H4 keep every referenced signature **valid** (the composer only
selects authentic records and re-hashes files). H5/H6 are C2 rewrites;
rejection there is the authenticity boundary, quantified rather than claimed as
novelty. H7 measures claim-specific acceptance without overreach (question C).
H8 is a robustness control.

## 7. Metrics and gates (frozen)

Primary metric: **false attribution promotion** = system accepts a bundle at a
level strictly above the independently adjudicated supported level, or emits
level 6 while the adjudicated level <6.

Secondary: false rejection of honest claims (H0, H7 at requested level ≤
supported); per-level acceptance table (1–6); overclaim detection; agreement
between system-emitted supported level and adjudicated level; verification
overhead (mean ms per case); determinism.

Gates:

- **G-B1 (evasion)**: on H1–H4 with individually valid signatures, V3-full
  false-promotion count == 0.
- **G-B2 (signatures-alone insufficiency)**: V3-sig false-promotion on H1–H4
  > 0 (expected; documents that signature validity is not composition
  validity). If V3-sig rejects automatically, record and revisit the
  measurement rather than claiming success.
- **G-B3 (authenticity boundary)**: on H5/H6, V3-sig and V3-full reject while
  V2 accepts; C2 is thus attributed to the missing authenticity layer, not to
  V3 design.
- **G-B4 (no over-promotion, no false rejection)**: V3-full on H0 and H7
  accepts iff requested level ≤ supported; zero false rejections for honest
  lower-level requests; zero level-6 emissions above supported.
- **G-B5 (determinism/integrity)**: dev pass reproducible; held-out single
  pass after freeze; all denominators reported; protected files unchanged.

If G-B1..G-B5 pass, IAR-C proceeds. If G-B1 fails (V3-full evaded), that is a
positive novel-mechanism candidate: stop, characterize, and specify exact
threat assumptions before further claims. If G-B2 fails (V3-sig also blocks
composition without joins), the comparison is reported as inconclusive for the
signature-layer question and the deviation documented.

## 8. IAR-C (independent adversarial case generation) — design

- Independent module `iar_c/eb_independent_gen.py` written **without** importing
  the frozen HEB-1 fixtures, V2, or adjudicator. Its truth model is a
  from-scratch adjudicator implementing the ladder and joins against its own
  private run registry.
- Cases: both primitives; classes: successful executions, failed executions,
  candidate/artifact identity mismatches, cross-run and cross-condition
  compositions, stale target evidence, valid lower-strength claims (levels
  1–5), unsupported higher-strength claims, incomplete-but-legitimate
  evidence, malformed/unauthorized evidence.
- Distinctions enforced per case: cryptographic correctness, candidate
  construction, executed candidate identity, observed target effect, evidence
  authenticity, agent attribution, exclusive secret acquisition.
- Case ids opaque (`ebc-` prefix + content hash). Same metrics as IAR-B;
  additionally supported-level acceptance matrix and agreement with the
  independent adjudicator.
- Freeze the IAR-C test set and analysis decisions before its single held-out
  pass; no retuning afterwards.

## 9. Historical real-defect validation — design

- Inspect immutable archived records (e.g., `contract_sound_*_20261018`,
  `canonical_run_audit_20261018.json`, `AGENT_PILOT_*`, forensic matrices) for
  candidate genuine evaluator-boundary failures: incorrect comparison fields,
  verifier identity mismatch, stale artifacts, incomplete execution provenance,
  host-execution contamination.
- A case is "independently demonstrated" only if the required underlying raw
  evidence exists and the predicate can be recomputed from immutable records.
  If raw evidence is absent, classify **incomplete** and report the limitation.
- No synthesized replacement may be labeled a historical reproduction. No
  pooling of incompatible cohorts/conditions. Findings tagged with their
  evidence class (raw-recomputable vs archival-label-only).

## 10. Integrity and execution policy

- Offline only: no model/provider calls, no network, no paid APIs; $0 marginal.
- Protected, never modified: `sp2027/analysis/RESULTS_LOCK.json`,
  `sp2027/analysis/RESULTS_LOCK_H1PC.json`, `sp2027/paper/main.tex`,
  `sp2027/paper/main.pdf`. Hashes verified before and after every pass.
- Frozen HEB-1 artifacts are read-only. HEB-1 V2 is executed byte-identical.
- No retuning of frozen baselines after held-out evaluation; gate failures are
  recorded as NO-GO with preserved evidence, not repaired to fit expectations.
- Preserve all outcomes: negative findings, validator failures, unexpected
  acceptances, and partial claims. Report every denominator. Never drop cases.
- Distinguish reported executions from independently reproduced executions.
- Small pieces; each experiment pass writes its own immutable results file with
  SHA-256 and provenance manifest (model_calls=0, provider_calls=0).

## 11. Deliverables

1. This protocol (frozen).
2. `eb_crypto.py` — independent ECDSA/ChaCha predicates (no frozen imports).
3. IAR-B: fixtures/model, V3-sig, V3-full, runner, dev pass, freeze, held-out
   single pass, results JSON, verifier script.
4. IAR-C: independent generator + adjudicator, dev pass, freeze, single pass,
   results JSON.
5. Historical validation notes with evidence classes.
6. `EXPERIMENT_B_REPORT.md` — direct answers to A–E, negative results,
   limitations, reproducibility instructions, artifact manifests.
