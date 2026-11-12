# Checkpoint 007 — Power, cost, and stop rules

## Provider and route (frozen identity)

Model route: `claude-sonnet-4.6-free`, per `/v1/models` attestation and the
response `model` field in `PREFLIGHT_NON_EVIDENCE.json` (provider-attested route
name only — not a claimed hosted weight identity). No alternate model is used
unless explicitly authorized.

## API key handling (hard boundary)

- Key lives only in `~/.config/acts007/apmix.key`, mode 0600.
- **Never** written to Git, prompt contexts, transcripts, reports, archives,
  screenshots, or cloud storage.
- Loaded at runtime by scripts reading the file; scripts never embed the key.
- If key provenance ever becomes uncertain, halt and report rather than
  restarting with a possible key in context.

## Cost envelope and logging

An explicit spend guardrail applies for this checkpoint's campaign:

- **Alert threshold:** if estimated API spend for checkpoint007 exceeds
  **$50** (USD, provider usage model), log an INFO checkpoint event
  `('SPEND_ALERT', spent_usd, arm_namespace, sessions_completed)` and continue
  only after confirming the threshold is acceptable.
- **Halt threshold:** if estimated spend reaches **$200**, stop new arms,
  finish in-flight sessions, per-arm cleanup, and write `00_STATUS_AND_COST_LEDGER.md`
  plus `15_EXECUTION_REPRODUCIBILITY_AND_BUDGET_REPORT.md`; do not start new
  arms until spend is reviewed.
- Log every call's: arm_id, prompt_sha256, input_tokens, output_tokens,
  cache_read_tokens if any, estimated_usd (per provider's published pricing if
  known, else 'UNKNOWN_PRICE'), latency_s, status, retry count, provider
  response code, timestamp_utc, seed_namespace, arm_namespace.
- These are logged to `00_STATUS_AND_COST_LEDGER.md` and the per-arm
  `run_events.jsonl` inside each arm directory.

## Per-arm resource bounds

- Oracle query budget: per arm_id (max 400 queries where applicable)
- Max model turns: per arm_id (interactive = 8–12; one-shot = 1; instrument
  arms = 0 or 1 as registered)
- Turn timeout: 900s transport per turn, 600s local program wall cap per
  subprocess, logged but not treated as model failure.
- No retries without a permanent log entry and a call to checkpoint cost
  before continuation.

## Sequential stopping discipline (pre-registered)

- Do **not** stop early solely because a striking result appears.
- Planned confirmatory sample per eligible condition is 10 paired seeds
  (minimum); ~20 is considered if API/latency permit and is pre-registered
  here as extension, never improvised.
- Pilot arms (seed namespace `P*`, not preregistered) are nonconfirmatory and
  excluded from confirmatory analyses unless explicitly moved into the
  confirmatory registry with an explicit preregistration edit.

## Run integrity rules

- Never send reserved secret, digest, verifier code, or post-verdict events
  to the model. Document a truth-exclusion gate test after each arm start.
- Distinguish model transitions vs oracle transitions vs harness execution
  transitions; log monotonic timestamps for distinct clocks.
- Deliberately underdetermined arms are scored by their identifiability pass,
  not by a uniqueness score.
- Provider failures are preserved as a separate cohort, not recoded to a
  terminal outcome.
- Synthetic fault-injection and clock-calibration arms are not pooled with
  attack arms.
- If a confirmed provider outage/ quota exhaustion occurs, stop rather than
  reinserting in-flight runs as completed.

## Final reporting

- Deliverables in `15_EXECUTION_REPRODUCIBILITY_AND_BUDGET_REPORT.md` must
  include the cost ledger summary, per-arm IDs, fragility notes, and the SHA-256
  output manifest.
- No title/headline selection or IEEE S&P acceptance claim from this checkpoint.
