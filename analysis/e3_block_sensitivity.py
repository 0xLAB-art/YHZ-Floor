from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SAMPLES = ROOT / "e3_rig" / "samples_full.jsonl"
OUT = ROOT / "e3_rig" / "e3_block_sensitivity.json"
PAIRS = [(t, c, s) for t in ("perf_counter_ns_monotonic", "getruseru_utime_split")
         for c in ("warm", "cold") for s in ("on", "off")]
BUILDS = ("vulnerable_ttable", "constant_time_control")
BLOCKS = (10, 50, 100, 250)
BOOT = 1000
SEED = 20261026


def load_cells() -> dict[str, np.ndarray]:
    cells: dict[str, list[float]] = {}
    with SAMPLES.open() as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("t_s", 0) > 0:
                cells.setdefault(row["cell"], []).append(float(row["t_s"]))
    return {k: np.asarray(v, dtype=float) for k, v in cells.items()}


def key(build: str, timer: str, cache: str, smt: str) -> str:
    return f"{build}:{timer}:{cache}:{smt}"


def moving_block_sample(x: np.ndarray, rng: np.random.Generator,
                        block: int) -> np.ndarray:
    starts = np.arange(x.size - block + 1)
    chosen = rng.integers(0, starts.size, int(np.ceil(x.size / block)))
    sample = np.concatenate([x[s:s + block] for s in starts[chosen]])
    return sample[:x.size]


def run(cells: dict[str, np.ndarray], block: int) -> dict[str, float]:
    rng = np.random.default_rng(SEED + block)
    stats = np.empty(BOOT)
    for i in range(BOOT):
        deltas = []
        for timer, cache, smt in PAIRS:
            vuln = moving_block_sample(
                cells[key(BUILDS[0], timer, cache, smt)], rng, block)
            control = moving_block_sample(
                cells[key(BUILDS[1], timer, cache, smt)], rng, block)
            deltas.append(np.median(vuln) - np.median(control))
        stats[i] = np.median(deltas) * 1e3
    lo, hi = np.percentile(stats, (2.5, 97.5))
    return {"median_ms": float(np.median(stats)), "ci95_ms": [float(lo), float(hi)],
            "n_resamples": BOOT, "seed": SEED + block}


def main() -> None:
    cells = load_cells()
    result = {
        "method": "moving-block bootstrap within each paired cell",
        "blocks_trials": list(BLOCKS), "pairs": len(PAIRS),
        "primary_estimator_unchanged": True,
        "results": {str(b): run(cells, b) for b in BLOCKS},
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    for block, values in result["results"].items():
        print(block, values["median_ms"], values["ci95_ms"])


if __name__ == "__main__":
    main()
