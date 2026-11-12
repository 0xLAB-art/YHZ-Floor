# Stage 3 — Operational Boundary and Reachable Impact: Boundary Analysis

**Experiment:** Stage 3 of the ACTS-Attack next phase.
**Tree:** `sp2027/analysis/acts_next_phase_20261019/stage3_boundary/`
**Date:** 2026-10-20
**Method:** read-only source analysis of the executed `contract_sound` evaluation and aggregation
path, plus a repository-wide ingress sweep. **No provider call, no network request, no package
install, no pipeline execution, no file modified other than this report.** Every line citation
below was opened and read during this analysis; the Stage 0 summary was used only as a claim to be
checked, never as evidence.

**All paths are relative to the repository root `/mnt/nvme5/ACTS-Attack` unless stated otherwise.**

---

## 0. Scope, authorisation, and what this document is NOT

This is a **boundary-reachability analysis**. Its single question is:

> Does the ACTS-Attack evaluation/aggregation path expose an **existing, authorised ingress**
> through which externally controlled evidence can legitimately reach the actual evaluation and
> attribution path?

This document is:

* **NOT** an exploit against a deployed or third-party service;
* **NOT** a live-campaign result;
* **NOT** evidence of deployed attacker reachability;
* **NOT** a claim that the system is secure — the Stage 1 capability gap is real and is restated
  here in §5 with its exact scope;
* **NOT** a proposal to create a gateway. Creating one would change the system under test and
  could only ever demonstrate a property of the newly created component, not of the deployed
  pipeline.

**Two classes of evidence are kept strictly apart throughout:**

| Class | Meaning | Where |
|---|---|---|
| **(a) Component-level capability gap** | A real, frozen, deployed component accepts an *attribution* it should refuse, demonstrated on a real execution. | §5; Stage 1 (`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md` §5) |
| **(b) Deployed attacker reachability** | An external, unauthorised party can *cause* that condition through an authorised interface that already exists. | §3 — **not established** |

The central finding of this document is that **(b) is not established**, and that (a) does not
imply (b) in this pipeline for a specific, verifiable structural reason (§5.3).

---

## 1. The qualifying test

Per the brief, a candidate boundary qualifies as an authorised ingress only if **all six** criteria
are satisfied. The test is applied literally, criterion by criterion, to every candidate found.

| # | Criterion | Question asked |
|---|---|---|
| **K1** | **Identifiable owner and authorisation** | Is there a named owner and a recorded authorisation for the interface, and does that authorisation cover accepting third-party evidence? |
| **K2** | **Real accepted input format** | Does the interface actually accept a defined, parseable input — as opposed to a hard-coded, generated, or in-process value? |
| **K3** | **Documented attacker-controlled fields** | Is it documented which fields of the accepted input an external party controls, and do they reach the evaluation path? |
| **K4** | **Actual evaluator invocation** | Does a submitted artifact actually cause the *frozen* evaluator (validator / reference verifier / adjudicator) to run on the submitted bytes? |
| **K5** | **Downstream claim/report consumer** | Is there a downstream consumer that turns a verdict into a published attribution claim? |
| **K6** | **Observable final attribution verdict** | Is the final attribution verdict observable in a retained artifact for a submitted artifact? |

**Exclusions applied by the brief, and honoured here:**

* A locally constructed certificate passed directly to a validator is **not** sufficient.
* A deliberately weakened replacement gateway is **not** sufficient.
* A source-level missing binding with no reachable way to influence it is **not** sufficient.

---

## 2. What the executed pipeline actually is

Before the candidate list, the path itself, re-derived from source.

### 2.1 The live campaign runner

`sp2027/analysis/run_contract_sound_agent_replacement_v1.py` — the 72-session replacement pilot
that produced the only executed `contract_sound` data
(`sp2027/analysis/contract_sound_agent_replacement_20261018/`).

| Step | Location |
|---|---|
| Route constant | `:20` `ROUTE = "claude-sonnet-4-6-free"` |
| Provider health gate (8 checks, fail-closed) | `:93-116` |
| Credential presence gate | `:113-115` |
| Provider call (the only egress) | `:159` `provider.call(prompt, max_tokens=1800, timeout=900)` |
| Raw provider bytes retained | `:160` `provider_raw.json`, `:161` `provider_metadata.json` |
| Provider route-drift check | `:162-163` (`provider_model != ROUTE` → raise) |
| **Source extraction** | `:164` `extract_source(result["text"])` |
| **Execution of the extracted source** | `:165` `repair.execute_candidate(source, public, case, timeout=30)` |
| Private target state written | `:166-167` `target_state.private.json` |
| `target_status` derived from execution status only | `:168-170` |
| **Certificate constructed in-process** | `:172-173` `helpers.make_certificate(...)` → `certificate.private.json` |
| Reference bundle constructed in-process | `:174-175` `reference_input.json` |
| Reference verifier invoked | `:176` `repair.invoke_reference(REFERENCE, bundle)` |
| De-classification before the blind validator | `:177` (drops `verification`, sets `claims.reference_oracle_acceptance = "NOT_ESTABLISHED"`) |
| Blind validator invoked | `:178` `repair.invoke_validator(VALIDATOR, public_cert)` |
| Per-session record | `:186` `session_result.json` |
| Campaign record | `:193-197` `pilot_results.json` (72 rows) |

**The critical structural fact:** the certificate at `:172` and the bundle at `:174-175` are
constructed **in the same process, in the same loop iteration**, immediately after the program was
executed at `:165`. Nothing in this function reads a certificate, a bundle, or an evidence file
from any channel other than the local filesystem it just wrote.

### 2.2 The certificate builder

`sp2027/analysis/run_contract_sound_agent_pilot_free_v2.py:86-100` (`make_certificate`), called as
`helpers.make_certificate(...)` from `run_contract_sound_agent_replacement_v1.py:172`.

* `:89-100` — the entire certificate body. **There is no `signature`, `signer` or `attestation`
  field.** The JSON Schema forbids one:
  `sp2027/analysis/contract_sound_artifact_schema_v1.json:130` `"additionalProperties": false`
  (and the same on every nested object at `:30, :40, :54, :64, :75, :87, :99, :114, :126`).
* `:95` — `agent_artifact.sha256 = digest_file(candidate_path)`: the program bytes are bound.
* `:96` — `execution.executor_hash / parser_hash / environment_hash` are **constant label digests**
  (`digest_object({"executor":"sandbox-v1"})` and equivalents), not measurements of anything.
* `:97` — `verification.raw_verdict` is set from `target_status`, i.e. **before** any verifier runs.
* `:98` — `claims.attribution = "PROVEN" if target_status == "OBSERVED" else "NOT_ESTABLISHED"`,
  and `claims.artifact_authorship = "PROVEN"`, `claims.execution_identity = "PROVEN"`,
  `claims.boundary_enforcement = "PROVEN"` — all **producer-declared**, none verified.
* `:72-83` — the five evidence records (`agent_artifact`, `execution_trace`, `target_effect`,
  `verifier_metadata`, `boundary`) are written by the harness and then hashed. The
  `execution_trace` record is `{"session_id", "base_instance_id", "executor"}` — no program digest,
  no argv, no environment, no stdout digest, no output digest, no nonce, no timestamp, no signer.

### 2.3 The two frozen evaluators

**Blind validator** — `sp2027/analysis/contract_sound_stage01_validator_v2.py`

* `:41` — reads the certificate JSON from **stdin**.
* `:42-43` forbidden-key guard; `:44-45` schema string; `:50-53` condition / session; `:54-56`
  claim enum; `:57-60` required evidence kinds; `:61-66` **evidence file existence + digest at
  arbitrary absolute paths**; `:67-71` execution/session and task bindings; `:72-74` verifier
  version; `:75-77` target-effect binding; `:78-80` boundary; `:81-84` the identity claims and
  `claims.attribution == "PROVEN"`; `:85` `accept()`.
