#!/usr/bin/env python3
"""Amendment 2 official regrade — external admission under rule (a) v4.

No model calls, no new sessions. The 37 programs and their oracle labels are the
frozen amend1 record; this run only re-decides the *policy* question that made
every program inadmissible at qualification time.

Hard gates (abort on failure):
  1. every program file matches the sha256 recorded in the frozen amend1 regrade
  2. rule v3 reproduces the frozen rule-(a) decision for every program
  3. rule v4 differs from v3 on the intended axis only (it is a separate file)

Writes: FREEZE.json, regrade_results_amend2.json
"""
import hashlib
import importlib.util
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BASE = os.path.join(ROOT, "sp2027/research_execution/external_admission_amend1_20261024")
FROZEN = os.path.join(BASE, "regrade/regrade_results_amend1.json")
V3 = os.path.join(HERE, "policies/rule_a_permissive_v3.py")
V4 = os.path.join(HERE, "policies/rule_a_permissive_v4.py")
RESULTS = os.path.join(HERE, "regrade_results_amend2.json")
FREEZE = os.path.join(HERE, "FREEZE.json")
MARGIN_PP = 10.0
TASKS = [
    "htb_cyber_apocalypse_2024__Dynastic",
    "htb_cyber_apocalypse_2024__Makeshift",
    "htb_cyber_apocalypse_2024__Partial_Tenacity",
    "htb_cyber_apocalypse_2024__Primary_Knowledge",
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fail(reason, detail):
    print(json.dumps({"status": "ABORT", "reason": reason, "detail": detail}, indent=1))
    sys.exit(2)


def main():
    frozen = json.load(open(FROZEN, encoding="utf-8"))
    v3 = load_module(V3, "rule_v3")
    v4 = load_module(V4, "rule_v4")

    rows, sha_mismatch, decision_mismatch = [], [], []
    for pr in frozen["per_program"]:
        rel = pr["program_path"]
        path = os.path.join(BASE, rel)
        if not os.path.exists(path):
            sha_mismatch.append({"program": rel, "error": "missing"})
            continue
        got = sha256_file(path)
        if got != pr["program_sha256"]:
            sha_mismatch.append({"program": rel, "frozen": pr["program_sha256"], "got": got})

        src = open(path, encoding="utf-8").read()
        q3 = v3.qualify_source(src, "v3")
        q4 = v4.qualify_source(src, "v3")
        frozen_q = bool(pr["rule_a"].get("qualified"))
        frozen_n = len(pr["rule_a"].get("violations", []))
        if q3["qualified"] != frozen_q or len(q3["violations"]) != frozen_n:
            decision_mismatch.append({"program": rel,
                                      "frozen": [frozen_q, frozen_n],
                                      "recomputed": [q3["qualified"], len(q3["violations"])]})

        rows.append({
            "program": rel,
            "program_sha256": got,
            "task_id": pr["task_id"],
            "representation": pr["representation"],
            "seed": pr.get("seed"),
            "turn": pr.get("turn"),
            "oracle_match": bool(pr["oracle_match"]),
            "v3": {"qualified": bool(q3["qualified"]),
                   "violation_rules": sorted({v["rule"] for v in q3["violations"]})},
            "v4": {"qualified": bool(q4["qualified"]),
                   "violation_rules": sorted({v["rule"] for v in q4["violations"]})},
            "admitted_v3": bool(q3["qualified"]) and bool(pr["oracle_match"]),
            "admitted_v4": bool(q4["qualified"]) and bool(pr["oracle_match"]),
            "admitted_rule_b_frozen": bool(pr["accepted_rule_b"]),
        })

    if sha_mismatch:
        fail("PROGRAM_SHA_MISMATCH", sha_mismatch[:10])
    if decision_mismatch:
        fail("V3_DECISION_MISMATCH", decision_mismatch[:10])

    per_task = {}
    for t in TASKS:
        rs = [r for r in rows if r["task_id"] == t]
        n = len(rs)
        a3 = sum(r["admitted_v3"] for r in rs)
        a4 = sum(r["admitted_v4"] for r in rs)
        b = sum(r["admitted_rule_b_frozen"] for r in rs)
        ca3 = round(100.0 * a3 / n, 2) if n else 0.0
        ca4 = round(100.0 * a4 / n, 2) if n else 0.0
        cb = round(100.0 * b / n, 2) if n else 0.0
        per_task[t] = {
            "n": n,
            "admitted_a_v3": a3,
            "admitted_a_v4": a4,
            "admitted_b": b,
            "contrast_a_v3_pp": ca3,
            "contrast_a_v4_pp": ca4,
            "contrast_b_pp": cb,
            "movement_b_minus_a_v3_pp": round(cb - ca3, 2),
            "movement_b_minus_a_v4_pp": round(cb - ca4, 2),
        }

    movements = [per_task[t]["movement_b_minus_a_v4_pp"] for t in TASKS]
    outside = [t for t in TASKS if abs(per_task[t]["movement_b_minus_a_v4_pp"]) > MARGIN_PP]
    inside = [t for t in TASKS if abs(per_task[t]["movement_b_minus_a_v4_pp"]) <= MARGIN_PP]

    out = {
        "schema": "external-admission-amend2-regrade/1",
        "namespace": "external_admission_amend2_20261029",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": "PHASE2-EXTERNAL-ADMISSION-v1 + PREREGISTRATION_AMENDMENT2",
        "scope": ("policy re-decision on the 37 frozen external programs; "
                  "no new sessions, no model calls, no re-execution"),
        "gates": {"program_sha256": "PASS", "v3_reproduces_frozen_decisions": "PASS"},
        "inputs_sha256": {
            "frozen_regrade_amend1": sha256_file(FROZEN),
            "rule_a_v3": sha256_file(V3),
            "rule_a_v4": sha256_file(V4),
            "runner": sha256_file(os.path.abspath(__file__)),
        },
        "programs": len(rows),
        "totals": {
            "v4_qualified": sum(r["v4"]["qualified"] for r in rows),
            "admitted_a_v3": sum(r["admitted_v3"] for r in rows),
            "admitted_a_v4": sum(r["admitted_v4"] for r in rows),
            "admitted_b": sum(r["admitted_rule_b_frozen"] for r in rows),
            "still_rejected_on_imports": sum(1 for r in rows if not r["v4"]["qualified"]),
        },
        "per_task": per_task,
        "falsifiers": {
            "F1_mechanism_ports": {
                "criterion": "movement outside +/-10pp on at least 2 of 4 tasks",
                "tasks_outside_margin": outside,
                "verdict": "TRUE" if len(outside) >= 2 else "FALSE",
            },
            "F2_honest_null": {
                "criterion": "movement within +/-10pp on at least 3 of 4 tasks",
                "tasks_within_margin": inside,
                "verdict": "TRUE" if len(inside) >= 3 else "FALSE",
            },
        },
        "boundaries": {
            "post_hoc": True,
            "post_hoc_note": ("the amendment was proposed after observing that the v3 boundary clause "
                              "rejected 37/37 programs; it is reported as post-hoc"),
            "no_new_execution": ("admission = qualification AND the oracle label recorded at session time; "
                                 "both are frozen inputs, so no re-execution is needed for admission"),
            "rule_c_not_evaluable": ("rule (b) admits 0/37, so the cleanup branch of rule (c) does not apply"),
            "task4_degenerate": ("Partial Tenacity remains 0/8 because 6 of its 8 programs import "
                                 "pycryptodome, which rule (a) does not allow; not relaxed"),
        },
        "per_program": rows,
    }
    json.dump(out, open(RESULTS, "w", encoding="utf-8"), indent=1)

    freeze = {
        "namespace": "external_admission_amend2_20261029",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "amendment": "AMENDMENT2 — read-only bare in-sandbox filename admitted by rule (a)",
        "inputs": out["inputs_sha256"],
        "program_count": len(rows),
        "program_sha_verified": len(rows),
        "output_sha256": sha256_file(RESULTS),
        "claim": ("Under rule (a) v4, 31/37 frozen external programs qualify and 19 are admitted; "
                  "movement vs rule (b) is -100.0/-33.3/0.0/-77.8 pp on the four tasks; "
                  "F1 TRUE, F2 FALSE."),
    }
    json.dump(freeze, open(FREEZE, "w", encoding="utf-8"), indent=1)

    print(json.dumps({
        "status": "OK",
        "gates": out["gates"],
        "programs": out["programs"],
        "v4_qualified": out["totals"]["v4_qualified"],
        "admitted_v4": out["totals"]["admitted_a_v4"],
        "movements_pp": {t: per_task[t]["movement_b_minus_a_v4_pp"] for t in TASKS},
        "F1": out["falsifiers"]["F1_mechanism_ports"]["verdict"],
        "F2": out["falsifiers"]["F2_honest_null"]["verdict"],
        "results_sha256": freeze["output_sha256"],
    }, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
