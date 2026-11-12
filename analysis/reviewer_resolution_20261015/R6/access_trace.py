import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def main():
    escrow = ROOT / "ACTS-ATTACK/targets/e5/escrow.py"
    loop = ROOT / "ACTS-ATTACK/harness/v2/agent_loop_v2.py"
    launch = ROOT / "ACTS-ATTACK/targets/e5/e5_session.py"
    handler = next(n for n in ast.parse(escrow.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "Handler")
    fields = [n.args[0].value for n in ast.walk(handler) if isinstance(n, ast.Call)
              and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
              and n.func.value.id == "req" and n.func.attr == "get"
              and n.args and isinstance(n.args[0], ast.Constant)]
    dispatch = [n.func.attr for n in ast.walk(handler) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Attribute)
                and n.func.value.attr == "escrow"]
    run = next(n for n in ast.walk(ast.parse(loop.read_text())) if isinstance(n, ast.FunctionDef) and n.name == "_run_once")
    popen = [n for n in ast.walk(run) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "Popen"]
    checks = {"handler_reads_operation_and_candidate": set(fields) == {"op", "candidate_hex"},
              "handler_dispatches_delivery_compare_reveal": set(dispatch) == {"send_key", "verify", "reveal"},
              "generated_code_uses_host_popen": len(popen) == 1,
              "inherits_environment_and_cwd": len(popen) == 1 and not {"env", "cwd"}.intersection(k.arg for k in popen[0].keywords),
              "launcher_binds_all_interfaces": '"0.0.0.0"' in launch.read_text()}
    result = {"scope": "Static source trace; no network or service execution", "checks": checks,
              "all_pass": all(checks.values()), "handler_fields": fields, "handler_escrow_calls": dispatch,
              "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (escrow, loop, launch)}}
    (OUT / "ACCESS_TRACE.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": len(checks), "all_pass": result["all_pass"]}))
    if not result["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
