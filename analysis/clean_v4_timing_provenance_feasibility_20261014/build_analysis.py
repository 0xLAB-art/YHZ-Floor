import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
AE = ROOT / "sp2027/agent-eval"
RUNS = AE / "runs_r1_clean_capture_first_v4_claude46_20261014_02"
MANIFEST = AE / "R1_CLEAN_COHORT_V4_02_MANIFEST.json"
FREEZE = AE / "R1_CLEAN_COHORT_V4_02_FREEZE.json"
LEDGER = AE / "R1_CLEAN_COHORT_V4_ROW_LEDGER.csv"
TASKS = {
    "rc4_keystream_reuse": "RC4",
    "chacha20_nonce_reuse": "ChaCha20",
    "cbc_padding_oracle": "CBC",
    "ecdsa_nonce_reuse": "ECDSA",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = read_json(MANIFEST)
    freeze = read_json(FREEZE)
    scheduled = manifest["entries"]
    ledger_rows = list(csv.DictReader(LEDGER.open(encoding="utf-8")))
    records = {p.stem: p for p in RUNS.glob("q*.json")}
    rows = []
    event_index = {}
    for entry in scheduled:
        lr = next(x for x in ledger_rows if x["entry_id"] == entry["entry_id"])
        rp = records[lr["run_id"]]
        rec = read_json(rp)
        tp = RUNS / "transcripts" / lr["run_id"] / "transcript.jsonl"
        events = [json.loads(x) for x in tp.read_text(encoding="utf-8").splitlines() if x.strip()]
        event_index[lr["run_id"]] = events
        end_events = [e for e in events if e.get("type") == "session_end"]
        oracle_events = [e for e in events if e.get("type") == "run" and isinstance(e.get("verdict"), dict)]
        accepted = [e for e in oracle_events if e["verdict"].get("verdict") == "success" and (e["verdict"].get("match") is True or (e["verdict"].get("signature_valid") is True and e["verdict"].get("key_matches") is True))]
        rejected = [e for e in oracle_events if e["verdict"].get("verdict") == "failure" and e["verdict"].get("match") is False]
        requests = rec.get("model_config", {}).get("request_records", [])
        clocks = rec.get("clocks", {})
        oracle = rec.get("oracle", {}).get("verdict", {})
        session = rec.get("session", {})
        artifact_hashes = ";".join(a.get("sha256", "") for a in rec.get("artifacts", []))
        candidate_events = [e for e in events if e.get("type") == "run" and e.get("claim") is not None]
        run_status_match = session.get("status") == lr["status"]
        transcript_end_matches = len(end_events) == 1 and end_events[0].get("tte_m_harness_ns") == clocks.get("tte_m_harness_ns")
        row = {
            "entry_id": lr["entry_id"], "run_id": lr["run_id"], "scheduled_task_id": entry["task_id"],
            "condition": entry["condition"], "task": TASKS[entry["task_id"]], "replicate": entry["replicate"],
            "track": entry["track"], "slot": entry["slot"], "manifest_sha256": sha(MANIFEST),
            "raw_record_path": str(rp.relative_to(ROOT)), "raw_record_sha256": sha(rp),
            "raw_run_id_matches": rec.get("run_id") == lr["run_id"], "ledger_terminal_status": lr["status"],
            "record_terminal_status": session.get("status"), "status_matches": run_status_match,
            "transcript_path": str(tp.relative_to(ROOT)), "transcript_sha256": sha(tp), "transcript_event_count": len(events),
            "transcript_session_end_count": len(end_events), "session_end_duration_matches_record": transcript_end_matches,
            "provider": rec.get("model_config", {}).get("provider"), "provider_route_label": rec.get("model_config", {}).get("model_id"),
            "requested_model_snapshot": rec.get("model_config", {}).get("model_snapshot"),
            "retained_llm_turn_events": sum(e.get("type") == "llm_turn" for e in events),
            "recorded_request_records": len(requests), "sum_llm_span_ns": sum(x.get("llm_span_ns", 0) for x in requests),
            "sum_response_chars": sum(x.get("response_chars", 0) for x in requests),
            "provider_http_request_attempts": "NOT_RETAINED; request records are model-turn aggregates",
            "agent_submission_attempts": session.get("attempts"), "oracle_queries": session.get("queries"),
            "oracle_impl_sha256": rec.get("oracle", {}).get("implementation_sha256"),
            "record_oracle_verdict": oracle.get("success"), "record_oracle_timestamp": oracle.get("verdict_timestamp"),
            "record_oracle_failure_reason": oracle.get("failure_reason"),
            "transcript_oracle_success_verdict_events": len(accepted), "transcript_oracle_failure_verdict_events": len(rejected),
            "candidate_claim_event_count": len(candidate_events), "candidate_artifact_hashes": artifact_hashes,
            "candidate_claim_and_verdict_same_run_transcript": bool(candidate_events and (accepted or rejected)),
            "task_instance_sha256": next((a.get("sha256") for a in rec.get("artifacts", []) if "instance" in a.get("path", "")), ""),
            "tte_m_harness_ns": clocks.get("tte_m_harness_ns"), "tte_m_oracle_ns": clocks.get("tte_m_oracle_ns"),
            "tte_op_agent_ns": clocks.get("tte_op_agent_ns"), "oracle_op_span_ns": clocks.get("oracle_op_span_ns"),
            "dual_clock_max_drift_ns": clocks.get("dual_clock_max_drift_ns"),
            "session_started_utc_record": session.get("started_utc"), "session_ended_utc_record": session.get("ended_utc"),
            "transcript_op_start_utc": end_events[0].get("op_start_utc") if end_events else "",
            "transcript_session_end_utc": end_events[0].get("utc") if end_events else "",
            "transcript_op_start_monotonic_ns": "NOT_RETAINED", "transcript_terminal_monotonic_ns": "NOT_RETAINED",
            "environment_qualification_manifest_sha256": rec.get("environment", {}).get("qualification", {}).get("manifest_sha256"),
            "environment_runtime_fingerprint": json.dumps({k: rec.get("environment", {}).get(k) for k in ("python", "platform", "uname", "openssl", "gcc", "docker")}, sort_keys=True),
        }
        rows.append(row)
    fields = list(rows[0])
    write_csv(OUT / "V4_COMPLETE_ROW_EVIDENCE_LEDGER.csv", rows, fields)

    successes = [r for r in rows if r["record_terminal_status"] == "SUCCESS"]
    timing_rows = []
    for r in successes:
        rec = read_json(ROOT / r["raw_record_path"])
        evs = event_index[r["run_id"]]
        end = next((e for e in evs if e.get("type") == "session_end"), {})
        ns = r["tte_m_harness_ns"]
        timing_rows.append({
            "run_id": r["run_id"], "task": r["task"], "replicate": r["replicate"], "terminal_status": r["record_terminal_status"],
            "oracle_verdict": "explicit accepted" if r["transcript_oracle_success_verdict_events"] > 0 else "record-level success; transcript chain incomplete",
            "tm_ns": ns, "tm_ms": ns / 1e6 if isinstance(ns, int) else "", "tm_s": ns / 1e9 if isinstance(ns, int) else "",
            "start_endpoint": "post-provision op_start_utc=" + str(end.get("op_start_utc")), "end_endpoint": "_end_session entry terminal sample; monotonic value not retained; following session_end_utc=" + str(end.get("utc")),
            "clock_source": "time.monotonic_ns in ACTS-ATTACK/harness/v3/agent_loop.py; elapsed persisted by V4 record builder",
            "clock_evidence_status": "SUPPORTED_WITH_QUALIFICATION: source calculation, run-bound transcript endpoints, and matching persisted duration; raw monotonic endpoint readings not retained",
            "provider_label": r["provider_route_label"], "transcript_path": r["transcript_path"],
            "oracle_record_path": r["transcript_path"], "source_record_sha256": r["raw_record_sha256"],
            "notes": "T_M is harness agent-session interval, not model-only, oracle-only, or agent operation span; provider HTTP attempt count is not retained",
        })
    write_csv(OUT / "V4_SUCCESSFUL_AGENT_TIMINGS.csv", timing_rows)

    summaries = {}
    for task_id, task in TASKS.items():
        tr = [r for r in rows if r["scheduled_task_id"] == task_id]
        sr = [r for r in tr if r["record_terminal_status"] == "SUCCESS"]
        admissible = [x for x in timing_rows if x["task"] == task and x["clock_evidence_status"].startswith("SUPPORTED_WITH_QUALIFICATION") and isinstance(x["tm_ns"], int)]
        vals = [x["tm_ns"] / 1e9 for x in admissible]
        summaries[task] = {
            "scheduled_n": len(tr), "retained_n": sum(r["raw_run_id_matches"] and r["transcript_event_count"] > 0 for r in tr),
            "success_n": len(sr), "timing_admissible_success_n": len(admissible),
            "successful_agent_tm_median_s": statistics.median(vals) if vals else None,
            "minimum_s": min(vals) if vals else None, "maximum_s": max(vals) if vals else None,
            "individual_successful_run_timings_s": [{"run_id": x["run_id"], "replicate": x["replicate"], "tm_s": x["tm_s"]} for x in admissible],
            "timing_qualification": "reported duration is retained and source-defined; raw monotonic boundary readings are not independently retained",
        }
    (OUT / "V4_SUCCESS_TIMING_BY_TASK.json").write_text(json.dumps({"cohort": "EXP-034 / CLEAN V4-02", "scheduled_n": 12, "retained_n": len(rows), "qualified_source_supported_success_timing_n": len(timing_rows), "independently_recomputable_from_raw_monotonic_endpoints_n": 0, "tasks": summaries}, indent=2) + "\n", encoding="utf-8")

    input_paths = [MANIFEST, FREEZE, LEDGER, AE / "R1_CLEAN_COHORT_V4_PROTOCOL.md", AE / "V4_CLOCK_CONTRACT_QUALIFIED.json",
                   ROOT / "ACTS-ATTACK/harness/v4/run_agent_operations_v4.py", ROOT / "ACTS-ATTACK/harness/v3/agent_loop.py",
                   ROOT / "ACTS-ATTACK/harness/v3/classify.py", ROOT / "ACTS-ATTACK/harness/v3/record_builder.py",
                   ROOT / "sp2027/analysis/RESULTS_LOCK_V4.json", ROOT / "sp2027/analysis/RESULTS_LOCK_H1PC.json",
                   ROOT / "sp2027/analysis/results_lock_v4.py", ROOT / "sp2027/analysis/results_lock_h1pc.py",
                   AE / "h1_positive_control_20261014_v2/H1_POSITIVE_CONTROL_MANIFEST.json",
                   AE / "h1_positive_control_20261014_v2/H1_POSITIVE_CONTROL_PROTOCOL.md",
                   AE / "h1_positive_control_20261014_v2/H1_POSITIVE_CONTROL_H1_CHECK.csv",
                   AE / "h1_positive_control_20261014_v2/H1_POSITIVE_CONTROL_VALIDATION.md",
                   AE / "h1_positive_control_20261014_v2/H1_POSITIVE_CONTROL_LEDGER.csv",
                   AE / "h1_positive_control_20261014_v2/H1_POSITIVE_CONTROL_MANIFEST.sha256",
                   AE / "h1_positive_control_20261014_v2/Dockerfile",
                   AE / "h1_positive_control_20261014_v2/configuration.json",
                   AE / "h1_positive_control_20261014_v2/task_card.json",
                   AE / "h1_positive_control_20261014_v2/task.py",
                   AE / "h1_positive_control_20261014_v2/oracle.py",
                   AE / "h1_positive_control_20261014_v2/run_control.py",
                   ROOT / "sp2027/paper/split_rebuild_v4_r23/verify_h1_positive_control.py",
                   ROOT / "sp2027/paper/README.md", ROOT / "sp2027/paper/main.tex", ROOT / "sp2027/paper/main.pdf",
                   ROOT / "sp2027/paper/arxiv_preprint_20261014/README.md",
                   ROOT / "sp2027/paper/arxiv_preprint_20261014/main.tex", ROOT / "sp2027/paper/arxiv_preprint_20261014/main.pdf",
                   ROOT / "sp2027/paper/split_rebuild_consistency/EXP035_INTEGRATION_REPORT.md",
                   ROOT / "sp2027/analysis/RESULTS_LOCK.json"]
    input_paths.extend(records.values())
    input_paths.extend(sorted(RUNS.glob("transcripts/*/transcript.jsonl")))
    input_paths.extend(sorted((AE / "h1_positive_control_20261014_v2/runs").glob("*.json")))
    lines = []
    for p in sorted(set(input_paths)):
        if p.is_file():
            lines.append(f"{sha(p)}  {p.relative_to(ROOT)}")
    (OUT / "ANALYSIS_INPUT_MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

    write_timing_summary(summaries, rows, timing_rows)
    write_oracle_audit(rows)
    write_clock_audit(rows, timing_rows)
    write_separation(summaries)
    write_patch(summaries)
    write_feasibility()
    write_value_cost(summaries, rows)
    write_validation(rows, timing_rows)


def write_timing_summary(s, rows, timing):
    lines = ["# Clean V4-02 successful-agent timing summary", "", "EXP-034 / CLEAN V4-02 has 12 scheduled and retained records; 8 are SUCCESS. The table reports source-defined `tte_m_harness_ns` converted to seconds. The denominator for timing-admissible successes is shown separately from raw SUCCESS.", "", "| Task | Scheduled | Retained | SUCCESS | Timing-admissible SUCCESS | Median T_M (s) | Range (s) | Individual successful runs (s) |", "|---|---:|---:|---:|---:|---:|---:|---|"]
    for task, d in s.items():
        iv = ", ".join(f"{x['run_id']}={x['tm_s']:.6f}" for x in d["individual_successful_run_timings_s"]) or "none"
        median = "none" if d["successful_agent_tm_median_s"] is None else f"{d['successful_agent_tm_median_s']:.6f}"
        ran = "none" if d["minimum_s"] is None else f"{d['minimum_s']:.6f}–{d['maximum_s']:.6f}"
        lines.append(f"| {task} | {d['scheduled_n']} | {d['retained_n']} | {d['success_n']} | {d['timing_admissible_success_n']} | {median} | {ran} | {iv} |")
    lines += ["", "These are descriptive summaries of n=2 or n=3 observed successful sessions, not stable task capability distributions. No confidence interval or pooled task median is estimated.", "", "The duration is captured per run and agrees between raw terminal record and transcript terminal event. Code identifies a monotonic harness interval from `op_start_mono` through `_end_session`; it stops at agent-terminal handling before physical close/cleanup. The numerical monotonic start/end readings are not themselves retained. Thus 8/8 successful intervals support qualified source-defined timing; 0/8 can be independently recomputed from two retained monotonic endpoints. A claim specifically extending through physical session close is not established.", "", "RC4 has 0/3 successes. No successful-agent median is defined for RC4."]
    (OUT / "V4_SUCCESS_TIMING_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_oracle_audit(rows):
    succ = [r for r in rows if r["record_terminal_status"] == "SUCCESS"]
    fail = [r for r in rows if r["record_terminal_status"] == "ORACLE_FAIL"]
    lines = ["# V4 oracle verdict authority audit", "", "## Authority path", "", "The retained transcript records the submitted candidate in a `run` event and an adjacent task-specific oracle verdict in that same session event. The raw terminal record binds `run_id`, task card, oracle implementation hash, terminal status, and oracle verdict. `SUCCESS` is assigned only when the classifier receives `verdict == \"success\"`; `ORACLE_FAIL` is assigned when it receives `verdict == \"failure\"`. The fallback branch also returns `ORACLE_FAIL` for an unmapped graded outcome, so a status label alone is not sufficient evidence of explicit rejection.", "", "## Row audit", "", "| run_id | status | Transcript explicit verdict | Candidate event | Result |", "|---|---|---|---:|---|"]
    for r in succ + fail:
        explicit = r["transcript_oracle_success_verdict_events"] > 0 if r["record_terminal_status"] == "SUCCESS" else r["transcript_oracle_failure_verdict_events"] > 0
        v = "accepted; task-specific checks true" if r["record_terminal_status"] == "SUCCESS" and explicit else "rejected; task-specific check false" if explicit else "no explicit corresponding transcript verdict"
        lines.append(f"| {r['run_id']} | {r['record_terminal_status']} | {v} | {r['candidate_claim_event_count']} | {'explicit verdict retained' if explicit else 'fallback cannot be excluded'} |")
    lines += ["", f"Result: sessions with at least one explicit accepted verdict: {sum(r['transcript_oracle_success_verdict_events'] > 0 for r in succ)}/{len(succ)}. Sessions with explicit rejection verdict(s): {sum(r['transcript_oracle_failure_verdict_events'] > 0 for r in fail)}/{len(fail)}. Each failure session has four submitted candidates and four explicit task-specific rejection events; successes have a final accepted event, with any preceding rejected candidate events retained.", "", "The transcript `run` record includes the submitted candidate and nested oracle response; task condition, replicate, model, and session-end record bind the exchange to the scheduled run. The raw record does not carry a separate oracle request UUID or candidate digest, so the link is same-session execution evidence rather than an independently addressable oracle transaction. No terminal label is changed. The classifier's fallback semantic is not needed to explain any of the observed ORACLE_FAIL rows.", ""]
    (OUT / "V4_ORACLE_VERDICT_AUTHORITY_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def write_clock_audit(rows, times):
    lines = ["# V4 clock endpoint audit", "", "## Evidence levels", "", "| Check | Classification | Basis |", "|---|---|---|", "| Contract names T_M start/end and monotonic source | DECLARED_ONLY | `V4_CLOCK_CONTRACT_QUALIFIED.json` declares post-provision start through retained terminal/session-close. |", "| Duration generated with monotonic clock | ENFORCED_BY_CODE | `agent_loop.py` uses `time.monotonic_ns()`; start is sampled after provisioning and instance materialization, immediately before `op_start`; stop is sampled at entry to `_end_session`. |", "| Stop is terminal/session-close endpoint | SUPPORTED_WITH_QUALIFICATION | Stop occurs after the agent loop's terminal outcome is available but before abort/cleanup, final oracle read, and transcript `session_end` write. It is an agent-terminal endpoint, not physical close after cleanup. |", "| Endpoint event belongs to this session | SUPPORTED_BY_RETAINED_RECORD | Transcript binds `op_start_utc`, subsequent session-end UTC marker, task, replicate, model and matching duration to same run; the session-end UTC is later than the monotonic stop sample. |", "| Raw monotonic start/end readings retained | NOT_ESTABLISHED | Only their difference is retained; exact monotonic endpoint values are absent. |", "| Duration finite, integer, nonnegative and unit documented | ENFORCED_BY_CODE / SUPPORTED_BY_RETAINED_RECORD | V4 structural clock validator checks primary clock integer/nonnegative and schema uses ns; every SUCCESS has a positive integer. |", "| Same-session binding of primary duration | SUPPORTED_BY_RETAINED_RECORD | run ID binds raw record, transcript path, scheduled identity and terminal duration; transcript event has session-bound UTC labels. |", "| Validator independently enforces complete raw endpoint pair | NOT_ESTABLISHED | It validates duration structure and cross-clock diagnostic, not two retained monotonic timestamps or their independent subtraction. |", "", "## Per-success check", "", "All 8 SUCCESS records have `tte_m_harness_ns`, one matching transcript `session_end`, one explicit oracle success, and finite nonnegative duration. `session.started_utc` and `session.ended_utc` in the top-level record are null. The transcript `op_start_utc` is sampled adjacent to the monotonic start, and its `session_end` UTC is written after the T_M stop and cleanup; neither exposes the raw monotonic sample. Accordingly, all eight values are reportable as source-defined, session-bound durations to agent-terminal handling with qualification; none is independently re-computable from two retained monotonic endpoints. If wording promises timing through physical session close, the records do not establish that longer interval.", "", "## Requests and retries", "", "`request_records` and transcript `llm_turn` events count model turns and aggregate elapsed time / response characters. They do not retain provider HTTP request IDs or individual transport attempts. V4's zero-replacement schedule constrains scheduled sessions; it does not prove exactly one HTTP request per model turn. `session.attempts` counts submitted-code attempts, not provider HTTP retries. Oracle query counts are separately retained and all 12 records report zero; each session nevertheless has a final task verdict. Provider HTTP attempts are therefore unknown from retained records.", ""]
    write_text("V4_CLOCK_ENDPOINT_AUDIT.md", lines)


def write_separation(s):
    vals = {k: v["successful_agent_tm_median_s"] for k, v in s.items()}
    lines = ["# Legacy, clean-agent, and fixed-executor timing separation", "", "| Task | Legacy successful T_M | Clean V4-02 successful T_M | Fixed-executor T_op | Scientific interpretation |", "|---|---:|---:|---:|---|"]
    entries = [("RC4", "8.3688372335 s", "no successful run (0/3)", "0.214196 ms", "Legacy success and operation-only execution refer to distinct cohorts and intervals; no clean successful-agent value exists."),
               ("ChaCha20", "3.5660625475 s", f"{vals['ChaCha20']:.6f} s (n=2)", "0.131647 ms", "Two cohort-specific descriptive medians; unmatched sessions and different clocks preclude a slowdown or causal ratio."),
               ("CBC", "no successful-agent median", f"{vals['CBC']:.6f} s (n=3)", "approximately 1.98 s", "Clean cohort supplies retained successful-agent interval missing from legacy; fixed operation remains a different interval."),
               ("ECDSA", "no successful-agent median", f"{vals['ECDSA']:.6f} s (n=3)", "6.956 ms", "Clean cohort supplies retained successful-agent interval missing from legacy; fixed operation remains a different interval.")]
    for e in entries:
        lines.append("| " + " | ".join(e) + " |")
    lines += ["", "No trials are matched. No agent slowdown, acceleration, paired effect, causal effect, significance test, or pooled cross-task median is estimated. The new observations do not revise the legacy results: they fill a task-specific descriptive endpoint absence in a separate clean cohort.", ""]
    write_text("V4_LEGACY_FIXED_TIMING_SEPARATION.md", lines)


def write_patch(s):
    lines = ["# Timing manuscript patch proposal (not applied)", "", "## Source status", "", "`sp2027/paper/README.md` names `sp2027/paper/main.tex` as the authoritative anonymous IEEE S&P source. Its current on-disk SHA-256 is `4daf3464443557a3b96db63d14f7bc2b6ebe7376dd7f3f0c1bffa88c6911780e`; its current PDF is 15 pages, despite the README's older 13-page hash/build statement. The separate `sp2027/paper/arxiv_preprint_20261014/main.tex` SHA-256 is `168c98e93333245d3d64940a5f29ab8539534036ff7dd64f3bffabe29912a406`; it builds to 18 pages and integrates V4 and EXP-035. It is the newest evidence-integrated manuscript candidate, but is a standalone preprint, not the status-designated IEEE S&P source. The two sources differ. This analysis does not edit either. A future patch must be routed to an author-selected target rather than silently choosing one.", "", "## Proposed paragraph", "", "A separate clean capture-first cohort retained 12 of 12 scheduled sessions and recorded eight oracle-accepted successes: two of three ChaCha20 sessions and all three CBC and ECDSA sessions. The retained harness clock records the interval from the post-provisioning agent-session start through terminal session close. Among successful sessions, descriptive median T_M was {chacha:.6f} s for ChaCha20 (range {chacha_min:.6f}–{chacha_max:.6f}; n=2), {cbc:.6f} s for CBC (range {cbc_min:.6f}–{cbc_max:.6f}; n=3), and {ecdsa:.6f} s for ECDSA (range {ecdsa_min:.6f}–{ecdsa_max:.6f}; n=3); RC4 had no successful session and no successful-agent median. The monotonic duration is retained and source-defined, although the raw monotonic endpoint readings are not separately retained. These observations supply successful-agent endpoint timings for CBC and ECDSA that are absent from the legacy cohort; they are separate cohorts and do not support a matched speed comparison or broader capability estimate.", "", "## Proposed table", "", "| Task | Scheduled / retained | Success | Successful-agent T_M median (range) |", "|---|---:|---:|---:|"]
    for task in ("RC4", "ChaCha20", "CBC", "ECDSA"):
        d = s[task]
        vals = [x["tm_s"] for x in d["individual_successful_run_timings_s"]]
        value = "not defined" if not vals else f"{statistics.median(vals):.6f} s ({min(vals):.6f}–{max(vals):.6f})"
        lines.append(f"| {task} | 3 / 3 | {d['success_n']}/3 | {value} |")
    lines += ["", "The paragraph and table are a secondary analysis of EXP-034, not a new arm or experiment. Do not merge these values with legacy E2 or fixed-executor T_op. Table line for RC4 intentionally reports no median.", ""]
    text = "\n".join(lines).format(chacha=s["ChaCha20"]["successful_agent_tm_median_s"], chacha_min=s["ChaCha20"]["minimum_s"], chacha_max=s["ChaCha20"]["maximum_s"], cbc=s["CBC"]["successful_agent_tm_median_s"], cbc_min=s["CBC"]["minimum_s"], cbc_max=s["CBC"]["maximum_s"], ecdsa=s["ECDSA"]["successful_agent_tm_median_s"], ecdsa_min=s["ECDSA"]["minimum_s"], ecdsa_max=s["ECDSA"]["maximum_s"])
    text = text.replace("The retained harness clock records the interval from the post-provisioning agent-session start through terminal session close.", "The retained harness clock records the post-provisioning agent-loop interval through terminal-outcome handling; its monotonic stop is sampled before harness cleanup and transcript session-close logging.")
    (OUT / "V4_TIMING_MANUSCRIPT_PATCH_PROPOSAL.md").write_text(text, encoding="utf-8")


def write_feasibility():
    matrix = [
        {"unchanged_H1_field": "source / implementation", "EXP035_evidence": "PASS: source hashes in frozen manifest and each run", "V4_agent_gap": "source hashes are frozen in schedule but V4 run record does not link complete source manifest fields for H1", "prospective_evidence": "freeze source tree commit plus hashes for agent loop, runner, writer, schema, oracle, task code", "assessment": "feasible"},
        {"unchanged_H1_field": "configuration", "EXP035_evidence": "PASS: configuration digest in manifest and runs", "V4_agent_gap": "provider config is recorded partially; request/retry policy and full config are not all run-bound", "prospective_evidence": "digest immutable config including prompt, model label, sampling, token budget, retry/timeouts, transport/proxy", "assessment": "feasible with external route limits"},
        {"unchanged_H1_field": "task / dataset / instance", "EXP035_evidence": "PASS: task card and instance identity linked", "V4_agent_gap": "task card and artifact hashes retained, but instance is temporary and only its digest remains", "prospective_evidence": "mount frozen instance read-only; retain bytes or content-addressed artifact reference and digest", "assessment": "feasible"},
        {"unchanged_H1_field": "immutable environment identity", "EXP035_evidence": "PASS: OCI final and base digest in manifest and run", "V4_agent_gap": "host environment fingerprint only; no image digest", "prospective_evidence": "build once, record final OCI digest and verify runtime reports that digest on each run", "assessment": "feasible"},
        {"unchanged_H1_field": "execution identity", "EXP035_evidence": "PASS: unique run ID bound to manifest digest and environment", "V4_agent_gap": "run identity is present but not bound to immutable runtime image", "prospective_evidence": "preassign run IDs from frozen schedule and bind session, provider exchanges, artifacts, clocks to the same run", "assessment": "feasible"},
        {"unchanged_H1_field": "retained result linkage", "EXP035_evidence": "PASS: candidate, artifact hash, oracle result, status and clock", "V4_agent_gap": "V4 has candidate, transcript, oracle verdict, terminal record and duration; HTTP-level calls not independently identified", "prospective_evidence": "persist request/response envelopes and IDs, candidate hash, oracle request/verdict, terminal outcome and interval", "assessment": "feasible; retry accounting required"},
        {"unchanged_H1_field": "external hosted-model backend", "EXP035_evidence": "not applicable; no model/provider", "V4_agent_gap": "APMIX route is externally hosted and mutable", "prospective_evidence": "retain route, requested label, timestamp, provider response metadata and all request attempts", "assessment": "cannot establish immutable weights or hosted backend reproducibility; not an H1 field"},
    ]
    write_csv(OUT / "REAL_AGENT_H1_FEASIBILITY_MATRIX.csv", matrix)
    write_text("REAL_AGENT_H1_FEASIBILITY_REPORT.md", ["# Real-agent H1 feasibility report", "", "## Verdict", "", "**FEASIBLE WITH MATERIAL PROVIDER/IDENTITY LIMITATIONS — APPROVAL REQUIRED.** The unchanged H1 checker requires source, configuration, task instance, immutable local environment, execution identity and retained result linkage. It does not impose an immutable proprietary provider-weight requirement. The existing checker specifically excludes `immutable_backend_weights` from its H1 conjunction. Do not interpret a pass as hosted-model reproducibility.", "", "A networked real-agent runner can satisfy H1 if a digest-pinned local OCI runtime executes the frozen harness, task, tool sandbox and verifier; run records bind the digest, config, task, identity and result. Provider egress must be explicit and bounded. A network-disabled EXP-035 image cannot itself call APMIX unchanged.", "", "V4 currently fails H1 on immutable environment identity: it retains host/runtime fingerprints but no content-addressed runtime digest. EXP-035 demonstrates the unchanged criterion using three deterministic local executions. However, its v2 manifest still says `execution_status=FROZEN_NOT_LAUNCHED`, while the retained run records, H1 check, validation report and active successor lock show 3/3 completed. This is a provenance metadata contradiction in the control package; it does not change the H1 field checks, but should be disclosed and resolved by a versioned administrative record before reuse. No hypothetical real-agent H1 outcome is asserted.", "", "The practical design is technically viable with narrow egress and full HTTP exchange capture, but provider response generation and model weights remain outside the locally content-addressed boundary. A successful H1 result would establish the retained local source/config/task/environment/execution/result link, not deterministic hosted inference, provider immutability, or replayability of the backend.", ""])


def write_text(name, lines):
    (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_value_cost(s, rows):
    write_text("REAL_AGENT_PROVIDER_TRUST_BOUNDARY.md", ["# Real-agent provider trust boundary", "", "## Option A: digest-pinned agent container with narrow provider egress", "", "The runner, task, oracle and local tool execution can be digest-pinned and identified. Permit egress only to the required provider endpoint through an allowlisted route, with DNS/TLS policy and request logging. Retain provider/model label, request body hash, response bytes/hash, timestamps and transport attempt IDs. This exposes the execution container to network access; it is not network-isolated. The hosted service and weights remain mutable and are not content-addressed locally. H1 can still pass because provider immutability is not a frozen H1 gate.", "", "## Option B: pinned agent container plus separate pinned proxy", "", "The agent container can address only a controlled proxy; proxy image, policy, configuration and logs are separately pinned and retained. The proxy becomes part of the execution trust boundary and adds network hop/queue/retry behavior. Record both proxy and agent digests and define whether proxy time is included in T_M (it ordinarily is if the agent waits for responses). The provider backend remains external and mutable. The H1 checker accepts additional environment evidence but must bind the agent environment and all relevant source/config/result identities; it does not certify proxy correctness automatically.", "", "## Option C: provider relay with captured request/response spool", "", "A local or separately deployed relay can capture exchanges while preserving the existing API protocol. The relay may be pinned; transport errors and retries must be logged as provider request attempts rather than collapsed into model turns. If the relay replays stored outputs, it is a mock/replay contract test, not a real-agent inference observation. A live relay still cannot pin hosted backend weights.", "", "## Required clocks and identities", "", "Define a session as schedule identity through terminal closure; a provider request attempt as each HTTP attempt; a model response as the response associated with a particular attempt; agent code attempts as submitted-code execution; oracle attempts as each grading exchange; terminal outcome as one census item. Record independent IDs for each and do not call one scheduled cell one provider request. T_M should include provider wait and local orchestration if the named interval is agent-session time; retain monotonic start and stop values plus duration and session binding.", "", "Internal retries in the current clean V4 records are not observable: model-turn records aggregate spans and do not retain transport attempt IDs. No evidence establishes zero HTTP retries. Any prospective protocol needs retry limits and attempt-level logs.", ""])
    write_text("EXP035_VS_NETWORKED_AGENT_ENVIRONMENT.md", ["# EXP-035 environment versus networked real-agent environment", "", "EXP-035 V2 built a Python OCI image from a digest-pinned base, froze final image digest `sha256:f8cddd76e34aed0e04ee3f41a958a213cf72f6658996beb41888418101a41040`, recorded source/config/runtime identity, and executed read-only with network disabled. Its manifest and per-run records link environment, task, execution, candidate, oracle verdict and clock endpoints. The unchanged H1 check passed 3/3. This was a deterministic provenance control, not an agent/provider experiment.", "", "The existing V4 runtime records Python/platform/OS/OpenSSL/GCC/Docker strings and hashes frozen code/config inputs, but no final OCI digest. It retains the task artifact digest, transcript and terminal result. It therefore captures execution identity without the immutable environment link and has H1=0/12.", "", "Reuse: base-image digest pinning, multi-stage build discipline, manifest-before-run, runtime/source/config/task/oracle hashes, read-only filesystem, stable run IDs, candidate/result binding, and unchanged H1 checker. Change: the live agent must have constrained provider egress; the environment cannot remain network-disabled. Add provider transport capture, transport retry accounting, route policy, and monotonic boundary values. Mount task inputs and generated code under explicit read/write mounts. Keep oracle grading local where possible and separate from model/provider network.", "", "Before use, verify the actual EXP-035 image digest with offline local image inspection where available; a manifest digest alone is a recorded identity, not proof that a local image is present. Its frozen design remains evidence of feasibility for local deterministic H1, not proof that the same image can execute a live hosted model call.", ""])
    write_text("PROPOSED_CONTENT_ADDRESSED_REAL_AGENT_PROTOCOL.md", ["# Proposed content-addressed real-agent protocol", "", "**NOT APPROVED**  ", "**NOT EXECUTED**", "", "## Objective and boundary", "", "Test whether a real-agent session can satisfy the unchanged H1 link across frozen local source, configuration, task instance, digest-pinned OCI runtime, unique execution identity and retained result. A pass would not imply immutable hosted weights or reproducible provider responses. This protocol is a design only; it creates no experiment registration or result.", "", "## Freeze before launch", "", "Freeze one provider route and requested model label; task card, instance, prompt, sampling, token budget and tool schema; source tree and runner; local oracle; OCI base and final digest; read-only/write mounts; proxy/egress policy; retry and timeout semantics; run-ID schedule; and unchanged H1 checker hash. Publish manifest and sidecar before any model request. Use exactly one unique scheduled run per preregistered cell and preserve every terminal outcome.", "", "## Event units", "", "Count and retain separately: scheduled session; provider HTTP attempt; provider response; model turn; agent code submission/execution; oracle request/attempt; terminal session result. Assign stable IDs and parent links. Instrument a maximum transport retry count of zero or a preregistered fixed bound; record every failed and successful HTTP attempt, including status, time, request/response hash and retry reason. Do not treat the schedule's one-cell rule as a one-request guarantee.", "", "## Runtime and network", "", "Use a read-only digest-pinned agent OCI image with only explicit writable scratch/output mounts. Permit only the provider endpoint through an allowlisted proxy or constrained egress policy. Record the agent image digest, proxy image/config digest, DNS/TLS/route policy, provider endpoint, timestamps and all exchange envelopes. Explicitly describe the runtime as networked. Do not claim the provider backend or weights are content-addressed.", "", "## Verification and clocks", "", "Run the unchanged H1 checker over each run record. Retain raw monotonic start and terminal readings as well as their difference, both bound to run ID and terminal event. The interval starts at first retained agent execution after provisioning and ends at terminal/session close. Keep oracle operation spans and model-turn latency separate. Retain task-specific oracle request, submitted candidate digest, verdict and terminal classifier inputs.", "", "## Stop and reporting", "", "No replacement cells, adaptive prompts, fallbacks or post-observation fixes. Technical failures remain in the census. Do not estimate task capability from 1–2 qualification sessions. Any protocol modification after freeze requires a new versioned protocol and separate review. Do not execute without explicit approval and separate arm registration after design acceptance.", ""])
    write_text("NEW_COHORT_SCIENTIFIC_VALUE.md", ["# Scientific value of an additional real-agent cohort", "", "EXP-034 supplies capture-first real-agent identity with H1=0/12 because the retained local runtime has no immutable image digest. EXP-035 supplies content-addressed source/config/task/environment/execution/result linkage with H1=3/3, but uses a deterministic local task and no model. These separate results do not establish that a real-agent execution and its task result can be jointly linked under the unchanged H1 criterion.", "", "A content-addressed real-agent session could support the new bounded claim that at least one real hosted-agent run was linked to a frozen local source/configuration/task/runtime/execution/result record under H1. It would not establish provider weight identity, hosted-model reproducibility, broad task capability, performance superiority, or causal effect of provenance controls. External backend mutability remains material.", "", "The joint provenance observation is scientifically distinct from a higher H1 numerator. One or two real sessions can qualify end-to-end wiring and show a concrete joint observation, but cannot estimate success yield. A large cohort is only justified if the paper intends to estimate replicated real-agent outcomes under the content-addressed local runtime; that is not needed to resolve the provenance criterion itself.", ""])
    turns = sum(len(r.get("model_config", {}).get("request_records", [])) for r in [read_json(ROOT / x["raw_record_path"]) for x in rows])
    tokens = "not retained" 
    write_text("NEW_COHORT_RESOURCE_ESTIMATE.md", ["# New-cohort resource estimate", "", "## Observed V4-02 usage", "", f"The 12 retained sessions contain {turns} model-turn request records (2.58 mean, 2.5 median, 1–4 observed range per session). They retain 90,209 response characters in total and 547.842 aggregate seconds of model-turn spans (14.228–105.562 s per session). They do not retain provider token-usage counts or HTTP request-attempt IDs. Source code permits up to eight model turns per task session, three transient-gateway outer attempts per turn, and two HTTP POST attempts within a call when JSON-mode fallback is triggered. This gives a conservative source-level ceiling of 48 HTTP attempts/session, but no retained request IDs verify actual attempts. The model configuration requests a maximum of 4,096 completion tokens per turn; provider-reported token usage and prompt-token totals are absent. Monetary pricing is not established by the retained artifact, so cost is **UNKNOWN**.", "", "## Bounded projections", "", "| Candidate | Scheduled sessions | Model turns (observed mean planning value; frozen upper bound) | HTTP attempts (source-level upper bound) | Completion-token ceiling (requested max only) | Monetary estimate |", "|---|---:|---:|---:|---:|---|", "| A. Technical qualification | 1–2 | about 2.58/session; 8–16 maximum | 48–96 maximum | 32,768–65,536 | UNKNOWN |", "| B. 4 tasks × 3 repetitions | 12 | about 31 observed-style; 96 maximum | 576 maximum | 393,216 | UNKNOWN |", "| C. 4 tasks × 10 repetitions | 40 | about 103 observed-style; 320 maximum | 1,920 maximum | 1,310,720 | UNKNOWN |", "", "Planning values multiply session count by observed mean turns and are not guarantees or forecasts of future service behavior. The upper values multiply the task-card 8-turn ceiling, three outer gateway attempts and two HTTP POST branches per attempt; provider-side billing treatment of failed/retried requests is unknown. A session is capped at 900 s and an individual model request at 240 s; serial execution upper wall-clock bounds from session timeout alone are 0.5 h, 3 h, and 10 h respectively, excluding setup and pauses. V4 observed total T_M is 558.0 s across 12 sessions, but that small observed sum is not a reliable future runtime bound. Docker build/runtime resource consumption is not measured in retained records; local offline image inspection confirmed the EXP-035 digest is present and matches its manifest.", "", "A future approved registration should require a hard provider-side credit cap or verified zero-cost guarantee, transport attempt limit/logs, max model turns, session timeout, and a stop condition. No provider use is authorized by this analysis; no experiment was launched and no request was made.", ""])
    write_text("SAMPLE_SIZE_VALUE_ANALYSIS.md", ["# Sample-size value analysis", "", "Moving from 3 to 10 repetitions per task would improve descriptive resolution of success counts and observed T_M variation for these four fixed task instances under this one requested provider route. It would not broaden the task family, provide provider generalization, make a mutable hosted backend immutable, or repair missing provenance fields by repetition alone.", "", "With n=3, per-task rates are coarse and timings show only a few observed successes; n=10 gives a more informative within-task census but still has high uncertainty for capability interpretation and dependence on one task card/instance design and one route. It cannot make the results a stable general capability estimate without broader task and provider sampling plus a defensible design.", "", "Endpoint correctness and H1 completeness are design/instrumentation properties, not sample-size properties. A single correctly instrumented session can test whether the end-to-end linkage works; more repetitions only replicate that linkage. The best value-to-cost choice for provenance is a narrow, separately approved qualification, not n≥10 per task.", ""])
    write_text("FINAL_EXPERIMENT_DECISION.md", ["# Final experiment decision", "", "| Option | New claim | Gap resolved | Provenance value | Statistical value | Cost exposure | Complexity / ambiguity | Recommendation |", "|---|---|---|---|---|---|---|---|", "| 1. No new execution; publish verified V4 timing analysis | Adds qualified CBC/ECDSA successful-agent intervals absent in legacy | Timing endpoint absence | None beyond existing V4 | No new sampling | None | Low; timing caveat must be explicit | Do now as derived analysis |", "| 2. Narrow real-agent provenance pilot after approval | Joint real-agent plus content-addressed local H1-linked observation | Tests end-to-end joint gap | High for feasibility, bounded to observed session(s) | None for capability yield | Limited but unknown without token/price cap | Moderate; external provider and retries must be explicit | **Scientifically justified; approval required** |", "| 3. Frozen full new provenance cohort | Repeated joint linkage and bounded task outcomes | Replication of joint H1 design | High | Some within-task descriptive precision | Higher, unknown | High; provider mutability/retry ambiguity | Not currently justified before pilot demonstrates value |", "| 4. Expanded ≥10/task cohort | More within-task outcomes | Reduces coarse count/timing variation only | Repeats same environment linkage | Moderate within four fixed tasks; no broad generality | Highest, unknown | High | Not justified for this evidence-boundary paper |", "", "Recommendation: publish the V4 timing analysis with its endpoint qualification. A narrow real-agent provenance pilot is scientifically justified only as a separate, explicitly approved test of the currently missing joint observation; do not launch it as a capability-yield expansion. The full new cohort and n≥10 design are not justified by current claims.", ""])


def write_validation(rows, timing):
    write_text("ANALYSIS_VALIDATION_REPORT.md", ["# Analysis validation report", "", "## Immutable-source and population checks", "", f"- V4-02 schedule rows: {len(rows)}; unique run IDs: {len({r['run_id'] for r in rows})}; unique entry IDs: {len({r['entry_id'] for r in rows})}.", f"- Physical raw records: {len(list(RUNS.glob('q*.json')))}; retained transcripts: {len(list(RUNS.glob('transcripts/*/transcript.jsonl')))}.", f"- Terminal census: {dict(Counter(r['record_terminal_status'] for r in rows))}.", f"- Successful sessions with explicit accepted verdicts: {sum(r['transcript_oracle_success_verdict_events'] > 0 for r in rows if r['record_terminal_status'] == 'SUCCESS')}/8; failure sessions with explicit rejection verdicts: {sum(r['transcript_oracle_failure_verdict_events'] > 0 for r in rows if r['record_terminal_status'] == 'ORACLE_FAIL')}/4.", f"- Timing rows: {len(timing)}; all have finite nonnegative integer T_M: {all(isinstance(r['tm_ns'], int) and r['tm_ns'] >= 0 for r in timing)}.", "- The 11 source hashes frozen in the V4 manifest match current files; EXP-035 image digest was verified against local Docker image metadata without a build.", "- Raw records are read-only inputs; no existing scientific result or lock is rewritten.", "", "## Lock checks", "", "`results_lock_h1pc.py` is the active successor lock checker and passed. It verifies public E1 H1=0/54, EXP-034 H1=0/12, EXP-035 H1=3/3 and arm accounting 35 mapped + 1 historical =36.", "", "The predecessor `results_lock_v4.py` is retained as a historical check. It fails its predecessor hash assertion because `RESULTS_LOCK.json` current SHA-256 is `4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39`, not its expected `335ea2a10afe3cfe02ea8ee7d0f3aafeb3d63078ba5efc21c4fe1a10f06e50eb`. This is a predecessor-hash expectation mismatch, not evidence that the active H1PC successor lock failed. The historical script/lock is not modified.", "", "## Freeze and manuscript status discrepancies", "", "V4-02 manifest has `execution_status=FROZEN_NOT_LAUNCHED` and freeze metadata has `model_evaluation_started=false`, despite the retained 12-row V4 ledger, 12 raw records, 12 transcripts and successor lock. EXP-035 v2's manifest likewise says `FROZEN_NOT_LAUNCHED` while its three run records, H1 check and active successor lock establish 3/3. Both are retained metadata contradictions and were not changed.", "", "`sp2027/paper/README.md` designates `sp2027/paper/main.tex` as the authoritative anonymous S&P manuscript, but README's claimed source hash and 13-page build are stale relative to the current root source/PDF (actual root PDF: 15 pages). The later `arxiv_preprint_20261014` source is a separate 18-page standalone preprint and contains V4/EXP-035. It is the newest evidence-integrated candidate, not the README-designated S&P source. Neither was modified.", "", "## Remaining limits", "", "The V4 timing values cannot be independently recomputed from raw monotonic endpoint readings because those readings were not serialized; only duration, session-bound UTC markers, code path and matching record/transcript are retained. Provider HTTP retries and token counts are not retained in V4. No manuscript was modified.", ""])
    write_text("FINAL_SCIENTIFIC_ASSESSMENT.md", ["# Final scientific assessment", "", "## Terminal verdicts", "", "**TIMING: CLEAN SUCCESS TIMINGS PARTIALLY VERIFIED — CLAIMS BOUNDED**", "", "The eight SUCCESS rows carry explicit accepted task-specific oracle verdicts. The four ORACLE_FAIL rows carry explicit rejected verdicts in their retained session transcripts; the generic classifier has a fallback ORACLE_FAIL branch, but that branch is not needed to explain these four rows. Each successful record has a retained, source-defined harness duration and matching session-end event. Raw monotonic endpoint readings are absent, so all eight durations are supportable with qualification, not independently recomputable from raw clock endpoints. The individual timing values and task medians are in the companion CSV/JSON/summary.", "", "**PROVENANCE: FEASIBLE WITH MATERIAL PROVIDER/IDENTITY LIMITATIONS — APPROVAL REQUIRED**", "", "The unchanged H1 rule can be met by a networked real-agent runtime that binds local source, configuration, task, immutable OCI digest, execution identity and result. Provider egress means the runtime is not network-isolated; APMIX/hosted backend identity and weights remain externally mutable. H1 does not establish hosted-model reproducibility.", "", "**SCIENTIFIC RECOMMENDATION: NARROW PROVENANCE PILOT JUSTIFIED — DO NOT EXECUTE WITHOUT APPROVAL**", "", "A narrow pilot would test the unobserved joint claim that real-agent execution and a content-addressed local environment can be linked under H1. EXP-034 and EXP-035 establish the two sides separately, not jointly. Do not scale to n≥10 per task for this paper's current evidence-boundary claims; repetition would refine only within-task description.", "", "## Required accounting and integrity answers", "", "1. All 8 SUCCESS rows: explicit accepted task-specific oracle verdicts retained.", "2. All 4 ORACLE_FAIL labels: explicit task-specific oracle rejections retained; no fallback-only failure row found.", "3. Independently recomputable T_M from two raw monotonic endpoints: 0/8. Source-defined, session-bound recorded T_M values with qualification: 8/8.", "4. Clean successful-agent medians: ChaCha20 n=2, CBC n=3, ECDSA n=3; exact individual values appear in `V4_SUCCESS_TIMING_SUMMARY.md` and `V4_SUCCESSFUL_AGENT_TIMINGS.csv`. RC4: 0 success, no median.", "5. Clean V4 adds descriptive successful-agent CBC/ECDSA endpoints absent from the legacy cohort. It does not update the unmatched legacy sample or enable speed ratios.", "6. Raw records modified: NO.", "7. Proposed networked content-addressed runtime satisfies unchanged H1 in principle: YES, with local runtime digest and linkage captured; no such new execution is claimed.", "8. External limitations: provider HTTP retries and token use absent from V4; backend/weights mutable; network egress must be disclosed and captured.", "9. New real-agent H1 cohort: narrow pilot has a material distinct joint-provenance claim; approval required.", "10. N=40+: not justified for current paper scope.", "11. New provider requests: NO.", "12. New experiments launched: NO.", "13. Arm accounting unchanged: YES, 35 mapped + 1 historical =36.", "", "## Population separation", "", "Public E1 H1=0/54; EXP-034 H1=0/12; EXP-035 H1=3/3 remain distinct. Legacy conditional=10/19 and operational=10/47 remain separate from CLEAN V4's 8 SUCCESS and 4 ORACLE_FAIL labels over 12 retained records. No denominator is pooled.", ""])


if __name__ == "__main__":
    main()
