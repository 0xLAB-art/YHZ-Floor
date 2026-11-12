# E5 Raw Run Census (2026-10-18)

- Canonical retained JSON records: **29**
- Status counts: `{'ORACLE_FAIL': 9, 'PROVIDER_UNAVAILABLE': 15, 'SUCCESS': 1, 'TOOL_FAILURE': 4}`

## Verified denominator partition

| Population | Records | Accepted | Interpretation |
|---|---:|---:|---|
| Initial graded arm | 4 | 0 | 0/4 |
| Extension graded arm | 10 | 1 | 1/10 |
| All graded records | 14 | 1 | 1/14 |
| Provider-unavailable launches | 15 | — | Separate; not attack failures |

The arithmetic is **29 = 14 graded + 15 provider-unavailable**. The raw records, statuses, paths, and SHA-256 digests are in `E5_RAW_RUN_CENSUS_20261018.json`.
