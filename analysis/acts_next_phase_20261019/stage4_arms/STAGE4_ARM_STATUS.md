# Stage 4 — AI-Agent vs Scripted Producer: Arm Status

**Experiment:** Stage 4 of the ACTS-Attack next phase.
**Tree:** `sp2027/analysis/acts_next_phase_20261019/stage4_arms/`
**Date:** 2026-10-20
**Method:** read-only source and artifact analysis. **No model call was made. No provider was
contacted. No network request was made. No package was installed. No historical session was
re-run. No file modified other than this report. No credential was read, printed, transmitted or
stored.**

**All paths are relative to the repository root `/mnt/nvme5/ACTS-Attack` unless stated otherwise.**

---

## 0. Status

```
STAGE4_STATUS: BLOCKED_BY_RESOURCE_OR_AUTHORIZATION
```

This is the same determination Stage 0 recorded as gap **G-4**
(`stage0/STAGE0_RESOURCE_GAPS.md:10`): *"No model/provider authorisation for a live AI-producer
arm. … **NOT REQUESTED** — the available route in this session is
`openrouter/minimax/minimax-m3.1-flash:free`; the named route was not usable."*

**Nothing in this document changes that status.** Stage 4 has not been run. No arm has been
executed. No arm-specific claim exists. The substance of this document is (a) the precise list of
confirmations that are still missing, (b) the matched-arm design that *would* be run once they are
obtained, (c) the interpretation rules that would govern the result, and (d) the evidence already
in hand that bears on the AI question — including two material defects in that evidence which
must be carried forward rather than glossed.

**This document is not a negative result about AI agents.** It is a statement that the
prerequisites for the experiment have not been confirmed, and that the existing evidence does not
bear on AI-specificity.

---

## 1. What Stage 4 requires

Stage 4 is the "AI-agent versus scripted producer" study. It requires three things, all of which
must hold *simultaneously*:

1. **A valid experimental interface** — a producer abstraction that an AI agent and a scripted
   program can both drive, producing artifacts of the same shape, evaluated under the same
   contract.
2. **Matched capabilities** — equivalent authorised interfaces, equivalent evidence privileges,
   equivalent attempt budgets, equivalent evaluation contracts across the two arms.
3. **Permitted model access** — an authorised provider route, with a confirmed model identity, a
   confirmed spending limit, a confirmed call ceiling, no paid fallback, known sampling controls,
   and a known retention policy.

Requirement 3 is not met. Requirements 1 and 2 have a design (Stage 1's evaluator, observer and
adjudicator are reusable) but are not exercised here.

---

## 2. The route and provider facts, as the repository records them

The task brief supplied four factual claims about the model route. `opencode.models` is **not**
available in this session, and the brief forbids making a model call, so these could not be
re-derived from a live catalogue. What follows is what **the repository itself records**, with the
recording source given in each case, plus the grep evidence.

### 2.1 The named AI route and the historical provider

| Fact | Repository record | Source |
|---|---|---|
| Desired AI route | `claude-sonnet-4-6-free` | `stage0/STAGE0_REPOSITORY_INVENTORY.md:127`; `sp2027/analysis/checkpoint007_active_experiments/runs_009/provider_adapter.py:19`; `sp2027/analysis/h1r3_20261019/h1r3_run.py:36`; `sp2027/analysis/run_contract_sound_agent_replacement_v1.py:20` |
| Historical provider | `https://api.apmix.ai` | `provider_adapter.py:19`; `h1r3_run.py:37`; `sp2027/analysis/h1r3_20261019/runs/confirmatory/EXECUTION_MANIFEST.json` → `provider_health.endpoint`; `sp2027/analysis/h1r3_20261019/EVIDENCE_PACKAGE_APMIX_README.md` |
| Route string recorded per session | `route` **and** `provider_model` = `"claude-sonnet-4-6-free"` for **852/852** H1-R3 records | `stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:137-149` |
| Route identity is **self-reported by the provider**, not attested by the harness | `provider_model` is populated from the provider's own response body (`body.get("model")`) | `provider_adapter.py:62`; `stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:151-156` |
| The route was **actually used** by the historical campaign | H1-R3: 852/852 `provider_status = SUCCESS`, `http_status = 200`, `finish_reason = end_turn`; contract-sound replacement pilot: 72/72 `SUCCESS`, 72/72 `http_status 200`, `provider_models = {claude-sonnet-4-6-free: 72}` | `stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:127-129`; `sp2027/analysis/contract_sound_agent_replacement_20261018/AGENT_PILOT_RESULTS_SUMMARY.json` |

### 2.2 The model-catalogue claims

| Claim (from the brief) | What the repository records | Independent verification possible in this session? |
|---|---|---|
| The catalogue contains **no** `gpt-5.6-luna` | `stage0/STAGE0_REPOSITORY_INVENTORY.md:127`: *"the `gpt-5.6-luna` model named in the brief does **not** exist in the provider catalogue"* | **No.** `opencode.models` is not available to me, and making a catalogue call is a provider call. A repository-wide grep for `gpt-5.6-luna` / `gpt-6-luna` / `gpt-5.4-nano` / `luna` returns exactly **two** hits: the Stage 0 inventory line above, and an unrelated mention of "GPT-5.6 Luna" as the *name of the six re-audit subagents* in `sp2027/analysis/heb1_independent_adversarial_audit_20261019/HEB1_MULTIAGENT_REAUDIT_20261019.md:4`. Neither is a provider catalogue entry. **Reported as the repository's record, not as a fact I independently established.** |
| `openai/gpt-6-luna` and `openai/gpt-5.4-nano` are **rejected for insufficient credit** | `stage0/STAGE0_REPOSITORY_INVENTORY.md:127`, same line | **No.** Same limitation. The repository records the rejection reason but not the provider response code, body, or timestamp. |
| The only usable route is `openrouter/minimax/minimax-m3.1-flash:free` | `stage0/STAGE0_REPOSITORY_INVENTORY.md:127` | **Partially.** The **harness** route of this very session is `openrouter/minimax/minimax-m3.1-flash:free` — that is the agent identity under which this document is being written, and it is a fact about the session, not about a provider catalogue I queried. It is **not** an authorised research route: no Stage 0–4 artefact records an authorisation for it, no provider attestation exists for it in this repository, and no spending/call ceiling is attached to it anywhere. |