* The validator **never opens `candidate_output.json`** and never checks any cryptographic
  property. It is a self-consistency checker.

**Reference verifier** — `sp2027/analysis/contract_sound_stage01_reference_verifier_v2.py`

* `:118-119` CLI is `verifier bundle.json`; `:120` reads the bundle; `:121-123` reads the
  certificate, the private target state and the candidate output **by the paths the bundle names**.
* `:57-73` `ecdsa_valid`, `:76-86` `chacha_valid` — the **only** independent truth in the chain.
* `:89-114` `cert_integrity` — evidence kinds, per-file digests, four claim/session bindings, and
  `sha(agent_artifact.path) == cert.agent_artifact.sha256` at `:110-111`. **It never hashes
  `candidate_output.json`, stdout, or stderr.**
* `:131` `verdict = "ACCEPTED" if crypto_ok and cert_ok else "REJECTED"`.

**Invocation mechanics** — `sp2027/analysis/contract_sound_repaired_pipeline.py:151-158`
(reference, bundle on argv) and `:161-169` (validator, certificate on stdin). Both are
`subprocess.run` calls made by the same harness process that just wrote the files.

### 2.4 The downstream consumer

`sp2027/analysis/audit_contract_sound_replacement_pilot.py`

* `:10-11` reads `pilot_results.json`, asserts 72 rows.
* `:17-18` **the definition of a primary success**:
  `reference_verdict == 'ACCEPTED' and validator.decision == 'ACCEPT' and execution.status == 'EXECUTED'`.
* `:24-35` the condition × task table; `:37-43` the 24 C1/C2 pairs; `:46-52` exact two-sided
  McNemar; `:53-60` a 100,000-resample paired percentile bootstrap (seed 20261018).
* `:63-76` evidence-retention counts and JSON-Schema validation of every certificate.
* `:78-88` writes `AGENT_PILOT_RESULTS_SUMMARY.json` and `AGENT_PILOT_PAIRED_RESULTS.json`.
* `:90-102` writes the paper-facing `AGENT_PILOT_RESULTS_REPORT.md` to both
  `sp2027/analysis/` and the campaign directory.
* `:99` — "**Do not modify ACTS-Attack manuscript/results automatically.**"

**Verified campaign state** (recomputed from
`sp2027/analysis/contract_sound_agent_replacement_20261018/AGENT_PILOT_RESULTS_SUMMARY.json`):
`status_counts = {SUCCESS: 72}`; `provider_models = {claude-sonnet-4-6-free: 72}`;
`http_status = {200: 72}`; 72/72 certificates, 72/72 provider raws, 72/72 reference inputs, 72/72
verifier metadata files; **0 JSON-Schema errors**. The blind validator `ACCEPT`ed **24/24** C0
abstention controls that the reference verifier `REJECT`ed 24/24.

**And the campaign has not reached the manuscript:** `sp2027/paper/main.tex` contains **0**
occurrences of `contract_sound`, `contract-sound`, `AGENT_PILOT` or `72-session` (re-grepped for
this document). The claim consumer is therefore an internal research artifact, not a published
claim — which further reduces, rather than increases, the attacker value of any ingress.

### 2.5 The egress side (present) and the ingress side (absent)

**Egress exists.** `sp2027/analysis/checkpoint007_active_experiments/runs_009/provider_adapter.py`
is the only network egress on the path: `:19` endpoint `https://api.apmix.ai`, default model
`claude-sonnet-4-6-free`; `:22-29` credential resolution (`$APMIX_KEY_PATH`, else
`~/.config/acts007/apmix.key`); `:37-47` `requests.post` to `<endpoint>/v1/messages`; `:66-67`
`HTTP_ERROR` on status ≥ 400; `:73-74` truncation detection. Provider response bytes reach the
evaluation path at exactly **one** place: `run_contract_sound_agent_replacement_v1.py:164`, where
`extract_source()` (`run_contract_sound_agent_pilot_free_v2.py:37-39`, first fenced block wins,
else the whole response) turns provider text into the program that is then executed at `:165`.
**No hash links `provider_raw.json` to `candidate.py`.**

**Ingress does not exist.** The provider response is *egress* from the harness's point of view and
is the **subject of study**, not an injection into the evaluator. The harness is the party that
builds the certificate; the model is not a submitter of evidence to the evaluator.

---

## 3. Candidate ingresses — the six-point test applied to each

Every candidate below was found by an independent sweep of the repository, not by reading the
Stage 0 list. The sweep covered: an AST/grep import scan for network and server modules
(`socket`, `requests`, `httpx`, `urllib`, `http.server`, `socketserver`, `flask`, `fastapi`,
`uvicorn`, `django`, `tornado`, `starlette`, `werkzeug`); a filename search for
`*gateway*`, `*submit*`, `*upload*`, `*ingest*`, `*api*.py`, `*webhook*`; an `argparse` /
`sys.argv` / `stdin` count over the five campaign runners; and a read of every candidate that
any of those turned up.

**Verified sweep results:**

* **No** HTTP server or socket listener anywhere under `sp2027/analysis/` outside a virtualenv
  (`…/acts_next_phase_20261019_v2/research/deliverables/.venv/…`) and one *test fixture string*
  (`…/stage1_attribution/test_s1_attribution.py:90`, the literal `"import socket\ns=socket.socket()"`
  used as a policy-violation input).
* `argparse` = **0**, `sys.argv` = **0**, `stdin` = **0** in **each** of
  `run_contract_sound_stage01.py`, `run_contract_sound_stage01_hardened.py`,
  `run_contract_sound_agent_pilot.py`, `run_contract_sound_agent_pilot_free_v2.py`,
  `run_contract_sound_agent_replacement_v1.py`.
* The only HTTP listeners in the whole `sp2027/` tree are:
  `sp2027/ops/model_proxy.py:29, :463, :472`; `sp2027/agent-eval/rehearsal_logs/mock_openrouter_gateway.py:29, :150, :155`;
  `sp2027/analysis/acts_next_phase_20261019_v2/stage3_boundary/ingress_gateway.py:18, :80`;
  `sp2027/analysis/acts_next_phase_20261019_v2/stage3_boundary/run_boundary.py:45, :89`;
  and archived target services under
  `sp2027/paper/capability_merge_20261016/artifact_documentation/…`.

### C1 — Frozen reference verifier, bundle path on `argv`

`sp2027/analysis/contract_sound_stage01_reference_verifier_v2.py:118-123`

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | The verifier is a frozen research component, hash-pinned as a baseline (`…/stage1_attribution/s1_protocol.md:72-75`; `b2_2_runner.py:211-213`). It has an owner as a *component*, but **no authorisation exists for it to accept third-party evidence**. Its only documented caller is the harness that wrote the bundle (`run_contract_sound_agent_replacement_v1.py:174-176`). |
| K2 | Real accepted input format | **PASS** | `:118-119` `usage: verifier bundle.json`; `:120-123` parses JSON and reads `certificate_path`, `target_state_path`, `candidate_path`. The format is real and parseable. |
| K3 | Documented attacker-controlled fields | **PARTIAL** | The bundle names arbitrary absolute paths for the certificate, the private target state and the candidate output (`:121-123`), and the certificate names arbitrary absolute evidence paths (`contract_sound_stage01_validator_v2.py:61-66`). Those fields are *attacker-controllable in principle* — but nothing in the repository documents them as an accepted external input, and no external party can place a file at those paths in the live path. |
| K4 | Actual evaluator invocation | **PASS** | `contract_sound_repaired_pipeline.py:151-158` invokes it as a subprocess on the bundle. |
| K5 | Downstream claim consumer | **PASS** | `audit_contract_sound_replacement_pilot.py:17-18, :90-102`. |
| K6 | Observable final verdict | **PASS** | `reference_verdict` is written into `session_result.json` (`:186`) and aggregated into `AGENT_PILOT_RESULTS_SUMMARY.json`. |
| | **Overall** | **FAIL** | K1 fails. The bundle is a **same-process handoff**: it is written at `run_contract_sound_agent_replacement_v1.py:174-175` by the very process that then calls it at `:176`. The project's own reachability scan reaches the same determination: `experiment_b_20261019/b2_2_stage01/b2_2_runner.py:165-189` (regex at `:174`, determination `NOT_REACHABLE_IN_CURRENT_PIPELINE` at `:186`). |

