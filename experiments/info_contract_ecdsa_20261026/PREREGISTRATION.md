# PREREGISTRATION — P012: information-contract 2×2 on a SECOND FIXTURE (ECDSA nonce reuse)

**Namespace:** `sp2027/research_execution/info_contract_ecdsa_20261026/`
**Date:** 2026-10-26 · Written before any provider call under this protocol
(the only call made so far is the 16-token AUTH_SMOKE health probe, logged
`HEALTH.json`, `evidence: false`).

**Motivation.** External review (S&P weak-reject round): "the premise result
is on one fixture (ChaCha20) and RC4 came out null. Is this a finding about
prompts or about ChaCha20 specifically?" This cohort transports the
information-contract 2×2 to a SECOND fixture family — ECDSA nonce reuse over
secp256k1 — while holding model label, cells, budget, policy, feedback, turn
flow, and analysis identical to the frozen P010 protocol. The load-bearing
premise slot is structurally analogous: in ChaCha20 the premise is "c2
encrypts an all-zero reference"; in ECDSA it is "the same ephemeral nonce k
was used for both signatures". RC4 stays recorded as the hash-frozen honest
null (saturated in the stated arm, 4/4 withheld — no discrimination) and is
not re-run.

## 1. Design (frozen)

- **Protocol:** `run_info_contract_2x2_ecdsa.py` (P012), SHA-256
  `8e67d904a08409d1489219bb4043a86259810340b87a86e449c3be2660ff60f0`,
  asserted at launch by the wrapper. Methodology copied from the frozen P010
  module: `extract_action`, `policy_check`, Latin-square rotations, max 2
  turns, max_tokens=1400, temperature provider-default, execution sandbox
  (`-I`, empty env, 20 s timeout), event log, summary schema. The ONLY
  changes vs P010 are fixture-specific and disclosed: `instance()`
  (deterministic secp256k1 ECDSA, stdlib hashlib only, two signatures under
  one private key with the same ephemeral k), `oracle()` (accepts
  `privkey_hex`), the A/B slot sentences and MIDDLE text naming the ECDSA
  family/target and restricting allowed imports to json, sys, hashlib, and
  the turn-2 feedback sentence saying "verifier-held secret" instead of
  "verifier-held plaintext".
- **Fixture self-test (completed before this file):** on seeds 141–156 the
  fixture is deterministic (16/16), the textbook nonce-reuse algebra
  (k = (z1−z2)·(s1−s2)⁻¹, d = (s1·k − z1)·r⁻¹ mod n) recovers the key and
  the oracle accepts it (16/16), the oracle rejects wrong/garbage keys
  (16/16), and the public key point is consistent with d·G (16/16).
  `extract_action` + `policy_check` accept a reference-style program.
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−) — same 2×2.
- **Seeds:** 141–156 (16 fresh seeds; verified unused as seed lists across
  the P010-family preregs — 41–44, 81–84, 101–118, 121–136 — and all other
  run namespaces' seed declarations). Four balanced Latin squares
  (rotation index = seed index mod 4).
- **Sessions:** 4 cells × 16 seeds = 64 sessions; ≤2 turns; one provider
  call per turn.
- **Model label:** `claude-sonnet-4-6-free` via `https://api.apmix.ai`
  (the primary label of P010/P010P/P010N16; route attested in
  `HEALTH.json`). Holding the model label fixed is the point of this
  cohort: only the fixture varies.

## 2. Primary and secondary analyses (frozen before any call)

- **Primary:** paired C1-vs-C4 discordance on the 16 shared seeds, exact
  binomial two-sided, reported with the full discordance count.
- **Secondary (all descriptive, prespecified):** per-cell acceptance with
  submissions/turns; premise marginal (C1+C3 vs C2+C4) and naming marginal
  (C1+C4 vs C2+C3), Fisher exact one- and two-sided; seed-stratified
  Cochran–Mantel–Haenszel on the premise contrast (post hoc, as in P010N16);
  submissions cost of C2 vs C1.
- **Cross-fixture view (prespecified, descriptive only):** side-by-side
  table against the ChaCha20 cohorts (P010 n=4, P010P n=8, P010L2 n=8,
  P010N16 n=16) and the RC4 honest null. No pooled rate across fixtures;
  any cross-fixture count is labeled descriptive, mirroring the
  cross-cohort discipline of prior preregs.
- **Falsifiers (prespecified):**
  - F1 (stated-arm ceiling): C1 below 12/16 means the fixture does not
    reproduce stated-arm determinism; the cohort is then reported as an
    instrument-difficulty result, not a premise result.
  - F2 (naming gates): C3 materially below C1.
  - F3 (derive frame): C2 near C1 — success without the premise.

## 3. Discipline

AUTH_SMOKE health probe (16 tokens, non-evidence) precedes the first
experiment call and is logged in `HEALTH.json`. Provider failures are
terminal per session, never retried; consecutive provider failures halt the
launch. Cost ceiling $5 estimated (prior 64-session cohort cost $0.39 on
this route; ECDSA prompts are the same size class). Every call's
tokens/cost appended to `sp2027/research_execution/BUDGET_LEDGER.jsonl`.
Git: freeze commit before the first experiment call. Never pooled with any
prior cohort except the prespecified cross-fixture descriptive table above.
Leak scan over all prompt files before analysis: the per-seed private keys
(the fixture truth) must appear in zero prompts.
