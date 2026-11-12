import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "sp2027/analysis/checkpoint007_active_experiments/runs_009"
OUT = Path(__file__).resolve().parent / "exploratory_code_feedback_20261017"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_code_feedback_exploration import extract_action, policy_check, oracle_candidate
sys.path.insert(0, str(RUNS))
from h1_campaign import ecdsa_instance


def main():
    rows = []
    for path in sorted((OUT / "raw_provider_responses").glob("*.json")):
        d = json.loads(path.read_text())
        text = "\n".join(x.get("text", "") for x in d.get("content", []) if isinstance(x, dict))
        action = extract_action(text)
        seed = int(path.name.split("__seed_")[1].split("__")[0])
        public, truth = ecdsa_instance(seed)
        row = {"raw_response": str(path), "seed": seed, "turn": int(path.name.rsplit("__turn", 1)[1].split(".")[0]), "action_present": bool(action)}
        if not action:
            row["stage"] = "action_parse_failed"
            rows.append(row); continue
        code = action["code"]
        allowed, policy = policy_check(code)
        row["policy"] = policy
        if not allowed:
            row["stage"] = "static_policy_rejected"
            rows.append(row); continue
        with tempfile.TemporaryDirectory(prefix="acts_code_feedback_audit_") as td:
            public_path = Path(td) / "public.json"
            public_path.write_text(json.dumps({"public_input": public}, sort_keys=True))
            code_path = Path(td) / "agent.py"
            code_path.write_text(code)
            proc = subprocess.run([sys.executable, "-I", str(code_path), str(public_path)], cwd=td, env={"PATH": "/usr/bin:/bin", "PYTHONPATH": ""}, capture_output=True, text=True, timeout=20)
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
            row["returncode"] = proc.returncode
            row["stdout_nonempty"] = bool(stdout)
            row["stderr_nonempty"] = bool(stderr)
            row["stderr_class"] = "none" if not stderr else ("key_error" if "KeyError" in stderr else "name_error" if "NameError" in stderr else "value_error" if "ValueError" in stderr else "other_runtime_error")
            try:
                candidate = json.loads(stdout.splitlines()[-1]) if stdout else None
            except (ValueError, IndexError):
                candidate = None
            row["candidate_json"] = isinstance(candidate, dict)
            if proc.returncode != 0 or not isinstance(candidate, dict):
                row["stage"] = "execution_or_candidate_parse_failed"
            elif oracle_candidate(public, candidate, truth):
                row["stage"] = "oracle_accepted"
            else:
                row["stage"] = "oracle_rejected_candidate"
        rows.append(row)
    (OUT / "failure_stage_matrix.json").write_text(json.dumps(rows, indent=2) + "\n")
    counts = {}
    for row in rows: counts[row["stage"]] = counts.get(row["stage"], 0) + 1
    summary = {"rows": len(rows), "stage_counts": counts, "interpretation": "Both sessions reached code execution but failed before oracle acceptance; the stage matrix distinguishes runtime/claim failures from a provider or action-format failure."}
    (OUT / "failure_stage_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
