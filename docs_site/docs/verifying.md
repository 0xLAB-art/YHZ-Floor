# Verifying results

Three independent layers, from zero-execution to full re-derivation. None of them
requires trusting a summary: everything regenerates from the frozen rows.

## Layer 1 — bundle integrity (no execution)

```sh
cd reviewer_bundle
python3 -B offline_checks.py verify
```

Checks every manifest-listed payload (24,023 files) against its SHA-256. Expected:
`integrity: PASS`, 0 errors. The `census` subcommand reads archived records only —
it never runs attack programs or contacts anything.

For the full codes+results tree, the [v1.0.0 release](https://github.com/0xLAB-art/YHZ-Floor/releases/tag/v1.0.0-codes-results)
ships `MANIFEST_CODES_RESULTS.sha256` (70,337 entries). Verify it from the extracted
bundle root:

```sh
sha256sum -c MANIFEST_CODES_RESULTS.sha256
```

## Layer 2 — per-cohort regeneration (closed-form, standard library)

Every printed statistic regenerates from the raw per-seed rows. Worked example — the
headline paired contrast of the power cohort (§5):

```sh
cd experiments/info_contract_aesgcm_random_p021ar_20261103/
python3 - <<'PY'
import json
rows = [json.loads(l) for l in open('results.jsonl') if l.strip()]
# registered rule: earliest row per (seed, cell), paired C1-vs-C4 on shared seeds
seen, dedup = set(), []
for r in rows:
    k = (r['seed'], r['cell'])
    if k not in seen: seen.add(k); dedup.append(r)
c1 = {r['seed'] for r in dedup if r['cell'] == 'C1' and r['status'] == 'SUCCESS'}
c4 = {r['seed'] for r in dedup if r['cell'] == 'C4' and r['status'] == 'SUCCESS'}
discord = len(c1 - c4), len(c4 - c1)
print('paired C1-vs-C4 discordance:', discord)   # expected: (96, 0)
PY
```

The exact two-sided binomial p for (96, 0) is `2.5e-29`; the Holm step-down over the
registered 16-member family gives `4.04e-28`. Reproduce the whole table from the
`experiments/` rows with the same enumeration — no statistics package required.

> Field names can differ per cohort (`oracle_verdict` vs `status`, per-cell files). If the
> one-liner above hits an unfamiliar key, read the cohort's `summary.json` first — it
> carries the registered per-cell counts this snippet re-derives.

## Layer 3 — the release manifest + the reviewer projection

- The release bundle's 70,337-entry manifest pins every file of the codes+results tree,
  so any extracted copy is checkable byte-for-byte.
- Inside the projection, [`COPY_LINEAGE.json`](https://github.com/0xLAB-art/YHZ-Floor/blob/main/docs/../reviewer_bundle/COPY_LINEAGE.json)
  records source→destination SHA-256 for every payload, proving the served copies are
  the frozen originals; [`ANONYMITY_SCOPE.json`](https://github.com/0xLAB-art/YHZ-Floor/blob/main/docs/../reviewer_bundle/ANONYMITY_SCOPE.json)
  records the direct-identifier scan (0 hits).

The authoring-time evidence gate (the script that pinned every manuscript number to its
rows during writing) is part of the private full candidate and is not served here; the
public reproducibility surface is Layers 1–2 plus the manifests. If you need a specific
gate check re-run, open an issue and the corresponding Layer-2 derivation will be added
to this document.
