# W3 Fill Runbook — from corpus to filled paper, in order

> **SUPERSEDED — 2026-10-03.** The planned 270-session E2 experiment failed
> to complete and halted at 33/270 scheduled graded sessions. Its source index
> is identity-invalid, so W3/W4 population estimates are excluded and W5 human
> annotation was not collected. The commands below preserve pre-campaign
> provenance and rehearsal logic only; do not launch providers, fill the paper,
> or treat the reconciliation inventory as a repaired corpus without a new,
> explicitly authorized campaign decision.

Built 2026-09-30 (pre-campaign) so the fill is execution, not improvisation.
**Rehearsal status: Steps 0→4 passed end-to-end on the real W2 pilot
(2026-09-30, ledger) — every number matched the paper's locked facts.**
**Day-1 lesson (T3-DAY1, 09-30): any launch-day code change to the harness
(rule-(a) spares, prompt fixes) MUST pass the null-content stub regression
(stub LLM returning 200 content:null → clean gateway_unavailable summary,
not a crash) BEFORE first light — three day-1 sessions were lost to exactly
this crash class.** The regression now exists as a runnable gate:
`cd ACTS-ATTACK/harness/v2 && OPENROUTER_API_KEY= python3 -m unittest test_null_content_stub -v`
(6 tests, local stub server, zero network/quota; written 2026-09-30 after
the fix landed in agent_loop_v2.request_action).
Every tool below exists and is tested; "no corpus yet" exits are expected
before 2026-10-05. The order matters: nothing enters the paper until the
lock re-derives it.

**Inputs:** `sp2027/agent-eval/runs_e2/` (the frozen campaign corpus;
gate-authorized launch per `ops/W3A_DAY_CHECKLIST.md`).
**Hard rule:** the validator (`schema/acts_audit.py validate ...`) must be
exit-0 over the corpus before any fill runs — a HARD-failed row never
enters a table (frozen discipline).

## Step 0 — Corpus sanity (daily, from day 1)

```bash
python3 sp2027/schema/acts_audit.py validate sp2027/agent-eval/runs_e2 --format text   # exit 0 required
python3 sp2027/analysis/w3_fill.py --dry-run                                            # census only
```

## Step 1 — Primary numbers (Table 3 + prose) — tool: `w3_fill.py`

```bash
python3 sp2027/analysis/w3_fill.py --emit-tex
```

Emits `w3_fill_evidence.json` (+ `w3_fill_table3.tex` fragment).
Fills the marks behind: Table 3 cells (ASR per slot with the frozen
denominator rule + Wilson CIs via `acts_stats.asr_cell`), operational-yield
columns, FSR under the independent oracle (e4's claim-submitted semantics),
median T_agent, outcome census, AOR_op/AOR_exec distributions.

## Step 2 — KM + the three-way outage band — tool: `bounds_tier.py`

```bash
python3 sp2027/analysis/bounds_tier.py \
  --claim "median time-to-success < 900 s"     # example; declare from data
```

Emits `bounds_tier_evidence.json` (tier1 censored / tier2 competing-risk
Aalen-Johansen / tier3 worst-case). Fills the two KM marks; a curve claim
enters the paper ONLY if it holds in all three tiers (frozen text).

## Step 3 — Latency decomposition + paired Fig 3 data

```bash
python3 sp2027/analysis/aor_decompose.py sp2027/agent-eval/runs_e2
```

Emits `aor_runs_e2.json` — component seconds, agent-reported op spans
(`tte_op_agent_ns` — the pre-registered AOR_op primary; W3 agents emit
OPSPAN_NS, pipeline verified end-to-end in `no_llm_pilot`/`test_v2`),
paired T_exec↔T_agent rows for the within-session figure upgrade.

## Step 4 — W4 sensitivity — tool: `e4_sensitivity.py --campaign`

```bash
python3 sp2027/analysis/e4_sensitivity.py --campaign sp2027/agent-eval/runs_e2 --skip-missing
```

(additive flag, 2026-09-30; default behavior byte-identical, regressions 43/43)
Scores the campaign through the identical A/B/C oracle regimes + rank-flip.
Fills the single [PENDING-W4] mark.

## Step 5 — Lock, then edit the paper

```bash
python3 sp2027/analysis/results_lock.py && python3 sp2027/analysis/results_lock.py
```

Only NOW does anyone touch `paper/main.tex`: replace `[PENDING-W3/W4]`
marks with the emitted numbers, update the census in `PAPER_HEADER_CENSUS`,
add one re-derivation claim per filled table (claim_e2_primary,
claim_km_band, ...), extend `CLAIMS` with the new artifacts. The lock must
be 100% verified ×2 with zero warnings BEFORE `pdflatex`.

## Step 6 — Build + page budget (ledger 2026-09-30 plan)

Body ≤ 13 pp ⇒ done; else levers in order: Table 1 footnotesize →
pilot-subsection dedup → Fig 3 height → appendix trim (last resort).
Related Work and every number are never compression targets.

## What remains human (not automatable by design)

- Interpretation without overclaiming (reviewer directive, 2026-09-30).
- W5: the 54-cell blind re-audit + Fleiss κ (external annotators, round-1
  window 10-05..10-11; D4 confirmation due 10-06) — fills the six
  [PENDING-W5] marks, then the statistics lock extends the CLAIMS table.
- Abstract flip future→found, contribution #3 plan→evidence (W6 punch list).
