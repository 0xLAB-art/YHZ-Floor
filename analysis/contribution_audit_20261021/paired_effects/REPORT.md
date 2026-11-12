# Exploratory paired policy and representation analysis

This additive analysis reads the original frozen H1-R3 confirmatory cohort. It does not modify the preregistration, manuscript, raw rows, or original analysis. All new interaction, pooling-sensitivity, and multiple-interval calculations are exploratory. No post-hoc equivalence certification is made.

## Provenance and denominators

Input: `/mnt/nvme5/ACTS-Attack/sp2027/analysis/h1r3_20261019/runs/confirmatory/results.jsonl`. SHA-256: `192d4669f9a2b8e9af253e5f1d0afe1134050fa736e4c7f1ebf8eae8a412e9a7`; checked before and after analysis.
All 852 rows are accounted for: 768 primary R0/R1/R2 sessions, 64 R4 repeat-prompt sessions, and 20 C0 abstention sessions. Main analyses use 256 complete matched triplets: 64 instances at L1, 64 at L2, and 128 at L3. Per family these are 32, 32, and 64. There are no missing primary arms, duplicate primary cells, provider/extraction exclusions, or denominator drops. Each representation contrast has 256 pairs across levels, not 512 independent instances; paired_instances.csv contains the two correlated contrasts for each instance.
All 852 retained candidate.py hashes match their row source hashes. Reapplying the existing legacy AST qualification function to each retained source reproduces all 852 recorded admission decisions and legacy rejection flags. This verifies the stored admission calculation, not the security soundness of the qualifier or fresh execution of the programs.
The recorded model route is `claude-sonnet-4-6-free` for all 852 rows. R0/R1/R2 are representation arms, not different models. Route metadata does not prove immutable backend weights.
R4 is reported separately: {'n': 64, 'success': 63}. C0 is separately {'n': 20, 'correct_abstention': 20}. Correct abstention is not exploit recovery; C0 can have terminal SUCCESS while terminal_success is zero. Neither control enlarges a representation-pair denominator.

## Estimands and resampling

For matched family/level/instance i, Y is terminal_success and A is the independently recomputed legacy source-admission indicator. Current outcome is Y; the legacy source-admission counterfactual is Y×A. For treatment R1 or R2, d_current = Y_t−Y_0, d_legacy = Y_t A_t−Y_0 A_0, and the policy interaction is q = d_legacy−d_current. Negative q means legacy admission makes the treatment contrast less favorable. Equivalently q is successful-source loss in R0 minus successful-source loss in the treatment. Every q lies in {−1,0,1}.
The current outcomes are historical execution outcomes under v3. The counterfactual only gates those same generated sources using legacy admission. No old-policy provider run, regeneration, adaptation, runtime replay, or causal behavior response to a changed policy is observed. The difference-in-differences is a paired algebraic admission contrast on fixed programs; it does not identify a fresh policy deployment effect.
Main bootstrap: 50,000 draws, seed 20261021, numpy default_rng PCG64. Resample complete matched instances jointly across current and legacy outcomes, retaining both source outcomes per pair. Pooled draws resample within each of the two fixed family strata, preserving observed 50:50 family weights. This respects pair dependence and shares draw indices for all three metrics within a contrast. Separate intervals are marginal; they must not be subtracted to obtain an interaction interval.
Pooling sensitivity includes (1) unstratified matched-instance sampling, (2) resampling shared numeric-seed blocks with both families together, and (3) changing the weight of ECDSA to 0, 0.25, 0.5, 0.75, or 1. Family-specific results are also leave-one-family-out estimates. Sharing a seed label does not by itself prove dependence across distinct task families; the block variant is a sensitivity analysis. Two selected families are inadequate for inference about a population of cryptographic families; no two-cluster asymptotic interval is claimed.
Multiplicity: all 36 exact two-sided McNemar tests (18 current and 18 legacy-admission contrasts) are Holm-adjusted together, rather than selectively testing L3 after inspection. The 54 main metric estimates include ordinary 95% percentile intervals and conservative Bonferroni54 percentile intervals at nominal 1−0.05/54 each. Bootstrap approximation and ceiling limitations still apply: Bonferroni does not repair poor marginal bootstrap coverage. Sensitivity intervals are unadjusted exploratory intervals. Policy interactions have intervals and sign counts, not a randomized-policy p-value. No multiple-testing result establishes equivalence.

