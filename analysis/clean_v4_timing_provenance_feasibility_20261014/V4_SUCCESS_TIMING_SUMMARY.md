# Clean V4-02 successful-agent timing summary

EXP-034 / CLEAN V4-02 has 12 scheduled and retained records; 8 are SUCCESS. The table reports source-defined `tte_m_harness_ns` converted to seconds. The denominator for timing-admissible successes is shown separately from raw SUCCESS.

| Task | Scheduled | Retained | SUCCESS | Timing-admissible SUCCESS | Median T_M (s) | Range (s) | Individual successful runs (s) |
|---|---:|---:|---:|---:|---:|---:|---|
| RC4 | 3 | 3 | 0 | 0 | none | none | none |
| ChaCha20 | 3 | 3 | 2 | 2 | 18.370820 | 17.501390–19.240250 | qedd7c9aab5dcad7ed9f33482__chacha20_nonce_reuse__T1_known__rep1=17.501390, qaef4f421945ab6cf6bf8ba2f__chacha20_nonce_reuse__T1_known__rep2=19.240250 |
| CBC | 3 | 3 | 3 | 3 | 50.062238 | 39.437838–71.127476 | qb043d10ca94bb987b03fd142__cbc_padding_oracle__T1_known__rep1=50.062238, qf86aba4885ba256ad42fb17a__cbc_padding_oracle__T1_known__rep2=39.437838, q83ce3aca8c16001d24a2a383__cbc_padding_oracle__T1_known__rep3=71.127476 |
| ECDSA | 3 | 3 | 3 | 3 | 15.294515 | 14.470609–16.635207 | qb868b7c841e0cd44e83089eb__ecdsa_nonce_reuse__T1_known__rep1=15.294515, qdde825bc566a03f633adaf41__ecdsa_nonce_reuse__T1_known__rep2=14.470609, q94a788081121781914024471__ecdsa_nonce_reuse__T1_known__rep3=16.635207 |

These are descriptive summaries of n=2 or n=3 observed successful sessions, not stable task capability distributions. No confidence interval or pooled task median is estimated.

The duration is captured per run and agrees between raw terminal record and transcript terminal event. Code identifies a monotonic harness interval from `op_start_mono` through `_end_session`; it stops at agent-terminal handling before physical close/cleanup. The numerical monotonic start/end readings are not themselves retained. Thus 8/8 successful intervals support qualified source-defined timing; 0/8 can be independently recomputed from two retained monotonic endpoints. A claim specifically extending through physical session close is not established.

RC4 has 0/3 successes. No successful-agent median is defined for RC4.
