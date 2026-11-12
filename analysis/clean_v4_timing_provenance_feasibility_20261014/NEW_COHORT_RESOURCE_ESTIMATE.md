# New-cohort resource estimate

## Observed V4-02 usage

The 12 retained sessions contain 31 model-turn request records (2.58 mean, 2.5 median, 1–4 observed range per session). They retain 90,209 response characters in total and 547.842 aggregate seconds of model-turn spans (14.228–105.562 s per session). They do not retain provider token-usage counts or HTTP request-attempt IDs. Source code permits up to eight model turns per task session, three transient-gateway outer attempts per turn, and two HTTP POST attempts within a call when JSON-mode fallback is triggered. This gives a conservative source-level ceiling of 48 HTTP attempts/session, but no retained request IDs verify actual attempts. The model configuration requests a maximum of 4,096 completion tokens per turn; provider-reported token usage and prompt-token totals are absent. Monetary pricing is not established by the retained artifact, so cost is **UNKNOWN**.

## Bounded projections

| Candidate | Scheduled sessions | Model turns (observed mean planning value; frozen upper bound) | HTTP attempts (source-level upper bound) | Completion-token ceiling (requested max only) | Monetary estimate |
|---|---:|---:|---:|---:|---|
| A. Technical qualification | 1–2 | about 2.58/session; 8–16 maximum | 48–96 maximum | 32,768–65,536 | UNKNOWN |
| B. 4 tasks × 3 repetitions | 12 | about 31 observed-style; 96 maximum | 576 maximum | 393,216 | UNKNOWN |
| C. 4 tasks × 10 repetitions | 40 | about 103 observed-style; 320 maximum | 1,920 maximum | 1,310,720 | UNKNOWN |

Planning values multiply session count by observed mean turns and are not guarantees or forecasts of future service behavior. The upper values multiply the task-card 8-turn ceiling, three outer gateway attempts and two HTTP POST branches per attempt; provider-side billing treatment of failed/retried requests is unknown. A session is capped at 900 s and an individual model request at 240 s; serial execution upper wall-clock bounds from session timeout alone are 0.5 h, 3 h, and 10 h respectively, excluding setup and pauses. V4 observed total T_M is 558.0 s across 12 sessions, but that small observed sum is not a reliable future runtime bound. Docker build/runtime resource consumption is not measured in retained records; local offline image inspection confirmed the EXP-035 digest is present and matches its manifest.

A future approved registration should require a hard provider-side credit cap or verified zero-cost guarantee, transport attempt limit/logs, max model turns, session timeout, and a stop condition. No provider use is authorized by this analysis; no experiment was launched and no request was made.

