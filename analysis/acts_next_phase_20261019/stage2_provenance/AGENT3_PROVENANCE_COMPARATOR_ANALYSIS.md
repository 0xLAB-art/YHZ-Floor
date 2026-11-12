# AGENT3 — Provenance Comparator Analysis: in-toto, SLSA-verifier, Sigstore/Cosign, and RATS (RFC 9334) vs. the ACTS-Attack Evidence-Binding Contract

- **Agent:** AGENT3 (provenance-systems specialist), stage `stage2_provenance`
- **Date:** 2026-10-20
- **Working root:** `/mnt/nvme5/ACTS-Attack`
- **Task type:** READ-ONLY + local analysis, plus read-only HTTP GET of public upstream documentation
- **Status of the file:** analysis deliverable. No existing repository file was modified. No package was installed, no binary was downloaded, no authenticated or write request was made.

---

## 0. Method, scope, and epistemic status

### 0.1 What was done

1. Read the local project context (read-only) to establish **what exactly is being compared**: the ACTS-Attack harness contract (execute a candidate program → capture `candidate_output.json` → run an independent reference verifier → a validator decides whether to promote a final attributed success claim), and the project's *existing* offline "design-class model" baselines.
2. Read the primary upstream specifications and source trees for in-toto, slsa-verifier, cosign, and RFC 9334, and the SLSA specification.
3. Produced the fair-comparison contract (P1..P10) and a per-system applicability verdict.

### 0.2 Epistemic labels used throughout

| Label | Meaning |
|---|---|
| **[SPEC]** | Claimed by a primary upstream specification, cited by URL. |
| **[SRC]** | Observed in upstream source code, cited by file URL (or GitHub API path listing) at the upstream `main`/`develop` branch as of the retrieval date. |
| **[DOC]** | Claimed by upstream operator/user documentation, cited by URL. |
| **[PROJECT]** | Observed in this repository (read-only), cited by repository-relative path. |
| **[UNVERIFIED]** | Could not be confirmed from a primary source within this task's constraints. Treated as unknown, not as false. |
| **[ESTIMATE]** | A reasoned magnitude, not a measurement. No timing was performed because installation was not authorized. |

All upstream URLs were retrieved on **2026-10-20** unless stated otherwise.

### 0.3 The "local digest-only helper" — an explicit anti-confusion statement

This project already contains a local Python program that implements *models* of these design classes. It must not be described as in-toto, SLSA, or RATS, and this analysis does not do so.

- **[PROJECT]** `sp2027/analysis/experiment_b_20261019/b2/b2_prov_baselines.py`, lines 10–13, states verbatim:
  > "Faithful-model caveat (B2_PROTOCOL.md section 3): these are MODELS of design classes (in-toto/SLSA-style digest-complete verification; RATS-style freshness/execution-identity binding), implemented offline from the public descriptions of those design classes. They are NOT the actual products, and no network/pip access was used."
- **[PROJECT]** `sp2027/analysis/experiment_b_20261019/b2/B2_PROTOCOL.md` line 55 repeats the caveat and states that the frozen corpus "use[s] one session key per run for all roles, and evidence records carry no nonce/attempt field, so multi-party (distinct per-role keys) and literal nonce-carrier designs are only representable in the degenerate single-identity form."
- **[PROJECT]** `sp2027/analysis/experiment_b_20261019/b2/B2_BASELINE_COMPARISON_REPORT.md` §1 states: "It is **not** evidence that an actual in-toto, SLSA, or RATS implementation was defeated. The new verifiers are offline models of design classes, not the established products."

Consequence for this analysis: **the B2 baselines are the right instrument for the rows that in-toto cannot express, and the wrong instrument for the rows it can express.** The right next experiment (§8) is to replace the model with the real product *only* on the rows in-toto can natively express, and to keep the model for the rest, with the two never mixed in a single claim.

### 0.4 What is NOT claimed here

- No upstream product was executed, benchmarked, or defeated.
- No claim that any upstream product is vulnerable to the project's attack families.
- No claim of novelty over in-toto, SLSA, cosign, or RATS. The purpose is to establish *applicability* and to define a fair contract, not to claim an advantage.

---

## 1. The thing being compared (the ACTS harness contract)

**[PROJECT]** The comparison target is the harness described in `sp2027/analysis/contract_sound_exploitation_preregistration_v1.md` §3–§7 and instantiated in `sp2027/analysis/experiment_b_20261019/`:

- A *candidate program* (e.g. `candidate.py`) is executed by a harness under a fixed contract.
- It must emit a correct cryptographic answer; the harness captures `candidate_output.json`.
- An **independent reference verifier** (a separate process, `contract_sound_stage01_reference_verifier_v2.py`) evaluates the captured output.
- A **validator** (`contract_sound_stage01_validator_v2.py`) decides whether to promote a final *attributed success claim*, on a 6-rung ladder (`artifact_authorship`, `execution_identity`, `target_effect`, `reference_oracle_acceptance`, `boundary_enforcement`, `attribution`) with `PROVEN` / `OBSERVED` / `ACCEPTED` / `NOT_ESTABLISHED` / `NOT_OBSERVED` / `REJECTED` value enums.
- The project's B2 study already compared three local systems on a frozen 112-case corpus (54 dev + 58 held-out): `V2` (claim binding, no signatures), `V3-sig` (signatures, no joins), `V3-full` (signatures + digest continuity + session joins), and the two new design-class models `digest-only` / `digest-session`.
- **[PROJECT]** Measured B2 result: `digest-only` produced **8 level-6 false promotions on the held-out 58** (families H6b, H10); `digest-session` produced **0**; `V3-full` produced **0**. Preserved pass: `sp2027/analysis/experiment_b_20261019/b2/runs/20261019_140814/results.json`, SHA-256 `0c492313aa5cfe702b18dff9819287a13e9d156547c3313d795ef51bea19c014`; protocol SHA-256 `adc953619d13bf2f06e03305dff6616d13477a2bb6efe7741168dae7eabbe18b`; freeze `22101d2ca36b53f9103a044cc969fd8f4127c96c18b97b8fbf7afddb9eeeb785`. (`B2_BASELINE_COMPARISON_REPORT.md` §2.)

The "provenance" analogue of this harness is: *a party that did not produce the artifact observes a property of it and signs that observation; the claim is only promoted if that signed observation is bound to the exact bytes, the exact attempt, and the exact target state.*

---

## 2. IN-TOTO — what the real product guarantees

### 2.1 The objects

| Object | What it is | Primary source |
|---|---|---|
| **Layout** | Project owner's signed policy: `expires`, `readme`, `keys` (functionary public keys), `steps`, `inspect`. | [SPEC] https://github.com/in-toto/docs/blob/master/in-toto-spec.md#43-file-formats-layout |
| **Step** | `{_type, name, threshold, expected_materials[], expected_products[], pubkeys[], expected_command}` | [SPEC] same URL, §4.3.1 |
| **Inspection** | `{_type, name, expected_materials[], expected_products[], run[]}` — a command the **client** executes at verification time. | [SPEC] same URL, §4.3.2 |
| **Link** | The signed record a functionary produces: `{_type, name, command, materials{}, products{}, byproducts{}, environment{}}` | [SPEC] same URL, §4.4 |
| **Metablock / DSSE Envelope** | Container carrying signatures. In in-toto 3.x both the traditional metablock and a DSSE envelope are supported. | [DOC] https://in-toto.readthedocs.io/en/latest/model.html |

**Key derivation.** [SPEC] "The KEYID of a key is the hexadecimal encoding of the SHA-256 hash of the canonical JSON form of the public key." (in-toto-spec.md §4.2.1)

**Hash object.** [SPEC] "A hash object is a dictionary that specifies one or more hashes, including the cryptographic hash function. For example: `{ "sha256": HASH, ... }`" (§4.2.3). Supported signing methods in the reference implementation: `RSASSA-PSS` (SHA-256), `ed25519`, `ecdsa` (nistp256). [SPEC §4.2.1]

### 2.2 The verification algorithm and exit codes