**Consequence.** The repository's own Stage 0 inventory records that the brief's named route was
*not* the route available in this session, and that the alternative route the brief names is the
harness route. Stage 4 as specified — an AI-producer arm on `claude-sonnet-4-6-free` via
`https://api.apmix.ai`, matched against a scripted arm — therefore has **no confirmed usable
route** in this session, in addition to having no confirmed authorisation.

### 2.3 What the repository records about sampling, budget and fallback

These are the closest things to answers for confirmations (iii), (iv), (v) and (vi). They are
**records of a historical campaign's controls**, not an authorisation for a new one.

| Control | Recorded value | Source |
|---|---|---|
| Sampling parameters **sent** | `["model", "max_tokens"]` | `sp2027/analysis/h1r3_20261019/h1r3_run.py:168`; `runs/confirmatory/EXECUTION_MANIFEST.json` → `provider_health.sampling_parameters_sent` |
| Sampling parameters **unavailable** | `["temperature", "top_p", "seed", "system"]` | `h1r3_run.py:169`; same manifest key |
| `max_tokens` | 2600 (H1-R3, `h1r3_run.py:38`); 1800 (contract-sound replacement pilot, `run_contract_sound_agent_replacement_v1.py:159`) | as cited |
| Paid fallback | `False` | `h1r3_run.py` manifest (`paid_fallback_allowed: false`); `run_contract_sound_agent_replacement_v1.py:133`; `runs/confirmatory/EXECUTION_MANIFEST.json` → `provider_health.paid_fallback_allowed` |
| Automatic retries | 0 | `run_contract_sound_agent_replacement_v1.py:134`; `h1r3_run.py` manifest |
| Seed replacement / adaptive stopping / study expansion | `False` / `False` / `False` | `run_contract_sound_agent_replacement_v1.py:135-136` |
| Cost ceiling | `provider_cost_ceiling_usd: 0.0`; `provider_charge_usd: 0.0` on all 72 rows | `run_contract_sound_agent_replacement_v1.py:132, :183`; `AGENT_PILOT_RESULTS_SUMMARY.json` |
| Provider plan / allowance at H1-R3 health capture | `plan: "free"`, `allowance: 3000000`, `remaining: 2404557`, `used: 595443`, `topup_remaining: 0` | `runs/confirmatory/EXECUTION_MANIFEST.json` → `provider_health.usage_before` |
| Health-gate checks (8) | `decision_pass`, `endpoint`, `model`, `model_free`, `usage_free`, `topup_zero`, `message_200`, `fallback_disabled`, `retries_zero` — all must be true or the run aborts | `run_contract_sound_agent_replacement_v1.py:100-112` |
| Programme-level budget rule | *"Existing $50 alert/$200 hard stop are financial authorizations, not date/deadline gates and must be obeyed. Estimate price correctly for `claude-sonnet-4-6-free`: distinguish provider price claims, theoretical accounting cost and actual invoice. Ask for explicit approval before increasing the budget or changing infrastructure."* | `ACTS_Attack_Continuous_Research_Execution_Plan.md:206` |

### 2.4 Credential handling — recorded, and deliberately not exercised

* The adapter resolves its credential from `$APMIX_KEY_PATH` if set, else
  `~/.config/acts007/apmix.key` (`provider_adapter.py:22-29`); it raises
  `ProviderFailure("CREDENTIAL_MISSING"/"CREDENTIAL_EMPTY")` if the file is absent or empty
  (`:27-31`).
* The contract-sound runner gates on the credential file's presence and non-emptiness
  (`run_contract_sound_agent_replacement_v1.py:113-115`).
