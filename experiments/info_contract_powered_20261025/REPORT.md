# REPORT — P010P: powered same-label replication of the information-contract 2×2

**Namespace:** `info_contract_powered_20261025/` · **Protocol:** P010P-…-POWERED-v1 · 2026-10-25
**Status: COMPLETED — 32/32 sessions, 45 provider responses, 0 provider failures, est $0.2165**
**Motivation:** the five-referee panel's statistical requirement (powered test of the RQ2 interaction claim at n=4/cell).

## 1. Results (per-cell n=8, seeds 101–108, frozen runner byte-identical)

| Cell | A | B | Accepted | Submissions |
|---|---|---|---|---|
| C1 | named | premise stated | **8/8** (all first-turn) | 8 |
| C2 | withheld | premise unstated | **0/8** | 16 (all reached turn 2) |
| C3 | withheld | premise stated | **8/8** (all first-turn) | 8 |
| C4 | named | premise unstated | **3/8** (all first-turn) | 13 |

- **Primary (preregistered): paired C1-vs-C4 discordance on the 8 shared seeds = 5, all C1 wins (5/0), exact binomial two-sided p = 0.0625.**
- Premise marginal: B+ (C1+C3) **16/16** vs B− (C2+C4) **3/16** — Fisher exact one-sided p = 1.6121e-06, two-sided p = 3.2242e-06 (scipy-verified; see §5 amendment).
- Naming marginal: A+ 11/16 vs A− 8/16 (Fisher one-sided p = 0.2363, two-sided p = 0.4725).
- **F1 FALSE** (paired discordance 5 > 2): the honest null does NOT replicate — the premise effect replicates directionally at 5-0.
- **F2 FALSE** (C3 8/8): naming does not gate — replicates P010 and P011.
- **F3 FALSE** (C2 0/8): the derive-from-observations frame did NOT sustain success in this cohort — P010's C2 4/4 and P011's C2 4/4 do not replicate at n=8; all 8 C2 sessions consumed turn 2 and failed.

## 2. Cross-cohort descriptive view (preregistered secondary; no pooling inference)

| Cell | P010 (n=4) | P011/RC4 (n=4) | Powered (n=8) |
|---|---|---|---|
| C1 | 4/4 | 4/4 | 8/8 |
| C2 | 4/4 | 4/4 | **0/8** |
| C3 | 4/4 | 4/4 | 8/8 |
| C4 | **0/4** | 4/4 | **3/8** |

Combined ChaCha20 (P010 + powered, descriptive): C1 12/12, C2 4/12, C3 12/12, C4 3/12; premise marginal 24/24 vs 7/24.

## 3. Reading (bounded)

- **The premise is load-bearing, now at conventional significance**: across 24 ChaCha20 sessions with the premise stated, 24/24 succeed; with it unstated, 7/24. The powered cohort converts the P010 finding from a 4-vs-0 pattern into a marginal contrast (16/16 vs 3/16) that clears any conventional bar, with the paired C1-vs-C4 test at 5/0 (p=0.0625, direction entirely one-way).
- **The interaction claim is refined, not overthrown**: at n=8 BOTH unstated-premise cells degrade (C2 0/8 harder than C4 3/8), so the earlier C4-only conjunction gives way to the cleaner premise-marginal statement; naming shows no gate effect while the premise is stated (C3 8/8, 12/12 combined).
- **The derive frame is not a reliable route**: C2's 0/8 refutes the "derive-from-observations sustains success" reading (P010 4/4, P011 4/4 at n=4 were small-sample outcomes); failure analysis retained in execution captures (all 8 sessions reached turn 2 and failed there).
- One model label (provider exposes exactly one — probed); single experimenter; synthetic fixture; never pooled except the prespecified descriptive table; mechanism identification, not capability rates.

## 4. Integrity

Freeze `99f4b7b7` + hash refresh `dab8d706` (pre-first-call subdir fix) BEFORE any experiment call. Leak scan: 45 prompt files, 0 truth hits. Ledger: one aggregate line (45 calls, 15,126/11,411 tokens, est $0.2165). Incident recorded: an accidental wrapper import re-invoked the frozen runner's main() with an empty plan (resume guard held; zero provider calls) and clobbered summary.json/run_info.json; both were regenerated from results.jsonl/events.jsonl and the clobber note is embedded in both files. Falsifier verdicts and counts unaffected.

## 5. Amendment (2026-10-25, paper-integration audit)

Recomputed all marginal tests with the exact conditional test
(`scipy.stats.fisher_exact`, independently re-derived with `math.comb`) and
found two report-level statistics that did not reproduce; corrected above,
frozen rows (`results.jsonl`, `events.jsonl`) unchanged:

- Premise marginal (16/16 vs 3/16): the previously reported one-sided
  0.00055 / two-sided 0.0011 do not come from the standard exact test.
  Correct values: one-sided **1.6121e-06**, two-sided **3.2242e-06**.
  The frozen summary.json carries no p-values, so no artifact is affected.
- Naming marginal (11/16 vs 8/16): previously "p = 0.5" (and "one-sided
  p = 0.1695" in an earlier draft). Correct values: one-sided
  **0.236274**, two-sided **0.472548**. Neither version supported the
  inert-naming conclusion by itself; the conclusion rests on C3 8/8 under
  a stated premise, unchanged.
Verdicts F1/F2/F3, all cell counts, and the paired primary test (5/0,
p = 0.0625) are unaffected.
