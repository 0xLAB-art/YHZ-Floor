# REPORT — P010L3: third-label replication of the information-contract 2×2

**Namespace:** `sp2027/research_execution/info_contract_label3_20261029/`
**Protocol:** `P010L3-INFO-CONTRACT-2X2-CHACHA20-LABEL3-v1`
**Label:** `gpt-6-astra` on `https://agentrouter.org`, Anthropic-compatible `/v1/messages`
**Frozen:** `PREREGISTRATION.md` + `FREEZE.json`, before the first provider call
**Run:** 2026-10-29 · 32/32 terminal sessions · 48 provider responses · 0 provider failures · 0 retries, 0 seed replacements

## 1. Result

| Cell | accepted | submissions | turns | first-turn |
|---|---:|---:|---:|---:|
| C1 (named, premise stated) | 8/8 | 8 | 8 | 8 |
| C2 (withheld, unstated) | 0/8 | 16 | 16 | 0 |
| C3 (withheld, stated) | 8/8 | 8 | 8 | 8 |
| C4 (named, unstated) | 0/8 | 16 | 16 | 0 |

- **Premise marginal:** 16/16 with the reference stated vs 0/16 withheld —
  Fisher one-sided **p = 1.66e-9**, two-sided **p = 3.33e-9**.
- **Seed-stratified CMH:** χ² = **24.0**, p = **9.63e-7**, 8 strata
  (uncorrected, the same statistic the earlier cohorts report; the
  implementation is validated by reproducing P010L2's χ² = 24.0, p = 9.6e-7
  exactly from label-2's own rows).
- **Paired C1-versus-C4 discordance:** 8/0, all C1, no ties —
  binomial two-sided **p = 0.0078**.
- **Naming marginal:** 8/16 vs 8/16, p = **1.0** — inert on this label too.
- **Derive frame stays refuted:** C2 0/8, every session reaching turn 2 and
  failing (16 submissions for zero acceptances).

## 2. What this adds

The premise share now transports across **three** provider-attested labels on
two families of serving stack: primary `claude-sonnet-4-6-free` (P010, P010P,
P010N16), `gpt-6.1-sol` (P010L2), and `gpt-6-astra` (this cohort). The withheld
arm's *degree* continues to differ by label (C4: 0/4, 3/8, 0/8, 0/8 across
labels) while the stated arm remains deterministic and the premise marginal
repeats the same 16/16 vs 0/16 split that label 2 produced. Cross-label counts
are **descriptive only and never pooled**; each cohort is its own population.

Not claimed: a capability rate, any vendor comparison, or that a label identity
was resolved beyond the route's own attestation.

## 3. Deviations and boundaries

1. **D1 provider injection** — the AgentRouter adapter is registered as
   `provider_adapter` before the frozen runner imports; the frozen runner's
   SHA-256 (`a08eab6f…`) is asserted at launch and the file is untouched.
2. **D2 token floor** — the adapter sends 2800 output tokens instead of the
   frozen runner's 1400, uniformly across cells, so reasoning-budget exhaustion
   cannot correlate with a cell. Identical to P010L2's deviation, same value.
3. **Post-registered design** — the cohort was designed after label 2's
   outcome was known; it is a replication of an established pattern, not a
   blind confirmation, and is described as such in the manuscript.
4. **Label-selection probes are not evidence** — the two smoke calls and the
   4-comparison identity probe in `smoke_labels.json` /
   `label_identity_probe.json` (sibling `p1/` directory) used a generic XOR
   task outside any fixture; they establish transport viability only.
5. **Cost ceiling.** Measured 17,108 input + 67,335 output tokens. At the
   route's published ratio-3 basis ($6/$6 per M) that is $0.51; at its ratio-2
   basis ($4/$20) it is $1.42. The route does not expose which group applies,
   so both are recorded in `BUDGET_LEDGER.jsonl` and the ≤$1.00 preregistered
   ceiling is reported as *met only under the lower basis* rather than resolved.

## 4. Reproduction and integrity

```bash
python3 sp2027/research_execution/info_contract_label3_20261029/analyze_label3.py
python3 sp2027/research_execution/info_contract_label3_20261029/leakscan_label3.py
```

- `ANALYSIS.json` — all statistics above, deduplicated to one row per
  (seed, cell); instrument duplicates are recorded, never deleted.
- `LEAK_SCAN.json` — 300 files scanned, **0 prompt files contain fixture truth**
  (`leak_free_prompts: true`); `hashes/all_artifacts.sha256` covers 301 files.
- `FREEZE.json` — pre-run hashes of the preregistration, wrapper, frozen runner
  and adapter.
