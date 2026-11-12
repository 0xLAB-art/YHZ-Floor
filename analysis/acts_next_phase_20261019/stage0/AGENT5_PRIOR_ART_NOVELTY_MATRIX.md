# AGENT5 — Prior-Art / Novelty Matrix for the ACTS-Attack Evidence-Binding Chain

**Date:** 2026-10-20
**Role:** Independent prior-art / novelty reviewer (subagent). Research-only.
**Question under review:** Is the ACTS-Attack proposal — a *causal evidence-binding chain for AI-agent security evaluation* — novel relative to published prior art?

**Scope note.** This is a novelty review, not an endorsement. It is deliberately conservative. The value of this document is that it is defensible against a hostile reviewer, not that it is exciting.

**Constraints honored.** No repository file was modified other than this new file. No packages installed, no binaries downloaded, no experiments run. Reading was done via `websearch`, `webfetch`, and read-only `curl` of public specification/paper/repository text. No model/provider calls.

---

## 0. What exactly is being claimed

The candidate contribution, as stated in the tasking and in `sp2027/analysis/EVALUATOR_BOUNDARY_NOVELTY_PROPOSAL.md` §3 and §7, is a chain of bindings:

> program source bytes (SHA-256) → exact executed program bytes → invocation command/args → execution environment identity/version → input/public-instance digest → target identity and state digest → execution attempt/session identity → captured stdout/stderr → parsed output artifact digest → an INDEPENDENT cryptographic reference-verifier verdict → signed evidence records with explicit issuer identity and role → aggregated certificate → final attributed success claim.

Six mechanism ingredients are evaluated below:

| ID | Ingredient (as tasked) |
|---|---|
| **(a)** | A **trusted execution observer** that is a *different party* from the artifact producer, so the chain does not rest solely on hashes supplied by an untrusted producer |
| **(b)** | **Claim-specific JOIN predicates** — each claim level requires its own binding (artifact authorship, execution identity, target effect, reference-oracle acceptance, boundary enforcement, final attribution) |
| **(c)** | **Tri-state adjudication** — MISSING evidence must yield INCONCLUSIVE; CONTRADICTORY evidence must yield REJECT (a false-acceptance vs false-rejection asymmetry) |
| **(d)** | **Freshness epoch + replay ledger** binding attempt/session identity |
| **(e)** | **Signer role authorization** — which issuer role may attest which kind of claim |
| **(f)** | A **final-claim aggregator** that cannot conceal execution failures or overclaims |

**Legend used in the matrix.** `NATIVE` = the mechanism is specified/present in the work itself. `CUSTOM` = the work supplies the substrate but the mechanism requires substantial user-supplied logic. `ABSENT` = the work does not address it. `UNVERIFIED` = I could not obtain/inspect the primary source, so the cell is not assessed.

**Depth / source-type legend.** `PRIMARY·full text` = I read the mechanism sections of the primary artifact (spec, paper, or code). `PRIMARY·abstract` = I read only the abstract / official abstract-level record. `PRIMARY·code+README` = I read the repository README and source text but did not audit the code. `SECONDARY·snippet` = I only saw search-result snippets or third-party summaries; the primary source was not obtained.

---

## 1. THE MATRIX

