# Causal analysis — C2 EMPTY_RESPONSE on the AgentRouter route (2026-11-03)

Question: why do C2 sessions return `EMPTY_RESPONSE` at a stable ~53% rate while
C1/C3/C4 never do, across every cohort run on this route?

## 1. The signature of every empty response (68/68 observations, no exception)

The adapter's failure log captures the raw provider body for every empty. All 68
empty responses (51 in the P021AR first pass, 17 in the A3 top-up) carry the
identical signature:

```json
{"content":[{"type":"text","text":""}],
 "stop_reason":"length",
 "usage":{"input_tokens":412..472, "output_tokens":4200},
 "http_status":200}
```

Three facts follow directly:

- **The route never failed.** Every empty is HTTP 200 on a live endpoint.
- **The model generated the full 4200 output tokens** — exactly the registered
  floor, never one token less. The output budget is exhausted server-side.
- **The surfaced text block is empty.** Whatever the model produced (reasoning)
  is not returned by the route: the response carries a single `text` block with
  an empty string, and `stop_reason:"length"` means the cap was hit before any
  final text was emitted.

The route exposes no reasoning channel; when the hidden deliberation outlasts
the floor, the caller receives an empty text block and the adapter — correctly
under its own contract — raises a non-retryable `EMPTY_RESPONSE`.

## 2. Ruled out

| Hypothesis | Evidence against |
|---|---|
| Transport accident (transient outage) | HTTP 200 every time; retries and re-runs reproduce the same rate; C2-only while the route serves C1/C3/C4 concurrently without failure |
| Seed-deterministic behaviour | Re-running exactly the 51 empty pairs (A3 top-up): only 17/51 empty again (33%), 16 produced text; the empty is memoryless at the seed level, re-sampled at the base rate each session |
| Rate-limit/concurrency artefact | The rate is ~53% in both the 8-worker P021AR pass and the 6-worker A3 pass; P023 (different day, different seeds) same 51/96 and same 45/51 ORACLE_FAIL/EMPTY split |
| Empty text = route swallowed text | `output_tokens:4200` with `stop_reason:"length"` — the budget was consumed by generation the route does not surface; when the model finishes inside the budget, the route returns full text (verified in 51 C2 text-bearing responses) |

## 3. Established causal chain

1. **Cell structure sets deliberation length.** Turn-1 output tokens for
   text-bearing responses (first pass, n per cell):

   | cell | condition | median | range | at/near cap |
   |---|---|---|---|---|
   | C1 | premise stated, oracle-bearing | 878 | 551–1483 | 0/96 |
   | C3 | premise stated, non-bearing | 991 | 604–1492 | 0/96 |
   | C4 | premise withheld, non-bearing | 2424 | 1484–3799 | 0/96 |
   | C2 | premise withheld, oracle-bearing | 3450 | 2198–4185 | (empties exceed cap) |

   The withheld premise forces deliberation (C4 > C1/C3: the model must decide
   what is missing and whether it can proceed). The bearing dimension forces
   more (C2 > C4: in C2 the model attempts to solve a task its withheld premise
   is load-bearing for — maximal deliberation).

2. **C2's deliberation distribution straddles the 4200 floor.** Its text-bearing
   median is 3450 with max 4185; the sessions whose reasoning outlasts the cap —
   ~53% of them — hit `stop_reason:"length"` with no surfaced text.

3. **The rate is a stable property of the (C2, label, floor) configuration.**
   Two independent cohorts on disjoint seed sets: P021AR 51/96 empty, P023
   51/96 empty, both with the identical 45 ORACLE_FAIL / 51 EMPTY split. The
   A3 top-up of the same 51 pairs re-produced emptiness at 17/33 = 51.5% of
   transport-clean sessions — the same base rate.

4. **The floor, not the route, is the binding constraint.** A text-bearing C2
   response at 4185 tokens and an empty one at 4200 are the same behaviour
   separated by 15 tokens. The phenomenon is an artifact of where the
   registered floor slices C2's deliberation distribution.

## 4. Corrections this forces

- **A3 amendment attribution is backwards.** The amendment reclassifies
  `EMPTY_RESPONSE` as *transport* for this cohort ("none of them from the
  model"). The evidence shows the opposite: the failures are model-side
  deliberation-length, surfaced as empty text by the route's response format.
  The amendment's *reporting structure* (primary and amended counts side by
  side) stands; its attribution sentence does not. This document supersedes it.
- **The provider census (CENSUS_P_PROVIDER_20261103) over-attributes.** Its
  rule counts any row carrying `provider_failures ≥ 1` as provider-caused loss.
  C2 floor-exhaustion rows carry `provider_failures:1`, so ~53% × 96 C2
  sessions per cohort on this route were attributed to the provider when the
  route is exonerated for them. The census's transport-caused loss figure needs
  a corrected layer separating (a) true transport loss (HTTP_ERROR, timeouts,
  4xx/5xx) from (b) floor-exhaustion empties (HTTP 200 + `output_tokens` = cap
  + `stop_reason:"length"` + empty text block).

## 5. Recommendation for analysis and reporting

- Treat C2 `EMPTY_RESPONSE` (HTTP 200, cap-exact output tokens, empty text
  block) as a distinct outcome category — **FLOOR_EXHAUSTED** — model-side,
  route-surfacing-limited, not transport and not scored.
- Keep the registered 4200 floor unchanged for the rerun cohorts; changing the
  floor mid-wave would be an unregistered protocol change. A floor-raised
  cohort, if wanted, is a new registration with its own disclosure.
- Report per cohort, per cell: sessions, accepted, ORACLE_FAIL,
  FLOOR_EXHAUSTED, transport-lost — side by side, as A3 already requires.

## 6. Reproduction

- Failure-log signatures: `info_contract_aesgcm_random_p021ar_20261103/failure_log.jsonl`
  (51 events) and `.../amendment_a3/failure_log.jsonl` (17 EMPTY events).
- Cell token distributions: `.../raw_provider_responses/*_turn1.json` usage.
- Cross-cohort rates: `info_contract_aesgcm_random_p023_20261103/results.jsonl`
  (C2: 45 ORACLE_FAIL + 51 EMPTY) vs `info_contract_aesgcm_random_p021ar_20261103/results.jsonl`.
- Probe attempt at 8000 tokens was refused by the route (HTTP 403, concurrency
  guard with the queue running); not needed — the failure-log bodies are the
  direct evidence.
