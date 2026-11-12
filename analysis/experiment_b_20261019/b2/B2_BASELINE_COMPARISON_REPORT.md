# B2 Baseline Comparison Report

## 1. Determination

B2 produced a **positive, bounded measurement**:

> On the frozen IAR-B corpus, a content-addressed-only provenance model
> accepted false level-6 claims in the deterministic-artifact class, while the
> same model with explicit execution-session joins rejected them and preserved
> honest partial claims.

This is stronger evidence for the deterministic-artifact equivocation mechanism
than Experiment B alone. It is **not** evidence that an actual in-toto, SLSA,
or RATS implementation was defeated. The new verifiers are offline models of
design classes, not the established products. It is also not, by itself, a new
mechanism or superiority over complete provenance systems: explicit execution
identity/freshness binding is already represented in the relevant prior art.

The live-campaign and untrusted-ingestion objectives remain unmet.

## 2. Reproducibility and integrity

| Item | Value |
|---|---|
| Protocol | `B2_PROTOCOL.md`, SHA-256 `adc953619d13bf2f06e03305dff6616d13477a2bb6efe7741168dae7eabbe18b` |
| Active freeze | `freeze/B2_FREEZE.json`, SHA-256 `22101d2ca36b53f9103a044cc969fd8f4127c96c18b97b8fbf7afddb9eeeb785` |
| Superseded freeze | `freeze/B2_FREEZE_v1_superseded.json`, SHA-256 `b965913dc7d94b0e5e3c99c14f2a5228fb9b0908e88809234501afe94ab2e023` |
| Preserved pass | `runs/20261019_140814/results.json` |
| Results SHA-256 | `0c492313aa5cfe702b18dff9819287a13e9d156547c3313d795ef51bea19c014` |
| Cases | 54 dev + 58 held-out = 112 |
| Model/provider/network calls | 0 / 0 / 0 |
| Marginal spend | $0 |

The first runner attempt crashed before recording any verdict because `adj` was
missing from the overhead accumulator. No result file was produced. That
failure is preserved in `B2_FREEZE_v1_superseded.json`; the active freeze records
the pre-pass repair and the corrected runner hash. The preserved pass then ran
without code changes.

All gates passed for both case sets. There were no fixture failures, no
determinism mismatches, and no malformed baseline verdicts. The four protected
file hashes were unchanged before and after execution.

## 3. Systems

The comparison includes the frozen references:

- V2: claim binding without signatures.
- V3-sig: signed records and content hashes without semantic joins.
- V3-full: signed records plus cross-record joins and session binding.
- Independent adjudicator: generator-side truth model.

The new systems are design-class models:

- `digest-only`: D1–D17 content, hash, signature, and declared-consistency
  checks; no session joins.
- `digest-session`: `digest-only` plus S1–S6 execution-session joins.
- `abl-authjoin`: removes authorship/session binding S1.
- `abl-refjoin`: removes reference/session binding S4.
- `abl-tracejoin`: removes trace/session binding S2.
- `abl-executor`: removes declared executor consistency D7.

The corpus has one session key per run and no explicit nonce-bearing evidence
field. Therefore this pass models the binding dimensions; it does not evaluate
literal product-specific nonce protocols or multi-party key layouts.

## 4. Results

### 4.1 False promotions and overclaims

| Case set | System | Level-6 false promotions | False-promotion families | Overclaims |
|---|---|---:|---|---:|
| Dev (54) | V2 | 16 | H5, H6a, H6b, H9 | 16 |
| Dev | V3-sig | 24 | H1, H2, H3, H4, H6b, H9 | 24 |
| Dev | V3-full | 0 | — | 0 |
| Dev | `digest-only` | **4** | **H6b** | **4** |
| Dev | `digest-session` | 0 | — | 0 |
| Dev | `abl-authjoin` | 4 | H6b | 4 |
| Dev | `abl-refjoin` | 0 | — | 0 |
| Dev | `abl-tracejoin` | 0 | — | 0 |
| Dev | `abl-executor` | 4 | H9 | 4 |
| Held-out (58) | V2 | 16 | H5, H6a, H6b, H9 | 16 |
| Held-out | V3-sig | 28 | H1, H2, H3, H4, H6b, H9, H10 | 28 |
| Held-out | V3-full | 0 | — | 0 |
| Held-out | `digest-only` | **8** | **H6b, H10** | **8** |
| Held-out | `digest-session` | 0 | — | 0 |
| Held-out | `abl-authjoin` | 4 | H6b | 4 |
| Held-out | `abl-refjoin` | 4 | H10 | 4 |
| Held-out | `abl-tracejoin` | 0 | — | 0 |
| Held-out | `abl-executor` | 4 | H9 | 4 |

