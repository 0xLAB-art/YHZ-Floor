# HEB-1 re-audit historical correction ledger

Date: 2026-10-19  
Scope: independent source audit of `HEB1_MULTIAGENT_REAUDIT_20261019.md`  
Constraints: read-only audit of existing artifacts; no network/provider calls, no
benchmark or gateway execution, no paper/report edits.

## Evidence basis

The re-audit was checked against the retained source, not against another
agent's summary. The principal files used here are:

- `sp2027/analysis/experiment_b_20261019/eb_v3_full.py`
- `sp2027/analysis/experiment_b_20261019/eb_fixtures.py`
- `sp2027/analysis/experiment_b_20261019/iar_c/eb_independent_gen.py`
- `sp2027/analysis/run_contract_sound_agent_pilot.py`
- `sp2027/analysis/heb1_remediation_v1/stage01/external_binding_wrapper.py`
- `sp2027/analysis/experiment_b_20261019/EXPERIMENT_B_PROTOCOL.md`

Line numbers below refer to the checked-in files as read during this audit.

## Historical corrections

| ID | Exact original claim and source | Verified status | Correction | What cannot be repaired retrospectively |
|---|---|---|---|---|
| C-01 | “duplicate/conflicting-record policy (different components treat duplicates differently)” in the list of missing V3-full controls, re-audit §3.10, lines 135–146; related wording says V3-full “lack[s] several controls.” | **Overstated for duplicate kinds.** `eb_v3_full.py:92–119` collects evidence kinds and returns `REJECT` with `duplicate-evidence-kind` when `len(set(kinds)) != len(kinds)`. The Stage01 external wrapper also rejects duplicate kinds at `external_binding_wrapper.py:76–96`, and its test covers this at `test_external_binding_wrapper.py:68–85`. | Replace the blanket claim with: “V3-full has an explicit duplicate-kind rejection; the audit did not establish a general policy for every possible conflicting-record representation or for every component.” A duplicate-kind attack is not an untested V3-full gap. Missing-kind behavior and cross-component semantic differences remain separate questions. | The re-audit's broad inventory wording and any downstream interpretation that treated duplicate kinds as an unimplemented V3-full control cannot be made true after the fact. Only a future corrected statement can distinguish duplicate rejection from unresolved conflict semantics. |
| C-02 | “Fixture signing keys are publicly derivable … This … invalidates interpreting V3-full as a realistic secret-held issuer model,” re-audit §3.8, lines 119–123. Protocol trust model says the composer “cannot obtain or use another run's signing key,” `EXPERIMENT_B_PROTOCOL.md:50–65`. | **Verified fixture property and threat-model mismatch; production impact not shown.** `eb_fixtures.py:112–123` derives the private key from `session`; `iar_c/eb_independent_gen.py:131–142` does the same with its own salt. The protocol's C1 composer assumption is therefore false for these shipped fixtures if session identifiers/seeds are known. | State precisely: “The fixture adversary can re-derive fixture private keys, so the fixture does not model secret-held issuers. V3-full's observed signature checks remain a deterministic test of the implemented records, but the experiment does not support conclusions about compromise-resistant signing or a production key boundary.” This is a scope/validity correction, not evidence that V3-full was cryptographically bypassed. | Existing signed-bundle results cannot retrospectively become evidence under a secret-held-key threat model. The key derivation cannot be repaired by prose; a new fixture/gateway experiment with independently generated, protected keys would be needed for that threat claim. |
| C-03 | “The certificate binds the agent artifact to `candidate.py`, while the reference verifier evaluates the separate candidate output … There is no candidate-program/output/trace chain,” re-audit §3.11, lines 148–152. | **Verified for the Stage01 pilot runner, but scope must be bounded.** `run_contract_sound_agent_pilot.py:57–70` executes `candidate.py` and writes `candidate_output.json`; `:87–100` records/hashes the program artifact; `:168–170` passes `candidate_output.json` to the reference verifier. The Stage01 wrapper explicitly says its `agent_artifact` is submitted candidate output, not program source, and “cannot prove a source-to-output chain” (`external_binding_wrapper.py:1–8`). By contrast, `eb_v3_full.py:120–125` hashes/binds its submitted `candidate.json`, and `:160–162` checks the trace's candidate hash against that same file hash. | Distinguish three propositions: (1) Stage01 has a real program-to-runtime-output provenance gap; (2) B2-2 demonstrates a candidate-output/credited-trace mismatch at that boundary; (3) this does **not** by itself show that V3-full's `candidate.json`/trace join is broken, nor that V3-full proves source-program-to-output provenance. The latter is an untested extension unless a program-execution contract is supplied. | The preserved B2-2 result cannot be relabeled as a V3-full source-to-output exploit. Conversely, the Stage01 result cannot be dismissed merely because V3-full binds its submitted candidate file. Historical reports must retain the component and object distinction. |
| C-04 | “Only the AI-agent arm produces unsupported attribution under the same complete contract: candidate AI-agent-specific mechanism,” re-audit §7, lines 191–212, especially line 210. | **Logical flaw.** Even under the stated matched experiment, an AI-only failure would establish an arm-specific outcome under that prompt/model/search setup, not an AI-specific security mechanism or novelty. The AI arm may differ in search capability, time allocation, parser interaction, source generation, or error distribution. | Correct interpretation: “AI-only unsupported attribution would be evidence of an AI-arm-specific failure mode or capability interaction, requiring mechanism tracing and controls; it would not by itself establish a novel mechanism. A generic provenance failure in both arms supports a generic issue. A scripted-only or AI-only difference is an outcome contrast, not a novelty proof.” | No retrospective arm comparison can identify a mechanism that was not measured. A bounded future experiment would need matched task/contract inputs, retained intermediate artifacts, and controls that separate search/capability differences from provenance semantics, followed by targeted prior-art comparison. |

