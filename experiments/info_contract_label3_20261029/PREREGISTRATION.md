# PREREGISTRATION — P010L3: third-label replication of the information-contract 2×2

**Namespace:** `sp2027/research_execution/info_contract_label3_20261029/`
**Date frozen:** 2026-10-29, before any provider call under this protocol.
**Motivation:** every information-contract cohort in the evidence-revision paper
runs on one or two provider-attested labels. Label 2 (`gpt-6.1-sol`) replicated
the premise marginal (16/16 vs 0/16, Fisher two-sided p = 3.33e-9). A third
label tests whether the premise effect is a property of *that pair* of routes or
of the model family more broadly, which is the remaining cross-label question.

## 1. Design (frozen)

- **Protocol:** the frozen P010 runner, imported byte-for-byte
  (`run_info_contract_2x2_chacha20.py`, SHA-256 `a08eab6f…83ee198`, asserted at
  launch), driven by a wrapper that changes **only**: output namespace, protocol
  label, seed list, Latin-square rotation modulo 4, and the provider transport
  (deviations D1–D2 below). Prompts, cell slots, fixture, oracle, policy,
  feedback strings, temperature provider-default, and turn flow are the frozen
  module's own code.
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−), identical slots to
  P010/P010P/P010L2, byte-identical prompts for the same seed.
- **Seeds:** 201–208. Verified unused on 2026-10-29 by scanning every
  `results.jsonl` under `sp2027/research_execution/**` for `seed ∈ [201,208]`
  (zero hits). Two balanced Latin squares (rotation index = seed index mod 4).
- **Sessions:** 4 cells × 8 seeds = 32 sessions; ≤2 turns; one provider call per
  turn; resume at seed granularity with earliest-row-per-(seed, cell) retained.
- **Model label:** `gpt-6-astra` on `https://agentrouter.org` via the
  Anthropic-compatible `/v1/messages` path.

## 2. Transport deviations (disclosed)

- **D1 — provider injection.** The AgentRouter adapter
  (`provider_adapter_agentrouter.py`, SHA-256 `d26dd920…aaa3dc`) is registered as
  `provider_adapter` in `sys.modules` before the frozen runner is imported; the
  frozen file is untouched and byte-asserted. The adapter is the same one used by
  P010L2; it sends `User-Agent: claude-cli/…`, without which the route returns
  401 "unauthorized client detected".
- **D2 — token floor.** The frozen runner requests 1400 output tokens; the adapter
  raises this to 2800 uniformly for every cell and records `max_tokens_sent`.
  A reasoning-family label that exhausts its budget mid-reasoning would truncate
  and correlate with cell; the floor removes that confound. This is the same
  deviation, at the same value, as P010L2.

## 3. Label-selection probe (NOT evidence)

Two smoke calls under the frozen adapter (2026-10-29, generic XOR task, no
fixture, no cell slots, not usable as evidence) established only transport
viability: both labels returned HTTP 200, `stop_reason=end_turn`, 267/275 output
tokens, 11.95/11.98 s. A follow-up identity probe with four random inputs
returned different outputs on 4/4 comparisons (0/4 identical), and repeating one
prompt returned a different output, so the labels are distinct backends and the
route does not serve cached completions. Those probes are transport diagnostics;
no session from them enters this cohort.

## 4. Estimand and falsifiers (unchanged from P010/P010L2)

- **Primary:** the A-premise marginal over cells C1+C4 versus C2+C3, by exact
  Fisher test on accepted sessions; reported per cell (4 arms × 8 seeds) and as
  the premise marginal (16 vs 16 slots).
- **F1 (mechanism):** the premise marginal is not a chance split at α = 0.05.
- **F2 (honest null):** if the marginal is saturated in both directions, the
  cohort reports a null and the mechanism claim does not extend to this label.
- **Not claimed:** a capability rate; cross-label pooling with pending/public
  production traffic; any comparison of vendors as quality measures.

## 5. Analysis plan

Per-cell accepted counts and turn structure; premise marginal; exact Fisher
two-sided and one-sided; per-seed paired view; comparison against P010 (n=4) and
P010L2 (n=8) as **descriptive only**, never pooled, with model mix and date
disclosed. Every failure retained; provider failures terminal, never retried.

## 6. Cost ceiling

≤ $1.00 at the provider's published rate for 32 sessions × ≤2 turns × ≤2800
output tokens. Measured cost is recorded in the report.
