import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "sp2027/agent-eval/runs_r1_clean_capture_first_v4_claude46_20261014_02"
OUT = Path(__file__).resolve().parent


def main():
    rows = []
    for path in sorted(RUNS.glob("*.json")):
        d = json.loads(path.read_text())
        task = d["task_card"]
        model = d["model_config"]
        oracle = d["oracle"]["verdict"]
        session = d["session"]
        request = model.get("request_records") or []
        rows.append({
            "run_id": d["run_id"],
            "task_id": task["task_id"],
            "status": session["status"],
            "oracle_success": oracle["success"],
            "attempts": session["attempts"],
            "turns": session["turns"],
            "queries": session["queries"],
            "gave_up": session["gave_up"],
            "request_records": len(request),
            "submitted_turns": sum(1 for r in request if r.get("action") == "submit"),
            "response_chars_total": sum(int(r.get("response_chars", 0)) for r in request),
            "artifact_count": len(d.get("artifacts", [])),
            "separate_process_oracle": d["oracle"]["separate_process"],
            "oracle_queries": oracle["oracle_queries"],
            "oracle_hash": d["oracle"]["implementation_sha256"],
            "run_record": str(path),
        })
    rows.sort(key=lambda r: r["run_id"])
    with (OUT / "V4_TRAJECTORY_MATRIX.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    by_task = defaultdict(Counter)
    for r in rows:
        by_task[r["task_id"]][r["status"]] += 1
    summary = {
        "rows": len(rows),
        "status_counts": dict(Counter(r["status"] for r in rows)),
        "task_status_counts": {k: dict(v) for k, v in sorted(by_task.items())},
        "accepted_rows_with_explicit_oracle": sum(r["status"] == "SUCCESS" and r["oracle_success"] for r in rows),
        "oracle_failed_rows": sum(r["status"] == "ORACLE_FAIL" for r in rows),
        "program_submission_count": sum(r["submitted_turns"] for r in rows),
        "rows_with_separate_process_oracle": sum(r["separate_process_oracle"] for r in rows),
        "total_model_turns": sum(r["turns"] for r in rows),
        "total_attempts": sum(r["attempts"] for r in rows),
        "total_queries": sum(r["queries"] for r in rows),
        "interpretation": "V4 is a run-linked real-agent cohort with explicit task-specific oracle outcomes. The trajectory matrix describes what succeeded and failed; it does not identify a causal feedback effect because the cohort is not a matched feedback ablation.",
    }
    (OUT / "V4_TRAJECTORY_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    md = ["# Canonical V4 trajectory audit", "", "Status: `PARTIAL_EXECUTION`", "", "This audit reads the 12 retained namespace-02 run records and keeps task, model, program, and oracle fields linked by run ID.", "", "## Findings", "", f"- Rows: {summary['rows']}; statuses: {summary['status_counts']}; submitted-program records: {summary['program_submission_count']}.", f"- Explicit accepted oracle outcomes: {summary['accepted_rows_with_explicit_oracle']}; oracle-failed rows: {summary['oracle_failed_rows']}.", f"- Separate-process oracle records: {summary['rows_with_separate_process_oracle']}/12.", "- The accepted and failed rows are direct attack evidence under this V4 task contract. They are not pooled with deterministic executors, H1 V2, or other historical namespaces.", "- The cohort does not support a causal claim that feedback caused success; a matched no-feedback intervention is absent.", "", "## Per-task status", ""]
    for task, counts in summary["task_status_counts"].items():
        md.append(f"- `{task}`: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    md += ["", "The complete row-level matrix is `V4_TRAJECTORY_MATRIX.csv`."]
    (OUT / "V4_TRAJECTORY_AUDIT.md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