| # | Work | (a) Trusted observer ≠ producer | (b) Per-claim join predicates | (c) MISSING→INCONCLUSIVE vs CONTRADICTORY→REJECT | (d) Freshness epoch + replay ledger | (e) Signer role authorization | (f) Final-claim aggregator that cannot conceal failure | Primary source URL | Depth / source type |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **RFC 9334 — RATS Architecture** (IETF, Jan 2023) | **NATIVE** — Attesting Environment is isolated from the Target Environment it measures (§12.1.1); Verifier is a distinct role from Attester; Evidence is appraised against an *Appraisal Policy for Evidence* | **NATIVE** — Claims set; §8.5 lists constraint kinds (equality vs Reference Value, range, set membership, cross-Claim check); separate policies for Evidence and for Attestation Results | **CUSTOM** — §8.4 boolean compliance/non-compliance, but §8.4 notes a result "may even indicate that the Evidence itself cannot be authenticated as being correct"; no formal tri-state verdict | **NATIVE** — §10 gives three freshness mechanisms (synchronized-clock timestamps, verifier nonces, distributor-issued **epoch IDs** with an epoch window); §12.2 requires "replay attack prevention" for any conceptual message; §12.3 analyses epoch-ID replay/drop/reorder and the **"confusion attack"** | **NATIVE** — Attester / Verifier / Relying Party / Relying Party Owner / Verifier Owner / Endorser / Reference Value Provider, each with its own trust anchor store (§7) and its own policy ownership | **NATIVE** — Verifier produces signed **Attestation Results** consumed by the Relying Party, which applies its own policy (§8.4); results "signed by a Verifier, allowing a Relying Party to only need a trust relationship with one entity" | https://www.rfc-editor.org/rfc/rfc9334.html | PRIMARY·full text (§§1–14 + App. A read) |
| 2 | **in-toto Specification v1.0.0** (in-toto docs) | **NATIVE** — §1.5.3: "we recommend separating the mechanisms responsible for in-toto metadata generation from those executing the steps themselves" (via `in-toto-record`); "Client inspection step" = an independent verification step; §1.5.4 "Task and privilege separation" | **NATIVE** — per-step `expected_materials`/`expected_products` artifact rules (MATCH / CREATE / DELETE / MODIFY / ALLOW / REQUIRE / DISALLOW) with explicit pseudocode (§4.3.3.1–.3); MATCH ties step A's product hash to step B's material | **CUSTOM** — §5.2 verification is fail-closed, and the reference implementation separates failure classes, but the *spec* defines no INCONCLUSIVE verdict; missing-evidence and bad-evidence are not specified as distinct outcomes | **NATIVE (partial)** — layout `expires` field; "Clients MUST NOT trust an expired file"; §1.5.2 states in-toto "inherently does not protect against attackers replaying older, as-yet unexpired layouts" and points to TUF for the replay ledger | **NATIVE** — layout carries `pubkeys` per step; a functionary is identified by the key that signs its link; `threshold` for multi-party steps; sublayout delegation | **NATIVE** — the "final product" aggregates layout + all link metadata + target files; client verification must check every step (§5.1–5.2) | https://raw.githubusercontent.com/in-toto/docs/master/in-toto-spec.md (canonical: https://github.com/in-toto/docs/blob/master/in-toto-spec.md) | PRIMARY·full text (§§1–5.3 read) |
| 3 | **in-toto reference implementation** | CUSTOM (separation tool `in-toto-record` is implemented) | NATIVE (rule engine) | **CUSTOM** — distinct exception types for "no signature found for key" vs "invalid signature" exist in `in_toto/models/metadata.py`; the *unfulfilled-step* vs *bad-link* distinction lives in the verifier, which I did **not** locate by grep in `runlib.py`/`layout.py` | ABSENT (no epoch/ledger in core) | NATIVE (keyid↔step) | CUSTOM | https://github.com/in-toto/in-toto | PRIMARY·code (partial; `metadata.py` read, verifier module not located) |
| 4 | **SLSA Provenance v1.0** | **NATIVE** — `runDetails.builder.id` = the trusted build platform (the observer); "The builder is distinct from the signer in order to support the case where one signer generates attestations for more than one builder" | **NATIVE** — `subject` digest, `buildType`, `externalParameters` ("Verifiers SHOULD reject unrecognized or unexpected fields within externalParameters"), `resolvedDependencies`, `metadata.invocationId` — each is a separate verification condition | **ABSENT** — the predicate carries no verdict; verdicts live in the VSA, which is binary | **CUSTOM** — `invocationId` ("SHOULD be globally unique") + `startedOn`/`finishedOn`; the v1.0 predicate has **no expiry field**, so freshness is not natively bound to a session | **NATIVE** — "Consumers MUST accept only specific signer-builder pairs"; `builder.id` is "the sole determiner of the SLSA Build level" | CUSTOM (provenance is an input, not a verdict) | https://slsa.dev/provenance/v1.0 | PRIMARY·full text |
| 5 | **SLSA v1.0 — "Verifying artifacts"** | **NATIVE** — roots of trust map *(builder public key identity, builder.id) → SLSA Build Level* | **NATIVE** — Step 1/2/3 decompose verification into per-field checks (signature, subject digest, predicateType, builder level, canonical source repo, buildType, externalParameters) with fail-closed semantics | CUSTOM (binary; distinct threat IDs E/F/G/H encode *why* verification failed) | ABSENT (no freshness requirement stated on this page) | NATIVE (the roots-of-trust map) | CUSTOM | https://slsa.dev/spec/v1.0/verifying-artifacts | PRIMARY·full text |
| 6 | **SLSA Verification Summary Attestation (VSA) v1.0** | **NATIVE** — `verifier.id` = the independent verifier entity | NATIVE (per-level claims: `verifiedLevels`, `dependencyLevels`) | **ABSENT (explicitly binary)** — `verificationResult` is `"PASSED"` or `"FAILED"`; no INCONCLUSIVE value exists in the schema | **CUSTOM** — `timeVerified` timestamp only; no epoch/nonce/replay ledger | **NATIVE** — "Consumers MUST accept only specific (signer, verifier) pairs" | **NATIVE** — this *is* the aggregated certificate: `inputAttestations` (digests of all attestations used), `policy` (uri+digest), `timeVerified`, `verifier.id`, `verificationResult` | https://slsa.dev/verification_summary/v1.0 | PRIMARY·full text |
| 7 | **slsa-verifier** (reference implementation) | CUSTOM | **NATIVE** — per-argument join predicates as separate CLI checks: `--source-uri`, `--source-branch`, `--source-tag`, `--source-versioned-tag`, `--build-workflow-input`, `--builder-id` | CUSTOM (tool returns per-check failures; not a tri-state contract) | **UNVERIFIED** — README grep found no `--max-age`/expiry flag; the `verifier.go` path I guessed returned no matches. Freshness in the tool is **not confirmed** | NATIVE (`--builder-id`) | CUSTOM | https://github.com/slsa-framework/slsa-verifier | PRIMARY·code+README (partial; grep-level) |
| 8 | **TUF Specification v1.0.37** (2026-10-08) | **CUSTOM** — role separation is about *key custody* (root offline, timestamp online), not an observing party distinct from a producer | **NATIVE** — `snapshot.json` binds version+length+hashes per targets-metadata file; `targets.json` binds length+hashes per target file; per-item, per-file predicates | **CUSTOM** — binary accept/reject, but with *distinct reported failure reasons* ("report the signature failure", "report the rollback attack") and an explicit distinction between "not found" (missing) and "version not incremented" (contradictory) | **NATIVE** — `expires` on every metadata file; monotonic `version` = rollback protection; timestamp role "frequently re-signed to limit the amount of time a client can be kept unaware of interference" and to "prevent an adversary from replaying an out-of-date signed metadata file whose signature has not yet expired"; consistent snapshots block mix-and-match | **NATIVE** — root/targets/snapshot/timestamp/mirrors roles with `keyids` + `threshold`; delegated roles constrained by `paths` / `path_hash_prefixes` so a delegated role is trusted **only for specific artifacts** | CUSTOM (no aggregated final-claim object) | https://theupdateframework.io/specification/latest/ | PRIMARY·full text (§§1–5.4 read) |
| 9 | **Sigstore Fulcio** | **NATIVE** — CA issues a short-lived (10-minute) cert binding an *external* OIDC identity (e.g. CI workflow identity) to a public key; the signer cannot self-assert its identity | CUSTOM (identity binding only; claim predicates left to consumer) | CUSTOM | CUSTOM (short cert lifetime bounds replay) | **NATIVE** — cert extensions carry the OIDC issuer + identity; downstream policy enforces which identity may attest what | ABSENT | https://github.com/sigstore/fulcio | PRIMARY·code+README (README read) |
| 10 | **Sigstore Rekor** | ABSENT | ABSENT | CUSTOM (distinct error paths for missing entry vs. failed inclusion proof) | **NATIVE** — "immutable tamper resistant ledger"; "query the transparency log for inclusion proof"; append-only, signed, log-indexed | CUSTOM | ABSENT | https://github.com/sigstore/rekor | PRIMARY·code+README (README read) |
| 11 | **sigstore-go / cosign verification** | NATIVE (via Fulcio identity) | CUSTOM | **CUSTOM** — `pkg/verify/errors.go` defines `ErrVerification` (contradictory); the "no signature found" path exists in the same package but I did **not** enumerate the full taxonomy | CUSTOM | CUSTOM | ABSENT | https://github.com/sigstore/sigstore-go | PRIMARY·code (partial; `pkg/verify/errors.go` read) |
| 12 | **ILAC-G8:09/2019** + ISO/IEC 17025:2017 §7.8.6 | ABSENT | ABSENT | **NATIVE** — the canonical statement of the *asymmetry* and the *third outcome*: decision rules are "designed to protect against the risk of false acceptance (declaring a nonconforming item as conforming) and false rejection (rejecting a conforming item)"; where the measurement overlaps the acceptance limit "it is not possible to state compliance or non-compliance" → **Indeterminate / Conditional Pass / Conditional Fail** | ABSENT | ABSENT | ABSENT | https://ilac.org/publications-and-resources/ilac-guidance-series (document PDF mirror: https://dastmardi.ir/wp-content/uploads/2020/11/ILAC_G8_09_2019.pdf) | SECONDARY·snippet (ILAC landing page read; **full PDF not obtained**) |
| 13 | **ISO/IEC 19795** biometric performance testing (FAR/FRR) | ABSENT | ABSENT | **NATIVE (terminology)** — the standard paired error metrics for a security decision system: false accept rate / false reject rate | ABSENT | ABSENT | ABSENT | https://www.nist.gov/document/3401mansfieldpanelibpcpdf (NIST panel presentation on ISO/IEC 19795) ; https://www.iso.org/standard/91306.html (ISO/IEC 19795-10 catalogue) | SECONDARY·snippet (abstract-level only) |
| 14 | **CyberGym** (arXiv:2506.02548) | **ABSENT** — the verifier is the benchmark harness, not an attested separate party | **NATIVE** — differential execution predicate: the PoC must trigger on the **pre-patch** build and **not** on the **post-patch** build; the PoC bytes are bound to a specific task/pre-patch commit | ABSENT (binary success) | **CUSTOM** — task/instance identity and per-instance containerization, but no epoch or replay ledger | ABSENT | ABSENT | https://arxiv.org/abs/2506.02548 ; https://www.cybergym.io/cybergym | PRIMARY·abstract |
| 15 | **ExploitBench** (arXiv:2605.14153) | ABSENT | **NATIVE** — 16 *separately measured* capability flags, each with its own deterministic oracle; differential execution against ground-truth binaries | ABSENT (binary per flag) | **NATIVE (partial)** — "per-run randomized **challenge-response**" for primitives: a run-scoped nonce binding the oracle exchange to that run | ABSENT | ABSENT | https://arxiv.org/abs/2605.14153 | PRIMARY·abstract |
| 16 | **ReproBench** (arXiv:2609.34450) | ABSENT | **NATIVE** — six phases, each "assessed … independently using verifiable experimental artifacts" (firmware images, unpacked binaries, analysis logs, validated crash samples) | ABSENT | CUSTOM (per-phase artifacts) | ABSENT | ABSENT | https://arxiv.org/abs/2609.34450 | PRIMARY·abstract |
| 17 | **ExploitGym** (arXiv:2605.11086) | ABSENT | ABSENT | ABSENT | ABSENT | ABSENT | ABSENT | https://arxiv.org/abs/2605.11086 | PRIMARY·abstract (title/record verified via arXiv API) |
| 18 | **CryptanalysisBench** (arXiv:2607.18538) | ABSENT | CUSTOM (independently verifiable attack criteria) | ABSENT | ABSENT | ABSENT | ABSENT | https://arxiv.org/abs/2607.18538 | PRIMARY·abstract (title/record verified via arXiv API) |
| 19 | **Governing Dynamic Capabilities** (arXiv:2603.14332) | **NATIVE** — capability-context separation; the governance layer cryptographically binds what the agent did, independently of the agent | **NATIVE** — capability integrity (G1), behavioral verifiability (G2), interaction auditability (G3) | CUSTOM (zero false positives reported; no explicit INCONCLUSIVE class) | **NATIVE** — "**Bounded Divergence Theorem** (replay-based verification yields a probabilistic safety certificate, ε ≤ 1 − α^(1/n))" — replay is the freshness primitive and it is *theorized* | **NATIVE** — governance-layer roles (capability issuer vs. runtime) | **NATIVE** — end-to-end chain verification over 5–20-agent pipelines; "**Chain Verifiability Theorem** (one unverifiable interior agent breaks end-to-end verification)" | https://arxiv.org/abs/2603.14332 | PRIMARY·abstract |
| 20 | **When Agent Evaluation Becomes Unreliable** (arXiv:2610.16067) | **ABSENT** — the auditor is the harness author; no independent attested observer | **NATIVE** — five state-integrity invariants + three known-answer controls; seven injected oracle defect classes; artifact gates (validity regression, order/cache counterexample, scoring regression, source binding) | **NATIVE (in substance)** — the whole paper is framed as measuring an evaluator's false positives/negatives: "All injected defect classes are detected, and the repaired oracle has no false positives" | **CUSTOM** — replay-based correction of labels (4,194 → 2,883 over 4,320 episodes) is a replay *check*, not a ledger | ABSENT | CUSTOM (explicit **portability boundary**: the audit cannot validate a second independently implemented benchmark) | https://arxiv.org/abs/2610.16067 | PRIMARY·abstract |
| 21 | **TRAP / ReplayBench** (arXiv:2610.16333) | ABSENT | ABSENT | ABSENT | **NATIVE (runtime layer)** — "tool-result **misbinding**": a genuine, unmodified tool output consumed in an incompatible execution context; cross-task replay mean Final-State Error Rate **0.649** | ABSENT | ABSENT | https://arxiv.org/abs/2610.16333 ; https://github.com/Phitooo/Replaybench | PRIMARY·abstract |
| 22 | **From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents** (arXiv:2606.04990v4) | CUSTOM | **NATIVE (taxonomy)** — claim-support graphs with typed relations Support / Contradict / Depend-on / Invalidate / Trigger / Update; §3.2 | **NATIVE (taxonomy, "Proposed" maturity)** — §3.2: claim–evidence mapping "explicitly distinguishes **supported claims, unsupported claims, and omitted evidence**" | CUSTOM — §6.3 lists *temporal consistency* as a proposed execution-provenance metric | ABSENT | CUSTOM — "failure attribution" is a trust function; no cryptographic aggregator specified | https://arxiv.org/html/2606.04990v4 | PRIMARY·full text (§§1–8 read) |
| 23 | **llmsa — LLM Supply-Chain Attestation** (GitHub) | **CUSTOM** — collectors run in the producer's CI, but Sigstore keyless OIDC makes the *identity* externally vouched rather than self-asserted | **NATIVE** — provenance-chain verification over a typed DAG: type-based dependencies ("an eval attestation must reference both prompt and corpus attestations"), ID-based `depends_on` references, temporal ordering, unknown/dangling-reference detection; four-stage pipeline (Signature → Schema → Digest → Chain) | **NATIVE** — explicit MISSING vs CONTRADICTORY separation: exit **10 = "Missing attestation or bundle"**, **11 = signature verification failure**, **12 = subject digest mismatch (tamper detected)**, **14 = schema/chain invalid**; plus "Policy enforcement in CI for **deny-on-missing-or-invalid evidence**" and fail-closed K8s admission | **NATIVE (partial)** — temporal ordering enforced ("Predecessor attestations must have been generated before their successors"); Rekor transparency-log integration is on the **roadmap**, not shipped | **NATIVE** — Sigstore keyless signing binds attestations to the CI workflow identity (e.g. `github.com/org/repo/.github/workflows/attest.yml@refs/heads/main`); OIDC issuer verified | **NATIVE** — chain verifier + admission webhook as final gate; "every claim about model quality (eval) is bound to the exact artifacts (prompt + corpus) it was tested against"; 20-case tamper-detection suite | https://github.com/ogulcanaydogan/LLM-Supply-Chain-Attestation | PRIMARY·code+README (README read; code not audited) |
| 24 | **EAT / Entity Attestation Token (RFC 9335)** | NATIVE (attesting party vs. authorizing party) | NATIVE (typed claims) | ABSENT | NATIVE (nonce) | NATIVE (attesting-environment identifier) | CUSTOM | https://www.rfc-editor.org/rfc/rfc9335.html | SECONDARY·snippet (read via RFC 9334's reference list only) |
| 25 | **"Grounded but Wrong: Claim–Computation Binding Catches Spoofable Provenance"** (preprints 202610.0322) | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | https://doi.org/10.20944/preprints202610.0322.v1 | **NOT OBTAINED** — cited from the project's own `HEB1_PRIOR_ART_ASSESSMENT_20261019.md`; per the project's own record, preprints.org returned 403 on two attempts. The project record claims 12 safeguards, a 28.9% → 2.2% run-level defect-rate reduction, Holm-corrected p = 0.0055, and ~26% of claims citing a real-but-wrong-variable statistic. **I did not verify any of these numbers.** |

