#!/usr/bin/env python3
"""Criterion-5 reference-solve runner — Amendment 3 (DRAFT 2026-11-05).

Offline harness, $0, zero model calls.  For each candidate task:

  1. reads the pinned challenge.json (oracle side; never copied into the
     solver fixture),
  2. materializes ONLY the declared handout files into a fresh directory
     (flattened to basenames; the artifact-name policy is registered in the
     preregistration),
  3. runs the stdlib-only reference solver with that directory as CWD,
     wall-clock capped,
  4. compares stdout (stripped) to the pinned answer byte-exactly,
  5. statically checks the solver source with the FROZEN declared-arm policy
     (v4 module, policy 'v3') and the amended-3 stress-arm pairing, and
     asserts that the pinned answer bytes do not occur in the solver source.

Output: reference_solve_run.jsonl (Phase-2 schema + verification fields).
"""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/mnt/nvme5/ACTS-Attack")
PIN = Path("/tmp/opencode/nyu_pin")
SCRATCH = Path("/tmp/opencode/refsolve")
OUT = HERE / "reference_solve_run.jsonl"

DECLARED_POLICY = REPO / "sp2027/research_execution/external_admission_amend2_20261029/policies/rule_a_permissive_v4.py"
STRESS_POLICY = REPO / "sp2027/research_execution/external_admission_amend3_20261105/policies_amend3_draft/rule_b_stress_legacy_repaired.py"

TASKS = [
    # task_id (NYU manifest id), path in pin, solver, expected answer source
    ("2017q-cry-almost_xor", "test/2017/CSAW-Quals/crypto/almost_xor", "solve_almost_xor.py"),
    ("2017q-cry-another_xor", "test/2017/CSAW-Quals/crypto/another_xor", "solve_another_xor.py"),
    ("2018q-cry-babycrypto", "test/2018/CSAW-Quals/crypto/babycrypto", "solve_babycrypto.py"),
    ("2018q-cry-lowe", "test/2018/CSAW-Quals/crypto/lowe", "solve_lowe.py"),
    ("2021q-cry-crack_me", "test/2021/CSAW-Quals/crypto/Crack-Me", "solve_crackme.py"),
    ("2019q-cry-des2bites", "test/2019/CSAW-Quals/crypto/DES2Bites", "solve_des2bites.py"),
    ("2015q-cry-eps", "development/2015/CSAW-Quals/crypto/eps", "solve_eps.py"),
    ("2015q-cry-eps_part2", "development/2015/CSAW-Quals/crypto/eps_part2", "solve_eps_part2.py"),
]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    declared = load_module(DECLARED_POLICY, "policy_declared_v4")
    stress = load_module(STRESS_POLICY, "policy_stress_amend3")
    records = []
    for task_id, rel, solver_name in TASKS:
        task_dir = PIN / rel
        meta = json.loads((task_dir / "challenge.json").read_text(encoding="utf-8"))
        answer = meta["flag"]
        declared_files = meta.get("files") or []
        solver_path = HERE / solver_name
        record = {
            "task_id": task_id,
            "path_in_pin": rel,
            "solver": str(solver_path.relative_to(HERE.parent)),
            "answer": answer,
            "declared_files": declared_files,
        }
        if not solver_path.exists():
            record.update({"output": None, "verdict": "NO_SOLVER",
                           "note": "criterion-5 probe not yet written"})
            records.append(record)
            continue

        source = solver_path.read_text(encoding="utf-8")
        record["solver_sha256"] = hashlib.sha256(source.encode()).hexdigest()
        record["solver_chars"] = len(source)
        record["est_tokens_chars_div4"] = len(source) // 4
        record["within_1600_token_budget_estimate"] = (len(source) // 4) <= 1600
        record["answer_bytes_in_solver_source"] = answer.encode() in source.encode()
        record["declared_arm"] = declared.qualify_source(source, "v3")
        record["stress_arm"] = stress.qualify_source(source, "legacy")

        fixture = SCRATCH / task_id
        if fixture.exists():
            shutil.rmtree(fixture)
        fixture.mkdir(parents=True)
        flat = {}
        for rel_file in declared_files:
            src = task_dir / rel_file
            if not src.exists():
                flat[rel_file] = None
                continue
            name = Path(rel_file).name
            shutil.copyfile(src, fixture / name)
            flat[rel_file] = name
        record["materialized"] = flat

        try:
            proc = subprocess.run(
                [sys.executable, str(solver_path)],
                cwd=fixture, capture_output=True, text=True, timeout=600)
            output = proc.stdout.strip()
            record["output"] = output
            record["exit_code"] = proc.returncode
            record["stderr_tail"] = proc.stderr.strip()[-500:]
            record["verdict"] = "MATCH" if output == answer else "MISMATCH"
        except subprocess.TimeoutExpired:
            record["output"] = None
            record["exit_code"] = "TIMEOUT"
            record["verdict"] = "TIMEOUT"
        records.append(record)
        print(f"{task_id}: {record['verdict']}"
              f" | declared={record['declared_arm']['status']}"
              f" | answer-in-source={record['answer_bytes_in_solver_source']}")

    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
                   encoding="utf-8")
    summary = {
        "tasks": len(records),
        "MATCH": sum(1 for r in records if r["verdict"] == "MATCH"),
        "MISMATCH": sum(1 for r in records if r["verdict"] == "MISMATCH"),
        "NO_SOLVER": sum(1 for r in records if r["verdict"] == "NO_SOLVER"),
        "declared_arm_qualified": sum(1 for r in records
                                      if r.get("declared_arm", {}).get("qualified")),
        "answer_bytes_in_any_source": sum(1 for r in records
                                          if r.get("answer_bytes_in_solver_source")),
        "out": str(OUT),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
