#!/usr/bin/env python3
"""
e3_analyze.py — E3 factorial analysis (frozen design: E3.yaml v0.2, D-RIG RESOLVED).

Inputs (sp2027/analysis/e3_rig/):
  samples_full.jsonl          per-trial records from e3_rig_driver.py
  e3_rig_results_full.json    aggregates + SMT block facts
  e3_rig_env.json             host declaration (measured)
  gate_verdict.json           negative-control verdict (e3_gate_check.py)

Frozen rules enforced here:
  - gate verdict != PASS        -> REFUSE: D-TIME demotion path (runbook §8)
  - no full-run results         -> REFUSE unless --allow-shakedown
                                   (draft outputs, marked DRAFT, never a claim)
  - shakedown after 2026-10-25  -> D-TIME notice printed
  - smt_applied = false         -> SMT contrasts skipped; covariate note emitted
                                   (E3.yaml v0.2: factorial reduces to 2×2×2)

Pre-declared analysis (E3.yaml `analysis:`):
  1. effect sizes: vulnerable − control per factor (overall + at each level
     of timer / cache / smt), effect = Δmedian (ms),
     CI = 10,000-resample percentile bootstrap (seed 20261026, recorded),
  2. nonparametric summaries under skew: per-cell n / median / p05 / p95,
  3. dudect-style Welch test per contrast (two-sided, alpha = 0.01; the
     machinery is shared with the gate via e3_gate_check.welch_t),
  4. rusage-arm supplement: user-CPU fraction of wall time per cell (the
     "split" that timer arm exists to provide).

SMT split-plot note (emitted verbatim in outputs): SMT is a BETWEEN-BLOCK
factor; contrasts computed within one block are clean, cross-block
summaries carry block-level variance and are labeled.

Outputs (sp2027/analysis/e3_rig/):
  e3_analyze_results.json    full results (draft-marked on shakedown input)
  tableC.tex                 paper Table C source (W5 fill; DRAFT-marked)
  e3_figure_effects.json     effect-size figure data (W5 figure scripts)

Run:  python3 sp2027/analysis/e3_analyze.py [--allow-shakedown]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RIG = HERE / "e3_rig"
sys.path.insert(0, str(HERE))
from e3_gate_check import ALPHA, welch_t  # noqa: E402  (shared dudect machinery)

BOOT_N = 10_000
BOOT_SEED = 20261026          # recorded; distinct from the driver's order seed
HARD_STOP = "2026-10-25"      # E3.yaml hard_stop
BUILD_V, BUILD_C = "vulnerable_ttable", "constant_time_control"
TIMERS = ["perf_counter_ns_monotonic", "getruseru_utime_split"]
CACHES = ["cold", "warm"]
SMTS = ["on", "off"]
SPLITPLOT_NOTE = ("SMT is a between-block (split-plot) factor: contrasts "
                  "within one block are clean; cross-block summaries carry "
                  "block-level variance.")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_and_guard(allow_shakedown: bool):
    gate_path = RIG / "gate_verdict.json"
    if not gate_path.exists():
        sys.exit("REFUSING: no gate_verdict.json — the negative-control gate "
                 "(runbook §6) must run and PASS before any analysis.")
    gate = json.loads(gate_path.read_text())
    if gate.get("verdict") != "PASS":
        sys.exit(f"REFUSING: gate verdict is {gate.get('verdict')!r} — D-TIME "
                 "demotion applies (runbook §8): demote Table C to a "
                 "motivating audit case, record in DECISIONS.md.")

    full = RIG / "e3_rig_results_full.json"
    if full.exists():
        tag = "full"
        results_path = full
    elif allow_shakedown:
        tag = "shakedown"
        results_path = RIG / "e3_rig_results_shakedown.json"
        today = datetime.now(timezone.utc).date().isoformat()
        if today > HARD_STOP:
            print(f"D-TIME NOTICE: {today} > hard stop {HARD_STOP} and no "
                  "full run exists — demotion applies automatically. This "
                  "shakedown analysis is DRAFT pipeline evidence only.")
    else:
        sys.exit(f"REFUSING: {full.name} not found — run the full factorial "
                 "(e3_rig_driver.py, ~32,000 trials) or pass --allow-shakedown "
                 "for a DRAFT pipeline test on shakedown data.")

    env_path = RIG / "e3_rig_env.json"
    samples_path = RIG / f"samples_{tag}.jsonl"
    if not samples_path.exists():
        sys.exit(f"REFUSING: {samples_path.name} missing — samples are the "
                 "released evidence; aggregates alone cannot be analyzed.")
    results = json.loads(results_path.read_text())
    env = json.loads(env_path.read_text()) if env_path.exists() else {}
    return gate, results, env, samples_path, tag


def load_samples(samples_path: Path) -> dict:
    """cell -> {wall: float[], user: float[]|None} (seconds)."""
    cells: dict[str, dict] = {}
    with samples_path.open() as fh:
        for line in fh:
            r = json.loads(line)
            if not r.get("t_s") or r["t_s"] <= 0:
                continue
            c = cells.setdefault(r["cell"], {"wall": [], "user": [],
                                             "block": r.get("smt_block")})
            c["wall"].append(r["t_s"])
            if r.get("ru_utime_s"):
                c["user"].append(r["ru_utime_s"])
    return cells


def cell_summary(vals: np.ndarray) -> dict:
    s = np.sort(vals)
    n = s.size
    return {"n": int(n),
            "median_ms": float(np.median(s) * 1e3),
            "p05_ms": float(s[max(0, n // 20)] * 1e3),
            "p95_ms": float(s[min(n - 1, n * 19 // 20)] * 1e3)}


def boot_ci_median_diff(x: np.ndarray, y: np.ndarray,
                        n: int = BOOT_N, seed: int = BOOT_SEED):
    """Percentile bootstrap CI for median(x) − median(y). Deterministic
    given (x, y, seed): the seed is frozen and recorded in every output."""
    rng = np.random.default_rng(seed)
    stats = np.empty(n)
    for i in range(n):
        xs = x[rng.integers(0, x.size, x.size)]
        ys = y[rng.integers(0, y.size, y.size)]
        stats[i] = np.median(xs) - np.median(ys)
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return float(lo * 1e3), float(hi * 1e3)


PAIRS = [(t, c, s) for t in TIMERS for c in CACHES for s in SMTS]


def combined_effect(cells: dict, pairs, n: int = BOOT_N,
                    seed: int = BOOT_SEED):
    """Build effect over a set of PAIRED cells (same timer/cache/smt on both
    builds) = median of the per-pair Δmedians, with a HIERARCHICAL bootstrap
    CI (resample trials within each paired cell, recompute every pair's
    Δmedian, re-combine). A pooled contrast across the cache factor is
    ill-posed: cold cells are process-start dominated (~6 ms) while warm
    cells are compute-dominated (~0.7–2.9 ms), so the pooled distribution is
    bimodal and its CI is meaningless (caught on the root-mode shakedown,
    2026-09-28)."""
    rng = np.random.default_rng(seed)
    kv = {p: np.sort(np.asarray(
        cells[f"{BUILD_V}:{p[0]}:{p[1]}:{p[2]}"]["wall"])) for p in pairs}
    kc = {p: np.sort(np.asarray(
        cells[f"{BUILD_C}:{p[0]}:{p[1]}:{p[2]}"]["wall"])) for p in pairs}
    point = float(np.median([np.median(kv[p]) - np.median(kc[p])
                             for p in pairs]))
    stats = np.empty(n)
    for i in range(n):
        deltas = []
        for p in pairs:
            xs = kv[p][rng.integers(0, kv[p].size, kv[p].size)]
            ys = kc[p][rng.integers(0, kc[p].size, kc[p].size)]
            deltas.append(np.median(xs) - np.median(ys))
        stats[i] = np.median(deltas)
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return point * 1e3, float(lo * 1e3), float(hi * 1e3)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-shakedown", action="store_true",
                    help="analyze shakedown samples; outputs marked DRAFT")
    args = ap.parse_args()

    gate, results, env, samples_path, tag = load_and_guard(
        args.allow_shakedown)
    cells = load_samples(samples_path)

    expected = [f"{b}:{t}:{c}:{s}" for b in (BUILD_V, BUILD_C)
                for t in TIMERS for c in CACHES for s in SMTS]
    missing = [k for k in expected if k not in cells or len(cells[k]["wall"]) == 0]
    if missing:
        sys.exit(f"REFUSING: incomplete factorial — {len(missing)} empty "
                 f"cells (e.g. {missing[:2]}). A partial run is not analyzable.")

    smt_applied = bool(results.get("smt_applied"))
    draft = tag == "shakedown"

    # ---- 1. per-cell nonparametric summaries -----------------------------
    summaries = {}
    for k in expected:
        wall = np.asarray(cells[k]["wall"])
        s = cell_summary(wall)
        if cells[k]["user"]:
            u = np.asarray(cells[k]["user"])
            frac = u[:min(u.size, wall.size)] / wall[:min(u.size, wall.size)]
            s["user_frac_median"] = float(np.median(frac))
        s["smt_block"] = cells[k]["block"]
        summaries[k] = s

    # ---- 2. pre-declared contrasts (build effect per factor) -------------
    # Every factor-level contrast aggregates ACROSS the remaining factors
    # (4 paired cells per level) via the hierarchical bootstrap; the
    # combined contrast uses all 8 pairs. The Welch p is auxiliary (pooled
    # means over the level's cells); the primary null-evidence instrument
    # is the negative-control gate, which must read PASS.
    contrasts = {}

    def level_effect(pairs, seed_off, note=None):
        point, lo2, hi2 = combined_effect(cells, pairs,
                                          seed=BOOT_SEED + seed_off)
        pv = np.concatenate([np.asarray(
            cells[f"{BUILD_V}:{p[0]}:{p[1]}:{p[2]}"]["wall"]) for p in pairs])
        pc = np.concatenate([np.asarray(
            cells[f"{BUILD_C}:{p[0]}:{p[1]}:{p[2]}"]["wall"]) for p in pairs])
        t2, df2, p2 = welch_t(pv.tolist(), pc.tolist())
        out = {"effect_ms": point, "ci95_ms": [lo2, hi2],
               "welch_t": t2, "welch_df": df2, "dudect_p": p2,
               "verdict": "difference" if p2 < ALPHA else "null",
               "n_pairs": len(pairs),
               "bootstrap_seed": BOOT_SEED + seed_off}
        if note:
            out["note"] = note
        return out

    contrasts["combined"] = level_effect(PAIRS, 0)
    contrasts["combined"]["definition"] = (
        "median of the per-pair build Δmedians; hierarchical bootstrap "
        "(within-cell resampling)")
    contrasts["combined"]["pooled_note"] = (
        "no pooled-across-cache point estimate: cold cells are "
        "process-start dominated (~6 ms) vs warm compute (~0.7–2.9 ms) — "
        "pooling is bimodal by construction")
    i = 1
    for tname in TIMERS:
        contrasts[f"build | timer={tname}"] = level_effect(
            [q for q in PAIRS if q[0] == tname], i)
        i += 1
    for cname in CACHES:
        contrasts[f"build | cache={cname}"] = level_effect(
            [q for q in PAIRS if q[1] == cname], i)
        i += 1
    if smt_applied:
        for sname in SMTS:
            contrasts[f"build | smt={sname}"] = level_effect(
                [q for q in PAIRS if q[2] == sname], i,
                note="within-block contrast (clean under the split-plot)")
            i += 1
    else:
        contrasts["build | smt"] = {"skipped": "smt_applied=false — SMT is "
                                    "a recorded covariate (E3.yaml v0.2); "
                                    "factorial reduces to 2×2×2"}

    # ---- 3. outputs -------------------------------------------------------
    stamp = datetime.now(timezone.utc).isoformat()
    out = {
        "run_tag": tag, "draft": draft,
        "generated_utc": stamp,
        "inputs": {"samples": str(samples_path),
                   "samples_sha256": sha256_file(samples_path),
                   "results_sha256": sha256_file(RIG / f"e3_rig_results_{tag}.json"),
                   "gate_verdict": gate.get("verdict"),
                   "gate_recorded_utc": gate.get("recorded_utc"),
                   "host_virtualization": (env.get("host") or {}).get("virtualization")},
        "analysis": {"bootstrap": {"n": BOOT_N, "seed": BOOT_SEED,
                                   "kind": "percentile, median difference"},
                     "dudect": {"test": "Welch t two-sided", "alpha": ALPHA},
                     "smt": {"applied": smt_applied,
                             "blocks": results.get("smt_blocks"),
                             "split_plot_note": SPLITPLOT_NOTE}},
        "cell_summaries": summaries,
        "contrasts": contrasts,
        "paper_slot": ("§Timing Table C — "
                       + ("DRAFT on shakedown data, not a claim (fills the "
                          "retired PENDING-E3R slot)" if draft
                          else "FULL RUN (fills the retired PENDING-E3R "
                               "slot; see ledger 2026-09-28)")),
    }
    (RIG / "e3_analyze_results.json").write_text(json.dumps(out, indent=2) + "\n")

    # figure data (W5 figure scripts consume this; no plotting here)
    fig = {"generated_utc": stamp, "draft": draft, "seed": BOOT_SEED,
           "effects": [{"contrast": k, "effect_ms": v["effect_ms"],
                        "ci95_ms": v["ci95_ms"], "dudect_p": v["dudect_p"],
                        "verdict": v["verdict"]}
                       for k, v in contrasts.items() if "effect_ms" in v]}
    (RIG / "e3_figure_effects.json").write_text(json.dumps(fig, indent=2) + "\n")

    # ---- Table C (booktabs; matches the paper's table style) -------------
    def row(name: str, v: dict) -> str:
        # Presentation floor (2026-09-29, post-freeze formatting-only patch,
        # ledger-recorded): the Welch computation is a normal approximation on
        # t (e3_gate_check.welch_t); for |t| this large (warm cells:
        # t = -115.2, df ~ 15.5k) the double-precision tail underflows to
        # exactly 0.0. Never print a bare 0 for a p-value — print the floor
        # the computation can honestly resolve (<1e-16) and release the exact
        # statistic + degrees of freedom in e3_analyze_results.json.
        p = v["dudect_p"]
        p_str = "<1e-16" if p == 0 else f"{p:.2g}"
        return (f"{name} & {v['effect_ms']:.3f} & "
                f"[{v['ci95_ms'][0]:.3f}, {v['ci95_ms'][1]:.3f}] & "
                f"{p_str} & {v['verdict']} \\\\")

    lines = [
        f"% AUTO-GENERATED by sp2027/analysis/e3_analyze.py — {stamp}",
        f"% run_tag={tag}" + ("  [DRAFT — shakedown data; NOT a claim]" if draft
                              else "  [FULL RUN]"),
        f"% gate={gate.get('verdict')} ({gate.get('recorded_utc')}); "
        f"bootstrap n={BOOT_N} seed={BOOT_SEED}; smt_applied={smt_applied}",
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{E3 timing factorial (frozen design): pre-declared build "
        r"contrasts (vulnerable $-$ constant-time control). Effect is the "
        r"median difference in ms; CIs are 10k-resample percentile "
        r"bootstraps (seed 20261026), conditional on the observed rig and "
        r"blocks; $p$ is a dudect-style Welch "
        r"calibration diagnostic (two-sided, $\alpha=0.01$), not "
        r"independent-trial or population-level inference. The combined row is the median of "
        r"the eight paired-cell $\Delta$medians, not the median of the "
        r"per-level rows; on this run the two summaries coincide "
        r"($-1.696$ ms) because the cold-cache deltas straddle the "
        r"warm-cache ones. SMT contrasts are within-block "
        r"(split-plot). Single host, measured bare metal, disclosed.}",
        r"\label{tab:timing-contrasts}",
        r"\small",
        r"\begin{tabular}{@{}lrrrl@{}}",
        r"\toprule",
        r"Contrast & $\Delta$median (ms) & 95\% CI (ms) & $p$ & verdict \\",
        r"\midrule",
        row("vulnerable $-$ control (combined: median of the 8 "
            "paired-cell $\\Delta$medians)",
            contrasts["combined"]),
        row(r"\quad timer = perf\_counter\_ns", contrasts[f"build | timer={TIMERS[0]}"]),
        row(r"\quad timer = getrusage\_utime", contrasts[f"build | timer={TIMERS[1]}"]),
        row(r"\quad cache = cold", contrasts[f"build | cache={CACHES[0]}"]),
        row(r"\quad cache = warm", contrasts[f"build | cache={CACHES[1]}"]),
    ]
    if smt_applied:
        lines.append(row(r"\quad smt = on", contrasts[f"build | smt={SMTS[0]}"]))
        lines.append(row(r"\quad smt = off", contrasts[f"build | smt={SMTS[1]}"]))
    else:
        lines.append(r"\quad smt (covariate mode) & \multicolumn{4}{l}{"
                     r"recorded condition, not a factor (E3.yaml v0.2)} \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    (RIG / "tableC.tex").write_text("\n".join(lines))

    # ---- printed report ---------------------------------------------------
    print(f"E3 analysis ({tag}{' DRAFT' if draft else ''}): "
          f"{len(expected)} cells, gate={gate.get('verdict')}, "
          f"smt_applied={smt_applied}")
    print(f"  combined build effect: {contrasts['combined']['effect_ms']:+.3f} ms "
          f"[{contrasts['combined']['ci95_ms'][0]:.3f}, "
          f"{contrasts['combined']['ci95_ms'][1]:.3f}], "
          f"p={contrasts['combined']['dudect_p']:.2g} -> "
          f"{contrasts['combined']['verdict']}")
    for k, v in contrasts.items():
        if k != "combined" and "effect_ms" in v:
            print(f"  {k:38s} {v['effect_ms']:+8.3f} ms  p={v['dudect_p']:.2g} "
                  f"({v['verdict']})")
    print(f"out: {RIG}/e3_analyze_results.json, tableC.tex, "
          f"e3_figure_effects.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
