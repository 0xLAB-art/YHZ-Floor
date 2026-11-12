#!/usr/bin/env python3
"""Offline triple regrade — Amendment 4 (frozen analysis input).

Reads the retained programs from the frozen session run and produces the
per-program record consumed by `regrade_amend4_contrast.py`:

  declared  = rule_a_permissive_v4.qualify_source(src, "v3")
  stress    = rule_b_stress_legacy_repaired.qualify_source(src, "legacy")
  cleanup   = stress.qualify_source(transform(src), "legacy")
  output_preserved = byte-identical stdout of (src, cleaned) on a fresh copy
                     of the task's declared artifacts; no eligible edit => True.

Per-program oracle labels are carried under BOTH registered codings:
  oracle_match    = C1 (registered primary: whole stripped stdout == pin)
  oracle_match_c2 = C2 (second admissible normalization: first flag-shaped
                    token == pin)
both read verbatim from the session turn records.

No model call; local program execution only. Deterministic input ordering.
"""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results.jsonl"
FIXTURES = HERE / "fixtures" / "tasks"
OUT = HERE / "regrade_results_amend4.json"
DECLARED = HERE / "policies_amend4/rule_a_permissive_v4.py"
STRESS = HERE / "policies_amend4/rule_b_stress_legacy_repaired.py"
CLEANUP = HERE / "policies_amend4/rule_c_cleanup.py"
EXEC_TIMEOUT_S = 30


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    return sha_bytes(Path(path).read_bytes())


def run_once(source, task, root):
    workdir = Path(tempfile.mkdtemp(prefix="amend4_cmp_", dir=root))
    (workdir / "prog.py").write_text(source)
    for artifact in sorted(FIXTURES.joinpath(task).iterdir()):
        if artifact.is_file():
            shutil.copyfile(artifact, workdir / artifact.name)
    try:
        proc = subprocess.run([sys.executable, "-I", "prog.py"], cwd=workdir,
                              capture_output=True, timeout=EXEC_TIMEOUT_S)
        return {"stdout": proc.stdout, "returncode": proc.returncode,
                "timed_out": False, "error": None}
    except subprocess.TimeoutExpired:
        return {"stdout": b"", "returncode": None, "timed_out": True,
                "error": "timeout"}
    except Exception as exc:
        return {"stdout": b"", "returncode": None, "timed_out": False,
                "error": f"{type(exc).__name__}: {exc}"}


def main():
    declared = load(DECLARED, "amend4_declared_v4")
    stress = load(STRESS, "amend4_stress_legacy_repaired")
    cleanup = load(CLEANUP, "amend4_cleanup")

    rows = [json.loads(line) for line in RESULTS.read_text().splitlines()
            if line.strip()]
    records, verified, preserved_true, preserved_false = [], 0, 0, 0
    root = Path("/tmp/amend4_regrade_cmp")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    for session in rows:
        turn_map = {rec["turn"]: rec for rec in session.get("turn_records", [])}
        for program in session.get("programs", []):
            path = HERE / program["path"]
            source = path.read_text(encoding="utf-8")
            if sha_bytes(source.encode()) != program["sha256"]:
                raise SystemExit(f"PROGRAM HASH MISMATCH: {program['path']}")
            verified += 1
            turn_rec = turn_map.get(program["turn"], {})
            declared_dec = declared.qualify_source(source, "v3")
            stress_dec = stress.qualify_source(source, "legacy")
            cleaned, edits, imports, dynamic = cleanup.transform(
                source, {"json", "sys", "base64"})
            cleanup_dec = stress.qualify_source(cleaned, "legacy")
            if cleaned == source:
                output_preserved = True
                cmp_note = "no eligible edit; source identical"
                orig = clean = {"stdout": b"", "returncode": None,
                                "timed_out": False, "error": None}
            else:
                orig = run_once(source, session["task_id"], root)
                clean = run_once(cleaned, session["task_id"], root)
                output_preserved = (orig["stdout"] == clean["stdout"]
                                    and orig["timed_out"] == clean["timed_out"])
                cmp_note = ("byte-identical stdout" if output_preserved
                            else "stdout/timeout divergence")
            if output_preserved:
                preserved_true += 1
            else:
                preserved_false += 1
            records.append({
                "label": session["label"],
                "task_id": session["task_id"],
                "representation": session["representation"],
                "seed": session["seed"],
                "turn": program["turn"],
                "program": program["path"],
                "program_sha256": program["sha256"],
                "oracle_match": bool(turn_rec.get("oracle_match")),
                "oracle_match_c2": bool(turn_rec.get("oracle_match_c2")),
                "declared_v4": declared_dec["qualified"],
                "declared_v4_violations": declared_dec["violations"],
                "stress_repaired": stress_dec["qualified"],
                "stress_violations": stress_dec["violations"],
                "cleanup_qualified": cleanup_dec["qualified"],
                "cleanup_edits": len(edits),
                "cleanup_dynamic": dynamic,
                "output_preserved": output_preserved,
                "compare_note": cmp_note,
                "orig_returncode": orig["returncode"],
                "clean_returncode": clean["returncode"],
                "orig_timed_out": orig["timed_out"],
                "clean_timed_out": clean["timed_out"],
            })

    payload = {
        "schema": "external-admission-amend4-regrade/1",
        "namespace": "external_admission_amend4_frontier_20261106",
        "protocol": "PHASE2-EXTERNAL-ADMISSION-AMEND4-FRONTIER-v1",
        "generated_date": "2026-11-06",
        "inputs_sha256": {
            "results": sha_file(RESULTS),
            "declared_policy": sha_file(DECLARED),
            "stress_policy": sha_file(STRESS),
            "cleanup_policy": sha_file(CLEANUP),
        },
        "gates": {"program_hashes_verified": verified,
                  "programs": len(records)},
        "totals": {
            "sessions": len(rows),
            "programs": len(records),
            "oracle_correct_programs_c1": sum(1 for r in records if r["oracle_match"]),
            "oracle_correct_programs_c2": sum(1 for r in records if r["oracle_match_c2"]),
            "declared_qualified": sum(1 for r in records if r["declared_v4"]),
            "stress_qualified": sum(1 for r in records if r["stress_repaired"]),
            "cleanup_qualified": sum(1 for r in records if r["cleanup_qualified"]),
            "output_preserved_true": preserved_true,
            "output_preserved_false": preserved_false,
        },
        "per_program": records,
        "boundaries": {
            "offline": True,
            "no_model_call": True,
            "no_new_sessions": True,
            "cleanup_compare_timeout_s": EXEC_TIMEOUT_S,
            "no_benchmark_quality_claim": True,
        },
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["totals"], indent=2))
    print("->", OUT)


if __name__ == "__main__":
    main()
