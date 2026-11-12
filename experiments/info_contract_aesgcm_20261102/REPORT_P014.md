# P014 — AES-GCM nonce-reuse cohort: completed analysis

**Protocol:** `P014-INFO-CONTRACT-2X2-AESGCM-NONCE-REUSE-v1`
**Namespace:** `sp2027/research_execution/info_contract_aesgcm_20261102/`
**State:** COMPLETE — 64/64 registered slots, 64 sessions recorded, 62 provider
responses, 19 terminal provider failures.
**Label:** `gpt-6-astra` via AgentRouter (`_LAUNCH.json`), token floor 2800.
**Generated:** 2026-11-02T10:18 local · estimator frozen before completion.

Sources: `summary.json` (runner), `analysis_p014.txt` (frozen
`analyze_p014.py`), `analysis_p014_exact.json` (exact scipy values for the
tests the frozen script prints at its float floor), `results.jsonl`,
`events.jsonl`, `raw_provider_responses/`.

## 1. Per-cell outcomes

| cell | premise | naming | accepted / evaluable | submissions | turns | terminal drops |
|---|---|---|---|---|---|---|
| C1 | stated | named | **16 / 16** | 16 | 16 | 0 |
| C2 | withheld | unnamed | 0 / 2 | 7 | 7 | **14** |
| C3 | stated | unnamed | **16 / 16** | 16 | 16 | 0 |
| C4 | withheld | named | 0 / 11 | 23 | 23 | **5** |

The two stated-premise cells accepted on every evaluable session. Neither
withheld-premise cell accepted any.

> **Correction (2026-11-03).** This table previously transposed the `premise`
> and `naming` labels for C3 and C4. The frozen cell map in
> `run_info_contract_2x2_aesgcm.py` is `C3 = (A_MINUS, B_PLUS)` (family
> unnamed, premise stated) and `C4 = (A_PLUS, B_MINUS)` (family named,
> premise withheld), and the premise marginal below (`32/32 vs 0/13`, where
> C1+C3 are the stated cells) already assumed that map. Only the two labels
> changed; no count, denominator or test moved, and `analysis_p014.txt`
> remains the frozen artifact.

## 2. Registered primary test

Paired C1-vs-C4 discordance over **evaluable** pairs:

- evaluable pairs: **11** (registered denominator 16 — five pairs lost to C4
  dropout)
- discordant `C1-accepted / C4-rejected`: **11**
- discordant `C1-rejected / C4-accepted`: **0**
- exact two-sided binomial **p = 9.77 × 10⁻⁴** (= 2⁻¹⁰)

## 3. Prespecified descriptives

| contrast | counts | Fisher two-sided |
|---|---|---|
| premise marginal (C1+C3 vs C2+C4) | 32/32 vs 0/13 | **1.37 × 10⁻¹¹** |
| naming marginal (C1+C4 vs C2+C3) | 16/27 vs 16/18 | 0.045 |
| attrition (withheld vs stated) | 19/32 vs 0/32 dropped | **7.97 × 10⁻⁸** |

Premise odds ratio with Haldane–Anscombe correction: **1755** (undefined
uncorrected, because both withheld cells are zero).

`analyze_p014.py` prints `p=0.0` for the premise marginal — that is its float
display floor, not a probability. The exact value above comes from
`scipy.stats.fisher_exact` on the same table; **the frozen estimator was not
edited after results**, and `analysis_p014.txt` remains the frozen artifact.

## 4. Falsifier checks (prespecified)

| id | rule | outcome |
|---|---|---|
| **F1** | C1 < 12/16 ⇒ instrument-difficulty, not a premise result | C1 = **16/16**, not triggered |
| **F2** | C3 materially below C1 ⇒ naming gates success | C3 = **16/16** = C1, not triggered — naming does not gate on this fixture |
| **F3** | C2 near C1 ⇒ success without hitting the premise, a real negative | C2 = **0/2** evaluable, not triggered |
| **F4** | cross-label divergence withdraws the replication claim | single-label cohort, not applicable (P016 runs the other labels) |

## 5. The result that constrains every reading of §2–§3

**Attrition is cell-correlated and severe.** All 19 terminal failures landed in
the withheld-premise cells: C2 lost 14 of 16 (87.5 %), C4 lost 5 of 16 (31.3 %),
C1 and C3 lost none. Fisher p = 7.97 × 10⁻⁸ on that contrast.

Consequences that must be stated wherever these numbers are used:

1. **The premise marginal's denominator is 13, not 32.** It is a contrast over
   the sessions that actually produced a model response.
2. **"Withheld arms never succeed" is not the same claim as "withheld arms
   never answer."** Filtering the "no answer" rows into the denominator would
   be conditioning on a post-treatment variable — the dropout is plausibly
   *caused* by the arm (the withheld prompt forces work the agent cannot
   finish), so the honest reporting unit is the registered session, with the
   dropout shown and the evaluable contrast shown beside it.
3. **The paired test is over 11 pairs, not 16**, and its p-value is conditional
   on those pairs. It is neither a 16-pair result nor a claim about the five
   sessions where C4 went silent.
4. **The failure mechanism is a budget effect, not a refusal.** Stored
   bodies from withheld-arm sessions that did complete burned 2546–2726 output
   tokens to emit 506–617 characters, against 512–1150 tokens for stated-arm
   responses (`INSTRUMENT_NOTE_dropout.md`). The 2800-token floor is
   near-binding exactly in the arms under test, so the dropout channel and the
   treatment channel are not cleanly separable in this cohort.

## 6. Deviations, disclosed

- **Provider injection** of `provider_adapter_agentrouter.py` before the frozen
  runner import; runner bytes asserted against `_REGISTRATION.json`.
- **Token floor 2800** (runner requests 1400), recorded per call as
  `max_tokens_sent`; rationale and its consequences are in §5.
- **One duplicate slot** `(seed 401, C1)` from a killed first launch; both rows
  accepted, earliest kept, disclosed in `DISCLOSURE_duplicate_slot.md`.
- **Finalizer liveness bug**, caught after the cohort: `pgrep -f
  run_p014_aesgcm` matched unrelated shells that merely mentioned the script,
  so the first finalizer instance waited instead of firing. Fixed to use the
  recorded `RUN_PID`; the analysis was then produced from the complete
  `results.jsonl` with no data change. No session, cell or verdict was altered
  by the delay.

## 7. What this cohort supports

- On a **third hidden-premise fixture** and the **first AEAD family**, withholding
  the load-bearing premise sentence is followed by zero oracle acceptances in
  the withheld cells and universal acceptance in the stated cells, with the
  paired discordance 11–0.
- Naming the family and benefit is **not** sufficient: C3, which receives the
  naming sentence but not the premise content, matches C1 (16/16); the naming
  marginal is weak and opposite in sign to a naming effect (16/27 vs 16/18).

## 8. What this cohort does not support

- No capability rate, no claim that the model "cannot" break GCM, no causal
  effect size: the design identifies a mechanism contrast under differential
  attrition.
- No provider or label generality — one label, one route (P015 cancelled with
  zero sessions; P016 is the within-route label replication).
- No pooling with ChaCha20, AES-CTR, ECDSA or RC4. A cross-fixture table is
  descriptive only and is not built here.
- No claim about the five pairs lost to C4 dropout, and none about the 14 silent
  C2 sessions beyond "no response was recorded".