## Pooled comparisons

All effects and interval endpoints below are percentage points. b/c are R0-only/treatment-only discordant successes; q−/q+ count negative/positive within-instance policy changes.

| Level / contrast | Pairs | Current R0 / treatment | Current effect [95%] | b/c | Legacy R0 / treatment | Legacy effect [95%] | b/c | Policy change [95%] | q−/q+ |
|---|---:|---|---|---|---|---|---|---|---|
| L1 R1-R0 | 64 | 61/64, 64/64 | 4.69 [0.00, 10.94] | 0/3 | 61/64, 64/64 | 4.69 [0.00, 10.94] | 0/3 | 0.00 [0.00, 0.00] | 0/0 |
| L1 R2-R0 | 64 | 61/64, 55/64 | -9.38 [-18.75, 1.56] | 9/3 | 61/64, 36/64 | -39.06 [-46.88, -28.12] | 27/2 | -29.69 [-37.50, -20.31] | 19/0 |
| L2 R1-R0 | 64 | 64/64, 64/64 | 0.00 [0.00, 0.00] | 0/0 | 46/64, 63/64 | 26.56 [17.19, 35.94] | 1/18 | 26.56 [17.19, 35.94] | 1/18 |
| L2 R2-R0 | 64 | 64/64, 55/64 | -14.06 [-23.44, -6.25] | 9/0 | 46/64, 31/64 | -23.44 [-32.81, -14.06] | 15/0 | -9.38 [-21.88, 3.12] | 12/6 |
| L3 R1-R0 | 128 | 125/128, 126/128 | 0.78 [-2.34, 3.91] | 2/3 | 100/128, 111/128 | 8.59 [0.78, 16.41] | 9/20 | 7.81 [0.00, 15.62] | 8/18 |
| L3 R2-R0 | 128 | 125/128, 124/128 | -0.78 [-4.69, 3.12] | 4/3 | 100/128, 58/128 | -32.81 [-42.19, -23.44] | 48/6 | -32.03 [-42.19, -21.88] | 50/9 |

The stated L3 R0/R2 example is correct: 125/128 versus 124/128 becomes 100/128 versus 58/128 under source admission. R0 loses 25 current successes and R2 loses 66, so the contrast changes by (25−66)/128 = −41/128 = −32.03125 pp. This is not merely a subtraction of independent rates: among 128 matched instances, 50 shift in the negative direction, 9 in the positive direction, and 69 have no policy-induced contrast change.

## Family-specific estimates