The observed family sets matched every pre-registered prediction. In
particular, H10 was accepted by `digest-only` but rejected by `digest-session`.
This is the targeted result: Z's authentic reference record has a valid
signature and the same artifact digest as Y's candidate, but the reference
event belongs to session Z rather than credited session Y.

### 4.2 Honest partial claims and agreement

| Case set | System | False rejects | Agreement with adjudicated level | Mean overhead |
|---|---|---:|---:|---:|
| Dev | V2 | 10 | 4/54 | 52.51 ms |
| Dev | V3-sig | 0 | 14/54 | 69.23 ms |
| Dev | V3-full | 0 | 14/54 | 68.79 ms |
| Dev | `digest-only` | 0 | 14/54 | 70.43 ms |
| Dev | `digest-session` | 0 | 14/54 | 72.22 ms |
| Held-out | V2 | 10 | 4/58 | 49.86 ms |
| Held-out | V3-sig | 0 | 14/58 | 66.02 ms |
| Held-out | V3-full | 0 | 14/58 | 68.50 ms |
| Held-out | `digest-only` | 0 | 14/58 | 69.01 ms |
| Held-out | `digest-session` | 0 | 14/58 | 67.41 ms |

Both new principal models accepted H0 at level 6 and every H7 honest partial
claim at its requested level. Neither introduced false rejects on those cases.

### 4.3 Minimal-binding ablation

| Removed binding | Result on held-out | Interpretation |
|---|---|---|
| S1 authorship/session | 4 H6b false promotions | Foreign authentic authorship can be substituted when the candidate digest is unchanged. |
| S4 reference/session | 4 H10 false promotions | Foreign authentic reference acceptance can be substituted when the candidate digest is unchanged. |
| S2 trace/session | 0 false promotions | H4 remains caught here by D7 executor mismatch in this corpus. |
| D7 executor consistency | 4 H9 false promotions | Certificate executor rewrite is then accepted. |

This localizes the H10 failure to the reference-event/session join, not to
cryptographic signature validity or candidate digest integrity.

## 5. Mechanism evidence

For H10, the two honest success runs (`y` and `z`) operate on the same public
instance. The recovered cryptographic result is instance-determined, so their
candidate files are byte-identical and have the same `candidate_sha256`.

The H10 bundle contains:

- Y's candidate and other evidence;
- Z's authentic `reference_acceptance` record;
- a credited execution session of Y;
- valid signatures for every included record.

Content-addressed checks cannot distinguish the producer of the identical
candidate bytes. The session check `reference.session_id == credited session`
does distinguish them. The result was independently adjudicated as supported
level 3, while `digest-only` promoted the submitted level-6 claim.

This is an independently reproducible counterexample to **digest-only model
verification on this evidence shape**. It is not an independently reproduced
failure of an actual complete provenance product.

## 6. What this does and does not establish

Established by B2:

1. The deterministic-artifact hypothesis predicts a real false-promotion
   pattern in the frozen evaluator corpus.
2. A digest-only model accepts H6b/H10 false promotions while preserving all
   content and signature checks.
3. Explicit execution-session binding rejects those promotions with no observed
   false rejects on honest partial claims.
4. The H10 result survives a dev-unseen held-out pass and the ablation table
   identifies S4 as necessary for that family.

Not established by B2:

1. A previously unrecognized mechanism. RATS freshness/nonce binding,
   in-toto-style authorized functionaries, and related provenance work already
   contain the relevant execution-identity/replay defense dimension.
2. Superiority over actual established complete provenance systems. No actual
   in-toto, SLSA, or RATS product was executed; the compared systems are
   offline design-class models.
3. Live-campaign exploitation. The ACTS campaigns have no demonstrated
   untrusted certificate-ingestion path, and provider phase R0/R1 remains
   blocked pending explicit authorization and budget.
4. General real-world prevalence. The fixtures are synthetic, the fault model
   is self-designed, and the corpus has no literal nonce field or multi-party
   attestation layout.

Accordingly, B2 should be reported as a stronger empirical measurement and
counterexample for a known provenance-design gap, **not** as the exceptional
HEB-1 result originally sought.

## 7. Artifact index

- Protocol: `B2_PROTOCOL.md`
- Models: `b2_prov_baselines.py`
- Runner: `b2_runner.py`
- Active freeze: `freeze/B2_FREEZE.json`
- Superseded pre-pass freeze: `freeze/B2_FREEZE_v1_superseded.json`
- Preserved raw results: `runs/20261019_140814/results.json`

No protected paper files were modified. No network, model, or provider calls
were made. Nothing was committed.