---

## 2. MECHANISM-LEVEL COMPARISON

This section compares **mechanisms**, not vocabulary. Keyword overlap is explicitly discounted: "attestation", "provenance", "agent", "claim" and "verification" appear in nearly every row above, and that overlap carries no novelty weight.

### 2.1 Ingredient (a) — Trusted execution observer distinct from the artifact producer

**This is the single most heavily precedented ingredient, and the precedent is architectural rather than incidental.**

- **RFC 9334 §3.1** makes it a *structural* requirement: the Attester consists of an **Attesting Environment** and a **Target Environment**; the Attesting Environment "collects Claims" from the Target Environment and signs them. §12.1.1: "It is assumed that an Attesting Environment is sufficiently isolated from the Target Environment it collects Claims about and that it signs the resulting Claims set with an attestation key **so that the Target Environment cannot forge Evidence about itself**." That is ingredient (a) stated as a threat model, with the isolation boundary named.
- **RFC 9334 §8.1** goes further and names the *failure mode ACTS-Attack proposes to discover*: "Evidence needs to be securely associated with the Target Environment **so that the Verifier cannot be tricked into accepting Claims originating from a different environment** (that may be more trustworthy)." This sentence is, in condensed form, the HEB-1 "cross-boundary verdict promotion" mechanism — published in an IETF Informational RFC in January 2023.
- **SLSA v1.0** separates the *observer* (`runDetails.builder.id` = the trusted build platform) from the *signer*, and says so explicitly: "The builder is distinct from the signer in order to support the case where one signer generates attestations for more than one builder." So a one-signer-many-builders topology — exactly the topology ACTS-Attack needs between an artifact producer and an execution observer — is a first-class, specified case.
- **in-toto §1.5.3** recommends the same separation operationally: "separating the mechanisms responsible for in-toto metadata generation from those executing the steps themselves," with `in-toto-record` named as the tool for it.
- **Sigstore/Fulcio** provides the *identity* half: a CA binds an external OIDC identity to a signing key, so the issuer's identity is not self-asserted.
- **Governing Dynamic Capabilities (arXiv:2603.14332)** proposes the same separation at the *agent-orchestration* layer (capability-context separation; the governance layer, not the agent, attests what was executed).

**Verdict on (a): NATIVE, long-standing, and already the default architecture of the relevant standards. Not a contribution.**

### 2.2 Ingredient (b) — Claim-specific join predicates

The mechanism is: *each* claim level is a separately-evaluated join, and satisfaction of a weaker join does not license a stronger one.

