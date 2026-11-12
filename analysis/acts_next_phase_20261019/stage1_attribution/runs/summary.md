# TOEEA-1 — Confirmatory results (recomputed from frozen raw results)

* Cases: **27** (frozen table: 27)
* Raw results: `runs/results.json` (schema `acts-next-phase/s1-results/1`)
* Computed by `s1_metrics.py` (post-hoc recomputation; no measurement)

## SET 1 — preregistered metric (`s1_protocol.md` §5), ground truth = `crypto_success`

Denominators: `crypto_success == true` **n=21**, `crypto_success == false` **n=6** (the protocol's illustrative 14/13 did not match the frozen manifest; the protocol fixes the *rule*, the manifest fixes the numbers).

* **digest_only** — FA 1/6 [0.030,0.564] · FR 7/21 [0.172,0.546] · CA 14/21 · CR 5/6
* **signed_digest_only** — FA 1/6 [0.030,0.564] · FR 9/21 [0.245,0.635] · CA 12/21 · CR 5/6
* **signed_context_only** — FA 1/6 [0.030,0.564] · FR 14/21 [0.454,0.828] · CA 7/21 · CR 5/6
* **full** — FA 0/6 [0.000,0.390] · FR 19/21 [0.711,0.973] · CA 2/21 · CR 6/6
* **full_lenient** — FA 0/6 [0.000,0.390] · FR 18/21 [0.654,0.950] · CA 3/21 · CR 6/6

### §5.1 caveat (material)

The preregistered `crypto_success` field records **whether the cryptographic predicate is true on the presented output**. For the C family the predicate is true by construction (the contradiction is *elsewhere*: the credited program was not the executed one, the output was not observed, the signature was tampered, and so on), while the correct decision for those cases is REJECT. The FR and CR columns above therefore count E3's **correct** rejections of the C family as 'false rejections'. SET 1 is reported because it is the preregistered metric; **SET 2 is the interpretable one** and is a post-hoc addition (deviation D-06).

## SET 2 — attribution ground truth (a bundle is a success iff the frozen
case table says its expected decision is `ATTRIBUTED_SUCCESS`)

Denominators: ground-truth success **n=2** (A01_ecdsa_correct, A02_chacha_correct), ground-truth non-success **n=25**.

| contract | false attribution | Wilson 95% | correct attribution | false rejection | Wilson 95% | correct rejection |
|---|---|---|---|---|---|---|
| `digest_only` | **13/25** | [0.335,0.700] | 2/2 | **0/2** | [0.000,0.658] | 12/25 |
| `signed_digest_only` | **11/25** | [0.267,0.629] | 2/2 | **0/2** | [0.000,0.658] | 14/25 |
| `signed_context_only` | **6/25** | [0.115,0.434] | 2/2 | **0/2** | [0.000,0.658] | 19/25 |
| `full` | **0/25** | [0.000,0.133] | 2/2 | **0/2** | [0.000,0.658] | 25/25 |
| `full_lenient` | **1/25** | [0.007,0.195] | 2/2 | **0/2** | [0.000,0.658] | 24/25 |

* `digest_only` false attributions: `A05_nonzero_exit_valid_output`, `C01_producer_digest_mismatch`, `C02_credited_program_not_executed`, `C03_submitted_output_not_observed`, `C04_context_attempt_conflict`, `C05_target_substitution`, `C06_stale_epoch`, `C07_tampered_signature`, `C08_unauthorized_signer`, `C11_stale_attempt`, `C12_observation_output_absent_from_bundle`, `R01_replay_shared_ledger`, `R02_prior_attempt_observation_replayed`
* `signed_digest_only` false attributions: `A05_nonzero_exit_valid_output`, `C01_producer_digest_mismatch`, `C02_credited_program_not_executed`, `C03_submitted_output_not_observed`, `C04_context_attempt_conflict`, `C05_target_substitution`, `C06_stale_epoch`, `C11_stale_attempt`, `C12_observation_output_absent_from_bundle`, `R01_replay_shared_ledger`, `R02_prior_attempt_observation_replayed`
* `signed_context_only` false attributions: `A05_nonzero_exit_valid_output`, `C01_producer_digest_mismatch`, `C02_credited_program_not_executed`, `C03_submitted_output_not_observed`, `C05_target_substitution`, `C12_observation_output_absent_from_bundle`
* `full_lenient` false attributions: `A05_nonzero_exit_valid_output`

## SET 3 — family decomposition

Family A (honest executions) n=8; family B (omission) n=5; families C+R (contradiction + replay) n=14.

| contract | A: success attributed | A: non-success not promoted | B: INCONCLUSIVE | B: REJECT | C+R: detected (REJECT) |
|---|---|---|---|---|---|
| `digest_only` | 2/2 | 1 promoted | 5/5 | 0/5 | **2/14** |
| `signed_digest_only` | 2/2 | 1 promoted | 5/5 | 0/5 | **4/14** |
| `signed_context_only` | 2/2 | 1 promoted | 5/5 | 0/5 | **9/14** |
| `full` | 2/2 | 0 promoted | 5/5 | 0/5 | **14/14** |
| `full_lenient` | 2/2 | 1 promoted | 5/5 | 0/5 | **14/14** |

### Frozen Stage01 pair (real frozen components, not a model)

Cases with a direct Stage01 analogue: **13/27**; the other 14 are **N/A** (no analogue exists) and are not counted in either direction.

| case | Stage01 final | E3 (`full`) | ground truth |
|---|---|---|---|
| `A01_ecdsa_correct` | **ACCEPTED** | ATTRIBUTED_SUCCESS | ATTRIBUTED_SUCCESS |
| `A02_chacha_correct` | **ACCEPTED** | ATTRIBUTED_SUCCESS | ATTRIBUTED_SUCCESS |
| `A03_ecdsa_wrong_answer` | **REJECTED** | REJECT | REJECT |
| `A04_chacha_wrong_answer` | **REJECTED** | REJECT | REJECT |
| `A05_nonzero_exit_valid_output` | **REJECTED** | REJECT | REJECT |
| `A06_malformed_stdout` | **REJECTED** | REJECT | REJECT |
| `A07_empty_stdout` | **REJECTED** | REJECT | REJECT |
| `A08_underdetermined_c0` | **REJECTED** | REJECT | REJECT |
| `B01_missing_observation` | **REJECTED** | INCONCLUSIVE | INCONCLUSIVE |
| `B04_missing_program_source_file` | **REJECTED** | INCONCLUSIVE | INCONCLUSIVE |
| `C01_producer_digest_mismatch` | **REJECTED** | REJECT | REJECT |
| `C02_credited_program_not_executed` | **ACCEPTED** | REJECT | REJECT |
| `C03_submitted_output_not_observed` | **ACCEPTED** | REJECT | REJECT |

Baseline positive control: the frozen Stage01 pair ACCEPTED 2 of the 2 ground-truth successes → the baseline is **not a strawman**.

**Stage01 false attributions: 2/25** — `C02_credited_program_not_executed`, `C03_submitted_output_not_observed`.

