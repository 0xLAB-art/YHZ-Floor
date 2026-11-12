# PREREGISTRATION — P017: AES-GCM at a data-derived token floor (withheld-arm follow-up)

**Namespace:** `sp2027/research_execution/info_contract_aesgcm_p017_20261102/`
**Date:** 2026-11-02 · Written before any provider call under this protocol.
**Status:** registered; runner SHA-256 in `_REGISTRATION.json`, asserted at launch.

## 1. The defect this cohort addresses

P014 (`REPORT_P014.md`) returned 16/16 accepted in both stated-premise cells and
0/n in both withheld cells, paired discordance 11–0 — but **19 of 32 withheld
sessions produced no response at all** (C2 14/16, C4 5/16), against 0/32 in the
stated cells (attrition Fisher p = 7.97 × 10⁻⁸). Measured completion length
explains it:

| arm | output tokens (median / max) |
|---|---|
| C1 stated | 884 / 1264 |
| C3 stated-premise, withheld-naming | 922 / 1764 |
| C2 withheld-premise | 2573 / 2726 |
| C4 withheld-naming | 2199 / 2747 |

The P014 floor was **2800**, i.e. **53 tokens above the maximum observed
completion**, and inside the arms under test. The withheld arms needed roughly
3× the stated arms' budget, so the dropout channel and the treatment channel
were not separable: "withheld premise ⇒ no acceptance" could not be distinguished
from "withheld premise ⇒ no answer within budget".

## 2. The single change, and why its value is what it is

**Token floor 2800 → 4200**, applied **uniformly to all four cells**, with the
runner, fixture, cells, slots, oracle, policy, sandbox and prompts untouched.

`4200 = round_up(1.5 × 2747, 400)`, where 2747 is the maximum completion observed
in P014. 1.5× the **maximum**, not the mean, because the failure mode is the tail
— a long reasoning pass that emits no final text. The rule is fixed here, before
P017 runs, and is not tuned to any P017 observation. Applied uniformly so no cell
gains a budget advantage that could manufacture an arm difference; a cell-specific
floor would be a treatment, not a fix.

## 3. Design

- **Runner:** `run_info_contract_2x2_aesgcm.py`, byte-identical to P014 (SHA
  asserted). Nothing about the task contract changes.
- **Cells:** all four, C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−). The
  withheld arms are the target, the stated arms are the same-budget reference
  inside the same cohort; running only C2/C4 would leave no within-cohort
  contrast for attrition.
- **Seeds:** 701–716, fresh and disjoint from every declared list (…, 401–416
  P014, 501–516 P015-unused, 601–616 P016). Four balanced Latin squares.
- **Sessions:** 4 × 16 = 64. ≤2 turns, one provider call per turn, runner
  requests 1400, adapter sends 4200 and records both.
- **Label:** `gpt-6-astra` (same label as P014, so the floor is the only changed
  variable), AgentRouter, sequential after P016 exits — one key, one cohort at a
  time.
- **Provider failures:** terminal per session, never retried, never imputed.

## 4. Analysis plan (frozen before any call)

**A1 — attribution (primary for this cohort's purpose).**
Response rate per cell. Prespecified decision rule:

- withheld-arm dropouts **≤ 2 per cell** ⇒ the P014 attrition is attributed to
  the budget and P014's acceptance results stand as reported, now with a
  same-instrument replication;
- withheld-arm dropouts **between 3 and 7 per cell** ⇒ budget explains part of
  it; both the dropout table and the acceptance table are reported, and no
  single-cause statement is made;
- withheld-arm dropouts **≥ 8 per cell** ⇒ the budget hypothesis **fails**; the
  dropout is not budget-bound, and this is reported as the cohort's main finding
  with the acceptance table as secondary.

**A2 — acceptance at adequate budget.** Per-cell accepted/evaluable, and the
paired C1-vs-C4 discordance on evaluable pairs, exact binomial two-sided, with
the evaluable-pair denominator stated. If any withheld session is accepted, the
P014 conclusion is **revised**, not defended: the withheld premise would no
longer be necessary on this fixture.

**A3 — descriptive crosses.** Dropout and acceptance against P014 at 2800
(descriptive only, no pooled estimate). Premise and naming marginals as in P014,
over evaluable sessions.

**Falsifiers:**
- **F1** C1 < 12/16 ⇒ instrument-difficulty on the stated arm at this floor, and
  the cohort cannot speak to the withheld arms either.
- **F2** C2 ≥ 12/16 accepted ⇒ premise is not load-bearing; P014 is revised.
- **F3** withheld dropout ≥ 8/16 in either withheld cell ⇒ budget attribution
  fails (rule A1-3).
- **F4** non-monotone pattern: withheld arms drop less but accept no more ⇒
  report as a floor artefact resolved with no change to the effect.

## 5. Discipline

Cost expectation ≤ $2 (P014: 63 ledgered calls, $1.57 at this basis; the larger
floor bills only on generated tokens). Every call appended to
`sp2027/research_execution/BUDGET_LEDGER.jsonl`. Leak scan over prompt files
before analysis. No mid-cohort change; any protocol edit forces a new number. No
retry of P014's failed sessions — P017 uses fresh seeds and is its own cohort.
