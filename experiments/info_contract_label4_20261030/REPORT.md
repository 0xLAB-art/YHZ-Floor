# REPORT — P010L4: fourth-label replication of the information-contract 2×2

**Namespace:** `sp2027/research_execution/info_contract_label4_20261030/`
**Protocol:** `P010L4-INFO-CONTRACT-2X2-CHACHA20-LABEL4-v1`
**Label:** `gpt-5.6-sol` on `https://agentrouter.org`, Anthropic-compatible `/v1/messages`
**Frozen:** `PREREGISTRATION.md` + `FREEZE.json`, committed before the first
experiment call (2026-10-30T00:32Z)
**Run:** 2026-10-30 · 32/32 terminal sessions · 0 instrument duplicates ·
**14 provider-side failures** (route degradation during the run —
EMPTY\_RESPONSE-class with no model body at all, terminal and never retried
per protocol; disclosed in §1 and bounded in §3)

## 0. Label designation

The owner designated `claude-opus-5-5`; the gateway returned HTTP 503 for all
six identifier variants across both keys (12/12 attempts, `HEALTH.json`)
while the gpt labels responded in 3.9–4.0 s, so the label was selected from
the gateway's attested list: `gpt-5.6-sol` (a GPT-family version no prior
cohort used). The **X1 discipline** was applied: a pre-freeze route-identity
fingerprint probe (raw body `model` echoes `gpt-5.6-sol`) and a mandatory
post-run fingerprint audit.

## 1. Result

| Cell | Naming (A) | Premise (B) | Accepted | First-turn accepted | Provider failures (no body) |
|---|---|---|---:|---:|---:|
| C1 | named | stated | 8/8 | 8 | 0 |
| C2 | withheld | unstated | 2/8 | 2 | 6 |
| C3 | withheld | stated | 8/8 | 8 | 0 |
| C4 | named | unstated | 0/8 | 0 | 8 |

- **Primary (preregistered): paired C1-versus-C4 discordance on the 8 shared
  seeds = 8, all C1 wins (8/0), no ties — exact binomial two-sided
  p = 0.0078** (the n=8 resolution floor). This contrast is evaluable only
  under the protocol's terminal-failure rule: a provider EMPTY\_RESPONSE is
  counted as a non-acceptance and never retried. Under it, C4 contributes
  8 non-acceptances, none of them an oracle rejection.
- **Premise marginal: 16/16 stated vs 2/16 withheld — Fisher one-sided
  p = 2.55e-7, two-sided p = 5.09e-7**; seed-stratified CMH χ² = 19.6,
  p = 9.5e-6, 8 strata (uncorrected, post hoc). Same convention: the 14
  withheld-arm sessions that received no model body enter the denominator as
  non-acceptances.
- **Naming marginal: 8/16 vs 10/16 — Fisher two-sided p = 0.7224 (inert).**
- The stated arm is first-turn deterministic (16/16, one submission each).
- **What this cohort does and does not show.** It re-measures the stated
  arm's determinism and the withheld arm's failure to produce an accepted
  program; it does **not** re-measure C4's rejection degree, because every
  C4 session died at the provider before any submission. F1 (the premise
  share transports) is FALSE under the registered non-acceptance rule; F2
  (naming gates when the premise is stated) is FALSE; F3 (the derive frame
  sustains success) is FALSE, resting here on C2's 2/8 rather than on an
  observed C4 rejection pattern.

## 2. Fingerprint audit (the X1 discipline, binding)

All 18 raw responses echo `model: gpt-5.6-sol` (Anthropic-style `message`
objects, `chat…`/`res…` ids); **0 mismatches** — the label claims are valid.
(`ANALYSIS.json` §fingerprint_audit.) The 14 failed sessions returned no body,
so they carry no fingerprint either way; they carry no evidence either.

## 3. Route degradation disclosure

14 of 32 sessions received no model body (`EMPTY_RESPONSE` at the gateway;
terminal per the frozen resume rule — never retried): **C2 seeds 212, 213,
214, 215, 216, 218** and **every C4 session (seeds 211–218)**. All 14 failed on
turn 1, before any submission, so no accepted session and no turn-2
observation exists for them. The two stated cells (C1, C3) are untouched
(8/8 each, first-turn). The gpt-5.6-sol route was measurably flakier than the
P010L3 route (0 failures) — a label-level serving-quality observation, not a
premise effect, and the reason this cohort bounds the marginal rather than
C4's degree.

## 4. Cost

The 18 provider responses carry usage blocks in
`raw_provider_responses/*.json`: **6,209 input and 11,389 output tokens**.
At the published AgentRouter ratio bases (the route does not expose which
applies) that is **$0.11 (ratio-3, $6/M + $6/M)** to **$0.25 (ratio-2,
$4/M prompt + $20/M completion)** against the **$10 hard stop** registered in
the preregistration — met under both bases. The accounting row is appended to
`../BUDGET_LEDGER.jsonl` (`namespace: info_contract_label4_20261030`,
`call_type: SESSION`). `events.jsonl` records session lifecycle, not usage.

## 5. Reading (bounded)

Under a route whose serving quality degraded mid-run, the fourth
provider-attested label reproduces the stated arm's first-turn determinism
(16/16) and the withheld arm's failure to be accepted (2/16, 14 sessions lost
to provider failures before any submission). The cross-label inference stays
descriptive and is never pooled; C4's degree is left unmeasured in this
cohort and is not claimed. The cross-vendor question remains open (P010X1
withdrawn to same-label).
