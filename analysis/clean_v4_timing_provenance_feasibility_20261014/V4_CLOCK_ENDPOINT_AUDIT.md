# V4 clock endpoint audit

## Evidence levels

| Check | Classification | Basis |
|---|---|---|
| Contract names T_M start/end and monotonic source | DECLARED_ONLY | `V4_CLOCK_CONTRACT_QUALIFIED.json` declares post-provision start through retained terminal/session-close. |
| Duration generated with monotonic clock | ENFORCED_BY_CODE | `agent_loop.py` uses `time.monotonic_ns()`; start is sampled after provisioning and instance materialization, immediately before `op_start`; stop is sampled at entry to `_end_session`. |
| Stop is terminal/session-close endpoint | SUPPORTED_WITH_QUALIFICATION | Stop occurs after the agent loop's terminal outcome is available but before abort/cleanup, final oracle read, and transcript `session_end` write. It is an agent-terminal endpoint, not physical close after cleanup. |
| Endpoint event belongs to this session | SUPPORTED_BY_RETAINED_RECORD | Transcript binds `op_start_utc`, subsequent session-end UTC marker, task, replicate, model and matching duration to same run; the session-end UTC is later than the monotonic stop sample. |
| Raw monotonic start/end readings retained | NOT_ESTABLISHED | Only their difference is retained; exact monotonic endpoint values are absent. |
| Duration finite, integer, nonnegative and unit documented | ENFORCED_BY_CODE / SUPPORTED_BY_RETAINED_RECORD | V4 structural clock validator checks primary clock integer/nonnegative and schema uses ns; every SUCCESS has a positive integer. |
| Same-session binding of primary duration | SUPPORTED_BY_RETAINED_RECORD | run ID binds raw record, transcript path, scheduled identity and terminal duration; transcript event has session-bound UTC labels. |
| Validator independently enforces complete raw endpoint pair | NOT_ESTABLISHED | It validates duration structure and cross-clock diagnostic, not two retained monotonic timestamps or their independent subtraction. |

## Per-success check

All 8 SUCCESS records have `tte_m_harness_ns`, one matching transcript `session_end`, one explicit oracle success, and finite nonnegative duration. `session.started_utc` and `session.ended_utc` in the top-level record are null. The transcript `op_start_utc` is sampled adjacent to the monotonic start, and its `session_end` UTC is written after the T_M stop and cleanup; neither exposes the raw monotonic sample. Accordingly, all eight values are reportable as source-defined, session-bound durations to agent-terminal handling with qualification; none is independently re-computable from two retained monotonic endpoints. If wording promises timing through physical session close, the records do not establish that longer interval.

## Requests and retries

`request_records` and transcript `llm_turn` events count model turns and aggregate elapsed time / response characters. They do not retain provider HTTP request IDs or individual transport attempts. V4's zero-replacement schedule constrains scheduled sessions; it does not prove exactly one HTTP request per model turn. `session.attempts` counts submitted-code attempts, not provider HTTP retries. Oracle query counts are separately retained and all 12 records report zero; each session nevertheless has a final task verdict. Provider HTTP attempts are therefore unknown from retained records.

