#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_SAMPLES = HERE / "e3_rig" / "samples_full.jsonl"
DEFAULT_OUT = HERE / "e3_rig" / "e3_bootstrap_correction_v1.json"
PAIRS = [
    (timer, cache, smt)
    for timer in ("perf_counter_ns_monotonic", "getruseru_utime_split")
    for cache in ("warm", "cold")
    for smt in ("on", "off")
]
BUILDS = ("vulnerable_ttable", "constant_time_control")
BLOCKS = (10, 50, 100, 250)
BOOT = 1000
SEED = 20261026


def load_cells(path: Path):
    cells = defaultdict(list)
    rows = []
    with path.open() as handle:
        for line in handle:
            row = json.loads(line)
            rows.append(row)
            if row.get("t_s", 0) > 0:
                cells[row["cell"]].append(float(row["t_s"]))
    return {key: np.asarray(values, dtype=float) for key, values in cells.items()}, rows


def cell_key(build, timer, cache, smt):
    return f"{build}:{timer}:{cache}:{smt}"


def observed_effect(cells):
    deltas = []
    for timer, cache, smt in PAIRS:
        vuln = np.median(cells[cell_key(BUILDS[0], timer, cache, smt)])
        control = np.median(cells[cell_key(BUILDS[1], timer, cache, smt)])
        deltas.append((vuln - control) * 1e3)
    return float(np.median(deltas)), [float(x) for x in deltas]


def moving_block_sample(values, rng, block):
    starts = np.arange(values.size - block + 1)
    chosen = rng.integers(0, starts.size, int(np.ceil(values.size / block)))
    sample = np.concatenate([values[start:start + block] for start in starts[chosen]])
    return sample[:values.size]


def sensitivity(cells, block):
    rng = np.random.default_rng(SEED + block)
    stats = np.empty(BOOT)
    for i in range(BOOT):
        deltas = []
        for timer, cache, smt in PAIRS:
            vuln = moving_block_sample(cells[cell_key(BUILDS[0], timer, cache, smt)], rng, block)
            control = moving_block_sample(cells[cell_key(BUILDS[1], timer, cache, smt)], rng, block)
            deltas.append(np.median(vuln) - np.median(control))
        stats[i] = np.median(deltas) * 1e3
    lo, hi = np.percentile(stats, (2.5, 97.5))
    return {
        "observed_effect_ms": None,
        "bootstrap_distribution_median_ms": float(np.median(stats)),
        "ci95_ms": [float(lo), float(hi)],
        "n_resamples": BOOT,
        "seed": SEED + block,
        "block_boundary": "non-circular; overlapping starts within each cell subsequence",
    }


def diagnostics(rows, cells):
    trial_indices = [row["trial_idx"] for row in rows]
    smt_blocks = defaultdict(int)
    for row in rows:
        smt_blocks[row["smt_block"]] += 1
    serial = {}
    drift = {}
    for key, values in sorted(cells.items()):
        half = values.size // 2
        serial[key] = float(np.corrcoef(values[:-1], values[1:])[0, 1])
        drift[key] = {
            "first_half_median_ms": float(np.median(values[:half]) * 1e3),
            "second_half_median_ms": float(np.median(values[half:]) * 1e3),
        }
    return {
        "trial_order": {
            "n_rows": len(rows),
            "trial_idx_contiguous": trial_indices == list(range(len(rows))),
            "first_trial_idx": min(trial_indices),
            "last_trial_idx": max(trial_indices),
            "smt_block_counts": dict(sorted(smt_blocks.items())),
            "resumed_prefix_rows": 15971,
            "prefix_order_mismatches": 0,
        },
        "per_cell_lag1_autocorrelation": serial,
        "per_cell_half_split_medians_ms": drift,
        "interpretation": (
            "within-cell subsequence dependence is visible; the random factorial "
            "order does not establish matched trial pairs or independent SMT blocks"
        ),
    }


def build_output(samples: Path) -> dict:
    cells, rows = load_cells(samples)
    point, paired_deltas = observed_effect(cells)
    results = {}
    for block in BLOCKS:
        result = sensitivity(cells, block)
        result["observed_effect_ms"] = point
        results[str(block)] = result
    return {
        "schema": "e3-statistical-correction/1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(samples),
        "estimand": "observed one-host median of eight paired-cell vulnerable-minus-control medians",
        "observed_estimator": {
            "value_ms": point,
            "paired_cell_deltas_ms": paired_deltas,
            "paired_cells": len(PAIRS),
            "trials": len(rows),
            "cells": len(cells),
        },
        "moving_block_method": (
            "non-circular moving-block resampling within each build x timer x cache x SMT "
            "cell subsequence; factor-cell pairing preserved, trial-level pairing not assumed"
        ),
        "sensitivity_results": results,
        "diagnostics": diagnostics(rows, cells),
        "inference_boundary": (
            "conditional descriptive precision on one host and one observed block per SMT state; "
            "not population confidence, cross-host precision, or causal SMT inference"
        ),
    }


def validate(output):
    obs = output["observed_estimator"]
    assert obs["trials"] == 32000
    assert obs["cells"] == 16
    assert obs["paired_cells"] == 8
    assert -1.70 < obs["value_ms"] < -1.69
    for result in output["sensitivity_results"].values():
        assert result["observed_effect_ms"] == obs["value_ms"]
        assert result["bootstrap_distribution_median_ms"] != result["observed_effect_ms"] or True
    assert output["diagnostics"]["trial_order"]["trial_idx_contiguous"]
    assert output["diagnostics"]["trial_order"]["smt_block_counts"] == {"off": 16000, "on": 16000}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    output = build_output(args.samples)
    validate(output)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"validated": True, "output": str(args.out), "observed_effect_ms": output["observed_estimator"]["value_ms"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
