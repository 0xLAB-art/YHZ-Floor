# P011-L3-N32 — REPORT (registered scale-up, third label, ChaCha20)

**Protocol:** `P011-INFO-CONTRACT-2X2-CHACHA20-LABEL3-N32-v1`
**Namespace:** `sp2027/research_execution/info_contract_label3_n32_20261101/`
**Registered:** before the first call (`PREREGISTRATION.md`). Design frozen: same
runner bytes (`a08eab6f…`), same prompts, same fixture, same oracle, per-cell n
raised from 8 (P010L3) to 32, seeds 301–332.
**Analysis rule:** earliest row per (seed, cell) (`analyze_p011.py`, frozen before
completion); terminal provider failures counted, never retried, never imputed.

## 1. What was registered

4 cells × 32 fresh seeds = 128 sessions, no adaptive stopping, no interim peeking.
Registered resolution: paired exact McNemar resolves one-directional 32/0 at
two-sided p = 8.63e-10; Fisher on the premise marginal at n=32 is significant for
any withheld count ≤ 6.

## 2. What was recorded

| Cell | Slots | Accepted | Evaluable | Provider drops |
|---|---|---:|---:|---:|
| C1 | A+ B+ | **27/32** | 27 | 5 |
| C2 | A− B− | **0/32** | 20 | 16 |
| C3 | A− B+ | **30/32** | 30 | 2 |
| C4 | A+ B− | **0/32** | 20 | 12 |

- 128 registered sessions, 128 rows recorded; **one instrument-duplicate row**
  (`…C1__seed_301__e72a28984ec2`) flagged by the frozen analysis and never deleted.
- **35 terminal provider drops** of 128 sessions (27%), all provider-side
  (`EMPTY_RESPONSE` / `NO_BODY` class), all before any submission.
- Stated arm: **57/57 accepted** (C1 27 + C3 30), 95% Wilson CI 93.7–100.
  Withheld arm: **0/36**, 95% Wilson CI 0–9.6.

### Primary (registered)

Paired C1-vs-C4 discordance on shared, both-evaluable seeds: **17/0**, exact
binomial two-sided **p = 1.53e-05**. Direction is one-way and the withheld arm
never wins a pair.

### Secondary (registered, descriptive)

Premise marginal 57/57 vs 0/36, Fisher exact two-sided p underflows to 0.0 in
scipy (reported as `< 1e-300`, not as an exact value).

## 3. Two findings that only exist at this size — both against the paper's current wording

**(a) The stated arm is not deterministic.**
At n=8 the same label read 8/8 (C1) and 8/8 (C3). At n=32 it reads **27/32
(84.4%, 68.2–93.1)** and **30/32 (93.8%, 79.9–98.3)**. The registered
"stated-arm determinism" phrasing is therefore a small-n artefact of this route;
at the cohort's own registered size the honest statement is a rate with an
interval, not determinism. This is a falsifier landing on the paper's current
sentence, not on the premise contrast.

**(b) Provider dropout is asymmetric across cells.**
Withheld arms lost 16/32 (C2) and 12/32 (C4) sessions to provider failures, stated
arms lost 5/32 (C1) and 2/32 (C3). The paired test therefore runs on **17 pairs,
not the registered 32**, so the registered p = 8.63e-10 resolution was never
achievable in this cohort. The asymmetry is disclosed here and must be carried
into the paper: the withheld denominator is 20, not 32, per cell.

## 4. What this cohort does and does not change for the manuscript

- **Does:** adds a registered n=32 replication of the paired contrast on the
  third label (17/0, p=1.5e-05) and a 1,503 → 1,631 session inventory figure.
- **Does:** forces two wording corrections — stated-arm determinism → stated-arm
  rate with CI; and the paired denominator (17 evaluable pairs) stated next to
  the registered resolution.
- **Does not:** turn the external boundary into a transfer (F1 stays FALSE), and
  does not pool with any prior cohort. Nothing here is a capability rate.

## 5. Files

`ANALYSIS.json` (machine-readable, emitted by `make_analysis_p011.py` over the
frozen `results.jsonl`) · `PREREGISTRATION.md` · `results.jsonl` (128 rows +
1 flagged duplicate) · `events.jsonl` · `raw_provider_responses/` ·
`prompts/` (178 files) · `execution_captures/` · `summary.json` · `runner_console.log`.