## Program/output and evidence-object distinction

The re-audit should not collapse these objects:

1. **Program source:** `candidate.py`, written from provider/model source by
   `run_contract_sound_agent_pilot.py:57–60`.
2. **Runtime output:** `candidate_output.json`, created only after execution and
   parsed at `:63–70`.
3. **Submitted candidate object in B2-2:** a file named through the certificate's
   `agent_artifact` pointer; the wrapper documents it as candidate output, not
   program source (`external_binding_wrapper.py:1–8`).
4. **V3-full candidate object:** `candidate.json`, whose file hash is compared to
   the certificate and whose digest is joined to the execution trace
   (`eb_v3_full.py:120–125, 159–162`).

Therefore the strongest supported wording is: **the Stage01 path lacks a
program-to-output-to-trace chain, and B2-2 demonstrates a candidate-output versus
credited-execution mismatch; V3-full demonstrates a signed candidate-file to
trace join on the synthetic bundle format, not source-program provenance.**

## Reachable local AI-runner boundary

Source inspection supports the following local boundary, without executing it:

- The local runner can receive a provider response, extract source, execute it in
  a case directory, and write runtime output (`run_contract_sound_agent_pilot.py:161–170`).
- It then constructs the certificate and reference-input bundle internally and
  invokes the local reference verifier and validator (`:167–170`).
- The runner's certificate is therefore an internally constructed artifact; the
  inspected path does not expose an external certificate upload, webhook, or
  aggregation consumer.
- The external Stage01 wrapper is a local command-line wrapper around a frozen
  validator (`external_binding_wrapper.py:40–56, 136–162`), not a deployed
  submission gateway.

This is a reachable **local construction/execution boundary**, not evidence of
remote or deployed exploitability. No provider call, gateway, or benchmark was
run for this ledger.

## Prioritized unresolved hypotheses

1. **P1 — faithful external submission boundary:** Does an authorized gateway
   accept a mixed bundle assembled from independently produced records and then
   feed its decision to a real downstream consumer? This is required before
   claiming live impact.
2. **P1 — secret-held issuer model:** With fresh private keys generated outside
   the composer and a separately integrity-protected trust anchor, which C1/C2
   compositions remain possible? The current fixtures cannot answer this.
3. **P2 — source-to-output provenance:** Does a complete implementation bind
   program bytes, exact invocation/input/environment, runtime output, trace, and
   reference verdict? The current Stage01 path does not establish this chain;
   V3-full's submitted-candidate join is narrower.
4. **P2 — conflict and omission semantics:** Beyond explicit duplicate-kind
   rejection, how should conflicting records, duplicate paths, missing kinds,
   and alternative representations be handled across each verifier? This is not
   the same as saying duplicate kinds are unhandled.
5. **P2 — AI-arm causal interpretation:** If matched scripted and AI arms differ,
   can the difference be attributed to a mechanism rather than search capability,
   prompt/model behavior, or harness interaction? An arm difference alone is not
   novelty evidence.

## Bounded next experiment recommendation (not executed)

Only after an authorized, faithful local-or-external gateway exists, run one
small matched test with scripted and AI producer arms under the same complete
contract. Preserve program source, runtime output, exact input/environment,
candidate/output/trace digests, signer identity, target state, freshness/replay
state, and the final consumer decision. Predeclare that an arm-specific
difference is an outcome requiring mechanism analysis—not a novel mechanism by
default. If no gateway is available, stop at the current bounded synthetic
claim; do not create another broad benchmark.
