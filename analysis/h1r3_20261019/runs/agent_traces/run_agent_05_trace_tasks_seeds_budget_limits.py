#!/usr/bin/env python3
"""Agent 5 of 5: trace task difficulty, seed coverage, budget, and model-identity limits.

Scope:
- Read the retained reports and maps.
- Separate what is supported vs what is explicitly not supported.
- No provider calls.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path("sp2027/analysis")
HERE = ROOT / "h1r3_20261019"
TRACE_DIR = HERE / "runs" / "agent_traces"
TRACE_DIR.mkdir(parents=True, exist_ok=True)

TRACT = {
    "agent": "trace_agent_05_tasks_seeds_budget_limits",
    "scope": "task/seed/budget/model-identity limits from retained results",
    "provider_calls": False,
    "started_utc": json.dumps(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()),
}

def load_text(p):
    try:
        return p.read_text()
    except Exception as e:
        return ""

results = load_text(ROOT / "final_deliverables_20261018" / "SCIENTIFIC_RESULTS_REPORT_20261018.md")
evidence = load_text(ROOT / "final_deliverables_20261018" / "EVIDENCE_PACKAGE_20261018.md")
coverage = load_text(ROOT / "COMPLETE_EXPERIMENT_COVERAGE_AUDIT_20261018.md")
rqmap = load_text(ROOT / "final_deliverables_20261018" / "RQ_EVIDENCE_MAP_20261018.md")

TRACT["sources_used"] = {
    "scientific_results_report": bool(results),
    "evidence_package": bool(evidence),
    "coverage_audit": bool(coverage),
    "rq_evidence_map": bool(rqmap),
}

# Task family headline results from the report
TRACT["task_family_outcomes"] = {
    "V4_frozen_cohort": "8/12 accepted total; RC4 0/3, ChaCha20 2/3, CBC 3/3, ECDSA 3/3",
    "bounded_reproduction": "18/18 across RC4/ECDSA/ChaCha20 explicit-observation lanes",
    "held_out_attempt4": "4/4 oracle accepted with integrity gate PASS and leak audit 0 hits",
    "adaptive_xor": "8 queries and 39 queries accepted runs; no adaptive-necessity claim",
    "composition": "1 accepted scaffolded chain; oracle_queries=1; not discovery",
    "surrogate": "9,640-query success on reconstructed executed bytes; exact control 20,480 by construction",
    "escrow_e5": "1/14 descriptive accepted; candidate-equals-commitment; not enforced acquisition",
}

# What the report explicitly does NOT establish
TRACT["not_established"] = [
    "any universal capability rate",
    "cross-family generalization",
    "causal feedback benefit",
    "enforced secret acquisition / host isolation",
    "immutable model identity beyond provider-attested label",
    "independently recomputable V4 raw timings",
    "external benchmark joins",
]

# Seed/budget/scope notes from the record
TRACT["seed_and_scope_notes"] = [
    {
        "item": "V4 cohort",
        "note": "12 sessions; 31 nested programs; 4 oracle failures retained; Wilson interval illustrative only",
    },
    {
        "item": "Explicit-observation lanes",
        "note": "18 distinct physical run IDs across family-stratified namespaces; no pooled rate",
    },
    {
        "item": "2x2 information-contract lane",
        "note": "n=4 per cell; one fixture family; one provider-attested model label; descriptive exact statistics",
    },
    {
        "item": "Task difficulty",
        "note": "ECDSA and ChaCha20 treated as calibration families; harder tasks with sufficiency witness flagged as needed for broader claims",
    },
    {
        "item": "Model identity",
        "note": "Hosted model weights are provider-attested labels only; independent immutable weight identity not available",
    },
    {
        "item": "Budget/paid path",
        "note": "Free route only in the reported completion work; paid fallback not authorized",
    },
]

TRACT["critical_issues_traced"] = [
    {
        "type": "calibration_families_not_generalization_evidence",
        "issue": "Strongest success clusters are in relatively easy, well-known algebraic/controlled fixtures",
        "impact": "Success there does not imply broad cryptographic-agent capability",
        "status": "documented as limit",
    },
    {
        "type": "no_pooled_estimate_anywhere",
        "issue": "Denominators are per-contract and per-namespace; no merged rate",
        "impact": "Any claim of an overall success rate would be unsupported",
        "status": "enforced by admissibility rules",
    },
    {
        "type": "provider_attested_model_only",
        "issue": "Model identity is provider-attested, not independently verified",
        "impact": "Cannot claim immutable model identity from these records",
        "status": "documented as limit",
    },
    {
        "type": "timing_not_recomputable_for_v4",
        "issue": "V4 raw monotonic endpoint pairs not retained",
        "impact": "Elapsed durations are recorded evidence only, not recomputable measurements",
        "status": "documented as limit",
    },
    {
        "type": "acquisition_claims_not_surviving",
        "issue": "E5-style results show candidate-vs-commitment behavior only",
        "impact": "No enforced-acquisition/host-isolation claim survives",
        "status": "documented as weakened claim",
    },
]

TRACT["stop_rule_applied"] = "No provider calls; trace-only from retained reports, evidence package, coverage audit, and RQ map."
TRACT["completed_utc"] = json.dumps(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())

out = TRACE_DIR / "agent_05_trace_tasks_seeds_budget_limits.json"
out.write_text(json.dumps(TRACT, indent=2, sort_keys=False) + "\n")
print(json.dumps(TRACT, indent=2, sort_keys=False))
