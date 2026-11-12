# PREREGISTRATION — P010X1: information-contract 2×2 on a SECOND VENDOR (gpt-oss:120b-cloud)

**Namespace:** `sp2027/research_execution/info_contract_x1_gptoss_20261026/`
**Date:** 2026-10-26 · Written before any provider call under this protocol
(the only call made so far is the 16-token SMOKE health probe, logged
`HEALTH.json`, `evidence: false`).

**Motivation.** External review (S&P weak-reject round): all information-
contract cohorts ran one provider label (`claude-sonnet-4-6-free`), the
withheld arm drifts across reruns on that label, and declining a non-provider
model cohort "reads as if you avoided the test". Per author decision
2026-10-26 the previously declined open-weight/local cohort is **still not
executed** (this project has never run a local model; that attestation gap
stays disclosed in §11 limits), and instead a SECOND-VENDOR cohort is
executed: the identical frozen ChaCha20 2×2 on a model from a different
vendor, served through the local Ollama gateway's cloud route. This
addresses vendor transport of the premise share; it does not close the
attestation gap (the model tag is provider-attested, not digest-pinned —
disclosed).

## 1. Design (frozen)

- **Protocol:** the FROZEN P010 runner imported byte-for-byte
  (`run_info_contract_2x2_chacha20.py`, SHA-256 `a08eab6f…83ee198`,
  asserted at launch) and driven by a wrapper that changes ONLY the output
  namespace, the protocol label, the seed list, the Latin-square rotation
  modulo 4, and — via environment variables only — the provider endpoint
  and model tag that the frozen module's own `provider_adapter.ClaudeProvider`
  already reads (`ACTS_PROVIDER_ENDPOINT`, `ACTS_PROVIDER_MODEL`,
  `ACTS_PROVIDER_API_KEY`). No methodology code changes: prompts, cell
  slots, fixture, oracle, policy, feedback strings, max_tokens=1400,
  temperature provider-default, and turn flow are the frozen module's own.
- **Model:** `gpt-oss:120b-cloud` via `http://127.0.0.1:11434/v1` (the
  local Ollama gateway's cloud route; free-tier plan — the route was probed
  for plan availability across all 12 served cloud tags before selection;
  kimi/glm/minimax/deepseek/qwen3.5 tags require a paid plan and were
  excluded). Provider-attested tag, NOT digest-pinned: disclosed limitation.
  Smoke probe route attested in `HEALTH.json`.
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−) — identical slots.
- **Seeds:** 161–176 (16 fresh seeds; verified unused as seed lists across
  the P010-family preregs — 41–44, 81–84, 101–118, 121–136 — and all other
  run namespaces' seed declarations). Four balanced Latin squares.
- **Sessions:** 4 cells × 16 seeds = 64 sessions; ≤2 turns; one provider
  call per turn.
- **Fixture:** ChaCha20 only, byte-identical to P010 (the fixture axis is
  held; only the vendor varies).

## 2. Primary and secondary analyses (frozen before any call)

- **Primary:** paired C1-vs-C4 discordance on the 16 shared seeds, exact
  binomial two-sided, reported with the full discordance count.
- **Secondary (all descriptive, prespecified):** per-cell acceptance with
  submissions/turns; premise marginal (C1+C3 vs C2+C4) and naming marginal
  (C1+C4 vs C2+C3), Fisher exact one- and two-sided; seed-stratified
  Cochran–Mantel–Haenszel on the premise contrast (post hoc, as in
  P010N16).
- **Cross-vendor view (prespecified, descriptive only):** side-by-side
  table against the same-label cohorts (P010, P010P, P010N16) and the
  second-prompt-label cohort (P010L2). No pooled rate across vendors.
- **Falsifiers (prespecified):**
  - F1 (stated-arm ceiling): C1 below 12/16 → the second vendor does not
    reproduce stated-arm determinism on this fixture; reported as such.
  - F2 (naming gates): C3 materially below C1.
  - F3 (derive frame): C2 near C1.

## 3. Discipline

SMOKE health probe (16 tokens, non-evidence) through the exact provider
code path precedes the first experiment call (`HEALTH.json`). Provider
failures (including free-plan rate/usage caps surfaced as HTTP 429/5xx
categories) are terminal per session, never retried; consecutive provider
failures halt the launch. The Ollama free plan has usage caps (the paid
plan advertises "no 5-hour or weekly caps"); a capped session is recorded
as its provider-failure category, exactly as any provider failure. Cost:
$0 marginal API cost (gateway free tier); wall-clock is the binding budget.
Every call's usage appended to `sp2027/research_execution/BUDGET_LEDGER.jsonl`
with pricing basis "ollama free-tier cloud route; $0 invoice claimed".
Git: freeze commit before the first experiment call. Never pooled with any
prior cohort except the prespecified cross-vendor descriptive table above.
Leak scan over all prompt files before analysis (ChaCha20 truths for seeds
161–176 must appear in zero prompts).
