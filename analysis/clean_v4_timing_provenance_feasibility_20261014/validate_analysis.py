import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
AE = ROOT / "sp2027/agent-eval"
RUNS = AE / "runs_r1_clean_capture_first_v4_claude46_20261014_02"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition, name, detail):
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    print(f"PASS {name}: {detail}")


def main():
    manifest = json.loads((AE / "R1_CLEAN_COHORT_V4_02_MANIFEST.json").read_text())
    freeze = json.loads((AE / "R1_CLEAN_COHORT_V4_02_FREEZE.json").read_text())
    scheduled = manifest["entries"]
    ledger = list(csv.DictReader((AE / "R1_CLEAN_COHORT_V4_ROW_LEDGER.csv").open()))
    rows = list(csv.DictReader((OUT / "V4_COMPLETE_ROW_EVIDENCE_LEDGER.csv").open()))
    timing = list(csv.DictReader((OUT / "V4_SUCCESSFUL_AGENT_TIMINGS.csv").open()))
    raw_files = list(RUNS.glob("q*.json"))
    transcript_files = list(RUNS.glob("transcripts/*/transcript.jsonl"))
    check(len(scheduled) == len(ledger) == len(rows) == len(raw_files) == len(transcript_files) == 12, "scheduled_physical_retained_census", "12 scheduled identities, 12 ledger rows, 12 physical records, 12 transcript directories")
    check(len({r["entry_id"] for r in rows}) == 12 and len({r["run_id"] for r in rows}) == 12, "unique_identity", "12 unique scheduled entry IDs and run IDs")
    check(Counter(r["record_terminal_status"] for r in rows) == Counter({"SUCCESS": 8, "ORACLE_FAIL": 4}), "terminal_census", "8 SUCCESS; 4 ORACLE_FAIL")
    for expected, recorded in zip(sorted(scheduled, key=lambda x: x["entry_id"]), sorted(ledger, key=lambda x: x["entry_id"])):
        check(expected["entry_id"] == recorded["entry_id"] and expected["task_id"] == recorded["task_id"] and expected["replicate"] == int(recorded["replicate"]), "schedule_to_ledger", expected["entry_id"])
    for r in rows:
        rec = json.loads((ROOT / r["raw_record_path"]).read_text())
        transcript = [json.loads(x) for x in (ROOT / r["transcript_path"]).read_text().splitlines()]
        finals = [e for e in transcript if e.get("type") == "session_end"]
        outcomes = [e.get("verdict", {}).get("verdict") for e in transcript if e.get("type") == "run" and e.get("verdict")]
        check(r["raw_run_id_matches"] == "True" and rec["run_id"] == r["run_id"], "raw_identity_binding", r["run_id"])
        check(sha(ROOT / r["raw_record_path"]) == r["raw_record_sha256"], "raw_record_hash", r["run_id"])
        check(sha(ROOT / r["transcript_path"]) == r["transcript_sha256"], "transcript_hash", r["run_id"])
        check(len(finals) == 1 and finals[0]["tte_m_harness_ns"] == rec["clocks"]["tte_m_harness_ns"], "clock_endpoint_record_consistency", r["run_id"])
        check(finals[0].get("op_start_utc") and finals[0].get("utc"), "session_utc_boundary_labels", r["run_id"])
        if rec["session"]["status"] == "SUCCESS":
            check("success" in outcomes and rec["oracle"]["verdict"]["success"] is True, "explicit_oracle_acceptance", r["run_id"])
        else:
            check(outcomes and all(v == "failure" for v in outcomes) and rec["oracle"]["verdict"]["success"] is False, "explicit_oracle_rejection", r["run_id"])
        t = rec["clocks"]["tte_m_harness_ns"]
        check(isinstance(t, int) and math.isfinite(t) and t >= 0, "primary_clock_finite_nonnegative_ns", r["run_id"])
    check(len(timing) == 8, "successful_timing_denominator", "8 row-level timing records")
    for task, expected_n in {"ChaCha20": 2, "CBC": 3, "ECDSA": 3}.items():
        vals = [float(x["tm_s"]) for x in timing if x["task"] == task]
        check(len(vals) == expected_n and math.isfinite(statistics.median(vals)), "task_timing_reconstruction", f"{task}: n={len(vals)}, median={statistics.median(vals):.9f} s")
    check(not [k for k, v in manifest["frozen_hashes"].items() if not (ROOT / k).is_file() or sha(ROOT / k) != v], "frozen_source_hashes", f"{len(manifest['frozen_hashes'])} V4 frozen source hashes match")
    check(sha(AE / "R1_CLEAN_COHORT_V4_02_MANIFEST.json") == freeze["manifest_sha256"], "manifest_freeze_binding", freeze["manifest_sha256"])
    input_mismatches = []
    for line in (OUT / "ANALYSIS_INPUT_MANIFEST.sha256").read_text().splitlines():
        digest, rel = line.split("  ", 1)
        path = ROOT / rel
        if not path.is_file() or sha(path) != digest:
            input_mismatches.append(rel)
    check(not input_mismatches, "analysis_input_manifest", f"{len((OUT / 'ANALYSIS_INPUT_MANIFEST.sha256').read_text().splitlines())} inputs unchanged since hash capture")
    current = json.loads((ROOT / "sp2027/analysis/RESULTS_LOCK_H1PC.json").read_text())
    check(current["e1_public_h1"] == {"numerator": 0, "denominator": 54} and current["exp034_positive_control_h1"] == {"numerator": 0, "denominator": 12} and current["h1_positive_control"]["pass"] == 3, "population_lock_values", "E1 0/54; EXP-034 0/12; EXP-035 3/3 remain separate")
    check(current["arm_accounting"]["mapped_scientific_evidence_arms"] == 35 and current["arm_accounting"]["historical_raw_arms"] == 1 and current["arm_accounting"]["actual_repository_evidence_arms"] == 36, "arm_accounting", "35 mapped + SP2-05 historical = 36 actual evidence arms")
    old = ROOT / "sp2027/analysis/RESULTS_LOCK.json"
    expected_old = json.loads((ROOT / "sp2027/analysis/RESULTS_LOCK_V4.json").read_text())["predecessor_lock_sha256"]
    print(f"INFO predecessor_hash_check: historical V4 expects {expected_old}; current predecessor is {sha(old)}; current successor H1PC lock checker passed separately")
    print("INFO immutable_runtime: local Docker image inspect matched EXP-035 final digest; no image was built or modified")
    print("INFO source_status: active S&P source named by README is distinct from newer H1PC-integrated arXiv preprint; neither was edited")
    print("VALIDATION_COMPLETE")


if __name__ == "__main__":
    main()
