import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def main():
    base = ROOT / "sp2027/agent-eval/runs_r1_clean_capture_first_v4_claude46_20261014_02"
    paths = sorted(base.glob("q*.json"))
    records = [json.loads(p.read_text()) for p in paths]
    total = Counter(r["task_card"]["task_id"] for r in records)
    accepted = Counter(r["task_card"]["task_id"] for r in records if r["oracle"]["verdict"]["success"] is True)
    if len(records) != 12 or len({r["run_id"] for r in records}) != 12 or sorted(total.values()) != [3, 3, 3, 3] or sum(accepted.values()) != 8:
        raise ValueError("Fixed cohort identity or task census changed")
    result = {"population": "The twelve retained sessions on four fixed tasks, three per task",
              "counts": {task: {"retained": n, "accepted": accepted[task]} for task, n in sorted(total.items())},
              "accepted": 8, "retained": 12, "observed_fraction": 8/12,
              "sampling_target": "No exchangeable Bernoulli or future-task sampling target asserted",
              "confidence_interval": None,
              "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (OUT / "COHORT_DESCRIPTION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"retained": 12, "accepted": 8, "task_counts": result["counts"], "confidence_interval": None}))


if __name__ == "__main__":
    main()
