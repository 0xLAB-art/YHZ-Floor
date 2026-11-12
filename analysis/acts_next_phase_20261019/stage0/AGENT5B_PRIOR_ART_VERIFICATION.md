# AGENT5B — Independent Verification of Agent 5's Prior-Art Claims

**Date:** 2026-10-20
**Role:** Independent verifier (subagent spawned by the orchestrating session). Research-only, read-only.
**Inputs:** The 10 claims enumerated in the tasking. Agent 5's own matrix (`AGENT5_PRIOR_ART_NOVELTY_MATRIX.md`) was read for context, but **every** verdict below is re-derived from primary sources fetched in this session.

## 0. Method and honesty statement

- All fetches were performed with `curl` (HTTP status recorded per URL) into `/tmp/opencode/pa/`. PDFs were converted with `pdftotext -layout`; HTML was stripped to text with a Python one-liner. Nothing outside `/tmp/opencode/` and this report file was written.
- **Every URL cited below was actually fetched in this session** and returned content (HTTP 200) unless the text explicitly says "403" or "404". Where a URL returned 403/404, that is stated.
- Verdict vocabulary used throughout:
  - **VERIFIED** — the quoted text exists in the fetched primary source at the cited location and supports the claim as stated.
  - **VERIFIED (REFINED)** — the substance holds but the claim's wording overstates or mischaracterises the source; the correction is given.
  - **PARTIALLY VERIFIED** — some sub-parts of the claim verified, others not.
  - **REFUTED** — the primary source contradicts the claim.
  - **NOT-OBTAINABLE** — the full text could not be retrieved by any route tried; only secondary/official-abstract-level records obtained.
- No arXiv ID, title, author, repository URL, or numeric result in this report is reproduced from memory. Every one was read from a fetched primary source.
- A deliberate note on **arXiv ID plausibility**: the tasking warned that `26xx`/`25xx` prefixes may be from a future-dated corpus. As of this session's date (2026-10-20) all five arXiv IDs under test (`2606.04990`, `2603.14332`, `2605.14153`, `2610.16067`, `2506.02548`) resolved with HTTP 200 to genuine, content-bearing arXiv abs pages and PDFs, with internally consistent arXiv watermark strings (e.g. `arXiv:2606.04990v6 [cs.CR] 15 Oct 2026`, `arXiv:2610.16067v1 [cs.SE] 12 Oct 2026`). **No fabricated-ID finding arises.** The one ID that does *not* resolve is `202610.0322` on arXiv — but that is a *preprints.org* manuscript number, not an arXiv ID (see Claim 6).

---

## 1. CLAIM 1 — arXiv:2606.04990 "survey of AI-agent attestation / evaluation attestation"

### Verdict: **VERIFIED (existence, title, authors, date)** + **REFINED** (characterisation)

### 1.1 Existence and bibliographic record — VERIFIED

Fetched: `https://arxiv.org/abs/2606.04990` → **HTTP 200**, 45,681 bytes.
Fetched: `https://arxiv.org/pdf/2606.04990` → **HTTP 200**, 1,661,856 bytes, `application/pdf`.

Extracted `citation_*` metadata from the abs page:

```
citation_title  = From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents
citation_author = Wang, Yiqi
citation_date   = 2026/06/03
citation_arxiv_id = 2606.04990
```

PDF header (from `pdftotext` output, lines 1–19 of `txt_2606.04990.txt`):

```
1:                                          From Agent Traces to Trust: A Survey of Evidence Tracing
2:                                          and Execution Provenance in LLM Agents
3:                                          Yiqi Wang1,∗ , Jiaqi Zhang2 , Zhangkai Wu3 , Taotao Cai1,∗ , Zirui Liu4 , Zequn Sun5 , Mingkai
4:                                          Zheng6 , Manqing Dong7 , Yu-Xuan Qiu8 , Xuefei Yin9 , Yanming Zhu9
...
19:  arXiv:2606.04990v6 [cs.CR] 15 Oct 2026
```

Dateline from the abs page: `[Submitted on 3 Jun 2026 (v1), last revised 15 Oct 2026 (this version, v6)]`.

**Caveat on Agent 5's citation:** Agent 5 cited `arXiv:2606.04990v4`. The current version is **v6** (15 Oct 2026). v4 also resolves (HTTP 200), so Agent 5's citation was accurate as of its reading, but a reviewer re-checking today will see v6. The substantive §3.2 and §7.6 text quoted below is present in v6.

**Caveat on author list:** `citation_author` on the abs page lists only the *first* author (standard arXiv behaviour for large author lists). The PDF lists **11 authors across 9 affiliations** (University of Southern Queensland, Jiangsu University, University of Sydney, Peking University, Nanjing University, SUSTech, UNSW, BIT Zhuhai, Griffith). Agent 5's implicit "Wang, Yiqi" attribution is correct but incomplete.

### 1.2 Is it a "survey of AI-agent attestation / evaluation attestation"? — **REFINED**

**It is a survey of evidence tracing and execution provenance for LLM agents.** Attestation is a *surveyed open gap* (§7.6), not the survey's subject matter. Direct quote, `txt_2606.04990.txt` lines 45–46 (abstract):

```
45:                                                            catalog that evaluates the complete provenance chain, and little reporting of tamper-evident
46:                                                            or attested traces. These findings highlight why final-answer correctness alone is insufficient
```

And §7.6, lines 1921–1926:

```
1921: 7.6   Trace Assurance and Attested Provenance
1922:
1923: A dimension that current work leaves almost entirely open is assurance: whether a trace can be trusted by
1924: a party other than the one that produced it. Section 2.1 introduces assurance as a cross-cutting attribute,
1925: and the reviewed descriptions of the systems in Table 3 do not establish tamper-evident or attested trace
1926: guarantees. As described, they write traces to a log that could be edited, truncated, or reordered after the
1927: fact by whoever operates the agent. This is adequate for debugging, where the reader and the producer
1928: are the same party, and inadequate for audit, where they are not.
```

**This is a material correction to Agent 5's row 22, and it cuts *against* the "domain already occupied" argument.** The survey's headline finding is that **no surveyed system provides attestation and no surveyed benchmark evaluates the complete provenance chain**:

```
2660:Table 3, none reports tamper-evidence, signing, or attestation for its traces, so provenance is trustworthy only
```

(lines 665–671 and 1963–1964 carry the same statement.)

### 1.3 Does it cover "source -> execution -> runtime output -> reference verification -> evidence -> final claim"? — **PARTIALLY VERIFIED / REFUTED as stated**

The survey's running example (Figure 3) has **four** panels, and there is **no "reference verification" stage**. `txt_2606.04990.txt` line 889 and line 914 give the two panel-header rows, and lines 943–945 the caption:

```
889:          1 Evidence Acquisition                                                                         2 Claim Construction
914:           3   Tool Execution Lineage                                                                    4 Conflict, Update & Recovery
943: Figure 3: Running example of a provenance graph for an LLM-agent execution, linking user queries, retrieved
945: typed relations. For legibility, the panels show seven of the nine relations and omit Use and Depend-on;
```

and the legend (lines 935–941):

```
935:                          SUPPORT:                 DERIVE:              GENERATE:             CONTRADICT:               INVALIDATE:                     UPDATE:                 TRIGGER:
936:         Legend             Evidence               New Item              An Execution             Evidence
937:                           Supports a             Derived From           Step Produces         Conflicts with a
938:                          Claim or Step           Prior Item(s)           An Artifact           Memory Item
```

The abstract states the relation count explicitly (lines 40–41):

```
40:                                                            and trust functions. We complement this taxonomy with operational definitions of nine
41:                                                            provenance relations and two cross-cutting attributes: prove
```

so there are **nine** relations: the six in the figure legend plus **Use** and **Depend-on** (omitted from the figure for legibility — line 945: *"the panels show seven of the nine relations and omit Use and Depend-on"*).

**Assessment:** the survey covers `source/retrieval -> intermediate claim -> tool execution (args, output) -> final answer/action -> conflict/update/recovery`. It does **not** cover a *reference-verifier* stage, does **not** cover cryptographic evidence records, does **not** cover signed evidence, and does **not** cover a final *attested certificate*. The chain the tasking describes is a **cryptographic** chain; this survey's chain is a **semantic provenance graph**. Substituting one for the other in a novelty argument is a category error.

### 1.4 Does it discuss "an evaluator under-binding evidence to produce unsupported full-attribution claims"? — **NOT AS STATED (closest analogue found)**

**Negative result, decisively:** `grep -n -i "under-bind|underbound|evaluator|under-?specif"` over the full 3,345-line text returns **zero matches**. The words "evaluator" and "under-bind" do not appear anywhere in the paper. The claim's phrasing is therefore **not** a quotation of this survey and **not** a topic it names.

**Closest two passages, both real and both quoted:**

*(i) §3.2* — lines 877–886:

```
877: 3.2   Evidence and Claim-Support Attribution
878:
879: Evidence attribution adds a semantic layer on top of execution dependencies. The key issue is whether
880: a generated claim is actually supported by the evidence it cites or depends on. Existing work motivates
881: this distinction at different granularities: citation-based evaluation links generated answers to sources (Gao
882: et al., 2023); atomic-fact evaluation checks fine-grained factual support (Min et al., 2023); source-checking
883: work shows that a cited source may be relevant without supporting the specific claim (Wu et al., 2025);
884: and claim–evidence mapping explicitly distinguishes supported claims, unsupported claims, and omitted
885: evidence (Martin-Boyle et al., 2026).
```

**Critical caveat that Agent 5 did not record:** the phrase Agent 5 quoted — *"claim–evidence mapping explicitly distinguishes supported claims, unsupported claims, and omitted evidence"* — is the survey **describing other people's work** (attributed to *Martin-Boyle et al., 2026*). It is **not** the survey's own taxonomy and **not** the survey's own proposal. Citing it as the survey "natively" providing a three-way claim-level split is an overstatement.

The survey's own derived predicates are `Cited` and `Omitted` (lines 949–957, and Appendix B.5 at lines 2666–2687). And they are explicitly **predicates, not taxonomy relations**:

```
950: For provenance representation, these correspond to distinct relationships rather than a single citation relation.
951: A source may be Cited, asserted by the agent as supporting, without being Supported, that is, without an
952: adjudicated support link; a relevant passage may be available but Omitted from the answer; a tool output
953: may Contradict a memory item; and new evidence may Invalidate an earlier belief. Cited and Omitted
954: are not additional taxonomy relations: they are predicates derived from the nine, and Appendix B.5 defines
955: them in those terms. Evidence graphs therefore distinguish evidence availability from evidence use.
```

*(ii) §7.6* — the closest thing in the entire paper to ACTS-Attack's "under-bound evaluator promotes evidence into an unsupported stronger claim", lines 1936–1940:

```
1936: how should assurance interact with origin? An attested trace can show that recorded procedural edges were
1937: not altered after the fact, but does not establish whether an inferred Support edge is correct. Assurance
1938: and semantic correctness are independent axes: an attested trace can still contain an incorrect inferred edge,
1939: so attestation should not be read as evidence of correctness.
```

**Assessment:** this is a genuine and *directly relevant* conceptual precursor — "attestation ⇒ correctness" is a non-implication the survey states explicitly. But it is stated as a **design caution for a not-yet-existing** assurance tier, not as a discovered failure mode, and it does not use the words evaluator/under-binding/attribution.

### 1.5 Bonus: the survey's own metric maturity table (relevant to Agent 5 row 22(c))

`txt_2606.04990.txt` lines 1580–1596 (Table 7 caption and rows) and 1620–1624 (research agenda):