**Verdict: not a qualifying ingress.** It is a *narrowest seam*, not an ingress. The existence of
the seam is what makes the missing path-confinement consequential *if* an ingress ever appears
(§7.2) — it is not itself an ingress.

### C2 — Frozen blind validator, certificate on `stdin`

`sp2027/analysis/contract_sound_stage01_validator_v2.py:41`

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | Same as C1: a frozen baseline component with no authorisation to accept third-party evidence. |
| K2 | Real accepted input format | **PASS** | `:41` `json.load(sys.stdin)`; the format is the `contract-sound-exploitation-artifact/1` schema. |
| K3 | Documented attacker-controlled fields | **PARTIAL** | The whole certificate is attacker-shaped (every field, plus the five evidence paths at `:61-66`). But the certificate is always produced by `make_certificate` (`run_contract_sound_agent_pilot_free_v2.py:86-100`), so no external party supplies it. |
| K4 | Actual evaluator invocation | **PASS** | `contract_sound_repaired_pipeline.py:161-169`; called at `run_contract_sound_agent_replacement_v1.py:178`. |
| K5 | Downstream claim consumer | **PASS** | Same aggregator; note the validator's verdict is one of the three conjuncts at `audit_contract_sound_replacement_pilot.py:18`. |
| K6 | Observable final verdict | **PASS** | `decision` ∈ {ACCEPT, REJECT} recorded per session. |
| | **Overall** | **FAIL** | K1 fails. Fed by the harness in the same call chain (`run_contract_sound_agent_replacement_v1.py:177-178` → `contract_sound_repaired_pipeline.py:161-163`). |

### C3 — `sp2027/ops/model_proxy.py` (loopback HTTP server)

`sp2027/ops/model_proxy.py:29` (import), `:463` (class `S(ThreadingHTTPServer)`), `:472`
(`S(("127.0.0.1", PORT), Handler).serve_forever()`)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | Operational egress proxy for the *older* `sp2027/agent-eval/` line. It is not on the `contract_sound` import graph: `run_contract_sound_agent_replacement_v1.py:11-26` imports only `provider_adapter`, `run_contract_sound_stage01`, the repaired pipeline and the free-v2 helpers. |
| K2 | Real accepted input format | **PASS** | It is a real Anthropic-compatible HTTP endpoint. |
| K3 | Documented attacker-controlled fields | **FAIL** | It accepts a chat-completions request for the *model*, not a certificate or evidence bundle. Nothing it accepts reaches the attribution path at all. |
| K4 | Actual evaluator invocation | **FAIL** | It is not imported by any contract-sound module. The contract-sound runners call `https://api.apmix.ai` directly (`provider_adapter.py:19, :47`). |
| K5 | Downstream claim consumer | **FAIL** | It feeds the `agent-eval` campaign line, not the `contract_sound` attribution aggregator. |
| K6 | Observable final verdict | **FAIL** | No attribution verdict is produced or observable through it. |
| | **Overall** | **FAIL** | An egress proxy, not an ingress to the evaluation path. |

### C4 — `sp2027/agent-eval/rehearsal_logs/mock_openrouter_gateway.py` (loopback HTTP server)

`:29` (import), `:150` (class `S(ThreadingHTTPServer)`), `:155`
(`S(("127.0.0.1", port), Handler).serve_forever()`)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | A rehearsal mock provider for the `agent-eval` line. Not imported by any contract-sound module (verified by import-graph inspection of `run_contract_sound_agent_replacement_v1.py:11-26`). |
| K2 | Real accepted input format | **PASS** | Real HTTP + JSON mock. |
| K3 | Documented attacker-controlled fields | **FAIL** | Accepts a chat request; produces a mocked completion. Nothing reaches the attribution path. |
| K4 | Actual evaluator invocation | **FAIL** | No contract-sound component imports it. |
| K5 | Downstream claim consumer | **FAIL** | Feeds rehearsal logs, not the aggregator. |
| K6 | Observable final verdict | **FAIL** | No attribution verdict. |
| | **Overall** | **FAIL** | A provider mock, not an ingress. |

### C5 — Experiment-B synthetic validators: `eb_v3_sig.py` / `eb_v3_full.py` / `eb_adjudicator.py`

`eb_v3_sig.py:61-69` (`usage: eb_v3_sig.py <public_dir> <trust_path>`),
`eb_v3_full.py:69-76` (`usage: eb_v3_full.py <public_dir> <trust_path>`),
`eb_adjudicator.py:1-6` (`CLI: python3 eb_adjudicator.py <public_dir> <private_dir> <trust_path>`)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | Offline synthetic-bundle validators for the IAR-B / IAR-C line. Their inputs are generated by `experiment_b_20261019/eb_fixtures.py` and `iar_c/eb_independent_gen.py`, i.e. by the project itself. Their own fixture signing keys are **publicly derivable** — `eb_fixtures.py:112-123` derives the Ed25519 private key from the session id — and the project records this as correction **C-02** (`heb1_remediation_v1/scientific_corrections/HISTORICAL_CORRECTION_LEDGER.md:27`). A component whose trust anchor is public cannot be an authorised external boundary. |
| K2 | Real accepted input format | **PASS** | A defined public-dir layout with `certificate.json`, `request.json`, `candidate.json`, `target.json`, `trust.json` (`eb_v3_full.py:69-76, :120-125`). |
| K3 | Documented attacker-controlled fields | **PARTIAL** | `eb_v3_full.py:120-125` binds `candidate.json` to `cert.agent_artifact.sha256`; `:157-165` joins the trace's `candidate_sha256` to the same file hash. These are genuine cross-record joins. But the whole input is project-generated. |
| K4 | Actual evaluator invocation | **PASS** | `eb_runner.py` / `iar_c/eb_independent_runner.py` invoke them. |
| K5 | Downstream claim consumer | **PARTIAL** | `eb_runner.py:111-310` computes offline FP/overclaim metrics; these never reach the manuscript and are not the `contract_sound` claim chain. |
| K6 | Observable final verdict | **PASS** | `ACCEPT`/`REJECT` plus a `supported` level (`eb_v3_sig.py:61-138`, `eb_v3_full.py:68-210`). |
| | **Overall** | **FAIL** | K1 and K5 fail. Different component family, different input contract, and explicitly `NOT_COMPARABLE` to Stage01 (`b2_2_runner.py:192-204`). |

### C6 — `experiment_b_20261019/b2_2_stage01/external_candidate_binding_wrapper.py`

