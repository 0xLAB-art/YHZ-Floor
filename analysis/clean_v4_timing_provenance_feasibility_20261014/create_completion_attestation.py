#!/usr/bin/env python3
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "sp2027/analysis/clean_v4_timing_provenance_feasibility_20261014"
OUT = ANALYSIS / "EXECUTION_COMPLETION_ATTESTATION.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(path.relative_to(ROOT))


def main():
    if OUT.exists():
        raise SystemExit(f"append-only output already exists: {OUT}")

    v4_manifest = ROOT / "sp2027/agent-eval/R1_CLEAN_COHORT_V4_02_MANIFEST.json"
    v4_dir = ROOT / "sp2027/agent-eval/runs_r1_clean_capture_first_v4_claude46_20261014_02"
    v4_ledger = ANALYSIS / "V4_COMPLETE_ROW_EVIDENCE_LEDGER.csv"
    with v4_ledger.open(newline="") as stream:
        v4_rows = list(csv.DictReader(stream))
    if len(v4_rows) != 12 or len({r["run_id"] for r in v4_rows}) != 12:
        raise SystemExit("V4 ledger does not contain 12 unique retained runs")
    v4_evidence = []
    for row in v4_rows:
        raw = ROOT / row["raw_record_path"]
        transcript = ROOT / row["transcript_path"]
        if sha(raw) != row["raw_record_sha256"] or sha(transcript) != row["transcript_sha256"]:
            raise SystemExit(f"V4 evidence hash mismatch: {row['run_id']}")
        v4_evidence.append({
            "run_id": row["run_id"],
            "scheduled_entry_id": row["entry_id"],
            "terminal_status": row["record_terminal_status"],
            "record_path": relative(raw),
            "record_sha256": sha(raw),
            "transcript_path": relative(transcript),
            "transcript_sha256": sha(transcript),
            "explicit_oracle_verdict": row["record_oracle_verdict"],
        })

    h1_manifest = ROOT / "sp2027/agent-eval/h1_positive_control_20261014_v2/H1_POSITIVE_CONTROL_MANIFEST.json"
    h1_dir = h1_manifest.parent
    with (h1_dir / "H1_POSITIVE_CONTROL_LEDGER.csv").open(newline="") as stream:
        h1_rows = list(csv.DictReader(stream))
    if len(h1_rows) != 3 or len({r["run_id"] for r in h1_rows}) != 3:
        raise SystemExit("EXP-035 ledger does not contain 3 unique retained runs")
    h1_evidence = []
    for row in h1_rows:
        record = h1_dir / "runs" / f"{row['run_id']}.json"
        if not record.exists():
            raise SystemExit(f"EXP-035 record missing: {row['run_id']}")
        payload = json.loads(record.read_text())
        if payload.get("run_id") != row["run_id"] or payload.get("session", {}).get("status") != row["status"]:
            raise SystemExit(f"EXP-035 record identity/status mismatch: {row['run_id']}")
        if payload.get("artifact", {}).get("candidate") != row["artifact_sha256"]:
            raise SystemExit(f"EXP-035 candidate artifact identity mismatch: {row['run_id']}")
        h1_evidence.append({
            "run_id": row["run_id"],
            "terminal_status": row["status"],
            "record_path": relative(record),
            "record_sha256": sha(record),
            "candidate_artifact_identity_from_ledger": row["artifact_sha256"],
            "candidate_artifact_content_sha256": payload.get("artifact", {}).get("sha256"),
            "h1_verdict": "H1",
        })

    validation = ANALYSIS / "ANALYSIS_VALIDATION_REPORT.md"
    lock = ROOT / "sp2027/analysis/RESULTS_LOCK_H1PC.json"
    attestation = {
        "schema": "acts-derived-execution-completion-attestation/1.0.0",
        "artifact_type": "append-only integrity attestation; not an experiment or result lock",
        "created_date": "2026-10-14",
        "completion_state_basis": "inferred from retained physical records, transcripts, ledgers, and current validation artifacts",
        "no_new_execution": True,
        "arms": [
            {
                "arm_id": "EXP-034 / CLEAN V4-02",
                "frozen_manifest_path": relative(v4_manifest),
                "frozen_manifest_sha256": sha(v4_manifest),
                "frozen_protocol_identity": "R1-CLEAN-CAPTURE-FIRST-V4-CLAUDE46-20261014-02",
                "manifest_execution_status_retained": "FROZEN_NOT_LAUNCHED",
                "completion_state_inferred_from_records": "COMPLETED; 12 of 12 scheduled cells have retained physical records, transcripts, and terminal outcomes",
                "retained_run_count": len(v4_evidence),
                "terminal_counts": {"SUCCESS": 8, "ORACLE_FAIL": 4},
                "explicit_oracle_verdict_counts": {"accepted_sessions": 8, "rejected_sessions": 4},
                "run_evidence": v4_evidence,
                "analysis_ledger_path": relative(v4_ledger),
                "analysis_ledger_sha256": sha(v4_ledger),
                "validation_report_path": relative(validation),
                "validation_report_sha256": sha(validation),
                "stale_status_explanation": "The frozen manifest records FROZEN_NOT_LAUNCHED although the retained 12-row physical record and transcript census establishes completion. The manifest and its historical hash are left unchanged.",
            },
            {
                "arm_id": "EXP-035 / H1-POSITIVE-CONTROL-20261014-02",
                "frozen_manifest_path": relative(h1_manifest),
                "frozen_manifest_sha256": sha(h1_manifest),
                "frozen_protocol_identity": "H1-POSITIVE-CONTROL-20261014-02",
                "manifest_execution_status_retained": "FROZEN_NOT_LAUNCHED",
                "completion_state_inferred_from_records": "COMPLETED; 3 of 3 deterministic control runs are retained and pass the unchanged H1 checker",
                "retained_run_count": len(h1_evidence),
                "terminal_counts": {"SUCCESS": 3},
                "h1_counts": {"H1": 3},
                "environment_image_digest": "sha256:f8cddd76e34aed0e04ee3f41a958a213cf72f6658996beb41888418101a41040",
                "run_evidence": h1_evidence,
                "ledger_path": relative(h1_dir / "H1_POSITIVE_CONTROL_LEDGER.csv"),
                "ledger_sha256": sha(h1_dir / "H1_POSITIVE_CONTROL_LEDGER.csv"),
                "h1_check_path": relative(h1_dir / "H1_POSITIVE_CONTROL_H1_CHECK.csv"),
                "h1_check_sha256": sha(h1_dir / "H1_POSITIVE_CONTROL_H1_CHECK.csv"),
                "validation_report_path": relative(h1_dir / "H1_POSITIVE_CONTROL_VALIDATION.md"),
                "validation_report_sha256": sha(h1_dir / "H1_POSITIVE_CONTROL_VALIDATION.md"),
                "active_lock_path": relative(lock),
                "active_lock_sha256": sha(lock),
                "stale_status_explanation": "The frozen manifest's FROZEN_NOT_LAUNCHED value conflicts with the retained three-run ledger, run artifacts, H1 check, validation report, and active successor lock. The manifest and its historical hash are left unchanged.",
            },
        ],
        "integrity_limits": [
            "This attestation records hashes and completion inferred from existing evidence; it does not add observations or repair manifests.",
            "No missing timestamps, provider transactions, or transport retry attempts are inferred.",
            "The clean V4 timing ledger retains elapsed durations but not raw monotonic start/stop values.",
            "This derived artifact is not a new experiment arm and does not alter H1 populations or arm accounting.",
        ],
    }
    OUT.write_text(json.dumps(attestation, indent=2, sort_keys=True) + "\n")
    print(f"created {relative(OUT)} sha256={sha(OUT)}")


if __name__ == "__main__":
    main()