* The H1-R3 attestation note states the key source was **environment-only** ("`APMIX_API_KEY`
  only; never written to disk or repo") and that the provider exposes **`/v1/messages` only**,
  returning 404 for `/v1/models` and `/v1/usage`
  (`sp2027/analysis/h1r3_20261019/EVIDENCE_PACKAGE_APMIX_README.md`).
* **In this session, the environment variables `APMIX_API_KEY`, `ANTHROPIC_API_KEY` and
  `OPENROUTER_API_KEY` are all set, and the file `~/.config/acts007/apmix.key` exists.** Only
  *existence* was checked. **No credential value was read, printed, transmitted, hashed or
  stored, and none appears in this document.**
* **Unresolved inconsistency, recorded because it bears on confirmation (vii):** the adapter's
  default credential source is an on-disk file (`provider_adapter.py:26`), whereas the H1-R3
  attestation note records an environment-only, never-written-to-disk key
  (`EVIDENCE_PACKAGE_APMIX_README.md`). The repository therefore contains **two different
  statements about where the provider key lives**, and the H1-R3 freeze-time runner used a
  third, file-only path (`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:530`). This must be
  reconciled before any Stage 4 call, because it determines what "retention" even means for the
  credential.

### 2.5 A concurrent sibling tree has already exercised a model arm

Recorded because a reader of the repository will encounter it:

* `sp2027/analysis/acts_next_phase_20261019_v2/stage4_arms/` contains a model arm manifest
  (`model_arm_manifest.json`) recording `provider_route: claude-sonnet-4-6-free`,
  `provider_endpoint: https://api.apmix.ai`, `provider_calls: 14`,
  `distinct_program_requests: 14`, `no_fallback: true`, `no_retry: true`,
  `no_seed_replacement: true`, together with a `provider_calls.jsonl` ledger and a
  `provider_attestation.json` (`http_status: 200`, `route_match: true`,
  `provider_model: claude-sonnet-4-6-free`, `credential_recorded: false`).
* `sp2027/analysis/acts_next_phase_20261019_v2/stage3_boundary/` similarly contains a
  `provider_calls.jsonl` with five HTTP-200 records.

**What this is, and what it is not.** It is evidence that **a different session, under its own
authorisation, has already made provider calls on this route.** It is *not*:

* an authorisation for this session;
* an arm executed in *this* tree (`acts_next_phase_20261019/stage4_arms/` — this document is the
  only file in it);
* a substitute for the seven confirmations in §3;
* evidence of any AI-specific result — no such claim is made or inherited here.

It does raise one **budget** question that must be answered before any new Stage 4 run: whether
the programme-level call budget (`ACTS_Attack_Continuous_Research_Execution_Plan.md:206`) is
consumed programme-wide or per-experiment, and therefore how many calls remain.

---

## 3. The confirmations that are still missing

Each of the seven must be answered **in this session, in writing, by the authorising party**
before a single model call is made. "The repository records something similar" is not an answer:
historical campaign controls describe a *past, differently-scoped* campaign and were set by the
campaign's own author, not granted to a new one.

| # | Confirmation required | The specific question that must be answered | Repository state | Status |
|---|---|---|---|---|
| **1** | **Provider authorisation** | *Is there an explicit, in-session authorisation to send prompts and to receive model outputs from `https://api.apmix.ai` **for the purpose of a Stage 4 AI-producer arm**, under the identity/credential the harness will use, and is the authorising party the same party that granted the programme-level budget rule at `ACTS_Attack_Continuous_Research_Execution_Plan.md:206`?* | The historical campaigns were authorised (H1-R3, 72-session replacement pilot). The sibling session has an attestation on file. **No authorisation for a Stage 4 arm has been granted to this session.** | **MISSING** |
| # | | *If the answer is no to `apmix.ai`: is there an authorised route for `openrouter/minimax/minimax-m3.1-flash:free`?* | No authorisation, attestation, budget or ceiling for that route exists in the repository. | **MISSING** |
| **2** | **Correct available model identity** | *Which exact model identifier is authorised, and what is the evidence that it is the model that will actually answer — as opposed to a route name the provider asserts about itself?* | `provider_model` is populated from the provider's own response body (`provider_adapter.py:62`) and is therefore **self-reported** (`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:151-156`); the preregistration itself disclaims "immutable backend model identity — the provider returns a route name, not a proof of weights". A route-drift check exists (`run_contract_sound_agent_replacement_v1.py:162-163`) but it compares the provider's self-report against the expected string, and so cannot detect a substituted backend. | **MISSING** |
| **3** | **Free or approved spending limit** | *What is the spending ceiling for this specific experiment, in the provider's own units (the historical free plan recorded `allowance: 3000000` tokens, `topup_remaining: 0`), and does it remain free-tier, or must it be drawn against the programme's $50 alert / $200 hard stop?* | `provider_cost_ceiling_usd: 0.0` was set for the 72-session pilot (`run_contract_sound_agent_replacement_v1.py:132`) and H1-R3 recorded `provider_charge_usd: 0.0`. The current allowance/remaining balance is unknown. | **MISSING** |
| **4** | **Maximum call count** | *What is the maximum number of provider calls permitted for Stage 4, in total and per arm, and how is it counted (one HTTP request = one call)?* | The historical campaigns fixed theirs: 72 (`:125`) and 852 (H1-R3 schedule). The sibling session used 14. **No ceiling has been set for Stage 4.** | **MISSING** |
| **5** | **No paid fallback** | *Is it confirmed that the harness will fail closed on any route that is not the exact approved one, with no automatic substitution, no retry-to-a-paid-model, and no escalation on error?* | The historical runners do implement this (`run_contract_sound_agent_replacement_v1.py:108, :134, :187-192`; the manifest records `automatic_retries: 0`, `paid_fallback_allowed: False`). **But that is the code's behaviour, not a confirmation of the policy that the fallback is *forbidden* — and note the H1-R3 freeze-time health gate was later relaxed on disk (see §7.3).** | **MISSING** |
| **6** | **Sampling controls and unavailable controls** | *Which sampling parameters may be set, which are unavailable on this route, and is the resulting design **reproducible** given that `temperature`, `top_p`, `seed` and `system` are recorded as unavailable?* | The repository records `sent = ["model", "max_tokens"]` and `unavailable = ["temperature", "top_p", "seed", "system"]` (`h1r3_run.py:168-169`). **Two consequences that must be resolved before the experiment is designed:** (a) with no seed and no temperature control, the arm is **not deterministic**, so repeated runs of the *same* case by the same arm are not replicates of a fixed function; (b) the `system` parameter being unavailable constrains the prompt channel, and therefore the "identical prompt" requirement of §4.2 must be met by the *user-message* channel alone. | **MISSING** |
| **7** | **Prompt and output retention policy** | *What is the provider's retention policy for prompts and outputs (training use, log retention, downstream sharing, jurisdiction), what does the project commit to retaining locally, and how long?* | **Nothing in the repository records a provider-side retention policy.** What the repository records is *local* retention: `provider_raw.json` (72/72) and `provider_metadata.json` per session (`run_contract_sound_agent_replacement_v1.py:160-161`; `AGENT_PILOT_RESULTS_SUMMARY.json` → `evidence_counts`), and per-session raw bodies for H1-R3. The H1-R3 attestation note says only that the key was "never written to disk or repo" — a statement about the **key**, not about prompts or outputs. | **MISSING** |

**Summary: 7 of 7 confirmations are missing in this session.**

---

## 4. The matched-arm design that would be run

This is the design that would be executed **if and only if** §3 is answered. It is written out in
full so that it is preregisterable, and so that the *matching* requirements are explicit rather
than assumed. **None of it has been executed.**

### 4.1 Arms

| | **Arm S — scripted producer** | **Arm A — AI producer** |
|---|---|---|
| Producer | A frozen, deterministic program generator that emits candidate artifacts for the same instances, under the same interface | The authorised model route, driven by the same harness code path with the same instance and the same user-message prompt |
| Model | none | the confirmed route from §3 |
| Session count | identical to Arm A | identical to Arm S |
| Attempts per case | identical (see §4.4) | identical |

**Arm S is a legitimate baseline**, and it is the baseline the historical evidence already used:
the project's own correction ledger records that the historical HEB-1 composer was **scripted, not
an AI agent** (`stage0/AGENT5_PRIOR_ART_NOVELTY_MATRIX.md:290, :294`;
`heb1_remediation_v1/scientific_corrections/HISTORICAL_CORRECTION_LEDGER.md:29`, correction C-04).
That makes Arm S a *well-understood* baseline — but it also means the historical evidence is a
**generic** provenance-composition result, not an AI result (§7.2).

**Why Arm S must be a real baseline and not a strawman.** Arm S must be capable of producing the
*same class* of artifact as Arm A, including the failure modes under test. If Arm S is
constructed so that it cannot produce an unsupported attribution, the comparison is vacuous. The
frozen Stage 1 corpus already contains a scripted producer that produces both honest successes
and contradiction-family artifacts — the 27 cases in
`stage1_attribution/s1_case_manifest.json` are exactly such a scripted producer's output.

### 4.2 The shared contract

Both arms must be evaluated under **one** contract, with **one** ground truth, on **one** case
set.

| Contract element | Requirement | Source of the component |
|---|---|---|
| Producer interface | Identical artifact shape, identical declared fields, identical instance inputs | `stage1_attribution/s1_case_manifest.json` (frozen corpus + expected outcomes) |
| Prompt / instance channel | **Identical user-message content** for the AI arm and the equivalent specification for the scripted arm; identical instance bytes | The `system` parameter being unavailable (§3 #6) means the user-message channel carries everything |
| Execution | Identical: the same trusted execution observer, the same source policy, the same sandbox, the same resource limits, the same parser | `stage1_attribution/s1_trusted_observer.py:96-120, :205-306`; the Stage 1 equivalence test already proves the new observer's source policy is equivalent to the historical `safe_source` on 7 parametrised sources (`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:43, :121`) |
| Evidence | Identical evidence kinds, identical retention, identical key custody, identical signing roles | `s1_protocol.md:116-144` (the 15-row evidence-chain table) |
| Evaluator | **The same frozen evaluator** for both arms: the Stage 1 `full` (E3) contract, plus the **frozen historical Stage01 pair** as a baseline column on the same bundles | `s1_protocol.md:89-112`; `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:136-156` |
| Decision vocabulary | Identical tri-state: `ATTRIBUTED_SUCCESS` / `REJECT` / `INCONCLUSIVE` | `s1_protocol.md:157-168` |
| Ground truth | One recorded pair per case, kept distinct: `expected_decision` and `expected_crypto_success` | `s1_protocol.md:203-208`; `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:67` |
| Denominators | One, stated, with malformed and honest-control inclusion declared | `s1_protocol.md:212-237`; the historical denominator defects in `stage0/AGENT2_HISTORY_FORENSIC_EXTRACTION.md` (D1–D6) are the cautionary precedent |
| Replay ledger | **Per-arm isolated.** A shared ledger would let one arm's submissions consume the other's slots and mask the very check a family is meant to exercise — the exact defect recorded as Stage 1 deviation **D-01** (`stage1_attribution/s1_deviations.md:20-39`) | `s1_deviations.md:20-39` |
| Transport | **Identical for both arms.** See §4.3. | — |

### 4.3 Transport: the Stage 3 finding constrains this design

Stage 3 established that there is **no authorised ingress** into the evaluation path
(`stage3_boundary/STAGE3_BOUNDARY_ANALYSIS.md` §3, §4). Two design rules follow, and both are
binding:

1. **If no authorised gateway is identified, both arms must submit in-process, identically.**
   The only currently available path is the same-process construction used by
   `run_contract_sound_agent_replacement_v1.py:165-178` and by the Stage 1 runner. Arm A and Arm S
   must use the *same* construction code.
2. **It is forbidden for one arm to submit through a gateway and the other not to.** If an
   authorised gateway is later identified and used, **both** arms must use it, with the same
   transport, the same request shape and the same bytes-on-the-wire check. Otherwise the arm
   difference is confounded with the transport difference, and the result is uninterpretable —
   a transport effect would be indistinguishable from an AI effect.

This rule is a direct consequence of the Stage 3 result and is stated here so that it cannot be
violated by convenience.

### 4.4 Attempt budget

* **Equal per arm, per case, declared before the run.** The historical precedent is
  `run_contract_sound_agent_replacement_v1.py:125` (72 scheduled sessions, asserted) and the H1-R3
  schedule (852, hash-pinned in `H1R3_FREEZE.json` → `schedule_sha256`).
* **One submission per case per arm**, with `automatic_retries: 0`, `seed_replacement: False`,
  `adaptive_stopping: False` — matching the historical controls
  (`run_contract_sound_agent_replacement_v1.py:134-136`).
* **A single run.** No case is re-run with a patched configuration; a component crash is recorded
  as the case outcome (`s1_protocol.md:279-280`).
* **The budget is stated in provider calls**, with the exact number, and reconciled against the
  programme-level $50 alert / $200 hard stop
  (`ACTS_Attack_Continuous_Research_Execution_Plan.md:206`) and against the calls already recorded
  in the sibling tree (§2.5).
* **No paid fallback** (§3 #5): any route that is not the exact approved one must cause a
  fail-closed abort, and the abort must be recorded as an outcome, not silently retried.
* **Because the route is non-deterministic** (`temperature`/`seed` unavailable, §3 #6), "one
  submission per case" is *not* a replicate of a fixed function. The budget must therefore be
  declared as **N independent draws per case** if the design wants per-case variance, and the
  analysis must treat the case as the unit of pairing, not the individual draw.

### 4.5 Evidence privileges

Both arms get **identical** evidence privileges — this is the single most important matching
requirement, because the historical failure mode was an *evidence* asymmetry, not a *producer*
asymmetry:

* The same evidence kinds are produced for both arms
  (`s1_protocol.md:116-144`).
* The same trusted execution observer signs both arms' facts, with the same key custody
  (`s1_trusted_observer.py:96-120`; key custody at `s1_deviations.md:86-100` — D-05, with the
  private keys outside the repository at `/tmp/acts_s1_keystore` or `$ACTS_S1_KEYSTORE`).
* The same reference verifier — the **frozen** `contract_sound_stage01_reference_verifier_v2.py`,
  hash-pinned at load time, fail-closed — recomputes the cryptographic predicate for both arms
  (`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:43`).
* The same retention policy for both arms' raw provider/model outputs and both arms' transcripts.
* The same role authorisation (`protected_signing`) and the same replay/context binding.

**No arm may be given an evidence privilege the other lacks.** In particular, the AI arm may not
be allowed extra retries, extra queries, extra tools, or a richer transcript format that the
scripted arm is denied — any of these converts a capability difference into an evidence
difference and destroys the comparison.

### 4.6 Controls

| Control | Requirement | Why |
|---|---|---|
| **Positive control** | Every honest case must be `ATTRIBUTED_SUCCESS` under the E3 contract for both arms. If not, the experiment is **NOT OPERATIONAL** and nothing else is reported. | `s1_protocol.md:248-250` |
| **Baseline positive control** | The frozen Stage01 pair must ACCEPT at least one honest case; otherwise the Stage01 comparison is **VOID** (strawman). | `s1_protocol.md:251-253` |
| **Negative controls** | Family A's cryptographically-false members (A03, A04, A06, A07, A08) must not be promoted by any contract claimed to bind the reference result. | `s1_protocol.md:255-256` |
| **Cross-implementation check** | E3's reference verdict and the frozen Stage01 reference verdict are computed by the *same* frozen predicate; any disagreement is a validity failure. | `s1_protocol.md:257-260` |
| **Claim-invariance control** | Two bundles over byte-identical evidence that differ only in `claims` must receive the same verdict — proving the verdict is a function of the evidence, not of the claim. | `s1_protocol.md:261-265` |
| **Arm-parity control** | For each case, the *inputs* delivered to the two arms must be byte-identical where they are comparable, and the difference must be recorded in a manifest before the run. | §4.2 |
| **Transport control** | The bytes received by the evaluator from each arm are hashed and compared against the bytes the producer emitted. | §4.3 |
| **Observer control** | A policy-violating program is refused, not executed — for both arms. | `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:125` |
| **Replay control** | A second evaluation of the same bundle against an already-consumed ledger is REJECTed (`context-replay-exceeded`) — **per arm**. | `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:123`; `s1_deviations.md:20-39` |
| **Freeze preflight** | The audited `heb1_remediation_v1/integrity/manifest_verifier.py` verifies the freeze manifest; the run **refuses to start** if the preflight fails, and the manifest is re-verified after execution. | `s1_protocol.md:269-283` |

### 4.7 Independent final-claim adjudication

The final attribution claim is **not** made by the arm runner and **not** by the party that
designed the arms. It is adjudicated from retained raw facts by an independent adjudicator:

* the adjudicator consumes the observer's signed facts, the reference verifier's signed verdict,
  and the bundle index — and **re-derives** the parsed output from the captured stdout rather
  than trusting the submitted output file
  (`deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:35`);
* it applies the same six-level ladder and the same tri-state vocabulary
  (`s1_protocol.md:146-168`);
* it runs on **both** arms' bundles with the **same** code, after the fact, from the retained
  records — not from any arm-level summary;
* every reported metric is recomputed from raw artefacts by a separate, measurement-free
  summariser (`s1_metrics.py`, per `s1_protocol.md:274-276, :283`).

---

## 5. How a difference would be interpreted

**The governing rule, from the project's own record:** *"Even under the stated matched experiment,
an AI-only failure would establish an arm-specific outcome under that prompt/model/search setup,
not an AI-specific security mechanism or novelty."*
(`heb1_remediation_v1/scientific_corrections/HISTORICAL_CORRECTION_LEDGER.md:29`, correction C-04;
restated at `stage0/AGENT5_PRIOR_ART_NOVELTY_MATRIX.md:207, :290, :294`.) C-04 further lists the
alternative explanations that must be excluded: *"The AI arm may differ in search capability,
time allocation, parser interaction, source generation, or error distribution."*

### 5.1 The four-cell interpretation matrix

Cells are defined by (scripted-arm outcome) × (AI-arm outcome), where the outcome is the
**independent adjudication verdict** for the submitted bundle.

| # | Cell | Scripted arm | AI arm | What the cell supports | What the cell does **not** support | Required follow-up |
|---|---|---|---|---|---|---|
| **1** | **Both arms fail identically** | REJECT (or INCONCLUSIVE) | REJECT (or INCONCLUSIVE), same verdicts, same cases | A **generic** provenance-composition failure, reproducible with no model in the loop. This is the historically observed shape (the scripted composer). | Any AI-specific claim. It is evidence that the failure does **not** depend on an AI producer. | Report as a generic result. Contrast with the prior-art baseline (RFC 9334 §8.1 names this mechanism). |
| **2** | **The gateway / transport rejects both** | submission refused before evaluation | submission refused before evaluation | **Nothing about the AI question.** The test measured the transport, not the arms. | Any comparison at all. | Re-run only if a transport defect is identified and fixed; otherwise the experiment is **VOID** on the AI question and must be reported as void, not as a null result. |
| **3** | **Scripted mixed; AI arm at least as good** | a mix of attributed and refused bundles | a mix, with the AI arm's false-attribution rate **not higher** | That the *generic* failure mode is **not** aggravated by an AI producer under this setup. A bounded, setup-specific non-differentiation. | "AI agents are safe." It is a null under one prompt, one model, one route, one budget, one corpus. | Report as a bounded null with the setup fully specified, and with the power/interval honestly stated. |
| **4** | **Only the AI arm produces unsupported attribution** | no unsupported attribution | unsupported attribution on ≥1 case the scripted arm refused | An **arm-specific outcome** — a candidate AI-arm failure mode, or an interaction between the AI arm and the contract. | **Not** an AI-specific security mechanism, **not** novelty, **not** a live-campaign finding. | **Mandatory mechanism-level tracing** (§5.2) before any AI-specific characterisation. If the tracing cannot exclude the C-04 alternative explanations, the result is reported as an arm-specific outcome with the confounders named, and nothing more. |

### 5.2 Mechanism-level tracing required before any AI-specific claim

An outcome difference in cell 4 is a *starting point*, not a finding. The following must be
produced, retained, and independently reviewed before the word "AI" appears in any characterisation:

1. **Intermediate-decision tracing.** The *intermediate* decisions, not just the final artifact:
   the AI arm's per-call outputs, its parse failures, its internal iteration count, and the exact
   source text it produced; the scripted arm's equivalent decision trace. The historical evidence
   already shows why: the H1-R3 evidence package claimed a specific wrong formula appeared in
   programs from R0, R1 and R2, but the retained sources support it in only **3 of 26** failing
   ECDSA programs, **none** of them in R1 or R2, across **22 distinct** text shapes
   (`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:421-452`). A *reading* of the printed code is not
   a telemetry trace, and a difference in printed code is not a difference in mechanism.
2. **Capability confound excluded.** Equal external attempt budget (§4.4), and the AI arm's
   *internal* search/iteration count measured and reported, since the arms necessarily differ in
   internal search.
3. **Time / budget confound excluded.** Equal wall-clock and equal token budget per case, or the
   difference stated and its effect bounded.
4. **Transport confound excluded.** Identical transport for both arms (§4.3), with a bytes-on-the-wire
   check.
5. **Parser / interface confound excluded.** The `json-last-line-v1` parser and the one-JSON-object
   rule are identical for both arms, and parse failures are recorded separately from cryptographic
   failures — the distinction the H1-R3 taxonomy actually used
   (`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:385-395`).
6. **Cryptographic-competence confound excluded.** This is the confound the historical data makes
   concrete: of the 28 cryptographic failures in H1-R3, **19 (67.86 %)** show the textbook
   "d wrong, k right" algebra-slip signature — **19/26 = 73.08 %** of ECDSA-family failures, and
   **24/26 = 92.31 %** on the broader reading — while only **2 (7.14 %)** are XOR-family content
   mismatches and **2 (7.14 %)** are `k`-only errors
   (`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:397-413`). **Most cryptographic failures were
   ECDSA algebra errors, not representation-decoding failures.** Therefore: an arm difference in
   *unsupported attribution* must be separated from an arm difference in *cryptographic
   competence* before it can be attributed to anything AI-shaped. A "the AI arm is worse at
   crypto" difference is a **capability** difference, and must be reported as such.
7. **Independent re-adjudication** of the final claim from raw records by a party that ran neither
   arm (§4.7).
8. **Prior-art check against the fair baselines.** Even a mechanism-level finding must be
   positioned against arXiv:2610.16067 and arXiv:2603.14332, not against V0/V1, and against
   RFC 9334 §8.1 — because the mechanism family is named in the standard
   (`stage0/AGENT5_PRIOR_ART_NOVELTY_MATRIX.md:237, :262, :290-294`).
9. **Pre-registration.** The decision rule, the case set, the denominators, the attempt budget and
   the analysis plan are frozen and hash-pinned **before** the first call, with the audited
   fail-closed preflight gating the run (`s1_protocol.md:269-283`); no metric, threshold,
   denominator, decision rule or case expectation is changed after the run begins
   (`s1_deviations.md:181-184`).

---

## 6. Standing prohibitions for Stage 4

Observed in this document, and to be observed by any future Stage 4 execution:

* **No model call was made** in producing this status, and none may be made until §3 is answered
  in writing.
* **The historic H1-R3 852 sessions are not to be re-run.** They are read-only *existing
  evidence*. The 852 sessions, the frozen schedule (`H1R3_FREEZE.json` → `schedule_sha256`), and
  the raw `runs/confirmatory/results.jsonl` are inputs to the analysis in §7, not a campaign to
  be repeated. Re-running them would also be a fresh 852-call campaign, which is outside any
  budget that has been authorised.
* **No credential is read, printed, transmitted, hashed into an artifact, or stored.** Only the
  *existence* of credential sources was checked (§2.4).
* **No network request** was made in producing this document.
* **No package was installed**; no historical file was modified, reset, cleaned or committed.
* **No arm is executed, and no AI-specific claim is made or inherited** in this document.
* If the run is later authorised, the standing prohibitions of the historical campaigns carry
  over unchanged: no retries, no seed replacement, no adaptive stopping, no paid fallback, no
  study expansion (`run_contract_sound_agent_replacement_v1.py:134-136`).

---

## 7. The evidence already in hand that bears on the AI question

This is what Stage 4 would build on, and it must be read with its defects attached.

### 7.1 The H1-R3 result

H1-R3 (`sp2027/analysis/h1r3_20261019/`) is the largest model-backed representation-contrast
dataset in the repository: **852 sessions**, route `claude-sonnet-4-6-free`, provider status
`SUCCESS` for 852/852, `http_status` 200 for 852/852, `finish_reason` `end_turn` for 852/852
(`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:37, :44, :127-129`).

**Primary result (L3, pooled, 128 paired instances per contrast, ±10 pp equivalence margin,
δ = 0.10):**

| Contrast | n | R0 | Arm | τ | 95 % CI | McNemar p (exact, 2-sided) | Decision |
|---|---:|---:|---:|---:|---|---:|---|
| L3 pooled, R1 vs R0 | 128 | 125/128 | 126/128 | **+0.007812** | **[−0.0234, +0.0391]** | 1.0000 | `EQUIVALENT_WITHIN_MARGIN` |
| L3 pooled, R2 vs R0 | 128 | 125/128 | 124/128 | **−0.007812** | **[−0.0469, +0.0312]** | 1.0000 | `EQUIVALENT_WITHIN_MARGIN` |

(`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:287-294, :320`.) **Both L3 pooled representation
contrasts fall inside the ±10 pp equivalence margin**, with the full 95 % CI inside `[−δ, +δ]`.

**Exploratory L2 ECDSA contrast (R2 vs R0, 32 paired instances):** R0 **32/32**, R2 **25/32**,
τ = **−0.2188** (−21.88 pp), 95 % CI **[−0.3750, −0.0938]**, exact two-sided McNemar
**p = 0.0156**, decision `INCONCLUSIVE` (the CI upper bound −0.0938 does not clear −0.10, so the
frozen rule does *not* call it "worse than reference")
(`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:316, :351-377`).

**Three properties of this dataset that bear directly on Stage 4:**

1. **The composer was scripted, not a model.** The historical HEB-1 composer — the artefact-
   composition adversary in the correction ledger — was **scripted**
   (`stage0/AGENT5_PRIOR_ART_NOVELTY_MATRIX.md:290, :294`;
   `heb1_remediation_v1/scientific_corrections/HISTORICAL_CORRECTION_LEDGER.md:29`, C-04).
   The historical evidence therefore establishes a **generic** provenance-composition failure
   reproducible with **no model in the loop**, and supplies **zero** evidence that AI agents make
   the failure more likely, more severe, or qualitatively different.
2. **H1-R3 contains no scripted arm at all.** All 852 sessions were provider calls on
   `claude-sonnet-4-6-free` (852/852 `route` and `provider_model`; arms R0 276, R1 256, R2 256,
   R4 64; kinds `primary` 768, `noise` 64, `c0` 20 — `stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:137-149, :189-202`).
   **H1-R3 is a within-AI representation-contrast study, not an AI-versus-scripted study.** It
   therefore cannot be cited as prior evidence of an AI-versus-scripted difference; it is prior
   evidence about *representation* inside a single producer class.
3. **Most cryptographic failures were ECDSA algebra errors, not representation-decoding
   failures** — the breakdown in §5.2 item 6 (19/28 = 67.86 % textbook "d wrong, k right";
   19/26 = 73.08 % of ECDSA failures; 24/26 = 92.31 % on the broader "d wrong" reading; only
   2/28 = 7.14 % XOR content mismatches)
   (`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:397-413`).

### 7.2 The material defects found independently in the H1-R3 material

These were found by an independent forensic pass
(`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md`), and Stage 4 must carry them forward rather than
build on the published aggregates as they stand.

**Defect A — the success denominator is 801, not 821.** The field that defines "success" for the
estimand is `terminal_success` (`int`, 0/1), and it is `1` for **801** of 852 records. The
`terminal` *stage label* reads `SUCCESS` for **821**. The 20-record gap is fully explained: **20
records have `terminal == "SUCCESS"` but `terminal_success == 0`**, and all 20 are the C0
abstention control (`kind == "c0"`, `arm == "R0"`), all 20 with `reference.abstained == True` and
`c0_correct_abstention == 1`. The runner code that produces this is at `h1r3_run.py:429-436`. The
defect is in the *reporting*: `H1R3_ANALYSIS.md` and `H1R3_EVIDENCE_PACKAGE_20261019.md` publish
only the 821 figure and **nowhere state 801**; a reader who takes "821 SUCCESS" as the numerator
of a success rate is off by the 20 C0 abstentions, which are *not* exploit successes
(`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:60-93`).

**Defect B — the manuscript's 123/128 is wrong; the recomputed value is 124/128.** The L3 pooled
R2 successes are **124/128** (XOR 63/64 + ECDSA 61/64). The wrong figure appears in **6 places**,
including three manuscript sources
(`sp2027/paper/capability_merge_20261016_h1r3_20261019/main_sections/08_h1r3.tex:13-14`,
`…/main_sections/08_information.tex:98-99`, `…/supp_sections/S26_h1r3.tex:33-34`) and
`H1R3_CAPABILITY_MERGE_INTEGRATION_REPORT.md:14`. The wrong number is **self-contradictory within
its own sentence**: the same passage reports `τ_{R2−R0} = −0.008`, but 123/128 against R0 = 125/128
gives τ = −0.0156, whereas −0.008 = −1/128 = (124−125)/128. The τ is right; the count is wrong.
The defect entered at the **manuscript-integration step**, not the analysis step:
`H1R3_ANALYSIS.md`, `H1R3_ANALYSIS.json`, `H1R3_PAPER_INTEGRATION_REPORT.md` and
`H1R3_EVIDENCE_PACKAGE_20261019.md` are all correct
(`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:634-655`).

**Defects C–E (also material, and all in the same register).**

* **C — the freeze contract does not cover the results.** `runs/confirmatory/results.jsonl` appears
  in **no** freeze or amendment manifest; its SHA-256 is "computed by me, recorded nowhere". The
  same applies to `H1R3_ANALYSIS.{json,md}`, `H1R3_FAILURE_DOSSIER.json`,
  `H1R3_INTEGRITY_AUDIT.json`, `EXECUTION_MANIFEST.json` and all 852 session directories
  (`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:477`).
* **D — the retained runner is not the frozen runner, and the change is unrecorded.** The
  on-disk `h1r3_run.py` hashes to `6605cf7a…` against the frozen `b0ba8cc2…` declared in the
  freeze **and both amendments**; `h1r3_analyze.py` hashes to `3bc48e6f…` against the recorded
  `9b813806…` — *"the recorded hash never matched the file that produced the analysis"*. The
  retained bytecode shows the change is exactly one function, `require_health()`: the frozen
  version required **all 8** checks to pass; the current on-disk version passes on
  **probe-only** (`checks["probe_200"] and checks["probe_model_matches"]`) and adds
  `strict_provider_certification: False`. The relaxation was made **~7 hours after the
  confirmatory campaign ended**, and the retained `EXECUTION_MANIFEST.json` proves the *frozen*
  gate is the one under which the data was collected
  (`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:480-547`).
* **E — the failure dossier is silently scoped.** `H1R3_FAILURE_DOSSIER.json` reports
  `"failures": 30` against the run summary's 31, because `h1r3_failures.py:42` filters on
  `kind == "primary"` and thereby excludes the single R4 noise-replicate crypto failure — with
  **no scope note** in the dossier's `summary` block
  (`stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md:657-670`).

**What this means for Stage 4.** Two of these defects (A and B) are exactly the class of
error the Stage 4 design must be built to prevent: a **numerator/denominator mismatch** and an
**un-recomputed manuscript figure**. They are carried forward as design requirements: the
denominator must be stated and the "success" field must be named (as Stage 1 does at
`s1_protocol.md:212-237`); and every published figure must be recomputed from raw artefacts by a
measurement-free summariser (`s1_metrics.py`), with the manuscript-integration step treated as a
separate, verified operation rather than a copy. Defect D is carried forward as a *freeze
requirement*: the code that runs must be the code that is hashed, and the manifest must be
re-verified after the run.

### 7.3 The Stage 1 experiment's producer arm is scripted — and therefore supplies no AI evidence

Stated plainly, because it is the single most consequential thing to get right here:

* Stage 1's producer arm is **scripted**, not a model. `s1_protocol.md:41-44`: *"The producer arm
  is scripted, not a model. Therefore no AI-specific claim may be derived from any result in this
  experiment."* `s1_deviations.md:179`: *"No model / provider call was made. The producer arm is
  scripted."* `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md:20`: *"**NOT** an AI-specific result
  — the producer arm is **scripted**, not a model."* And `:176`: *"The producer arm is scripted. No
  AI-specific claim is possible from this experiment."*
* Therefore the Stage 1 result — 0/25 false attributions for E3 against 13/25 for E0, 2/25 for the
  frozen Stage01 pair, 5/5 correct INCONCLUSIVE classifications — is a result about **contracts**,
  not about producers. It measures the *discriminating power of evaluator contracts* on a
  constructed corpus. It says nothing about AI behaviour.
* The H1-R3 result (§7.1) is a result about **representation** within one producer class. It also
  says nothing about AI-versus-scripted, because it contains no scripted arm.
* The historical HEB-1 composer was **scripted** (C-04), so the project's own historical evidence
  on the composition-failure mechanism is a **generic** result.

**The net position: the repository currently contains zero measurements that bear on whether an AI
producer behaves differently from a scripted producer in the attribution path.** Stage 4 is the
experiment that would produce the first one, and it is blocked on §3.

---

## 8. Machine-readable status block

```
STAGE4_STATUS: BLOCKED_BY_RESOURCE_OR_AUTHORIZATION
STAGE4_BLOCKING_GAP: G-4_NO_MODEL_PROVIDER_AUTHORISATION_FOR_A_LIVE_AI_PRODUCER_ARM
STAGE4_MODEL_CALLS_MADE: 0
STAGE4_PROVIDER_CALLS_MADE: 0
STAGE4_NETWORK_REQUESTS: 0
STAGE4_PACKAGE_INSTALLS: 0
STAGE4_HISTORICAL_SESSIONS_RERUN: 0
STAGE4_CREDENTIALS_READ_PRINTED_TRANSMITTED_OR_STORED: NONE
STAGE4_ARMS_EXECUTED: NONE
STAGE4_AI_SPECIFIC_CLAIM_MADE: NONE
STAGE4_CONFIRMATIONS_REQUIRED: 7
STAGE4_CONFIRMATIONS_OBTAINED: 0
STAGE4_CONFIRMATION_1_PROVIDER_AUTHORISATION: MISSING
STAGE4_CONFIRMATION_2_AVAILABLE_MODEL_IDENTITY: MISSING
STAGE4_CONFIRMATION_3_SPENDING_LIMIT: MISSING
STAGE4_CONFIRMATION_4_MAXIMUM_CALL_COUNT: MISSING
STAGE4_CONFIRMATION_5_NO_PAID_FALLBACK: MISSING
STAGE4_CONFIRMATION_6_SAMPLING_CONTROLS_AND_UNAVAILABLE_CONTROLS: MISSING
STAGE4_CONFIRMATION_7_PROMPT_AND_OUTPUT_RETENTION_POLICY: MISSING
STAGE4_DESIRED_ROUTE: claude-sonnet-4-6-free
STAGE4_HISTORICAL_PROVIDER: https://api.apmix.ai
STAGE4_ROUTE_AUTHORISED_IN_THIS_SESSION: NO
STAGE4_REPOSITORY_RECORDED_FALLBACK_ROUTE: openrouter/minimax/minimax-m3.1-flash:free
STAGE4_FALLBACK_ROUTE_AUTHORISED_IN_THIS_SESSION: NO
STAGE4_STAGE1_PRODUCER_ARM: SCRIPTED
STAGE4_STAGE1_SUPPLIES_AI_EVIDENCE: NO
STAGE4_H1R3_SESSIONS: 852
STAGE4_H1R3_L3_POOLED_R1_VS_R0_TAU: 0.007812
STAGE4_H1R3_L3_POOLED_R2_VS_R0_TAU: -0.007812
STAGE4_H1R3_EQUIVALENCE_MARGIN_PP: 10
STAGE4_H1R3_L3_POOLED_BOTH_EQUIVALENT_WITHIN_MARGIN: YES
STAGE4_H1R3_L2_ECDSA_R2_VS_R0: 25/32 vs 32/32
STAGE4_H1R3_L2_ECDSA_TAU: -0.2188
STAGE4_H1R3_L2_ECDSA_CI: [-0.3750,-0.0938]
STAGE4_H1R3_L2_ECDSA_MCNEMAR_P: 0.0156
STAGE4_H1R3_L2_ECDSA_DECISION: INCONCLUSIVE
STAGE4_H1R3_HISTORICAL_COMPOSER: SCRIPTED
STAGE4_H1R3_TERMINAL_SUCCESS_COUNT: 801
STAGE4_H1R3_TERMINAL_STAGE_SUCCESS_COUNT: 821
STAGE4_H1R3_C0_ABSTENTION_RECORDS_TERMINAL_SUCCESS_BUT_NOT_SUCCESS: 20
STAGE4_H1R3_MANUSCRIPT_FIGURE: 123/128
STAGE4_H1R3_RECOMPUTED_FIGURE: 124/128
STAGE4_H1R3_CRYPTO_FAILURES_ECDSA_ALGEBRA_SHARE: 19/28
STAGE4_H1R3_CRYPTO_FAILURES_ECDSA_ALGEBRA_SHARE_OF_ECDSA: 19/26
STAGE4_H1R3_CRYPTIC_FAILURES_NOT_REPRESENTATION_DECODING: 26/28
STAGE4_TRANSPORT_RULE: BOTH_ARMS_MUST_USE_AN_IDENTICAL_PATH
STAGE4_ADJUDICATION_RULE: INDEPENDENT_ADJUDICATOR_FROM_RETAINED_RAW_RECORDS
STAGE4_AI_SPECIFICITY_RULE: OUTCOME_DIFFERENCE_IS_NOT_A_MECHANISM__C-04
```

**Human-readable restatement.** Stage 4 cannot be run: all seven required confirmations are
missing in this session, and no model call was made. The matched-arm design is specified in
full so that it is ready to preregister the moment authorisation exists. The repository's existing
evidence on the AI question is: an 852-session model-backed representation study whose L3 pooled
contrasts are inside the ±10 pp equivalence margin, whose historical composer was **scripted**
rather than a model, whose cryptographic failures were overwhelmingly **ECDSA algebra errors**
rather than representation-decoding failures, and whose published aggregates carry two material
defects (801 vs 821 on the success denominator; 123/128 vs the recomputed 124/128) that any
future Stage 4 analysis must not inherit.

---

*Prepared 2026-10-20 as part of the ACTS-Attack next-phase programme. Companion documents:
`stage0/STAGE0_RESOURCE_GAPS.md` (gap G-4), `stage0/STAGE0_REPOSITORY_INVENTORY.md:127` (route
record), `stage0/AGENT4B_H1R3_FORENSIC_EXTRACTION.md` (H1-R3 recomputation and defects),
`stage0/AGENT5_PRIOR_ART_NOVELTY_MATRIX.md` (AI-specificity assessment),
`stage1_attribution/s1_protocol.md` and `s1_deviations.md` (Stage 1 preregistration, scope and
deviations), `deliverables/END_TO_END_ATTRIBUTION_RESULTS.md` (Stage 1 results),
`stage3_boundary/STAGE3_BOUNDARY_ANALYSIS.md` (Stage 3 boundary finding).*
