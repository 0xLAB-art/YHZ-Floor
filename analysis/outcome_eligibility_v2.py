import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "sp2027/agent-eval/runs_legacy_v1"
OUT = ROOT / "sp2027/analysis/reviewer_resolution_20261015/R5/OUTCOME_REANALYSIS.json"


def classify(record):
    status = record["session"]["status"]
    if status not in {"SUCCESS", "ORACLE_FAIL", "AGENT_GIVEUP", "PROVIDER_UNAVAILABLE"}:
        raise ValueError(f"Unreviewed legacy terminal status: {status}")
    invalid = record["legacy"].get("exclusion_reason") == "harness_defect_session_invalid"
    provider = status == "PROVIDER_UNAVAILABLE"
    valid = not invalid and not provider
    clock = record["clocks"].get("dual_clock_max_drift_ns")
    historical_clock_gate = status in {"SUCCESS", "ORACLE_FAIL"} and clock is not None and clock > 1_000_000
    return {"run_id": record["run_id"], "task": record["task_card"]["task_id"], "status": status,
            "success": status == "SUCCESS", "relay_invalid": invalid,
            "outcome_conditional_eligible": valid,
            "outcome_operational_eligible": not invalid,
            "historical_strict_conditional_eligible": valid and not historical_clock_gate,
            "historical_strict_operational_eligible": not invalid and not historical_clock_gate,
            "historical_clock_gate": historical_clock_gate,
            "candidate_rejection_observed": status == "ORACLE_FAIL"}


def summarize(records):
    ids = [r["run_id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate execution identity")
    rows = [classify(r) for r in records]
    estimates = {}
    for field in ("outcome_conditional_eligible", "outcome_operational_eligible",
                  "historical_strict_conditional_eligible", "historical_strict_operational_eligible"):
        eligible = [r for r in rows if r[field]]
        successes = sum(r["success"] for r in eligible)
        estimates[field] = {"successes": successes, "denominator": len(eligible),
                            "fraction": successes / len(eligible) if eligible else None}
    return {"estimands": estimates, "rows": rows}


def main():
    lock = json.loads((ROOT / "sp2027/analysis/STATISTICAL_CORRECTION_LOCK.json").read_text())
    frozen = lock["immutable_source_digests"][str(CORPUS.relative_to(ROOT))]
    paths = sorted(CORPUS.glob("*.json"))
    if {p.name for p in paths} != set(frozen):
        raise ValueError("Legacy population differs from frozen source set")
    for path in paths:
        if hashlib.sha256(path.read_bytes()).hexdigest() != frozen[path.name]:
            raise ValueError(f"Frozen legacy record changed: {path.name}")
    records = [json.loads(p.read_text()) for p in paths]
    raw_path = ROOT / "ACTS-ATTACK/harness/rerun/results_rerun/agent/agent_records.jsonl"
    raw = [json.loads(line) for line in raw_path.open()]
    if len(raw) != 54 or any(r["legacy"] != original for r, original in zip(records, raw)):
        raise ValueError("Migrated legacy payloads differ from the nested primary rows")
    result = summarize(records)
    observed = [(v["successes"], v["denominator"]) for v in result["estimands"].values()]
    if observed != [(10, 23), (10, 51), (10, 19), (10, 47)]:
        raise ValueError(f"Population reconstruction changed: {observed}")
    restored = [r for r in result["rows"] if r["outcome_conditional_eligible"] and not r["historical_strict_conditional_eligible"]]
    if len(restored) != 4 or any(r["success"] for r in restored):
        raise ValueError("Unexpected historical-clock exclusion outcomes")
    result.update({"scope": "Outcome rates ignore timing disagreement; historical timing-selected estimators retained as sensitivity. No new session or model comparison.",
                   "restored_outcome_rows": [r["run_id"] for r in restored],
                   "raw_primary_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
                   "frozen_record_hashes": frozen, "whole_census": {"successes": 10, "records": 54,
                   "meaning": "Descriptive retained census, including three relay-invalid sessions; not a replacement eligible-outcome rate"}})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"nested_primary_rows_match": True, "frozen_records": len(paths), "estimands": result["estimands"]}))


if __name__ == "__main__":
    main()
