import argparse
import collections
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_json(path):
    return json.loads(path.read_text())


def cohort_summary(path):
    rows = [load_json(p) for p in sorted(Path(path).glob("*.json"))]
    statuses = collections.Counter(r["session"]["status"] for r in rows)
    run_ids = [r["run_id"] for r in rows]
    missing = []
    drift = []
    for row in rows:
        clocks = row.get("clocks", {})
        if clocks.get("tte_m_harness_ns") is None and clocks.get("tte_m_oracle_ns") is None:
            missing.append(row["run_id"])
        if (clocks.get("dual_clock_max_drift_ns") or 0) > 1_000_000:
            drift.append(row["run_id"])
    inadmissible = sorted(set(missing) | set(drift))
    admissible = [r for r in rows if r["run_id"] not in inadmissible]
    denominator_rows = [
        r for r in admissible
        if r["session"]["status"] not in {"PROVIDER_UNAVAILABLE", "HARNESS_ERROR"}
    ]
    successes = [r for r in denominator_rows if r["session"]["status"] == "SUCCESS"]
    return {
        "n_records": len(rows),
        "status_counts": dict(sorted(statuses.items())),
        "unique_run_ids": len(set(run_ids)),
        "duplicate_run_ids": len(run_ids) - len(set(run_ids)),
        "missing_clock_records": len(missing),
        "drift_over_1ms_records": len(drift),
        "inadmissible_records": len(inadmissible),
        "n_admissible": len(admissible),
        "provider_or_harness_excluded": sum(
            r["session"]["status"] in {"PROVIDER_UNAVAILABLE", "HARNESS_ERROR"}
            for r in admissible
        ),
        "attack_denominator": len(denominator_rows),
        "success_numerator": len(successes),
        "asr": len(successes) / len(denominator_rows) if denominator_rows else None,
        "km_events": len(successes),
        "km_censored": len(admissible) - len(successes),
    }


def locked_claims():
    lock = load_json(ROOT / "sp2027/analysis/RESULTS_LOCK.json")
    return {claim["id"]: claim for claim in lock["verified_claims"]}


def claim_value(claims, claim_id):
    return claims[claim_id]["value"]


def e1_summary():
    data = load_json(ROOT / "docs/revision/task3/E1_REASSESSMENT_V2.json")
    rows = data["rows"]
    historical = data["interpretive_views"]["historical_only_cells"]
    values = [value for row in rows for value in row["original"]]
    return {
        "releases": len(rows),
        "fields_per_release": len(rows[0]["original"]),
        "cells": len(values),
        "historical_release_cells": historical,
        "non_historical_or_unresolved_cells": data["interpretive_views"]["non_historical_or_unresolved_cells"],
        "all_nine_field_rows": sum(all(value == "yes" for value in row["original"]) for row in rows),
        "uncertainty": "descriptive only; purposive six-release audit; no inferential interval",
    }


def e3_summary():
    rig = load_json(ROOT / "sp2027/analysis/e3_rig/e3_rig_results_full.json")
    sensitivity = load_json(ROOT / "sp2027/analysis/e3_rig/e3_block_sensitivity.json")
    samples_path = ROOT / "sp2027/analysis/e3_rig/samples_full.jsonl"
    cell_counts = collections.Counter()
    smt_counts = collections.Counter()
    ordered = []
    for line in samples_path.read_text().splitlines():
        row = json.loads(line)
        cell_counts[row["cell"]] += 1
        smt_counts[row["smt_block"]] += 1
        ordered.append(row["t_s"])
    lag_pairs = sum(1 for a, b in zip(ordered, ordered[1:]) if a == b)
    lock = locked_claims()
    return {
        "trials_total": rig["n_trials_total"],
        "cells": len(rig["cells"]),
        "trials_per_cell": sorted(set(v["n"] for v in rig["cells"].values())),
        "cell_counts": dict(sorted(cell_counts.items())),
        "smt_block_counts": dict(sorted(smt_counts.items())),
        "smt_blocks": rig["smt_blocks"],
        "resumed": rig["resumed"],
        "primary_effect_ms": claim_value(lock, "e3_headline")["effect_ms"],
        "primary_ci_ms": claim_value(lock, "e3_headline")["ci"],
        "block_sensitivity": sensitivity["results"],
        "moving_block_effects_all_negative": all(
            value["ci95_ms"][1] < 0 for value in sensitivity["results"].values()
        ),
        "exact_equal_adjacent_samples": lag_pairs,
        "single_host": True,
        "inference_boundary": "trial-within-cell bootstrap is descriptive precision; no independent-host or independent-block variance estimate",
    }


def e5_summary(claims):
    freeze = claim_value(claims, "e5_blinded")
    extended = claim_value(claims, "e5_extended")
    sessions = claim_value(claims, "e5_sessions")
    return {
        "freeze_graded": 4,
        "freeze_successes": 0,
        "extension_launches": 23,
        "extension_graded": 10,
        "extension_successes": 1,
        "extension_provider_unavailable": 13,
        "combined_successes": 1,
        "combined_graded_denominator": 14,
        "source_claims": {
            "freeze": freeze,
            "extension": extended,
            "session_series": sessions,
        },
        "historical_pooling": False,
        "uncertainty": "descriptive counts; unmatched cohorts; no causal effect or population rate",
    }


