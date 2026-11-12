# REPORT — P012: information-contract 2×2 on a SECOND FIXTURE (ECDSA nonce reuse) — observability control

**Namespace:** `info_contract_ecdsa_20261026/` · **Protocol:** P012-INFO-CONTRACT-2X2-ECDSA-NONCE-REUSE-v1 · 2026-10-26
**Status: COMPLETED — 64/64 sessions, 75 session-turns (77 raw responses incl. resume duplicates), 0 provider failures, 2 instrument duplicates (seed 141 C1/C2, earliest-row rule), leak scan PASS, est $0.5859**
**Motivation:** external review (S&P weak-reject round): "the premise result is on one fixture (ChaCha20) and RC4 came out null. Is this a finding about prompts or about ChaCha20 specifically?" P012 transports the 2×2 to a second family whose analogous premise is **redundantly observable** in the public data — it is the **observability control** of the cross-fixture program (P013 restores the hidden premise on AES-CTR; RC4 remains the saturated honest null).

## 1. Results (per-cell n=16, seeds 141–156, frozen runner sha-asserted)

| Cell | A | B | Accepted | Submissions | Turns |
|---|---|---|---|---|---|
| C1 | named | premise stated | **16/16** | 16 | 19 |
| C2 | withheld | premise unstated | **16/16** | 16 | 18 |
| C3 | withheld | premise stated | **16/16** | 16 | 19 |
| C4 | named | premise unstated | **16/16** | 16 | 19 |

- **Primary (preregistered): paired C1-vs-C4 discordance = 0 (0/0), exact binomial two-sided p = 1.0.**
- Premise marginal: B+ (C1+C3) 32/32 vs B− (C2+C4) **32/32** — Fisher exact two-sided p = 1.0.
- Naming marginal: A+ 32/32 vs A− 32/32 — Fisher exact two-sided p = 1.0.
- Seed-stratified CMH on the premise contrast: degenerate (zero variance; every stratum at ceiling).
- **F1 FALSE** (C1 at 16/16 ≥ 12: the fixture reproduces stated-arm determinism — the instrument works on this family).
- **F2 FALSE** (C3 = C1: naming never gates when the premise is stated — 5th cohort running, both families, both vendors).
- **F3 TRUE** (C2 = 16/16 ≈ C1: success without the premise sentence) — **the preregistered predicted outcome on this fixture.**

## 2. Reading (bounded)

This is the **predicted structural null, not a refutation of the premise share.** The ECDSA nonce-reuse premise ("the same ephemeral nonce k was used for both signatures") is redundantly encoded in the public observations themselves: r₁ = r₂ is the textbook signature of the condition, and the fixture additionally carries a public `nonce_reuse` flag. Withholding the sentence therefore removes nothing the agent cannot read off the data — so a null premise effect here is what the observability account predicts *by construction*, exactly as the preregistration stated before any call.

The result does real work for the paper: it **brackets the claim.** The premise share is not a generic property of "stating attack facts"; it appears precisely when the load-bearing premise is a fact about **secret content** that semantic security makes unobservable (ChaCha20's all-zero reference; AES-CTR's premise-stated record — P013). When the same fact is observable, the withheld arm recovers it and the contract costs nothing (16/16 here; RC4's saturation is the other limiting case). A reviewer asking "prompts or ChaCha20?" now gets a three-fixture answer along a prespecified observability axis, not a single-fixture anecdote.

Bounded as always: one model label, one experimenter, synthetic fixture, provider-attested (not digest-pinned) route; mechanism identification, not capability rates; never pooled with other cohorts except the prespecified descriptive table.

## 3. Integrity

Freeze `3af87647` (runner + prereg + wrapper + smokes + scanner) BEFORE any experiment call; AUTH_SMOKE health probe passed first (attest 200, evidence=false). Frozen runner SHA-256 `8e67d904…0ff60f0` asserted at launch by the wrapper. Leak scan PASS: 78 prompt files, 0 truth hits (`LEAK_SCAN.json`). Ledger: entries appended (77 calls, 32,851/32,488 tokens, est $0.5859 of $5 ceiling). 0 provider failures, 0 terminal truncations. Instrument duplicates (seed 141 C1/C2 from the disclosed resume rule) recorded, never deleted; earliest-row rule applied in `analysis.json`. Artifacts: `results.jsonl`, `events.jsonl`, `prompts/`, `raw_provider_responses/`, `execution_captures/`, `analysis.json`, `summary.json`, `run_info.json`, `HEALTH.json`, `FREEZE.json` — frozen in place.

## 4. What this changes in the paper (for integration, not yet applied)

The cross-fixture table (S30) gains an ECDSA row: all cells 16/16, premise effect 0 by observability. The §5/§10 premise claim gains its boundary condition: the contract matters iff the premise is unobservable, and an observability control now demonstrates the null on a second family rather than leaving it implied. F2's "naming never gates" null replicates on a second family for the first time.
