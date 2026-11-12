# PREREGISTRATION — P014: information-contract 2×2 on a MODERN AEAD fixture (AES-GCM nonce reuse)

**Namespace:** `sp2027/research_execution/info_contract_aesgcm_20261102/`
**Date:** 2026-11-02 · Written before any provider call under this protocol.
**Status:** registered; no experiment call has been made. Runner SHA-256 recorded
in `_REGISTRATION.json` at this commit and asserted by the launch wrapper.

## Motivation

The audited testbed covered ChaCha20, AES-CTR, ECDSA and RC4: a stream cipher, a
block cipher in counter mode, a signature scheme, and a legacy stream cipher.
**No AEAD was covered**, so a reader can ask whether the premise share is a
property of *unauthenticated* constructions only — and every production record
layer a reader works on (TLS 1.3, QUIC) is AEAD. P014 closes that gap on AES-GCM,
where nonce reuse is a real, documented failure class rather than a synthetic
contrivance.

Structure preserved from the frozen design:

- the **reuse is observable** (same key and nonce, public `nonce_reuse` flag);
- the **load-bearing premise is secret content** — "c2 encrypts a 64-byte
  reference whose content is the 16-byte ASCII header `START_OF_RECORD:`
  followed by 48 spaces" — unobservable without performing the attack;
- therefore withholding the sentence must strand the agent exactly as in
  ChaCha20 and AES-CTR, and stating it must not.

Authentication tags are a fixture detail, not a barrier: GCM confidentiality
fails on nonce reuse, so the keystream recovered from the premise-stated record
decrypts c1 without touching either tag. This is stated in the B+ sentence so no
arm is asked to do something the public fields cannot support.

## 1. Design (frozen)

- **Protocol:** `run_info_contract_2x2_aesgcm.py` (P014), SHA-256 recorded in
  `_REGISTRATION.json`, asserted at launch. Methodology copied from the frozen
  P010 module: `extract_action`, `policy_check`, Latin-square rotations, ≤2
  turns, max_tokens=1400, temperature provider-default, sandbox (`-I`, empty
  env, 20 s timeout), event log, summary schema.
- **Fixture delta vs P013 (only these, all disclosed):** `instance()` uses
  `AESGCM` with a 96-bit nonce and 16-byte tag; c1 encrypts a seed-derived
  64-byte secret and c2 encrypts the FIXED 64-byte ASCII record under the same
  key and nonce; `public()` names AES-GCM and reports `record_length` and
  `tag_length`; `oracle()` accepts `plaintext1_hex`; slot sentences and MIDDLE
  name the AEAD family; allowed imports stay `json`, `sys`, `hashlib` (the
  winning move is XOR over the premise-stated record — no third-party crypto
  needed; `cryptography` is NOT in the agent's allowed-import list).
- **Cells:** C1 (A+ B+), C2 (A− B−), C3 (A− B+), C4 (A+ B−). B− withholds only
  the *content* of the reference, so the withheld arm still knows a reference
  exists.
- **Seeds:** 401–416 (16 fresh seeds; no overlap with any declared seed list —
  41–44, 81–84, 101–118, 121–136, 141–156, 161–176, 181–196, 201–208, 211–218,
  221–228, 301–332). Four balanced Latin squares (rotation = seed index mod 4).
- **Sessions:** 4 cells × 16 seeds = 64 sessions; ≤2 turns; one call per turn.
- **Model label:** pinned and recorded in `run_info.json` by the runner; the
  transport adapter and token floor are disclosed the same way P011 disclosed
  them (wrapper injection, frozen runner bytes untouched).
- **Fixture self-test before launch:** `selftest_aesgcm.py` must pass
  (deterministic public bytes, keystream structure c1⊕c2 = secret⊕record, the
  reference attack accepted through the same sandbox, oracle rejects
  wrong/truncated/garbage, no secret or record content in any public JSON, slot
  discipline). No provider call is made by the self-test.

## 2. Analysis plan (frozen before any call)

- **Primary:** paired C1-vs-C4 discordance on shared seeds, exact binomial
  two-sided, reported with the full discordance count and the evaluable-pair
  denominator (not the registered one).
- **Secondary (descriptive, prespecified):** per-cell acceptance with
  submissions/turns; premise marginal (C1+C3 vs C2+C3) and naming marginal
  (C1+C4 vs C2+C3), Fisher exact one- and two-sided; provider-dropout counts by
  cell, disclosed as a denominator effect.
- **Cross-fixture view:** descriptive table against ChaCha20 (P010 family),
  AES-CTR (P013), ECDSA (P012, observable-premise control), RC4 (saturated
  honest null). No pooled rate across fixtures.
- **Falsifiers (prespecified):**
  - **F1 (stated-arm ceiling):** C1 below 12/16 means the fixture does not
    reproduce stated-arm behaviour; the cohort is then reported as an
    instrument-difficulty result, not a premise result.
  - **F2 (naming gates):** C3 materially below C1.
  - **F3 (derive frame):** C2 near C1 — success without the premise; on a
    hidden-premise fixture this would mean the premise is not load-bearing here
    either, and is reported as a real negative.

## 3. Discipline

Provider failures are terminal per session, never retried, never imputed;
consecutive provider failures halt the launch. Expected cost ≤ $5 (prior
64-session cohorts cost $0.39–$0.43 on this route; GCM prompts are the same size
class). Every call's tokens/cost appended to
`sp2027/research_execution/BUDGET_LEDGER.jsonl`. Leak scan over all prompt files
before analysis: the per-seed secret and the record content must appear in zero
prompts other than the premise sentence of the stated arms. Never pooled with
any prior cohort except the prespecified descriptive cross-fixture table.