- **in-toto** is the canonical implementation: per-step `expected_materials` / `expected_products` with MATCH/CREATE/DELETE/MODIFY/ALLOW/REQUIRE/DISALLOW rules and specified evaluation pseudocode (§4.3.3.1). A MATCH rule is literally a *hash-equality join between two named steps' artifacts*; a step's link must be signed by the key the layout authorizes for that step. A claim ("this step's product is the next step's material") is bound by its own predicate, and the framework is designed so that a link cannot satisfy a step it was not issued for.
- **SLSA v1.0 "Verifying artifacts"** decomposes verification into Step 1 (builder identity in roots of trust, envelope signature, subject digest match, predicateType, build level) and Step 2 (per-field *expectations* for canonical source repo, `buildType`, `externalParameters`), with "Verification tools SHOULD reject unrecognized fields in externalParameters to err on the side of caution." Each field is an independent join condition; unrecognized ⇒ fail.
- **SLSA Provenance** formalizes trust scoping of the *inputs*: `externalParameters` are "untrusted; they MUST be included in the provenance and MUST be verified downstream", while `internalParameters` "are trusted because the platform is trusted." That is an explicit per-claim trust gradient — the very thing ACTS-Attack's "artifact authorship vs. execution identity vs. target effect" ladder encodes.
- **TUF** does it per item: `snapshot.json` binds version+length+hashes for each targets-metadata file; `targets.json` binds length+hashes for each target file. No item is accepted on the strength of another item's verification.
- **CyberGym** does it in the target domain: the success predicate is a *two-sided* join — "verifying the PoC triggers on the pre-patch version but not on the post-patch version." A PoC that crashes both builds, or neither, does not satisfy the claim. This is the exact shape of the ACTS-Attack "target effect" join predicate.
- **ExploitBench** does it per capability: 16 flags, each with its own deterministic oracle, per-run randomized challenge-response, and differential execution against ground-truth binaries — i.e. per-claim joins with per-run freshness and an independent reference.

**Verdict on (b): NATIVE in at least five independent standards/benchmarks, including two in the AI-agent exploitation domain. Not a contribution.**

### 2.3 Ingredient (c) — MISSING → INCONCLUSIVE vs. CONTRADICTORY → REJECT, with a false-acceptance / false-rejection asymmetry

This is the ingredient with the **most interesting** prior-art profile, and the assessment is nuanced.

- **The asymmetry is not a new idea.** It is the classical Type I / Type II error pair, given a standardized home in **ISO/IEC 19795** as FAR / FRR for a security decision system, and given its *decision-theoretic* home in **ILAC-G8:09/2019**, which explicitly frames decision rules as being "designed to protect against the risk of **false acceptance** (declaring a nonconforming item as conforming) and **false rejection** (rejecting a conforming item)," and which defines the **third outcome** — where the measurement overlaps the acceptance limit, "it is not possible to state compliance or non-compliance" — reported as *Indeterminate / Conditional Pass / Conditional Fail*. This is precisely the MISSING-vs-CONTRADICTORY structure, abstracted from security into general conformity assessment, and it predates the current literature by a decade.
- **The three-way claim-level distinction already exists in the AI-agent literature.** The 2026 survey arXiv:2606.04990 §3.2 reports that claim–evidence mapping "explicitly distinguishes **supported claims, unsupported claims, and omitted evidence**." Omitted evidence ≠ contradictory evidence is exactly the MISSING/INCONCLUSIVE vs CONTRADICTORY/REJECT split, at claim granularity, in the LLM-agent domain. The survey also records the *maturity* of the relevant metrics: evidence-attribution metrics are "Established"; execution-provenance metrics (trace completeness, provenance accuracy, dependency coverage, temporal consistency) are only "**Proposed**" — i.e. proposed, not yet operationalized.
- **A shipped implementation already separates MISSING from CONTRADICTORY.** `llmsa` uses distinct exit codes (10 missing, 11 signature failure, 12 digest mismatch) and states the policy as "deny-on-missing-or-invalid evidence" with fail-closed admission.
- **The measurement of evaluator false positives/negatives is already an established genre.** arXiv:2610.16067 measures an LLM-agent benchmark's oracle with fault injection, known-answer controls, and reports "no false positives"; arXiv:2603.14332 reports "detection of all attack scenarios with zero false positives" with a measured <0.02% overhead; the project's own cited "Grounded but Wrong" record claims a 28.9% → 2.2% run-level defect-rate reduction with Holm-corrected p = 0.0055 (unverified by me).
- **But the *specific standards* ACTS-Attack leans on are binary.** SLSA's VSA is explicitly `"PASSED"` or `"FAILED"`. RFC 9334's Attestation Result is a boolean compliance/non-compliance flag. TUF is accept/reject with distinct *reasons*. So the tri-state is **not** native to the provenance standards; it must be added.

**Verdict on (c): the *principle* is a known general principle (A); the *tri-state contract over a provenance chain* is a small, defensible engineering increment over binary provenance verdicts, but it is not novel as a concept and is not novel as an implementation (llmsa) or as a taxonomy (arXiv:2606.04990).**

### 2.4 Ingredient (d) — Freshness epoch + replay ledger bound to attempt/session identity

- **RFC 9334 §10** gives three native mechanisms and explicitly names the third "**Epoch IDs**" with an "epoch window," a distributor, and analysis of the attack surface in §12.3 (tamper, replay, drop, delay, reorder; the "confusion attack" where "a Verifier can be tricked into accepting Evidence coming from a past epoch as fresh"). §12.2 requires "end-to-end integrity protection and **replay attack prevention**" for *any* solution conveying conceptual messages.
- **TUF** is the reference implementation of a replay-resistant ledger: monotonic `version` (rollback protection), `expires` on every metadata file, and the **timestamp role** that is "frequently re-signed to limit the amount of time a client can be kept unaware of interference" and exists "to prevent an adversary from replaying an out-of-date signed metadata file whose signature has not yet expired." This is a *replay ledger bound to a versioned snapshot*, i.e. ingredient (d) with a named role and a named threat.
- **Sigstore Rekor** is an append-only, tamper-resistant, inclusion-proof transparency log — a literal ledger.
- **ExploitBench** binds the oracle exchange to the run with a **per-run randomized challenge-response** — the nonce pattern from RFC 9334 §10.2, applied to exploit verification.
- **SLSA Provenance** provides `metadata.invocationId` ("SHOULD be globally unique") plus `startedOn`/`finishedOn` — the attempt/session identity — but the v1.0 predicate has **no expiry or epoch field**, so the freshness *binding* is not closed in the artifact itself; it must be imposed by the verifier or a transparency log.
- **TRAP/ReplayBench (arXiv:2610.16333)** demonstrates that the *replay/misbinding* phenomenon is now a measured, named failure mode in the agent runtime: cross-task replay mean Final-State Error Rate 0.649, with mitigation via "explicit contextual binding in tool-using agent runtimes."

**Verdict on (d): NATIVE, heavily precedented, and the threat taxonomy (including the specific confusion attack) is published. Not a contribution.**

### 2.5 Ingredient (e) — Signer role authorization

- **RFC 9334** separates *seven* roles, each with its own trust anchor store and its own policy ownership: "Appraisal Policy for Evidence" is owned by the Verifier Owner; "Appraisal Policy for Attestation Results" is owned by the Relying Party Owner. The architecture is built so that different parties can be trusted for different things.
- **in-toto** encodes role authorization in the layout: `pubkeys` per step, `threshold` for multi-party steps, and sublayout delegation (a functionary may act as a project owner for a sub-chain — a *scoped* delegation of attestation authority).
- **TUF** is the most explicit: root/targets/snapshot/timestamp/mirrors with `keyids` + `threshold`, and **delegated roles constrained by `paths` / `path_hash_prefixes`** — a delegated role is trusted *only* for particular artifacts. This is literally "which issuer role may attest which kind of claim."
- **SLSA**: "Consumers MUST accept only specific signer-builder pairs" (provenance) and "Consumers MUST accept only specific (signer, verifier) pairs" (VSA). The roots of trust is a map from *(key identity, builder.id)* to an authorized level.
- **Sigstore/Fulcio**: OIDC issuer + identity embedded in the cert; downstream policy (policy-controller) decides what that identity may attest.

**Verdict on (e): NATIVE and, if anything, the *most* saturated ingredient. Not a contribution.**

### 2.6 Ingredient (f) — Final-claim aggregator that cannot conceal execution failures or overclaims

