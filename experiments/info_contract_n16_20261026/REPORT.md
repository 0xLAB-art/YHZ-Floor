# REPORT — P010N16: per-cell n=16 increase of the information-contract 2×2

**Namespace:** `info_contract_n16_20261026/` · **Protocol:** P010N16-INFO-CONTRACT-2X2-CHACHA20-N16-v1 · 2026-10-26
**Status: COMPLETED — 64/64 sessions, 88 provider responses, 0 provider failures, 0 instrument duplicates, est $0.3894**
**Motivation:** `REVISION_NOTES_20261026.md` §"Still open" item 1 — the information-contract headline rested on 5 and 8 discordant pairs; this cohort doubles per-cell n on the primary label. Item 2 (open-weight cohort) **declined by decision**: this project has never executed a local/open-weight model; every cohort in its record ran an API route.

## 1. Results (per-cell n=16, seeds 121–136, frozen runner byte-identical)

| Cell | A | B | Accepted | Submissions |
|---|---|---|---|---|
| C1 | named | premise stated | **16/16** (all first-turn) | 16 |
| C2 | withheld | premise unstated | **3/16** | 29 (13 reached turn 2) |
| C3 | withheld | premise stated | **16/16** (all first-turn) | 16 |
| C4 | named | premise unstated | **6/16** | 27 (10 reached turn 2) |

- **Primary (preregistered): paired C1-vs-C4 discordance on the 16 shared seeds = 10, ALL C1 wins (10/0), exact binomial two-sided p = 0.001953.** The registered paired test now clears conventional significance with room to spare (the n=8 floor was p=0.0625; the observed 5/0 at n=8 became 10/0 at n=16, with 6 ties).
- Premise marginal: B+ (C1+C3) **32/32** vs B− (C2+C4) **9/32** — Fisher exact two-sided p = 3.82e-10.
- Naming marginal: A+ 22/32 vs A− 19/32 — Fisher exact two-sided p = 0.603 (inert).
- **F1 FALSE** (discordance 10, all one-way, > 4): the honest null does not replicate at n=16.
- **F2 FALSE** (C3 16/16 = C1): naming never gates when the premise is stated — 4th cohort.
- **F3 FALSE** (C2 3/16 far below C1 16/16): the derive-from-observations frame does not sustain success.

## 2. Cross-cohort descriptive view (prespecified; never pooled as a rate)

| Cell | P010 (n=4) | P010P (n=8) | P010L2 label2 (n=8) | drift-check (n=4, post-hoc) | **P010N16 (n=16)** |
|---|---|---|---|---|---|
| C1 stated | 4/4 | 8/8 | 8/8 | 4/4 | **16/16** |
| C2 withheld | 4/4 | 0/8 | 0/8 | 2/4 | **3/16** |
| C3 stated | 4/4 | 8/8 | 8/8 | 4/4 | **16/16** |
| C4 withheld | 0/4 | 3/8 | 0/8 | 2/4 | **6/16** |

Combined sonnet-line ChaCha20 (P010+P010P+P010N16, descriptive only): premise stated 28/28 vs unstated 18/40. The stated-premise arm is deterministic across every cohort and both labels (48/48); the unstated-premise arm is where all instability lives (18/40), consistent with the drift-check's localization.

## 3. Reading (bounded)

- **The registered primary now has real resolution and clears it**: 10/0 discordance, p=0.001953 — the exact paired test's floor at this size is p≈3.05e-5, so the result is no longer a small-n artifact.
- **The premise is load-bearing at n=16**: 32/32 vs 9/32 on the primary label; the naming slot remains inert (p=0.60), replicating F2's null for the fourth cohort running.
- **C2/C4 degree movement is real but bounded**: C4 moved 0/4 → 3/8 → 6/16 across sonnet cohorts and C2 4/4 → 0/8 → 3/16 — the withheld arm shifts with seeds/time while staying far below the stated arm; this is exactly the instability the drift-check localized, and it never touches C1/C3.
- One model label (provider exposes exactly one — attested), single experimenter, synthetic fixture, never pooled except the prespecified descriptive table; mechanism identification, not capability rates.

## 4. Integrity

Freeze `b1266972` BEFORE any experiment call (AUTH_SMOKE 13 in/4 out, attest 200, evidence=false). Frozen runner SHA-256 `a08eab6f…83ee198` asserted at launch. Leak scan PASS: 64 prompt files, 0 truth hits (`LEAK_SCAN.json`). Ledger: aggregate line appended (88 calls, 29,374/20,083 tokens, est $0.3894 of $5 ceiling). 0 provider failures, 0 terminal truncations, 0 instrument duplicates. Artifacts: `results.jsonl`, `events.jsonl`, `prompts/`, `raw_provider_responses/`, `execution_captures/`, `analysis.json`, `summary.json`, `run_info.json` — frozen in place.

## 5. What this changes in the paper (for integration, not yet applied)

The §5/abstract paired-test sentence can now cite n=16 with p=0.001953 instead of resting on the n=8 p=0.0625 floor; the premise marginal becomes 32/32 vs 9/32 (primary label) alongside the existing 24/24 vs 7/24 line; S30 gains this cohort as a fifth row. All prior registered numbers stand unchanged; this is an additive cohort, disclosed as such.