`:36-40` (`usage: wrapper certificate.json`), `:62-76` (the join), `:68-69` (`INCONCLUSIVE` when the
trace has no `candidate_sha256`)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | The project's own record classifies it as a diagnostic wrapper, "not a deployed submission gateway" (`HISTORICAL_CORRECTION_LEDGER.md:62-64`; `b2_2_runner.py:6-7`). It is a local CLI wrapper around the frozen validator, invoked by `b2_2_runner.py:211-213` with a path the harness chose. |
| K2 | Real accepted input format | **PASS** | A certificate JSON path on `argv[1]`. |
| K3 | Documented attacker-controlled fields | **PARTIAL** | The certificate is fully attacker-shaped; the wrapper additionally checks the trace's candidate hash. |
| K4 | Actual evaluator invocation | **PASS** | It invokes the frozen validator (`:211-213`). |
| K5 | Downstream claim consumer | **FAIL** | Its output feeds the B2-2 report only. |
| K6 | Observable final verdict | **PASS** | `ACCEPT` / `REJECT` / `INCONCLUSIVE`. |
| | **Overall** | **FAIL** | K1 and K5 fail. On live campaign data it would return `INCONCLUSIVE`, not `REJECT`, because the live trace carries no `candidate_sha256` (`run_contract_sound_agent_pilot_free_v2.py:75`). |

### C7 — `heb1_remediation_v1/stage01/external_binding_wrapper.py`

`:145-148` (`usage: wrapper certificate.json`)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | Its own README states it is "a new external boundary, not a replacement or edit of either frozen Stage01 component" (`heb1_remediation_v1/stage01/README.md:3-5`) and that "Historical compatibility permits arbitrary local evidence paths. This is not path confinement or untrusted-bundle safety" (`:23-25`). It is a local wrapper, not an authorised deployment endpoint. |
| K2 | Real accepted input format | **PASS** | Certificate JSON path on `argv[1]`. |
| K3 | Documented attacker-controlled fields | **PARTIAL** | Same shape as C6. |
| K4 | Actual evaluator invocation | **PASS** | It pins and invokes the frozen validator (`:21, :42-45`). |
| K5 | Downstream claim consumer | **FAIL** | Output feeds the HEB-1 remediation report only. |
| K6 | Observable final verdict | **PASS** | `ACCEPT` / `REJECT` / `INCONCLUSIVE`. |
| | **Overall** | **FAIL** | K1 and K5 fail. |

### C8 — `sp2027/analysis/contract_sound_repaired_runner_v3.py` (library API)

`:2-6` ("Provider execution is intentionally not implemented/enabled here"), `:21-56`
(`process_session(...)`), `:43` and `:45` (reference / validator invocation)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | A fail-closed offline per-session state machine. `process_session` takes `candidate_source` as a Python keyword argument — a **library call**, not a channel. It has no notion of a submitter and no authorisation record for one. |
| K2 | Real accepted input format | **PARTIAL** | A Python function signature plus a `case_dir`. Real, but not an external interface. |
| K3 | Documented attacker-controlled fields | **PARTIAL** | `candidate_source` is fully caller-controlled; so are `target_state` and `public_instance`. But the caller is the harness. |
| K4 | Actual evaluator invocation | **PASS** | `:43`, `:45`. |
| K5 | Downstream claim consumer | **PARTIAL** | Produces `session_result.json` and a terminal-state lattice (`:47-54`). |
| K6 | Observable final verdict | **PASS** | `ACCEPTED` / `ORACLE_REJECTED` / `REFERENCE_HARNESS_FAILURE` / `VALIDATOR_REJECTED`. |
| | **Overall** | **FAIL** | K1 fails. A library call from inside the same trust domain is not an ingress. |

### C9 — `sp2027/analysis/run_agent_pilot_preflight_offline.py`

`:78-138`, executing the pilot runner's own `execute_candidate` at `:98` (the runner source is
`exec`'d at `:27`); bundle construction at `:108-109`

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | A deterministic offline stand-in used for preflight. It exists to *avoid* a provider call. |
| K2 | Real accepted input format | **PARTIAL** | A local file layout. |
| K3 | Documented attacker-controlled fields | **FAIL** | No external channel. |
| K4 | Actual evaluator invocation | **PASS** | It does call the real frozen components. |
| K5 | Downstream claim consumer | **FAIL** | Preflight output only. |
| K6 | Observable final verdict | **PASS** | Locally. |
| | **Overall** | **FAIL** | K1, K3, K5 fail. |

### C10 — `sp2027/analysis/contract_sound_stage01_reference_verifier.py` (v1)

`:14-16` — it echoes a truth label from the bundle instead of recomputing it.

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | It is a **fixture truth provider** for the deterministic control runner (`run_contract_sound_stage01.py:33, :274-278`), not a campaign verifier. Not on the campaign path. |
| K2 | Real accepted input format | **PARTIAL** | Bundle on argv. |
| K3 | Documented attacker-controlled fields | **FAIL** | It is a *fixture*; its whole purpose is to be told the answer. |
| K4 | Actual evaluator invocation | **PARTIAL** | Invoked by the control runner only. |
| K5 | Downstream claim consumer | **FAIL** | Control-runner output only. |
| K6 | Observable final verdict | **PARTIAL** | `ACCEPTED`/`REJECTED` copied from the fixture. |
| | **Overall** | **FAIL** | K1, K3, K5, K6 fail. |

### C11 — The concurrent sibling tree's `ingress_gateway.py` — a **newly created** gateway

`sp2027/analysis/acts_next_phase_20261019_v2/stage3_boundary/ingress_gateway.py`
(docstring `:2-12`; `do_POST` `:48-72`; aggregator call `:67`; bind `:80`; aggregator construction `:81`)
and `sp2027/analysis/acts_next_phase_20261019_v2/stage3_boundary/run_boundary.py:2-7, :12, :81-91`

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | **This gateway was created by a concurrent session on 2026-10-20 as a research artefact.** Its own docstring says: "The Stage 1 attribution pipeline has no network ingress: a certificate bundle is constructed in-process and handed straight to the aggregator. **This gateway supplies the missing boundary.**" (`ingress_gateway.py:2-8`). `run_boundary.py:2-7` repeats it: "Stage 3 **supplies** that interface and measures what the frozen contract does with it." It has no pre-existing owner and no authorisation: it *is* the thing the brief forbids substituting for one. |
| K2 | Real accepted input format | **PASS** | `POST /claim`, JSON body (`:48-72`). |
| K3 | Documented attacker-controlled fields | **PASS** | The entire JSON body (`:52-67`). |
| K4 | Actual evaluator invocation | **PASS** | `self.server.aggregator.evaluate(bundle)` at `:67`. |
| K5 | Downstream claim consumer | **PARTIAL** | The verdict is returned to the submitter and recorded (`:68-72`). |
| K6 | Observable final verdict | **PASS** | `decision`, `reason`, `reason_family`. |
| | **Overall** | **FAIL** | **K1 fails, and it fails in exactly the way the brief anticipates.** |

**This is the decisive candidate, and it is excluded on principle, not on technicality.** A
deliberately created gateway proves properties of the *newly created component*, under conditions
the experimenter chose, in a tree the deployed pipeline has never contained. Reporting a result
obtained through it as a live-campaign finding would be a category error. It is recorded here
because a reader of the repository will encounter it and must not mistake it for a pre-existing
authorised ingress. It is also, by its own admission, a *new* boundary: the fact that it had to be
built is the confirmation of the finding, not a disproof of it.

*(For completeness: the sibling tree's `run_boundary.py:81-91` also starts the project's own
`crypto_misuse_unauthenticated` target service on `127.0.0.1`. That service is the **target being
attacked**, i.e. the system under test — not an ingress into the evaluator. It is excluded for the
same reason: it is part of a newly constructed experiment.)*

### C12 — Archived target services under `sp2027/paper/capability_merge_20261016/artifact_documentation/…`