| Level | Family | Contrast | Pairs | Current effect [95%]; b/c | Legacy effect [95%]; b/c | Policy change [95%]; q−/q+ |
|---|---|---|---:|---|---|---|
| L1 | ECDSA_Nonce_Reuse | R1-R0 | 32 | 9.38 [0.00, 21.88]; 0/3 | 9.38 [0.00, 21.88]; 0/3 | 0.00 [0.00, 0.00]; 0/0 |
| L1 | ECDSA_Nonce_Reuse | R2-R0 | 32 | -18.75 [-37.50, 3.12]; 9/3 | -78.12 [-93.75, -56.25]; 27/2 | -59.38 [-75.00, -40.62]; 19/0 |
| L1 | XOR_Keystream_Reuse | R1-R0 | 32 | 0.00 [0.00, 0.00]; 0/0 | 0.00 [0.00, 0.00]; 0/0 | 0.00 [0.00, 0.00]; 0/0 |
| L1 | XOR_Keystream_Reuse | R2-R0 | 32 | 0.00 [0.00, 0.00]; 0/0 | 0.00 [0.00, 0.00]; 0/0 | 0.00 [0.00, 0.00]; 0/0 |
| L2 | ECDSA_Nonce_Reuse | R1-R0 | 32 | 0.00 [0.00, 0.00]; 0/0 | 53.12 [34.38, 71.88]; 1/18 | 53.12 [34.38, 71.88]; 1/18 |
| L2 | ECDSA_Nonce_Reuse | R2-R0 | 32 | -21.88 [-37.50, -9.38]; 7/0 | -40.62 [-59.38, -25.00]; 13/0 | -18.75 [-43.75, 6.25]; 12/6 |
| L2 | XOR_Keystream_Reuse | R1-R0 | 32 | 0.00 [0.00, 0.00]; 0/0 | 0.00 [0.00, 0.00]; 0/0 | 0.00 [0.00, 0.00]; 0/0 |
| L2 | XOR_Keystream_Reuse | R2-R0 | 32 | -6.25 [-15.62, 0.00]; 2/0 | -6.25 [-15.62, 0.00]; 2/0 | 0.00 [0.00, 0.00]; 0/0 |
| L3 | ECDSA_Nonce_Reuse | R1-R0 | 64 | 0.00 [-6.25, 6.25]; 2/2 | 15.62 [0.00, 31.25]; 9/19 | 15.62 [0.00, 31.25]; 8/18 |
| L3 | ECDSA_Nonce_Reuse | R2-R0 | 64 | -1.56 [-7.81, 4.69]; 3/2 | -43.75 [-59.38, -26.56]; 34/6 | -42.19 [-59.38, -23.44]; 36/9 |
| L3 | XOR_Keystream_Reuse | R1-R0 | 64 | 1.56 [0.00, 4.69]; 0/1 | 1.56 [0.00, 4.69]; 0/1 | 0.00 [0.00, 0.00]; 0/0 |
| L3 | XOR_Keystream_Reuse | R2-R0 | 64 | 0.00 [-4.69, 4.69]; 1/1 | -21.88 [-32.81, -12.50]; 14/0 | -21.88 [-32.81, -12.50]; 14/0 |

At L1/L2, the legacy-admission interaction is confined to ECDSA in these data; XOR has zero such changes. At L3 both families contribute to the negative R2 shift. Equal-family pooling is therefore a defined weighted summary, not evidence that every family shares one magnitude.

## Pooling and multiplicity sensitivity

| Level / contrast | Policy change: family-stratified 95% | Unstratified 95% | Shared-seed-block 95% | Bonferroni54 interval |
|---|---|---|---|---|
| L1 R1-R0 | [0.00, 0.00] | [0.00, 0.00] | [0.00, 0.00] | [0.00, 0.00] |
| L1 R2-R0 | [-37.50, -20.31] | [-40.62, -18.75] | [-37.50, -20.31] | [-43.75, -14.29] |
| L2 R1-R0 | [17.19, 35.94] | [15.62, 39.06] | [17.19, 35.94] | [9.38, 42.19] |
| L2 R2-R0 | [-21.88, 3.12] | [-21.88, 3.12] | [-21.88, 3.12] | [-29.69, 12.50] |
| L3 R1-R0 | [0.00, 15.62] | [0.00, 15.62] | [0.00, 15.62] | [-4.69, 20.31] |
| L3 R2-R0 | [-42.19, -21.88] | [-42.19, -21.88] | [-41.41, -22.66] | [-49.22, -14.06] |

Family-mixture sensitivity for the L3 R2 policy change (weight is assigned to ECDSA; remainder to XOR):

| ECDSA weight | Policy change (pp) |
|---:|---:|
| 0.0 | -21.88 |
| 0.25 | -26.95 |
| 0.5 | -32.03 |
| 0.75 | -37.11 |
| 1.0 | -42.19 |

All full estimates, discordance tables, McNemar p values and Holm36 values are in contrasts.csv/results.json. The interactions and alternative intervals were selected for this audit and remain exploratory even where intervals exclude zero.

## Ceiling, zero discordance, and preregistration

