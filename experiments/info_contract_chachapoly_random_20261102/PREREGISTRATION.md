# PREREGISTRATION — P019: ChaCha20-Poly1305 (TLS 1.3 AEAD) on CSPRNG instances

**Namespace:** `sp2027/research_execution/info_contract_chachapoly_random_20261102/`
**Date:** 2026-11-02 · Written before any provider call under this protocol.
**Status:** registered; harness, fixture module, adapter and seed receipt pinned.

## 1. Why this fixture

The frozen campaign grid tests **raw ChaCha20** (no Poly1305) — not the AEAD that TLS 1.3
actually deploys. A reviewer can therefore say the suite contains no modern *construction*,
only a modern primitive and the catastrophic AES-GCM case. ChaCha20-Poly1305 (RFC 8439) is
the second TLS 1.3 AEAD, and its nonce reuse is structurally the same break: the ChaCha20
keystream **and** the Poly1305 one-time key are reused.

The reference attack therefore transfers unchanged: ciphertext XOR recovers plaintext XOR;
the premise-stated reference record yields the keystream; XOR against c1 recovers the
secret. This is a mechanism replication on a second deployed AEAD, not a new claim.

## 2. Fixture (offline selftest evidence, before any call)

`fixtures_aead_modern.py`, SHA pinned. `selftest_modern_aead.py` reports:

| check | result |
|---|---|
| deterministic instance per (family, seed) | 8/8 |
| nonce reuse exposes keystream | 8/8 |
| reference attack accepted via the real sandbox | 8/8 |
| oracle rejects garbage / truncation | 5/5 |
| no secret or record content in public JSON | 0 leaks |

Public JSON shape is identical to P014 (80-byte ciphertext = 64 + 16 tag, 96-bit nonce), so
cell semantics and difficulty are comparable across fixtures.

## 3. Design

- **Fixture:** `chacha20poly1305`. **Harness:** `run_modern_aead_cohort.py` (self-hash
  pinned; sandbox, event schema, status taxonomy and oracle pattern identical to the
  AES-GCM runner).
- **Seeds:** 24 CSPRNG values, `seeds_random_20261102T105650Z.json`,
  `seeds_sha256 = 99f78675…`, drawn after the P018 draw and disjoint from it by construction.
  No re-draw, no reorder, no substitution after the first call.
- **Sessions:** 4 × 24 = 96. **Label:** `gpt-6-astra`. **Floor:** 4200 via the pinned
  P017 adapter.
- **Scheduling:** after P018 exits (one key, one cohort at a time).
- **Provider failures:** terminal per session, never retried, never imputed.

## 4. Analysis plan (frozen before any call)

- **Primary:** paired C1-vs-C4 discordance on instances evaluable in both cells, exact
  binomial two-sided; *direction replicated* iff b10 > b01 and p < 0.05.
- **Secondary:** per-cell accepted/evaluable with Wilson 95% CIs; premise marginal Fisher
  two-sided; drops by cell disclosed.
- **Cross-fixture comparison (descriptive only):** direction and magnitude against P014
  (AES-GCM, same label, same cells). No pooled rate: the fixtures differ by construction,
  which is the point of the comparison.
- **Falsifiers:** no evaluable C4 sessions (paired test undefined); b01 ≥ b10 (no
  replication).

## 5. What this does not establish

No claim that AEAD misuse is exploitable "in general": exactly one misuse class (nonce
reuse) and one mode pair are tested. No provider or model-family claim.
