# Three-clock source map and manuscript distinction

This map records the evidence behind the Legacy, Clean V4-02, and Fixed-executor
columns. They are separate settings and intervals; none is a matched trial
comparison.

| Setting | Source evidence | Quantity retained | Use in manuscript |
|---|---|---|---|
| Legacy agent cohort | Frozen Legacy E2 analysis and the derived comparison at `V4_LEGACY_FIXED_TIMING_SEPARATION.md`; the nested `ACTS-ATTACK/` checkout is not its source. | Historical successful-session agent durations; successful medians RC4 8.3688372335 s (n=8) and ChaCha20 3.5660625475 s (n=2). No successful CBC/ECDSA median. | Legacy `T_M`; not paired with either other setting. |
| Clean V4-02 agent cohort | `sp2027/analysis/clean_v4_timing_provenance_feasibility_20261014/V4_SUCCESSFUL_AGENT_TIMINGS.csv` and `V4_SUCCESS_TIMING_BY_TASK.json` | Source-defined logged agent-terminal elapsed duration; ChaCha20 18.370820229 s (n=2), CBC 50.062237569 s (n=3), ECDSA 15.294515114 s (n=3), RC4 n=0. Raw harness monotonic start/stop readings are absent, so 0/8 durations can be independently recomputed from endpoint pairs. The interval stops before cleanup and physical session-close logging. | Labeled as Clean logged agent-terminal duration; explicitly not presented as endpoint-reconstructed time. |
| Fixed executor | `ACTS-ATTACK/results_rerun/operation_records.jsonl` (12 physical records) and `ACTS-ATTACK/results_rerun/operation_verdicts.json` (summary) | `executor_op_span_ms`; independently recomputed medians are RC4 0.214196 ms, ChaCha20 0.131647 ms, CBC 1981.556789 ms, and ECDSA 6.956233 ms, each from n=3 successful runs. | Labeled `Fixed operation T_op`; operation-only interval after the operation is constructed, not an agent duration. |

The nested `ACTS-ATTACK/` checkout is the source for the Fixed-executor
operation records. It is not the source for Legacy or Clean agent timings.
Its README describes a broader standalone ACTS-Attack project; the exact files
above are mapped because their task labels, fields, and recomputed medians
match the Fixed-executor rows used here. The nested checkout had unrelated
pre-existing working-tree modifications at inspection; no files in it were
changed.

SHA-256 values at inspection:

| File | SHA-256 |
|---|---|
| `ACTS-ATTACK/results_rerun/operation_records.jsonl` | `3f56aa3aa04af6cfa42ab96a9e69eede9b656e13fb06b5e72053e49ea88521d7` |
| `ACTS-ATTACK/results_rerun/operation_verdicts.json` | `6467127c50519cb6095e56a5edb38b6f8275e18b4525fec01daa3c8071ddabc2` |
| `sp2027/analysis/clean_v4_timing_provenance_feasibility_20261014/V4_SUCCESSFUL_AGENT_TIMINGS.csv` | `3abf46206a7eb4857b193d50197ba9a6d3dc44c4a47fee7af31805b498ffddfb` |

The manuscript table now names the Clean measure as a logged agent-terminal
duration, identifies Fixed as operation-only, states that cohorts are
unmatched, and carries the 0/8 raw-endpoint reconstruction limit and
pre-cleanup stop boundary in its note. No slowdown ratio, speedup, causal
comparison, or model-performance claim is supported by these three columns.
