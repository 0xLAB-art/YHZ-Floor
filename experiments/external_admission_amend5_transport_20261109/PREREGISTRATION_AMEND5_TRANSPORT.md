# PREREGISTRATION — Amendment 5: transport-repaired external admission panel

**Protocol:** PHASE2-EXTERNAL-ADMISSION-AMEND5-TRANSPORT-v1 ·
**Namespace:** `sp2027/research_execution/external_admission_amend5_transport_20261109`
· **Registered:** 2026-11-09, before the first evidence call.

## 1. Question

Amendment 4 gave the registered portability falsifier its first test on the
paper's GPT-family labels, and the audit decomposition
(`external_admission_amend4_frontier_20261106/FINDING_TRANSPORT_DECOMPOSITION.md`,
schema `amend4-transport-decomposition-audit/1`) measured that the panel's
null was dominated by two **transport** layers, unrelated to agent behavior:

1. **Empty-visible-content completions** — 220/279 recorded provider calls
   (78.8%) ended `stop_reason: length` with an EMPTY visible content block
   under the `/v1/messages` facade over a `chatcmpl-` backend; 1,323,000
   output tokens were charged for zero visible text; all 108 give-up
   sessions (61 primary + 47 recovery) are empty-visible-content
   `('length','length')` turn pairs, i.e. the AGENT_GIVEUP class measured
   the route, not the agent;
2. **Gateway content filter** — 216/216 provider-failure events were HTTP
   400 `content-blocked` (re-verified on `/v1/responses` and under the new
   funded account on 2026-11-09: blocked pairs are a gateway-wide,
   account-independent property), erasing 72/168 slots = 42.9% of the
   grid's denominators before any measurement.

Amendment 5 repeats the registered protocol on a transport whose
completions are visible (OpenAI Responses API; the `reasoning.effort`
field is omitted — measured ignored by the backend), with the census-pass
(task, rep, label) map registered before the freeze, a 4-turn loop with
captured-output feedback, and explicit provider-side status classes
(COMPLETION_TRUNCATED alongside the carried CRASH class).
The Amendment-3 and Amendment-4 records stand unchanged; never pooled.

## 2. Design (frozen constants)

- **Transport:** `agentrouter /v1/responses` (OpenAI Responses API),
  `max_output_tokens = 12000` per call (calibrated below), temperature
  omitted, `reasoning.effort` field OMITTED (measured: the backend ignores
  it — effort=low consumed a full 16,000-token budget with zero visible
  text at calibration), Python-stdlib client, `claude-cli` User-Agent.
  Per-call attestation recorded: `model_echo`, `finish_reason/status`,
  `usage.output_tokens_details.reasoning_tokens`, transport tag
  `responses_api`.
- **Cap calibration (registered, from non-evidence calibration probes,
  2026-11-09):** at cap 4200 the lowe label-run ruminated to
  `incomplete` with zero visible text; at cap 12000 the same frozen pair
  completed on gpt-6-astra (reasoning 7,099 + 2,076-char JSON program) and
  gpt-6.1-sol (reasoning 4,142 + 2,052-char JSON program). 4200 reproduces
  the Amendment-4 empty-completion regime; 12000 is the smallest cap under
  which a registered label emitted a full program on a task other than
  eps, so it is the registered evidence-call budget.
- **Labels (unchanged):** `gpt-5.6-sol`, `gpt-6-astra`, `gpt-6.1-sol` — the
  paper's registered GPT-family labels; provider-attested at call time,
  never digest-pinned.
- **Pair set (registered from the completeness census, before the freeze):**
  the 14 frozen (task, representation) prompt pairs of Amendments 3/4 are
  hashed byte-identical (`PROMPT_HASHES.json` verified at prep and
  re-verified at every live start). A compat pre-gate measured the OLD
  calibration (cap 4200 + effort field, `COMPAT_GATE_AMEND5.json`): 6
  pairs HTTP-400 content-blocked (re-verified thrice — messages wave,
  responses re-probe, funded account — label-independent), 6 pairs
  rumination-empty at 4200, 2 pairs (eps R0+RT) passing. The census
  (`completeness_census_amend5.py`) upgrades this to the REGISTERED
  (pair, label) map at the calibrated cap: every non-blocked pair × every
  label, one non-evidence probe each, classified
  PASS_VISIBLE_JSON / COMPLETION_RUMINATION_OVERFLOW / other. The
  runner's plan is built ONLY from census `pass_combinations`
  ((task, rep, label) triples × seeds 425–428); every other entry is a
  measured boundary with its own census row — a two-sided exclusion,
  never a zero, never silent, never agent behavior. Blocked pairs
  (`babycrypto` R0+RT, `eps_part2` R0+RT, `almost_xor` RT, `lowe` RT)
  never enter any label's plan (frozen from the thrice-replicated
  filter measurement).
