# Timing manuscript patch proposal (not applied)

## Source status

`sp2027/paper/README.md` names `sp2027/paper/main.tex` as the authoritative anonymous IEEE S&P source. Its current on-disk SHA-256 is `4daf3464443557a3b96db63d14f7bc2b6ebe7376dd7f3f0c1bffa88c6911780e`; its current PDF is 15 pages, despite the README's older 13-page hash/build statement. The separate `sp2027/paper/arxiv_preprint_20261014/main.tex` SHA-256 is `168c98e93333245d3d64940a5f29ab8539534036ff7dd64f3bffabe29912a406`; it builds to 18 pages and integrates V4 and EXP-035. It is the newest evidence-integrated manuscript candidate, but is a standalone preprint, not the status-designated IEEE S&P source. The two sources differ. This analysis does not edit either. A future patch must be routed to an author-selected target rather than silently choosing one.

## Proposed paragraph

A separate clean capture-first cohort retained 12 of 12 scheduled sessions and recorded eight oracle-accepted successes: two of three ChaCha20 sessions and all three CBC and ECDSA sessions. The retained harness clock records the post-provisioning agent-loop interval through terminal-outcome handling; its monotonic stop is sampled before harness cleanup and transcript session-close logging. Among successful sessions, descriptive median T_M was 18.370820 s for ChaCha20 (range 17.501390–19.240250; n=2), 50.062238 s for CBC (range 39.437838–71.127476; n=3), and 15.294515 s for ECDSA (range 14.470609–16.635207; n=3); RC4 had no successful session and no successful-agent median. The monotonic duration is retained and source-defined, although the raw monotonic endpoint readings are not separately retained. These observations supply successful-agent endpoint timings for CBC and ECDSA that are absent from the legacy cohort; they are separate cohorts and do not support a matched speed comparison or broader capability estimate.

## Proposed table

| Task | Scheduled / retained | Success | Successful-agent T_M median (range) |
|---|---:|---:|---:|
| RC4 | 3 / 3 | 0/3 | not defined |
| ChaCha20 | 3 / 3 | 2/3 | 18.370820 s (17.501390–19.240250) |
| CBC | 3 / 3 | 3/3 | 50.062238 s (39.437838–71.127476) |
| ECDSA | 3 / 3 | 3/3 | 15.294515 s (14.470609–16.635207) |

The paragraph and table are a secondary analysis of EXP-034, not a new arm or experiment. Do not merge these values with legacy E2 or fixed-executor T_op. Table line for RC4 intentionally reports no median.