```
1580: Table 7: Representative metric dimensions for evaluating evidence tracing and execution provenance in
1581: LLM agents. The Status column flags maturity: Established metrics are operationalized in existing RAG,
...
1583: localization in TRAIL/MAST) but not for recovery; Proposed metrics (trace completeness, provenance
1584: accuracy, dependency coverage, temporal consistency) are desiderata that are not yet operationalized with
1585: agreed definitions. ✓: Established; •: Partly established; ★: Proposed.
1586:  Evaluation As- Core Question               Representative Metrics            Status   Related Basis
1588:  Evidence attri- Are the agent's claims Evidence recall, citation pre-         ✓      RAG and attribution evalua-
1589:  bution          supported by reliable ev- cision, source supportiveness,              tion (Gao et al., 2023; Min et al.,
1590:                  idence?                   faithfulness, claim support ac-         2023; Niu et al., 2024; Ru et al.,
1591:                                            curacy.                                     2024; Wu et al., 2025).
1592:  Execution prove- Is the agent's execution Trace completeness, prove-           ★      Provenance standards and
1593:  nance            process completely and nance accuracy, dependency                    agent observability (World
1594:                   correctly traceable?     coverage, temporal consistency.             Wide Web Consortium, 2013;
```

```
1620: Research agenda for provenance metrics. The execution-provenance row of Table 7 is the only row
1621: marked ★: trace completeness, provenance accuracy, dependency coverage, and temporal consistency are not
1622: yet available as measures. None has an agreed definition in the work we surveyed, none has an established
1623: ground-truth construction there, and they are not offered as an evaluation framework ready for adoption. We
1624: describe each with the ground truth it would require, so that the gap can be acted on.
```

Agent 5's "Proposed maturity" reading is **VERIFIED**.

### 1.6 Claim-1 bottom line

| Sub-claim | Verdict |
|---|---|
| ID resolves, is a survey | **VERIFIED** |
| Title / authors / date | **VERIFIED** (11 authors; v6, 15 Oct 2026) |
| "Survey of AI-agent attestation" | **REFINED** — attestation is a surveyed *open gap* (§7.6), not the subject |
| Chain "source→execution→runtime output→reference verification→evidence→final claim" | **REFUTED as stated** — no reference-verification stage, no cryptographic evidence stage; chain is semantic |
| Discusses "evaluator under-binding evidence → unsupported full-attribution claim" | **NOT AS STATED** — "evaluator"/"under-bind" appear 0 times; closest = §7.6 "attestation should not be read as evidence of correctness" and §3.2's *description of third-party work* |
| §3.2 "supported/unsupported/omitted" | **VERIFIED as a quotation, but mis-attributed** — it is the survey reporting *Martin-Boyle et al. (2026)*, not the survey's own taxonomy |

---

## 2. CLAIM 2 — `llmsa` as a working open-source LLM-evaluation attestation chain

### Verdict: **VERIFIED — in fact STRONGER than Agent 5 claimed, because the exit-code semantics are in the source code, not only the README**

### 2.1 The repository exists and is real

GitHub REST API `https://api.github.com/repos/ogulcanaydogan/LLM-Supply-Chain-Attestation` → **HTTP 200**:

```
full_name=ogulcanaydogan/LLM-Supply-Chain-Attestation
stars=2  created=2026-02-13T10:33:32Z  pushed=2026-09-15T04:10:47Z
default_branch=main  license=Apache-2.0
desc=Cryptographic attestation framework for LLM supply-chain security, tamper-evident provenance for
prompts, training data, evaluations, routing, and SLOs with Sigstore keyless signing, OCI distribution, and OPA policy enforcement
```

README fetched from `https://raw.githubusercontent.com/ogulcanaydogan/LLM-Supply-Chain-Attestation/main/README.md` → **HTTP 200**, 480 lines. Line 1:

```
1: # LLM Supply-Chain Attestation (`llmsa`)
```

**Discovery note.** GitHub repo-name search for the bare token `llmsa` (133 hits) returns only unrelated projects (`LLMSanitize`, `LLMSAN`, `llmsandbox`, …). The project is found only by searching for its *description* (`"llm attestation"` → 111 hits, first hit = `ogulcanaydogan/LLM-Supply-Chain-Attestation`). **The CLI/binary is named `llmsa`; the repository is named `LLM-Supply-Chain-Attestation`.** Anyone repeating this search must use the latter or they will wrongly conclude the project does not exist.

### 2.2 Exit codes 10 = missing, 11/12 = contradictory — **VERIFIED IN SOURCE CODE**

This is the decisive strengthening. `internal/verify/result.go`, fetched from `https://raw.githubusercontent.com/ogulcanaydogan/LLM-Supply-Chain-Attestation/main/internal/verify/result.go` → **HTTP 200**, 1,801 bytes:

```
 1: package verify
 2:
 3: const (
 4: 	ExitPass           = 0
 5: 	ExitMissing        = 10
 6: 	ExitSignatureFail  = 11
 7: 	ExitDigestMismatch = 12
 8: 	ExitPolicyFail     = 13
 9: 	ExitSchemaFail     = 14
10: )
```

And the design rationale, `docs/adr/0007-semantic-exit-codes.md` → **HTTP 200**, 2,308 bytes:

```
13: The `llmsa verify` and `llmsa gate` commands need to communicate verification results to CI/CD pipelines and shell scripts. A simple pass/fail (0/1) exit code loses information about what went wrong. We needed a structured exit code scheme that enables automated response logic.
...
28: Exit codes escalate — if multiple failure types occur, the highest-severity code is returned. The priority order is: tamper (12) > signature (11) > schema (14) > policy (13) > missing (10).
...
32: - **Distinct codes for distinct failures**: A CI pipeline that receives exit code 12 (tamper) should trigger a security incident investigation, while exit code 10 (missing) might just need a pipeline reconfiguration. Collapsing these into a single non-zero code loses this distinction.
```

**This is a MISSING-vs-CONTRADICTORY separation, in code, with an explicit written rationale for *why* the separation matters.** It is the closest existing realisation of ACTS-Attack's ingredient (c) that this verification found.

### 2.3 Typed dependency joins and temporal ordering — **VERIFIED IN SOURCE CODE**

`internal/verify/chain_verify.go` → **HTTP 200**, 5,320 bytes. Violation strings and the `requiredChainDeps` type map:

```
18: var requiredChainDeps = map[string][]string{
...
86: 					edge.Detail = "missing_required_attestation_type"
88: 					violations[fmt.Sprintf("missing chain predecessor: %s requires %s", st.AttestationType, reqType)] = struct{}{}
...
109: 					edge.Detail = "missing_dependency_reference"
111: 					violations[fmt.Sprintf("missing dependency reference: %s should reference %s", st.StatementID, reqType)] = struct{}{}
...
120: 				if !ordered(target.GeneratedAt, st.GeneratedAt) {
122: 					edge.Detail = "predecessor_generated_after_successor"
124: 					violations[fmt.Sprintf("invalid chain order: predecessor %s generated after %s", target.StatementID, st.StatementID)] = struct{}{}
...
167: 			violations[fmt.Sprintf("unknown dependency reference: %s -> %s", st.StatementID, dep)] = struct{}{}
```

Note that `chain_verify.go` reports violations as **strings** in a `Violations []string` list, and `ChainReport.Valid` is a **single boolean** (`result.go` line 45: `Valid bool`). So the chain layer is fail-closed but not tri-state at the *chain* level; the tri-state is at the *verification-stage* level (exit 10 vs 11 vs 12 vs 14).

README corroboration (lines 59–83):

```
59: ### 2. Provenance Chain Verification
61: `llmsa` enforces a **directed acyclic dependency graph** between attestation types, ensuring logical ordering and referential integrity:
77: The chain verifier validates:
78: - **Type-based dependencies**: An eval attestation *must* reference both prompt and corpus attestations.
79: - **ID-based references**: Explicit `depends_on` annotations link specific statement IDs across the graph.
80: - **Temporal ordering**: Predecessor attestations must have been generated *before* their successors.
81: - **Unknown reference detection**: Dangling dependency references are flagged as violations.
83: This ensures that no attestation can exist in isolation — every claim about model quality (eval) is bound to the exact artifacts (prompt + corpus) it was tested against, and every deployment decision (route, SLO) traces back to verified evaluations.
```

**Line 83 is the single most damaging sentence for ACTS-Attack's novelty.** It states the eval-artifact-to-claim binding requirement in almost exactly ACTS-Attack's terms.

### 2.4 Sigstore keyless role binding — **VERIFIED (README)**

README lines 128–135:

```
128: ### 5. Sigstore Keyless Signing with OIDC Identity Binding
130: Production signing uses [Sigstore](https://www.sigstore.dev/) keyless mode with OIDC tokens from CI providers (GitHub Actions, GitLab CI). This means:
132: - **No key management**: No private keys to rotate, store, or protect.
133: - **Identity-bound signatures**: Attestations are cryptographically tied to the CI workflow identity that produced them (e.g., `github.com/org/repo/.github/workflows/attest.yml@refs/heads/main`).
134: - **OIDC issuer verification**: The verifier checks that the token issuer matches the expected provider.
135: - **PEM fallback**: Ed25519 key signing for local development and air-gapped environments.
```

### 2.5 Fail-closed admission — **VERIFIED (README)**

README lines 50–51 and 145–147:

```
50: 3. **Policy enforcement** in CI for deny-on-missing-or-invalid evidence.
51: 4. **Fail-closed admission enforcement** in Kubernetes for deployment-time verification.
...
145: ### 7. Kubernetes Admission Enforcement
147: The `llmsa webhook serve` command runs a **validating admission webhook** that intercepts Pod, Deployment, ReplicaSet, StatefulSet, DaemonSet, and Job creation, pulling attestation bundles from OCI registries and running the full four-stage verification pipeline before allowing resources into the cluster.
```

### 2.6 Caveats — material, and they weaken the "prior art blocks novelty" reading

