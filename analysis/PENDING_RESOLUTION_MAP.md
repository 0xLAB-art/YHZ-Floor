# Historical PENDING Resolution Map — every mark → its exact disposition

> Scientific status update, 2026-10-04: manuscript placeholder closure is
> not empirical completion. See ../paper/REVIEWER3_REPAIR_STATUS.md for open
> human-validation, clean-campaign, external-remeasurement, and portable-
> reconstruction requests. No missing result is supplied by this ledger.

> Superseded on 2026-10-03. The 270-session experiment failed to complete and
> halted at 33/270 scheduled
> graded sessions, so no fill-night, provider call, or retrospective repair
> is authorized. The census below is retained as provenance; the final
> manuscript disposition is recorded in the section at the end of this file.

**Census at mapping (2026-09-30): 27 raw matches = 24 logical marks**
(L822–824 hold 9 table-cell matches = 3 logical cells × 3 columns;
L13/14/17 are the header legend itself, resolved with their groups).

**Historical gates (superseded):** W3 was designed to close at **270 graded
sessions or the 2026-10-25 hard stop**; W4 was coupled to W3; W5-κ depended
on a human annotation round. None of those future gates is being executed in
the reopened draft.

---

## W3 group — 19 logical marks → `w3_fill.py` + `aor_decompose.py` + `bounds_tier.py`

| # | Location | What fills it | Tool (tested) | Artifact emitted |
|---|---|---|---|---|
| 1 | L92 Abstract: latency decomposition + KM curves | decomposition stats + KM medians per tier | `w3_fill.py` + `bounds_tier.py` | `w3_fill_evidence.json`, `bounds_tier_evidence.json` |
| 2 | L165 Contributions: decomposed components + curves | same as #1 | same | same |
| 3 | L170 Δmedian −1.70ms campaign analogue | campaign latency decomposition headline | `aor_decompose.py` | `aor_runs_e2.json` |
| 4 | L353 validator pass rate over the corpus | audit exit-0 rate (100% required) | `acts_audit.py validate` | validator output (pinned daily) |
| 5 | L721 Results section opens | — (section gate; resolves with the table) | — | — |
| 6 | L800 paired operation spans fill at W3 | T_rep↔T_op paired rows count + ranges | `aor_decompose.py` | `aor_runs_e2.json` (OPSPAN_NS pipeline pre-verified) |
| 7–9 | L822–824 Table 3: ASR ×3 slots | Wilson CIs per slot × track (frozen denominators) | `w3_fill.py --emit-tex` | `w3_fill_table3.tex` fragment |
| 10–12 | L822–824 Table 3: FSR ×3 | claim-submitted vs oracle rejection per slot | `w3_fill.py` | same |
| 13–15 | L822–824 Table 3: median T_agent ×3 | per-slot medians | `w3_fill.py` | same |
| 16 | L842 operational yield | graded/attempted + provider-state table | `w3_fill.py` | `w3_fill_evidence.json` |
| 17 | L844 FSR per session | as #10–12 (prose restatement) | — | — |
| 18 | L932 KM: when outcomes happen | KM curves + median time-to-success | `bounds_tier.py --claim …` | `bounds_tier_evidence.json` |
| 19 | L942 three-way outage band | censored / competing-risk / worst-case band | `bounds_tier.py` | same |

**Automated tonight/nightly:** Steps 0+1d+3 via `ops/w3_daily_fill_step.sh`
(cron 13:40). **Fill night:** `w3_fill.py --emit-tex` → paste fragment →
`bounds_tier.py --claim "<declared from data>"` → lock ×2 → build.

## W4 group — 1 mark → `e4_sensitivity.py --campaign`

| # | Location | What fills it | Tool | Artifact |
|---|---|---|---|---|
| 20 | L867 regime comparison + rank-flip primary | A/B/C re-grading per model×task + rank-flip test | `e4_sensitivity.py --campaign sp2027/agent-eval/runs_e2 --skip-missing` | `e4_sensitivity_results.json` (frozen artifact updated at fill) |