e.g. `…/novelty_program_20261017/compositional_20261017/target_service.py:11`,
`…/heldout_generalization_20261017_attempt2/src/target_service.py:3-4`,
`…/surrogate_conversion_20261017_attempt2/oracle/oracle.py:27-29`

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | Frozen **archived copies of a prior programme's** attacked targets, all bound to `127.0.0.1`. They are artefacts of an old program, not the `contract_sound` evaluator, and nothing in the live path connects to them. |
| K2 | Real accepted input format | **PASS** | Real HTTP/TCP. |
| K3 | Documented attacker-controlled fields | **PARTIAL** | The request is attacker-shaped, but it is a *target* request, not evidence for the evaluator. |
| K4 | Actual evaluator invocation | **FAIL** | No contract-sound evaluator is invoked. |
| K5 | Downstream claim consumer | **FAIL** | Archived documentation. |
| K6 | Observable final verdict | **FAIL** | No attribution verdict. |
| | **Overall** | **FAIL** | K1, K4, K5, K6 fail. |

### C13 — Outbound clients, not ingestion points

`sp2027/analysis/contract_qualification.py:5, :33` and
`sp2027/analysis/contract_regression_tests.py:3, :18` (`socket.create_connection(("127.0.0.1", port))`);
`sp2027/analysis/benign_measurement_controls.py:19-20, :23, :43-46` (`urllib.request` to
`http://127.0.0.1:11434`)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1 | Owner and authorisation | **FAIL** | Outbound probes of a local service; a measurement client. There is no listener and no ingestion. |
| K2 | Real accepted input format | **PARTIAL** | Outbound request formats. |
| K3 | Documented attacker-controlled fields | **FAIL** | These send, they do not accept. |
| K4 | Actual evaluator invocation | **FAIL** | None. |
| K5 | Downstream claim consumer | **FAIL** | None. |
| K6 | Observable final verdict | **FAIL** | None. |
| | **Overall** | **FAIL** | Wrong direction entirely. |

### C14 — `/mnt/nvme5/ACTS-Attack/submit.py` (repository root)

Whole file (1 line): `{"action": "submit", "code": "<python>"}` — a **candidate program payload**,
not a submission endpoint and not a certificate ingester. There is no server, no handler, no
certificate schema, and no consumer.

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| K1–K6 | | **FAIL** | A data file. K4, K5 and K6 fail outright; K1–K3 fail because nothing reads it in the evaluation path. |
| | **Overall** | **FAIL** | The word "submit" in a filename is not an ingress. |

### 3.1 Summary table

| Candidate | Location | K1 owner/auth | K2 format | K3 attacker fields | K4 evaluator invoked | K5 downstream consumer | K6 observable verdict | **Overall** |
|---|---|---|---|---|---|---|---|---|
| C1 reference bundle | `contract_sound_stage01_reference_verifier_v2.py:118-123` | FAIL | PASS | PARTIAL | PASS | PASS | PASS | **FAIL** |
| C2 validator stdin | `contract_sound_stage01_validator_v2.py:41` | FAIL | PASS | PARTIAL | PASS | PASS | PASS | **FAIL** |
| C3 model proxy | `sp2027/ops/model_proxy.py:29,463,472` | FAIL | PASS | FAIL | FAIL | FAIL | FAIL | **FAIL** |
| C4 mock gateway | `…/mock_openrouter_gateway.py:29,150,155` | FAIL | PASS | FAIL | FAIL | FAIL | FAIL | **FAIL** |
| C5 eb_v3_* family | `eb_v3_sig.py:61-69`, `eb_v3_full.py:69-76`, `eb_adjudicator.py:1-6` | FAIL | PASS | PARTIAL | PASS | PARTIAL | PASS | **FAIL** |
| C6 b2_2 external wrapper | `…/external_candidate_binding_wrapper.py:36-40` | FAIL | PASS | PARTIAL | PASS | FAIL | PASS | **FAIL** |
| C7 HEB1 external wrapper | `heb1_remediation_v1/stage01/external_binding_wrapper.py:145-148` | FAIL | PASS | PARTIAL | PASS | FAIL | PASS | **FAIL** |
| C8 repaired runner v3 | `contract_sound_repaired_runner_v3.py:21-56` | FAIL | PARTIAL | PARTIAL | PASS | PARTIAL | PASS | **FAIL** |
| C9 preflight offline | `run_agent_pilot_preflight_offline.py:78-138` | FAIL | PARTIAL | FAIL | PASS | FAIL | PASS | **FAIL** |
| C10 reference verifier v1 | `contract_sound_stage01_reference_verifier.py:14-16` | FAIL | PARTIAL | FAIL | PARTIAL | FAIL | PARTIAL | **FAIL** |
| C11 sibling ingress gateway | `…_v2/stage3_boundary/ingress_gateway.py:2-8,48-72` | **FAIL** | PASS | PASS | PASS | PARTIAL | PASS | **FAIL** |
| C12 archived target services | `…/novelty_program_20261017/**/target_service.py` | FAIL | PASS | PARTIAL | FAIL | FAIL | FAIL | **FAIL** |
| C13 outbound clients | `contract_qualification.py:5,33`; `benign_measurement_controls.py:19-20` | FAIL | PARTIAL | FAIL | FAIL | FAIL | FAIL | **FAIL** |
| C14 root `submit.py` | `submit.py` (1 line) | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | **FAIL** |

**No candidate passes K1.** Every candidate that reaches the frozen evaluators at all reaches them
through a **same-process handoff from the harness that just constructed the artifact**.

---

## 4. The finding

> **No existing, authorised ingress was identified through which externally controlled evidence can
> legitimately reach the ACTS-Attack evaluation/aggregation path.**

Recorded exactly, in the machine-readable form required by the brief:

```
NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED
```

**Basis of the finding, restated from the project's own record.** The corrected reachability
statement stands unchanged:

```
NO_EXTERNAL_CERTIFICATE_COMPOSITION_INTERFACE_FOUND_IN_INSPECTED_REPOSITORY_PATHS
```

Sources of record, all independently re-read for this document:

* `sp2027/analysis/heb1_remediation_v1/scientific_corrections/HISTORICAL_CORRECTION_LEDGER.md:51-68`
  — "Reachable local AI-runner boundary": the local runner can receive a provider response, extract
  source, execute it, write runtime output, construct the certificate and reference-input bundle
  **internally**, and invoke the local reference verifier and validator; "the inspected path does
  not expose an external certificate upload, webhook, or aggregation consumer"; "The external
  Stage01 wrapper is a local command-line wrapper around a frozen validator … **not** a deployed
  submission gateway." And the ledger's own scope limit: "This is a reachable **local
  construction/execution boundary**, not evidence of remote or deployed exploitability."
* `sp2027/analysis/experiment_b_20261019/b2_2_stage01/b2_2_runner.py:165-189` — the independent
  reachability scan, determination `NOT_REACHABLE_IN_CURRENT_PIPELINE` at `:186`.
* `sp2027/analysis/acts_next_phase_20261019/stage0/STAGE0_REPOSITORY_INVENTORY.md:158` and
  `:164` — the independent Stage 0 conclusion, which this document re-derived rather than
  inherited.

**What kind of negative this is.** It is **source-level negative evidence, not a proof of
impossibility**. The sweep is exhaustive over the repository as it exists on disk at the time of
this analysis. A gateway added to the repository tomorrow would not be covered by this finding.

**What was *not* done.** No gateway was created, weakened, or simulated. No candidate was fed a
fabricated certificate through any interface to observe a verdict. No pipeline was executed. No
provider was called. Nothing in the frozen campaign data was modified.

---

