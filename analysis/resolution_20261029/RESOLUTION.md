# Design resolution (exact, no model calls)

Two-sided Fisher, alpha=0.05, power=0.8, baseline p=0.5 (best case).

| n per arm | max power (at p2=1.0) | smallest detectable diff (pp) |
|---:|---:|---:|
| 4 | 0.06 | none (no d resolves at this n) |
| 8 | 0.36 | none (no d resolves at this n) |
| 10 | 0.62 | none (no d resolves at this n) |
| 16 | 0.96 | 46 |
| 32 | 1.00 | 35 |
| 64 | 1.00 | 25 |

n required to resolve 20pp: 93 per arm, 10pp: 388 per arm (standard pooled-variance normal approximation, per-arm n; no continuity correction).

| observed claim | k/n per arm | MDE (pp) | 95% CI |
|---|---|---:|---|
| H2 wrapper extension (accepted) | 5/10 vs 7/10 | none | [0.187, 0.813] vs [0.348, 0.933] |
| H2 frozen pairs (accepted) | 2/4 vs 3/4 | none | [0.068, 0.932] vs [0.194, 0.994] |
| P010L2 withheld arm (accepted) | 0/8 vs 8/8 | none | [0.0, 0.369] vs [0.631, 1.0] |
