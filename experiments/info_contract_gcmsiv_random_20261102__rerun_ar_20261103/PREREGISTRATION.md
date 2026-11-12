# PREREGISTRATION — P020: AES-GCM-SIV negative control (misuse-resistant AEAD)

**Namespace:** `sp2027/research_execution/info_contract_gcmsiv_random_20261102/`
**Date:** 2026-11-02 · Written before any provider call under this protocol.
**Status:** registered; harness, fixture module, adapter and seed receipt pinned.

## 1. Why a negative control

P014/P016/P018/P019 all use nonce-reuse breaks that expose a keystream. A reviewer can
therefore say the suite only measures "the model can find a keystream when the mode leaks
one", and that the information-contract result says nothing about modern constructions
that are *designed* against misuse.

AES-GCM-SIV (RFC 8452) is exactly such a construction. Its synthetic IV is derived from the
plaintext, so two different plaintexts under the same key **and the same nonce** use
different counter blocks. Nonce reuse leaks equality of plaintexts and nothing else; there
is no keystream to recover.

## 2. Fixture (offline selftest evidence, before any call)

`fixtures_aead_modern.py`, SHA pinned. `selftest_modern_aead.py` reports:

| check | result |
|---|---|
| deterministic instance per (family, seed) | 8/8 |
| nonce reuse exposes keystream | **0/8** (as designed) |
| P014 reference attack accepted via the real sandbox | **0/8** (as designed) |
| same plaintext → same ciphertext under reuse | true |
| oracle rejects garbage | 5/5 |
| no secret in public JSON | 0 leaks |

The prompt, public JSON shape, oracle and cell structure are identical to P014/P019. The
only difference is the cipher — which is the variable under control.

## 3. Design

- **Fixture:** `aesgcmsiv`. **Sessions:** 4 × 8 = 32. **Label:** `gpt-6-astra`.
  **Floor:** 4200 via the pinned P017 adapter.
- **Seeds:** 8 CSPRNG values, `seeds_random_p020_20261102T1057Z.json`,
  `seeds_sha256 = c660f63b…`, disjoint from the P018 and P019 draws.
- **Scheduling:** after P019 exits.
- **Provider failures:** terminal per session, never retried, never imputed.

## 4. Analysis plan (frozen before any call)

- **Primary (prespecified prediction):** **zero accepted sessions in every cell.** The task
  is cryptographically unsolvable by the attack the other cohorts reward; the oracle still
  accepts a correct plaintext, so acceptance is possible only if the model actually recovers
  the secret, which would mean the fixture is wrong.
- **Decision rule:** any acceptance ⇒ **fixture/defect flag**; the cohort is then reported as
  an instrument failure, not as a model result, and the affected instance is inspected
  before any claim is written.
- **Secondary:** per-cell submission and drop counts, with Wilson 95% CIs. A high submission
  rate with zero acceptances is the expected pattern (the model attempts and fails).
- No p-value is computed against the positive cohorts: the prediction is a fixed count, not
  a contrast.

## 5. What this does not establish

It does not show that models "cannot break misuse-resistant AEADs" in general — only that
this task, with this premise, has no keystream to exploit. It bounds the scope of the
positive cohorts: their result is mode-specific, not a general statement about modern crypto.
