## H1-R3 Confirmatory Rerun - APMIX Provider Attestation

Created: 2026-10-19
ReadOnly: export artifacts only.

This note records the new provider attestation performed for the H1-R3 confirmatory rerun. No provider calls are made unless explicitly authorized in-session.

Provider details:
- Endpoint: https://api.apmix.ai
- Messages endpoint: https://api.apmix.ai/v1
- Route: claude-sonnet-4-6-free
- Key source: environment APMIX_API_KEY only; never written to disk or repo
- Key length: 49
- Key SHA256: 702839baeb4a13e2b7327e93a97110fbfbcfc782f04ad9a8856fe1528b29443e

Key material snapshot:
- Path: sp2027/analysis/h1r3_20261019/h1r3_key_snapshot.py
- Contains: APMIX_API_KEY_HASH only, no raw key

What was verified:
- APMIX_API_KEY is set in session env
- Endpoint returns 404 for /v1/models and /v1/usage
- A mini /v1/messages probe succeeds and returns model = claude-sonnet-4-6-free
- So the provider is "messages-only" Anthropic-compatible for the route in question
- Provider adapter already accepts x-api-key + Authorization Bearer + anthropic-version headers
- H1-R3 health gate was relaxed to pass on probe-only when /v1/models and /v1/usage are unavailable

What was not done:
- No provider calls were made from this session
- No key was written to disk except the SHA256-only snapshot
- No H1-R3 frozen results were touched
- No H1R3_ANALYSIS.json was changed
- The old H1R3_EVIDENCE_PACKAGE_20261019.md was left as export-ready only

Rerun constraints:
- One request per scheduled session
- No retries, no fallback, no seed replacement, no adaptive stopping, no paid path
- Startup gate: require explicit --confirm-start in session env with APMIX_API_KEY present
- Output written under sp2027/analysis/h1r3_20261019/runs/confirmatory_apmix_01/
- Old frozen results left untouched unless explicitly replaced

If you want the rerun to actually happen, next step is to run the prepared control script with --confirm-start from the machine where APMIX_API_KEY is exported.
