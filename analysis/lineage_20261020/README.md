# Lineage and cause recomputation (2026-10-20)

Read-only diagnostics over retained artifacts. They exist so that two families
of numbers in the paper can be re-derived rather than quoted: the historical
attribution-lineage cells of Appendix J, and the cause of the retained ECDSA
failures in the H1-R3 cohort.

## Contents

| File | Purpose |
|---|---|
| `recompute_lineage.py` | Runs all three diagnostics and writes `lineage_recomputation.json`. Exit code 0 means every recomputation and cross-check agreed. |
| `verify_lineage.py` | Re-runs the recomputation and compares it with the committed JSON. Exit code 0 means the committed file is reproduced byte for byte. |
| `lineage_recomputation.json` | The committed output. Deterministic: no timestamps, no paths outside the repository. |

## What the three diagnostics do

1. **Lineage cells.** The level-6 false-promotion and false-reject cells of
   IAR-B dev, IAR-B held-out and IAR-C are recomputed from the `per_case`
   records of the raw runs. Denominators are *derived* (attack-family cases for
   false promotions, honest-within-evidence cases for false rejects), not
   assumed, and each recomputed numerator is cross-checked against the value
   the artifact itself records. The artifacts do not record which of the three
   defensible denominators they used for the IAR-B sets; the note in the
   appendix says so explicitly.

2. **ECDSA cause taxonomy.** Every retained ECDSA program is re-executed
   exactly as the harness did (`python -I candidate.py public_instance.json`),
   and then again with its group-order literal replaced by the secp256k1 order
   the instances were generated on. A session is attributed to a wrong
   group-order literal when the as-recorded program fails and the corrected one
   recovers the hidden scalar. Two sessions recover the secret correctly and
   are rejected on the nonce instead, because the L3 predicate requires both.

3. **Cross-arm instance identity.** For every instance shared by the R0 and R2
   arms, the payload is decoded under each arm's own encoding and compared
   value by value. This establishes that the arms differ in rendering only, so
   no outcome difference can be attributed to altered or withheld instance
   content.

## What these diagnostics do not establish

- The ECDSA cause taxonomy is a **post-hoc** diagnostic. It does not change the
  preregistered analysis, the frozen margin rule, or the recorded verdict that
  the L1/L2 R2--ECDSA asymmetry is inconclusive.
- It does not establish *why* the arm is associated with the wrong constant.
  The retained transcripts contain no curve reasoning, so that link is open.
- It licenses no causal representation claim and no capability rate. The
  lineage cells are properties of specified evaluator variants on specified
  case sets, not of agents.
- The lineage cells are **not** pooled with any other population: the IAR
  sets, the H1-R3 cohort and the 852-session matched cohort remain separate.

## Reproduction

```sh
python3 sp2027/analysis/lineage_20261020/recompute_lineage.py   # writes the JSON
python3 sp2027/analysis/lineage_20261020/verify_lineage.py      # checks the committed JSON
```

The recomputation takes about 30 seconds: most of it is re-executing the 426
retained ECDSA programs twice. No provider is called, no network is used, and
no retained record is modified.