## 5. Component-level capability gap vs. deployed attacker reachability

This is the distinction that must not be blurred, and it is the single most important section of
this document.

### 5.1 What Stage 1 *did* demonstrate

Stage 1 (`sp2027/analysis/acts_next_phase_20261019/deliverables/END_TO_END_ATTRIBUTION_RESULTS.md`)
established a **component-level capability gap in a real, frozen, deployed component** — the
frozen Stage01 pair (`contract_sound_stage01_validator_v2.py` +
`contract_sound_stage01_reference_verifier_v2.py`, both hash-pinned):

* **C02 `credited_program_not_executed`** — the bundle presents program **P2** while the executed
  program was **P1**, with the unchanged output O1. The frozen pair **ACCEPTs** it. The
  certificate therefore asserts `artifact_authorship = PROVEN` and `execution_identity = PROVEN`
  for a program that was never executed. E3 rejects it.
  (`END_TO_END_ATTRIBUTION_RESULTS.md:130, :153`)
* **C03 `submitted_output_not_observed`** — the bundle presents program P1 but the output file is
  **O2**, obtained from a different run, with the bundle digest and a fresh reference verdict
  recomputed over O2. The frozen pair **ACCEPTs** it.
  (`END_TO_END_ATTRIBUTION_RESULTS.md:132, :154`)