- **RFC 9334 §8.4**: the Verifier "vouches for the validity of the results" by signing the Attestation Result; the Relying Party then applies *its own* policy to that result. Two-party appraisal, with the result signed by a party that is not the measurer. §3.4 explicitly discusses *combining* roles and warns that "the assumed security properties of the individual components and roles still hold despite the lack of separation and that emergent risk is not introduced" — i.e. the aggregator-concealment concern is itself named.
- **SLSA VSA** is the artifact form of a final claim: it records `verifier.id`, `timeVerified`, `policy.uri` + `policy.digest`, the digests of **all** `inputAttestations` used, and a `verificationResult`. Because `inputAttestations` "MUST contain information on all the attestations used for verification," the summary cannot silently drop a failed input without violating the schema.
- **in-toto**: the "final product" is the aggregation of layout + all links + targets, and client verification must check *every* step; §5.2 is a fail-closed algorithm. The `in-toto attest` command exists precisely to summarize a set of artifacts.
- **llmsa**: the chain verifier plus a Kubernetes validating admission webhook, with exit-code discipline, is an aggregator that "cannot conceal" because the policy is "deny-on-missing-or-invalid."
- **Governing Dynamic Capabilities (arXiv:2603.14332)** supplies the *proof*: the **Chain Verifiability Theorem** ("one unverifiable interior agent breaks end-to-end verification for all downstream nodes") and the **Bounded Divergence Theorem** (replay-based verification ⇒ ε ≤ 1 − α^(1/n)). A theorem that the aggregator *cannot* conceal interior failure is stronger than what ACTS-Attack proposes to demonstrate empirically.

**Verdict on (f): NATIVE in RATS/SLSA/in-toto, and already *theorized* in the 2026 agent-governance literature. Not a contribution; and note that a theorem is a harder-to-beat baseline than a measured detection rate.**

### 2.7 The "cross-boundary verdict promotion" mechanism, located in the literature

The HEB-1 hypothesized mechanism — *a verdict valid for one object/run is promoted into a stronger attribution claim about a different object/run when joins are under-specified* — is not unrecognized. It appears, under different names, in at least five established places:

1. **RFC 9334 §8.1** — "the Verifier [must not be] tricked into accepting Claims originating from a different environment." *(IETF, 2023.)*
2. **RFC 9334 §12.3** — the epoch-ID "confusion attack," where the Verifier accepts past-epoch Evidence as fresh.
3. **TUF §5.3 / rollback protection** — "Clients MUST NOT replace a metadata file with a version number less than the one currently trusted"; the classic rollback/fast-forward/indefinite-freeze family.
4. **SLSA v1.0 "Verifying artifacts"** — Threat "C" (adversary injects unofficial behavior) is mitigated *only* by per-field expectations, which is the standard's own recognition that per-field joins are the control.
5. **TRAP / ReplayBench (arXiv:2610.16333)** — "tool-result misbinding," measured at FSER 0.649, in the agent runtime.
6. **arXiv:2606.04990** — the LLM-agent "misbinding / provenance-substitution" framing, with the survey's own framing of *omitted* vs *contradictory* evidence.

The unifying name for this family is the **confused-deputy / evidence-substitution** pattern, which is decades old. ACTS-Attack's contribution is therefore, at best, a *re-domained instance* of a known pattern and a *new measurement* of its rate in one domain.

### 2.8 Is the *specific combination* in a single prior work?

**No single prior work contains all of (a)–(f) as one specified system.** But the question is close to moot, because:

- The **union** is fully established: RFC 9334 supplies (a), (b), (d), (e), (f) and the failure mode; in-toto supplies (a), (b), (d), (e), (f) with concrete per-join rules; TUF supplies (b), (d), (e) with a replay-resistant ledger; Sigstore supplies (a), (d), (e); SLSA supplies (a), (b), (e), (f) with a *concrete certificate format*. Each ingredient is native somewhere; the assembly is routine engineering.
- More damagingly, the **AI-agent application of the union is already occupied**. `llmsa` (row 23) is a working system with (b) native, (c) native, (e) native, (f) native, (d) partial — and it targets exactly the *evaluation-attribution* use case ("every claim about model quality (eval) is bound to the exact artifacts it was tested against"), with Sigstore keyless issuance, a typed dependency DAG, temporal ordering, MISSING-vs-CONTRADICTORY exit codes, and fail-closed admission. The 2026 survey arXiv:2606.04990 establishes the surrounding research programme, names the exact metrics, and marks them as *proposed*.
- And the **evaluation-side methodology** — fault injection, known-answer controls, false-positive measurement, replay-based correction, hash/schema baselines — is established by arXiv:2610.16067 and arXiv:2603.14332, both of which report *better* quantitative results (zero false positives; 54/57 detection; <0.02% overhead) than ACTS-Attack's proposed endpoint would need to beat to be interesting.

**Conclusion for §2.8:** the combination is established by the union, and the AI-agent application is already implemented and surveyed. Only a narrowly-scoped *measurement* contribution (a validated metric and a reproducible benchmark) survives, and it is a category-C claim at best.

---

## 3. CATEGORY ASSESSMENT A–E

### Category A — Known general principle (anticipated)

**Assessment: STRONGLY SUPPORTED (i.e. the contribution is *this*).**

Every one of the six ingredients is a known general principle with a named home:

- (a) observer/attester independent of the producer → **RFC 9334 §3.1, §12.1.1**; **SLSA `builder.id` vs signer**; **in-toto §1.5.3**; **Sigstore Fulcio**.
- (b) per-claim join predicates → **in-toto artifact rules**; **SLSA per-field expectations**; **TUF per-item hashes**; **CyberGym differential pre/post-patch predicate**; **ExploitBench per-flag oracles**.
- (c) tri-state with false-acceptance/false-rejection asymmetry → **ISO/IEC 19795 FAR/FRR**; **ILAC-G8 Indeterminate**; **arXiv:2606.04990 §3.2** supported/unsupported/omitted; **llmsa exit codes 10 vs 11/12**.
- (d) freshness epoch + replay ledger → **RFC 9334 §10.2/§10.3 + §12.3**; **TUF timestamp role + rollback protection**; **Sigstore Rekor**; **ExploitBench per-run challenge-response**.
- (e) role authorization → **RFC 9334's seven roles**; **in-toto layout pubkeys/threshold/sublayouts**; **TUF delegated roles with `paths`**; **SLSA signer-builder pairs**.
- (f) fail-closed final aggregator → **RFC 9334 §8.4**; **SLSA VSA**; **in-toto final product**; **arXiv:2603.14332 Chain Verifiability Theorem**.

There is no ingredient here that is not a restatement, in AI-evaluation vocabulary, of a 2010–2023 software-supply-chain / remote-attestation mechanism. **The honest verdict is that ACTS-Attack's generic mechanism is Category A.**

### Category B — Known mechanism applied to a new domain (AI-agent exploit evaluation)

**Assessment: STRONGLY SUPPORTED, and the "new domain" is already occupied.**

Category B is the *correct* framing for whatever remains. But its "new domain" claim is weak on two independent grounds:

1. **The domain is not new.** Applying evidence-binding, provenance graphs, and claim-level attribution to LLM agents is the explicit subject of arXiv:2606.04990 (a full survey with a six-dimensional taxonomy, a gap analysis, and a metrics table). Its §6.2 names the *core gaps* — cross-component provenance, relation annotation, recovery-oriented evaluation — and §6.3 lists the proposed metrics ACTS-Attack's endpoint would sit in. §7.2 names "claim-level and semantic provenance" as the open problem.
2. **The application is already implemented.** `llmsa` implements the binding chain for LLM *evaluation* artifacts specifically, including MISSING-vs-CONTRADICTORY adjudication, per-type dependency joins, temporal ordering, Sigstore keyless role/identity binding, and fail-closed admission. arXiv:2603.14332 implements and *theorizes* cryptographic binding + replay-based verification for agent tool use with zero false positives and measured overhead. arXiv:2605.14153 and arXiv:2506.02548 implement per-claim exploit verification with independent differential oracles and run-scoped freshness in the *exploitation* domain specifically.

So the residual novelty in Category B is not "the domain" but "the specific metric and its instantiation for cryptographic exploit-attribution certificates" — a narrow slice, better characterized as a Category C increment.

### Category C — New empirical measurement methodology

**Assessment: WEAKLY TO MODERATELY PLAUSIBLE, but (i) heavily precedented in method and (ii) currently unsupported by the project's own evidence.**

