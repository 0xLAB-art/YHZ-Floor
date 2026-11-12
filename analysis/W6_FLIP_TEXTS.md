# W6 Flip Texts — abstract/intro results-voice conversion (fill night)

> **SUPERSEDED — 2026-10-03.** The planned 270-session E2 experiment failed
> to complete and halted at 33/270 scheduled graded sessions. The authoritative
> manuscript now records that campaign as an audit-only non-result; no fill
> night, provider call, or paper rewrite using the parameterized fragments below
> is authorized. This file is retained only as pre-campaign provenance.

Applied AFTER w6_transform --apply and lock x2. Each fragment: BEFORE (frozen
text, verbatim) → AFTER (parameterized; `{...}` filled from the named artifact
field, never typed by hand — copy the printed values from the tools).

## F1 — Abstract/intro delivery sentence (§1, ~line 85)

BEFORE:
    A frozen 270-session campaign across three open-weight model slots is
    pre-registered to deliver the primary results: oracle-verified success
    rates per task and disclosure track, false-success rates under independent
    verification, latency decomposed into model, execution, retry, and
    residual components, and Kaplan--Meier failure-time curves that keep
    outages visible~[PENDING-W3].

AFTER:
    A 270-session campaign across three open-weight model slots delivered the
    primary results: oracle-verified success rates per task and disclosure
    track (ASR {w3.by_slot.O1.asr.value|O2|O3 — per-slot table in
    Table~\ref{tab:primary}}), false-success rates under independent
    verification (overall FSR {w3.fsr_overall} across {w3.graded} graded
    sessions), latency decomposed into model, execution, retry, and residual
    components (aor_decompose, Table~\ref{tab:aor}), and Kaplan--Meier
    failure-time curves that keep outages visible ({w3.outage_counts} provider
    outages retained as censored rows).

Guard: if {w3.graded} != 270, the sentence must instead state the graded
denominator and the outage/exclusion counts explicitly — never write "270"
against a different number.

## F2 — Contributions bullet (~line 163)

BEFORE:
    ... latency decomposed into model, execution, retry, and residual
    components, and failure-time curves that keep provider outages
    visible~[PENDING-W3] (Section~\ref{sec:results}).

AFTER:
    ... latency decomposed into model, execution, retry, and residual
    components, and failure-time curves that keep provider outages visible
    ({w3.outage_counts} censored; KM median time-to-success
    {bounds.median_tts_s} s, CI {bounds.ci}) (Section~\ref{sec:results}).

## F3 — Primary sensitivity result (~line 867)

BEFORE:
    The campaign's multi-model grid turns the regime comparison and the
    rank-flip test into the primary sensitivity result~[PENDING-W4].

AFTER (two variants — pick by what the data show, never by preference):
  - Flip found: "The campaign's multi-model grid turned the regime comparison
    and the rank-flip test into the primary sensitivity result: model ranking
    FLIPS between Oracle A (self-report) and Oracle C (independent oracle)
    ({e4.campaign.rankflip_detail})."
  - No flip: "The campaign's multi-model grid turned the regime comparison
    and the rank-flip test into the primary sensitivity result: model
    ranking is STABLE across all three oracle regimes ({e4.campaign.detail});
    stability under independent verification is itself the finding."

## F4 — Fleiss' kappa sentence (~line 176)

BEFORE:
    ... three external annotators score stratified samples~[PENDING-W5]
    (Section~\ref{sec:taxonomy}).

AFTER (human round):
    ... three external annotators scored stratified samples (Fleiss' $\kappa =
    {kappa.kappa:.2f}$ over {kappa.items}; {kappa.note}) (Section
    ~\ref{sec:taxonomy}).
  - D-ANNOT fallback (if triggered 10-15): Cohen's $\kappa$ with two
    externals + authors, disclosed as the pre-registered fallback.

## F5 — Table 3 caption (fills at w6_transform)

The caption's "fills from runs_e2 at W3" clause becomes "as graded by the
frozen validator; validator pass rate per cell" — w6_transform replaces the
cells; this caption clause flips in the same manual pass.

## Order of operations (fill night, after the campaign)

1. runbook Steps 0–4 (validator → fill --emit-tex → bounds --claim → aor → e4)
2. lock x2 (100%, zero warnings) — twice
3. `python3 sp2027/analysis/w6_transform.py --dry-run` → inspect preview
4. `--apply` (table cells + generic marks)
5. Apply F1–F5 above by hand, values copied from the artifacts (30–45 min)
6. pdflatex x2 → page check (13 pp; page levers if body grows)
7. Final grep: zero PENDING-W outside comments; every number greps back to an
   artifact; commit; then and only then: S&P upload.