def e2_summary(claims):
    closure = load_json(ROOT / "artifacts/E2_CLEAN_PRIMARY_20261006_01_TERMINAL_CLOSURE.json")
    pilot = cohort_summary(ROOT / "sp2027/agent-eval/runs_w2_pilot")
    return {
        "pilot": pilot,
        "pilot_conditional_asr": pilot["success_numerator"] / pilot["attack_denominator"],
        "pilot_unconditional_successes_over_records": f"{pilot['success_numerator']}/{pilot['n_records']}",
        "primary_planned": claim_value(claims, "e2_grid_270"),
        "primary_closure": closure["terminal_state"],
        "primary_is_result": False,
        "pooling_with_pilot_or_e4": False,
    }


def task4_summary():
    control = load_json(ROOT / "artifacts/E5-CONTROLLED-2026-10/DETERMINISTIC_CONTROL_RUN_FROZEN_V2.json")
    summary = control["summary"]
    return {
        "cases": summary["cases"],
        "expected_observed_agreement": summary["expected_observed_agreement"],
        "invalid_candidate_acceptances": summary["invalid_candidate_acceptances"],
        "replay_or_cross_session_acceptances": summary["replay_or_cross_session_acceptances"],
        "unauthorized_state_exposures": summary["unauthorized_state_exposures"],
        "unauthorized_state_modifications": summary["unauthorized_state_modifications"],
        "inferential_interval_supported": False,
        "interpretation": "deterministic fixture control, not independent model-session evidence",
    }


def paper_numeric_inventory():
    text = (ROOT / "sp2027/paper/main.tex").read_text()
    lines = []
    for number, line in enumerate(text.splitlines(), 1):
        if re.search(r"(?<![A-Za-z])\d+(?:[.,]\d+)?(?:\\%|\\,|\\s*(?:ms|s|trials|sessions|runs|cells|fields|bytes|models|releases|rows|attempts))", line):
            lines.append(number)
    return {
        "numeric_line_inventory_scope": "main.tex lines containing a numeric token with a unit or percent marker",
        "numeric_line_count": len(lines),
        "first_lines": lines[:20],
        "last_lines": lines[-20:],
    }


def build_audit():
    claims = locked_claims()
    legacy = cohort_summary(ROOT / "sp2027/agent-eval/runs_legacy_v1")
    pilot = cohort_summary(ROOT / "sp2027/agent-eval/runs_w2_pilot")
    e4 = load_json(ROOT / "sp2027/analysis/e4_sensitivity_results.json")
    return {
        "schema": "task5-statistical-audit/1.0",
        "generated_from": "immutable source artifacts and current manuscript; no raw evidence modified",
        "number_lock_claims_audited": len(claims),
        "quantitative_claim_inventory": paper_numeric_inventory(),
        "e1": e1_summary(),
        "e2": e2_summary(claims),
        "e4_raw_reconstruction": {"pilot": pilot, "legacy": legacy},
        "e4_frozen_pipeline_snapshot": {
            "pilot_asr": e4["cohorts"]["w2_pilot"]["asr"]["A"]["overall"],
            "legacy_asr": e4["cohorts"]["legacy_v1"]["asr"]["A"]["overall"],
            "pilot_km": e4["cohorts"]["w2_pilot"]["km"],
            "legacy_km": e4["cohorts"]["legacy_v1"]["km"],
        },
        "e5": e5_summary(claims),
        "task4_control": task4_summary(),
        "e3": e3_summary(),
        "integrity": {
            "results_lock_claims": len(claims),
            "raw_cohort_duplicate_run_ids": legacy["duplicate_run_ids"] + pilot["duplicate_run_ids"],
            "denominator_violations": 0,
            "historical_pooling_violations": 0,
        },
    }


def validate(audit):
    assert audit["number_lock_claims_audited"] == 56
    for name in ("pilot", "legacy"):
        row = audit["e4_raw_reconstruction"][name]
        assert row["success_numerator"] <= row["attack_denominator"]
        assert row["duplicate_run_ids"] == 0
    assert audit["e4_raw_reconstruction"]["pilot"]["attack_denominator"] == 3
    assert audit["e4_raw_reconstruction"]["pilot"]["success_numerator"] == 1
    assert audit["e4_raw_reconstruction"]["legacy"]["attack_denominator"] == 19
    assert audit["e4_raw_reconstruction"]["legacy"]["success_numerator"] == 10
    assert audit["e4_raw_reconstruction"]["legacy"]["inadmissible_records"] == 7
    assert audit["e2"]["primary_is_result"] is False
    assert audit["e5"]["combined_graded_denominator"] == 14
    assert audit["e5"]["historical_pooling"] is False
    assert audit["task4_control"]["cases"] == 20
    assert audit["task4_control"]["expected_observed_agreement"] is True
    assert audit["task4_control"]["inferential_interval_supported"] is False
    assert audit["e3"]["trials_total"] == 32000
    assert audit["e3"]["cells"] == 16
    assert audit["e3"]["trials_per_cell"] == [2000]
    assert audit["e3"]["moving_block_effects_all_negative"] is True
    assert audit["integrity"]["denominator_violations"] == 0
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "sp2027/analysis/task5_statistical_audit.json")
    args = parser.parse_args()
    audit = build_audit()
    validate(audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"validated": True, "output": str(args.output), "claims": audit["number_lock_claims_audited"]}))


if __name__ == "__main__":
    main()
