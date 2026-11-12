import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

RIG = Path(__file__).resolve().parent / "e3_rig"
ARMS = {"perf_counter_ns_monotonic": "Wall only", "getruseru_utime_split": "Wall + rusage"}
BUILDS = ("vulnerable_ttable", "constant_time_control")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(records):
    if not records:
        raise ValueError("Empty timing cell")
    wall = [r["t_s"] for r in records]
    if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) or v <= 0 for v in wall):
        raise ValueError("Wall samples must be finite positive seconds")
    user = [r.get("ru_utime_s") for r in records]
    present = [v is not None for v in user]
    if any(present) and not all(present):
        raise ValueError("Partially missing child CPU samples")
    result = {"n": len(wall), "wall_median_ms": statistics.median(wall) * 1000}
    if all(present):
        if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) or v < 0 for v in user):
            raise ValueError("CPU samples must be finite nonnegative seconds")
        result["user_cpu_descriptive"] = {
            "n": len(user), "zero_samples": sum(v == 0 for v in user),
            "median_ms": statistics.median(user) * 1000,
            "median_fraction_of_paired_wall": statistics.median(u / w for u, w in zip(user, wall))}
    return result


def load_cells(path):
    cells = {}
    for line in path.read_text().splitlines():
        record = json.loads(line)
        cells.setdefault(record["cell"], []).append(record)
    expected = {f"{b}:{a}:{c}:{s}" for b in BUILDS for a in ARMS for c in ("cold", "warm") for s in ("on", "off")}
    if set(cells) != expected or any(len(v) != 2000 for v in cells.values()):
        raise ValueError("Expected exactly sixteen declared cells of 2000 samples")
    return cells


def corrected_report(rig):
    raw_path = rig / "samples_full.jsonl"
    legacy_path = rig / "e3_analyze_results.json"
    legacy = json.loads(legacy_path.read_text())
    if legacy["inputs"]["samples_sha256"] != sha(raw_path):
        raise ValueError("Raw samples differ from the historical analysis input digest")
    raw_cells = load_cells(raw_path)
    summaries = {name: summarize(rows) for name, rows in sorted(raw_cells.items())}
    for name, cell in summaries.items():
        if not math.isclose(cell["wall_median_ms"], legacy["cell_summaries"][name]["median_ms"], abs_tol=1e-10):
            raise ValueError(f"Published cell does not reproduce from wall seconds: {name}")
        cpu_present = "user_cpu_descriptive" in cell
        if cpu_present != (name.split(":")[1] == "getruseru_utime_split"):
            raise ValueError("CPU samples do not match capture-arm schema")
    differences = []
    for arm in ARMS:
        for cache in ("cold", "warm"):
            for smt in ("on", "off"):
                suffix = f"{arm}:{cache}:{smt}"
                delta = summaries[f"{BUILDS[0]}:{suffix}"]["wall_median_ms"] - summaries[f"{BUILDS[1]}:{suffix}"]["wall_median_ms"]
                differences.append({"arm": arm, "cache": cache, "smt": smt, "wall_delta_ms": delta})
    levels = {"combined": differences}
    levels.update({f"build | timer={arm}": [d for d in differences if d["arm"] == arm] for arm in ARMS})
    levels.update({f"build | cache={c}": [d for d in differences if d["cache"] == c] for c in ("cold", "warm")})
    levels.update({f"build | smt={s}": [d for d in differences if d["smt"] == s] for s in ("on", "off")})
    contrasts = {}
    mean_diagnostics = {}
    for name, members in levels.items():
        recomputed = statistics.median(d["wall_delta_ms"] for d in members)
        old = legacy["contrasts"][name]
        if not math.isclose(recomputed, old["effect_ms"], abs_tol=1e-10):
            raise ValueError(f"Published contrast does not reproduce from wall seconds: {name}")
        label = name
        for arm, human in ARMS.items():
            label = label.replace(f"timer={arm}", f"capture_arm={human}")
        contrasts[label] = {"wall_effect_ms": recomputed, "retained_ci95_ms": old["ci95_ms"],
                            "historical_key": name}
        mean_diagnostics[label] = {"null": "Equal pooled trial mean wall spans across builds within this label stratum",
                                   "welch_t": old["welch_t"], "welch_df": old["welch_df"],
                                   "recorded_normal_approximation_p": old["dudect_p"],
                                   "scope": "Auxiliary pooled-mean diagnostic, not a test of the median-of-cell-medians effect"}
    gate_path = rig / "gate_verdict.json"
    gate = json.loads(gate_path.read_text())
    inputs = [raw_path, legacy_path, rig.parent / "e3_analyze.py", rig.parent / "e3_rig_driver.py",
              gate_path, rig.parent / "e3_gate_check.py"]
    return {"correction": "R2: both arms estimate perf_counter_ns subprocess wall elapsed time",
            "measurement_scope": {"workload": "Synthetic indexed lookup versus full 256-entry scan, 20000 iterations; not AES leakage testing",
                                  "interval": "Fresh subprocess launch, execution and output capture",
                                  "cold": "sync and drop_caches=3 before timing; filesystem-cache operation",
                                  "warm": "Skip drop_caches, still a fresh subprocess",
                                  "smt": "Recorded labels; retained initial source toggles during block preparation, with no per-trial hardware attestation for the interrupted prefix. No identified causal SMT effect."},
            "raw_trials": sum(len(v) for v in raw_cells.values()), "capture_arms": ARMS,
            "input_sha256": {str(p): sha(p) for p in inputs},
            "interval_provenance": "Intervals and pooled Welch diagnostics retained from frozen historical analysis; no new resampling or hypothesis test. Welch diagnostics do not test the median-of-cell-medians estimand.",
            "cpu_scope": "Descriptive child-user-CPU summaries include zeros and preserve trial pairing; not a second timer estimate of the published contrasts.",
            "historical_gate": {"recorded_verdict": gate["verdict"], "n_control_fixed": gate["n_fix"],
                                "n_control_random": gate["n_rand"], "recorded_control_p": gate["p_ct"],
                                "actual_canary_comparison": "vulnerable fixed seed versus control random seeds",
                                "leakage_validation_established": False,
                                "meaning": "Historical PASS is not constant-time assurance or evidence of within-vulnerable input-dependent sensitivity; non-rejection is not equivalence. Current wall reporting does not use this verdict as a scientific admission gate."},
            "primary_estimand": "Median of V-minus-CT cell-median differences; bootstrap conditional on retained host/label strata",
            "cell_summaries": summaries, "paired_cell_differences": differences, "wall_contrasts": contrasts,
            "auxiliary_pooled_mean_diagnostics": mean_diagnostics}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rig", type=Path, default=RIG)
    parser.add_argument("--output", type=Path, default=RIG / "reporting_correction_v2/e3_wall_report.json")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.parent == args.rig.resolve():
        parser.error("Use a separate correction directory; do not overwrite historical rig artifacts")
    report = corrected_report(args.rig)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"raw_trials": report["raw_trials"], "cells": len(report["cell_summaries"]),
                      "reproduced_wall_contrasts": len(report["wall_contrasts"]), "output": str(output)}))


if __name__ == "__main__":
    main()
