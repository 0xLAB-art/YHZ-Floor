#!/usr/bin/env python3
"""Predeclared, non-agent arithmetic controls. No tools or security targets.

Local inference is optional and restricted to a non-remote Ollama model.
Fault conditions are synthetic, not observations of a real provider.
Outputs are exclusive-create; an existing experiment cannot be resumed/overwritten.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
import random
import re
import statistics
import time
import urllib.error
import urllib.request
import uuid

BASE = "http://127.0.0.1:11434"
MODEL = "gemma4local:latest"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def write_new(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def request(endpoint, payload=None, timeout=5):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + endpoint, data=data,
                                 headers={"Content-Type": "application/json"})
    # Explicit loopback and no ambient proxy; never select a cloud model.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as response:
        return json.load(response)


def local_model():
    rows = request("/api/tags")["models"]
    row = next(r for r in rows if r["name"] == MODEL)
    if row.get("remote_host") or row.get("remote_model") or row["size"] < 1_000_000:
        raise ValueError("A real local weight model is required")
    if not re.fullmatch(r"[0-9a-f]{64}", row["digest"]):
        raise ValueError("Missing full model digest")
    return {k: row[k] for k in ("name", "digest", "size", "details")}


def correct(text, integers):
    return bool(re.fullmatch(r"\s*-?\d+\s*", text)) and int(text) == sum(integers)


def make_plan(mode, model=None, runtime=None):
    namespace = str(uuid.uuid4())
    rng = random.Random(20261004)
    rows = []
    if mode == "local":
        for index in range(12):
            values = [rng.randint(-30, 60) for _ in range(4)]
            rows.append({"task": "integer_sum", "track": "benign_no_tools",
                         "integers": values, "ordinal": index})
    else:
        for scenario in ("ok", "429_once", "503_once", "429_persistent", "503_persistent", "malformed"):
            for retry_limit in (0, 1, 2):
                for latency_ms in (0, 5):
                    for replicate in range(5):
                        rows.append({"task": "integer_sum", "track": "synthetic_fault",
                                     "integers": [7, -2, 11, 4], "scenario": scenario,
                                     "retry_limit": retry_limit, "latency_ms": latency_ms,
                                     "replicate": replicate})
        rng.shuffle(rows)
    for row in rows:
        row["run_id"] = str(uuid.uuid5(uuid.UUID(namespace), json.dumps(row, sort_keys=True)))
    return {"schema": "benign-control-v1", "namespace": namespace, "mode": mode,
            "created_utc": utc(), "seed": 20261004, "cases": rows,
            "model_snapshot": model, "runtime": runtime,
            "environment": {"system": platform.system(), "release": platform.release(),
                            "machine": platform.machine(), "python": platform.python_version(),
                            "container_digest": None, "execution": "native_not_containerized"},
            "options": {"temperature": 0, "seed": 20261004, "num_predict": 32,
                        "num_ctx": 2048}, "timeout_seconds": 40,
            "request": {"stream": False, "think": False, "keep_alive": "5m"},
            "prompt_template": "Return only the integer sum, no explanation: {integers}",
            "grade": "strict integer-only response equals Python sum; no retries for local",
            "fault_backoff_seconds": 0.002,
            "scope": "benign instrument control, NOT a security-agent campaign or human validation",
            "exclusions": "retain every scheduled case and failure; no selective dropping"}


def synthetic(case, plan):
    attempts = []
    started = time.perf_counter_ns()
    text = ""
    scenario = case["scenario"]
    for attempt in range(case["retry_limit"] + 1):
        a0 = time.perf_counter_ns()
        time.sleep(case["latency_ms"] / 1000)
        error = scenario.startswith(("429", "503")) and ("persistent" in scenario or attempt == 0)
        code = int(scenario[:3]) if error else 200
        text = "not an integer" if scenario == "malformed" else str(sum(case["integers"]))
        attempts.append({"attempt": attempt, "http_code": code,
                         "elapsed_ns": time.perf_counter_ns() - a0})
        if code == 200:
            break
        if attempt < case["retry_limit"]:
            time.sleep(plan["fault_backoff_seconds"])
    end = time.perf_counter_ns()
    g0 = time.perf_counter_ns()
    status = "PROVIDER_UNAVAILABLE" if attempts[-1]["http_code"] != 200 else (
        "SUCCESS" if correct(text, case["integers"]) else "ORACLE_FAIL")
    return {"attempts": attempts, "response": text if attempts[-1]["http_code"] == 200 else None,
            "status": status, "request_elapsed_ns": end - started,
            "grader_elapsed_ns": time.perf_counter_ns() - g0,
            "synthetic": True}


def infer(case, plan):
    before = local_model()
    if before != plan["model_snapshot"]:
        return {"status": "HARNESS_ERROR", "error": "model snapshot changed before request"}
    payload = dict(plan["request"], model=MODEL, options=plan["options"],
                   prompt=plan["prompt_template"].format(integers=case["integers"]))
    start = time.perf_counter_ns()
    try:
        response = request("/api/generate", payload, plan["timeout_seconds"])
        elapsed = time.perf_counter_ns() - start
        g0 = time.perf_counter_ns()
        if response.get("model") != MODEL or response.get("done") is not True:
            status = "HARNESS_ERROR"
        else:
            status = "SUCCESS" if correct(response.get("response", ""), case["integers"]) else "ORACLE_FAIL"
        grader = time.perf_counter_ns() - g0
        return {"status": status, "request_payload": payload, "provider_response": response,
                "request_elapsed_ns": elapsed, "grader_elapsed_ns": grader,
                "snapshot_before": before, "snapshot_after": local_model(), "synthetic": False}
    except (OSError, ValueError, urllib.error.URLError) as exc:
        return {"status": "PROVIDER_UNAVAILABLE", "error": str(exc),
                "request_elapsed_ns": time.perf_counter_ns() - start, "synthetic": False}


def validate(plan, records):
    errors = []
    ids = [r["case"]["run_id"] for r in records]
    if len(set(ids)) != len(ids):
        errors.append("duplicate run IDs")
    cases = {c["run_id"]: c for c in plan["cases"]}
    if set(ids) != set(cases):
        errors.append("missing or unexpected scheduled records")
    for r in records:
        if r["case"] != cases.get(r["case"]["run_id"]):
            errors.append("task/track/condition identity mismatch")
        if r["plan_sha256"] != digest(plan):
            errors.append("plan provenance mismatch")
        if plan["mode"] == "local" and r.get("status") in ("SUCCESS", "ORACLE_FAIL"):
            if r.get("snapshot_before") != plan["model_snapshot"] or r.get("snapshot_after") != plan["model_snapshot"]:
                errors.append("snapshot mismatch")
        if r["status"] == "HARNESS_ERROR":
            errors.append("harness error")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("local", "fault"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    model = local_model() if args.mode == "local" else None
    runtime = request("/api/version") if args.mode == "local" else {"kind": "synthetic_python_no_provider"}
    plan = make_plan(args.mode, model, runtime)
    plan["runner_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    write_new(args.output / "PLAN.json", plan)  # frozen before any inference
    records = []
    for case in plan["cases"]:
        record = {"case": case, "plan_sha256": digest(plan), "started_utc": utc()}
        record.update(infer(case, plan) if args.mode == "local" else synthetic(case, plan))
        record["finished_utc"] = utc()
        write_new(args.output / (case["run_id"] + ".json"), record)
        records.append(record)
        print(f"{len(records)}/{len(plan['cases'])} {record['status']}", flush=True)
    errors = validate(plan, records)
    grouped = defaultdict(Counter)
    for r in records:
        c = r["case"]
        key = (f"{c['scenario']}|retry={c['retry_limit']}|latency_ms={c['latency_ms']}"
               if args.mode == "fault" else "local_integer_sum")
        grouped[key][r["status"]] += 1
    summary = {"scope": plan["scope"], "planned": len(plan["cases"]), "recorded": len(records),
               "status_counts": dict(Counter(r["status"] for r in records)),
               "identity_gate_errors": errors, "eligible_for_benign_control_only": not errors,
               "model_snapshot": model, "runtime": runtime, "plan_sha256": digest(plan),
               "per_condition": dict(grouped), "security_campaign_complete": False,
               "median_request_ms": statistics.median(r.get("request_elapsed_ns", 0) for r in records) / 1e6,
               "median_grader_ms": statistics.median(r.get("grader_elapsed_ns", 0) for r in records) / 1e6,
               "file_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(args.output.glob("*.json"))}}
    write_new(args.output / "SUMMARY.json", summary)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
