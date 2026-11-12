# PREREGISTRATION — P010L4: fourth-label replication of the information-contract 2×2

**Namespace:** `sp2027/research_execution/info_contract_label4_20261030/`
**Date frozen:** 2026-10-30, before any provider call under this protocol.
**Authorization:** campaign opened by explicit project-owner instruction
(2026-10-30, "استخدم دول" + key rotation), the same amendment mechanism as
P010L2/P010L3. Budget hard stop **$10** (opus-class pricing was anticipated;
actual per-session cost is recorded per call and the ceiling's met/not-met
status is reported either way, never hidden).

## 0. Label designation and the X1 discipline

The owner designated the opus label (`claude-opus-5-5`). The gateway returned
**HTTP 503 for every opus identifier variant across both keys (12/12 attempts,
`HEALTH.json`)** while the gpt labels responded normally (3.9–4.0 s), so the
label was selected from the gateway's own attested list: **`gpt-5.6-sol`** —
a GPT-family version no prior cohort has used.

**The X1 lesson is binding on this cohort:** P010X1's label claim was
withdrawn on 2026-10-30 because its configuration-only redirect was inert and
no pre-freeze route-identity check existed. This cohort therefore (a) ran a
pre-freeze **route-identity fingerprint probe** (`HEALTH.json`: the raw
response's own `model` field echoes `gpt-5.6-sol` on this route), and (b) is
conditional on a **post-run fingerprint audit**: every raw response in
`raw_provider_responses/` must echo `gpt-5.6-sol`; any mismatch voids the
cohort's label claims (numbers would be retained as mislabeled-at-runtime,
reported as such).

## 1. Design (frozen)

- **Protocol:** the frozen P010 runner, imported byte-for-byte
  (`run_info_contract_2x2_chacha20.py`, SHA-256 `a08eab6f…83ee198`, asserted
  at launch), driven by a wrapper that changes **only**: output namespace,
  protocol label, seed list, Latin-square rotation modulo 4, provider
  transport (D1), token floor (D2), and the label binding (D3). Prompts, cell
  slots, fixture, oracle, policy, feedback strings, temperature
  provider-default, and turn flow are the frozen module's own code.
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−), identical slots
  to P010/P010P/P010N16/P010L2/P010L3, byte-identical prompts for the same
  seed.
- **Seeds:** 211–218. Verified unused on 2026-10-30 by scanning every
  `results.jsonl` under `sp2027/research_execution/**` for
  `seed ∈ [211,218]` (zero hits). Two balanced Latin squares (rotation index =
  seed index mod 4).
- **Sessions:** 4 cells × 8 seeds = 32 sessions; ≤2 turns; one provider call
  per turn; resume at seed granularity with earliest-row-per-(seed, cell)
  retained.
- **Model label:** `gpt-5.6-sol` on `https://agentrouter.org` via the
  Anthropic-compatible `/v1/messages` path, key rotated by the owner
  2026-10-30 (`.env`, gitignored).

## 2. Transport deviations (disclosed)

- **D1 — provider injection** (identical to P010L2/L3): the AgentRouter
  adapter (`provider_adapter_agentrouter.py`, SHA-256 `d26dd920…aaa3dc`) is
  registered as `provider_adapter` in `sys.modules` before the frozen runner
  is imported; the frozen file is untouched and byte-asserted. The adapter
  sends `User-Agent: claude-cli/…`, without which the route returns 401.
- **D2 — token floor** (identical to P010L2/L3): 1400 → 2800 uniformly for
  every cell, recorded per-call as `max_tokens_sent`. A reasoning-family
  label that exhausts its budget mid-reasoning would truncate and correlate
  with cell; the floor removes that confound.
- **D3 — label binding** (new, the X1 lesson): the label is bound via
  `AGENTROUTER_LABEL_MODEL=gpt-5.6-sol` before import AND verified by the
  pre-freeze fingerprint probe and the mandatory post-run fingerprint audit
  (§0).

## 3. Pre-freeze evidence (NOT evidence)

One label-selection + route-identity probe (2026-10-30, `HEALTH.json`):
attested list under the rotated key, one generic 32-token call on
`gpt-5.6-sol` whose raw body's `model` field echoes `gpt-5.6-sol` exactly.
No fixture, no cell slots, no oracle — unusable as evidence by construction.

## 4. Statistics (frozen, identical to every information-contract cohort)

- **Primary (pre-specified):** paired C1-versus-C4 discordance on the 8
  shared seeds, exact binomial two-sided. Floor at n=8: p = 0.0078 requires
  8/0; the cohort's registered decision rule mirrors P010L3's.
- **Premise marginal** (B+ vs B−): Fisher exact, one- and two-sided;
  seed-stratified CMH post hoc.
- **Naming marginal:** Fisher exact (expected inert).
- **Falsifiers (frozen):** F1 (the paired discordance ≤ 2 → the premise share
  does not transport), F2 (C3 < C1 → naming gates), F3 (C2 ≥ C1 → the derive
  frame sustains success without the premise).
- Separate population; never pooled with any other cohort; cross-cohort
  counts appear only as labeled descriptives.

## 5. Post-run requirements (binding)

1. **Fingerprint audit:** every `raw_provider_responses/*.json` `model` field
   must equal `gpt-5.6-sol`; the audit result is recorded in the namespace.
2. **Leak scan** over all prompts and raw responses (same scanner family as
   P010L3).
3. **Analysis** mirrors `analyze_label3.py` on the earliest-row rule.
4. This file, `FREEZE.json`, and the wrapper are committed before the first
   experiment model call; the freeze hashes bind all of them.
