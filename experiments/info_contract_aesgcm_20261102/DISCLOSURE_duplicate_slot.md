# P014 instrument disclosure — one duplicate (seed, cell) slot

**Date:** 2026-11-02 · **Cohort:** P014 AES-GCM (`info_contract_aesgcm_20261102/`)

## What happened

The cohort was launched twice. The first launch ran in the foreground and was
killed by tool cleanup after exactly one session; the relaunch then resumed at
**seed** granularity, and seed 401 had only C1 recorded, so the wrapper re-ran
all four of its cells. Result: two rows for `(seed 401, C1)`.

| run_id | cell | status | oracle |
|---|---|---|---|
| `…__C1__seed_401__7d5a8fcc8850` (first launch) | C1 | SUCCESS | accepted |
| `…__C1__seed_401__11a15b2da9d5` (relaunch) | C1 | SUCCESS | accepted |

Both rows agree (accepted/accepted), so the duplicate cannot move the cell
count either way. Rows carry no per-row start/finish timestamps, so the
analysis resolves the pair by **file order — earliest row wins**, the rule
frozen in `analyze_p011.py` before any cohort completed.

## Why it is disclosed rather than deleted

Deleting one row would be a silent edit to an evidence file. The frozen rule is
"flag, never delete": `analyze_p014.py` prints the duplicate run_ids in its
header so a reader sees exactly which slots were run more than once. This is the
same instrument-duplicate path already reported for the P011 family, and it is
an artifact of the launcher lifecycle (foreground kill + seed-level resume),
not of the fixture, the oracle, or the model.

## Effect on the analysis

- Cell counts: unchanged (earliest row accepted, second also accepted).
- Pairing: unaffected — the pair is formed per seed, and each seed contributes
  one C1 verdict.
- Denominator: 64 registered slots, 63 distinct rows after de-duplication; the
  duplicate is reported alongside the provider-dropout counts so the
  evaluable-pair denominator is auditable.