- **Grid:** census-defined. Measured census state (non-evidence, cap
  12000): eps R0 and eps RT pass on all three labels; lowe R0 passes on
  all three; almost_xor R0 and another_xor R0+RT ruminate to the full
  12k budget on every label probed (astra another_xor R0 completed with
  573 visible chars but no parseable JSON contract — not a pass). Four
  crack_me probes were cut mid-census by the operator account's quota
  exhaustion (HTTP 403, remaining quota −$304.72, 2026-11-09) and are
  completed by the registered resume script BEFORE the freeze — the
  census JSON is final before anything is frozen. The exact session
  count is whatever the final census registers, printed by `--dry-run`
  before the freeze; it is never enumerated from optimism.
  Seeds label the session only (Amendment-3 convention); sweep receipt:
  `seed_sweep_AMEND5_SEED_SWEEP.json` (range previously unregistered).
- **Tasks/artifacts/prompts:** byte-identical copies of the Amendment-3
  frozen inputs (hash-asserted at runtime against `PROMPT_HASHES.json`).
- **Turns:** ≤4. Turn-1 prompt is the frozen prompt; turns >1 append the
  registered feedback: on parse failure,
  `REVISION REQUEST ... {\"code\": ...}`; on execution/oracle rejection,
  `EXECUTION_OR_ORACLE_REJECTED` **plus the captured stdout tail (≤600
  chars) and stderr tail (≤600 chars)** — the blind-feedback defect of
  Amendments 3/4 is withdrawn, identically for both arms and every label.
- **Sandbox:** `python -I prog` with the declared artifacts only, 30 s exec
  timeout — verbatim from Amendment-3.

## 3. Oracle — dual codings, unchanged from Amendment 4

For every executed program, both codings are computed and recorded per
turn; **acceptance (`SUCCESS`) is C1**; C2 is reported side by side (P024b
both-codings discipline; declared before any outcome):

- **C1 (primary):** `stage == output AND returncode == 0 AND
  stdout.strip() == pinned answer` (whole stripped stdout).
- **C2 (second admissible normalization):** first flag-shaped token
  extracted by `flag\{[ -~]*?\}` equals the pinned answer, rc==0,
  stage==output.

The per-pair representation contrast, its movement (stress − declared), and
the falsifiers are computed **under each coding separately**; both verdicts
are the product. The codings' disagreement remains a registered measurement
of the answer-normalization owner (Amendment-3 layers 1; Amendment-4 eps/lowe split).

## 4. Status taxonomy — COMPLETION_TRUNCATED added; CRASH carried

Terminal states: SUCCESS, CRASH (final submitted program exited non-zero),
ORACLE_FAIL (final submitted program ran clean, rc=0, failed both codings),
TIMEOUT, AGENT_GIVEUP (submissions ≥0, agent produced visible content and
never submitted), MODEL_REFUSAL, TOOL_FAILURE, PROVIDER_UNAVAILABLE,
**COMPLETION_TRUNCATED (new, provider-side)**, HARNESS_ERROR.

- **COMPLETION_TRUNCATED:** a provider response with `stop_reason: length`
  / `status: incomplete` and an EMPTY visible completion. It is never coded
  as an agent decision. Rule: re-attempt ≤2 per call per the two-sided rule;
  if a session ends with zero submissions AND at least one
  empty-visible-completion response, its terminal class is
  `COMPLETION_TRUNCATED` (not AGENT_GIVEUP). At the registered 12k cap this
  class measures genuine reasoning-budget exhaustion — the census rows
  prove it is task- and label-dependent (eps 0.5–3.1k reasoning finishes;
  almost_xor/another_xor/crack_me exceed 12k on every label tested), which
  is itself a registered capability×budget boundary measurement, not a
  transport defect.
- **Honest-capability slot:** if a session produces visible content,
  submits nothing parseable over its 4 turns, and shows no refusal marker,
  it remains AGENT_GIVEUP — that class now measures actual agent behavior
  on this transport (in Amendment 4 it measured the route 108/108).
- **Terminal precedence (registered):** provider-side category
  (PROVIDER_UNAVAILABLE / TIMEOUT / HARNESS_ERROR) > MODEL_REFUSAL >
  COMPLETION_TRUNCATED > AGENT_GIVEUP > TOOL_FAILURE > task-side classes
  (SUCCESS / CRASH / ORACLE_FAIL / TIMEOUT).

## 5. Admission arms and regrade

The three frozen admission arms apply unchanged to retained programs:
declared v4 (policy v3), stress-repaired, cleanup; regrade scripts of the
locked machinery recompute qualification/output preservation on this
namespace's frozen programs. Per-pair movement = stress contrast − declared
contrast, under C1 and C2 separately; undefined (no denominator in at least
one representation) is never counted as zero.

## 6. Registered falsifiers (per coding)

