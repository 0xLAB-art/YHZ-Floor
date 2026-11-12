# Quota block — 2026-11-03 17:49 EET

Every session in this namespace's first attempt was rejected by the route with
HTTP 403 "user quota is not enough" (AgentRouter billing layer) — no model call
succeeded. The outputs were moved to quota_blocked_20261103/ as evidence and
removed from the live tree so the registered run can start clean. The
registration (PREREGISTRATION.md, _REGISTRATION.json) is untouched; the run
clock starts at the first successful call.
