import ast
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
DRIVER = ROOT / "sp2027/analysis/e3_rig_driver.py"
RESUME = ROOT / "sp2027/analysis/e3_rig_resume.py"
RAW = ROOT / "sp2027/analysis/e3_rig/samples_full.jsonl"
ENV = ROOT / "sp2027/analysis/e3_rig/e3_rig_env.json"


def call_name(node):
    if not isinstance(node, ast.Call):
        return None
    return node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else None


def block_facts(tree):
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    loops = [n for n in ast.walk(main) if isinstance(n, ast.For) and isinstance(n.target, ast.Name) and n.target.id == "smt"]
    result = []
    for loop in loops:
        calls = [(n.lineno, call_name(n)) for n in ast.walk(loop) if isinstance(n, ast.Call)]
        result.append({"loop_line": loop.lineno, "toggle_lines": [line for line, name in calls if name == "apply_smt"],
                       "trial_lines": [line for line, name in calls if name == "one_trial"]})
    return result


def main():
    source = DRIVER.read_text()
    tree = ast.parse(source)
    constants = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
                 if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("VULN_SRC", "CT_SRC")}
    initial = block_facts(tree)
    resumed = block_facts(ast.parse(RESUME.read_text()))
    trials = [json.loads(line) for line in RAW.open()]
    env = json.loads(ENV.read_text())
    prefix = env["original_run"]["flushed_trials_before_resume"]
    checks = {"two_20000_iteration_programs": all("(s, 20000)" in s for s in constants.values()),
              "indexed_lookup_vs_256_entry_scan": "T[b]" in constants["VULN_SRC"] and "i < 256" in constants["CT_SRC"],
              "drop_filesystem_caches_command": "sync; echo 3 > /proc/sys/vm/drop_caches" in source,
              "initial_trial_loop_has_no_toggle": any(b["trial_lines"] and not b["toggle_lines"] for b in initial),
              "initial_prepare_loop_has_toggle": any(b["toggle_lines"] and not b["trial_lines"] for b in initial),
              "resume_toggles_inside_block": any(b["toggle_lines"] and b["trial_lines"] and max(b["toggle_lines"]) < min(b["trial_lines"]) for b in resumed),
              "prefix_count_15971": prefix == 15971,
              "trial_indices_in_order": [r["trial_idx"] for r in trials] == list(range(32000)),
              "no_raw_per_trial_actual_state": all("actual_state" not in r and "smt_actual" not in r for r in trials)}
    result = {"scope": "Static retained-source and recorded-label trace; no timing or hardware operation executed",
              "checks": checks, "all_pass": all(checks.values()),
              "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (DRIVER, RESUME, RAW, ENV)},
              "initial_source_block_facts": initial, "resume_source_block_facts": resumed,
              "prefix_recorded_smt_labels": dict(Counter(r["smt_block"] for r in trials[:prefix])),
              "suffix_recorded_smt_labels": dict(Counter(r["smt_block"] for r in trials[prefix:])),
              "interpretation": "Retained source contains a preparation/execution toggle placement defect. Matching trial-order labels and resumed aggregate metadata do not establish actual hardware state throughout the original prefix. Historical runtime source identity is not independently recovered."}
    (OUT / "CONDITION_TRACE.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": len(checks), "all_pass": result["all_pass"], "prefix_labels": result["prefix_recorded_smt_labels"], "suffix_labels": result["suffix_recorded_smt_labels"]}))
    if not result["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
