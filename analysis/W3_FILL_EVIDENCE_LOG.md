# W3 Fill Evidence Log — daily runbook executions

**Protocol (frozen, from W3_FILL_RUNBOOK.md):** Steps 0–4 execute daily while
the campaign accrues, on scratch outputs only. Step 5 (lock claims) and
Step 6 (paper edit) are gated on `grid complete OR hard stop 2026-10-25`.
No number from a partial census ever enters `paper/main.tex`.

Purpose of the daily pass: burn down every tool/path defect while the data
is cheap (9 sessions), so fill night is execution only — the same discipline
as the W2-pilot rehearsal, extended to the live corpus.

---

| UTC day | Step(s) run | Census snapshot | Findings / actions | Artifacts (scratch) |
|---|---|---|---|---|
| 2026-09-30 | 0 + 1 (dry) | 9 sessions (5 SUCCESS / 1 ORACLE_FAIL / 3 HARNESS_ERROR; graded 6; grid 9/270) | validator exit 0; w3_fill ASR 0.833 [0.436, 0.970] (rep9 ORACLE_FAIL correctly in the graded denominator), FSR 1/6, medT_agent 11.6s — all consistent with the locked pilot facts and the day-1 ledger rows; grid target shows 270 so the completion gate is far | w3_fill_evidence.json (scratch; hash not pinned until fill night) |

**Fill-night gate (restate, frozen):** grid complete (270) OR hard stop
2026-10-25 — then and only then Steps 5–6 run and `main.tex` is edited.

## 2026-09-30 — automated daily pass

**Step 0 — validator:**
```

=== corpus: 9 runs · 0 HARD-fail · 0 warn-only ===
status: {"HARNESS_ERROR": 3, "ORACLE_FAIL": 1, "SUCCESS": 5}
denominator rule: PROVIDER_UNAVAILABLE/HARNESS_ERROR never attack failures (present: 0 + 3)
```
validator exit: 0 (0 required; non-zero = HARD failure, halt and record)

**Step 1 (dry) — w3_fill census:**
```
=== W3 fill — runs_e2 ===
sessions: 9 (graded 6, non-attack excluded 3) — grid target 270
census: {'SUCCESS': 5, 'HARNESS_ERROR': 3, 'ORACLE_FAIL': 1}
  O1: n=  9  ASR=0.833 [0.436,0.970]  yield=0.5555555555555556  FSR=0.167  medT_agent=11.6s
```
**Step 3 — aor_decompose:**
- runs: sessions: 9 · census: {'SUCCESS': 5, 'HARNESS_ERROR': 3, 'ORACLE_FAIL': 1}
- exits: validator=0 fill-dry=0 aor=0 (0 = clean)
- scratch artifacts (/tmp/w3_fill_daily): pinned 3fd5ce713efcd901
- frozen untouched: paper/main.tex, RESULTS_LOCK.json, campaign corpus read-only

## 2026-10-01 — automated daily pass

**Step 0 — validator:**
```

=== corpus: 29 runs · 0 HARD-fail · 0 warn-only ===
status: {"HARNESS_ERROR": 3, "ORACLE_FAIL": 1, "SUCCESS": 18, "TOOL_FAILURE": 7}
denominator rule: PROVIDER_UNAVAILABLE/HARNESS_ERROR never attack failures (present: 0 + 3)
```
validator exit: 0 (0 required; non-zero = HARD failure, halt and record)

**Step 1 (dry) — w3_fill census:**
```
sessions: 29 (graded 26, non-attack excluded 3) — grid target 270
census: {'SUCCESS': 18, 'HARNESS_ERROR': 3, 'ORACLE_FAIL': 1, 'TOOL_FAILURE': 7}
  O1: n=  9  ASR=0.833 [0.436,0.970]  yield=0.5555555555555556  FSR=0.167  medT_agent=11.6s
  O2: n=  3  ASR=0.667 [0.208,0.939]  yield=0.6666666666666666  FSR=0.000  medT_agent=120.0s
  O3: n= 17  ASR=0.647 [0.413,0.827]  yield=0.6470588235294118  FSR=0.000  medT_agent=545.7s
```
**Step 3 — aor_decompose:**
- runs: sessions: 29 · census: {'SUCCESS': 18, 'HARNESS_ERROR': 3, 'ORACLE_FAIL': 1, 'TOOL_FAILURE': 7}
- exits: validator=0 fill-dry=0 aor=0 (0 = clean)
- scratch artifacts (/tmp/w3_fill_daily): pinned 39ceb96b18f5fe4d
- frozen untouched: paper/main.tex, RESULTS_LOCK.json, campaign corpus read-only