What is *not* new about the method:
- Fault injection into an evaluator + known-answer controls + detection-rate reporting: **arXiv:2610.16067** ("seven injected oracle defect classes… All injected defect classes are detected, and the repaired oracle has no false positives").
- Comparing a richer verifier against simpler baselines, with pre-registration: **arXiv:2603.14332** (basic vs. enhanced crypto instantiations; <0.02% overhead; all attack scenarios detected) and the project's own cited (unverified) "Grounded but Wrong" pre-registered ablation.
- FAR/FRR reporting: **ISO/IEC 19795**; **ILAC-G8**.
- Replay-based correction of labels: **arXiv:2610.16067** (4,194 → 2,883).

What *might* be new: the specific endpoint **"false attribution-promotion rate"** — the rate at which a composed verdict crosses a run/condition boundary and yields a stronger attribution claim than the evidence supports — measured against schema-only and hash-only baselines in a cryptographic exploitation-evaluation setting, with a genuinely independent reference adjudicator, blind validation, and a held-out set.

That is a *legitimate* contribution **if** it is executed as specified. The blockers are not conceptual, they are evidentiary:
- The project's own record (`HEB1_MULTIAGENT_REAUDIT_20261019.md` §7, and correction C-04 in `HISTORICAL_CORRECTION_LEDGER.md`) states the AI-arm/scripted-arm difference would be "an outcome contrast, not a novelty proof," and that an arm difference alone is not novelty evidence.
- The correction ledger's C-02 records that the shipped fixtures derive private keys from the session identifier, so the fixtures **do not model secret-held issuers**; the current artifacts therefore cannot support any claim about compromise-resistant signing or a production key boundary.
- The prior-art assessment's own falsification conditions (F1–F4) remain open: if V0/V1 produce no false promotions on B1–B4, the mechanism is not exhibited.

**Verdict on C: possible, but it is a category-C contribution that must be earned by an experiment that has not yet been run in its final form, must be positioned against arXiv:2610.16067 / arXiv:2603.14332 as the fair baseline, and cannot currently claim AI-specificity (see §5).**

### Category D — Previously unrecognized causal failure mechanism

**Assessment: NOT SUPPORTED. This claim should be abandoned.**

Reasons, in order of force:

1. **The mechanism is named in a published standard.** RFC 9334 §8.1 (January 2023) states that Evidence "needs to be securely associated with the Target Environment so that the Verifier cannot be tricked into accepting Claims originating from a different environment." That is the cross-boundary promotion mechanism, published.
2. **The mechanism is named again in the adjacent AI-agent literature** as "tool-result misbinding" (arXiv:2610.16333) with a measured rate, and as claim-evidence "unsupported vs. omitted" distinction (arXiv:2606.04990 §3.2).
3. **The mechanism is a known general family** (confused deputy / evidence substitution / confused-deputy on attestation freshness), with a 2013 RFC and a 2026 spec-level treatment (TUF rollback/freeze attacks).
4. **The empirical instance is synthetic and self-generated.** HEB-1's own instances are *injected* cross-boundary mismatches, and the project's own anti-overclaim rule says: "Do not claim a new security mechanism from a certificate schema, hash list, or perfect performance on self-generated fixtures alone." A synthetic injection that demonstrates the *designed* behaviour of a deliberately under-specified baseline is a validation of the design, not a discovery.
5. **The domain transfer is not AI-specific.** Per §5 below, the historical composer was scripted, so the historical evidence establishes a *generic* provenance-composition failure — one that RATS/in-toto/SLSA already anticipate.

**A reviewer will not accept D, and attempting it is the single highest-risk item in the proposal.** A "previously unknown security mechanism" claim that is refuted by RFC 9334 §8.1 is a credibility problem far worse than a modest Category B/C paper.

### Category E — New defense with measurable advantage over a fair, technically appropriate baseline

**Assessment: NOT SUPPORTED by currently available evidence; and the baseline landscape is hostile.**

- **The defense is not new.** A claim-specific join predicate validator is in-toto's artifact-rule engine, SLSA's per-field expectations, and TUF's per-item hashes.
- **Prior art already reports stronger numbers on analogous defenses.** arXiv:2603.14332: "detection of all attack scenarios with **zero false positives**", "<0.02% overhead", verify latency 97 µs (Ed25519/SHA-256) / 13.8 ms (BBS+/Groth16), plus two theorems. arXiv:2610.16067: all injected defect classes detected, "no false positives", with a replay-corrected label change from 94.3% to 65.5% success over 4,320 episodes. A new defense must beat *these*, not a strawman.
- **The proposed baseline ladder is not new.** "Schema-only (V0) vs hash-only (V1) vs claim-bound (V2)" is the standard escalating-assurance ladder already instantiated in llmsa's four-stage pipeline (Signature → Schema → Digest → Chain) and in the arXiv:2603.14332 basic-vs-enhanced crypto instantiation.
- **The project's own artifacts currently under-mine an E claim:** the correction ledger records that the shipped fixtures let the adversary re-derive the private signing keys, so the "signed evidence with explicit issuer identity and role" element was not exercised under a secret-held-key threat model in the historical run. C-03 records a program-to-output-to-trace chain gap in the Stage01 path.
- **There is no live impact evidence.** The ledger's P1 hypothesis is that a faithful *external* submission boundary does not yet exist; the current evidence supports a "local construction/execution boundary," not a deployed exploit or a consequential false attribution in a real evaluation pipeline.

**Verdict on E: cannot be claimed now. It would require a substantially larger and independently reproduced experiment, with the historical scripted fixtures explicitly labelled as non-evidence for the AI arm and with arXiv:2610.16067 / arXiv:2603.14332 used as the fair baseline rather than V0/V1.**

### Summary table

| Category | Verdict | One-line justification |
|---|---|---|
| **A** Known general principle | **SUPPORTED (strongly)** | All six ingredients are native to RATS/in-toto/SLSA/TUF/Sigstore and to ISO/IEC 19795 + ILAC-G8. |
| **B** Known mechanism applied to a new domain | **SUPPORTED (strongly), but the domain is already occupied** | arXiv:2606.04990 surveys it; llmsa implements it; arXiv:2603.14332 theorizes it; arXiv:2605.14153 / arXiv:2506.02548 instantiate it in AI-agent exploitation. |
| **C** New empirical measurement methodology | **POSSIBLE, narrow, and not yet earned** | Method precedents (arXiv:2610.16067, arXiv:2603.14332) are strong; the residual novelty is a metric definition + reproducible benchmark; F1–F4 still open. |
| **D** Previously unrecognized causal failure mechanism | **NOT SUPPORTED — abandon** | RFC 9334 §8.1 names the mechanism; arXiv:2610.16333 measures it in the agent runtime; the instance is synthetic and self-generated. |
| **E** New defense with measurable advantage over a fair baseline | **NOT SUPPORTED by current evidence** | The defense is in-toto/SLSA/TUF; prior art reports zero-false-positive results and a *theorized* chain-verifiability bound; the project's own fixtures do not model secret-held issuers. |

---

## 4. WHAT WOULD HAVE TO BE TRUE (for a D, or an exceptional-E, claim)

Stating the bar honestly is more useful than gesturing at it.

### 4.1 For a Category D claim (previously unrecognized causal failure mechanism)

All of the following would have to hold:

