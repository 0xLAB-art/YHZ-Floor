# SESSIONS — explicit empty state

**Zero experiment sessions were run in this phase.**

The conditional grid (6 tasks × {R0, RT} × seeds 95, 96 = 24 sessions, ≤2
turns) never instantiated because the task-selection quorum was unmet at
census: **0 of 40** pinned CVE-Bench tasks qualify under the five mirrored
criteria (`TASK_SELECTION.md`, `selection/census.json`); 0 < 6 → honest early
stop with status `no_go`, exactly as the phase prompt prescribes.

Consequences, all retained rather than filled:

- Terminal states recorded: none (no session existed to fail or succeed).
- `PROVIDER_UNAVAILABLE` count: 0 — and note the provider was in fact healthy
  (16-token AUTH_SMOKE, `HEALTH.json`, non-evidence); the stop is a *design*
  stop, not an infrastructure stop.
- No seed was consumed, replaced, or retried: seeds 95–96 remain unused by any
  cohort (verified against all preregistrations and `results.jsonl` files under
  `sp2027/` before the freeze — 0 prior matches).
- Zero experiment provider calls were made under this namespace. The only
  provider call is the non-evidence AUTH_SMOKE probe.

Falsifiers F1–F3 are therefore **NOT EVALUABLE** (no sessions, no programs).
