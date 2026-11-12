# REPORT — P010X1: information-contract 2×2 on a SECOND VENDOR (gpt-oss:120b-cloud)

**Namespace:** `info_contract_x1_gptoss_20261026/` · **Protocol:** P010X1-INFO-CONTRACT-2X2-CHACHA20-GPTOSS120B-v1 · 2026-10-26
**Status: COMPLETED — 64/64 sessions, 93 session-turns (97 raw responses incl. resume duplicates), 0 provider failures, 3 instrument duplicates (seed 161 C1/C2/C3, earliest-row rule), leak scan PASS, $0 API cost (gateway free tier)**
**Motivation:** external review (S&P weak-reject round): every information-contract cohort ran one provider label (`claude-sonnet-4-6-free`), that label's withheld arm drifts across reruns, and declining a non-provider cohort "reads as if you avoided the test." P010X1 executes the identical frozen ChaCha20 2×2 on a model from a **different vendor** (OpenAI gpt-oss:120b served via the local Ollama gateway's cloud route). The open-weight/local-model attestation gap stays disclosed (never run locally; the tag is provider-attested, NOT digest-pinned).

## 1. Results (per-cell n=16, seeds 161–176, frozen P010 runner sha-asserted byte-for-byte)

| Cell | A | B | Accepted | Submissions | Turns |
|---|---|---|---|---|---|
| C1 | named | premise stated | **16/16** | 16 | 16 |
| C2 | withheld | premise unstated | **6/16** | 32 | 32 |
| C3 | withheld | premise stated | **16/16** | 16 | 16 |
| C4 | named | premise unstated | **6/16** | 28 | 29 |

(The runner's pre-dedup summary shows C2 7/16; the preregistered earliest-row rule counts seed 161's first C2 attempt — ORACLE_FAIL — and the resume's later success is recorded as an instrument duplicate, never deleted.)

- **Primary (preregistered): paired C1-vs-C4 discordance on the 16 shared seeds = 10, ALL C1 wins (10/0), exact binomial two-sided p = 0.001953** — the same primary statistic as the claude n=16 cohort (P010N16: 10/0, p = 0.001953), on a different vendor, different seeds, same frozen protocol and fixture.
- Premise marginal: B+ (C1+C3) **32/32** vs B− (C2+C4) **12/32** — Fisher exact two-sided p = 2.30e-08.
- Naming marginal: A+ 22/32 vs A− 22/32 — Fisher exact two-sided p = 1.0 (**inert on the second vendor too**).
- Seed-stratified CMH on the premise contrast: χ²_cc = 22.56, p = 2e-06.
- **F1 FALSE** (C1 16/16: stated-arm determinism transports to the second vendor).
- **F2 FALSE** (C3 = C1 16/16: naming never gates when the premise is stated — second family, second vendor).
- **F3 FALSE** (C2 6/16 far below C1: the derive-from-observations frame does not sustain success).

## 2. Reading (bounded)

**The premise share is a property of the contract, not of the vendor.** On the identical frozen ChaCha20 2×2, a model from a different vendor reproduces the primary discordance profile exactly (10 one-way discordant pairs, zero in the other direction), keeps the stated-premise arms deterministic (32/32), keeps naming inert (p = 1.0), and keeps the derive-frame collapse (6/16). Single-label drift on `claude-sonnet-4-6-free` cannot be the explanation for the premise share: the effect appears on a route that shares no weights, no serving stack, and no vendor with the primary label.

What *is* vendor-dependent is the **level** of the withheld arms (descriptive only, never pooled): claude's derive frame ran 4/4 → 0/8 → 3/16 across its cohorts; gpt-oss runs 6/16 here. That is consistent with the paper's localization claim — instability lives entirely in the withheld arms; the stated arms never move — and it is the strongest available rebuttal to "your withheld-arm numbers drift, so the whole result is drift."

Bounded as always: provider-attested tag (ATTESTED_METADATA_ONLY, not digest-pinned — disclosed), single experimenter, synthetic fixture, localhost execution; mechanism identification, not capability rates; never pooled across vendors except the prespecified descriptive table.

## 3. Integrity

Freeze `3af87647` (prereg + sha-asserted wrapper + smoke + scanner) BEFORE any experiment call; SMOKE health probe passed first (attest 200, evidence=false). Frozen P010 runner SHA-256 `a08eab6f…83ee198` asserted at launch; the wrapper changes only namespace, protocol label, seeds, rotation modulo 4, and — via environment variables the frozen adapter already reads — the endpoint/model tag. Leak scan PASS: 98 prompt files, 0 truth hits (`LEAK_SCAN.json`). Ledger: entries appended with pricing basis "ollama free-tier cloud route; $0 invoice claimed". 0 provider failures, 0 terminal truncations. Instrument duplicates (seed 161 from the disclosed resume rule) recorded, never deleted; earliest-row rule applied in `analysis.json`. Artifacts: `results.jsonl`, `events.jsonl`, `prompts/`, `raw_provider_responses/`, `execution_captures/`, `analysis.json`, `summary.json`, `run_info.json`, `HEALTH.json`, `FREEZE.json` — frozen in place.

## 4. What this changes in the paper (for integration, not yet applied)

The single-label drift objection loses its force: §5/S30 gain a cross-vendor row with the same primary (10/0, p = 0.001953) and the same falsifier verdicts (F1/F2/F3 all FALSE). §11 limits must state the attestation difference honestly (provider-attested tag, not digest-pinned; the local open-weight gap remains open by decision). The "capability number is a property of the contract" thesis extends across vendors: what is vendor-invariant is the premise share; what varies is the withheld-arm level.
