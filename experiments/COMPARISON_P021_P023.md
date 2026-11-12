# P021 vs P023 — drop-rate comparison

- **P021** `P021-INFO-CONTRACT-2X2-AESGCM-CSPRNG-SEEDS-v1` — label `gpt-6-astra`, 384 sessions, seeds `07a9e4422a0c…`
- **P023** `P023-INFO-CONTRACT-2X2-AESGCM-CSPRNG-SEEDS-v2` — label `gpt-6-astra`, 384/384 sessions, seeds `056aa34e8e53…`
- Same runner, cells, rotations, floor and analyzer. **Different seed draws**, so this is a per-cell comparison, not an instance-paired test.

## P021 (original transport)

| cell | sessions | transport drops | model-level drops | evaluable | accepted | drop rate (95% Wilson) | accepted/evaluable (95% Wilson) |
|---|---|---|---|---|---|---|---|
| C1 | 96 | 43 | 0 | 53 | 53 | 44.8% [35.2, 54.7] | 100.0% [93.2, 100.0] |
| C2 | 96 | 46 | 35 | 15 | 0 | 84.4% [75.8, 90.3] | 0.0% [0.0, 20.4] |
| C3 | 96 | 43 | 0 | 53 | 53 | 44.8% [35.2, 54.7] | 100.0% [93.2, 100.0] |
| C4 | 96 | 59 | 0 | 37 | 0 | 61.5% [51.5, 70.6] | 0.0% [0.0, 9.4] |
| **total** | 384 | 191 | 35 | 158 | 106 | 58.9% [53.9, 63.7] | 67.1% |

## P023 (repaired transport)

| cell | sessions | transport drops | model-level drops | evaluable | accepted | drop rate (95% Wilson) | accepted/evaluable (95% Wilson) |
|---|---|---|---|---|---|---|---|
| C1 | 96 | 1 | 0 | 95 | 95 | 1.0% [0.2, 5.7] | 100.0% [96.1, 100.0] |
| C2 | 96 | 0 | 51 | 45 | 0 | 53.1% [43.2, 62.8] | 0.0% [0.0, 7.9] |
| C3 | 96 | 0 | 0 | 96 | 96 | 0.0% [0.0, 3.8] | 100.0% [96.2, 100.0] |
| C4 | 96 | 0 | 0 | 96 | 0 | 0.0% [0.0, 3.8] | 0.0% [0.0, 3.8] |
| **total** | 384 | 1 | 51 | 332 | 191 | 13.5% [10.5, 17.3] | 57.5% |

## Drop-rate difference (P023 − P021)

| cell | P021 drops/sessions | P023 drops/sessions | Δ (95% Newcombe) | Fisher two-sided |
|---|---|---|---|---|
| C1 | 43/96 (44.8%) | 1/96 (1.0%) | -43.8% [-53.7, -33.1] | 1.43e-14 |
| C2 | 81/96 (84.4%) | 51/96 (53.1%) | -31.2% [-42.8, -18.3] | 4.57e-06 |
| C3 | 43/96 (44.8%) | 0/96 (0.0%) | -44.8% [-54.7, -34.5] | 4.98e-16 |
| C4 | 59/96 (61.5%) | 0/96 (0.0%) | -61.5% [-70.6, -50.7] | 6.04e-24 |
| total | 226/384 (58.9%) | 52/384 (13.5%) | -45.3% [-51.0, -39.1] | 1.12e-40 |

## Provider-failure attempts by category

Attempts, not sessions: the repaired transport retries before a session is lost.

| category | P021 attempts | P023 attempts |
|---|---|---|
| EMPTY_RESPONSE | 35 | 51 |
| HTTP_ERROR | 189 | 1 |
| TIMEOUT | 2 | 0 |

## Reading

- P021 lost **226/384** sessions (58.9%); **191** of those were transport-level.
- P023 has lost **52/384** so far (13.5%); **1** transport-level.
- Transport drop rate: P021 49.7% → P023 0.3%. Δ -49.5% ([-54.5, -44.4]).
- Model-level drops (textless/truncated completions) are unaffected by the repair by design: P021 35, P023 51.

