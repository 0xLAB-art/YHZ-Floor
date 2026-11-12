import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import e3_statistical_correction as e3c
import e4_statistical_correction as e4c

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / "STATISTICAL_CORRECTION_LOCK.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    e4 = e4c.build_output()
    e4c.validate(e4)
    cells, rows = e3c.load_cells(e3c.DEFAULT_SAMPLES)
    point, deltas = e3c.observed_effect(cells)
    assert len(rows) == 32000
    assert len(cells) == 16
    source_paths = [
        ROOT / "sp2027/analysis/RESULTS_LOCK.json",
        ROOT / "sp2027/agent-eval/runs_legacy_v1",
        ROOT / "sp2027/agent-eval/runs_w2_pilot",
        ROOT / "sp2027/analysis/e3_rig/samples_full.jsonl",
        ROOT / "sp2027/analysis/e3_rig/e3_rig_env.json",
        ROOT / "sp2027/analysis/e3_rig/e3_rig_results_full.json",
        ROOT / "sp2027/analysis/e3_rig/e3_block_sensitivity.json",
    ]
    files = {}
    for path in source_paths:
        if path.is_dir():
            files[str(path.relative_to(ROOT))] = {
                p.name: digest(p) for p in sorted(path.glob("*.json"))
            }
        else:
            files[str(path.relative_to(ROOT))] = digest(path)
    output = {
        "schema": "statistical-correction-lock/1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "historical_number_lock_preserved": True,
        "immutable_source_digests": files,
        "derived_artifacts": {
            "e4": "sp2027/analysis/e4_statistical_correction_v1.json",
            "e3": "sp2027/analysis/e3_rig/e3_bootstrap_correction_v1.json",
        },
        "verified_values": {
            "e4_legacy": e4["cohorts"]["legacy"]["operational_cif"]["event_counts"],
            "e4_pilot": e4["cohorts"]["pilot"]["operational_cif"]["event_counts"],
            "e3_trials": len(rows),
            "e3_cells": len(cells),
            "e3_observed_effect_ms": point,
            "e3_observed_cell_deltas_ms": deltas,
        },
        "interpretation": {
            "e4_primary": "descriptive Aalen-Johansen operational cumulative incidence",
            "e4_km": "secondary assumption-dependent latent-continuation sensitivity",
            "e3": "conditional one-host calibration; no population or causal SMT inference",
        },
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"validated": True, "output": str(OUT), "e3_effect_ms": point}))


if __name__ == "__main__":
    main()
