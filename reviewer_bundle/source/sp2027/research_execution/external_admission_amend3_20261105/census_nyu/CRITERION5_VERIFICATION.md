# Criterion-5 verification — NYU CTF Bench crypto candidates (DRAFT 2026-11-05)

Pinned archive `nyu_ctf_bench__NYU_CTF_Bench__4c5744f55a31.tar.gz` (sha256 `ad376a2e1a33856fa3c0b4ac073d921b3337355bf966bd01dfb82a412d41f537`), complete census in `census_nyu/census_nyu_crypto.json`. This file records the pre-registered criterion-5 gate: an offline stdlib-only reference solve reproducing the pinned answer byte-exactly, admissible under the declared arm, with no pinned-answer bytes in the solver source, within the fixed 1600-token program budget.

**Quorum: 7 qualified ≥ 6 required — MET.**

| task | id | chars | est tokens | declared arm | disposition |
|---|---|---|---|---|---|
| eps | `2015q-cry-eps` | 936 | ≤234 | QUALIFIED | **QUALIFIED** |
| eps_part2 | `2015q-cry-eps_part2` | 1076 | ≤269 | QUALIFIED | **QUALIFIED** |
| almost_xor | `2017q-cry-almost_xor` | 3003 | ≤750 | QUALIFIED | **QUALIFIED** |
| another_xor | `2017q-cry-another_xor` | 2499 | ≤624 | QUALIFIED | **QUALIFIED** |
| babycrypto | `2018q-cry-babycrypto` | 1027 | ≤256 | QUALIFIED | **QUALIFIED** |
| lowe | `2018q-cry-lowe` | 2212 | ≤553 | QUALIFIED | **QUALIFIED** |
| Crack Me | `2021q-cry-crack_me` | 4036 | ≤1009 | QUALIFIED | **QUALIFIED** |
| DES 2 Bites | `2019q-cry-des2bites` | 8191 | ≤2047 | QUALIFIED | verified, budget-excluded |
| stfu | `2013f-cry-stfu` | — | — | — | FAIL_CRITERION_5 |
| collusion | `2018q-cry-collusion` | — | — | — | FAIL_CRITERION_5 |
| CSAWpad | `2013q-cry-csawpad` | — | — | — | not reached |
| onlythisprogram | `2013q-cry-onlythisprogram` | — | — | — | not reached |
| bricks_of_gold | `2015q-cry-bricks_of_gold` | — | — | — | not reached |
| Killer cipher | `2016f-cry-killer_cipher` | — | — | — | not reached |
| ECXOR | `2017f-cry-ecxor` | — | — | — | not reached |
| M@sTEr 0F PrN9 | `2022f-cry-m_ster_0f_prn9` | — | — | — | not reached |

## Reasons

- **DES 2 Bites** — the reference solve reproduces the pinned answer byte-exactly under the declared arm, but the pure-stdlib DES implementation it needs is 8191 source chars (~2047+ tokens at a conservative 4 chars/token), above the registered 1600-token program budget; excluded conservatively from grid membership
- **stfu** — the decoded artifact (LFSR keystream reproduced from the release header) is a 25,300-byte printable visual rendering of the answer; reading it requires a human viewer, and no admissible programmatic derivation was found within the registered budget
- **collusion** — the declared artifacts' message body is a 31-byte GCM payload (15-byte plaintext; the release's generator encrypts the literal 'mission payload'), while the pinned answer is a 48-byte string — the answer cannot be the decrypted message, and no derivation rule from the declared files produces it (recorded as a selection outcome, not a claim about the benchmark)

Not reached (6): CSAWpad, onlythisprogram, bricks_of_gold, Killer cipher, ECXOR, M@sTEr 0F PrN9 — not reached: the pre-registered verification schedule stopped once the quorum was exceeded; no eligibility claim is made.

Boundary: This record is a task-selection artifact. It makes no claim about the quality of any benchmark; every non-qualifying disposition is a statement about our contract's ability to derive the pinned answer from the declared handout files within the registered budget.
