import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def main():
    path = ROOT / "ACTS-ATTACK/data/c2t1_open_source_reproduction.json"
    record = json.loads(path.read_text())
    rows = record["results"]
    checks = {"one_named_open_pipeline": isinstance(record["open_pipeline"], str),
              "three_distinct_recorded_runs": len(rows) == 3 and {r["run"] for r in rows} == {1, 2, 3},
              "all_wire_format_valid": all(r["wire_format_valid"] is True for r in rows),
              "binary_verification_not_established": all(r["r2_verified"] is False for r in rows),
              "same_transformation_sizes": all((r["original_bytes"], r["patched_bytes"]) == (1349, 159) for r in rows)}
    result = {"checks": checks, "all_pass": all(checks.values()), "open_pipeline": record["open_pipeline"],
              "recorded_runs": len(rows), "operation_seconds": [r["tte_attack_s"] for r in rows],
              "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "scope": "One pipeline's three summary-level run entries. Not three independent pipelines, proof of autonomous construction, verified binary analysis, or a completed live TLS downgrade."}
    (OUT / "PIPELINE_TRACE.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": len(checks), "all_pass": result["all_pass"], "pipelines": 1, "recorded_runs": len(rows)}))
    if not result["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