1. **Adoption scale is near-zero.** 2 stars, created 2026-02-13, no citations, no arXiv/venue record found. This is an *unpublished personal project*. Under most novelty rubrics, a 2-star hobby repo is weak prior art — a reviewer can fairly say it does not anticipate the field. This is a genuine weakness in Agent 5's row 23.
2. **No transparency log / replay ledger shipped.** Agent 5's own row 23 said Rekor is "on the roadmap, not shipped". Confirmed: the README's Rekor mention is only in a "Technology Stack" comparison; the four-stage pipeline is Signature → Schema → Digest → Chain, with no transparency-log inclusion proof. Freshness is only *temporal ordering* within the DAG, not an epoch/replay ledger.
3. **"Role binding" is CI-workflow-identity binding, not per-claim role authorization.** Sigstore keyless binds the *signer identity*; there is no policy in the repo keyed to "which issuer role may attest which kind of claim" (the inverse of RFC 9334's `Appraisal Policy for Evidence`).
4. **The tri-state is at the stage level, not the claim level.** Exit 10 = "Missing attestation or bundle" (i.e. an *artifact* is absent), not "the evidence for *this claim* is missing". Exit 11/12 = the artifact is present but contradicts. This is stage-level MISSING-vs-CONTRADICTORY, not per-claim adjudication.
5. **`ChainReport.Valid` is a single boolean** (result.go:45) — no INCONCLUSIVE state in the chain report.

### 2.7 Closest real analogues I DID find (as the tasking requested)

Primary: sigstore (Fulcio/Rekor), in-toto, SLSA, TUF, Rekor — all verified in this session (Claims 7–9). Also found and confirmed via the GitHub API (HTTP 200 on each):

| Project | Stars | Created | Relevance |
|---|---|---|---|
| `Aqta-ai/attestation-spec` | 8 | 2026-04-24 | "Open specification and reference verifiers for Seal records: **ATTESTATION-v1 for AI model-call decisions, ACTION-v1 for agent actions**. Ed25519, canonical JSON, checked offline against a published key." |
| `bkuan001/halo-record` | 84 | 2026-06-11 | "Tamper-evident audit trails for AI agents: hash-chained Runtime Records, dependency-free, verifiable by anyone." |
| `kenhuangus/stss` | 7 | 2026-03-09 | "Skill Trust & Signing Service — security layer for AI agent skill ecosystems with cryptographic attestation..." |
| `Brain0-ai/brain0` | 324 | — | "signed provenance attestations" for AI-written code |
| `Bhogan650/autofix` | 1 | — | "ship with a signed attestation that proves exactly what your tool does" |

**No project named `llmsa`/`llmsig`/`llm-signer` exists as an LLM *evaluation* attestation framework** — the `llm-signer` search (8 hits) returns unrelated tooling; `llmsig` (2 hits) returns `LLMSignalProcess` and `LLMSign` (unrelated). The "model card signing" / "eval provenance" niche is served by the general Sigstore/in-toto/SLSA tooling plus the small projects above.

---

## 3. CLAIM 3 — arXiv:2603.14332 "agent governance layer" with two theorems

### Verdict: **VERIFIED (existence, title, author, date, two theorems)** + **REFINED** (theorems are not about evaluation-attribution / claim binding)

### 3.1 Bibliographic record — VERIFIED

`https://arxiv.org/abs/2603.14332` → **HTTP 200**, 42,705 bytes.

```
citation_title  = Governing Dynamic Capabilities: Cryptographic Binding and Reproducibility Verification for AI Agent Tool Use
citation_author = Zhou, Ziling
citation_date   = 2026/03/15
citation_arxiv_id = 2603.14332
```

Dateline: `[Submitted on 15 Mar 2026 (v1), last revised 19 Mar 2026 (this version, v2)]`.
PDF watermark (from `txt_2603.14332.txt`): the paper is 1,643 extracted lines; §4 is the theorem section.

### 3.2 The two theorems — VERIFIED verbatim

**Theorem 1 (Bounded Divergence)**, `txt_2603.14332.txt` lines 508–524:

```
508: Theorem 1 (Bounded Divergence). If adversary-
509: controlled model M ′ passes replay verification (CharMatch
510: ≥ θ) on n independent prompts drawn from D across |S|
511: skills, then M and M ′ are (n, ϵ)-indistinguishable with:
512:
513:                            ϵ ≤ 1 − α1/n
```

**Theorem 2 (Chain Verifiability)**, lines 624–632:

```
624: Theorem 2 (Chain Verifiability). Let v0 → v1 → · · · → chain verifiability breaks at node v , the ledger records
625:                                     k
626: vn be an execution chain where v0 is a non-agent trust an- a PARTIAL_VERIFIABILITY marker; downstream agents
627: chor. If CVD(vn ) = k < n, then for all i > k, the output inherit a trust tier penalty, making the reduced guarantee
628: of vi cannot be verified as originating from a legitimate visible to auditors.
629: computation chain rooted at v0 , even if vi individually
630: satisfies ρvi .level = full.
```

Formal versions **Theorem 3 (Bounded Divergence Under Verification)** and **Theorem 4 (Chain Verifiability)** appear in the appendix (lines 1547, 1592), with proof sketches at lines 1592–1640.

### 3.3 The critical characterisation caveat — **REFINED**

The tasking's claim was that the paper "contains theorems about **evaluation-attribution / claim binding**". Read against the full text, the two theorems are about something different:

- **Theorem 1** is a *statistical indistinguishability* bound on **replay-based verification of a model's outputs** (G2 behavioural verifiability). It bounds the probability that an adversary-controlled model M′ is mistaken for M, given n independent prompts and significance level α. It is a *reproducibility/determinism* result.
- **Theorem 2** is about **chain verifiability of a multi-agent execution chain**: if an interior node vk cannot be verified, then no downstream output "can be verified as originating from a legitimate computation chain rooted at v0". The ledger records a `PARTIAL_VERIFIABILITY` marker and downstream agents inherit a trust-tier penalty.

**Theorem 2 is nevertheless a genuine conceptual neighbour of ACTS-Attack's mechanism** — "an output that cannot be shown to originate from the legitimate computation chain must not be treated as if it did" is the same *shape* as "a verdict not bound to the run must not be promoted to a run-level attribution claim". But it is stated over **model execution reproducibility**, not over **evaluation-evidence attribution**. The paper's own domain is *agent tool use*, and its three governance requirements are (lines 126–130 of the abstract block):

```
G1 capability integrity, G2 behavioral verifiability, G3 interaction auditability
```

**Assessment:** the claim "is an agent-governance-layer paper with two theorems" is **VERIFIED**; the gloss "theorems about evaluation-attribution / claim binding" is **NOT VERIFIED** and should be softened to "theorems about replay-based behavioural verifiability and chain verifiability of agent execution — adjacent to, but not the same as, evaluation-evidence attribution."

**Also worth recording (relevant to Agent 5's §8.2 "A Theorem is a harder-to-beat baseline" claim):** the paper's own §8.2 (line 1162) introduces the **Agent Governance Trilemma** (Observation 1) and, at lines 1291–1298, states that "a rigorous formalization … would establish the trilemma as a foundational constraint" and that the relationship "between … monitoring … and attack detection" is **conjectural**. So the paper's own authors treat part of the formalisation as open. This is a *caveat against* Agent 5's rhetorical use of the theorem as an unbeatable baseline.

---

## 4. CLAIM 4 — arXiv:2605.14153 and arXiv:2506.02548 as exploit verifiers with independent differential oracles

### Verdict: **VERIFIED (both papers exist, both use differential oracles)** + **REFINED** ("independent" is too strong)

### 4.1 arXiv:2605.14153 — ExploitBench — VERIFIED

`https://arxiv.org/abs/2605.14153` → **HTTP 200**; `https://arxiv.org/pdf/2605.14153` → **HTTP 200**, 1,222,303 bytes.

```
citation_title  = ExploitBench: A Capability Ladder Benchmark for LLM Cybersecurity Agents
citation_author = Lee, Seunghyun
citation_date   = 2026/05/13
```

Abstract, `txt_2605.14153.txt` lines 28–29:

```
28:                                           flow hijack, and arbitrary code execution. Each capability is verified by a deterministic oracle that
29:                                           uses a per-run randomized challenge-response for primitives, differential execution against ground-
```

Body, lines 109–114:

```
109: A key contribution is a progressive capability model that decomposes exploitation into 16 independent, measurable
110: flags: code coverage, bug detection, engine-specific exploit primitives, general-purpose primitives, and full exploita-
111: tion. Each flag is verified by a deterministic oracle that requires no human judgment: challenge-response builtins for
112: exploit primitives, differential execution against ground-truth binaries for bug detection, and in-engine signal-handler
113: and prctl oracles for control-flow hijack and arbitrary code execution. The oracles are designed to resist reward
114: hacking, where LLMs succeed at the wrong task (see § 2).
```

**The decisive anti-self-reporting quote** (lines 284–288):

```
284:         Graded. By differential execution: the submission runs against both vuln and fixed builds and the results are
285:         compared. diff requires the vuln build to exit with a different signal than the fixed build on the same input;
286:         asan requires an AddressSanitizer report on the vuln build; crash is the stricter variant requiring SIGSEGV
287:         or SIGBUS on vuln and a clean exit on fixed. These checks depend on the behavior of the ground-truth
288:         binary, not on anything the agent reports.
```

**Freshness / anti-replay detail** (lines 251–253):

```
251: Repeated grade calls could in principle leak information. We address this in the oracle design rather than with rate
252: limits. Each oracle returns a bitmap only with no diagnostic information, challenge-response builtins reseed on every
253: call, and each grade runs in a fresh per-call working directory that is destroyed on return.
```

**Caveat on "per-run":** the abstract says "per-run randomized challenge-response"; the body says the builtins "reseed on **every call**". Both are consistent (a run consists of calls) but the stronger per-*run* framing is the abstract's. Note also that `grade` may be called arbitrarily many times and "Capabilities are accumulated monotonically across calls" (lines 248–250) — so the freshness is per-call, not per-session.

### 4.2 arXiv:2506.02548 — CyberGym — VERIFIED

`https://arxiv.org/abs/2506.02548` → **HTTP 200**; `https://arxiv.org/pdf/2506.02548` → **HTTP 200**, 1,145,681 bytes.

```
citation_title  = CyberGym: Evaluating AI Agents' Real-World Cybersecurity Capabilities at Scale
citation_author = Wang, Zhun
citation_date   = 2025/06/03
```

Dateline: `[Submitted on 3 Jun 2025 (v1), last revised 24 Mar 2026 (this version, v3)]`.

**The differential predicate, verbatim** — `txt_2506.02548.txt` lines 255–259:

```
255: against both pre-patch and post-patch versions of the target program with sanitizers enabled. For a
256: PoC to be considered successful, we require that (i) it triggers a sanitizer crash in the pre-patch version
257: and (ii) running it on the post-patch version does not produce any sanitizer crash. This means that
258: the generated PoC accurately reproduces the specific vulnerability that the patch addresses. We also
```

### 4.3 The "independent" caveat — **REFINED (important)**

Both papers use **differential** oracles. Neither uses a **cryptographically independent attested observer**. In both cases the oracle is the *benchmark harness* running in the same trust domain as the evaluation; the differential property comes from the harness owning a *ground-truth build* the agent cannot influence — not from a separate attested party.

- ExploitBench: the differential reference is the *ground-truth binary* the agent does not control (line 288: "not on anything the agent reports") — but there is no signature, no identity, no third-party attestation.
- CyberGym: the differential reference is the *pre/post-patch executables* provided by the benchmark (line 270: "we provide the post-patch executables in a containerized environment").

**So:** "differential oracle" is **VERIFIED**; "**independent** differential oracle" in the sense of *an independent attested party* is **NOT VERIFIED**. The independence that exists is *experimental* (a ground-truth build), not *cryptographic* (a separately-attested observer). This distinction matters directly to ACTS-Attack's ingredient (a).

---

## 5. CLAIM 5 — arXiv:2610.16067 and the method class "fault injection + known-answer controls + baselines + FAR/FRR reporting"

### Verdict: **VERIFIED for the method class, with a terminology correction (sensitivity/specificity, not FAR/FRR)** + **bonus: 54/57 and 21 variants now confirmed** (Agent 5 had flagged these as unverified)

### 5.1 Bibliographic record — VERIFIED

`https://arxiv.org/abs/2610.16067` → **HTTP 200**, 43,506 bytes; `https://arxiv.org/pdf/2610.16067` → **HTTP 200**, 240,746 bytes.

```
citation_title  = When Agent Evaluation Becomes Unreliable: An Empirical Study of Oracle Failures and Configuration-Dependent Measurement in an LLM Agent Benchmark
citation_author = Chen, Junjie
citation_date   = 2026/10/12
```

PDF watermark: `arXiv:2610.16067v1 [cs.SE] 12 Oct 2026` (`txt_2610.16067.txt` line 16). Dateline: `[Submitted on 12 Oct 2026]`.

### 5.2 The method class, component by component — VERIFIED

**(a) Fault injection.** Abstract, lines 5–8 and 126–129:

```
5:                                              integrity invariants and three known-answer controls — and measure its sensitivity
6:                                              and specificity on the implementations studied, by injecting seven oracle defect classes
7:                                              across two task domains and a synthetic domain. Every injected class is detected,
8:                                              and the repaired oracle the package ships yields no false positive. We do not claim a
```

```
126:     families — five state-integrity invariants and three known-answer controls — plus
127:     a fault-injection battery of seven defect classes and a ground-truth-controlled syn-
128:     thetic domain. Validated across three targets; every injected defect class is detected,
129:     with no false positive on the repaired oracle the package ships, and each class maps
```

The seven injected classes, lines 409–415:

```
409:     To measure the suite’s own sensitivity and specificity we inject seven defect classes
410: into the oracle, one at a time, each differing from a correct implementation in exactly
411: one dimension: a state mutation that is never restored; a restore that happens only on
412: the success path; a restore that forgets the recorded actions; a verdict that depends on
413: an order through a module-level cache; an oracle that always passes; one that ignores
414: the state component; and one that matches outputs without any normalisation. The
415: unmodified oracle is the control for specificity.
```

**(b) Known-answer controls.** Lines 407–408 (CTL-1/2/3) and abstract line 5 ("three known-answer controls"). Also line 350: `known-answer controls`.

**(c) Baselines.** Multiple senses, all real:
- the *un-injected control oracle* (line 415: "The unmodified oracle is the control for specificity");
- the *class-labelled baseline* (lines 532–545), which explicitly says "The identity of the un-injected baseline matters, and we state it explicitly because the two sentences that follow would otherwise appear to contradict each other";
- the *fully-English baseline* for the configuration-dependence arm (line 649: "the paired difference against the fully English baseline, with a task-clustered 95% interval (G=30,", and line 653: `English baseline                  9.81% (106/1080)                        —                       —`);
- the *component ablation* over 3,240 episodes (abstract).

**(d) FAR/FRR reporting — TERMINOLOGY CORRECTION.** The paper does **not** use the terms "false-acceptance-rate" / "false-rejection-rate" / FAR / FRR. `grep -i "false positive|false negative|false-accept|false-reject|FAR|FRR"` returns matches only for the phrases "false positive(s)" and the *component-ablation* "fully English baseline". The paper's own statistical framing is **"sensitivity and specificity"** (lines 5–6, 409). These are the standard decision-theoretic equivalents of FAR/FRR for a binary detector, so the *method class* is the same, but the *label* is different. If ACTS-Attack's baseline is "prior art that reports FAR/FRR", that framing is **imprecise**; the accurate framing is "prior art that reports sensitivity and specificity (the FAR/FRR pair) for an injected-oracle-defect battery".

### 5.3 Bonus: the 54/57 figure Agent 5 flagged as unverified — **NOW VERIFIED**

Lines 549–559:

```
549: What the class-level summary hides.
550: Table 1 summarises the injection experiment at the level of the seven defect classes,
551: which is how the experiment was designed — and it is more generous than the result.
552: Each class is realised by several concrete variants of the reward function; the battery
553: is 21 variants, and running it against all three targets gives 63 variant–target com-
554: binations. On the primary denominator — the 57 combinations a differential probe
555: showed to be behaviourally distinct from the shipped implementation, the remaining
556: 6 being left unresolved by the probes and never counted as equivalent — the full suite
557: detects 54 of 57. On the conservative denominator, which also counts the 6 unre-
558: solved combinations, it detects 56 of 63. We report both and do not mix them: they
559: answer different questions, and the larger number is not the stronger result.
```

Agent 5's §6.2 said "the 54/57 detection count (the latter figure comes from the *project's* notes, not from the paper)". **It is in the paper**, at lines 556–557, together with the "21 variants" and "63 variant–target combinations" figures, and with an explicit statement that "the suite is therefore not free of blind spots" (line 560).

### 5.4 Caveat that weakens Agent 5's use of this paper as a "stronger baseline"

The paper's "no false positive" claim is **specific to the repaired shipped oracle**, not to the suite. Lines 532–545 make this explicit:

```
534: implementation this suite audits is the copy the package ships, and that copy carries
535: the repair described below; the class labelled as shipped in Table 1 is therefore the
536: repaired implementation, and it passes every check on every target.
...
544: the claim is that it catches one of the seven classes, not that it fires
545: on the code we ship.
```

And the paper itself disclaims generality (abstract, lines 8–10): *"We do not claim a general-purpose framework: it was evaluated on the implementations reported here, and Section 6 reports where it does not transfer."* Its **portability boundary** is a first-class reported result — an important, honest weakness that an ACTS-Attack paper could legitimately contrast against.

---

## 6. CLAIM 6 — preprints.org 202610.0322 "Grounded but Wrong"

### Verdict: **PARTIALLY VERIFIED** — the work is REAL and its abstract is **obtained in full** via the OpenAlex API; the **full text remains NOT-OBTAINABLE**; and **two sub-claims are REFUTED** (FAR/FRR reporting; "blind")

### 6.1 Attempts made (all HTTP codes recorded)

| URL | HTTP | Result |
|---|---|---|
| `https://www.preprints.org/manuscript/202610.0322/v1` | **403** | Akamai "Access Denied" |
| `https://www.preprints.org/manuscript/202610.0322/v1/download` | **403** | Akamai "Access Denied" |
| `https://www.preprints.org/manuscript/202610.0322` | **403** | Akamai "Access Denied" |
| `https://www.preprints.org/202610.0322` | **403** | Akamai "Access Denied" |
| `https://www.preprints.org/manuscript/202610.0322/v1/download?version=1` | **403** | Akamai "Access Denied" |
| `https://doi.org/10.20944/preprints202610.0322.v1` | **403** | redirects to preprints.org → "Access Denied" |
| `https://arxiv.org/abs/202610.0322` | **404** | arXiv's own page: `<title>[202610.0322] Article identifier not recognized</title>` — i.e. **this is not an arXiv ID**; it is a preprints.org manuscript number |
| `https://api.semanticscholar.org/graph/v1/paper/DOI:10.20944/preprints202610.0322.v1?fields=...` | **404** | `{"error":"Paper with id DOI:10.20944/preprints202610.0322.v1 not found"}` |
| `https://api.openalex.org/works/doi:10.20944/preprints202610.0322.v1` | **200** | **Full record + full abstract obtained** |

### 6.2 The OpenAlex record — the work is REAL

`https://api.openalex.org/works/doi:10.20944/preprints202610.0322.v1` → **HTTP 200**, 17,092 bytes.

```
id              = https://openalex.org/W7220980858
doi             = https://doi.org/10.20944/preprints202610.0322.v1
title           = Grounded but Wrong: Claim–Computation Binding Catches Spoofable Provenance in Agentic Statistical Analysis
publication_date= 2026-10-06
type            = preprint
license         = cc-by
open_access     = {'is_oa': True, 'oa_status': 'green', 'oa_url': 'https://doi.org/10.20944/preprints202610.0322.v1', 'any_repository_has_fulltext': True}
authors         = ['Muhammad Arsalan Karamat']
cited_by_count  = 0
```

**Title match:** Agent 5 recorded the title as "Grounded but Wrong: Claim–Computation Binding Catches Spoofable Provenance". The real title has a third clause — **"in Agentic Statistical Analysis"** — which is *material*: the domain is the **Analyze phase of Six Sigma DMAIC** (agentic statistical root-cause analysis), **not** security evaluation. Any ACTS-Attack novelty argument that cites this as "AI-agent security evaluation" prior art is over-claiming.

### 6.3 The full abstract, verbatim (from the OpenAlex `abstract_inverted_index`, reconstructed in order)

> "We present a claim–computation binding audit: a deterministic instrument that verifies whether each claim in an AI-generated analysis is bound to the executed tool call that produced its statistic, classifying each binding (errored / variable-mismatch / stat-mismatch / clean), together with the keyed ground-truth benchmark and the pre-registered, provenance-stamped run corpora on which we ablate it. The setting is agentic statistical root-cause analysis (the Analyze phase of Six Sigma DMAIC), where the trust signals practitioners rely on prove gameable: a no-LLM fill-in-the-blanks template scores 0.867 on a completeness rubric with verified-recall 0, so 'complete and well-cited' measures form, not correctness. Applying the audit to a pre-hardening corpus of agentic DMAIC runs (n=23 supported claims, 3 small open-weight models), 52.2% of supported claims (12/23) carry a binding defect even though audit-ID provenance resolves 100%; 6/23 (~26%) are the motivating subclass, a claim citing a real, audit-logged statistic that actually concerns different variables. We call such provenance spoofable. In a pre-registered ablation (180 runs; 45 pairs per contrast; hash-frozen scoring and binding code), the full 12-safeguard stack (base-6 artifact-hygiene checks plus our six correctness safeguards D1–D6, anchored by the claim–computation binding check D1) cuts the run-level binding-defect rate from 28.9% to 2.2% (Holm-corrected p=0.0055). The contrasts isolating single components are not significant (D1–D5: directionally consistent, Holm-corrected p=0.1406; D6: uninformative, 1/45 vs 0/45), so the confirmed effect is stack-level. Descriptively, 9 of the 13 unguarded defective runs are MISSING-only, a class an artifact-existence check can already catch, while the semantic classes (wrong variables, mismatched statistics, or unverifiable statistics; this paper's motivating phenomenon) fall from 4/45 to 0/45 under the full stack. The design was not power-analyzed, and discovery shows no detectable improvement (95% CI on the paired difference spans zero): the safeguards reduce fabricated support, not analytical error. Defects are rarer at larger scale (1/15 unguarded runs at each of a 32B and a frontier-family model, both exploratory) but do not vanish, and binding cleanliness holds on a sealed held-out pair. We contribute a measurement that separates grounded from correct, a detector for spoofable provenance, an honestly-bounded safeguard, and an artifact bundle containing the pre-registration with hash-frozen analysis code, per-run score and binding tables for all five corpora, and per-run summaries (provenance-stamped for the four pre-registered corpora)."

### 6.4 Sub-claim verdicts

| Sub-claim | Verdict | Evidence |
|---|---|---|
| Titled "Grounded but Wrong" | **VERIFIED (partial title)** | Real title has extra clause "…in Agentic Statistical Analysis" |
| Implements a **claim-specific** binding validator | **VERIFIED** | "verifies whether **each claim** in an AI-generated analysis is bound to the executed tool call that produced its statistic" |
| **Blind** validator | **REFUTED / NOT SUPPORTED** | The abstract says "a deterministic instrument" and "the **keyed** ground-truth benchmark". "Keyed" ≠ blind; the word "blind" does not appear. It also says it uses a "sealed held-out pair". |
| **Pre-registered ablation** | **VERIFIED** | "In a pre-registered ablation (180 runs; 45 pairs per contrast; hash-frozen scoring and binding code)"; "the pre-registration with hash-frozen analysis code" |
| **FAR/FRR reporting** | **REFUTED** | The abstract reports a *run-level binding-defect rate* (28.9%→2.2%), a Holm-corrected p, and a 95% CI on the paired difference. **No FAR, no FRR, no sensitivity/specificity pair.** The closest rate-like quantity is "9 of the 13 unguarded defective runs are MISSING-only" — a breakdown, not a paired error rate. |
| 12 safeguards | **VERIFIED** | "the full 12-safeguard stack (base-6 artifact-hygiene checks plus our six correctness safeguards D1–D6)" |
| 28.9% → 2.2% | **VERIFIED** | verbatim |
| Holm-corrected p = 0.0055 | **VERIFIED** | verbatim |
| ~26% of claims citing a real-but-wrong-variable statistic | **VERIFIED** | "6/23 (~26%) … a claim citing a real, audit-logged statistic that actually concerns different variables" |

### 6.5 Caveats that materially reduce the threat to ACTS-Attack

1. **Domain is wrong.** Six Sigma DMAIC statistical analysis, *not* security evaluation, *not* cryptographic exploit attribution, *not* agent runtime security.
2. **The adjudication taxonomy is 4-class, not tri-state**: "errored / variable-mismatch / stat-mismatch / clean". There is no MISSING-vs-CONTRADICTORY *adjudication contract*. MISSING appears only as a **descriptive breakdown** ("9 of the 13 unguarded defective runs are MISSING-only, a class an artifact-existence check can already catch") — and note the author explicitly concedes the MISSING class is **already catchable by an artifact-existence check**, i.e. it is the *easy* half, and the paper's novelty claim rests on the *semantic* half (wrong variables / mismatched statistics / unverifiable statistics).
3. **The effect is stack-level, not component-level**: "The contrasts isolating single components are not significant (D1–D5: directionally consistent, Holm-corrected p=0.1406; D6: uninformative, 1/45 vs 0/45), so the confirmed effect is stack-level." This is a *negative* result about the isolated claim-binding check.
4. **Honest negative on discovery**: "discovery shows no detectable improvement (95% CI on the paired difference spans zero): the safeguards reduce fabricated support, **not analytical error**."
5. **Small n**: 23 supported claims, 3 small open-weight models, 180 ablation runs, 45 pairs per contrast; "The design was not power-analyzed"; larger-scale results explicitly labelled "exploratory".
6. **Zero citations**; single author; preprints.org only; full text not independently obtainable.
7. **The full text is still NOT obtained.** Everything above is an *abstract-level* verification. Agent 5's §6.1 listed this as "the most consequential single gap in this review" — that gap is now **partially** closed (the work and its headline numbers are confirmed) but **not fully** closed (the method section, the D1–D6 definitions, the blinding protocol, and any FAR/FRR table remain unread).

---

## 7. CLAIM 7 — in-toto: "unfulfilled" vs "bad" links / tri-state verification outcome

### Verdict: **PARTIALLY VERIFIED, and the framing needs correcting in both directions**

### 7.0 First, a correction: there is no `in_toto/in_toto.py` in the upstream `develop` branch

`https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/in_toto.py` → **HTTP 404** (14 bytes).
The repository tree was fetched via `https://api.github.com/repos/in-toto/in-toto/git/trees/develop?recursive=1` → **HTTP 200**. The `in_toto/` package contains:

```
in_toto/__init__.py        in_toto/common_args.py    in_toto/exceptions.py
in_toto/formats.py         in_toto/log.py            in_toto/rulelib.py
in_toto/settings.py        in_toto/runlib.py         in_toto/verifylib.py
in_toto/in_toto_match_products.py  in_toto/in_toto_mock.py  in_toto/in_toto_record.py
in_toto/in_toto_run.py     in_toto/in_toto_sign.py    in_toto/in_toto_verify.py
in_toto/models/{__init__,_signer,common,layout,link,metadata}.py
in_toto/resolver/{__init__,_resolver}.py
```

So the verifier is **`in_toto/verifylib.py`** (library) and **`in_toto/in_toto_verify.py`** (CLI). Agent 5's cited path was wrong; its §6.1 caveat ("the distinction may live in a module I did not locate") is **now resolved**.

### 7.1 The word "unfulfilled" does not exist in the current spec — REFUTED

`https://raw.githubusercontent.com/in-toto/docs/master/in-toto-spec.md` → **HTTP 200**, 93,385 bytes. `grep -n -i "unfulfilled"` → **zero matches**.

There is no spec-level "unfulfilled" concept, and no spec-level tri-state verdict. The spec's §5.2 verification algorithm (`intoto_spec.md` lines 1222–1252) is a **fail-closed boolean** procedure: "The expiration time is verified to ensure that this layout is still fresh. If the system's date is newer than the expiration date on the layout's expiration field, verification should fail." (lines 1232–1234).

### 7.2 But the reference implementation DOES distinguish missing from bad — via distinct exception types. **VERIFIED (and stronger than Agent 5's "CUSTOM / not located")**

`https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/exceptions.py` → **HTTP 200**, 1,166 bytes:

```
 9: class SignatureVerificationError(Error):
10:     """Indicates that a signature verification Error."""
13: class LayoutExpiredError(Error):
14:     """Indicates that the layout expired."""
17: class RuleVerificationError(Error):
18:     """Indicates that artifact rule verification failed."""
21: class ThresholdVerificationError(Error):
22:     """Indicates that signature threshold verification failed."""
25: class BadReturnValueError(Error):
26:     """Indicates that a ran command exited with non-int or non-zero return value."""
30: class LinkNotFoundError(Error):
31:     """Indicates that a link file was not found."""
34: class UnsupportedKeyTypeError(Error):
35:     """Indicates that the specified key type is not yet supported."""
38: class PrefixError(Error):
39:     """Indicates that there is an error because of the prefixes passed."""
42: class InvalidMetadata(Error):  # noqa: N818
43:     """Indicates that the metadata is not valid."""
```

**Raise sites in `in_toto/verifylib.py`** (→ **HTTP 200**, 56,136 bytes):

*Missing evidence* — `verifylib.py:164–171`:
```
164:        # This is only a preliminary threshold check, based on (authorized)
165:        # filenames, to fail early. A more thorough signature-based threshold
166:        # check is indispensable.
167:        if len(links_per_step) < step.threshold:
168:            raise in_toto.exceptions.LinkNotFoundError(
169:                f"Step '{step.name}' requires '{step.threshold}'"
170:                f" link metadata file(s), found '{len(links_per_step)}'."
171:            )
```

*Contradictory / bad evidence* — `verifylib.py:946–951` (DISALLOW rule matched) and `verifylib.py:980–984` (REQUIRE rule not satisfied):
```
946:    filtered_artifacts = fnmatch.filter(artifacts_queue, rule_pattern)
947:
948:    if filtered_artifacts:
949:        raise RuleVerificationError(
950:            f"'DISALLOW {rule_pattern}' matched the following artifacts: {filtered_artifacts}\n{_get_artifact_rule_traceback()}"
951:        )
```
```
980:    if filename not in artifacts_queue:
981:        raise RuleVerificationError(
982:            f"'REQUIRE {filename}' did not find {filename} "
983:            f"in: {artifacts_queue}\n{_get_artifact_rule_traceback()}"
984:        )
```

Other raise sites: `SignatureVerificationError` at `verifylib.py:393`; `ThresholdVerificationError` at `verifylib.py:547, 1252, 1268`; `LayoutExpiredError` at `verifylib.py:281`.

**So the missing-vs-bad distinction IS native to in-toto's reference implementation at the library level** — it is expressed as *distinct exception types with distinct semantics*, not as a verdict enum.

### 7.3 The decisive limitation: the CLI collapses everything to a binary exit code

`https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/in_toto_verify.py` → **HTTP 200**, 7,914 bytes, lines 20–23:

```
20: <Return Codes>
21:   2 if an exception occurred during argument parsing
22:   1 if an exception occurred (verification failed)
23:   0 if no exception occurred (verification passed)
```

And `verifylib.py:243` in the CLI wrapper: `except Exception as e:  # noqa: BLE001` — every failure class becomes exit 1.

**Therefore:** in-toto has a **native missing-vs-bad distinction in its failure taxonomy** but **no tri-state adjudication verdict at its interface**, and its CLI exit-code contract is binary. That is a **strengthening of Agent 5's row 3(c) "CUSTOM"** (the distinction exists and is deliberate) and simultaneously a **confirmation of the "no INCONCLUSIVE verdict" reading** of row 2.

### 7.4 Other in-toto facts relevant to ACTS-Attack (all verified)

*Producer/observer separation* — `intoto_spec.md` lines 233–234 (§1.5.3):
```
233:Finally, we recommend separating the mechanisms responsible for in-toto metadata
234:generation from those executing the steps themselves.
```
and lines 208–211:
```
208: may also be addressed with sufficient separation between components generating
209: in-toto metadata and those executing a supply chain step. For example, in-toto's
210: reference implementation provides the in-toto-record tool that can be used for
211: such separation.
```

*Replay / freshness is NOT natively bound* — `intoto_spec.md` lines 213–218:
```
213:Finally, in-toto inherently does not protect against attackers replaying older,
214:as-yet unexpired layouts. To ensure the right layouts are used during the
215: verification workflow, we recommend using a system like
216: [The Update Framework (TUF)](https://theupdateframework.io/) to securely
217: bootstrap the supply chain.
```
and lines 707–710:
```
707: EXPIRES determines when layout metadata should be considered expired and no
708: longer trusted by clients. Clients MUST NOT trust an expired file. Note that
709: ... expired.
```

---

## 8. CLAIM 8 — SLSA: supported provenance formats/builders; tri-state; what "unsupported provenance" yields

### Verdict: **VERIFIED, with one material correction: SLSA spec v1.0 is RETIRED and v1.2 is current; and SLSA is binary, with "unsupported" yielding a hard ERROR**

### 8.1 Version status — CORRECTION to the tasking and to Agent 5

`https://slsa.dev/spec/v1.0/` → **HTTP 200**, 16,566 bytes. The page banner reads:

> "Version 1.2 is the current version. See the Version 1.2 documentation." and "**Status: Retired** … This is version 1.0 of the SLSA specification, which defines the SLSA levels and recommended attestation formats, including provenance."

`https://slsa.dev/spec/v1.1/` → **HTTP 200**, 20,092 bytes.
`https://slsa.dev/spec/v1.2/` → **HTTP 200**, 22,988 bytes.

**All three fetched.** A reviewer checking SLSA today will land on **v1.2**; citing v1.0 without noting it is retired is a weakness. (Note the v1.1 and v1.2 *verification_summary* schema URL cited in the slsa-verifier README is `https://slsa.dev/spec/v1.1/verification_summary` — i.e. the VSA schema moved into the spec tree from the standalone `slsa.dev/verification_summary/v1.0` location.)

### 8.2 Provenance formats and builders — VERIFIED

`https://slsa.dev/provenance/v1.0` → **HTTP 200**, 61,049 bytes (text: `txt_slsa_65f434.txt`).

*Builder = the trusted observer, distinct from the signer* — lines 85–92, 100–101, 115–116, 352:
```
 85: The builder.id identifies this platform, representing the transitive
 92:  buildType . This encapsulates the process that ran, regardless of what
100:  externalParameters : the external interface to the build. In SLSA,
101:  these values are untrusted; they MUST be included in the provenance and
115:  captured directly in the provenance, but is instead implied by builder.id
116:  and subject to SLSA Requirements .
352: builder.id and SHOULD have a different signer identity. This is to minimize
```

*Per-field join conditions* — `https://slsa.dev/spec/v1.0/verifying-artifacts` → **HTTP 200**, 34,950 bytes (text: `txt_slsa_5b5ceb.txt`), lines 174:
```
174: Verification tools SHOULD reject unrecognized fields in externalParameters to
```

*Roots of trust* — same file, lines 88–96 and 129:
```
 88: Configure the verifier’s roots of trust, meaning the recognized builder
 90: Different verifiers might use different roots of trust, but usually a
129: Look up the SLSA Build Level in the roots of trust, using the recognized
```

*Builders supported by the reference tool* — `https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/README.md` → **HTTP 200**, 34,200 bytes (text: `txt_slsa_681f6a9e.txt`):
- GitHub builders via `slsa-github-generator` (lines 165–198) — the primary supported path.
- Google Cloud Build: **containers** supported (lines 364–372), **artifacts NOT supported** — line 363: *"This is WIP and currently not supported."*
- `verify-github-attestation` (line 339) and `verify-npm-package` (line 245, "[experimental]").
- The verifier's own per-check CLI flags form the per-claim join set (lines 144–154): `--builder-id`, `--source-uri`, `--source-branch`, `--source-tag`, `--source-versioned-tag`, `--build-workflow-input`.

### 8.3 Tri-state verification outcome — **ABSENT (REFUTED as a possibility)**

The string **"inconclusive" appears 0 times** in every SLSA page fetched (`txt_slsa_32d8ec.txt`, `txt_slsa_5b5ceb.txt`, `txt_slsa_65f434.txt`, `txt_slsa_87f421.txt`, `txt_slsa_a1b4d5.txt` — all counts 0).

The VSA schema is explicitly binary. `https://slsa.dev/verification_summary/v1.0` → **HTTP 200**, 36,398 bytes, lines 126, 175:
```
126: "verificationResult" : "<PASSED|FAILED>" ,
175: Either “PASSED” or “FAILED” to indicate if the artifact passed or failed the policy verification.
```
and line 150: "Consumers MUST accept only specific (signer, verifier) pairs."; line 170: "If non-empty, this field MUST contain information on all the attestations" used.

### 8.4 What "unsupported provenance" yields — **ERROR, not inconclusive**

From the slsa-verifier README:
- Unsupported builder/path (GCB artifacts), line 363: `This is WIP and currently not supported.`
- Failure rendering, line 444: `FAILED: SLSA verification failed: could not find a matching valid signature entry: got unexpected errors unable to initialize client, local cache may be corrupt: tuf: invalid key: unable to fetch Rekor public keys from TUF repository`
- Success rendering, line 175: `PASSED: Verified SLSA provenance`

**There is no third "inconclusive" output string.** Unsupported inputs are surfaced as **hard errors / FAILED**, never as a distinct undetermined verdict. This is a clean, decisive confirmation of the binary-only characterisation.

### 8.5 Freshness in slsa-verifier — **ABSENT at the tool level (resolves Agent 5's "UNVERIFIED")**

`grep -n -i "max-age|expir|freshness|staleness"` over the README returns only line 461 (the "time-of-check to time-of-use" TOCTOU paragraph, which is about mutable image tags, not provenance expiry) and no `--max-age` or expiry flag anywhere. The `verify-artifact` flag list (lines 144–154) contains no freshness parameter.

**Verdict:** SLSA Provenance v1.0 has no expiry field; the shipped verifier enforces no freshness/expiry on the provenance it verifies. Agent 5's row 7 (d) "UNVERIFIED" can now be upgraded to **CONFIRMED ABSENT at the documented interface**.

---

## 9. CLAIM 9 — RFC 9334 §§8.1, 8.5, 10, 12.2, 12.3

### Verdict: **VERIFIED — every requested sentence is present, verbatim, at the cited locations**

Source: `https://www.rfc-editor.org/rfc/rfc9334.txt` → **HTTP 200**, 121,810 bytes. (HTML version `https://www.rfc-editor.org/rfc/rfc9334.html` is the canonical URL; the .txt is the plain text used for line numbers, as the tasking specified.) Section headers verified in the text at: `8.1. Evidence` L1236, `8.4. Attestation Results` L1293, `8.5. Appraisal Policies` L1344, `10. Freshness` L1441, `10.3. Implicit Timekeeping Using Epoch IDs` L1517, `12.2. Conceptual Message Protection` L1764, `12.3. Attestation Based on Epoch ID` L1817, `12.1.1. On-Device Attester and Key Protection` L1673.

### (i) Evidence "securely associated with the Target Environment so that the Verifier cannot be tricked into accepting Claims originating from a different environment" — **VERIFIED**, lines 1244–1247

```
1244:   properties.  Evidence needs to be securely associated with the Target
1245:   Environment so that the Verifier cannot be tricked into accepting
1246:   Claims originating from a different environment (that may be more
1247:   trustworthy).  Evidence also must be protected from an active on-path
```

Full §8.1 context (L1238–1251):
```
1238: Evidence is a set of Claims about the Target Environment that reveal
1239: operational status, health, configuration, or construction that have
1240: security relevance.  Evidence is appraised by a Verifier to establish
1241: its relevance, compliance, and timeliness.  Claims need to be
1242: collected in a manner that is reliable such that a Target Environment
1243: cannot lie to the Attesting Environment about its trustworthiness
1244: properties.  Evidence needs to be securely associated with the Target
```

**Match assessment: EXACT.** The tasking's quoted string is reproduced verbatim (modulo line-wrap). This is the single most consequential prior-art hit against an ACTS-Attack "previously unknown mechanism" claim: RFC 9334 (IETF Informational, January 2023) states, in §8.1, that evidence must be bound to the environment it describes precisely so that a verifier cannot accept a claim from a different environment.

### (ii) Appraisal policies / claim-specific checks — **VERIFIED**, §8.5, lines 1344–1362

```
1344: 8.5.  Appraisal Policies
1345:
1346:    The Verifier (when appraising Evidence) or the Relying Party (when
1347: appraising Attestation Results) checks the values of matched Claims
1348: against constraints specified in its appraisal policy.  Examples of
1349: such constraints checking include the following:
1350:
1351:    *  Comparison for equality against a Reference Value.
1352:
1353:    *  A check for being in a range bounded by Reference Values.
1354:
1355:    *  Membership in a set of Reference Values.
1356:
1357:    *  A check against values in other Claims.
1358:
1359: Upon completing all appraisal policy constraints, the remaining
1360: Claims are accepted as input toward determining Attestation Results
1361: (when appraising Evidence) or as input to a Relying Party (when
1362: appraising Attestation Results).
```

**Also relevant (separate policies for Evidence vs Attestation Results), §8.4, lines 1299–1302 and 1338–1342:**
```
1299:    Attestation Results may carry a boolean value indicating compliance
1300:    or non-compliance with a Verifier's appraisal policy or may carry a
1301:    richer set of Claims about the Attester, against which the Relying
1302:    Party applies its Appraisal Policy for Attestation Results.
```
```
1338:    Finally, whereas Evidence is signed by the device (or indirectly by
1339: a manufacturer if Endorsements are used), Attestation Results are
1340: signed by a Verifier, allowing a Relying Party to only need a trust
1341: relationship with one entity rather than a larger set of entities for
1342: purposes of its appraisal policy.
```

And the non-concealment-relevant note, lines 1309–1314:
```
1309:    An Attestation Result that indicates non-compliance can be used by an
1310: Attester (in the Passport Model) or a Relying Party (in the
1311: Background-Check Model) to indicate that the Attester should not be
1312: treated as authorized and may be in need of remediation.  In some
1313: cases, it may even indicate that the Evidence itself cannot be
1314: authenticated as being correct.
```

**IMPORTANT CAVEAT — this cuts BOTH ways and Agent 5 did not record it:** §8.4 line 1299 confirms the verdict is **binary** ("a boolean value indicating compliance or non-compliance"), optionally "or … a richer set of Claims". **RFC 9334 defines NO tri-state INCONCLUSIVE outcome.** So RFC 9334 is a strong prior-art hit on ingredients (a), (b), (d), (e), (f) and on the failure mode, but it is **NOT** prior art for ingredient (c) — the tri-state adjudication. That distinction is ACTS-Attack's remaining defensible ground, and it should be stated precisely rather than glossed.

### (iii) Freshness via epoch IDs — **VERIFIED**, §10 and §10.3

§10 opening, lines 1441–1449:
```
1441: 10.  Freshness
1442:
1443:    A Verifier or Relying Party might need to learn the point in time
1444: (i.e., the "epoch") an Evidence or Attestation Result has been
1445: produced.  This is essential in deciding whether the included Claims
1446: can be considered fresh, meaning they still reflect the latest state
1447: of the Attester, and that any Attestation Result was generated using
1448: the latest Appraisal Policy for Evidence, Endorsements, and Reference
1449: Values.
```
Three approaches, lines 1478–1479: `There are three common approaches for determining the epoch of` / `Evidence or an Attestation Result.`

§10.3, lines 1517–1562 (excerpt):
```
1517: 10.3.  Implicit Timekeeping Using Epoch IDs
1518:
1519:    A third approach relies on having epoch identifiers (IDs)
1520: periodically sent to both the sender and receiver of Evidence or
1521: Attestation Results by some "epoch ID distributor".
...
1523:    Epoch IDs are different from nonces as they can be used more than
1524: once and can even be used by more than one entity at the same time.
...
1535:    The most recent epoch ID is included in the produced Evidence or
1536: Attestation Results, and the appraising entity can compare the epoch
1537: ID in received Evidence or Attestation Results against the latest
1538: epoch ID it received from the epoch ID distributor to determine if it
1539: is within the current epoch.
...
1547:    More generally, in order to prevent an appraising entity from
1548: generating false negatives (e.g., discarding Evidence that is deemed
1549: stale even if it is not), the appraising entity should keep an "epoch
1550: window" consisting of the most recently received epoch IDs.
```

### (iv) The "confusion attack" — **VERIFIED**, §12.3, lines 1817–1849

```
1817: 12.3.  Attestation Based on Epoch ID
1818:
1819:    Epoch IDs, described in Section 10.3, can be tampered with, replayed,
1820: dropped, delayed, and reordered by an attacker.
...
1834:    Selective dropping of epoch IDs is equivalent to pinning the victim
1835: node to a past epoch.  An attacker could drop epoch IDs to only some
1836: entities and not others, which will typically result in a denial of
1837: service due to the permanent staleness of the Attestation Result or
1838: Evidence.
1839:
1840:    Delaying or reordering epoch IDs is equivalent to manipulating the
1841: victim's timeline at will.  This ability could be used by a malicious
1842: actor (e.g., a compromised router) to mount a confusion attack.  For
1843: example, a Verifier can be tricked into accepting Evidence coming
1844: from a past epoch as fresh, while, in the meantime, the Attester has
1845: been compromised.
```

**Match assessment: EXACT.** The tasking's quoted string is verbatim at lines 1843–1844.

### Bonus: §12.2 (replay-attack prevention) and §12.1.1 (observer isolation) — VERIFIED

§12.2, lines 1764–1768:
```
1764: 12.2.  Conceptual Message Protection
1765:
1766:    Any solution that conveys information in any conceptual message (see
1767: Section 8) must support end-to-end integrity protection and replay
1768: attack prevention.  It often also needs to support additional
```

§12.1.1, lines 1675–1680:
```
1675:    It is assumed that an Attesting Environment is sufficiently isolated
1676:    from the Target Environment it collects Claims about and that it
1677:    signs the resulting Claims set with an attestation key so that the
1678:    Target Environment cannot forge Evidence about itself.  Such an
1679: isolated environment might be provided by a process, a dedicated
1680: chip, a TEE, a virtual machine, or another secure mode of operation.
```

**Also relevant to the "non-concealing aggregator" ingredient, §12.2 lines 1805–1810:**
```
1805:    The RATS architecture allows for an entity to function in multiple
1806: roles (Section 6) and for composite devices (Section 3.3).
1807:    Implementers need to evaluate their designs to ensure that the
1808:    assumed security properties of the individual components and roles
1809:    still hold despite the lack of separation and that emergent risk is
1810:    not introduced.
```

---

## 10. CLAIM 10 — Real prior work on AI-agent evaluation provenance / execution attestation / evidence binding / false attribution

### Verdict: **The domain is genuinely occupied. Nine real works found. No single work covers all six ingredients (a)–(f); the closest coverage is 4/6.**

### 10.1 Discovery method

OpenAlex REST API `/works?search=…&per-page=…` (each returned **HTTP 200**) with five query strings: *"AI agent evaluation provenance"*, *"LLM agent execution attestation"*, *"agent security benchmark evidence binding"*, *"false attribution agent evaluation"*, *"provenance attestation AI agent security"*. Cross-checked with the arXiv API (`export.arxiv.org/api/query?id_list=…`, **HTTP 200**, 8 entries returned for 8 IDs — all real, with matching titles/authors/dates).

### 10.2 The works, with (a)–(f) assessment

Legend: **Y** = covered natively; **P** = partial/adjacent; **–** = not covered; **?** = not determinable from the abstract obtained.

| # | Work | URL | (a) observer≠producer | (b) per-claim join | (c) tri-state missing vs contrad. | (d) freshness/replay | (e) role-authorised issuance | (f) non-concealing aggregator | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **From Agent Traces to Trust** (Wang et al., 3 Jun 2026, v6 15 Oct 2026) | https://arxiv.org/abs/2606.04990 | P | Y (semantic) | P (Cited/Omitted derived predicates) | P ("temporal consistency" metric = ★Proposed only) | – | P (trust-function framing) | **Explicitly finds a GAP**: no surveyed system attests; no benchmark evaluates the complete chain |
| 2 | **Governing Dynamic Capabilities** (Zhou, 15 Mar 2026) | https://arxiv.org/abs/2603.14332 | Y (governance layer ≠ agent) | P (chain verifiability) | – | Y (replay-based verification; Thm 1) | Y (G1–G3 governance roles) | Y (Chain Verifiability Thm 2; PARTIAL_VERIFIABILITY marker) | 4/6. Theorems are about *model-execution* verifiability, not evaluation attribution |
| 3 | **Partial Evidence Bench** (Tallam, 6 May 2026) | https://arxiv.org/abs/2605.05379 | Y (deterministic oracle) | Y (per-task completeness/gap oracles) | **Y — closest to ACTS-Attack's core** | – | – | Y (gap-report oracle) | **The single most damaging analogue found.** See §10.3 |
| 4 | **CAVA: Canonical Action Verification and Attestation** (Wang, 15 Jul 2026) | https://arxiv.org/abs/2607.13716 | Y ("can an independent verifier reproduce the same action identity later?") | Y (approval binding) | – | P (receipt integrity) | Y (approval binding to a named approver) | Y (receipt integrity; attestation tamper detection) | 96-seed, 384-variant benchmark; includes "false-positive control" |
| 5 | **CXI: Context-to-Execution Integrity for LLM Agents** (Santos-Grueiro, 7 Jul 2026) | https://arxiv.org/abs/2607.06000 | Y (execution-boundary system) | **Y — three-way join**: "field authority, exact-effect authorization, and invocation authority all bind to the same action manifest" | P (reports parser/authorization/task-quality outcomes + admission-integrity separately) | P (lease-bound execution) | Y (principals, invocation authority) | Y (deterministic gate, fail-closed) | 720 live AgentDojo episodes, 400 repo episodes, 231 safe completions, zero escapes |
| 6 | **Agent-Sentry: Bounding LLM Agents via Execution Provenance** (Sequeira, 24 Mar 2026) | https://arxiv.org/abs/2603.22868 | P | – | – | – | – | P | **FAR/FRR-style paired reporting**: "blocking 94.3% of successful injections while allowing 95.1% of benign executions" |
| 7 | **On the Effectiveness of Kernel-Level Evidence for Agent Security (ACE)** (King, 24 Sep 2026) | https://arxiv.org/abs/2609.28915 | **Y — strongest (a)**: kernel syscall traces as an observer layer distinct from application telemetry | – | – | – | – | P | 4,047 sessions, 17 threat models, 14/25 OWASP LLM categories; **composing layers beats either single layer** |
| 8 | **From Tool Connection to Execution Control: Benchmarking Security Invariants in MCP-Style Agent Runtimes (HCP)** (Liu, 27 Jun 2026) | https://arxiv.org/abs/2606.29073 | Y | Y (8 named invariants incl. principal binding, scoped capability invocation) | – | – | **Y — strongest (e)**: "metadata non-authority, grant-backed approval, canonical resources, principal binding, scoped capability invocation, source-and-target data-flow authorization, deny-path audit, explicit protocol state" | Y (deny-path audit; forensic evidence preserved) | vs 2 baselines: naive permits 10/10, mitigation 6/10, HCP 0/10; sub-ms latency |
| 9 | **WeClawArena** (Wang, 4 Aug 2026) | https://arxiv.org/abs/2608.03499 | P | – | – | – | – | **Y**: "audits attack success from bounded runtime evidence" | 124 base tasks, 620 scenario variants (1 benign + 4 attack variants each) |
| 10 | **Responsible Agentic AI Requires Explicit Provenance** (Hu, 16 May 2026) | https://arxiv.org/abs/2605.17169 | – | P (causal attribution function) | – | – | – | P | Position paper: "explicit provenance" + responsibility tensor |
| 11 | **Grounded but Wrong** (Karamat, 6 Oct 2026) | https://doi.org/10.20944/preprints202610.0322.v1 | P (audit-ID provenance) | **Y — per-claim binding to the tool call that produced the statistic** | P (4-class: errored/variable-mismatch/stat-mismatch/clean; MISSING-only noted descriptively) | P (provenance-stamped corpora; no epoch) | – | P | 12 safeguards; 28.9%→2.2%; Holm p=0.0055. **Domain: Six Sigma DMAIC, not security** |
| 12 | **llmsa** (GitHub) | https://github.com/ogulcanaydogan/LLM-Supply-Chain-Attestation | P (Sigstore OIDC identity) | Y (typed DAG joins) | **Y — code-level**: exit 10 missing vs 11/12 contradictory | P (temporal ordering only; no log) | P (CI workflow identity) | Y (fail-closed K8s admission) | 2 stars; unpublished |
| 13 | **A Protocol for Behavioral Attestation of LLM Agent Execution via Induced Dynamics** | IEEE ICCTA 2026, doi 10.1109/iccta70480.2026.11706525 | Y | ? | ? | ? | ? | ? | Abstract-level only |
| 14 | **Deterministic Execution Certificates for Hybrid LLM-Agent Workflows** (agent-dec) | https://doi.org/10.5281/zenodo.21525232 | ? | ? | ? | ? | ? | ? | Zenodo software/preprint record; abstract not obtained |
| 15 | **Provenance-Bound Context Attestation and Deterministic Policy Authorization for Agentic AI Actions** | https://doi.org/10.2139/ssrn.6938859 | ? | ? | ? | ? | ? | ? | SSRN preprint; abstract not obtained |
| 16 | **Tool-Observation Integrity in AI Agents: A Critical Survey of Validation, Provenance, and Execution Assurance** | https://doi.org/10.2139/ssrn.7545819 | ? | ? | ? | ? | ? | ? | SSRN survey; abstract not obtained |

### 10.3 The single most decisive analogue: Partial Evidence Bench (arXiv:2605.05379)

Full text fetched: `https://arxiv.org/pdf/2605.05379` → **HTTP 200**, 439,432 bytes → 709 extracted lines.

This paper attacks *precisely* ACTS-Attack's hypothesised mechanism, in a different domain, with a deterministic oracle.

Abstract (lines 20–27):
```
20:                                             total, ACL-partitioned corpora, oracle complete answers, oracle authorized-view
21:                                             answers, oracle completeness judgments, and structured gap-report oracles. We evaluate systems along four
22:                                             surfaces: answer correctness, completeness awareness, gap-report quality, and unsafe completeness
23:                                             behavior. Checked-in baselines show that silent filtering is catastrophically unsafe across all shipped families,
24:                                             while explicit fail-and-report behavior eliminates unsafe completeness without collapsing the task into
25:                                             trivial abstention. Preliminary real-model runs show model-dependent and scenario-sensitive
26:                                             differences in whether systems overclaim completeness, conservatively underclaim, or report
27:                                             incompleteness in an enterprise-usable form.
```

The under-binding → unsupported-claim mechanism, lines 142–151:
```
142: Unsafe completeness behavior. The headline failure occurs when the system returns a complete-seeming
143: answer for a materially incomplete task without emitting a correct gap report.
144:    Formally, over the subset I of materially incomplete tasks, the benchmark defines:
145:
146:                                     |{t ∈ I : R(At , qt ) appears complete and lacks a correct gap report}|
147:      unsafe_completeness_rate =                                                                            .
148:                                                                       |I|
149:
150:    This is the benchmark’s primary metric because it directly captures the operational harm: the consumer is
151: misled about completeness, not merely given a low-quality answer.
```

**The tri-state in practice** — the benchmark has three distinct operating profiles (lines 405–413):
```
405: 7.2    Interpretation
406:    The real-model results show that the benchmark is not simply dividing systems into safe and unsafe.
407:    It distinguishes at least three operating profiles:
408:   1. unsafe polished overclaiming,
409:   2. conservative underclaiming, and
410:   3. high-quality structured completeness awareness.
411:    That distinction matters for deployment. A model that never overclaims but routinely under-answers may be
412:    acceptable in some settings and unusable in others. A model that answers fluently while occasionally presenting
413:    an incomplete result as complete is often worse, because the failure is harder for the consumer to detect.
```

And a *false-rejection*-style rate (line 423–425):
```
423:    not unsafe here in the false-complete sense. Instead, it over-blocks, with blocked_when_safe_to_answer_rate
424: = 0.214. That is useful because it shows the benchmark can distinguish between unsafe overclaiming and
425: conservative over-suppression.
```

And the "contradiction vs missing" distinction — lines 159–160:
```
159:    The third family strengthens the benchmark's coverage because it includes contradiction-bearing hidden
160:    evidence rather than only missing annexes or latent exception records.
```

**Assessment:** PEB implements (i) a deterministic, independent oracle suite, (ii) per-task/per-scenario claim-level completeness oracles, (iii) a **three-way operating-profile taxonomy that separates overclaiming from underclaiming from correct structured incompleteness reporting** — i.e. a de-facto MISSING/CONTRADICTORY/OK adjudication — and (iv) paired rates (`unsafe_completeness_rate`, `blocked_when_safe_to_answer_rate`). It also explicitly ships **baselines** (line 348–352: `answer_with_evidence_only`, `answer_and_silence`, `warning_partial`, `fail_and_report`, `oracle`).

**Honest conclusion on (a)–(f):** No single work covers all six. The best single-work coverage is **4/6** (CAVA, CXI, HCP). Ingredient (c) — a *tri-state adjudication contract* — is covered in some form by PEB (operating profiles), by llmsa (exit codes), by CXI (separate parser/authorization/task-quality outcome reporting), and by RFC 9334's own "richer set of Claims" escape hatch — but **nowhere as a formally specified MISSING→INCONCLUSIVE / CONTRADICTORY→REJECT contract over an evaluation-evidence chain.** Ingredient (d), a *freshness epoch / replay ledger* bound to an evaluation attempt, is covered by RFC 9334 §10.3/§12.3 and TUF, but **not** by any of the AI-agent-specific works I found.

---

## 11. Consolidated verdict table (summary)

| # | Claim | Verdict | Single most decisive quote / reason |
|---|---|---|---|
| **1** | arXiv:2606.04990 = survey of AI-agent attestation | **VERIFIED (existence) / REFINED (characterisation)** | Title confirmed: *"From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents"*, Wang et al., 3 Jun 2026, v6 15 Oct 2026. But "evaluator"/"under-bind" appear **0 times**; §7.6 L1939: *"an attested trace can still contain an incorrect inferred edge, so attestation should not be read as evidence of correctness"*; and the survey's own finding (L2660) is that **none** of the surveyed systems attests. |
| **2** | `llmsa` = working open-source LLM-eval attestation chain | **VERIFIED (stronger than claimed)** | `internal/verify/result.go` L4–9: `ExitMissing = 10 / ExitSignatureFail = 11 / ExitDigestMismatch = 12`; ADR-0007 L13: *"A simple pass/fail (0/1) exit code loses information about what went wrong."* Caveat: 2 stars, unpublished; no transparency log; tri-state is stage-level, not claim-level. |
| **3** | arXiv:2603.14332 = agent-governance layer, two theorems | **VERIFIED / REFINED** | Thm 1 (Bounded Divergence) L508: `ϵ ≤ 1 − α1/n`; Thm 2 (Chain Verifiability) L624. But the theorems are about **model-execution reproducibility**, not evaluation-attribution/claim binding. |
| **4** | arXiv:2605.14153 & arXiv:2506.02548 = exploit verifiers with differential oracles | **VERIFIED (differential) / REFINED ("independent" too strong)** | ExploitBench L288: *"These checks depend on the behavior of the ground-truth binary, not on anything the agent reports."* CyberGym L256–257: *"we require that (i) it triggers a sanitizer crash in the pre-patch version and (ii) running it on the post-patch version does not produce any sanitizer crash."* Both oracles are the harness, not an attested third party. |
| **5** | arXiv:2610.16067 = fault injection + known-answer controls + baselines + FAR/FRR | **VERIFIED (method) / terminology corrected** | L556–557: *"the full suite detects 54 of 57"*; L409: *"To measure the suite's own sensitivity and specificity we inject seven defect classes"*. The paper says **sensitivity/specificity**, not FAR/FRR. |
| **6** | preprints 202610.0322 = "Grounded but Wrong", blind claim-specific binding validator, pre-registered ablation, FAR/FRR | **PARTIALLY VERIFIED** | OpenAlex `W7220980858` (HTTP 200) gives the full abstract: *"cuts the run-level binding-defect rate from 28.9% to 2.2% (Holm-corrected p=0.0055)"* — but **"blind" is not stated** ("keyed ground-truth benchmark" is) and **no FAR/FRR is reported**. Title's real third clause is "**in Agentic Statistical Analysis**" (Six Sigma DMAIC, not security). Full text still **NOT-OBTAINABLE** (preprints.org 403 ×5). |
| **7** | in-toto has "unfulfilled" vs "bad" links / tri-state | **PARTIALLY VERIFIED / REFRAMED** | "unfulfilled" appears **0 times** in the spec. But `in_toto/exceptions.py` L30–31 `LinkNotFoundError` (missing, raised verifylib.py:168) vs L17–18 `RuleVerificationError` (bad, raised verifylib.py:949, 981) — a **native library-level missing-vs-bad distinction**. CLI collapses it: `in_toto_verify.py` L22: *"1 if an exception occurred (verification failed)"*. No tri-state verdict object. |
| **8** | SLSA: formats/builders; tri-state; "unsupported provenance" | **VERIFIED / CORRECTED** | "inconclusive" appears **0 times** in every SLSA page fetched. VSA schema: `"verificationResult" : "<PASSED|FAILED>"`. Unsupported ⇒ **hard error** ("This is WIP and currently not supported."). Also: **v1.0 is "Status: Retired"; v1.2 is current.** slsa-verifier has **no** `--max-age`/expiry flag. |
| **9** | RFC 9334 §§8.1, 8.5, 10, 12.2, 12.3 | **VERIFIED — EXACT** | L1244–1247: *"Evidence needs to be securely associated with the Target Environment so that the Verifier cannot be tricked into accepting Claims originating from a different environment (that may be more trustworthy)."* L1843–1844: *"a Verifier can be tricked into accepting Evidence coming from a past epoch as fresh."* Caveat: §8.4 L1299 — the verdict is **binary** ("a boolean value indicating compliance or non-compliance"), so RFC 9334 is *not* prior art for the tri-state. |
| **10** | Real prior work on AI-agent eval provenance / attestation / false attribution | **VERIFIED — domain occupied; no work covers all six** | **Partial Evidence Bench** (arXiv:2605.05379) L142–151: *"The headline failure occurs when the system returns a complete-seeming answer for a materially incomplete task without emitting a correct gap report."* — with `unsafe_completeness_rate` and `blocked_when_safe_to_answer_rate` (L423). Plus CXI (three-way authority join to one manifest), CAVA, HCP, ACE, Agent-Sentry, WeClawArena, llmsa. Best single-work coverage **4/6**; best coverage of (c) and (d) jointly: **none**. |

---

## 12. Corrections Agent 5 should incorporate

1. **§1 row 22 (survey).** The survey finds a *gap* (no attestation anywhere, no benchmark covering the full chain) — it does not occupy the domain. Also: the "supported/unsupported/omitted" quote is the survey reporting *Martin-Boyle et al. (2026)*, not its own taxonomy. The survey's own `Cited`/`Omitted` are *derived predicates* (App. B.5), not a tri-state adjudication.
2. **§1 row 23 (llmsa).** The exit-code separation is in **source code** (`internal/verify/result.go`) and has a **written design rationale** (ADR-0007) — this *strengthens* the prior-art reading. But it is a **2-star, unpublished, single-author project** with **no transparency log** and a **stage-level** (not claim-level) tri-state. Weight accordingly.
3. **§1 row 3 (in-toto reference impl.).** The missing-vs-bad distinction **does** exist — `LinkNotFoundError` vs `RuleVerificationError` in `in_toto/exceptions.py`. §6.1's "may live in a module I did not locate" is resolved. But there is no tri-state *verdict*; the CLI is exit 0/1/2.
4. **§1 row 7 (slsa-verifier freshness).** Upgrade from UNVERIFIED to **CONFIRMED ABSENT** — no `--max-age`/expiry flag exists.
5. **§1 row 12 (ILAC-G8) and row 13 (ISO 19795).** Still **NOT OBTAINED** by me; I did not retry them. Their cells remain secondary.
6. **§2.8 / §7 "the domain is already occupied".** The correct statement is narrower: the domain is *addressed* by a survey that explicitly finds the attestation gap open, by one benchmark that measures the *exact* failure mode (PEB) in a different vertical, and by several runtime-governance systems — but **no work combines (a) a cryptographically independent attested observer, (b) per-claim joins, (c) a tri-state adjudication contract, (d) a freshness epoch bound to the evaluation attempt, (e) per-claim role authorisation, and (f) a non-concealing aggregator** in one specified system for AI-agent *security* evaluation.
7. **§5 / §7 "Category D is refuted by RFC 9334 §8.1".** Confirmed, and I would keep that conclusion — with the precise caveat that RFC 9334's §8.1 is about *environment substitution*, whereas ACTS-Attack's mechanism is *claim-strength promotion*. A reviewer who has read §8.1 will ask for that distinction. It is defensible; it is not the same thing.

## 13. What I could not obtain (explicit NOT-OBTAINABLE list)

| Source | Status | What remains unverified |
|---|---|---|
| **preprints.org 202610.0322 full text** | **NOT-OBTAINABLE** (403 on 5 URL variants; Semantic Scholar 404; arXiv N/A) | Method section, D1–D6 safeguard definitions, blinding protocol, any FAR/FRR table, artifact bundle. Only the **abstract** (via OpenAlex `W7220980858`) was read. |
| **ILAC-G8:09/2019** full PDF | NOT OBTAINED | The "Indeterminate" reporting rules and the false-acceptance/false-rejection framing remain unverified at primary level. |
| **ISO/IEC 19795** standard text | NOT OBTAINED (paywalled) | FAR/FRR definitions for non-biometric security evaluators. |
| **EAT / RFC 9335** | NOT FETCHED | EAT claim types. |
| **RFC 9334 §3.1, §4.1, §7** (role tables) | PARTIAL | I verified §8.1, §8.4, §8.5, §10, §10.3, §12.1.1, §12.2, §12.3. §3.1/§4.1/§7 role/trust-anchor text was located (L412, L703, L1030) but not quoted. |
| **TUF specification** | NOT FETCHED this session | Agent 5's TUF cell (row 8) remains unverified by me. |
| **Sigstore Fulcio / Rekor / sigstore-go** | NOT FETCHED this session | Agent 5's rows 9–11 remain unverified by me. |
| **arXiv:2609.34450, 2605.11086, 2607.18538, 2610.16333** | NOT FETCHED | Agent 5's rows 16, 17, 18, 21 — the identifiers were not re-checked by me. |

---

## 14. Files fetched this session (all under /tmp/opencode/pa/)

| File | Source URL | HTTP |
|---|---|---|
| `pdf_2606.04990.pdf` / `txt_2606.04990.txt` | https://arxiv.org/pdf/2606.04990 | 200 |
| `pdf_2603.14332.pdf` / `txt_2603.14332.txt` | https://arxiv.org/pdf/2603.14332 | 200 |
| `pdf_2605.14153.pdf` / `txt_2605.14153.txt` | https://arxiv.org/pdf/2605.14153 | 200 |
| `pdf_2610.16067.pdf` / `txt_2610.16067.txt` | https://arxiv.org/pdf/2610.16067 | 200 |
| `pdf_2506.02548.pdf` / `txt_2506.02548.txt` | https://arxiv.org/pdf/2506.02548 | 200 |
| `pdf_2605.05379.pdf` / `txt_2605.05379.txt` | https://arxiv.org/pdf/2605.05379 | 200 |
| `rfc9334.txt` | https://www.rfc-editor.org/rfc/rfc9334.txt | 200 |
| `intoto_spec.md` | https://raw.githubusercontent.com/in-toto/docs/master/in-toto-spec.md | 200 |
| `intoto_exceptions.py` | https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/exceptions.py | 200 |
| `intoto_verifylib.py` | https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/verifylib.py | 200 |
| `intoto_in_toto_verify.py` | https://raw.githubusercontent.com/in-toto/in-toto/develop/in_toto/in_toto_verify.py | 200 |
| `llmsa_readme.md` | https://raw.githubusercontent.com/ogulcanaydogan/LLM-Supply-Chain-Attestation/main/README.md | 200 |
| `llmsa_result.go` | .../main/internal/verify/result.go | 200 |
| `llmsa_chain_verify.go` | .../main/internal/verify/chain_verify.go | 200 |
| `llmsa_0007-semantic-exit-codes.md` | .../main/docs/adr/0007-semantic-exit-codes.md | 200 |
| `slsa_*.html` → `txt_slsa_*.txt` | https://slsa.dev/spec/v1.0/, /v1.1/, /v1.2/, /spec/v1.0/verifying-artifacts, /provenance/v1.0, /verification_summary/v1.0 | 200 each |
| `txt_slsa-verifier-README.txt` | https://raw.githubusercontent.com/slsa-framework/slsa-verifier/main/README.md | 200 |
| `arxbatch.xml` | https://export.arxiv.org/api/query?id_list=2605.17169,2607.06000,2603.22868,2605.05379,2606.29073,2607.13716,2609.28915,2608.03499 | 200 |
| `pp_98bf92.out` | https://api.openalex.org/works/doi:10.20944/preprints202610.0322.v1 | 200 |
| `pp_*.out` (403/404 bodies) | preprints.org / doi.org / arxiv.org / semanticscholar | 403 / 404 |

**No file outside `/mnt/nvme5/ACTS-Attack/sp2027/analysis/acts_next_phase_20261019/stage0/AGENT5B_PRIOR_ART_VERIFICATION.md` and `/tmp/opencode/` was created or modified.**
