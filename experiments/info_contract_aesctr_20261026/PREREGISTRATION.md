# PREREGISTRATION — P013: information-contract 2×2 on a SECOND HIDDEN-PREMISE FIXTURE (AES-CTR keystream reuse)

**Namespace:** `sp2027/research_execution/info_contract_aesctr_20261026/`
**Date:** 2026-10-26 · Written before any provider call under this protocol
(the only call made so far is the 16-token AUTH_SMOKE health probe, logged
`HEALTH.json`, `evidence: false`).

**Motivation.** External review (S&P weak-reject round): "the premise result
is on one fixture (ChaCha20) and RC4 came out null. Is this a finding about
prompts or about ChaCha20 specifically?" Two answers are being executed as
separate preregistered cohorts. P012 (ECDSA nonce reuse) transports the 2×2
to a second family, but its analogous premise ("the same ephemeral nonce k
was used for both signatures") is **redundantly observable in the public
data** (r₁ = r₂, plus a public `nonce_reuse` flag), so withholding the
premise sentence costs nothing *by construction*; P012 is therefore an
**observability control**, and a null premise effect there is the predicted
structural outcome, not a refutation. P013 — this cohort — restores the
ChaCha20 structure on a third family: **AES-CTR keystream reuse**. As in
ChaCha20, the *reuse* is observable (same key and counter, public
`nonce_reuse` field) while the *load-bearing premise is a fact about secret
content* — "c2 encrypts a 64-byte reference whose content is the 16-byte
ASCII header `START_OF_RECORD:` followed by 48 spaces" — which is
unobservable without performing the attack (semantic security). Withholding
that sentence should strand the agent exactly as in ChaCha20; if it does,
the premise share transports to a second secret-content family and the
"ChaCha20-specific" reading is falsified. RC4 stays recorded as the
hash-frozen honest null (saturated in the stated arm, 4/4 withheld — no
discrimination) and is not re-run.

## 1. Design (frozen)

- **Protocol:** `run_info_contract_2x2_aesctr.py` (P013), SHA-256
  `6bdb25fcf2b4af3672ebb4f33ff2d765366102f85978a6fd47d541d778133f03`,
  asserted at launch by the wrapper. Methodology copied from the frozen P010
  module: `extract_action`, `policy_check`, Latin-square rotations, max 2
  turns, max_tokens=1400, temperature provider-default, execution sandbox
  (`-I`, empty env, 20 s timeout), event log, summary schema. The ONLY
  changes vs P010 are fixture-specific and disclosed: `instance()`
  (AES-CTR keystream reuse via the `cryptography` library — the same
  library P010 allowed — with c2 encrypting a FIXED 64-byte ASCII record
  and c1 encrypting a seed-derived secret), `oracle()` (accepts
  `plaintext1_hex`), the A/B slot sentences and MIDDLE text naming the
  AES-CTR family/target, restricting allowed imports to json, sys, and
  hashlib (the winning move is XOR over the premise-stated record — no
  third-party crypto needed; `cryptography` is NOT in the allowed-import
  list for the agent, disclosed), and the claim-field/format sentence
  (`plaintext1_hex`, lowercase hex, no 0x — same convention P012 used for
  `privkey_hex`).
- **Fixture self-test (completed before this file, `selftest_aesctr.py`,
  seeds 181–196):** the fixture is deterministic (16/16); the keystream-
  reuse structure holds (c1 ⊕ c2 = secret ⊕ RECORD, 16/16); the reference
  attack — recover the keystream from the premise-stated record, XOR
  against c1 — executed through the SAME sandbox the runner uses
  (`python3 -I`, empty env, 20 s timeout) is accepted by the oracle
  (16/16); the oracle rejects wrong/truncated/garbage candidates (16/16);
  `extract_action` + `policy_check` accept a reference-style program (1/1);
  slot discipline holds (C1 states family + premise content, C2 neither,
  C3 premise content only, C4 family only), and no public JSON contains
  the secret or the record content (1/1).
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−) — same 2×2 as
  P010; B− withholds only the *content* of the reference ("c2 encrypts a
  64-byte reference"), mirroring P010's B− ("c2 encrypts a 64-byte
  reference"), so the withheld arm still knows a reference exists but not
  what it is.
- **Seeds:** 181–196 (16 fresh seeds; verified unused as seed lists across
  the P010-family preregs — 41–44, 81–84, 101–118, 121–136, 141–156,
  161–176 — and all other run namespaces' seed declarations). Four balanced
  Latin squares (rotation index = seed index mod 4).
- **Sessions:** 4 cells × 16 seeds = 64 sessions; ≤2 turns; one provider
  call per turn.
- **Model label:** `claude-sonnet-4-6-free` via `https://api.apmix.ai`
  (the primary label of P010/P010P/P010N16/P012; route attested in
  `HEALTH.json`). Holding the model label fixed is the point of this
  cohort: only the fixture varies, so any cell-pattern difference vs
  ChaCha20 is attributable to the fixture, not the label.

## 2. Primary and secondary analyses (frozen before any call)

- **Primary:** paired C1-vs-C4 discordance on the 16 shared seeds, exact
  binomial two-sided, reported with the full discordance count.
- **Secondary (all descriptive, prespecified):** per-cell acceptance with
  submissions/turns; premise marginal (C1+C3 vs C2+C4) and naming marginal
  (C1+C4 vs C2+C3), Fisher exact one- and two-sided; seed-stratified
  Cochran–Mantel–Haenszel on the premise contrast (post hoc, as in
  P010N16); submissions cost of C2 vs C1.
- **Cross-fixture view (prespecified, descriptive only):** side-by-side
  table against the ChaCha20 cohorts (P010 n=4, P010P n=8, P010L2 n=8,
  P010N16 n=16), the ECDSA observability control (P012), and the RC4
  honest null. No pooled rate across fixtures; any cross-fixture count is
  labeled descriptive, mirroring the cross-cohort discipline of prior
  preregs. The three fixtures span a prespecified premise-observability
  axis: hidden content premise (ChaCha20, AES-CTR) vs observable premise
  (ECDSA) vs saturated ceiling (RC4).
- **Falsifiers (prespecified):**
  - F1 (stated-arm ceiling): C1 below 12/16 means the fixture does not
    reproduce stated-arm determinism; the cohort is then reported as an
    instrument-difficulty result, not a premise result.
  - F2 (naming gates): C3 materially below C1.
  - F3 (derive frame): C2 near C1 — success without the premise; on a
    hidden-premise fixture this would mean the premise is NOT load-bearing
    here either (a real negative, reported as such).

## 3. Discipline

AUTH_SMOKE health probe (16 tokens, non-evidence) precedes the first
experiment call and is logged in `HEALTH.json`. Provider failures are
terminal per session, never retried; consecutive provider failures halt the
launch. Cost ceiling $5 estimated (prior 64-session cohorts cost $0.39–$0.43
on this route; AES-CTR prompts are the same size class). Every call's
tokens/cost appended to `sp2027/research_execution/BUDGET_LEDGER.jsonl`.
Git: freeze commit before the first experiment call. Never pooled with any
prior cohort except the prespecified cross-fixture descriptive table above.
Leak scan over all prompt files before analysis: the per-seed secrets (the
fixture truth) and the record content must appear in zero prompts other
than the premise sentence of the stated arms.