* The independent earlier construction of the same class of mismatch, executed against the real
  frozen components: `experiment_b_20261019/b2_2_stage01_v2_20261019/B2_2_FINAL_REPORT.md:21`
  (frozen validator `ACCEPT / public-evidence-consistent`, reference `ACCEPTED / predicate=True /
  integrity=True`, outer hashes `PASS`, wrapper `REJECT / semantic-candidate-execution-mismatch`),
  `:26` ("a genuine semantic mismatch result, not stale-hash rejection"), `:67` (gate "Original
  Stage01 semantic binding enforcement | **FAIL/ABSENT**").
* The underlying source fact: `cert_integrity` never touches `candidate_output.json`, stdout or
  stderr (`contract_sound_stage01_reference_verifier_v2.py:89-114`); the blind validator never
  opens `candidate_output.json` at all (`contract_sound_stage01_validator_v2.py:61-66`); stdout and
  stderr are never hashed anywhere on the path.

**This is a real finding and it is not downgraded by anything in this document.** The frozen
components *would* grant an attribution they should refuse, if presented with such a bundle.

### 5.2 What Stage 3 must establish, and did not

Stage 3 must establish **reachability**: that an external party can *cause* that condition through
an interface that already exists, and that the resulting attribution propagates to a downstream
claim. Section 3 shows that no such interface exists. Therefore:

> The C02/C03 condition is **not reachable by an external party through the current path.**

### 5.3 Why (a) does not imply (b) here — the specific structural reason

The gap is a **missing binding**, and a missing binding is only exploitable if something can
*substitute* one side of the binding. In this pipeline, **the pipeline's own aggregator constructs
the certificate internally, in the same process and in the same loop iteration, immediately after
executing the program** (`run_contract_sound_agent_replacement_v1.py:165` → `:172` → `:175` →
`:176`). Concretely:

1. The program that is credited (`agent_artifact.path` / `.sha256`,
   `run_contract_sound_agent_pilot_free_v2.py:95`) is **the same file** that was written at
   `contract_sound_repaired_pipeline.py:109` and executed at `:117-127`.
2. The candidate object that the reference verifier consumes
   (`contract_sound_stage01_reference_verifier_v2.py:123`) is **the same file** that the harness
   wrote at `contract_sound_repaired_pipeline.py:147` from the parse of that program's own stdout
   (`:140-142`).
3. The two are not *bound* (no hash joins them) — but they are also not *separable*. The
   substitution that C02 and C03 perform requires two distinct artefacts to coexist. In the live
   path there is only ever one, and it is produced by one process, in one call chain, with no
   intervening untrusted party.

The C02/C03 fixtures are therefore **discrimination fixtures**: they show the evaluator *can*
discriminate the contradiction class when the contradiction is presented. They do not show that
the live pipeline can be made to *present* it. This is the same limitation Stage 1 itself
recorded (`s1_protocol.md:34-39`; `END_TO_END_ATTRIBUTION_RESULTS.md:22`): the contradiction-family
cases "do not establish that an attacker can cause that condition in the ACTS-Attack pipeline.
Reachability is a separate question."

### 5.4 The two places where a reachability gap *would* bite, if an ingress appeared

Recorded for §7, not as findings:

* **Arbitrary evidence paths.** Both frozen components read evidence and artifacts at arbitrary
  absolute paths declared inside the certificate
  (`contract_sound_stage01_validator_v2.py:61-66`;
  `contract_sound_stage01_reference_verifier_v2.py:95-97, :110-111`). The project states the limit
  itself: "Historical compatibility permits arbitrary local evidence paths. This is not path
  confinement or untrusted-bundle safety" (`heb1_remediation_v1/stage01/README.md:23-25`).
* **Producer-declared attribution.** `claims.attribution = "PROVEN"` is set before any verifier
  runs (`run_contract_sound_agent_pilot_free_v2.py:98`), and both frozen components *require* that
  self-declared value (`contract_sound_stage01_reference_verifier_v2.py:109`;
  `contract_sound_stage01_validator_v2.py:83-84`).

Both are currently **unreachable**, because no external party can supply a certificate. The moment
an ingress appears that accepts an externally composed certificate, both become live.

---

## 6. The historical `contract_sound_repaired_pipeline.py` bwrap sandbox, and the historical static source policy

### 6.1 What the bwrap sandbox is

`sp2027/analysis/contract_sound_repaired_pipeline.py:79-99` builds the command; `:116-127` runs it.

* `:81-83` — `bwrap` must be present or execution **fails closed** with
  `OS_SANDBOX_UNAVAILABLE:bwrap-not-found` (`:129`).
* `:89` `--die-with-parent`; `:90` `--unshare-net`; `:91` `--ro-bind / /`;
  `:92` `--bind <case_dir> <case_dir>`; `:93` `--chdir <case_dir>`; `:95-98` the child argv
  `sys.executable -I <candidate.py> <input_path>`.
* `:71-76` — bounded resources: `RLIMIT_CPU` 2 s, `RLIMIT_AS` 256 MB, `RLIMIT_FSIZE` 1 MB,
  `RLIMIT_NOFILE` 32. `:123` a 30 s wall-clock timeout. `:114` a minimal environment
  (`PATH`, `PYTHONHASHSEED=0`).

**What it does guarantee (within the executed campaign):**

1. The candidate cannot reach the network: the network namespace is empty (`:90`).
2. The candidate cannot modify the host filesystem: the root is bound read-only (`:91`).
3. The candidate can write only inside its own per-session case directory (`:92`), which contains
   only that session's own files.
4. The candidate cannot fork out of the harness's lifetime (`:89`) and is resource-bounded
   (`:71-76`).
5. The sandbox is **fail-closed**: absent `bwrap`, no execution occurs at all (`:81-83`, `:129`).
   The executed campaign shows this path working as designed: 2 of 72 sessions were
   `SANDBOX_REJECTED` because the model-authored program imported `hashlib`
   (`replacement-005-8163a4307df9` and `replacement-013-d23672d9f3fe`, `execution.qualification`
   = `[{"line": 3, "rule": "disallowed-import-from", "value": "hashlib"}]`).

**What it does NOT guarantee:**

1. It is **not** a namespace-complete sandbox for the candidate's *read* view: `--ro-bind / /`
   makes the whole host filesystem **readable** to the candidate. The historical campaign's
   own isolation probe (`sp2027/analysis/run_os_isolation_probe.py:1-17`) is a capability probe
   that reports `host_write` and `network` outcomes; it is not an execution observer and it does
   not assert anything about host reads.
2. It does not bind the executed program bytes to the certificate: the certificate's
   `agent_artifact.sha256` is computed **after** execution
   (`run_contract_sound_agent_pilot_free_v2.py:95`, called at
   `run_contract_sound_agent_replacement_v1.py:172`, i.e. after `:165`). A program that modified
   its own source in place would be credited with its post-execution bytes. (Under the static
   policy this is not reachable — see §6.2 — and in any case it is the *observability* half of the
   Stage 1 gap, not a separate reachability finding.)
3. It does not hash stdout or stderr into any evidence record, and it does not hash
   `candidate_output.json` into the certificate
   (`contract_sound_repaired_pipeline.py:136-137, :147`; the certificate's evidence list is
   `run_contract_sound_agent_pilot_free_v2.py:99-100`).

### 6.2 What the historical static source policy is, and what it does not cover

Two generations of policy exist in the tree.

* **Historical policy** — `run_contract_sound_agent_pilot_free_v2.py:42-53` (`safe_source`): AST
  allow-list `{"json", "sys", "base64"}`; forbidden boundary tokens `subprocess`, `socket`,
  `requests`, `urllib`, `os.`, `open(`, `__import__`; applied to `ast.Call` and `ast.Attribute`
  nodes. This is the policy of the *earlier*, **unsandboxed** runner
  (`:56-69` runs `subprocess.run([sys.executable, "-I", artifact, input_path], ...)` with **no**
  `bwrap`), i.e. of the campaign that was infrastructure-invalid (72/72 `PROVIDER_FAILURE`,
  HTTP 401).
* **Repaired policy** — `contract_sound_repaired_pipeline.py:13-14, :17-35, :38-68`
  (`qualify_source`): `ALLOWED_IMPORTS = {"json", "sys", "base64"}`,
  `FORBIDDEN_BOUNDARIES = {"subprocess", "socket", "requests", "urllib", "os.", "__import__"}`, and
  a precise rule for the one permitted read `open(sys.argv[1], "r"|"rt")` (`:17-35`). This is the
  policy of the **executed** campaign.

**What the repaired policy does guarantee:** a candidate program can import only `json`, `sys`,
`base64`; can call `open` only on `sys.argv[1]` in a read-only mode; and is rejected for any
`ast.Call`/`ast.Attribute` whose source text contains a forbidden token. On the executed
campaign it rejected 2 of 72 model-authored programs (`hashlib`), which is the policy working
as intended.

**What it does not guarantee — a source-level completeness observation.** The policy is a
**token-and-shape check on the AST**, not a capability check on the runtime. A program that
reaches a forbidden module *without writing a forbidden token* is not detected. Verified **offline
and without executing any program** by applying `qualify_source()` — a pure function — to two
sample source strings:

| Sample source | `qualify_source()` verdict |
|---|---|
| `import json, sys` + `json.load(open(sys.argv[1]))` + `print(json.dumps(d))` | `True / QUALIFIED / []` (the intended baseline) |
| `import sys` + `m = sys.modules['os']` + `m.system('id')` | `True / QUALIFIED / []` |
| `import sys` + `m = getattr(sys.modules.get('o'+'s'), 'system')` | `True / QUALIFIED / []` |

The second and third are accepted because the AST walk inspects only `ast.Import`,
`ast.ImportFrom`, `ast.Call` and `ast.Attribute` (`:44-67`); a `ast.Subscript` into
`sys.modules` is not one of them, and the unparsed call text `sys.modules['os'].system('id')`
contains none of the forbidden tokens (not even `os.`, because the quote breaks the token).
Independently confirmed as a runtime fact, without executing any payload: under `python -I`,
`'os' in sys.modules` is `True` (the `os` module is always imported during interpreter start-up),
so `sys.modules['os']` is reachable from a program that imports only `sys`.

**Bounding this observation, precisely and in the right order:**

1. **It is not a live-campaign finding, and it is not presented as one.** No campaign was re-run,
   no provider was called, no candidate program was executed, and nothing in the frozen 72-session
   dataset was modified. The verification was: apply a pure function to two strings.
2. **It does not escape the sandbox.** If such a program were executed, the achievable effect
   would be arbitrary command execution *inside* the `bwrap` sandbox: no network (`:90`), no host
   writes (`:91`), writes confined to the case directory (`:92`), bounded resources (`:71-76`).
   That is a **weaker boundary than the policy implies**, not a boundary break.
3. **It does not produce an attribution.** The reference verifier independently recomputes the
   cryptographic predicate from the private target state and the candidate bytes
   (`contract_sound_stage01_reference_verifier_v2.py:122-129, :131`). A program that reached `os`
   still has to produce a cryptographically correct answer to be `ACCEPTED`; bypassing the policy
   grants no new cryptographic capability. The private target state is written *after* execution
   (`run_contract_sound_agent_replacement_v1.py:166-167`), so it is not readable during the run.
4. **It creates no external ingress.** A model-authored program is the **system under test**,
   not an external submitter of evidence. It does not create a channel through which an external
   party can reach the evaluation path.
5. **The correct characterisation** is: *the static source policy is a syntactic boundary, and
   the OS sandbox, not the policy, is the enforcing boundary for filesystem and network effects.*
   The repair is the `bwrap` isolation; the policy is a defence-in-depth pre-filter. The executed
   campaign's own report already treats it this way: the 2 `SANDBOX_REJECTED` sessions are
   reported as *pre-execution contract rejection*, a different category from cryptographic failure
   (`sp2027/analysis/H1_FINAL_DISPOSITION.md:90-95`).

**Therefore this observation changes nothing in §4.** It is recorded because it is a real,
checkable property of the historical policy, and because the honest engineering statement is more
useful to a reader than the reassuring one.

### 6.3 Net statement

The historical sandbox and policy constrain **what an executed candidate program can do**. They
do **not** create, and cannot create, a channel by which an *external party* delivers evidence to
the evaluator. Reachability of the C02/C03 condition is governed by the **interface topology**
(§3), not by the strength of the in-process controls.

---

## 7. What would change the answer

### 7.1 The exact property an authorised gateway would need

A qualifying ingress would have to satisfy **all six** criteria of §1. Concretely, it would need
to be an interface that **already exists**, with:

1. **An identifiable owner and a recorded authorisation** that explicitly covers accepting
   third-party-composed evidence into the attribution path (K1) — a deployment artefact, a
   documented API, a registered service interface. A gateway *authored for this experiment* fails
   this criterion by construction, regardless of how it is implemented.
2. **A real, documented accepted input format** that is a *superset* of, or identical to, the
   certificate/evidence format the frozen components consume (K2).
3. **Documented attacker-controlled fields** — a written statement of which fields an external
   party controls, and which of those fields reach the evaluator's decision inputs (K3). On the
   current components the sensitive fields are: `agent_artifact.path` and `.sha256`, the five
   `evidence[].path`/`.sha256` entries, `claims.*`, and the `candidate_output.json` path named
   in the reference bundle
   (`contract_sound_stage01_validator_v2.py:61-66`;
   `contract_sound_stage01_reference_verifier_v2.py:95-97, :110-111, :121-123`).
4. **An actual evaluator invocation** on the submitted bytes — the frozen validator and/or
   reference verifier running on the submitted artifact, not on a re-serialised copy (K4).
5. **A downstream claim consumer** — the aggregator's `primary()` conjunction
   (`audit_contract_sound_replacement_pilot.py:17-18`) and the report it writes (`:90-102`) — and
   therefore a path from a submitted artifact to a published attribution (K5).
6. **An observable final attribution verdict** retained per submission (K6).

The single decisive property is #1: **the interface must pre-date and be independent of this
research programme.** Everything else is engineering detail.

### 7.2 The smallest scoped test that would then be run

*Only if and when such a gateway is identified.* It is described here so that the design is on
record; it is **not** a proposal, and nothing in it has been executed.

**Precondition (blocking).** A written, in-session authorisation naming the gateway, its owner,
its endpoint, and the scope of the test. Absent that, Stage 3 stays at
`NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED` and the remaining authorised defensive work
continues.

**Design.**

| Element | Specification |
|---|---|
| **Object under test** | The **frozen** components, hash-pinned before and after: `contract_sound_stage01_validator_v2.py`, `contract_sound_stage01_reference_verifier_v2.py`, and the aggregator `audit_contract_sound_replacement_pilot.py`. |
| **Path under test** | The gateway exactly as deployed. No proxy, no re-serialisation, no local shim. |
| **Submitter** | The test harness acting as the untrusted submitter, over the gateway's own transport, with the authorisation's stated fields only. |
| **Attempt budget** | The smallest number that can produce an interpretable result, **declared in advance**, with the provider-side budget statement for the gateway's own cost model. If the gateway is metered, the budget is stated in the gateway's own units, not in provider units. |
| **Case set** | The minimum discriminating set: (a) a **clean control** — an honest bundle that the *reference* verifier accepts and that must be attributed; (b) the **C02 analogue** — credited program ≠ executed program; (c) the **C03 analogue** — credited output ≠ observed output; (d) a **path-confinement probe** — an evidence path outside the authorised evidence root, to test the `arb_evidence_paths` weakness (§5.4); (e) a **claims-only tamper** — the same evidence with `claims.attribution` altered, to test whether the frozen components' verdict is a function of the evidence or of the claim. |
| **Controls that must run** | (i) The **same** case set passed to the frozen components *locally*, in-process, as a baseline. Without the local baseline, a rejection cannot be distinguished from a gateway rejection. (ii) A **positive control** per case: a well-formed submission that the gateway accepts and that must be attributed, to separate "the gateway rejected it" from "the evaluator rejected it". (iii) A **transport-only control**: a submission that is well-formed but whose evidence is deliberately incomplete, to confirm the gateway transmits bytes without interpreting them (or, if it does interpret them, to characterise that). (iv) **Byte-identity control**: the submitted bytes' digest recorded at the gateway and re-hashed at the evaluator, to prove nothing rewrote the artifact in transit. |
| **Independent final-claim adjudication** | The final attribution verdict must be adjudicated by a party that did **not** build the gateway and did **not** build the test harness, using (a) the gateway's own retained submission record, (b) the frozen components' raw stdout, and (c) an independent recomputation of the cryptographic predicate. The Stage 1 pattern — a trusted execution observer holding its own key and adjudicating from retained signed facts (`…/stage1_attribution/s1_trusted_observer.py:96-120, :205-306`) — is the appropriate model. The adjudicator's output is the only thing reported. |
| **Recording** | Every submission, every response, every evaluator invocation, the gateway's own logs, and the final adjudication, retained verbatim; the adjudicator's verdict computed from the raw records, not from any summary. |
| **Stopping rule** | Predeclared: stop at the end of the attempt budget; a single confirmed end-to-end attribution of a bundle that should have been refused ends the test immediately and is reported as-is. |
| **Reporting constraint** | The result is reported as *"under the gateway's authorisation, the frozen components granted an attribution to a bundle it should have refused"* — **not** as a live-campaign result, unless the gateway is demonstrably the deployed production interface and the authorisation covers that claim. |

### 7.3 What is explicitly **not** proposed

* **Not** creating a gateway, a mock, a shim, or a replacement ingress, and not using the
  concurrent sibling tree's `ingress_gateway.py` (C11) as a substitute. A deliberately created
  replacement gateway is excluded by the brief and by §3/C11; it would measure the replacement,
  not the system.
* **Not** weakening, patching, or re-writing the frozen components. The point is to measure what
  they do, not what they could do.
* **Not** re-running the historical 72-session campaign, and not making any provider call.
* **Not** presenting a source-level observation as a live finding.

---

## 8. Residual work that remains authorised

The following are inside the authorised boundary and were **not** performed in this document, so
that the record is accurate about what remains open:

1. Extend the §3 sweep to any repository that is later brought inside scope (the finding is
   scoped to this repository at this time).
2. Keep §5.4's two latent weaknesses (arbitrary evidence paths; producer-declared attribution)
   tracked as **latent, not live**, and re-test them *only* if a qualifying ingress appears.
3. Carry §6.2's policy-completeness observation into the remediation track as a **defensive
   hardening** item (a capability-based check in place of, or in addition to, the token-based
   check) — explicitly as a *policy* change, not as a reachability claim.
4. Report the Stage 1 capability gap with the §5 scope wording attached: the frozen components
   would accept a bundle they should refuse; **no external party can currently make them do so**.

---

## 9. Machine-readable determination

```
STAGE3_FINDING: NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED
STAGE3_METHOD: READ_ONLY_SOURCE_ANALYSIS_PLUS_REPOSITORY_WIDE_INGRESS_SWEEP
STAGE3_CANDIDATE_INGRESSES_EVALUATED: 14
STAGE3_CANDIDATES_PASSING_ALL_SIX_CRITERIA: 0
STAGE3_QUALIFYING_CRITERION_FAILED_BY_EVERY_CANDIDATE: K1_OWNER_AND_AUTHORISATION
STAGE3_COMPONENT_LEVEL_CAPABILITY_GAP: DEMONSTRATED_IN_STAGE_1_AGAINST_FROZEN_STAGE01_PAIR
STAGE3_DEPLOYED_ATTACKER_REACHABILITY: NOT_ESTABLISHED
STAGE3_PROVIDER_CALLS: 0
STAGE3_NETWORK_REQUESTS: 0
STAGE3_PACKAGE_INSTALLS: 0
STAGE3_PIPELINE_EXECUTIONS: 0
STAGE3_GATEWAY_CREATED_OR_MODIFIED: NO
STAGE3_LIVE_CAMPAIGN_FINDINGS_CLAIMED: NONE
STAGE3_REACHABILITY_STATEMENT_OF_RECORD: NO_EXTERNAL_CERTIFICATE_COMPOSITION_INTERFACE_FOUND_IN_INSPECTED_REPOSITORY_PATHS
STAGE3_EVIDENCE_TYPE: SOURCE_LEVEL_NEGATIVE_EVIDENCE_NOT_PROOF_OF_IMPOSSIBILITY
STAGE3_BLOCKING_RESOURCE_GAP: G-5_NO_AUTHORIZED_SUBMISSION_GATEWAY
```

**Human-readable restatement:** no existing, authorised ingress was found through which externally
controlled evidence can legitimately reach the ACTS-Attack evaluation and attribution path. The
Stage 1 capability gap against the frozen Stage01 pair stands unchanged and is a *component-level*
result. The deployed-reachability claim is **not** made, because the pipeline's own aggregator
constructs the certificate internally, in-process, immediately after execution — and no candidate
interface in this repository can change that.

---

*Prepared 2026-10-20 as part of the ACTS-Attack next-phase programme. Companion documents:
`stage0/AGENT1_TRUST_BOUNDARY_MAP.md` (source map, re-derived and independently checked here),
`stage1_attribution/s1_protocol.md` and `s1_deviations.md` (Stage 1 preregistration and scope),
`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md` (Stage 1 results), `stage4_arms/STAGE4_ARM_STATUS.md`
(Stage 4).*
