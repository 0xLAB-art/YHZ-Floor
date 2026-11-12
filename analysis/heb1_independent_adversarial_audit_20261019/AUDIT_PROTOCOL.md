# HEB-1 Independent Adversarial Audit Protocol

**Status:** completed, read-only, offline

## Scope

This audit independently challenges HEB-1, IAR-A/B/C, B2-1, and B2-2. It does
not rerun H1/R0/R1/P010, redesign or rerun IAR-B/IAR-C, modify frozen artifacts,
call providers, access external targets, or use the network. It does not create a
new benchmark.

## Questions

1. What guarantee did HEB-1 actually promise?
2. Do the raw cases establish a false promotion under that guarantee?
3. Are the baselines compared under a common claim contract?
4. Does the real Stage01 pipeline expose an external composition boundary?
5. Is V3-full's zero conditional on aligned fixtures and a restricted attacker?
6. Does the local prior-art record establish exact anticipation or only the broad
   provenance/binding principle?

## Evidence classes

- **IR:** independently reproduced by executing an existing verifier or by
  recomputing an existing raw result without changing its inputs.
- **SCI:** source-code inference from the inspected implementation/dataflow.
- **UH:** untested hypothesis; not treated as a result.

## Commands executed

```text
python3 sp2027/analysis/heb1_crossboundary_20261019/iar/verify_iar_a.py
```

The command returned `TOTAL 77 checks | PASS 75 | WARN 2 | FAIL 0` and wrote
only its report under `/tmp/opencode/iar_a_verify/`.

The audit also ran read-only Python recomputation over:

```text
sp2027/analysis/heb1_crossboundary_20261019/heldout/heldout_results.json
sp2027/analysis/experiment_b_20261019/iar_c/runs/20261019_121621/results.json
sp2027/analysis/experiment_b_20261019/b2/runs/20261019_140814/results.json
sp2027/analysis/experiment_b_20261019/b2_2_stage01/B2_2_RESULTS.json
```

No existing repository artifact was written by these recomputations.

## Integrity boundary

The protected files were hashed read-only during the audit and matched the
standing expected values:

```text
RESULTS_LOCK.json       4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39
RESULTS_LOCK_H1PC.json  8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103
main.tex                51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461
main.pdf                fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a
```

The repository contains extensive unrelated pre-existing modifications. The
audit did not reset, clean, or overwrite them.