- **F1 (mechanism ports):** movement outside the ±10 pp margin on **≥4 of
  7 tasks** on at least one label? (the Amendment-3/4 registered bar;
  unchanged — with the measured caveat that the 2 wholly-filtered tasks
  cannot move, the bar is reachable max out of 5 measurable tasks).
- **F2 (honest null band):** every defined contrast within the margin.
- **F3 (preservation):** cleanup preserves byte-identical stdout on all
  edited programs (0 lost/None by construction).
- **Cross-label rule:** F1 TRUE on ≥2 of 3 labels (with F3 PASSED).

## 7. Operational rules (frozen)

- **Two-sided provider-failure rule (verbatim):** infrastructure failures
  re-attempt ≤2 and never consume a task-side terminal state; slots with no
  model content are excluded from acceptance denominators (Amendment-2/3
  discipline).
- **Halt rule:** ≥3 consecutive provider-side pre-output failures ⇒
  status halted; resume windows recorded in `RESUME_RECORD.md`.
- **Label substitution order (registered up front, unchanged):** if a label
  exhausts quota or sustains rate limiting, its remaining slots re-run on
  the first label in [`gpt-6.1-sol`, `gpt-5.6-sol`, `gpt-6-astra`] not
  itself exhausted/substituted; per-label group splits always reported,
  never pooled; substitutions recorded in `RECOVERY_LABEL_SUBSTITUTION.md`.
- **Cost ceiling (enforced live):** phase ceiling **2,500,000 output
  tokens**, soft checkpoint 2,000,000; token counts are the
  measurement-relevant quantity; USD reconciled at settlement in the
  ledger. Operator account: agentrouter key funded
  2026-11-09 (~$170 operator-stated balance), key read from process
  environment only, never printed, never written to any artifact.
- **Fingerprint audit (post-run):** every raw provider response is checked
  for the attested label echo (`model_echo` endswith the registered slug);
  a drifting cohort is withdrawn to same-label with numbers retained
  (P010X1 discipline), recorded in `FINGERPRINT_AUDIT_AMEND5.json`.
- **Non-evidence probes:** the compat pre-gate calls, the cap-calibration
  probes, the per-label AUTH smokes, and every completeness-census probe
  are `evidence=false` and are excluded from all analyses; recorded
  probes (2026-11-09, evidence=false): transport smokes (responses-API
  JSON echo; babycrypto/eps_part2/lowe-RT/almost_xor-RT re-blocked under
  responses API and under the funded account); gate (14 pair probes at
  cap 4200 + effort, `COMPAT_GATE_AMEND5.json`); calibration (effort
  ignored at caps 4200/16000; cap-12000 completions on lowe R0);
  census rows 1–20 of 24 (`COMPLETENESS_CENSUS_stream.jsonl`), suspended
  at the account-quota 403 and completed by the resume script before the
  freeze.

## 8. What would count against the thesis

Unchanged from Amendment 4 §8, with the transport disclosure added: a
positive result instantiates the admission owner on external tasks; a null
under both codings with correct programs present is a measured owner
boundary. Movement computed from visible-content completions only; blocked
and truncated slots are exclusions with their own ledger rows, never
imputed.

## 9. Frozen-input integrity and freeze

`FREEZE.json` lists SHA-256 for: this preregistration, the runner, the
client, the census script and its final `COMPLETENESS_CENSUS_AMEND5.json`,
the census resume script, the pre-gate script and
`COMPAT_GATE_AMEND5.json` (recorded pre-calibration probe history),
`PROMPT_HASHES.json`, the 14 prompt files, the 10 artifacts,
`oracle/answers.json`, `census_nyu/criterion5_outcomes.json`, and
`seed_sweep_AMEND5_SEED_SWEEP.json`. The namespace-restricted freeze
commit is the registration act; live mode refuses to run until
`FREEZE_COMMIT.txt` exists. The API key is read from the process
environment, never printed, never written to any artifact.

## 10. Deviation ledger so far (pre-first-call)

1. **D1 — census suspension at the account-quota exhaustion (2026-11-09,
   pre-freeze, zero evidence calls):** the funded operator account's
   gateway quota went negative mid-census (HTTP 403, remaining quota
   −$304.72, on the almost_xor R0 gpt-6-astra probe); the census was
   suspended at 20/24 rows by the operator's stop order before any
   further spend. Rows 1–20 are preserved verbatim in
   `COMPLETENESS_CENSUS_stream.jsonl`; the four pending crack_me probes
   complete via `completeness_census_resume.py` against a re-funded
   account BEFORE the freeze — no frozen input is computed from the
   suspended state.
2. Amendment-4 registered two pre-first-call amendments for
   route-temperature constraints; this protocol omits the temperature
   field from the start, so route-temperature deviations are structurally
   excluded.

Any post-freeze change lands here with its reason and boundary.
