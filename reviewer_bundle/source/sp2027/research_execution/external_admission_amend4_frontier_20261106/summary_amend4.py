#!/usr/bin/env python3
"""Amendment-4 headline summary — the numbers the paper's §7/appendix quote.
Reads results.jsonl (primary) and results_recovery_8400.jsonl (if present,
reported separately, never mixed).  Writes SUMMARY_AMEND4.json.
"""
import json
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parent


def summarize(path, wave):
    if not path.exists():
        return None
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    s = {
        "wave": wave,
        "sessions": len(rows),
        "by_label": dict(collections.Counter(r["label"] for r in rows)),
        "by_status": dict(collections.Counter(r["status"] for r in rows)),
        "acceptances_c1": sum(1 for r in rows if r.get("accepted")),
        "acceptances_c2": sum(1 for r in rows if r.get("accepted_c2")),
        "provider_attempts": sum(r.get("provider_attempts", 0) for r in rows),
        "floor_exhausted_giveups": sum(
            1 for r in rows if r["status"] == "AGENT_GIVEUP"),
        "cells": {},
    }
    for r in rows:
        key = (r["label"], r["task_id"].split("cry-")[-1], r["representation"])
        cell = s["cells"].setdefault(key, {"n": 0, "c1": 0, "c2": 0,
                                           "statuses": collections.Counter()})
        cell["n"] += 1
        cell["c1"] += 1 if r.get("accepted") else 0
        cell["c2"] += 1 if r.get("accepted_c2") else 0
        cell["statuses"][r["status"]] += 1
    s["cells"] = {f"{k[0]}|{k[1]}|{k[2]}": {
        "n": v["n"], "c1": v["c1"], "c2": v["c2"],
        "statuses": dict(v["statuses"])} for k, v in sorted(s["cells"].items())}
    led = Path("/mnt/nvme5/ACTS-Attack/sp2027/research_execution/BUDGET_LEDGER.jsonl")
    if led.exists():
        lines = [json.loads(l) for l in led.read_text().splitlines() if l.strip()]
        cls = "recovery call" if wave == "recovery_8400" else "experiment call"
        mine = [l for l in lines
                if l.get("namespace") == "external_admission_amend4_frontier_20261106"
                and l.get("classification") == cls]
        s["tokens"] = {"input": sum(l.get("input_tokens", 0) for l in mine),
                       "output": sum(l.get("output_tokens", 0) for l in mine),
                       "calls": len(mine)}
    return s


out = {"schema": "external-admission-amend4-summary/1",
       "primary_floor_4200": summarize(HERE / "results.jsonl", "primary_4200"),
       "recovery_floor_8400": summarize(HERE / "results_recovery_8400.jsonl",
                                        "recovery_8400"),
       "boundary": ("primary and recovery floors are reported side by side; "
                    "never pooled; acceptance is C1; C2 is the second "
                    "admissible normalization")}
(HERE / "SUMMARY_AMEND4.json").write_text(json.dumps(out, indent=1))
p = out["primary_floor_4200"]
print(json.dumps({k: p[k] for k in ("sessions", "by_status", "acceptances_c1",
                                    "acceptances_c2")}, indent=1) if p else "no primary rows")