Proven: 2026-09-30 on the live 9-session corpus (T3-START-ALL) — the
campaign cohort appears in the identical A/B/C pipeline; rep9 landed in the
FSR numerator honestly. Re-run at fill = one command.

## W5 group — 4 marks → humans × `e6_grade_round1.py`

| # | Location | What fills it | Owner | Gate |
|---|---|---|---|---|
| 21 | L93 Abstract: external annotators under frozen protocol | κ + raw agreement | 3 humans | sheets due 10-12 |
| 22 | L176 three annotators score stratified samples | per-annotator counts + κ | same | same |
| 23 | L962 Fleiss κ vs classifier + adjudication | κ + adjudication notes | same | same |
| 24 | L1167 human annotation scope (taxonomy + selected items) | scope restatement resolved with #21–23 | — | — |

**Historical state at halt:** codebook v1.0+v1.1, packet (30 items, blinded), send packs ×4
(`recruitment/outbox/`, blinding gate PASS), grader selftested.
The external-human round was not collected; no fallback was triggered.

---

## Historical fill-night checklist (not executed; retained for provenance)

```bash
# 0. preconditions
python3 sp2027/schema/acts_audit.py validate sp2027/agent-eval/runs_e2   # exit 0
# 1. primary numbers
python3 sp2027/analysis/w3_fill.py --emit-tex
# 2. KM band (declare the claim from the data first — frozen rule)
python3 sp2027/analysis/bounds_tier.py --claim "<median time-to-success < X s>"
# 3. decomposition
python3 sp2027/analysis/aor_decompose.py sp2027/agent-eval/runs_e2
# 4. sensitivity
python3 sp2027/analysis/e4_sensitivity.py --campaign sp2027/agent-eval/runs_e2 --skip-missing
# 5. lock ×2 (must be 100% verified ×2, zero warnings) — THEN paper edits
python3 sp2027/analysis/results_lock.py && python3 sp2027/analysis/results_lock.py
# 6. replace marks from the emitted evidence → census re-pin → pdflatex ×2 → page levers if body > 13pp
```

**Historical next steps:** these commands were not run after the halt; the
final disposition above supersedes this fill plan.

## Final disposition — 2026-10-03

All 24 logical pending marks are closed in the authoritative S&P manuscript
without inventing measurements or modifying raw records:

| Group | Marks | Final disposition | What the paper may claim |
|---|---:|---|---|
| W3 | 19 | **Experiment failed to complete; closed in the manuscript as an audit-only non-result.** It halted at 33/270 scheduled graded sessions. `INDEX.jsonl` has 38 rows, 32 unique physical records, and 10 identity defects; the reconciliation inventory is diagnostic only. | No campaign ASR, FSR, latency distribution, Kaplan--Meier curve, outage band, slot comparison, or model ranking. |
| W4 | 1 | **Closed by exclusion.** The campaign corpus is not identity-valid, so campaign sensitivity re-grading would not produce an admissible estimand. | The completed legacy/pilot sensitivity results remain; no W3 regime comparison is claimed. |
| W5 | 4 | **Closed as not collected.** The available round is a four-model AI diagnostic over 30 items, not external-human annotation. | Report AI diagnostic agreement as an instrument stress test only; do not claim human inter-rater reliability or human taxonomy validation. |

The completed E3 timing factorial, E1 audit, pilot, fixed-executor arm,
agent-loop arm, hybrid-policy control, and escrow-blinded rerun remain in
scope under the number lock. No provider account, model
call, campaign worker, raw-record rewrite, external artifact release, or
submission action was performed to close this register.

The terminal campaign state is also enforced in code: provider launchers and
continuation/fill paths refuse the failed 33/270 campaign through
`sp2027/ledger/CAMPAIGN_STATE.json` and `sp2027/ops/campaign_guard.py`.
