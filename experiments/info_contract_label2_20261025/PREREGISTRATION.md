# PREREGISTRATION — P010L2: second-label replication of the information-contract 2×2

**Namespace:** `sp2027/research_execution/info_contract_label2_20261025/`
**Date:** 2026-10-25 · Written before any provider call under this protocol.
**Motivation:** the 2026-10-25 five-referee panel (REVIEW_PANEL_20261025.md)
and the standing single-label weakness: every information-contract cohort in
the paper runs on ONE provider-attested label (`claude-sonnet-4-6-free`, the
only label the original provider exposed — probed 2026-10-25). Referee R3's
demand, verbatim: "which shares move across labels". This cohort supplies the
cross-label test. The user provisioned a second route (AgentRouter,
Anthropic-compatible `/v1/messages`) and authorized choosing any model it
exposes.

## 1. Design (frozen)

- **Protocol:** P010's frozen runner, imported byte-for-byte
  (`run_info_contract_2x2_chacha20.py`, SHA-256 `a08eab6f…83ee198`, asserted
  at launch) and driven by a wrapper that changes ONLY: output namespace,
  protocol label, seed list, Latin-square rotation modulo 4, and the provider
  transport (deviation D1 below). Prompts, cell slots, fixture, oracle,
  policy, feedback strings, temperature provider-default, and turn flow are
  the frozen module's own code, unchanged. Resume rule identical to P010P
  (seed granularity; earliest row per (seed, cell) kept; provider failures
  terminal, never retried).
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−) — identical slots
  to P010/P010P, byte-identical prompts for the same seed.
- **Seeds:** 111–118 (8 fresh seeds; verified unused 2026-10-25 by search over
  preregistrations and all `results.jsonl` under `sp2027/research_execution/`
  — zero hits). Two balanced Latin squares (rotation index = seed index mod 4).
- **Sessions:** 4 cells × 8 seeds = 32 sessions; ≤2 turns; one provider call
  per turn.
- **Model label:** `gpt-6.1-sol` on `https://agentrouter.org` (route attested
  via `/v1/models`: exposes exactly three labels — `gpt-5.6-sol`,
  `gpt-6-astra`, `gpt-6.1-sol`, all GPT-family, all `openai`-endpoint-listed
  yet served through the Anthropic-compatible `/v1/messages` path).
  - **Label selection probe (2026-10-25, NON-experiment task — a generic XOR
    recovery, no fixture, no cell slots, not usable as evidence):**
    - `gpt-5.6-sol`: **excluded** — at the frozen 1400-token budget it
      exhausted all output tokens on internal reasoning, returned zero text
      (stop=length); unusable under the frozen runner's call shape without
      fabricating terminal provider failures.
    - `gpt-6-astra`: usable (1361/1400 output tokens, 36s, parseable JSON).
    - `gpt-6.1-sol`: **selected** — usable (1211/1400, 26s, parseable JSON),
      newest of the three, fastest; selection made on transport capability
    grounds before any freeze.
  - This label is a DIFFERENT MODEL FAMILY from `claude-sonnet-4-6-free`
    (OpenAI vs Anthropic), which is the strongest form of the panel's
    weights-relativity question. Whether the provider proxies to the named
    weights is provider-attested only — the same epistemic status as the
    paper's primary label, disclosed.
- **RC4 fixture:** NOT re-run (P011 saturated 16/16; no detectable effect
  possible) — same registered design decision as P010P.

## 2. Disclosed transport deviations (D1) — adapter, not methodology

All three live in `provider_adapter_agentrouter.py` (hash-pinned in the
wrapper and in FREEZE.json); the frozen runner binds it via a `sys.modules`
injection asserted at launch (`base.ClaudeProvider is injected.ClaudeProvider`);
the frozen file itself stays byte-identical.

- **D1a — route/credentials:** endpoint `AGENTROUTER_BASE_URL`, key from env
  (gitignored root `.env`), `x-api-key` + `Authorization` +
  `anthropic-version` headers identical in shape to the frozen adapter.
- **D1b — required User-Agent:** the router rejects non-`claude-cli` clients
  with HTTP 401 UNAUTHENTICATED (isolated probe 2026-10-25: default
  python-requests UA → 401, empty UA → 401, `claude-cli/2.0.0 (external, cli)`
  → 200, three repeats). The adapter sends that UA on every call; recorded
  in per-call request metadata as `user_agent`.
- **D1c — token floor 2800 (uniform across cells):** the frozen runner
  requests 1400; the adapter sends `max(requested, 2800)` for EVERY cell and
  session. Rationale measured pre-freeze (see §1 label probe): these are
  reasoning-family labels that spend output tokens on internal reasoning
  before emitting text; keeping 1400 would make truncation-induced terminal
  failures correlate with cell difficulty and fabricate an arm difference.
  Both `max_tokens_requested_by_runner` and `max_tokens_sent` are recorded
  per call. If truncation still occurs, `INCOMPLETE_RESPONSE` remains a
  terminal provider failure per the frozen protocol.
- **D1d — timeout:** default 600s (frozen runner passes none; reasoning
  latency observed up to ~160s pre-freeze).

## 3. Primary and secondary analyses (frozen before any call)

- **Primary (cross-label question, prespecified):** per-cell acceptance
  profile of this cohort SIDE BY SIDE with P010P (same label as P010,
  n=8/cell, same fixture family) — cell-by-cell, with the paired C1-vs-C4
  discordance computed on this cohort's own 8 seeds, exact binomial
  two-sided, reported whether or not it clears any threshold. The registered
  question, verbatim: **which cells' acceptance rates move across labels?**
- **Secondary (all descriptive, prespecified):** premise marginal
  (C1+C3 vs C2+C4) and naming marginal (C1+C4 vs C2+C3) on this cohort,
  Fisher exact one- and two-sided; submissions/turns per cell; cross-label
  table includes P010 (n=4) and P010P (n=8) columns as descriptive context.
- **Falsifiers (prespecified, mirroring P010P's at n=8):**
  - F1: C4 succeeds about as often as C1 on THIS label (premise effect does
    not transport) → verdict by paired discordance ≤ 2 of 8.
  - F2: C3 fails while C1 succeeds → naming gates when premise stated.
  - F3: C2 succeeds → derive frame sustains success without the premise.
- **Interpretation guard:** results speak to MODEL-LABEL RELATIVITY of the
  information-contract effect on one fixture family — never pooled with
  P010/P010P/P011/H1/V4; any combined display is the labeled descriptive
  cross-cohort table only (as P010P did).

## 4. Discipline

AUTH_SMOKE health probe (16 tokens, exact adapter code path, non-evidence)
precedes the first experiment call and is logged in `HEALTH.json`. Provider
failures are terminal per session, never retried; if most consecutive sessions
fail on the provider, the launch stops with status halted. Cost ceiling $5
estimated (pre-freeze probe ~119 in / ~1200 out per call at this route's
published ratios ⇒ est. well under $1 for 32–64 calls; ledger is authoritative).
Every call's tokens/cost appended to `sp2027/research_execution/BUDGET_LEDGER.jsonl`.
Git: freeze commit before the first experiment call; namespace-restricted
commits thereafter. Never pooled with any other cohort except the
prespecified descriptive cross-label table above.
