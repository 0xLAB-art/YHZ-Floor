import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def main():
    source_path = ROOT / "sp2027/analysis/e3_gate_check.py"
    gate_path = ROOT / "sp2027/analysis/e3_rig/gate_verdict.json"
    tree = ast.parse(source_path.read_text())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "welch_t"]
    arguments = [[ast.unparse(a) for a in call.args] for call in calls]
    gate = json.loads(gate_path.read_text())
    checks = {"control_fixed_vs_random": ["samples['ct_fix']", "samples['ct_rand']"] in arguments,
              "canary_is_cross_build": ["samples['vuln_spot']", "samples['ct_rand']"] in arguments,
              "no_vulnerable_random_class": "vuln_rand" not in source_path.read_text(),
              "retained_control_classes_60_each": gate["n_fix"] == gate["n_rand"] == 60,
              "no_class_samples_in_verdict": "samples" not in gate}
    result = {"checks": checks, "all_pass": all(checks.values()), "welch_arguments": arguments,
              "historical_verdict": gate["verdict"], "control_p": gate["p_ct"],
              "canary_p_as_recorded": gate["canary_p_vuln"],
              "interpretation": "Cross-build runtime canary and failure to reject control seed difference are insufficient for leakage-sensitivity or constant-time assurance. No test or new trial executed.",
              "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (source_path, gate_path)}}
    (OUT / "GATE_TRACE.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": len(checks), "all_pass": result["all_pass"]}))
    if not result["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
