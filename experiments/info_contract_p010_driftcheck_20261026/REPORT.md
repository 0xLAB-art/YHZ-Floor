# P010 Drift-Check Rerun — Report (2026-10-26)

Same protocol (`P010-INFO-CONTRACT-2X2-CHACHA20-v1`), same label
(`claude-sonnet-4-6-free`), original seeds 41–44, base runner
byte-identical. 16 unique sessions (+1 duplicate C1/seed41 from the resume
edge; both draws SUCCESS on turn 1, 1 submission). 23 provider responses,
0 provider failures.

| cell | P010 (2026-10-18) | drift-check (2026-10-26) | P010P seeds 101–108 |
|------|-------------------|--------------------------|---------------------|
| C1 stated | 4/4 | 4/4 | 8/8 |
| C2 withheld | 4/4 | **2/4** | 0/8 |
| C3 stated | 4/4 | 4/4 | 8/8 |
| C4 withheld | 0/4 | **2/4** | 3/8 |

- **Premise marginal reproduces exactly**: stated 8/8 vs withheld 4/8 —
  identical to the original P010 marginal (8/8 vs 4/8).
- **Stated cells reproduce exactly**: C1 and C3 both 4/4, all first-turn,
  one submission each (same as P010 and P010P saturation).
- **Withheld-arm internal split is unstable across time on identical
  seeds**: C2 4/4→2/4, C4 0/4→2/4. Paired C1-vs-C4 discordance this run:
  2/0 (ties on seeds 41, 44) vs the original 4/0.

## Verdict on the drift-vs-heterogeneity question
Neither pure explanation holds. The registered P010 estimands (premise
marginal; C1-over-C4 direction) reproduce on the same seeds, so the
powered cohort's C2 0/8 is not explained by a changed environment alone.
But the withheld cells' per-cell outcomes shift between identical-seed
runs, so the original C2 4/4 was not a stable property of those seeds
either. The instability is concentrated entirely in the
withheld-premise arm; the stated-premise arm is deterministic at this
scale. This is consistent with the paper's registered treatment: cell-level
nulls in the withheld arm are descriptive, and inference rests on the
powered and second-label replications of the premise marginal.

## Epistemic status
Post-hoc reproducibility rerun; not pooled with any cohort; disclosed in
the supplement (S30) as such. Frozen artifacts: prompts/, raw_provider_responses/,
execution_captures/, events.jsonl, results.jsonl, summary.json, run_info.json
(annotated `rerun_kind`).
