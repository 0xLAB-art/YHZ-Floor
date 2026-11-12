# Verifying results

Three independent layers, from zero-execution to full re-derivation.

## Layer 1 — bundle integrity (no execution)

```sh
cd reviewer_bundle
python3 -B offline_checks.py verify
```

Checks **every manifest-listed payload** (24,023 files) against its SHA-256. Expected: `integrity: PASS`, 0 errors. The census subcommand reads archived records only — it never runs attack programs or contacts anything.

## Layer 2 — per-cohort regeneration (closed-form, stdlib)

Every printed statistic regenerates from the raw per-seed rows. Worked example — the 96/0 paired contrast of the power cohort:

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

The exact two-sided binomial p for (96, 0) is `2.5e-29`; the Holm step-down over the registered 16-member family gives `4.04e-28` — reproduce the whole table from `experiments/` rows with the same enumeration.

## Layer 3 — the paper-level evidence gate

`verify_evidence_revision.py` (shipped with the source bundle) runs **194 checks**: every headline number is pinned to the source text as a case-sensitive needle, per-cohort arithmetic is recomputed from the raw rows (P021AR/P022 cells, Fisher/McNemar/Holm), page budgets are measured, and the abstract echoes the body. Cross-references the build logs and the dist manifests.

## What the rows prove — and what they don't

- Each `results.jsonl` row is a **recorded outcome**: the per-slot verdict under the registered rules, with its attestation block.
- The rows do **not** independently re-prove the cryptography (that would require executing the retained programs — see `reviewer_bundle/review.py h1r3` for the sandboxed path, and `prior_validation/BINDING.json` for what the prior validation covered).
- Censored slots (`COMPLETION_TRUNCATED`, `submissions = 0`) are **unmeasured, not failed** — the estimand is the paired contrast on evaluable pairs, printed beside the all-registered-session sensitivity.

## The chain of custody

`COPY_LINEAGE.json` (in `reviewer_bundle/`) records source→destination SHA-256 for every copied payload; `MANIFEST.json` hashes the assembled package; failed attempts remain separate (no trial added or removed); nothing was executed during packaging. Records retain the originating workstation's bare mount prefix — a filesystem location, not an identity.

---

<div align="center">

Next: <b><a href="docs/REPO_MAP.md">Repository map</a></b> &nbsp;·&nbsp; <a href="README.md">README</a> &nbsp;·&nbsp; <a href="https://0xlab-art.github.io/YHZ-Floor/">Rendered site</a>

</div>
