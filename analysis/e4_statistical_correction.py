#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

from acts_stats import kaplan_meier
import e4_sensitivity as original_e4

SCHEMA = "e4-statistical-correction/1.0"
DEFAULT_OUT = HERE / "e4_statistical_correction_v1.json"
COHORTS = (
    ("legacy", ROOT / "sp2027/agent-eval/runs_legacy_v1"),
    ("pilot", ROOT / "sp2027/agent-eval/runs_w2_pilot"),
)

TERMINAL_STATUSES = {
    "AGENT_GIVEUP",
    "HARNESS_ERROR",
    "MODEL_REFUSAL",
    "ORACLE_FAIL",
    "TIMEOUT",
    "TOOL_FAILURE",
    "PROVIDER_UNAVAILABLE",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def event_type(status: str) -> str:
    if status == "SUCCESS":
        return "success"
    mapping = {
        "AGENT_GIVEUP": "agent_terminal_failure",
        "HARNESS_ERROR": "harness_error",
        "MODEL_REFUSAL": "model_refusal",
        "ORACLE_FAIL": "oracle_rejection",
        "TIMEOUT": "timeout",
        "TOOL_FAILURE": "tool_failure",
        "PROVIDER_UNAVAILABLE": "provider_unavailable",
    }
    if status not in mapping:
        raise ValueError(f"unknown session status: {status!r}")
    return mapping[status]


def classification_uncertainty(status: str, record: dict) -> str:
    if status == "SUCCESS":
        return "none: independent-oracle success is observed"
    if status == "PROVIDER_UNAVAILABLE":
        return (
            "external interruption is observed, but the counterfactual outcome "
            "under continued provider service is unavailable; informative "
            "interruption cannot be ruled out"
        )
    if status == "TIMEOUT":
        return (
            "the harness reports a terminal timeout, but the retained record "
            "does not expose a common pre-declared horizon; operationally "
            "terminal, horizon semantics remain uncertain"
        )
    if status == "AGENT_GIVEUP" and "provider" in (
            ((record.get("session") or {}).get("error") or "").lower()):
        return (
            "status is AGENT_GIVEUP, but the terminal error mentions provider "
            "overload; retain source status and flag possible external cause"
        )
    return (
        "terminal source status is observed; no later same-session success is "
        "possible in the retained record, but causal attribution is not identified"
    )


def source_end_time(record: dict) -> str | None:
    session = record.get("session") or {}
    if session.get("ended_utc"):
        return session["ended_utc"]
    verdict = ((record.get("oracle") or {}).get("verdict") or {})
    return verdict.get("verdict_timestamp")


def build_ledger() -> tuple[list[dict], dict]:
    ledger: list[dict] = []
    source_summary: dict = {}
    for cohort, path in COHORTS:
        records = original_e4.load_corpus(path)
        source_summary[cohort] = {
            "source_dir": str(path.relative_to(ROOT)),
            "source_sha256": {
                p.name: sha256_file(p) for p in sorted(path.glob("*.json"))
            },
            "raw_records": len(records),
        }
        for record in records:
            run_id = record["run_id"]
            status = (record.get("session") or {}).get("status")
            admissibility_reason = original_e4.inadmissible_reason(record)
            admissible = admissibility_reason is None
            clocks = record.get("clocks") or {}
            duration_ns = clocks.get("tte_m_harness_ns")
            duration_source = "tte_m_harness_ns"
            if duration_ns is None:
                duration_ns = clocks.get("tte_m_oracle_ns")
                duration_source = "tte_m_oracle_ns"
            duration_s = (duration_ns / 1e9) if duration_ns is not None else None
            valid_time = duration_s is not None and duration_s > 0
            start_utc = (record.get("session") or {}).get("started_utc")
            operational_type = event_type(status) if admissible and valid_time else None
            is_success = operational_type == "success"
            ledger.append({
                "run_id": run_id,
                "cohort": cohort,
                "start_time_utc": start_utc,
                "end_time_utc": source_end_time(record),
                "duration_s": duration_s,
                "duration_source": duration_source if duration_ns is not None else None,
                "event_time_valid": valid_time,
                "original_status": status,
                "admissibility": admissible,
                "admissibility_reason": admissibility_reason,
                "success_event": is_success,
                "operational_competing_event": (
                    None if is_success or operational_type is None else operational_type
                ),
                "censoring_event": None if operational_type else "not_at_risk",
                "latent_km_classification": (
                    "event" if is_success else (
                        "right_censored" if admissible and valid_time else "excluded"
                    )
                ),
                "classification_uncertainty": (
                    classification_uncertainty(status, record)
                    if operational_type else
                    "not classified because the source row failed the admissibility/time gate"
                ),
                "source_path": str((path / f"{run_id}.json").relative_to(ROOT)),
            })
    return ledger, source_summary


def _curve(records: list[dict], event_types: Iterable[str]) -> dict:
    wanted = tuple(event_types)
    rows = [r for r in records if r["admissibility"] and r["event_time_valid"]]
    rows.sort(key=lambda r: (r["duration_s"], r["run_id"]))
    n = len(rows)
    at_risk = n
    survival = 1.0
    cif = {name: 0.0 for name in wanted}
    points = []
    i = 0
    while i < n:
        t = rows[i]["duration_s"]
        j = i
        while j < n and rows[j]["duration_s"] == t:
            j += 1
        events = Counter(
            (rows[k]["operational_competing_event"] or "success")
            for k in range(i, j)
        )
        total_events = sum(events.values())
        if total_events:
            before = survival
            for name in wanted:
                cif[name] += before * events.get(name, 0) / at_risk
            survival *= 1.0 - total_events / at_risk
            points.append({
                "time_s": t,
                "risk_set_before": at_risk,
                "events_by_type": dict(sorted(events.items())),
                "event_free_survival_after": survival,
                "cif_by_type_after": {k: cif[k] for k in wanted},
            })
        at_risk -= j - i
        i = j
    return {
        "n": n,
        "event_counts": dict(sorted(Counter(
            r["operational_competing_event"] or "success" for r in rows
        ).items())),
        "curve": points,
        "final_cif": cif,
        "estimator": "Aalen-Johansen cumulative incidence; descriptive, no Fine-Gray regression",
    }


def km_secondary(records: list[dict]) -> dict:
    rows = [r for r in records if r["admissibility"] and r["event_time_valid"]]
    km = kaplan_meier(
        [r["duration_s"] for r in rows],
        [r["success_event"] for r in rows],
    )
    return {
        "estimand": "hypothetical latent time-to-success under non-informative censoring",
        "n": km.n,
        "events": km.events,
        "censored": km.censored,
        "median_s": km.median,
        "curve": [
            {"time_s": t, "survival": s}
            for t, s in zip(km.times, km.survival)
        ],
        "assumption_status": "not established; provider interruption may be informative",
    }


def build_output() -> dict:
    ledger, source_summary = build_ledger()
    eligible = [r for r in ledger if r["admissibility"] and r["event_time_valid"]]
    by_cohort = {}
    for cohort, _ in COHORTS:
        rows = [r for r in ledger if r["cohort"] == cohort]
        at_risk = [r for r in rows if r["admissibility"] and r["event_time_valid"]]
        types = sorted({r["operational_competing_event"] or "success" for r in at_risk})
        by_cohort[cohort] = {
            "raw_records": len(rows),
            "excluded_records": sum(not r["admissibility"] for r in rows),
            "admissible_records": len(at_risk),
            "status_counts_admissible": dict(sorted(Counter(
                r["original_status"] for r in at_risk
            ).items())),
            "operational_cif": _curve(at_risk, types),
            "secondary_km": km_secondary(at_risk),
            "risk_set_reconciliation": {
                "at_risk": len(at_risk),
                "event_total": sum(
                    (by_type := Counter(
                        r["operational_competing_event"] or "success"
                        for r in at_risk
                    )).values()
                ),
                "censor_total": 0,
            },
        }
    return {
        "schema": SCHEMA,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "estimands": {
            "operational": {
                "question": "probability of verified success before an observed terminal outcome",
                "time_zero": "declared E4 session launch; absolute launch timestamp is unavailable in source records",
                "success_event": "status SUCCESS at observed TTE_M endpoint",
                "terminal_events": "all observed non-success statuses in the admissible risk set, including provider interruption",
                "administrative_censoring": "none identified; no common documented horizon is recoverable",
                "primary_estimator": "Aalen-Johansen cumulative incidence, by observed event type",
            },
            "latent": {
                "question": "hypothetical time to success if non-success follow-up had continued",
                "censoring_assumption": "all non-successes treated as right-censored and independent of latent success time",
                "status": "secondary sensitivity only; assumption is not established",
            },
        },
        "source_summary": source_summary,
        "cohorts": by_cohort,
        "combined_eligible_records": len(eligible),
        "event_ledger": ledger,
        "provenance": {
            "immutable_sources_unchanged": True,
            "original_pipeline_preserved": True,
            "e5_or_other_cohorts_pooled": False,
        },
    }


def validate(output: dict) -> None:
    assert output["cohorts"]["legacy"]["raw_records"] == 54
    assert output["cohorts"]["legacy"]["excluded_records"] == 7
    assert output["cohorts"]["legacy"]["admissible_records"] == 47
    assert output["cohorts"]["pilot"]["raw_records"] == 20
    assert output["cohorts"]["pilot"]["excluded_records"] == 0
    assert output["cohorts"]["pilot"]["admissible_records"] == 20
    for cohort in output["cohorts"].values():
        counts = cohort["operational_cif"]["event_counts"]
        assert sum(counts.values()) == cohort["admissible_records"]
        assert cohort["risk_set_reconciliation"]["censor_total"] == 0
        assert cohort["secondary_km"]["events"] == counts.get("success", 0)
    assert output["cohorts"]["legacy"]["operational_cif"]["event_counts"]["success"] == 10
    assert output["cohorts"]["pilot"]["operational_cif"]["event_counts"]["success"] == 1
    assert all(
        not (r["admissibility"] is False and r["operational_competing_event"] is not None)
        for r in output["event_ledger"]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    output = build_output()
    validate(output)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"validated": True, "output": str(args.out), "records": len(output["event_ledger"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
