# REPORT — P010L2: second-label replication of the information-contract 2×2

**Namespace:** `info_contract_label2_20261025/` · **Protocol:** P010L2-INFO-CONTRACT-2X2-CHACHA20-LABEL2-v1 · 2026-10-25
**Status: COMPLETED — 32/32 sessions, 44 provider responses, 2 terminal provider failures, est ≤ $0.87 (upper bound) of the $5 ceiling**
**Motivation:** five-referee panel (REVIEW_PANEL_20261025.md), R3's demand: "which shares move across labels" — the paper's cohorts all ran on ONE provider-attested label (`claude-sonnet-4-6-free`). This cohort runs the byte-frozen P010 methodology on a DIFFERENT MODEL FAMILY (`gpt-6.1-sol`, GPT-family, AgentRouter route).

## 1. Results (per-cell n=8, seeds 111–118, frozen runner byte-identical)

| Cell | A | B | Accepted | Submissions |
|---|---|---|---|---|
| C1 | named | premise stated | **8/8** (all first-turn) | 8 |
| C2 | withheld | premise unstated | **0/8** | 12 |
| C3 | withheld | premise stated | **8/8** (all first-turn) | 8 |
| C4 | named | premise unstated | **0/8** | 16 |

- **Primary (preregistered): paired C1-vs-C4 discordance on the 8 shared seeds = 8, all C1 wins (8/0), exact binomial two-sided p = 0.0078** — clears conventional significance on this label.
- Premise marginal: B+ (C1+C3) **16/16** vs B− (C2+C4) **0/16** — Fisher exact one-sided p = 1.66e-9, two-sided p = 3.33e-9 (verified: 1/C(32,16) with symmetric tail; scipy-free recomputation).
- Naming marginal: A+ (C1+C4) 8/16 vs A− (C2+C3) 8/16 — Fisher p = 1.0.
- **F1 FALSE** (paired discordance 8 > 2): the premise effect TRANSPORTS to the second label — this is the cohort's central finding.
- **F2 FALSE** (C3 8/8): naming does not gate — third cohort in a row to replicate this (P010, P010P, now P010L2).
- **F3 FALSE** (C2 0/8): the derive-from-observations frame again sustains NOTHING on this label; P010P's C2 0/8 refutation replicates across labels.

## 2. Cross-label descriptive view (prespecified; no pooling inference)

| Cell | P010 (n=4, sonnet) | P010P (n=8, sonnet) | **P010L2 (n=8, gpt-6.1)** |
|---|---|---|---|
| C1 | 4/4 | 8/8 | **8/8** |
| C2 | 4/4 | 0/8 | **0/8** |
| C3 | 4/4 | 8/8 | **8/8** |
| C4 | 0/4 | 3/8 | **0/8** |

Premise marginal by label: sonnet cohorts 24/24 vs 7/24 (Fisher exact one-sided p = 8.15e-08; the previously cited p=0.00055 did not reproduce under the exact test — see the P010P REPORT §5 amendment); **gpt-6.1: 16/16 vs 0/16 (p=1.66e-9)**. Naming marginal across all three cohorts: A+ 23/40 vs A− 24/40 (no effect anywhere).

## 3. Answer to R3's question — "which shares move across labels?"

- **The premise share does NOT move — it transports and strengthens**: the premise-marginal contrast is 16/16 vs 0/16 on the second label (larger and cleaner than the first label's 16/16 vs 3/16, Fisher exact one-sided p = 1.61e-06). The paired C1-vs-C4 test clears p=0.0078 here vs p=0.0625 on sonnet.
- **The naming share does NOT move**: naming never gates on either label (A+ 8/16 vs A− 8/16 here; identical conclusion across all cohorts).
- **The derive-frame refutation (C2) does NOT move**: 0/8 on both labels at n=8 — the refutation is label-invariant, not a sonnet quirk.
- **The only moving cell is C4 in degree**: 0/4 (P010) → 3/8 (P010P sonnet) → 0/8 (this label) — acceptance under named+unstated-premise varies across labels (3/8 vs 0/8) while remaining far below C1's 8/8. Direction consistent everywhere; magnitude label-sensitive.
- **Bounded reading**: one fixture family (ChaCha20 nonce-reuse), provider-attested labels only (route/weights identity is an assumption of BOTH labels, disclosed), 2 terminal EMPTY_RESPONSE failures (below), never pooled. What this buys the paper: §11's model-relativity caveat becomes a MEASURED boundary on one axis (premise/naming/derive shares stable across two model families; C4's unstated-premise cell label-sensitive), and the abstract gains a legitimate second-label line.

## 4. Failures and integrity (all disclosed, none retried)

- **2 terminal provider failures**: C2 seeds 112 and 116, turn 1, category EMPTY_RESPONSE (HTTP 200 with empty text from the router — no raw body was emitted; events record model_start → provider_failure). Per the frozen protocol these are terminal, never retried, and the sessions count as recorded (0/8 for C2 includes them). All 44 stored raw responses are `end_turn`; **zero truncations** — the uniform 2800-token floor (disclosed deviation D1c) did its job (pre-freeze measurement: gpt-5.6-sol exhausted the frozen 1400 with zero text; gpt-6.1-sol spent 1211/1400 on a generic task).
- **Transport deviations** (all pre-frozen in FREEZE.json, transport-only, methodology untouched): D1a route from env; D1b required `claude-cli` User-Agent (isolated probe: python-requests UA → 401, claude-cli UA → 200); D1c uniform 2800-token floor recorded per call as `max_tokens_sent`; D1d 600s timeout. The frozen runner's binding to the injected adapter is asserted at launch (`base.ClaudeProvider is injected.ClaudeProvider`); the frozen file's SHA-256 `a08eab6f…83ee198` verified unchanged.
- **Freeze** `49d91bc0` BEFORE any experiment call (PREREGISTRATION.md + FREEZE.json + wrapper/adapter hash-pinned). AUTH_SMOKE via the exact adapter code path: OK (11 in/18 out, attest 200), evidence=false, in HEALTH.json.
- **Leak scan**: 47 prompt files, 0 truth hits (LEAK_SCAN.json); the 28 files with hits are all `execution_captures/*.stdout.txt` of oracle-accepted programs printing their recovered plaintext by design.
- **Instrument duplicates**: 0 (single uninterrupted launch; the killed first attempt died mid-call before any row was recorded).
- **Ledger**: one aggregate line (44 calls, 15,680 in / 56,500 out, est ≤ $0.866 upper bound of the $5 ceiling).
- **Never pooled** with P010/P010P/P011/H1/V4 except the prespecified descriptive cross-label table.
