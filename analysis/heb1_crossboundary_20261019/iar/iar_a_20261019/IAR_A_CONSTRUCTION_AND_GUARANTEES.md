# IAR-A — Exact Construction, Capability Model, and Guarantee Mapping

**Date:** 2026-10-19
**Status:** Reconciliation and guarantee analysis of the executed IAR-A pass. No campaign artifact was modified; protected locks were verified unchanged during the run.
**Frozen inputs:** `iar_a_results.json` (sha256 `c3f225825d8b0989d6a14336ba44e80342c572a23bee9b64b79448f300401313`), `iar_a_stage01_transfer.py` (sha256 `27c01caba5a1fbf8e56e484ebad22a1277e05ba6e2c100b2889eb1507448c01b`), real components `contract_sound_stage01_validator_v2.py` (`f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a`) and `contract_sound_stage01_reference_verifier_v2.py` (`15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b`).
**Purpose:** resolve the A1 composition-wording discrepancy between the memo and the adjudication protocol, state exactly which security guarantee each IAR-A test exercises, and record the accurate (bounded) description of the finding.

## 1. Exact A1 composition (verified byte-level from `iar_a_20261019/`)

Two ground-truth runs exist for the same task (`ECDSA_Nonce_Reuse-base-01`); neither registry is visible to the validator or the reference verifier:

| record | session | candidate sha256 | effect | executor |
|---|---|---|---|---|
| X (failed run) | `iar-session-X` | `aed7e1d8456b4e98548b7b8b88dd2fbc7ae191e1feb7701448733b6eeaca8ad` | NOT_OBSERVED | `iar-executor-X` |
| Y (successful run) | `stage01-hardened-session-001` | `e1647eab901a58ebef676f731590014cc86620bb21cf5a594bebab2e65a3aae7` | OBSERVED | `stage01-executor-v1` |

A1 public certificate (`A1_trace_candidate_splice.public_certificate.json`, sha256 `1e738566ae78a61806c55ca6b54add650da3defce9543c3e706506f5b2e0b0f2`) carries:

| certificate element | value | origin |
|---|---|---|
| `execution.session_id` | `iar-session-X` | X |
| `execution.trace_hash` | sha256(`x_execution_trace.json`) = `fe9f1e4b…` | X |
| `execution.executor_hash` | sha256(`"iar-executor-X"`) = `7af0c5ed…` | X |
| `agent_artifact.path` / `.sha256` | `y_candidate.json` / `e1647eab…` | **Y** |
| evidence `agent_artifact` | `x_agent_artifact.json` = {artifact: `"candidate.json"`, producer: `iar-run-X`, session_id: `iar-session-X`} | **X** (authorship record, no artifact hash) |
| evidence `execution_trace` | `x_execution_trace.json` = {base_instance_id, executor: `iar-executor-X`, session_id: `iar-session-X`} | **X** (trace, no candidate hash) |
| evidence `target_effect.status` | `OBSERVED` | **Y** (Y's run outcome) |
| submitted candidate (bundle) | `y_candidate.json` = `e1647eab…` | **Y** |

Submitted candidate sha equals registry Y and differs from registry X. The blind validator returned `ACCEPT` / `public-evidence-consistent`; the reference verifier returned `ACCEPTED` (`cryptographic_predicate: true`, `certificate_integrity: true`, `certificate_errors: []`).

**What the accepted certificate therefore asserts:** (a) the submitted candidate solves the target (reference recomputation, true for Y); (b) the certificate is internally consistent (all evidence file hashes match; `trace.session_id == execution.session_id` = X; task instance binding; verifier version; effect status matches the declared claim); (c) session X is present via its trace. **What it does not assert, and no component checks:** that session X executed the submitted candidate. Nothing in the certificate relates the trace or the authorship record to the submitted candidate's hash — the trace carries no candidate hash, and `x_agent_artifact.json` names `"candidate.json"` without any hash.

## 2. Reconciliation of memo vs protocol wording

The memo line "execution/trace/authorship from **X**, candidate/effect from **Y**" and the protocol line "uses X's `execution_trace` and execution session but Y's candidate, `agent_artifact`, and `target_effect`" are both correct at different JSON levels:

- **Memo** refers to the *evidence records* (`execution_trace` record = X's; `agent_artifact` **evidence record** = X's authorship record) and the `execution` block (session X).
- **Protocol** refers to the certificate's `agent_artifact` **pointer** (`.path`/`.sha256` → Y's candidate bytes), the submitted candidate, and the `target_effect` status (Y's outcome).

There is no contradiction in the tested bytes. The ambiguity was wording only; the exact composition is the table in §1. The adjudication protocol's A1 description is corrected in `HEB1_ADJUDICATION_RESPONSE_20261019.md` to use "X's `agent_artifact` **evidence record**" versus "the certificate's `agent_artifact` **pointer**".

## 3. Capability model (what the tested composer could do)

| class | capability | IAR-A tests |
|---|---|---|
| C0 | selection only — re-present an existing certificate and records unchanged | **not tested**; no test relies on C0 |
| C1 | certificate issuance — assemble a new certificate around selected records and recompute hashes/pointers | **A1** (new certificate binding X's records to Y's candidate/effect), **A2a** (declared `trace_hash` altered), **A2c** (declared reference claim altered) |
| C2 | per-record metadata rewrite (no signatures exist to verify) | **A2b** (authorship record session rewritten to Y), **A3** (trace/authorship relabeled to Y) |
| C3 | forgery of a signed/anchored record | **out of scope** — no signature layer exists in the Stage01 format; IAR-B introduces one to measure the boundary |

Accurate label for A1: capability **C1**, with per-run records **synthesized by the experiment** (deterministic X/Y runs), not harvested from a live campaign. The previous "selection-only" phrasing in the memo is imprecise and is superseded by this table. A note pointing here can be added to the memo; the memo itself is left unaltered.

## 4. Per-test guarantee mapping

| test | guarantee it targets | what actually happened | independent? |
|---|---|---|---|
| A0 clean | positive acceptance control | `ACCEPT` / `ACCEPTED` | control |
| A1 splice | evidence-to-artifact binding: "the session credited with the success executed this candidate" | Both components accepted; nothing ties X's trace/authorship to Y's submitted candidate | **independent core gap** (blind validator). Outside the reference verifier's stated guarantee (candidate correctness + certificate-internal consistency) |
| A1b session mismatch | explicit execution-session binding | `REJECT` / `REJECTED` (`execution-session-binding`) | negative control; shows binding is active, not vacuous |
| A2a wrong `trace_hash` | declared-field verification | Both accepted; `execution.trace_hash` is declared but unverified by both components | not independent — documents an unchecked declared field; only misleads consumers that trust declared values |
| A2b authorship session mismatch | authorship-record-to-execution binding | Both accepted; only the **trace** session is compared to the execution session | not independent — compounds A1 (authorship record is unbound) |
| A2c reference claim without evidence | claim integrity of `reference_oracle_acceptance` | Both accepted on the public certificate; the reference verifier independently recomputes the predicate, so its own verdict is sound | conditional — a consumer trusting the public claim without calling the reference verifier would be misled; the campaign harness normally writes `NOT_ESTABLISHED` |
| A3 relabeled trace | authenticity of record bytes | Both accepted; unsigned session field can be rewritten | expected consequence of unsigned metadata (RATS/in-toto principle), not an independent finding |

Net: one substantive, independent gap (A1, and its compounding A2b variant): the Stage01 validation components do not bind the accepted candidate to the execution identity credited with it. A1b proves the components are not vacuous; A2a/A2c are declared-field notes; A3 is the authenticity boundary.

## 5. Reachability and accurate characterization

- **Hardened runner** (`run_contract_sound_stage01_hardened.py`): certificates are generated by the trusted harness from a single case; the bundle is assembled by the harness; there is no ingestion path for externally issued certificates. The campaign's own `replay_cross_session` defect (trace session `other-session`) **is** caught by `execution-session-binding`.
- **Agent pilot** (`run_contract_sound_agent_pilot.py`, frozen 72-session campaign, not rerun): the model authors only the candidate artifact; the harness assembles evidence and certificate; again no untrusted certificate issuance.
- Therefore the accurate description of IAR-A is: **a confirmed acceptance-boundary weakness in the existing Stage01 validation components under constructed adversarial inputs (capability C1/C2 composer scenario)**, not an observed attack against a live AI-agent evaluation campaign.
- Conditions for it to matter operationally: a pipeline where a middle layer (aggregator, merge step, or external evidence ingestion) issues certificates from records of multiple runs without binding the accepted candidate to the credited execution — precisely the pattern HEB-1's synthetic V0/V1 demonstrated, now shown to be permissible input to the real Stage01 components. None of the current campaign scripts creates that path, and the certificate format lacks the binding field that would prevent it.
- Novelty status unchanged: the binding principle is anticipated by RFC 9334 (RATS), in-toto, and the session-bound evidence-record work; the candidate contribution remains the empirical measurement of false-attribution promotion in AI-authored cryptographic-exploitation evaluation.

## 6. Independent verification

- `python3 sp2027/analysis/heb1_crossboundary_20261019/iar/verify_iar_a.py` (stdlib only) re-runs both frozen components per variant (temp bundles under `/tmp/opencode`), recomputes every file/evidence hash, asserts the composition facts of §1 (Y pointer vs X evidence; registry mismatch), compares verdicts against `iar_a_results.json`, and exits nonzero on any mismatch. It also checks the two component hashes above and reports any drift.
- Protected locks (`RESULTS_LOCK.json`, `RESULTS_LOCK_H1PC.json`, `paper/main.tex`, `paper/main.pdf`) remain unchanged; the verification re-checks them.

## 7. Next

IAR-B (Ed25519-authenticated provenance baseline; B5' metadata-rewrite variant to locate the binding/authenticity boundary) and IAR-C (independent generation; partial-claim acceptance for honest levels 1–5). No campaign artifacts are touched by either.
