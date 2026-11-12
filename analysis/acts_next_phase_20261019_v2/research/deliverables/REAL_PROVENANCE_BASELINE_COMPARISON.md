# Stage 2 — Real Provenance Baseline Comparison

**Project:** ACTS-Attack  
**Stage:** Stage 2 — Real Provenance Baseline Comparison  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/`  
**Date:** 2026-10-20  
**Status:** EXECUTED — bounded cross-tool cryptographic and format-compatibility comparison

---

## 1. Scope and Non-Equivalence Warning

The Stage 1 evaluator and the three upstream tools do not decide the same proposition:

- **ACTS E2A** decides whether a particular producer execution causally produced a candidate that satisfies an independently evaluated cryptographic predicate.
- **Cosign** verifies signatures/attestations and, in keyless modes, transparency-log and certificate identity properties.
- **in-toto** verifies a signed software-supply-chain layout, authorized functionaries, links, and material/product rules.
- **SLSA Verifier** verifies SLSA provenance for an artifact against source/builder expectations.

Consequently, reporting upstream-tool “false positive/negative rates” on ACTS decisions would be scientifically invalid unless the ACTS experiment were first represented by a preregistered in-toto/SLSA policy. This stage therefore performs only comparisons that are semantically defensible:

1. independent verification of the exact ACTS signed bytes with Cosign;
2. negative tamper controls over those bytes;
3. direct native-format ingestion probes; and
4. a capability comparison describing which ACTS policy checks are not supplied merely by verifying a signature.

No Stage 1 artifact was modified.

---

## 2. Installed Upstream Implementations

The user authorized isolated installation. The tools were installed under `research/deliverables/`, not into the project environment.

| Tool | Version | Isolated location |
|------|---------|-------------------|
| in-toto | 3.1.0 | `.venv/` |
| securesystemslib | 1.5.1 | `.venv/` |
| cryptography | 50.0.2 | `.venv/` |
| Sigstore-Cosign | 2.6.5 | `.bin/cosign` |
| SLSA Verifier | 2.7.1 | `.bin/slsa-verifier` |

Approximate installed footprint at measurement time:

- Python environment: 76 MiB
- Cosign binary: 131.4 MiB
- SLSA Verifier binary: 31.8 MiB
- Combined: approximately 239 MiB (filesystem reporting/rounding applies)

---

## 3. Reproducible Harness and Inputs

**Harness:** `stage2_provenance/run_baseline.py`  
**Results:** `stage2_provenance/baseline_results.json`  
**Harness SHA-256:** `eeb075a68e5a924f1afd056f1b3aabc1bdd136e98172585cb8d21beaced53dbd`  
**Results SHA-256:** `7b9960e350cf2ac3a65e5ead1ddb48e31de08c2e35a8b6031bf15e12614cedf1`

The harness reads all 22 cases from:

`stage1_e2a/runs/20261020T065943Z_confirmatory/raw_results.jsonl`

For every available claim, observation, and reference envelope, it reconstructs the exact canonical byte string signed by the Stage 1 implementation:

- record: `json.dumps(unsigned_record, sort_keys=True, separators=(",", ":")) + "\n"`
- context: `json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`

Raw Ed25519 public keys from `stage1_e2a/frozen/issuers_public.json` are converted in temporary storage to standard SubjectPublicKeyInfo PEM. Temporary private material is neither needed nor created.

One deliberately incomplete case lacks an observation envelope and another case lacks one evidence envelope at the certificate layer. The test therefore covers **64 signed envelopes × 2 signature layers = 128 authentic signature checks**, not 132. Missing evidence is not synthesized.

---

## 4. Executed Results

### 4.1 ACTS control result

| Metric | Result |
|--------|--------|
| Cases | 22 |
| ATTRIBUTED_SUCCESS | 6 |
| REJECT | 12 |
| INCONCLUSIVE | 4 |
| False negatives | 0 |
| False positives | 0 |

### 4.2 Cosign independent signature verification

Each record signature and context signature was verified with:

`cosign verify-blob --offline --insecure-ignore-tlog --key <role.pem> --signature <base64-signature> <canonical-blob>`

| Check | Denominator | Passed / rejected as expected |
|-------|-------------|-------------------------------|
| Authentic signed blobs accepted | 128 | **128/128** |
| Tampered blobs rejected | 128 | **128/128** |

For each tamper control, the original signature and key were retained while a signed field was changed:

- record layer: `domain` modified;
- context layer: `attempt_id` modified.

This independently confirms the cryptographic integrity and tamper sensitivity of every signed envelope available in the 22-case run. It does **not** by itself confirm issuer authorization, cross-envelope causal consistency, the reference cryptographic predicate, or the final ACTS decision.

### 4.3 Native in-toto ingestion

The unmodified ACTS claim envelope was supplied directly as an in-toto layout. Result:

| Result | Cases |
|--------|-------|
| Native accept | 0/22 |
| Native reject | 22/22 |

Representative error: `InvalidMetadata`. This is expected: `e2a-signed-record/1` is not an in-toto root layout, and the certificate evidence is not emitted as in-toto link metadata. This is a format-compatibility result, **not evidence that in-toto is weaker or stronger**.

### 4.4 Native SLSA Verifier ingestion

The ACTS claim envelope and `candidate_output.json` were supplied directly to SLSA Verifier. The reproducible harness blocks external access and records 0/22 native accepts; the verifier attempted Sigstore trust-root access and failed closed in offline mode.

After user authorization, one online compatibility probe was executed for `H_OK_EC_01`. The verifier reached its normal Rekor lookup path and failed with:

`no matching entries found`

This is also expected. The ACTS claim is neither a SLSA provenance bundle nor a Rekor-published attestation for the candidate artifact. It is not valid to interpret this as an ACTS classification error.

---

## 5. Capability Comparison

| Property | ACTS E2A | Cosign verify-blob | in-toto | SLSA Verifier |
|----------|----------|--------------------|---------|---------------|
| Detached signature integrity | Yes | Yes | Yes (metadata signatures) | Yes (provenance signature/bundle) |
| Role-specific issuer policy | Yes, frozen ACTS policy | Key/certificate identity policy, not ACTS roles | Functionary keys/thresholds | Builder/source identity policy |
| Cross-envelope `(target, attempt, epoch, role, kind)` binding | Explicit ACTS check | No generic ACTS check | Can be modeled in layout/metadata, not native ACTS schema | Not an ACTS-native concept |
| Executed-source-byte binding | Yes, observer/memfd evidence | Only if represented in signed content | Materials/products and commands can model supply-chain steps | Artifact/build provenance, subject to predicate format |
| Candidate stdout/parse binding | Explicit | Only signed-byte integrity | Requires a designed link/layout representation | Requires a designed SLSA predicate representation |
| Independent cryptographic task predicate | Yes | No | Inspection could be designed | Not a general task-predicate evaluator |
| Transparency log | No | Supported; intentionally absent here | Not inherent | Sigstore/Rekor path used |
| Native ACTS envelope support | Yes | Blob-level only | No | No |

The central result is complementarity: upstream provenance systems provide mature metadata, identity, layout, builder, and transparency mechanisms, while ACTS E2A supplies a task-specific causal/predicate policy. A fair product-level comparison would require implementing the same ACTS policy as an in-toto layout/inspection or SLSA predicate and preregistering that translation before observing outcomes.

---

## 6. Negative Results and Limitations

1. **No native interoperability:** unmodified ACTS envelopes are not native in-toto or SLSA metadata.
2. **No Rekor entry:** the authorized online SLSA probe found no matching transparency-log entry.
3. **No product superiority claim:** this study does not establish ACTS superiority over in-toto, SLSA, or Sigstore.
4. **No matched policy translation:** therefore no cross-product false-positive/false-negative comparison is reported.
5. **Cosign scope is cryptographic:** 128/128 authentic and 128/128 tamper-control results validate signatures, not the entire ACTS attribution policy.
6. **Small bounded corpus:** all results concern the preregistered 22-case confirmatory inventory.

---

## 7. Determination

Stage 2 is complete as a bounded empirical comparison.

- The Stage 1 signature layer is independently interoperable with a genuine upstream verifier at the Ed25519 blob-verification level: **128/128 authentic checks passed**.
- Negative controls were perfect in this corpus: **128/128 altered blobs were rejected**.
- Direct native-format interoperability is absent: **0/22 in-toto accepts**, **0/22 offline SLSA accepts**, and the one authorized online SLSA probe found no Rekor entry.
- These outcomes neither prove nor disprove relative product security. They identify a representation gap and precisely bound what was compared.