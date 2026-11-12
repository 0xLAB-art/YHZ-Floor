#!/usr/bin/env python3
"""Read-only reconstruction of benign control records; never calls a model."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import statistics


def replay(directory):
    plan = json.loads((directory / "PLAN.json").read_text())
    summary = json.loads((directory / "SUMMARY.json").read_text())
    errors = []
    phash = hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()
    rows, groups = [], defaultdict(list)
    names = {"PLAN.json", "SUMMARY.json"} | {c["run_id"] + ".json" for c in plan["cases"]}
    if {p.name for p in directory.glob("*.json")} != names:
        errors.append("filename inventory mismatch")
    ids = [c["run_id"] for c in plan["cases"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate IDs")
    for name, expected in summary["file_sha256"].items():
        path = directory / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append("file digest mismatch: " + name)
    for case in plan["cases"]:
        path = directory / (case["run_id"] + ".json")
        if not path.is_file():
            errors.append("missing record")
            continue
        row = json.loads(path.read_text())
        if row["case"] != case or row["plan_sha256"] != phash:
            errors.append("identity/provenance mismatch")
        if row.get("request_elapsed_ns", 0) <= 0:
            errors.append("missing request clock")
        mode = plan["mode"]
        if mode == "local":
            group = "local_integer_sum"
            if row["status"] in ("SUCCESS", "ORACLE_FAIL"):
                for key in ("snapshot_before", "snapshot_after"):
                    if row.get(key) != plan["model_snapshot"]:
                        errors.append("missing or changed model snapshot")
                response = row["provider_response"]
                text = response.get("response", "")
                expected = "SUCCESS" if re.fullmatch(r"\s*-?\d+\s*", text) and int(text) == sum(case["integers"]) else "ORACLE_FAIL"
                payload = dict(plan["request"], model=plan["model_snapshot"]["name"],
                               options=plan["options"],
                               prompt=plan["prompt_template"].format(integers=case["integers"]))
                if row.get("request_payload") != payload or response.get("model") != payload["model"] or response.get("done") is not True:
                    errors.append("request/response metadata mismatch")
                if row["status"] != expected:
                    errors.append("independent arithmetic verdict mismatch")
            elif row["status"] != "PROVIDER_UNAVAILABLE":
                errors.append("local harness/unknown error")
        else:
            group = f"{case['scenario']}|retry={case['retry_limit']}|latency_ms={case['latency_ms']}"
            scenario = case["scenario"]
            expected = "ORACLE_FAIL" if scenario == "malformed" else (
                "PROVIDER_UNAVAILABLE" if "persistent" in scenario or
                (scenario.endswith("once") and case["retry_limit"] == 0) else "SUCCESS")
            expected_attempts = (case["retry_limit"] + 1 if "persistent" in scenario else
                                 min(2, case["retry_limit"] + 1) if scenario.endswith("once") else 1)
            codes = ([int(scenario[:3])] * expected_attempts if "persistent" in scenario else
                     [int(scenario[:3])] + ([200] if expected_attempts == 2 else []) if scenario.endswith("once") else [200])
            if row["status"] != expected or [a["http_code"] for a in row["attempts"]] != codes:
                errors.append("fault/outcome reconstruction mismatch")
        groups[group].append(row)
        rows.append(row)
    counts = dict(Counter(r["status"] for r in rows))
    if counts != summary["status_counts"] or len(rows) != summary["recorded"] or len(rows) != len(plan["cases"]):
        errors.append("summary census mismatch")
    per_group = {}
    for key, group in groups.items():
        per_group[key] = {"n": len(group), "statuses": dict(Counter(r["status"] for r in group)),
                          "median_request_ms": statistics.median(r["request_elapsed_ns"] for r in group) / 1e6}
    return {"mode": plan["mode"], "planned": len(plan["cases"]), "recorded": len(rows),
            "errors": errors, "pass": not errors, "status_counts": counts,
            "per_condition": per_group,
            "scope": "Independent offline reconstruction of benign controls; no security capability or human-validation inference"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = replay(args.directory)
    print(json.dumps(result, indent=2))
    raise SystemExit(not result["pass"])
