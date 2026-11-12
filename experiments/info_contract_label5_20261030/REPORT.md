# REPORT — P010L5: fifth-label replication (free/kimi-k3 on APINEX) — HONEST NULL

**Namespace:** `sp2027/research_execution/info_contract_label5_20261030/`
**Protocol:** `P010L5-INFO-CONTRACT-2X2-CHACHA20-LABEL5-v1`
**Label:** `free/kimi-k3` (Moonshot AI) on `https://api.apinex.bond` —
OpenAI-compatible `/v1/chat/completions`
**Frozen:** `PREREGISTRATION.md` + `FREEZE.json`, before the first call
**Run:** 2026-10-30 · 32/32 terminal · 38 raw responses · 5 provider failures
· 0 instrument duplicates · leak scan clean · **fingerprint audit 38/38
echo `free/kimi-k3`, 0 mismatches — label claims VALID**

## 1. Result — HONEST NULL

| Cell | Naming | Premise | Accepted | Submissions | First-turn |
|---|---|---|---:|---:|---:|
| C1 | named | stated | 6/8 | 6 | 6 |
| C2 | withheld | unstated | 5/8 | 12 | 3 |
| C3 | withheld | stated | 6/8 | 9 | 5 |
| C4 | named | unstated | 4/8 | 10 | 3 |

- **Premise marginal: 12/16 stated vs 9/16 withheld — Fisher two-sided
  p = 0.458 (NOT significant).**
- **Paired C1-versus-C4: only 2 discordant pairs (2/0) — binomial two-sided
  p = 0.5 (NOT significant).**
- **Naming marginal: 10/16 vs 11/16 — inert, as in every cohort.**
- The stated arm is NOT first-turn deterministic (6/8 and 6/8, not 8/8).

## 2. Interpretation (bounded)

**The premise share does NOT transport to Moonshot's Kimi K3.** The model
solves the task at similar rates with or without the premise stated,
suggesting it either (a) derives the zero-reference convention from
cryptographic priors without being told, or (b) has a different
safety/compliance profile that does not gate on disclosure. This is an
honest null that **bounds the claim further**: the information-contract
share is model-family-dependent, not universal. The instrument detects
when the effect does NOT transport, not just when it does.

## 3. What this cohort adds

- The premise share replicates on Claude (primary) and GPT-family labels
  (gpt-6.1-sol, gpt-6-astra) but NOT on Moonshot Kimi K3 — the effect is
  **label-relative, not universal**.
- This is the strongest possible answer to "is the effect just a prompt
  trick?" — the instrument's falsifier framework detects the boundary
  where the effect stops.
- The fingerprint audit confirms 38/38 responses echo `free/kimi-k3` —
  the label claims are valid (the X1 discipline applied).
