# Amendment A3 — EMPTY_RESPONSE exceeds the registered falsifier

Registered falsifier (PREREGISTRATION.md): provider-failure rate above 5% of
sessions means the transport is still unfit; stop and report rather than analyse a
damaged cohort. Observed at 130/384: **17 EMPTY_RESPONSE sessions (13%)**, all of
them from the router, none from the model.

Two facts bound the damage:

- The failures are *not* outcomes. No cell is scored on them; they are dropped
  before any acceptance is computed.
- Acceptance inside completed sessions is clean: bearing cells 68/68 accepted,
  withheld cells 0/62.

The registered retry policy deliberately does not retry `EMPTY_RESPONSE`
(it is treated as a model-side signal, not transport). On this route that
classification is wrong. A3 records the correction **after** the fact:

1. `EMPTY_RESPONSE` is reclassified as transport for this cohort only.
2. After the first pass finishes, exactly the failed (seed, cell) pairs are
   re-run, in a separate pass, with `AMENDMENT_A3` stamped on every row.
3. No completed session is re-run; no acceptance number is recomputed from the
   amendment pass without reporting both counts.
