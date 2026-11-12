# P011-INFO-CONTRACT-2X2-CHACHA20-LABEL3-N32-v1 — PREREGISTRATION
# SCALE-UP COHORT (registered before the first call; hash-frozen)

**Registered:** 2026-11-01, immediately before launch.
**Purpose:** registered scale-up replication of P010L3 (third-label, AgentRouter
gpt-6-astra). Per-cell n grows from 8 to 32. No other design change.

## Design

- Frozen methodology byte-for-byte: FROZEN RUNNER `run_info_contract_2x2_chacha20.py`
  SHA-256 `a08eab6f4be2401aacf1b39a47ba6960373164dcc57640d3672d8c36583ee198`
  asserted at launch. Identical prompts, cell slots, fixture, oracle, policy,
  feedback strings, temperature provider-default, turn flow.
- Provider injection (two disclosed deviations identical to P010L3):
  1. transport adapter `provider_adapter_agentrouter.py`
     SHA-256 `d26dd920d8c2dda1d4ef919daa07d3e82dcd8109f14175e335f2da428aaaa3dc`
     injected as `provider_adapter` before the frozen runner import; token floor
     2800 uniformly per call for all cells (max_tokens_sent recorded).
  2. (cosmetic, disclosed) run_id prefix literal differs in this namespace;
     rows identified by protocol field.
- **Protocol:** P011-INFO-CONTRACT-2X2-CHACHA20-LABEL3-N32-v1
- **Cells:** C1, C2, C3, C4 (frozen 2x2: A = naming, B = premise stated).
- **Seeds:** 301..332 (32 per-cell seeds; fresh, no overlap with any earlier
  cohort; Latin rotation mod 4 identical rule).
- **Total sessions:** 4 cells x 32 seeds = 128 registered sessions before the
  first call. No adaptive stopping; no interim peeking rule; the full grid runs
  regardless of interim outcomes.
- **Power (registered expectation at n=32, per-cell):** exact paired McNemar
  with 32 discordant pairs resolves one-directional 32/0 at two-sided
  p = 8.63e-10; 31/1 at 1.34e-9; 6/0 floor rule (2 of 6+ one-directional)
  unchanged. Premise marginal Fisher exact at 32/32 vs k/32 is significant at
  any k<=6 at 4.5e-12 or stronger. The cohort's own registered design
  resolution table: detectable one-directional paired shift 0/32 vs 32/32.

## Analysis plan (frozen before the first call)

Primary inferential test, unchanged from P010L3: paired C1-vs-C4 discordance on
shared seeds, exact binomial two-sided, with the pre-specified discordance floor
rule applied against our own interest (a 5/0-style outcome at n=32 remains
NON-SIGNIFICANT unless the registered floor is met). Secondary descriptives:
premise marginal, naming marginal, per-seed per-cell counts, turn counts,
submissions, provider-failure row-status drops (recorded, never imputed).

Deviations from the registered plan are admitted at analysis time as
post-hoc-noted, not absorbed into primary inference.

## Corrections policy

Any gamma-style error is corrected at analysis time with frozen counts
unchanged (the P010L3 precedent). Results are never redecorated after the fact.