[DOC] `in-toto-verify` performs: layout signature check → layout expiry check → link metadata load → link signature verification against layout keys → sublayout recursion → **soft** command alignment → threshold artifact constraints → artifact-rule processing → execution of inspection commands → inspection artifact-rule processing.
(https://in-toto.readthedocs.io/en/latest/command-line-tools/in-toto-verify.html)

[SRC] The Python API `in_toto.verifylib.in_toto_verify` documents the same 11-step order, and states:
> "7. Soft-verify alignment of reported and expected commands. Note: verification does not fail if commands don't match, instead a warning is logged as per the in-toto specification"
(https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/verifylib.py)

[DOC] Exit codes: **0 = verification passed, 1 = verification failed, 2 = wrong arguments.**
(https://in-toto.readthedocs.io/en/latest/command-line-tools/in-toto-verify.html)

[SRC] The CLI catches *every* exception and exits 1, but logs the exception class name:
```python
except Exception as e:  # noqa: BLE001
    LOG.error("(in-toto-verify) %s: %s", type(e).__name__, e)
    sys.exit(1)
```
(https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/in_toto_verify.py)
→ **The distinction between failure classes is recoverable from stderr, but *not* from the exit code.**

[SRC] The typed exception hierarchy is (`https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/exceptions.py`):
`SignatureVerificationError`, `LayoutExpiredError`, `RuleVerificationError`, `ThresholdVerificationError`, `BadReturnValueError`, `LinkNotFoundError`, `UnsupportedKeyTypeError`, `PrefixError`, `InvalidMetadata` — all subclasses of `securesystemslib.exceptions.Error`; plus `securesystemslib.exceptions.FormatError` for malformed input.

### 2.3 What in-toto actually proves about the four questions asked

#### (a) Program source bytes
**Partially — natively.** The link's `materials` map is a `{path: hash-object}` of files recorded **before** the step command runs; `products` is the same **after**. [DOC] https://in-toto.readthedocs.io/en/latest/command-line-tools/in-toto-run.html ("It records paths and hashes of 'materials' (files before command execution) and 'products' (files after command execution)").

The *authorization* of those bytes is enforced by the project owner's **artifact rules**, which are a genuine native mechanism:
- `MATCH <pattern> [IN <src-prefix>] WITH (MATERIALS|PRODUCTS) [IN <dst-prefix>] FROM <step>` — binds step N's product to step N+1's material/product, with path relocation support. [SPEC] in-toto-spec.md §4.3.3.
- `MODIFY <pattern>` — "products matched by the pattern must appear as materials of this step, **and their hashes must not be the same**." [SPEC] §4.3.3. (Implementation: `verify_modify_rule`, verifylib.go→ `verifylib.py`.)
- `CREATE`, `DELETE`, `ALLOW`, `DISALLOW`, `REQUIRE` — [SPEC] §4.3.3.
- Processing semantics: firewall-like sequential queue consumption; implicit trailing `ALLOW *`; "By explicitly specifying `DISALLOW *`, in-toto verification fails if an artifact was not consumed by an earlier rule." [SPEC] §4.3.3.1.

**What in-toto does NOT prove about source bytes:** it does not attest *which* bytes were compiled into the product unless the project owner writes the rules; `expected_command` is explicitly untrusted ("in a case where a functionary's key is compromised, this field can easily be forged ... and thus it should not be trusted for security checks", [SPEC] §4.3.1) and a mismatch is only a warning. The `environment` block is opaque and unverified ([SPEC] §4.4: "The format of the environment information is not mandated ... but we recommend to store ..."; and §4.4.1 says the values "can be used to detect mistakes during compilation or invalid hosts" — not to make a security decision).

#### (b) Exact execution environment
**No.** The `environment` dictionary is explicitly opaque, is not part of the default verification routine, and the spec's own framing is diagnostic ("These values can be used to detect mistakes during compilation or invalid hosts carrying out steps"). [SPEC] §4.4, §4.4.1. There is no environment digest, no container digest, no toolchain attestation in the in-toto model.

#### (c) Runtime output
**No — and this is a hard limitation.** [SPEC] §4.4: "The `byproducts` field is an opaque dictionary that contains additional information about the step performed. **Byproducts are not verified by in-toto's default verification routine.**" `stdout`, `stderr`, `return-value` are captured by `in-toto-run` but are *not* checked by `in-toto-verify`. So in-toto has **no native mechanism** that observes what a program printed, returned, or wrote at runtime, other than the digests of files that the project owner nominated as `materials`/`products`.

#### (d) A downstream final claim
**No.** in-toto's verification result is a **boolean** (all steps + inspections passed) plus a summary `Link` object of the chain's materials/products. `in_toto_verify` "Returns: A Link object, which summarizes the materials and products of the overall software supply chain." [SRC] verifylib.py docstring. There is no multi-rung, partially-satisfiable claim ladder and no notion of a *claim* being promoted to a level. **Our ladder semantics are entirely our own.**

### 2.4 in-toto's own documented limitations (quoted, not paraphrased)

These are the load-bearing quotes for the honest comparison.

1. **The functionary is trusted; in-toto attests to its report, not to reality.** [SPEC] §1.5.2 Non-goals: "We are not trying to protect against a functionary (or actor in the supply chain) who unwittingly introduces a vulnerability while following all steps of the supply chain as designed. We are trying to prevent such functionaries from performing operations other than the ones intended for a supply chain. ... We assume that there will not be two colluding (or deceived) developers who jointly introduce a vulnerability." And §1.5.3: "Finally, we recommend separating the mechanisms responsible for in-toto metadata generation from those executing the steps themselves."
   → The project's H6b/H10 attack family (substituting an *authentic* record produced by a different, honest run) is **inside** in-toto's threat model, and in-toto's answer is: the layout defines who may sign which step. in-toto's answer does *not* include "which attempt".
2. **Replay of an unexpired layout is explicitly out of scope.** [SPEC] §1.5.2: "Finally, in-toto inherently does not protect against attackers replaying older, as-yet unexpired layouts. To ensure the right layouts are used during the verification workflow, we recommend using a system like The Update Framework (TUF)..."
3. **No key-revocation / key-age semantics.** [SRC] verifylib.py: "in-toto does not rely on the creation time, revocation status, and usage flags for PGP keys. To revoke or otherwise affect the usage of a key, the supply chain owner must sign a new layout with the corresponding changes." [DOC] same statement at https://in-toto.readthedocs.io/en/latest/command-line-tools/in-toto-verify.html.
4. **No metadata-attribute integrity.** [SPEC] §1.5.2: "in-toto's artifact integrity guarantee is based on bit-for-bit equivalence of artifact contents. in-toto does not record or verify any accompanying artifact metadata such as file permissions and timestamps."
5. **No judgment of layout quality.** [SPEC] §1.5.2: "it is possible to configure the supply chain layout so that no code review is performed and a package is built on an untrusted server --- which is an incredibly insecure configuration. While this may be visible to users installing the software, in-toto's role is not to judge or block layouts that are insecure."
6. **Inspections are the client-executed checks; their failure mode is a non-zero exit.** [SRC] `BadReturnValueError` — "Indicates that a ran command exited with non-int or non-zero return value." [SRC] verifylib.py `_raise_on_bad_retval`.
7. **Unauthorized / badly signed links are *skipped*, not reported as contradictions.** [SRC] verifylib.py `verify_link_signature_thresholds`: "Skipping link. Keyid '%s' is not authorized to sign links for step '%s'"; "Skipping link. Broken link signature with keyid '%s'". The only surfaced error is `ThresholdVerificationError` ("Step '%s' requires at least '%d' links validly signed by different authorized functionaries. Only found '%d'"). → **in-toto collapses "contradictory evidence" into "insufficient evidence" at the threshold step.** This is a material weakness for contract row P10 and must be reported as such.
8. **Threshold semantics.** [SRC] "Links signed by different subkeys of the same main key are counted only once towards the threshold." [SPEC] §4.3.1: THRESHOLD "is intended to be used for steps that require a higher degree of trust, so multiple functionaries must perform the operation and report the same results."

### 2.5 Which in-toto guarantee corresponds to each of the four asks

| Ask | in-toto construct | Native? |
|---|---|---|
| **Source** (which bytes were consumed) | link `materials` + owner-defined `MATCH`/`MODIFY`/`CREATE`/`DISALLOW` rules | **Yes**, but only as far as the project owner writes the rules; no `expected_command` enforcement (warning only) |
| **Execution step** (who performed it, in what order) | layout `steps[]` with `pubkeys[]` + `threshold`; link `name` binds a link to a step; `MATCH ... FROM <step>` chains the steps | **Yes** for identity/order-of-record; **No** for "the command really ran" |
| **Artifact origin** (which bytes came out of which step) | link `products` + `MATCH`/`MODIFY` rules over digests; `expected_command` is untrusted; `byproducts`/`environment` unverified | **Yes** for digest continuity; **No** for runtime behaviour or environment |
| **Signed evidence** | metablock / DSSE envelope over the canonical JSON of the link; keyid = SHA-256 of canonical public key | **Yes** |

### 2.6 Offline behaviour of in-toto

[DOC] "The verification workflow is performed in isolation and does not rely on information about keys that are available through external sources." (https://in-toto.readthedocs.io/en/latest/command-line-tools/in-toto-verify.html)
[SRC] Same statement in `in_toto_verify.py` docstring, plus: "in-toto's verification workflow directly uses the key for verifying signatures. It does not communicate with external sources of information for specific attributes about keys. This ensures that verification can be performed in isolation."
→ **in-toto is the only one of the three products that is fully offline-capable by design, with no trust-root bootstrapping problem.**

---

## 3. SLSA VERIFIER — what the real product guarantees, and why it does not apply

### 3.1 Identity, versions, status

- [DOC] Latest release: **v2.7.1**, released 2025-06-27 (https://github.com/slsa-framework/slsa-verifier/releases/tag/v2.7.1).
- [DOC] **Maintenance status:** the project README opens with:
  > "This project is **no longer actively maintained**. We are working on guidance and simpler tooling to replace it. If you are verifying attestations for GitHub Actions, we suggest generating them with GitHub artifact attestations ... and verifying them with `gh attestation verify`."
  (https://github.com/slsa-framework/slsa-verifier/blob/main/README.md)
- [DOC] Supported provenance producers: "1. [SLSA generator] (slsa-github-generator) 2. [Google Cloud Build (GCB)]" (same README, "It currently supports verifying provenance generated by:").

### 3.2 Supported provenance formats

[SRC] The verifier's provenance parsers live in `verifiers/internal/gha/slsaprovenance/` and comprise exactly `v0.2/` and `v1.0/` sub-packages, with `iface/` and `common/`:
https://github.com/slsa-framework/slsa-verifier/tree/main/verifiers/internal/gha/slsaprovenance
→ **v0.2 and v1.0 SLSA provenance predicates only.** No v1.1 / v1.2 predicate support in v2.7.1.

[SPEC] For context: the SLSA v1.0 provenance predicate page is marked "**Status: Retired**", and the site states "Version 1.2 is the current version" (https://slsa.dev/spec/v1.0/provenance; current: https://slsa.dev/spec/v1.2/provenance).

[SRC] The only verifier back-ends are `gcb`, `gha`, `vsa`: https://github.com/slsa-framework/slsa-verifier/tree/main/verifiers/internal

### 3.3 The policy model (roots of trust + expectations)

[SPEC] SLSA's verification model is a three-step procedure (https://slsa.dev/spec/v1.0/verifying-artifacts):

1. **Bootstrapping the verifier:** "Configure the verifier's roots of trust, meaning the recognized builder identities and the maximum SLSA Build level each builder is trusted up to." The example root-of-trust object binds `(publicKey, builderId) → slsaBuildLevel`, or a `sigstore` block binding a Fulcio/Rekor root plus a `subjectAlternativeNamePattern` to a `builderId`.
2. **Verifying provenance for an artifact:** (i) verify the envelope's signature against the roots of trust; (ii) "Verify that statement's `subject` matches the digest of the artifact in question"; (iii) verify `predicateType == https://slsa.dev/provenance/v1`; (iv) "Look up the SLSA Build Level in the roots of trust, using the recognized public keys and the `builder.id`, defaulting to SLSA Build L1."
3. **Checking expectations:** compare against expected values for *builder identity*, *canonical source repository*, *buildType*, and *externalParameters*. The spec adds: "Verification tools SHOULD reject unrecognized fields in `externalParameters` to err on the side of caution."
4. **(Optional) Recursive dependency checking:** "Note that SLSA v1.0 does not have any requirements on the completeness or verification of `resolvedDependencies`."

Threat coverage per the same page: threat "E" (build compromise) is addressed only at L3 and "assum[es] you trust the build platform"; "IMPORTANT: SLSA Build L3 does **not** cover compromise of the build platform itself, such as by a malicious insider"; "F" (post-build tampering of artifact/provenance) is covered by L2 subject+signature verification; "G"/"H" (registry compromise, in-transit compromise) are covered by consumer-side verification.

### 3.4 The CLI surface (and what is *not* there)

[SRC] `cli/slsa-verifier/verify/options.go`:
- `verify-artifact` flags: `--build-workflow-input`, `--builder-id`, `--print-provenance`, `--provenance-path`, `--source-branch`, `--source-tag`, `--source-uri`, `--source-versioned-tag`. **`--source-uri` is `MarkFlagRequired("source-uri")`.** `--source-tag` and `--source-versioned-tag` are mutually exclusive.
- **There is no `--artifact-digest` flag.** The artifact digest is *implicit*: [SRC] `verify_artifact.go` computes `computeFileHash(artifact, sha256.New())` and passes it as `options.ProvenanceOpts.ExpectedDigest`; the verifier then requires it to equal the provenance's subject digest (error sentinel `ErrorMismatchHash = "artifact hash does not match provenance subject"`, https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/errors/errors.go).
- `verify-vsa` flags: `--attestation-path`, `--public-key-id`, `--public-key-path`, `--resource-uri`, `--subject-digest` (repeatable), `--verified-level` (repeatable), `--verifier-id`, `--print-attestation`. `--subject-digests`, `--attestation-path`, `--verifier-id`, `--resource-uri`, `--public-key-path` are required.
- **There is no `--trusted-root` flag in v2.7.1.** The trust material is hard-wired: [SRC] `verifiers/utils/sigstore_tuf.go` uses `sigstoreTUF.DefaultClient()` and `sigstoreRoot.NewLiveTrustedRoot(sigstoreTUF.DefaultOptions())`. [SRC] sigstore-go `pkg/tuf/options.go` `DefaultOptions()` sets `opts.Root = DefaultRoot()` (an **embedded** `root.json` for the public-good instance), `opts.CachePath = ~/.sigstore/root`, and `opts.RepositoryBaseURL = DefaultMirror` (network). → first use needs network; afterwards the TUF metadata is cached under `~/.sigstore/root`.

[DOC] Exit behaviour: `PASSED: SLSA verification passed` / `FAILED: SLSA verification failed: <err>` with exit 1 on failure (https://github.com/slsa-framework/slsa-verifier/blob/main/README.md; https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/cli/slsa-verifier/verify.go).

### 3.5 The one genuinely interesting sub-command: `verify-vsa`

[DOC] The README's "Verification Summary Attestations (VSA)" section, and the "Caveats" subsection, state: "This support does not work yet with VSAs wrapped in Sigstore bundles, only with simple DSSE envelopes. With that, we allow the user to pass in the public key."

[SRC] `verifiers/internal/vsa/verifier.go` `VerifyVSA` performs, following https://slsa.dev/spec/v1.1/verification_summary#how-to-verify:
1. verify the envelope signature ("implicit because we accept a user-provided public key");
2. match the subject digests;
3. match the verifier ID;
4. match the expected resource URI;
5. "confirm the slsaResult is PASSED" (sentinel `ErrorInvalidVerificationResult = "verificationResult is not PASSED"`);
6. match the verified levels;
> "no other fields are checked."

[SRC] The VSA predicate schema parsed by the verifier is fixed (`verifiers/internal/vsa/v1.0/vsa.go`): `verifier{id,version}`, `timeVerified`, `resourceUri`, `policy`, `inputAttestations[]`, `verificationResult`, `verifiedLevels[]`, `dependencyLevels{}`, `slsaVersion`; `predicateType == "https://slsa.dev/verification_summary/v1"`.

**Why this matters for us:** `verify-vsa` is the *only* slsa-verifier sub-command that is (i) fully offline (user-supplied public key, plain DSSE envelope, no Sigstore, no Rekor), and (ii) structurally the same *shape* as our "independent reference verifier signs a verdict bound to the candidate's digest" step — a **second party** (not the artifact producer) signs a **PASSED/FAILED verdict** bound to a **subject digest**. This is the closest existing product analog to the project's `reference_oracle_acceptance` rung.

**Why it is still not a drop-in fit:** the VSA's `verificationResult` semantically means "this verifier verified *provenance* at these SLSA levels", not "this oracle evaluated a candidate's cryptographic answer". Our verdict bit would have to be transported in a field whose meaning the verifier does not check, or be mapped onto `verificationResult` (a schema abuse). The *mechanism* is native; the *semantics* are ours. This must be reported as **partial (P)** with an explicit note, never as "SLSA verifies our oracle verdict".

### 3.6 What SLSA / slsa-verifier does NOT cover (relevant to our contract)

- **Runtime exploit attribution.** SLSA is a *build* attestation framework: "Provenance is an attestation that a particular build platform produced a set of software artifacts through execution of the `buildDefinition`." [SPEC] https://slsa.dev/spec/v1.0/provenance. There is no concept of "a program was run and produced an answer that was judged".
- **Non-build-produced artifacts.** The subject model is "the output of a build". A program *executed* by an evaluation harness is not a build product of a supported builder.
- **Freshness / attempt epoch.** `runDetails.metadata.invocationId / startedOn / finishedOn` exist in the v1.0 schema, but slsa-verifier **does not check them**; there is no nonce/epoch check anywhere in the verifier.
- **Target instance / live state.** The subject is a name+digest. There is no notion of "the state of a running target at the time of the attempt".
- **An independent second-party verdict** (except the VSA path, §3.5).
- **A multi-rung claim ladder.** `verifiedLevels` is a set of *builder* levels, not a ladder over evidence rungs.

### 3.7 APPLICABILITY VERDICT FOR SLSA-VERIFIER

> **NOT APPLICABLE as the primary comparator for an ACTS harness attempt. APPLICABLE only in two narrow, clearly-labelled ways.**

Justification, in order of force:

1. **Builder scope mismatch.** [DOC] Only SLSA-generator (GHA) and GCB provenance is supported. [SRC] `getVerifier` dispatches on `builder.id` and returns `ErrorVerifierNotSupported` otherwise. An ACTS attempt has no `builder.id` and never will.
2. **Mandatory source-repository expectation.** [SRC] `verify-artifact` requires `--source-uri` (`github.com/org/repo` form). An ACTS attempt is a local program execution with a local file digest; it has no canonical source repository. This is a *structural* mismatch, not a configuration inconvenience.
3. **Provenance provenance.** The verifier's trust model is Sigstore: a Fulcio short-lived identity certificate + a Rekor transparency-log entry, verified against the Sigstore TUF trusted root. Producing that offline, with no OIDC issuer and no writes to Rekor, is impossible; and the project operates under an explicit "$0 marginal, offline, no network" constraint ([PROJECT] `B2_PROTOCOL.md` §Constraints).
4. **No inspection / no second-party-verdict path** in the GHA/GCB verifiers. `verify-vsa` is the only relevant sub-command, and it is a different predicate family.
5. **Maintenance.** The project is "no longer actively maintained" [DOC]. Building a new fairness claim on a deprecated verifier is a review liability, even if the specific sub-command still works.
6. **Predicate drift.** v2.7.1 parses only v0.2/v1.0 predicates while the current SLSA spec is v1.2.

**Where SLSA *is* legitimately usable in this project:**
- **[USABLE]** As a **citation-grade comparator** for *what a build-centric provenance system does and does not cover* — i.e., the argument in §3.6 and rows P5/P6/P7/P9 of §6.
- **[USABLE]** `slsa-verifier verify-vsa` as a **mechanism-level** instantiation of "a second party signs PASSED over a subject digest", with the semantic stretch stated in writing. This is a *comparison of mechanism*, not of verdict correctness.
- **[NOT USABLE]** `slsa-verifier verify-artifact` as a verdict oracle on the ACTS corpus. Any experiment that ran it would be comparing a rejection of "no source-uri / unsupported builder" against our system's verdicts — a comparison of error messages, not of security properties.

---

## 4. SIGSTORE / COSIGN

### 4.1 What `cosign verify-blob` does

[DOC] https://docs.sigstore.dev/cosign/verifying/verify/ (source: https://raw.githubusercontent.com/sigstore/docs/main/content/en/cosign/verifying/verify.md):
```shell
cosign verify-blob <file> --bundle artifact.sigstore.json \
  --certificate-identity=name@example.com --certificate-oidc-issuer=https://accounts.example.com
```
Keyless verification binds the *identity* in a Fulcio certificate (`--certificate-identity` / `--certificate-identity-regexp`) and the *issuer* (`--certificate-oidc-issuer` / `--certificate-oidc-issuer-regexp`); or `--key cosign.pub` for a local public key; or `--ca-roots` / `--ca-intermediates` / `--certificate-chain` for "bring your own PKI".

[DOC/SRC] `cosign verify-blob` flags (https://raw.githubusercontent.com/sigstore/cosign/main/doc/cosign_verify-blob.md): `--bundle`, `--certificate-identity[-regexp]`, `--certificate-oidc-issuer[-regexp]`, `--certificate-github-workflow-{name,ref,repository,sha,trigger}`, `--insecure-ignore-sct`, `--insecure-ignore-tlog`, `--key`, `--offline`, `--trusted-root`, `--new-bundle-format`.

[SRC] Blob↔signature binding: in `cmd/cosign/cli/verify/verify_blob.go`, the blob bytes (or an explicit `alg:digest`) become the artifact policy — `sgverify.WithArtifactDigest(alg, digest)` / `sgverify.WithArtifact(bytes.NewReader(blobBytes))` — and are then checked by `cosign.VerifyNewBundle` / `cosign.VerifyBlobSignature`. So the digest of the blob is inside the signed material. **This is a native, product-enforced P1.**

### 4.2 What `cosign verify-attestation` does

[DOC] It verifies an in-toto statement attached to an OCI image, and supports `--policy` with **CUE** or **Rego** to validate the *predicate* portion of the attestation (https://raw.githubusercontent.com/sigstore/docs/main/content/en/cosign/verifying/attestation.md). `--type <PREDICATE_TYPE>` selects the predicate type; `--check-claims` (default true) validates the cosign claims.

[SRC] `cosign verify-attestation` flags include `--type`, `--policy`, `--check-claims`, `--insecure-ignore-tlog`, `--insecure-ignore-sct`, `--certificate-identity`, `--certificate-oidc-issuer`, `--key`, `--offline`, `--trusted-root`. (https://raw.githubusercontent.com/sigstore/cosign/main/doc/cosign_verify-attestation.md)

### 4.3 Does cosign add anything beyond in-toto / SLSA for our contract?

**No, not for the substance of the contract.** Cosign contributes exactly three things:
1. **A signature + identity + transparency wrapper** over a blob or an in-toto statement. Both in-toto and slsa-verifier already provide signature + key binding; cosign adds *keyless* (Fulcio/OIDC) identity and *transparency* (Rekor) on top.
2. **A generic policy engine over the predicate** (CUE/Rego) — which is powerful, but **the policy is our code**. This is a textbook **POSSIBLE-WITH-CUSTOM-INSPECTION** row, not a product guarantee.
3. **Bundle formats and offline replay** (`--bundle`, `--trusted-root`, `--offline`, `--new-bundle-format`), which are packaging conveniences.

**What cosign does NOT do:** it has no notion of a supply-chain *step*, no artifact-rule language, no material→product chaining, no inspection/execution model, no claim ladder, no attempt/epoch binding, no target state. It is a *transport + signature* layer.

### 4.4 N/A VERDICT FOR COSIGN

> **NOT APPLICABLE as a comparator for this contract.** cosign is a *transport-and-signature* layer, not a *supply-chain-evidence* layer. Using it in the comparison would compare a signature checker against an evidence-binding protocol.

**Conditions under which cosign becomes relevant (all must hold):**
- The project decides to publish attempt attestations to a public transparency log so that **third parties** can verify them (cosign's unique value: Fulcio identity + Rekor inclusion + a signed bundle that replays offline). This is a *publication/interop* goal, not a *verdict correctness* goal.
- The comparison is re-scoped from "who decides the verdict" to "can a third party re-verify the verdict offline" — in which case cosign is the *transport* and in-toto or the project's own format is the *payload*.
- The project accepts network egress to a Rekor instance and a public OIDC issuer, or pre-seeds a `trusted_root.json` + bundle and accepts `--insecure-ignore-tlog` semantics (which weakens the transparency claim to "signed by a key we trust").

**Conditions under which cosign must NOT be used:**
- As the *system under test* for P1–P10. Every one of P1..P10 except P3 (and P2 in the keyless form) is either absent from cosign or implemented by user-supplied CUE/Rego.

---

## 5. RFC 9334 (RATS) — architecture, not a product

### 5.1 What it prescribes

[SPEC] https://www.rfc-editor.org/rfc/rfc9334.txt — "Remote ATtestation procedureS (RATS) Architecture", H. Birkholz et al., Informational, **January 2023**.

- **Roles** (§4.1): `Attester`, `Relying Party`, `Verifier`, `Relying Party Owner`, `Verifier Owner`, `Endorser`, `Reference Value Provider` — with "Produces:" / "Consumes:" lists.
- **Conceptual messages** (§8): `Evidence`, `Endorsements`, `Reference Values`, `Attestation Results`, `Appraisal Policies`.
- **Appraisal** (§8.5): "The Verifier (when appraising Evidence) or the Relying Party (when appraising Attestation Results) checks the values of matched Claims against constraints specified in its appraisal policy." Example constraints: equality against a Reference Value, range bounds, set membership, "A check against values in other Claims."
- **Attestation Results** (§8.4): "may carry a boolean value indicating compliance or non-compliance with a Verifier's appraisal policy **or may carry a richer set of Claims** about the Attester, against which the Relying Party applies its Appraisal Policy for Attestation Results." And: "By default, the Relying Party does not believe the Attester to be compliant."
- **Verifier ≠ producer** (§8.1): "Evidence needs to be securely associated with the Target Environment so that the Verifier cannot be tricked into accepting Claims originating from a different environment." And: "Claims need to be collected in a manner that is reliable such that a Target Environment cannot lie to the Attesting Environment about its trustworthiness properties."
- **Freshness** (§10) — three prescribed mechanisms:
  - §10.1 **Explicit timekeeping using synchronized clocks** (signed timestamp, RATS-TUDA).
  - §10.2 **Implicit timekeeping using nonces**: "an unpredictable nonce is sent by the appraising entity and the nonce is then signed and included along with the Claims in the Evidence or Attestation Result. After checking that the sent and received nonces are the same, the appraising entity knows that the Claims were signed after the nonce was generated."
  - §10.3 **Implicit timekeeping using epoch IDs** (periodically distributed, compared against a local "epoch window").
  - §12.3: freshness is checked as `time(RG_v) - time(EG_a) < Threshold`, where the Threshold "is decided by the Appraisal Policy for Evidence".
- **Trust anchoring** (§7, §12.4) and **key protection** (§12.1) are named as required concerns.
- **Composition** (§3.1–§3.3): Attester = Attesting Environment + Target Environment; layered and composite topologies; "Passport Model" and "Background-Check Model" (§5).

### 5.2 What it does NOT prescribe — verified by exhaustive string search

[SRC] Full-text search of https://www.rfc-editor.org/rfc/rfc9334.txt for the following strings returned **zero** hits:

`Rekor` (0) · `DSSE` (0) · `transparency` (0) · `in-toto` (0) · `SLSA` (0) · `Sigstore` (0) · `causal` (0) · `multi-signature` (0) · `joint` (0) · `multiple signatures` (0).

Therefore RFC 9334 does **not** prescribe:
- a transparency log, a log protocol, or log-inclusion proofs;
- a specific envelope/signature format (no DSSE, no PAE);
- any in-toto / SLSA / Sigstore binding;
- **semantic validity of a step** (nothing requires an attester to demonstrate that a *step* was correct, only that claims are present and appraised);
- **causality between steps** (there is no step chain, no artifact-rule language, no material→product join);
- **target state** beyond the abstract claim that Evidence must be "securely associated with the Target Environment" (§8.1) and the layered-environment model (§3.1–§3.2) — it does not define *how* to bind a specific target instance identity or state to a claim.

The "thresholds" in RFC 9334 are **freshness time thresholds** (§10, §12.3), *not* multi-party signature thresholds. RFC 9334 contains no construct analogous to in-toto's `steps[].threshold` (multiple authorized functionaries required per step).

### 5.3 The task prompt's premise about RFC 9334, corrected

The task brief describes RFC 9334 as prescribing "rekor transparency log, DSSE envelopes, keyless identity, roles/thresholds". **That is not accurate.** RFC 9334 prescribes *roles*, *conceptual messages*, *appraisal policies*, and *freshness mechanisms*; it does **not** mention Rekor, DSSE, or keyless identity at all (zero hits, §5.2), and its "thresholds" are time thresholds, not signature-count thresholds. The Sigstore/Rekor/DSSE stack is an *implementation* of the RATS model (Fulcio ≈ keyless identity + endorsements, Rekor ≈ an append-only log, DSSE ≈ a claim-protection envelope), but that mapping is **our construction**, not an RFC 9334 requirement. Any write-up that says "RFC 9334 requires Rekor" would be a citation error and must be corrected before submission.

### 5.4 VERDICT FOR RATS

> **COMPARABLE ONLY AS AN ARCHITECTURAL TARGET.** RFC 9334 is a normative *architecture* with no reference implementation, no CLI, and no encoding. It is therefore:
> - **The right target** for contract rows **P6 (freshness/epoch)**, **P7 (target binding)**, and **P9 (claim aggregation)**, because it is the only one of the four that prescribes a mechanism for each — even though prescribing ≠ implementing.
> - **Not runnable**, so it can never be a "system" in a verdict-comparison experiment. It can only be a **row-coverage reference** in the P1..P10 matrix.
> - Its "N" marks in §6 mean **"prescribed by the architecture; a conforming implementation must provide it"** — never "shipped and tested".

---

## 6. THE FAIR COMPARISON CONTRACT (P1..P10)

### 6.1 Definitions

The contract is stated in terms of what a verifier must be able to *decide* about a single ACTS attempt. It is deliberately independent of any one system's vocabulary, so that each system can be mapped onto it without being reinterpreted.

| ID | Property | Precise question | What counts as satisfying it |
|---|---|---|---|
| **P1** | Artifact digest equality | Are the bytes the verifier accepts bit-identical to the bytes that were produced/claimed? | A cryptographic digest equality check performed by the system over a *named* artifact, where the digest is of the artifact bytes (not of a record describing them). |
| **P2** | Signer identity + role authorization | *Who* may assert *what* about *which* step? | The system has a configured mapping from a key/identity to an authorized role, and rejects an assertion made by a party not authorized for that role. |
| **P3** | Signature validity / key binding | Is the assertion cryptographically bound to a specific key? | The system verifies a signature over the assertion and binds it to a key whose identity it can name. |
| **P4** | Step-to-step causal join | Does the output of step N provably feed step N+1? | The system natively checks that step N+1 consumed the exact bytes step N produced, by digest (not by assertion). |
| **P5** | Trusted execution observation | Does a party *other than the artifact producer* attest to the execution? | A second party, holding its own key, signs an observation about the artifact/attempt. |
| **P6** | Freshness / replay / epoch binding | Can a stale-but-valid assertion from a prior attempt be rejected? | The system has a native mechanism (expiry, nonce, epoch id, invocation binding) that makes a replayed assertion detectable as belonging to a different attempt/epoch. |
| **P7** | Target instance + state binding | Is the claim bound to *this* target instance in *this* state? | The system binds the claim to an identifier and a state description of the specific target the attempt acted on. |
| **P8** | External reference-oracle verdict binding | Is an *independent* verdict (from a party other than the producer) bound to the exact artifact and its verdict content? | The verdict is carried in signed material, bound to the artifact by digest, and its *content* is checked by the system (not merely its presence). |
| **P9** | Final-claim aggregation correctness | Is the final claim a *calibrated* aggregation of partial truths, rather than a single boolean? | The system can express "level 4 established, level 5 not established" as distinct outcomes, and the promotion decision is a function of the system, not of user code. |
| **P10** | Malformed/missing vs contradictory distinction | Can a downstream consumer tell "the evidence is absent/unparseable" from "the evidence contradicts the claim"? | The system's *machine-readable output* distinguishes the two classes. |

### 6.2 The matrix

Legend — **N** = native mechanism (the product implements the check; a failure is a product-detected rejection) · **P** = partial (a native mechanism exists but covers strictly less than the row) · **C** = possible only with **custom inspection** (the row can be reached only by supplying our own logic through the product's extension point; **this is our guarantee, not the product's**) · **A** = not applicable (no mechanism and no meaningful extension point).

> ⚠ **Rows marked C or P-C are NOT product guarantees.** Any claim in the manuscript must be worded as "achievable only by user-supplied inspection logic", never as "SLSA/in-toto provides X".
>
> ⚠ **Every cell marked `C`, `P` (where the note says the content is ours), or `P` in RATS's column, is additionally tagged inline with the literal token `[CUSTOM-INSPECTION]`.** That token is the machine-checkable marker for "this guarantee is ours, not the vendor's". A cell with no `[CUSTOM-INSPECTION]` token and marked **N** is a genuine product guarantee.

| ID | in-toto 3.1.0 | slsa-verifier 2.7.1 | cosign 3.1.3 | RATS (RFC 9334) | Decisive primary source |
|---|---|---|---|---|---|
| **P1** artifact digest equality | **N** — `materials`/`products` hash objects; `MATCH`/`MODIFY` compare digests | **N** — `subject[].digest` vs computed SHA-256 of the file | **N** — blob digest inside the signed material | **C** [CUSTOM-INSPECTION] — Claims comparison is policy code | in-toto-spec §4.3.3/§4.4; slsa `verify_artifact.go`; cosign `verify_blob.go`; RFC 9334 §8.5 |
| **P2** signer identity + role authorization | **N** — layout `steps[].pubkeys[]` + `threshold`; unauthorized signers skipped → threshold failure | **N** — `builder.id` vs roots of trust; `--builder-id` | **N** — `--certificate-identity` / `--certificate-oidc-issuer` / `--key` | **N (arch.)** [CUSTOM-INSPECTION] — role model + Appraisal Policy owned by Verifier Owner; RFC 9334 ships no verifier, so realizing this is our implementation | in-toto-spec §4.3.1; slsa.dev/spec/v1.0/verifying-artifacts; cosign `verify-blob` docs; RFC 9334 §4.1, §7.5 |
| **P3** signature validity / key binding | **N** — metablock/DSSE; keyid = SHA-256 of canonical public key | **N** — DSSE via Sigstore | **N** — DSSE / simple-signing | **N (arch.)** [CUSTOM-INSPECTION] — §12.1, §12.2; RFC 9334 ships no verifier | in-toto-spec §4.2.1; RFC 9334 §12.1–12.2 |
| **P4** step-to-step causal join | **N** — `MATCH ... FROM <step>` (+ `MODIFY` requires digest change) | **P** — `resolvedDependencies`/`externalParameters` express dependency, but "SLSA v1.0 does not have any requirements on the completeness or verification of `resolvedDependencies`"; verifier checks only source-uri/tag/inputs, so *enforcing* a dependency join would be **[CUSTOM-INSPECTION]** | **A** — no step notion | **A** — no step/chain notion | in-toto-spec §4.3.3, §4.3.3.1; slsa.dev/spec/v1.0/verifying-artifacts (Step 3) |
| **P5** trusted execution observation | **P** [CUSTOM-INSPECTION for the rule content] — *client-side inspection* is a native second-party observation (client runs the command; artifact rules bind its result). **No** native observation that a *step's* command actually ran (`expected_command` mismatch = warning only; `byproducts`/`environment` unverified) | **A** | **A** | **N (arch.)** [CUSTOM-INSPECTION] — Attester ≠ Verifier; Evidence "securely associated with the Target Environment" | in-toto-spec §4.3.1, §4.4, §4.4.1; verifylib.py step 7; RFC 9334 §3.1, §8.1 |
| **P6** freshness / replay / epoch | **P (layout-level only)** — `expires` → `LayoutExpiredError`. **No** per-attempt freshness: link has no timestamp/nonce/attempt id; "in-toto inherently does not protect against attackers replaying older, as-yet unexpired layouts" | **A** — `invocationId`/`startedOn`/`finishedOn` are not checked; no nonce/epoch check | **A** — Rekor gives inclusion time, not attempt epoch | **N (arch.)** [CUSTOM-INSPECTION] — three prescribed mechanisms: signed timestamps (§10.1), verifier nonces (§10.2), epoch IDs (§10.3) | in-toto-spec §1.5.2, §4.3, §4.4; slsa errors.go / verify_artifact.go; RFC 9334 §10 |
| **P7** target instance + state binding | **A** — "Target files are opaque to the framework"; no live target/state concept | **A** — subject is name+digest | **A** | **N (arch.)** [CUSTOM-INSPECTION] — §3.1 Attesting+Target Environment; §8.1 secure association with the Target Environment | in-toto-spec §2 (System overview); RFC 9334 §3.1, §8.1 |
| **P8** external reference-oracle verdict binding | **P** [CUSTOM-INSPECTION for the verdict content] — inspection command run by the client; non-zero exit → `BadReturnValueError`; binding to the artifact is by artifact rules. **But** the verdict *content* is not carried or checked — only pass/fail | **P** [CUSTOM-INSPECTION for the semantics] — `verify-vsa`: a *Verifier-signed* `verificationResult: PASSED` bound to `subject[].digest` + `resourceUri` + `verifier.id`; content is "verification levels", not a cryptographic-answer verdict | **C** [CUSTOM-INSPECTION] — `verify-attestation --policy` (CUE/Rego) can check an arbitrary predicate, but the policy is our code | **N (arch.)** [CUSTOM-INSPECTION] — Reference Values from a Reference Value Provider compared to Evidence; Attestation Results carry Claims | in-toto-spec §4.3.2; verifylib.py `BadReturnValueError`; slsa `vsa/verifier.go`; RFC 9334 §8.3–8.5 |
| **P9** final-claim aggregation correctness | **A** — verification is a boolean conjunction of steps+inspections plus a summary link; no rung ladder | **C** [CUSTOM-INSPECTION] — `verifiedLevels[]` is a container, but the ladder semantics are ours | **C** [CUSTOM-INSPECTION] — predicate + policy is ours | **N (arch.)** [CUSTOM-INSPECTION] — Attestation Results may carry "a richer set of Claims" appraised by the Relying Party | verifylib.py `in_toto_verify` return; slsa `vsa.go`; RFC 9334 §8.4 |
| **P10** malformed/missing vs contradictory | **P** — Python API has a typed exception hierarchy (`FormatError`/`InvalidMetadata` = malformed; `SignatureVerificationError`, `ThresholdVerificationError`, `RuleVerificationError`, `LayoutExpiredError`, `BadReturnValueError` = failed); CLI collapses to exit 1 but prints the exception class name to stderr. **Partial collapse:** an unauthorized or badly-signed *link* is silently *skipped* and reported as `ThresholdVerificationError` | **P** — distinct sentinels (`ErrorInvalidDssePayload` = malformed; `ErrorMismatchHash`, `ErrorMismatchSource`, `ErrorMismatchBuilderID`, `ErrorNoValidSignature`, `ErrorInvalidVerificationResult` = contradictory) but the CLI prints only a message string and exits 1 | **P** — exit 1 + message string | **A** — no encoding of validity states is prescribed | in-toto `exceptions.py`, `in_toto_verify.py`; slsa `errors/errors.go`, `cli/slsa-verifier/verify.go`; RFC 9334 (no such construct) |

### 6.3 Reading the matrix honestly

- **How to read a cell.** A cell marked **N** with **no** `[CUSTOM-INSPECTION]` token is a *genuine product guarantee* shipped by a runnable product (in-toto, slsa-verifier, cosign). A cell carrying the `[CUSTOM-INSPECTION]` token is **our** logic, **our** encoding, or an architectural prescription with no implementation — and must never be reported as a vendor guarantee. The RATS column carries the token on every **N (arch.)** cell because RFC 9334 ships no verifier at all.
- **in-toto is the only product with a native mechanism in P1, P2, P3, and P4.** P4 in particular is *the* row that separates in-toto from cosign and from SLSA's practical surface: SLSA's dependency graph is schema-level and explicitly unverified, cosign has no step concept at all.
- **P6, P7, P9 are the rows where in-toto, slsa-verifier and cosign are all `A`/`P` and where the project's own design is strongest.** That is the defensible novelty space — *provided* the comparison is stated as "rows the products do not cover" and not as "we beat in-toto".
- **P5 and P8 have a partial native mechanism in in-toto (inspections) and in slsa-verifier (`verify-vsa`).** These are the two rows where a fair experiment can produce a *real* product comparison rather than a design-class model comparison — but the *content* of the check in both cases is ours, so the token applies.
- **P10 is `P` everywhere and never `N` at the exit-code level.** Any harness that consumes any of these products must parse stderr (or import the library) to recover the malformed/contradictory distinction. Our own validator's separate `NOT_ESTABLISHED` / `REJECTED` / `NOT_OBSERVED` value enums are a *design difference*, not a product-beating result.

### 6.3.1 Index of genuinely native, product-shipped mechanisms

| Row | in-toto | slsa-verifier | cosign | RATS |
|---|---|---|---|---|
| P1 | **native** | **native** | **native** | none (custom) |
| P2 | **native** | **native** | **native** | none (custom) |
| P3 | **native** | **native** | **native** | none (custom) |
| P4 | **native** | none (schema only) | none | none |
| P5 | partial (custom content) | none | none | none (custom) |
| P6 | partial (layout expiry only) | none | none | none (custom) |
| P7 | none | none | none | none (custom) |
| P8 | partial (custom content) | partial (custom semantics) | none (custom) | none (custom) |
| P9 | none | none (custom) | none (custom) | none (custom) |
| P10 | partial (real, but CLI collapses) | partial (real, but CLI collapses) | partial (real, but CLI collapses) | none |

**"native" in this table means: the row is checked by shipped product code, over product-owned data, and a violation is a product-detected rejection.** Nothing in P5–P9 qualifies for any of the three runnable products.

### 6.4 Where the project's existing offline models sit in this matrix

**[PROJECT]** `b2_prov_baselines.py` implements the `digest-only` model (D1..D17) and the `digest-session` model (D1..D17 + S1..S6) plus four single-check ablations. Mapping the B2 check families onto the contract rows:

| B2 check family | Contract row | Note |
|---|---|---|
| D2 (declared evidence-file digests), D4/D5/D6 (artifact digest joins) | **P1** | These are a *model* of in-toto's digest rules, not in-toto's rules. |
| D3 (detached Ed25519 signature under a trusted anchor) | **P3** | Model of metablock signature verification. |
| S1–S6 (`record.session_id == cred` joins) | **P4/P6** | **Not an in-toto mechanism at all.** in-toto has no session/attempt field. This is the project's own design; RATS §10.2/§10.3 is the nearest prior-art *architecture* for it. |
| D8–D13 (effect observed / reference accepted / boundary enforced / verifier version) | **P8/P9** | Model of the ladder; not an in-toto mechanism (in-toto has no ladder). |

**Consequence:** the B2 result "digest-only falsely promotes 8/58; digest-session 0/58" is a measurement about **the project's own two designs**. It is *not* a measurement about in-toto, and §8 below specifies the experiment that would turn it into one.

---

## 7. Feasibility, installation, offline operation, and cost

### 7.1 Exact upstream versions

| System | Version | Evidence | Release date |
|---|---|---|---|
| in-toto (Python) | **3.1.0** | [SRC] PyPI JSON API https://pypi.org/pypi/in-toto/json (`info.version`); [SRC] https://github.com/in-toto/in-toto/releases/latest → `v3.1.0` | wheel `in_toto-3.1.0-py3-none-any.whl` uploaded 2026-04-25 |
| slsa-verifier | **2.7.1** | [DOC] README install section; [SRC] https://github.com/slsa-framework/slsa-verifier/releases/latest → `v2.7.1` | 2025-06-27 |
| cosign | **3.1.3** | [SRC] https://github.com/sigstore/cosign/releases/latest → `v3.1.3` | 2026-08-06 |
| RFC 9334 (RATS) | Informational, January 2023 | [SPEC] https://www.rfc-editor.org/rfc/rfc9334.txt | — |

### 7.2 Install methods and runtime dependencies

**in-toto 3.1.0**
- [DOC] `pip install in-toto` (https://in-toto.readthedocs.io/en/latest/installing.html). Also `apt install in-toto`, `pacman -S in-toto`.
- [SRC] `pyproject.toml` (https://raw.githubusercontent.com/in-toto/in-toto/develop/pyproject.toml): `requires-python = ">=3.9"`; `dependencies = ["attrs", "iso8601", "pathspec", "python-dateutil", "securesystemslib[crypto]~=1.0"]`; build backend `hatchling`.
- [DOC] System deps: OpenSSL (for RSA signature generation/verification and GPG export/verify); GPG only if generating PGP signatures (verification works without GPG).
- [SRC] Console scripts: `in-toto-mock`, `in-toto-record`, `in-toto-run`, `in-toto-sign`, `in-toto-verify`, `in-toto-match-products`. **There is no `in-toto-layout` CLI** — a layout must be constructed with the Python API (`in_toto.models.layout.Layout`, https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/models/layout.py) or written as JSON. That is a real, non-trivial authoring cost for the experiment in §8, because the *layout is the policy* and it must be frozen before the pass.

**slsa-verifier 2.7.1**
- [DOC] `go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@v2.7.1`; or `git checkout v2.7.1 && go run ./cli/slsa-verifier`; or download the release binary and check it with `sha256sum -c --strict SHA256SUM.md`; or Homebrew.
- [SRC] The module path is `/v2`, so the tool must be installed at `v2.7.1`.
- [UNVERIFIED] The minimum Go version required by the v2.7.1 `go.mod` was not read in this task (the file was not fetched). The local toolchain is **go1.22.2** (`go version` → `go version go1.22.2 linux/amd64`); whether that satisfies the module's `go` directive is **[UNVERIFIED]** and must be checked at install time.

**cosign 3.1.3**
- [DOC] `go install github.com/sigstore/cosign/v3/cmd/cosign@latest` (Go 1.20+), or the release binary/rpm/deb, or Homebrew, pacman, apk, Nix. The release binary is keyless-signed and should be verified before use (https://raw.githubusercontent.com/sigstore/docs/main/content/en/cosign/system_config/installation.md).
- Note the `/v3` module path.

### 7.3 Offline capability

| System / command | Fully offline? | Evidence |
|---|---|---|
| **in-toto** `in-toto-verify` | **YES** — by design | [DOC] "The verification workflow is performed in isolation and does not rely on information about keys that are available through external sources." https://in-toto.readthedocs.io/en/latest/command-line-tools/in-toto-verify.html |
| **slsa-verifier** `verify-artifact` / `verify-image` / `verify-npm-package` | **NO (first run)** — requires the Sigstore TUF trusted root (network fetch of TUF metadata, cached at `~/.sigstore/root`) and a Rekor inclusion check; v2.7.1 exposes **no `--trusted-root`** flag | [SRC] `verifiers/utils/sigstore_tuf.go`; [SRC] `options/options.go` (no trusted-root field); [SRC] sigstore-go `pkg/tuf/options.go` `DefaultOptions()` |
| **slsa-verifier** `verify-vsa` | **YES** — user-supplied public key + plain DSSE envelope; no Sigstore, no Rekor | [SRC] `verifiers/internal/vsa/verifier.go`; [DOC] README "Caveats → Sigstore" |
| **cosign** `verify-blob` / `verify-attestation` | **YES with `--bundle` + `--trusted-root` + `--offline`** (new bundle format); or `--key` + `--insecure-ignore-tlog` | [DOC] https://raw.githubusercontent.com/sigstore/docs/main/content/en/cosign/verifying/verify.md; [SRC] `cosign_verify-blob.md`, `verify_blob.go` (`--trusted-root only supported with --new-bundle-format`) |
| **RFC 9334** | **N/A** — no implementation | — |

### 7.4 Estimated local overhead — **[ESTIMATE], NOT MEASURED**

No installation was performed, so **no timing was measured**. The following are reasoned magnitudes for budgeting only, and must be replaced by measurements before any overhead claim enters the manuscript.

| System | Per-invocation overhead, CLI | Per-case overhead, in-process library | Dominant cost |
|---|---|---|---|
| `in-toto-verify` | ~0.6–2.0 s (Python interpreter + `securesystemslib` + `cryptography` import) | ~1–10 ms (one Ed25519 verify ≈ tens of µs; one RSA-2048 PSS verify ≈ ~1 ms; plus SHA-256 and artifact-rule matching) | interpreter start (CLI) / signature verification (library) |
| `slsa-verifier verify-artifact` | ~50–300 ms (Go binary start, SHA-256 of artifact, DSSE verify) + Sigstore TUF/Rekor network cost on first use | n/a (Go, no embeddable API for our use) | artifact hashing + Sigstore material |
| `slsa-verifier verify-vsa` | ~50–200 ms | n/a | DSSE verify |
| `cosign verify-blob` | ~50–300 ms | n/a | DSSE/simple-signing verify |
| Project's own validator **[PROJECT]** | — | **~50–80 ms** (measured mean overhead reported in `B2_BASELINE_COMPARISON_REPORT.md` §4.2: `digest-only` 69.01 ms, `digest-session` 67.41 ms, `V3-full` 68.50 ms on the held-out set) | JSON parsing + Ed25519 verifies |

The obvious engineering consequence: **do not measure the CLI.** Call `in_toto.verifylib.in_toto_verify` in-process, exactly as the project's own baselines call their verifiers in-process, so that the overhead comparison is apples-to-apples. The in-toto CLI exists mainly to fix the exit code and the artifact-loading conventions, both of which we can reproduce in a thin wrapper.

### 7.5 Exactly what user approval is required

Nothing has been installed. The following would each need explicit approval, and each is a **network-egress + filesystem-write** action:

1. **`pip install in-toto==3.1.0`** into an isolated virtualenv (e.g. `python3 -m venv .venv-intoto && .venv-intoto/bin/pip install in-toto==3.1.0`). This pulls `securesystemslib[crypto]~=1.0` → `cryptography` (binary wheels), `attrs`, `iso8601`, `pathspec`, `python-dateutil`. *Recommended*, because it is the only installation that makes the primary comparison possible, it is pure-Python-installable, and it is fully offline after install.
2. **A Go toolchain check / `go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@v2.7.1`** (Go 1.22.2 is already present locally) *or* downloading the release binary. *Needed only* for the §8.2 optional `verify-vsa` mechanism demonstration. Note the Go module cache writes to `~/go/pkg/mod` and `~/go/bin`.
3. **A cosign release binary** (v3.1.3) into a scratch directory, plus a Sigstore `trusted_root.json` if the offline path is to be exercised. *Needed only* if the team decides to pursue the §4.4 "publication/interop" direction, which this analysis rates **N/A** for the contract.
4. **Writing the new experiment directory** under `sp2027/analysis/acts_next_phase_20261019/stage2_provenance/` (a **new**, previously-empty directory — no existing file is touched).

**Budgetary note:** items 1–3 are one-time, low-cost, offline-after-install operations. The project constraint "$0 marginal, no network" ([PROJECT] `B2_PROTOCOL.md` §Constraints) refers to *experiment execution*, not to one-time tool provisioning; a one-time install is compatible with it, but it must be recorded as a deviation from the "no network" clause of the earlier B2 protocol and must not be conflated with the B2 run itself.

---

## 8. A concrete, scientifically FAIR comparison plan

### 8.1 Research question and the honesty constraint

> **RQ:** *On the frozen IAR-B corpus, and under one common contract (P1..P10), does the real in-toto verifier (as a product) reach a different verdict than the project's own evidence-binding design — and if so, on which contract row, with the row's coverage attributed to a product mechanism rather than to our own code?*

The **honesty constraint** is the crux: a difference in verdict is only scientifically meaningful if it is attributed to a row that the product covers **natively**. Otherwise the experiment compares our code against our code wearing a product's clothes. Therefore:

> **Rule C1 (no laundering):** a verdict difference counts as a *product* result only if the responsible contract row is marked **N** in §6.2 for that product. Differences on rows marked **P** or **C** are reported as *"achievable only with user-supplied inspection logic"* and are **not** counted as product advantages.

> **Rule C2 (no substitution of models for products):** the B2 `digest-only` / `digest-session` models may appear in the results table **only** in a row explicitly labelled "design-class model (not the product)". They may never be cited as "in-toto" or "SLSA". This is already mandated by [PROJECT] `B2_PROTOCOL.md` §3 and `b2_prov_baselines.py` lines 10–13, and this document extends the same rule to the new experiment.

### 8.2 Arms

| Arm | System | Status | Rows natively covered (from §6.2) |
|---|---|---|---|
| **A0** | `V3-full` (project, existing) | reference | P1, P2, P3, P4, P5, P6, P7, P8, P9, P10 |
| **A1** | `digest-only` (project model of in-toto/SLSA design class) | model, **labelled** | P1, P2, P3, P4, P10 |
| **A2** | `digest-session` (project model) | model, **labelled** | + P6 |
| **A3** | **in-toto 3.1.0 `in_toto.verifylib.in_toto_verify`** | **REAL PRODUCT** | P1, P2, P3, P4, (P5 via inspection), (P8 via inspection), (P10 via exception class) |
| **A4** | **slsa-verifier 2.7.1 `verify-vsa`** | **REAL PRODUCT**, mechanism-only | P3, (P8 partial), (P10 partial) |
| **A5** | `cosign 3.1.3 verify-blob` | **REAL PRODUCT** | P1, P2, P3 |
| **A6** | RFC 9334 | **architecture only** | row-coverage reference; never a verdict arm |

**A6 is explicitly not a verdict arm.** RATS has no implementation; putting it in the results table as a "system" would be exactly the kind of category error the task warns about.

### 8.3 Shared input and shared contract

- **Corpus:** the frozen IAR-B corpus — dev 54 (`iar_b/cases/dev/`) and held-out 58 (`iar_b_heldout/cases/…`), with `labels/*_labels.json` and `trust/*_run_keys.json`. **[PROJECT]** `B2_PROTOCOL.md` §5. No case file is modified, copied-with-edits, or regenerated.
- **Truth source:** the existing `eb_adjudicator.py` (generator-side truth), unchanged. **[PROJECT]**
- **Claim ladder:** the existing 6 rungs and value enums, unchanged. **[PROJECT]**
- **Outcome contract:** every arm must emit the same line: `{system, decision ∈ {ACCEPT, REJECT}, supported ∈ 0..6 ∪ null, requested ∈ 1..6, reason}`. **[PROJECT]** `b2_prov_baselines.py` docstring already specifies this shape; the in-toto arm must map its `Link`/exception onto it.
- **Normalization of in-toto's boolean verdict:** in-toto returns pass/fail, not a rung. The mapping must be **pre-registered**: in-toto's success ⇒ `supported = 6`; in-toto's failure ⇒ `supported = 0` *unless* the failure is attributable to a specific rung, in which case the rung is derived from **which rule failed** (a deterministic function of the exception type and the rule traceback), pre-registered before the pass. This mapping is **our** code and must be labelled as such under Rule C1 — in particular, in-toto's rung attribution can never be cited as a product-native P9.

### 8.4 The translation layer — and the trap it contains

To run in-toto on the corpus, each case's records must be expressed as in-toto objects. This requires a **frozen translation layer** `intoto_translate.py` (pre-registered, hash-frozen, audited) that:

1. Emits one `link` per evidence record, signed by the *authorized functionary key* for that step, with `materials` = the declared evidence digests and `products` = the case's candidate digest, encoded as `{path: {"sha256": hex}}` hash objects.
2. Emits a `layout` with one `step` per case (or one shared layout with per-case sublayouts) whose `pubkeys` = the authorized functionary keyid, `threshold = 1`, and `expected_materials`/`expected_products` carrying the `MATCH`/`MODIFY`/`DISALLOW` rules that encode the case's intended joins.
3. Emits an `inspection` whose `run` is the project's own reference-verdict command (replaying the case's adjudicated verdict), with artifact rules binding the verdict to the candidate digest.

**The trap, stated precisely:** *the in-toto link format has no field for an attempt/session identifier.* The format is exactly `{_type, name, command, materials, products, byproducts, environment}` [SPEC §4.4], and `byproducts` and `environment` are **not verified** [SPEC §4.4, §4.4.1]. Therefore:

- **(T1) Naive translation:** the attempt identity is dropped. Then the H6b/H10 cases (foreign authentic record, identical candidate digest) are **accepted** by in-toto, because the foreign record is signed by an authorized key and the digests match. This predicts in-toto reproduces the `digest-only` model's 8 held-out false promotions.
- **(T2) Encoding the attempt into the artifact path:** the attempt id *can* be smuggled into the artifact **path** (e.g. `attempts/<session_id>/candidate.json`), because artifact rules match on path *and* digest. This is a legitimate construction and would make in-toto reject the H6b/H10 cases. **But it is our encoding, not an in-toto feature.** It must be reported as a **custom construction (C)**, never as "in-toto binds attempts".
- **(T3) Encoding the attempt into `environment`:** in-toto will **accept** the substituted record, because `environment` is unverified. This is a *product-level* result and must be reported as such: it demonstrates that in-toto's own "record the execution context" facility is not a security mechanism.

**T1 and T3 together are the most scientifically valuable outcomes of the experiment**, because they are *product* results on a row (P6/P4) where in-toto is `A`/`P`, and they are directly comparable to the project's own `digest-only` vs `digest-session` contrast.

### 8.5 Metrics

Identical to the existing B2 metrics so results are poolable ([PROJECT] `B2_PROTOCOL.md` §6):
- **false_promotion** — ACCEPT at asserted level 6 for a case whose adjudicated `truth_strong` is False; broken out per family (H1..H10).
- **overclaim** — asserted `supported` > adjudicated `supported`, on a non-malformed case.
- **false_reject** — adjudicated `supported` ≥ 1, `requested` ≤ adjudicated `supported`, system rejected.
- **agreement** — asserted `supported` == adjudicated `supported`.
- **overhead_ms** — first of two identical runs; plus double-run determinism.
- **NEW: row coverage** — for each of P1..P10, whether the arm's *product* (not our code) exercised the row on this corpus, and the count of cases where the row changed the verdict. This is the primary scientific deliverable, and it is computed from the §6.2 matrix, not from the outcomes.

### 8.6 Pre-registered predictions (written before the pass)

- **P-A:** in-toto (T1 naive translation) produces level-6 false promotions on exactly the H6b/H10 held-out cases (predicted count: 8, matching `digest-only`). *If the count differs, that is a deviation to be reported, not retuned.*
- **P-B:** in-toto (T2 attempt-in-path) produces 0 level-6 false promotions, i.e. in-toto *can* express the join — but only via a custom construction, and the result must be labelled **C** under Rule C1.
- **P-C:** in-toto rejects every case whose adjudicated reference verdict is negative, because the inspection command exits non-zero (`BadReturnValueError`). *Exception:* if the inspection's material/product rules are also violated, the failure may surface as `RuleVerificationError` instead — the pre-registered mapping must handle both.
- **P-D:** no arm produces a false reject on the honest-partial family H7(k) at level k.
- **P-E:** `verify-vsa` (A4) will accept a VSA we construct with `verificationResult: PASSED` and the case's candidate digest as `subject[].digest`, and will reject it if the digest is altered. *This demonstrates the mechanism, not the semantics, and must be reported as such.*
- **P-F:** overhead of the in-process in-toto arm is within an order of magnitude of the project's own baselines (both dominated by signature verification, not by policy logic).

### 8.7 What would count as an ADVANTAGE

1. **A product advantage** (the strong claim): an arm whose verdict on a case differs from `V3-full`'s, on a contract row that the arm covers with a **N** (native) mechanism, with the difference attributable to that mechanism. Example shape: *in-toto natively rejects case X because the `MODIFY` rule requires the digest to change and it did not* — a real, product-level, row-P1/P4 result.
2. **A design-space advantage** (the honest, likely claim): the project's design covers rows P6/P7/P9 natively while **every** product arm is `A`/`P` there. This must be framed as **"rows the compared products do not cover"**, with the exact per-product citations attached, and never as "we defeated in-toto".
3. **A cost/ergonomics result**: e.g. in-toto's requirement that a *layout* (frozen policy) be authored and signed before verification, and that the *link* carry no attempt field, imposes measurable authoring cost relative to the project's single-schema bundle. This is a defensible, measurable systems claim.

### 8.8 What would be NOT_COMPARABLE (must be declared in the paper)

- Any comparison of in-toto vs SLSA-verifier vs cosign **verdicts on the ACTS corpus** — SLSA and cosign cannot be instantiated as verdict arms (§3.7, §4.4). A table showing "SLSA: REJECT (no source-uri)" against our verdicts is a comparison of error messages.
- Any comparison where one side's check is user-supplied inspection logic and the other side's is product-native (Rule C1). This includes in-toto's **inspection**-based checks (P5/P8) and any **CUE/Rego** policy in cosign.
- Any comparison of the **B2 models** against the real products and calling the difference a product result (§0.3, Rule C2).
- Any comparison involving **keyless / Fulcio / Rekor / TUF bootstrapping** as a *correctness* dimension. Those are **deployment** properties, not evidence-binding properties. They belong in a separate "deployment cost" discussion, if at all.
- Any claim that a *model* was defeated by an *attack* rather than *accepted a case it should have rejected* (the B2 measurement is a false-promotion rate on a fixed corpus, not an exploit).
- Any comparison where the *truth source* differs between arms. The adjudicator must be identical for all arms.
- Any claim about RATS' runtime behaviour. It has none.

### 8.9 Preconditions and freeze discipline

- The translation layer (`intoto_translate.py`), the layout templates, the in-toto↔rung mapping, and the pre-registered predictions are **frozen with SHA-256 in a freeze packet** before the preserved pass, mirroring [PROJECT] `B2_PROTOCOL.md` §6 gate B2-G5 and the existing `b2/freeze/B2_FREEZE.json`.
- The preserved pass is single-shot, with double-run determinism, and results are hashed. No retuning after the pass. Deviations are recorded with cause.
- All gates from `B2_PROTOCOL.md` §6 (fixture integrity, determinism, honest preservation, discrimination, integrity) are re-used unchanged so the two experiments are directly comparable.
- **Protocol amendment required:** the new experiment introduces a one-time tool installation (network egress) that the B2 protocol forbade. That amendment must be written into the new protocol *before* the pass, with the pre-registration of the new arm names and predictions, and must not modify the frozen B2 artefacts.

---

## 9. Verdicts at a glance

| Question | Answer |
|---|---|
| Is **in-toto** genuinely comparable to the ACTS evidence-binding contract? | **Yes — the only one that is.** It natively covers P1, P2, P3, P4; partially covers P5 and P8 via its inspection mechanism; partially covers P10 via its typed exceptions; and is **fully offline** by design. Its gaps (P6, P7, P9) are exactly the project's strongest rows. |
| Is **slsa-verifier** comparable? | **No, not as a verdict comparator.** It only verifies provenance from SLSA-generator (GHA) and GCB, `verify-artifact` *requires* `--source-uri`, its trust material is Sigstore/TUF/Rekor (network), it has no inspection or second-party-verdict model in the GHA/GCB path, its project is unmaintained, and v2.7.1 parses only v0.2/v1.0 predicates while the current SLSA spec is v1.2. **Exception:** `slsa-verifier verify-vsa` is offline and *is* a native "second party signs PASSED over a subject digest" mechanism — usable as a **mechanism-level** comparator on P8 with an explicit semantic-stretch disclosure. |
| Is **cosign** comparable? | **No.** It is a transport-and-signature layer with no step, join, inspection, ladder, attempt, or target-state concept. It becomes relevant only if the project decides to publish attempt attestations to a transparency log for third-party verification. |
| Is **RFC 9334 (RATS)** comparable? | **Only as an architectural target and a row-coverage reference.** It ships no implementation. Note that the task brief's premise about it is inaccurate: it prescribes **no** Rekor, **no** DSSE, **no** keyless identity, and its "thresholds" are *freshness time thresholds*, not signature-count thresholds. |
| Are the project's existing `digest-only` / `digest-session` baselines in-toto or SLSA? | **No.** They are explicitly-labelled offline *models of design classes* (`b2_prov_baselines.py` lines 10–13). They must never be reported as product results. |
| What is the honest, defensible claim? | Not "we beat in-toto/SLSA". It is: **"Under a common 10-row contract, the established provenance systems natively cover P1–P4 (in-toto), P1–P3 (cosign), and P1–P3 + a partial P8 (slsa-verifier), while P6 (freshness/epoch), P7 (target binding) and P9 (claim aggregation) are uncovered by all three; we give a constructive mechanism for all ten and measure it against the real in-toto verifier on rows P1–P4, P5(inspection) and P8(inspection), with the custom-construction rows labelled as ours."** |

---

## 10. Source list (all retrieved 2026-10-20)

**in-toto**
1. Specification (layout, step, inspection, link, artifact rules, goals/non-goals, terminology, workflow): https://github.com/in-toto/docs/blob/master/in-toto-spec.md — raw: https://raw.githubusercontent.com/in-toto/docs/master/in-toto-spec.md
2. Reference-implementation docs (metadata model, CLI): https://in-toto.readthedocs.io/en/latest/model.html · https://in-toto.readthedocs.io/en/latest/command-line-tools/index.html · https://in-toto.readthedocs.io/en/latest/command-line-tools/in-toto-verify.html · https://in-toto.readthedocs.io/en/latest/command-line-tools/in-toto-run.html · https://in-toto.readthedocs.io/en/latest/installing.html
3. Repository README (design summary, artifact-rule rule list): https://github.com/in-toto/in-toto
4. `verifylib.py` (verification order, exception docstring, link-skipping, thresholds): https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/verifylib.py
5. `in_toto_verify.py` (exit codes, stderr exception class): https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/in_toto_verify.py
6. `exceptions.py` (typed exception hierarchy): https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/exceptions.py
7. `models/layout.py` (no layout-creation CLI helper): https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/models/layout.py
8. `pyproject.toml` (deps, console scripts, requires-python): https://raw.githubusercontent.com/in-toto/in-toto/develop/pyproject.toml
9. PyPI metadata: https://pypi.org/pypi/in-toto/json
10. Attestation framework spec (v1.2: Predicate/Statement/Envelope/Bundle): https://github.com/in-toto/attestation/blob/main/spec/README.md

**SLSA**
11. Provenance predicate v1.0 (schema, buildDefinition/runDetails, verification pointer): https://slsa.dev/spec/v1.0/provenance
12. Verifying Artifacts (roots of trust, three-step procedure, expectations, threat mapping E/F/G/H, resolvedDependencies caveat): https://slsa.dev/spec/v1.0/verifying-artifacts
13. Current spec (v1.2) and VSA spec: https://slsa.dev/spec/v1.2/provenance · https://slsa.dev/spec/v1.1/verification_summary
14. slsa-verifier README (maintenance banner, supported builders, install, option list, VSA, caveats, TOCTOU): https://github.com/slsa-framework/slsa-verifier/blob/main/README.md
15. `verifiers/verifier.go` (verifier dispatch: gcb/gha/vsa only): https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/verifiers/verifier.go
16. `verifiers/internal/gha/slsaprovenance/` (v0.2 and v1.0 parsers only): https://github.com/slsa-framework/slsa-verifier/tree/main/verifiers/internal/gha/slsaprovenance
17. `cli/slsa-verifier/verify/options.go` (flags; `--source-uri` required; no `--trusted-root`): https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/cli/slsa-verifier/verify/options.go
18. `cli/slsa-verifier/verify/verify_artifact.go` (implicit artifact digest): https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/cli/slsa-verifier/verify/verify_artifact.go
19. `cli/slsa-verifier/verify.go` (PASSED/FAILED, exit 1): https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/cli/slsa-verifier/verify.go
20. `options/options.go` (ExpectedDigest, ExpectedSourceURI, …): https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/options/options.go
21. `verifiers/utils/sigstore_tuf.go` (hard-wired Sigstore trusted root): https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/verifiers/utils/sigstore_tuf.go
22. `verifiers/internal/vsa/verifier.go` (VSA verification steps; offline public key): https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/verifiers/internal/vsa/verifier.go
23. `verifiers/internal/vsa/v1.0/vsa.go` (VSA predicate schema): https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/verifiers/internal/vsa/v1.0/vsa.go
24. `errors/errors.go` (typed error sentinels): https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/errors/errors.go
25. Releases: https://github.com/slsa-framework/slsa-verifier/releases/tag/v2.7.1

**Sigstore / cosign**
26. Verifying signatures (keyless, bundles, `verify-blob`, `verify-attestation`): https://docs.sigstore.dev/cosign/verifying/verify/ — source: https://raw.githubusercontent.com/sigstore/docs/main/content/en/cosign/verifying/verify.md
27. In-toto attestations via cosign + CUE/Rego predicate validation: https://raw.githubusercontent.com/sigstore/docs/main/content/en/cosign/verifying/attestation.md
28. Installation: https://raw.githubusercontent.com/sigstore/docs/main/content/en/cosign/system_config/installation.md
29. `cosign verify-blob` reference: https://raw.githubusercontent.com/sigstore/cosign/main/doc/cosign_verify-blob.md
30. `cosign verify-attestation` reference: https://raw.githubusercontent.com/sigstore/cosign/main/doc/cosign_verify-attestation.md
31. `cmd/cosign/cli/verify/verify_blob.go` (blob↔digest binding, `--trusted-root`/bundle constraints): https://raw.githubusercontent.com/sigstore/cosign/main/cmd/cosign/cli/verify/verify_blob.go
32. sigstore-go TUF defaults (embedded root, `~/.sigstore/root` cache, mirror URL): https://raw.githubusercontent.com/sigstore/sigstore-go/main/pkg/tuf/options.go
33. Releases: https://github.com/sigstore/cosign/releases/tag/v3.1.3

**RATS**
34. RFC 9334 (full text, used for both the positive claims and the exhaustive zero-hit searches): https://www.rfc-editor.org/rfc/rfc9334.txt — info page: https://www.rfc-editor.org/info/rfc9334

**Local project (read-only)**
35. `sp2027/analysis/experiment_b_20261019/b2/B2_PROTOCOL.md` (design-class models; §3 faithful-model caveat; §5 case sets; §6 metrics and gates; §7 predictions)
36. `sp2027/analysis/experiment_b_20261019/b2/b2_prov_baselines.py` (lines 10–13: "NOT the actual products")
37. `sp2027/analysis/experiment_b_20261019/b2/B2_BASELINE_COMPARISON_REPORT.md` (measured results, hashes, overheads)
38. `sp2027/analysis/experiment_b_20261019/b2/freeze/B2_FREEZE.json` (freeze packet)
39. `sp2027/analysis/experiment_b_20261019/eb_v3_sig.py`, `eb_v3_full.py`, `eb_adjudicator.py` (arms A0 and truth source)
40. `sp2027/analysis/contract_sound_exploitation_preregistration_v1.md` (harness contract, rungs, exclusions)

### 10.1 Items marked **[UNVERIFIED]** in this document

1. The minimum Go version required by `slsa-verifier` v2.7.1's `go.mod` (the file was not fetched). The local toolchain is go1.22.2; compatibility must be checked at install time.
2. All overhead figures in §7.4 are **[ESTIMATE]**. No timing was measured because installation was not authorized. The only measured overhead numbers in this document are the project's own, from `B2_BASELINE_COMPARISON_REPORT.md` §4.2.
3. The exact content of in-toto's `in-toto-verify` `--inspection-timeout` default is documented as 10 seconds [DOC] and was not re-verified against `in_toto.settings.LINK_CMD_EXEC_TIMEOUT` in source.

---

*End of AGENT3 provenance comparator analysis. One file written; no other repository file was modified; no package was installed; no authenticated or write request was made; all upstream access was read-only HTTP GET of public documentation and public source trees.*