1. **RFC 9334 §8.1 must not actually cover the mechanism.** It does: "the Verifier cannot be tricked into accepting Claims originating from a different environment." **This condition already fails.** A D claim would additionally have to show that the RATS notion (environment substitution) and the ACTS-Attack notion (claim-strength promotion across a run/condition boundary) are *not* the same mechanism — a distinction that is plausible but is a claim about taxonomy, not about discovery, and would not survive a reviewer who reads §8.1.
2. **The failure must be discovered in the wild, not injected.** A mechanism is "previously unrecognized" only if it was observed in a real pipeline, unprompted, with a pre-existing harm. HEB-1's instances are injected by construction, and the project's own proposal forbids the inference.
3. **It must not be a re-domaining of a named agent-runtime phenomenon.** arXiv:2610.16333 already names misbinding/replay in agent runtimes and measures it (FSER 0.649). A D claim would have to show the *evaluation-verdict* variant is a distinct causal mechanism with distinct consequences, and that this distinction is not merely "same pattern, different layer."
4. **It must survive the AI-specificity correction** (§5). Since the historical evidence is scripted, a D claim would have to be made for the generic mechanism — where condition (1) is fatal.
5. **It must have a consequence that the prior-art mitigations demonstrably do not prevent.** Prior art offers specific, named controls (TUF rollback checks, SLSA per-field expectations, in-toto artifact rules, RFC 9334 epoch IDs, arXiv:2603.14332's theorems). A D claim must show those controls are *insufficient* against the discovered instance, in a way that survives contact with their authors.

**Honest verdict: a D claim is not reachable on the current evidence base, and I would advise against pursuing it.** The chance of it surviving review is low, and the downside (an overclaim refuted by a 2023 RFC) is severe.

### 4.2 For an exceptional Category E claim (new defense, measurable advantage over a fair baseline)

1. **A fair baseline** must be arXiv:2610.16067's oracle-integrity audit (five state-integrity invariants + three known-answer controls + 7 injected defect classes) and arXiv:2603.14332's chain-verification (with its theorems), **not** only V0/V1. A reviewer who knows these papers will ask what V2 does that a state-integrity invariant set plus a chain-verification theorem does not.
2. **Adversarial fixtures must be independently generated** after a freeze, with at least one composition pattern not used in development, and the generator must not see defect labels — already required by the project's own §5; this must be *executed*, not specified.
3. **The defense must beat the state of the art on the *same* axis.** The relevant axes are: false-attribution-promotion rate ↓, false rejection on clean controls, and overhead. Prior art already claims 0 false positives and <0.02% overhead. A claim of "measurable advantage" therefore requires a *strictly harder* setting (cross-boundary claim-strength promotion) in which prior-art controls demonstrably fail — and a demonstration that they fail, not merely that V0/V1 fail.
4. **The threat model must be sound.** The correction ledger's C-02 (derivable fixture keys) and C-03 (program→output→trace gap) must be repaired with fresh, externally generated, protected keys and a real program-execution contract, or E cannot be claimed.
5. **There must be a consequential victim.** The ledger's P1 hypothesis (no faithful external submission boundary) means there is currently no deployed consumer whose decision is corrupted. Without a real consumer, "advantage" is a laboratory statistic with no threat model.
6. **The measurement must be reported as FAR/FRR-style paired rates with confidence intervals** (ISO/IEC 19795 / ILAC-G8 convention), not as a point count.

**Honest verdict: an exceptional-E claim is *not* impossible, but it is at least a full frozen-and-held-out experimental cycle away, and it must be benchmarked against arXiv:2610.16067 and arXiv:2603.14332 rather than against a self-constructed baseline ladder.**

### 4.3 The realistic, defensible target

The contribution that survives this review is:

> A **domain instantiation and measurement** of a known evidence-binding pattern (RATS/in-toto/SLSA/TUF/Sigstore) for **cryptographic exploit-evaluation evidence**, whose incremental value is (i) a *defined and validated metric* — false attribution-promotion rate — for a failure mode that the existing standards anticipate but do not quantify in this domain, (ii) an empirical comparison of that metric against **existing** evaluator-integrity controls and existing provenance verifiers, and (iii) a reproducible, independently-generated fixture corpus.

That is a Category B/C paper. It should be introduced with the RFC 9334 / in-toto / SLSA lineage stated in the first paragraph, and it should not use "previously unknown mechanism" language anywhere.

---

## 5. THE HISTORICAL CORRECTION: SCRIPTED COMPOSER, NOT AN AI AGENT

**Correction accepted as stated.** The composer in the historical HEB-1 experiment was scripted, not an AI agent. The project's own audit record is the source: `sp2027/analysis/heb1_remediation_v1/scientific_corrections/HISTORICAL_CORRECTION_LEDGER.md`, correction **C-04**, and `sp2027/analysis/heb1_independent_adversarial_audit_20261019/HEB1_MULTIAGENT_REAUDIT_20261019.md` §7. The correction ledger also records (C-02) that the shipped fixtures derive the private signing key from the session identifier, so the fixture adversary can re-derive it, and (C-03) that the Stage01 path has a program-source → runtime-output → trace chain gap.

### 5.1 What the correction destroys

1. **Any "AI-specific mechanism" claim (D, and the AI-flavoured part of C) loses its empirical basis.** The historical run demonstrates a *generic* provenance-composition failure reproducible with no model in the loop. There is therefore no evidence that AI agents make this failure more likely, more severe, or qualitatively different. Correcting C-04's own logic: an arm difference would have been "an outcome contrast, not a novelty proof"; a *scripted-only* result is a generic result.
2. **The "AI-agent security evaluation" framing of the title is not supported by the project's own artifacts** and must be either (i) supported by a *future, separately approved* AI-arm experiment, or (ii) dropped in favour of the honest generic framing.

### 5.2 What survives — the generic contribution, assessed on its own

The generic contribution, stripped of AI-specificity, is: *"a signed, role-scoped, per-claim-bound evidence chain for a security evaluation, with an independent reference adjudicator, a tri-state verdict that separates missing from contradictory evidence, and a freshness/replay binding to the execution attempt, aggregated into a certificate that cannot overclaim."*

Assessed against the prior art in §1, that generic contribution is:

- **Mechanism:** entirely within the established design space. Every ingredient is native to RFC 9334, in-toto, SLSA, TUF, or Sigstore; the only non-native element is the tri-state verdict over a provenance chain (binary elsewhere) — a small, real, but modest increment.
- **Novelty class:** **A, with a thin B/C veneer.** The honest label is "a well-engineered instantiation of a known pattern in a new domain, with a new measurement."
- **Claim strength that is defensible:** "we instantiate and *quantify* an anticipated cross-boundary promotion failure mode in cryptographic exploit-evaluation evidence chains, and show that a claim-bound validator reduces false attribution promotion relative to schema-only and hash-only baselines." **Not:** "we discovered a previously unknown mechanism," "we identify an AI-specific failure mode," or "we introduce a new security primitive."

### 5.3 The honest self-critique the manuscript should contain

A reviewer who has read RFC 9334 and in-toto will ask: *"why is this not just in-toto with a different schema?"* The only satisfactory answer is empirical: the standards anticipate the failure but **do not quantify it in this domain**, and a domain-specific measurement with a validated metric, a fair baseline drawn from the existing evaluator-integrity literature, and a reproducible independently-generated fixture corpus is a real, if bounded, contribution. That answer requires the frozen held-out experiment to actually be run. It does not currently exist.

---

## 6. INCOMPLETENESS STATEMENT

This review is a **best-effort sweep, not an exhaustive survey**. The following primary sources could **not** be obtained or were not read at the depth claimed by this document's matrix. Every comparison depending on them is correspondingly weaker, and the conclusions above do not rest on them (except where explicitly flagged).

### 6.1 Primary sources not obtained

| Source | Status | What remains unassessed |
|---|---|---|
| **"Grounded but Wrong: Claim–Computation Binding Catches Spoofable Provenance"** (preprints 202610.0322) | **NOT OBTAINED.** The project's own record (`HEB1_PRIOR_ART_ASSESSMENT_20261019.md`) reports preprints.org returned HTTP 403 on two attempts; I did not retry with an alternate host. | Row 25 is entirely `UNVERIFIED`. The project's cited figures (12 safeguards; 28.9% → 2.2% run-level defect rate; Holm-corrected p = 0.0055; ~26% of claims citing a real-but-wrong-variable statistic) are **not confirmed by me**. If that work already implements a blind, claim-specific, pre-registered binding validator with FAR/FRR reporting, the residual Category C space shrinks further. **This is the most consequential single gap in this review.** |
| **ILAC-G8:09/2019** full PDF | Landing/index page read (https://ilac.org/publications-and-resources/ilac-guidance-series); the full document was reached only via a third-party mirror and search snippets. | The exact wording of the "Indeterminate" reporting rules and the false-acceptance/false-rejection framing is quoted from search snippets and secondary summaries, not read in the primary PDF. The (c) assessment for row 12 should be treated as **provisionally** NATIVE. |
| **ISO/IEC 19795-1/-2** (the standard text) | Paywalled. A NIST panel presentation describing the standard (https://www.nist.gov/document/3401mansfieldpanelibpcpdf) and ISO catalogue pages for 19795-10 were seen only at snippet level. | Row 13 is a **terminology** claim only; I did not verify the standard's own definitions or its applicability to non-biometric security evaluators. |
| **EAT / RFC 9335** | Read only through RFC 9334's reference list. | Row 24 is `SECONDARY·snippet`; the specific EAT claim types (software measurements, secure boot, authorizing party) were not read in the primary text. |
| **sigstore-go / cosign** error taxonomy | `pkg/verify/errors.go` read (`ErrVerification` confirmed). The "no signature found" error path and the policy-controller's per-constraint result model were **not** located/verified. | Row 11 (c) is `CUSTOM` on partial evidence. The precise MISSING-vs-CONTRADICTORY contract in the Sigstore toolchain is **unverified**. |
| **slsa-verifier** freshness handling | README grep found no `--max-age`/expiry flag; the source path I guessed (`verifiers/verifier.go`) returned no matches. | Row 7 (d) is `UNVERIFIED`. Whether the shipped tool enforces provenance expiry / max-age **is unknown to me**; SLSA v1.0's predicate definitively has no expiry field (that *was* read). |
| **in-toto** "unfulfilled step" vs "bad link" distinction | I grepped `in_toto/models/layout.py` and `in_toto/runlib.py` for the expected strings and found **no match**; the distinction may live in a module I did not locate, or may be expressed differently. | Row 2 (c) and row 3 (c) may **understate** in-toto: the reference implementation may already implement an explicit missing-vs-bad distinction, which would make in-toto a fully NATIVE row for (c). Treat (c) for in-toto as **lower-bounded**, not final. |
| **RATS "Trust Requirements"** (draft-ietf-rats-trust) and **RATS "Evidence"** (draft-ietf-rats-evidence) | Not fetched. | These drafts plausibly contain **stronger** role-separation and evidence-validity language than RFC 9334 and would only *strengthen* the Category A/B finding against ACTS-Attack. Fetching them was not necessary to reach the verdict, which is why the omission is noted rather than corrected. |

### 6.2 Sources read only at abstract level

Rows 14–21 (CyberGym, ExploitBench, ReproBench, ExploitGym, CryptanalysisBench, Governing Dynamic Capabilities, When Agent Evaluation Becomes Unreliable, TRAP/ReplayBench) were assessed from **official arXiv abstracts plus, in three cases, the arXiv API record** (used to confirm the identifiers 2603.14332, 2605.11086, 2605.14153, 2607.18538, 2609.34450 all resolve to the titles the project matrix attributes to them). Their full texts, appendices, and artifacts were not read. Mechanistic sub-claims — in particular ExploitBench's per-run challenge-response construction, arXiv:2603.14332's theorem statements as formalized, and arXiv:2610.16067's eight artifact gates and 54/57 detection count (the latter figure comes from the *project's* notes, not from the paper) — are therefore **abstract-level claims**.

### 6.3 Search coverage

- The sweep was English-language and web-indexed. Non-indexed venues (W3C, ISO/IEC paywalled texts, ITET, USENIX proceedings not linked from search results) may contain closer prior art.
- The 2026 literature is moving fast; works from 2026-10-14 to 2026-10-20 were not systematically swept.
- The project's own `contract_sound_prior_art_matrix_v1.md` was used as a *secondary* pointer for arXiv:2605.11086 / 2605.14153 / 2607.18538 / 2609.34450 / 2610.16067 / 2610.16333 / 2603.14332 and the ePrint/preprints items; the arXiv identifiers were independently confirmed to resolve, but the *characterizations* in the project matrix (e.g. the "five state-integrity invariants", "21 variants × 3 targets", "54/57", "FSER 0.649", "8 checks / 4 load-bearing") were **not** independently re-derived from the papers' full text, with the partial exception of the arXiv:2610.16067 abstract, which does state "five state-integrity invariants and three known-answer controls", "seven oracle defect classes", "All injected defect classes are detected, and the repaired oracle has no false positives", and the 4,320-episode / 4,194→2,883 / 94.3%→65.5% figures.
- The in-repo `HEB1_PRIOR_ART_ASSESSMENT_20261019.md` and `PRIOR_ART_NOTES_20261019.md` were read and are consistent with this review's direction, but this review reaches them independently and, on the "AI-specific" question, more negatively.

### 6.4 What would most change this assessment

1. Obtaining **"Grounded but Wrong"** (preprints 202610.0322) in full. If it already implements a blind claim-specific binding validator with pre-registered ablation and FAR/FRR reporting, then even the residual Category C space is largely closed, and the correct verdict becomes a flat **A/B** with no viable C.
2. Obtaining **RATS Trust Requirements** and **RATS Evidence** drafts. Likely to strengthen the finding against D and E only.
3. A dedicated search of **USENIX Security / IEEE S&P / CCS 2023–2026** proceedings for "attestation" + "evaluation" + "provenance" that the web sweep may have under-indexed.

---

## 7. BOTTOM LINE

**Category verdict (honest best assessment):**

- **A — Known general principle: YES, strongly.** The mechanism is an assembly of RFC 9334 / in-toto / SLSA / TUF / Sigstore primitives, plus a tri-state verdict lifted from ISO/IEC 19795 + ILAC-G8. Nothing in it is unrecognized.
- **B — Known mechanism in a new domain: YES, strongly — and the domain is already occupied** by arXiv:2606.04990 (survey), llmsa (implementation), arXiv:2603.14332 (governance-layer implementation + theorems), arXiv:2605.14153 and arXiv:2506.02548 (AI-agent exploitation verifiers with independent differential oracles).
- **C — New empirical measurement methodology: only weakly and narrowly** — plausibly a validated "false attribution-promotion rate" metric plus a reproducible benchmark, benchmarked against arXiv:2610.16067 and arXiv:2603.14332 rather than against V0/V1. **Not yet earned**; the F1–F4 falsification conditions remain open, and the historical fixtures do not model secret-held issuers.
- **D — Previously unrecognized causal failure mechanism: NO.** Abandon this claim. RFC 9334 §8.1 names the mechanism; arXiv:2610.16333 measures the adjacent instance; the historical instance is synthetic and the composer was scripted.
- **E — New defense with measurable advantage: NO on current evidence.** The defense is in-toto/SLSA/TUF; prior art reports zero false positives and a *theorized* chain-verifiability bound; the project's own artifacts do not currently support a signed-issuer threat model or a program→output→trace chain.

**Single most damaging prior-art hit:** **RFC 9334 (IETF Informational, January 2023), §8.1** — "Evidence needs to be securely associated with the Target Environment so that the Verifier cannot be tricked into accepting Claims originating from a different environment" — read together with §3.1/§12.1.1 (attester independent of the measured target), §10/§12.2/§12.3 (epoch IDs, mandatory replay-attack prevention, and the named "confusion attack"), §4.1/§7 (seven roles with separate trust anchors and separate appraisal policies) and §8.4/§8.5 (signed attestation result; per-constraint appraisal). **A single published architecture that simultaneously (i) specifies the trusted-observer separation, (ii) specifies the per-claim join predicates, (iii) specifies the freshness epoch and replay prevention, (iv) specifies the role authorization, (v) specifies the fail-closed final aggregator, and (vi) names the cross-boundary promotion failure mode the proposal presents as a discovery.** URL: https://www.rfc-editor.org/rfc/rfc9334.html

**Runner-up (which closes the "but it is AI-specific" escape hatch):** **arXiv:2606.04990v4, "From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents"** (https://arxiv.org/html/2606.04990v4), together with the working implementation at **https://github.com/ogulcanaydogan/LLM-Supply-Chain-Attestation** — the AI-agent application of this union is already surveyed, already specified, and already built, including the MISSING-vs-CONTRADICTORY verdict distinction and the binding of evaluation claims to the exact evaluated artifacts.

**Consequence for the project:** reframe from "new security mechanism" to "domain instantiation with a new measurement." State the RATS/in-toto/SLSA/TUF/Sigstore lineage in the first paragraph, use RFC 9334 §8.1 as the motivating citation rather than as a rival, and make the paper's claim the *metric* and the *reproducible corpus* — the only things in the current proposal that are not already owned.
