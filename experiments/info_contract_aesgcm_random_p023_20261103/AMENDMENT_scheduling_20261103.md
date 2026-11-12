# P023 scheduling amendment — 2026-11-03

**Status:** operational amendment, declared after 27 of 384 sessions had been
recorded and before the remaining 357. Frozen design unchanged.

## What was observed

The registered runner executes its plan as a single sequential loop
(`for seed, cell in plan`). Measured throughput on this route over the first
1.4 h of P023: **27 sessions / 96 min ≈ 20 sessions/h** in practice (the
44/h figure came from the first 30 min, before the slower C2/C4 sessions
entered the queue). Each session costs 1–2 provider calls producing up to
4,200 completion tokens, so wall time is dominated by sequential generation
latency, not by local execution.

At that rate the cohort needed ≈ 9–19 h, and the two P024 arms behind it
(768 sessions) a further 38 h.

## What was changed

Execution scheduling only:

* open sessions (**not** turns) run on a 10-thread pool
  (`parallelize_cohort.py`, hash recorded in `_CONCURRENCY.json`);
* resumption is at `(seed, cell)` granularity: the 27 pairs already in
  `results.jsonl` were not repeated, including terminal provider-drop rows;
* every row written from now on carries `execution_concurrency: 10` and
  `execution_phase: "parallel"`; rows from the serial prefix carry neither.

## What was deliberately NOT changed

Cells, prompts and their slot wording; rotations and their index into the
**full** registered seed list; the 4,200-token floor; the model label and
route; the two-turn limit; the harness feedback strings; the local 20 s
subprocess; the oracle; the transport-retry policy (4 attempts, 2/5/12 s);
the analysis. Turn 1 → feedback → turn 2 inside a session remains strictly
sequential, so no session can observe another session's output.

Note: the launcher's own seed-level resume is disabled when parallelism is on,
because trimming `SEEDS` would re-derive rotation indices from a shortened
list and silently change cell assignment. The parallel driver skips completed
`(seed, cell)` pairs instead, preserving the registered assignment.

## Known risk and how it is handled

Concurrency can raise router throttling. Transport retries absorb it, but a
sustained burst could convert into terminal `EMPTY_RESPONSE`/`HTTP_ERROR`
rows — a denominator effect, not a model outcome. Mitigation:

1. `failure_log.jsonl` records every failed attempt with HTTP status and body
   excerpt, so a throttling burst is visible as attempt-level failures rather
   than being inferred from terminal rows;
2. rows are tagged by `execution_concurrency`, so the analysis can report the
   terminal-drop rate separately for the serial prefix and the parallel suffix;
3. if the parallel-suffix terminal-drop rate materially exceeds the serial
   prefix, that is reported as a transport-phase effect on the denominator and
   **not** attributed to the information contract.

## Effect

357 remaining sessions at the observed parallel rate (≈ 400 sessions/h during
the C1/C3 fast block; slower once C2/C4 dominate) ⇒ expected ≈ 1.5–2.5 h
instead of 9–19 h.
