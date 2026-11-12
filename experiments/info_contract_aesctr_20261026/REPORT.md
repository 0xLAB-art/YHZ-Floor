# REPORT — P013: information-contract 2×2 on a SECOND HIDDEN-PREMISE FIXTURE (AES-CTR keystream reuse)

**Namespace:** `info_contract_aesctr_20261026/` · **Protocol:** P013-INFO-CONTRACT-2X2-AESCTR-KEYSTREAM-REUSE-v1 · 2026-10-26
**Status: COMPLETED — 64/64 sessions, 96 session-turns, 0 provider failures, 0 instrument duplicates, leak scan PASS (incl. premise-token arm check), est $0.4113**
**Motivation:** external review (S&P weak-reject round): "the premise result is on one fixture (ChaCha20) and RC4 came out null. Is this a finding about prompts or about ChaCha20 specifically?" P013 restores the ChaCha20 *structure* — an observable reuse plus a load-bearing premise that is a **fact about secret content** — on a third family (AES-CTR keystream reuse). It is the confirmatory hidden-premise transport; P012 (ECDSA) is the observability control on the same axis.

## 1. Results (per-cell n=16, seeds 181–196, frozen runner sha-asserted)

| Cell | A | B | Accepted | Submissions | Turns |
|---|---|---|---|---|---|
| C1 | named | premise stated | **16/16** | 16 | 16 |
| C2 | withheld | premise unstated | **0/16** | 31 | 32 |
| C3 | withheld | premise stated | **16/16** | 16 | 16 |
| C4 | named | premise unstated | **0/16** | 27 | 32 |

- **Primary (preregistered): paired C1-vs-C4 discordance on the 16 shared seeds = 16, ALL C1 wins (16/0), exact binomial two-sided p = 3.052e-05** — no ties, no exceptions. (The exact paired test's floor at n=16 is p ≈ 3.05e-5, so this primary sits AT the resolution floor of the instrument: perfect one-way discordance.)
- Premise marginal: B+ (C1+C3) **32/32** vs B− (C2+C4) **0/32** — Fisher exact two-sided p = 1.09e-18.
- Naming marginal: A+ 16/32 vs A− 16/32 — Fisher exact two-sided p = 1.0 (**inert, third family running**).
- Seed-stratified CMH on the premise contrast: χ²_cc = 45.05, p < 1e-15.
- **F1 FALSE** (C1 16/16: stated-arm determinism reproduces on this fixture — the instrument works).
- **F2 FALSE** (C3 = C1 16/16: naming never gates when the premise is stated — second family, same verdict).
- **F3 FALSE** (C2 **0/16** far below C1: the derive-from-observations frame collapses completely; the hidden premise is *not* recoverable from the public observations).

## 2. Reading (bounded)

**The premise is perfectly load-bearing on a second hidden-premise family — and more cleanly than on ChaCha20.** The withheld arms land at 0/16 *even when the family is named* (C4), and the premise alone suffices regardless of naming (C3 = 16/16, all first-turn, one submission each). On ChaCha20 the derive frame recovers the all-zero reference on a minority of seeds (C2 3/16, C4 6/16 on the primary label), so the withheld arm is partially porous there; on AES-CTR the premise-stated record ("header + 48 spaces") is not guessable at all, and the withheld arm is exactly zero. The contract difference (stated vs unstated premise) is therefore not an artifact of one cipher's particular reference choice: it appears on any fixture whose load-bearing premise is unobservable content, and its *magnitude* tracks how guessable that content is.

The three-fixture observability axis is now complete (descriptive, never pooled):

| Fixture | Premise kind | Withheld arms (C2 / C4) | Verdict |
|---|---|---|---|
| ChaCha20 (claude label, n=16) | hidden content (all-zero ref) | 3/16, 6/16 | premise share, derive frame porous |
| ChaCha20 (gpt-oss vendor, n=16) | hidden content | 6/16, 6/16 | premise share transports across vendors |
| **AES-CTR (claude label, n=16)** | **hidden content (stated record)** | **0/16, 0/16** | **premise perfectly load-bearing** |
| ECDSA (claude label, n=16) | observable (r₁ = r₂ + flag) | 16/16, 16/16 | null by construction (control) |
| RC4 (claude label, n=4) | saturated ceiling | 4/4, 4/4 | honest null (instrument cannot discriminate) |

A reviewer asking "prompts or ChaCha20?" now gets a falsifiable answer: **the contract effect tracks premise observability, not cipher identity** — it is maximal when the premise is unguessable secret content (AES-CTR 0/16), partial when that content is guessable (ChaCha20), and exactly zero when the premise is observable (ECDSA). Bounded as always: one model label (provider exposes exactly one — attested), single experimenter, synthetic fixtures, localhost execution; mechanism identification, not capability rates; never pooled except the prespecified descriptive table.

## 3. Integrity

Freeze `ce923c1a` (module + prereg + sha-asserted wrapper + auth smoke + leak scanner + self-test) BEFORE any experiment call; AUTH_SMOKE health probe passed first (attest 200, evidence=false). Frozen runner SHA-256 `6bdb25fc…8133f03` asserted at launch by the wrapper. Preflight self-test 16/16 (determinism, keystream-reuse structure, reference attack through the real sandbox, oracle rejections, action/policy, slot discipline). Leak scan PASS: 96 prompt files, 0 secret hits, premise token in exactly the 32 stated-arm prompts and **zero** withheld-arm prompts (`LEAK_SCAN.json`). Ledger: entries appended (96 calls, 33,725/20,672 tokens, est $0.4113 of $5 ceiling). 0 provider failures, 0 terminal truncations, 0 instrument duplicates. Artifacts: `results.jsonl`, `events.jsonl`, `prompts/`, `raw_provider_responses/`, `execution_captures/`, `analysis.json`, `summary.json`, `run_info.json`, `HEALTH.json`, `FREEZE.json` — frozen in place.

## 4. What this changes in the paper (for integration, not yet applied)

The §5/S30 premise claim gains its confirmatory transport: "one fixture" becomes "two hidden-premise families plus an observability control plus a cross-vendor replication." The headline paired test can cite the strongest single cohort (16/0, p = 3.05e-05) alongside the primary label's 10/0 (p = 0.001953). §10/§11 gain the observability-axis framing (the contract matters iff the premise is unobservable) and its boundary condition. F2's naming inert now replicates on a second family.