Current pooled R0 failure headroom is 3/64 at L1, 0/64 at L2, and 3/128 at L3. At L3, the empirical maximum positive treatment−R0 contrast is only 3/128 = 2.34 pp because R0 already succeeds in 97.66%. A negative treatment effect could still be much larger; ceiling does not symmetrically bound harm. Lower-level R2 arms fail in 9/64 each, creating more observed outcome variation than L3 R2 (4/128). The lower-level R0 baselines do not have uniformly more headroom than L3.
An all-zero observed contrast yields a degenerate empirical bootstrap; it does not establish that unseen instances have zero effect. For every zero-discordance current/legacy contrast and every all-zero policy-change vector, results.json supplies the exact independent-instance zero-event upper bound 1−0.05^(1/n) on nonzero-event probability, which also bounds the absolute mean of a variable in {−1,0,1}. For n=32,64,128 these are about 8.94%,4.57%,2.31%. The more conservative alpha=0.025 bound is also provided (10.89%,5.60%,2.84%), along with an alpha=0.05/54 familywise companion. Shared-seed sensitivity also reports zero-event bounds at the smaller number of independent seed blocks (32/32/64 across levels). These bounds concern the tested fixed design under instance-sampling assumptions; they do not apply to arbitrary new models, families, or difficulty regimes.
The original preregistration text describes 1−0.025^(1/n) as one-sided 95%; mathematically that expression is one-sided 97.5% (or the upper endpoint of a two-sided 95% zero-event interval). Its prose sample-size approximation also does not match that expression. The stats helper uses alpha=0.05 by default; the original analyzer attaches the alpha=0.025 companion. Both conventions are exposed here without altering the freeze or decision.
preregistered_L3_reproduction.json executes the original collect_pairs/contrast functions on the original rows, retaining the original 20,000 bootstrap draws, seed 20261019, and ±0.10 decision rule. It reproduces the original bounded L3 EQUIVALENT_WITHIN_MARGIN labels for R1/R2, intervals [−2.34375,3.90625] and [−4.6875,3.125] pp, and Holm p=1 for both. This is a reproduction of that predeclared result, not a new equivalence claim for the exploratory analyses.

## Permitted conclusion and unsupported generalization

The retained cohort demonstrates that a source-admission rule can change the magnitude and apparent ordering of representation-arm completion contrasts while program bytes and historical cryptographic outcomes are held fixed. The strongest numerical example is the L3 R2−R0 shift of −32.03 pp under legacy admission. The current L3 contract retains its original bounded representation conclusion. Family and level differences are material to interpretation.
These data do not establish policy effects on regenerated programs, behavior under a newly disclosed policy, a model ranking, cross-provider robustness, autonomous vulnerability discovery, arbitrary evaluator designs, transfer to other benchmarks, or general representation invariance. The source-admission calculation cannot validate the isolation/security properties of the sandbox or reconstruct unobserved old-policy executions. A smaller interval at ceiling is precision about this selected population under stated assumptions, not universal equivalence.

## Runnable evidence and validation

Run from `/mnt/nvme5/ACTS-Attack`:

```bash
python sp2027/analysis/contribution_audit_20261021/paired_effects/analyze.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s sp2027/analysis/contribution_audit_20261021/paired_effects -p test_analysis.py -v
python sp2027/analysis/contribution_audit_20261021/paired_effects/render_report.py
```

The captured invocations redirect output to .omo/evidence/analysis.log, tests.log, and report.log. Exact commands, binary observables, and artifact paths for each criterion are recorded in .omo/evidence/EVIDENCE.json. Nine tests exercise duplicate/missing-pair rejection, family/instance identity, exclusions, counterfactual interaction signs, joint-bootstrap identity and reproducibility, fixed family weights, zero-discordance uncertainty, and the frozen L3 count claim. The first analysis assertion incorrectly treated C0 terminal SUCCESS as an exploit outcome; the assertion was corrected to retain the distinct C0 predicate, and the full analysis and test scenario were rerun.
All deliverables remain under the assigned paired_effects directory. No provider calls or fresh candidate executions were made.
