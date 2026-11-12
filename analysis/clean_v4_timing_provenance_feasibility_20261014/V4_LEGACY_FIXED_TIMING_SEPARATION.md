# Legacy, clean-agent, and fixed-executor timing separation

| Task | Legacy successful T_M | Clean V4-02 successful T_M | Fixed-executor T_op | Scientific interpretation |
|---|---:|---:|---:|---|
| RC4 | 8.3688372335 s | no successful run (0/3) | 0.214196 ms | Legacy success and operation-only execution refer to distinct cohorts and intervals; no clean successful-agent value exists. |
| ChaCha20 | 3.5660625475 s | 18.370820 s (n=2) | 0.131647 ms | Two cohort-specific descriptive medians; unmatched sessions and different clocks preclude a slowdown or causal ratio. |
| CBC | no successful-agent median | 50.062238 s (n=3) | approximately 1.98 s | Clean cohort supplies retained successful-agent interval missing from legacy; fixed operation remains a different interval. |
| ECDSA | no successful-agent median | 15.294515 s (n=3) | 6.956 ms | Clean cohort supplies retained successful-agent interval missing from legacy; fixed operation remains a different interval. |

No trials are matched. No agent slowdown, acceleration, paired effect, causal effect, significance test, or pooled cross-task median is estimated. The new observations do not revise the legacy results: they fill a task-specific descriptive endpoint absence in a separate clean cohort.

