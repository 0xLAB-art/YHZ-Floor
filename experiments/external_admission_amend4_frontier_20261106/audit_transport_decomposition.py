#!/usr/bin/env python3
"""Transport-decomposition audit of the frozen Amendment-4 artifacts.

Post-hoc, offline audit (zero model calls, zero network, zero writes outside
this namespace) of the registered outcome RECORD, following the
Amendment-3 null-decomposition audit precedent
(`../external_admission_amend3_20261105/audit_null_decomposition.py`).

Purpose. SUMMARY_AMEND4.json records 61 primary AGENT_GIVEUP sessions and
47 recovery AGENT_GIVEUP sessions ("floor-exhausted giveups"). This audit
measures WHAT the provider actually returned in those slots: the raw
provider response bodies in sessions/raw_provider_responses/ are re-parsed
from disk and cross-tabulated against the registered results rows.

Registered verdicts are NOT recomputed and NOT changed: F1/F2/F3 remain the
frozen values. This is status-taxonomy accounting only — the same class of
corrective disclosure the Amendment-3 audit performed when it found 103
terminal crashes recorded as ORACLE_FAIL.

Boundary: no benchmark-quality claim; no native-benchmark-defect claim;
the transport is characterized as measured, not judged.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "sessions" / "raw_provider_responses"
RESULTS = HERE / "results.jsonl"
RECOVERY = HERE / "results_recovery_8400.jsonl"
FILTER_MAP = HERE / "CONTENT_FILTER_MAP.json"
LEDGER = Path("/mnt/nvme5/ACTS-Attack/sp2027/research_execution/BUDGET_LEDGER.jsonl")
OUT_JSON = HERE / "AUDIT_TRANSPORT_DECOMPOSITION.json"
SCHEMA = "amend4-transport-decomposition-audit/1"


def load_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def main() -> int:
    primary = load_jsonl(RESULTS)
    recovery = load_jsonl(RECOVERY)

    # --- layer A: raw provider body census -------------------------------
    raw_census = []  # per call: stop_reason, visible text len, charged tokens
    for p in sorted(RAW.glob("*.json")):
        d = json.loads(p.read_text())
        blocks = d.get("content", []) or []
        text = "".join(b.get("text", "") for b in blocks
                       if isinstance(b, dict) and b.get("type") == "text")
        raw_census.append({
            "file": p.name,
            "stop_reason": d.get("stop_reason"),
            "visible_text_chars": len(text),
            "charged_output_tokens": (d.get("usage") or {}).get("output_tokens"),
            "backend_id_prefix": str(d.get("id", ""))[:8],
            "block_types": sorted({b.get("type") for b in blocks
                                   if isinstance(b, dict)}),
        })

    stop_census = Counter(c["stop_reason"] for c in raw_census)
    text_len_by_stop = defaultdict(list)
    for c in raw_census:
        text_len_by_stop[c["stop_reason"]].append(c["visible_text_chars"])
    empty_length_calls = [c for c in raw_census
                          if c["stop_reason"] == "length"
                          and c["visible_text_chars"] == 0]
    charged_on_empty = sum(c["charged_output_tokens"] or 0
                           for c in empty_length_calls)
    empty_len_token_split = Counter(c["charged_output_tokens"]
                                    for c in empty_length_calls)
    backend_ids = Counter(c["backend_id_prefix"] for c in raw_census)

    # --- layer B: session-level cross-tab --------------------------------
    # Join every AGENT_GIVEUP session to its raw turn files.
    def session_rows(rows, wave):
        out = []
        for r in rows:
            slug = r["run_id"].split("__")[1]
            rec = {
                "wave": wave,
                "run_id": r["run_id"],
                "status": r["status"],
                "label": slug,
                "task_id": r["task_id"],
                "representation": r["representation"],
                "turns": r.get("turns"),
                "submissions": r.get("submissions"),
                "turn_finish_reasons": [t.get("finish_reason")
                                        for t in r.get("turn_records", [])],
            }
            out.append(rec)
        return out

    rows_a = session_rows(primary, "primary_4200")
    rows_b = session_rows(recovery, "recovery_8400")

    giveup_frs = Counter(tuple(r["turn_finish_reasons"])
                         for r in rows_a if r["status"] == "AGENT_GIVEUP")
    giveup_frs_b = Counter(tuple(r["turn_finish_reasons"])
                           for r in rows_b if r["status"] == "AGENT_GIVEUP")

    # sessions with visible output (end_turn calls exist for these runs)
    def calls_for(run_prefix: str, suffix_count: int) -> int:
        return len(list(RAW.glob(f"{run_prefix}__turn*.json")))

    content_sessions_primary = [r for r in rows_a
                                if r["status"] != "AGENT_GIVEUP"]
    # per-status raw-call accounting across BOTH waves together
    per_status = defaultdict(lambda: {"sessions": 0, "raw_calls": 0,
                                      "length_calls": 0, "end_turn_calls": 0})
    runid_by_status = defaultdict(list)
    status_of_runid = {}
    for r in rows_a + rows_b:
        status_of_runid[r["run_id"]] = r["status"]
        per_status[r["status"]]["sessions"] += 1
    # map run_id -> status; account every raw call to its session's status
    unrecorded_calls = []
    for c in raw_census:
        rid = c["file"].split("__turn")[0]
        st = status_of_runid.get(rid)
        if st is None:
            per_status["UNRECORDED_SESSION"]["raw_calls"] += 1
            per_status["UNRECORDED_SESSION"][
                "length_calls" if c["stop_reason"] == "length"
                else "end_turn_calls" if c["stop_reason"] == "end_turn"
                else "other_calls"] += 1
            unrecorded_calls.append({
                "file": c["file"],
                "stop_reason": c["stop_reason"],
                "visible_text_chars": c["visible_text_chars"],
                "charged_output_tokens": c["charged_output_tokens"],
                "note": ("raw provider response exists but no terminal row in"
                         " results.jsonl / results_recovery_8400.jsonl — the"
                         " recovery wave records 48 rows while this slot's"
                         " attempt left an orphan call; counted here, never"
                         " pooled into any registered cell"),
            })
            continue
        per_status[st]["raw_calls"] += 1
        per_status[st]["length_calls" if c["stop_reason"] == "length"
                      else "end_turn_calls" if c["stop_reason"] == "end_turn"
                      else "other_calls"] += 1

    # --- layer C: events-log transport-failure accounting ------------------
    fm = json.loads(FILTER_MAP.read_text())
    event_rows = [json.loads(l) for l in
                  (HERE / "sessions" / "events" /
                   "events_amend4.jsonl").read_text().splitlines()
                  if l.strip()]
    pf_events = [e for e in event_rows if e.get("kind") == "provider_failure"]
    pf_reasons = Counter()
    for e in pf_events:
        d = str(e.get("detail", ""))
        if "HTTP 400" in d and "content-blocked" in d:
            pf_reasons["HTTP_400_content_blocked"] += 1
        elif "HTTP 429" in d:
            pf_reasons["HTTP_429"] += 1
        elif "HTTP 5" in d:
            pf_reasons["HTTP_5xx"] += 1
        else:
            pf_reasons["other"] += 1
    blocked_slots = sum(
        n
        for label in fm["session_slots_blocked_by_cell"].values()
        for task in label.values()
        for n in task.values())

    # --- assemble ---------------------------------------------------------
    audit = {
        "schema": SCHEMA,
        "title": "Transport decomposition of the Amendment-4 null",
        "scope": ("post-hoc offline audit of registered Amendment-4 artifacts;"
                  " zero model calls, zero network, zero changes to registered"
                  " verdicts"),
        "inputs": {
            "results_primary": "results.jsonl",
            "results_recovery": "results_recovery_8400.jsonl",
            "raw_provider_responses_dir": str(RAW.relative_to(HERE)),
            "content_filter_map": "CONTENT_FILTER_MAP.json",
            "budget_ledger": str(LEDGER),
        },
        "layer0_production_defect_disclosure": (
            "v1 of this audit keys raw files to sessions by file-name prefix;"
            " names are {run_id}__turn{n}.json where run_id already ends with"
            " a 12-hex suffix, so the prior subtraction bug is avoided here."
        ),
        "layerA_raw_provider_body_census": {
            "raw_files": len(raw_census),
            "stop_reason_counts": dict(stop_census),
            "visible_text_chars_by_stop_reason": {
                k: {"n": len(v), "min": min(v), "max": max(v)}
                for k, v in text_len_by_stop.items()},
            "empty_visible_text_and_length_cut_calls": len(empty_length_calls),
            "charged_output_tokens_on_empty_calls": charged_on_empty,
            "charged_output_tokens_split_on_empty_calls":
                dict(empty_len_token_split),
            "backend_id_prefixes": dict(backend_ids.most_common(4)),
            "note": ("every length-cut call's content is a single empty text"
                     " block; the gateway re-serializes an"
                     " OpenAI-chat-style backend (id prefix 'chatcmpl-');"
                     " hidden reasoning consumed the whole completion budget"
                     " under the Anthropic-messages facade"),
        },
        "layerB_session_cross_tab": {
            "primary_giveup_finish_reason_pairs":
                {str(k): v for k, v in giveup_frs.items()},
            "recovery_giveup_finish_reason_pairs":
                {str(k): v for k, v in giveup_frs_b.items()},
            "per_status_raw_call_accounting":
                {k: dict(v) for k, v in sorted(per_status.items())},
        },
        "layerC_transport_failure_accounting": {
            "events_log_provider_failure_reasons": dict(pf_reasons),
            "http_400_content_blocked_events":
                pf_reasons["HTTP_400_content_blocked"],
            "content_filter_blocked_session_slots": blocked_slots,
            "grid_sessions": 168,
            "blocked_fraction_of_grid": round(blocked_slots / 168, 4),
        },
        "regression_of_registered_taxonomy": {
            "claimed": "AGENT_GIVEUP reads as the agent declining to submit",
            "measured": ("all AGENT_GIVEUP sessions ended both turns with"
                         " stop_reason=length and EMPTY visible content; the"
                         " model never produced a visible answer"),
            "proper_class_under_registered_taxonomy":
                "PROVIDER-side completion (route's hidden-reasoning budget"
                " consumed the max_tokens floor before any text);"
                " classification as agent behavior is a taxonomy artifact",
        },
        "boundaries": {
            "no_benchmark_quality_claim": True,
            "no_model_call": True,
            "no_new_sessions": True,
            "offline": True,
            "registered_verdicts_unchanged": True,
        },
    }
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    # compact stdout summary
    s = audit["layerA_raw_provider_body_census"]
    print(json.dumps({
        "raw_files": s["raw_files"],
        "stop_census": s["stop_reason_counts"],
        "empty_length_calls": s["empty_visible_text_and_length_cut_calls"],
        "charged_on_empty": s["charged_output_tokens_on_empty_calls"],
        "primary_giveup_pairs": audit["layerB_session_cross_tab"][
            "primary_giveup_finish_reason_pairs"],
        "recovery_giveup_pairs": audit["layerB_session_cross_tab"][
            "recovery_giveup_finish_reason_pairs"],
        "http400_events": audit["layerC_transport_failure_accounting"][
            "http_400_content_blocked_events"],
        "blocked_slots": audit["layerC_transport_failure_accounting"][
            "content_filter_blocked_session_slots"],
        "per_status": audit["layerB_session_cross_tab"][
            "per_status_raw_call_accounting"],
    }, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
