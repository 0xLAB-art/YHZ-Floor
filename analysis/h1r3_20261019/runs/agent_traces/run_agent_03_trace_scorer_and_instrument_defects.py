#!/usr/bin/env python3
"""Agent 3 of 5: trace scorer and instrument/evaluation defects.

Scope:
- XOR scorer wrong-truth defect and control.
- H1 V2 denominator/retention issues.
- Other evaluator-side artifacts that can look like model failures.
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
    "agent": "trace_agent_03_scorer_and_instrument_defects",
    "scope": "evaluator/instrument defects from retained records",
    "provider_calls": False,
    "started_utc": json.dumps(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()),
}

pointers = {
    "scientific_results_report": ROOT / "final_deliverables_20261018" / "SCIENTIFIC_RESULTS_REPORT_20261018.md",
    "evidence_package": ROOT / "final_deliverables_20261018" / "EVIDENCE_PACKAGE_20261018.md",
    "coverage_audit": ROOT / "COMPLETE_EXPERIMENT_COVERAGE_AUDIT_20261018.md",
    "h1v2_summary": ROOT / "research_execution" / "H1_V2_FAILURE_STAGE_SUMMARY.json",
    "h1v2_matrix": ROOT / "research_execution" / "H1_V2_FAILURE_STAGE_MATRIX.csv",
    "xor_control_root": ROOT / "postfreeze_integrity_resolution_20261018",
}

TRACT["pointers"] = {k: str(v) for k, v in pointers.items()}
TRACT["exists"] = {k: v.exists() for k, v in pointers.items()}

def load_text(p):
    try:
        return p.read_text()
    except Exception as e:
        return ""

results_txt = load_text(pointers["scientific_results_report"])
evidence_txt = load_text(pointers["evidence_package"])
coverage_txt = load_text(pointers["coverage_audit"])

TRACT["scientific_report_section_3"] = (
    results_txt[results_txt.find("## 3. Information-contract results"):]
    if "## 3. Information-contract results" in results_txt
    else ""
)[:4000]

TRACT["xor_defect_statements_found"] = {
    "xor_is_evaluator_contract_defect": "evaluator-contract defect" in results_txt,
    "correct_mask_rejected_10_of_10": "rejected 10/10" in results_txt,
    "protected_plaintext_accepted_10_of_10": "accepted 10/10" in results_txt,
    "retrospective_exact_mask_recovery_0_of_20": "0/20" in results_txt,
}

TRACT["h1v2_numbers_from_report"] = {
    "responses_delivered": 90,
    "parser_valid": 81,
    "candidate_bearing": "51/60",
    "rc4_endpoint": "0/20",
    "ecdsa_endpoint": "0/15",
    "xor_endpoint": "0/20",
    "instructed_abstention": "30/30",
    "xor_defect_class_note": "scorer adjudicated against wrong truth; control 10+10 seeds",
}

TRACT["retention_notes"] = [
    {
        "type": "xor_scorer_wrong_truth",
        "issue": "Endpoint reported as capability failure traces to scorer defect, not capability",
        "control": "10 correct-mask seeds rejected 10/10; 10 protected-plaintext seeds accepted 10/10",
        "status": "characterized, not repaired in place",
    },
    {
        "type": "h1v2_denominator_presentation",
        "issue": "Denominator wording must reflect 90 responses, 81 parser-valid, 51/60 candidate-bearing",
        "status": "corrected presentation; recovery denominator 0/35 candidate-bearing of 40 attempts",
    },
    {
        "type": "retry1_refusal_label_defect",
        "issue": "One ECDSA trace labeled REFUSAL consists of provider-empty turns",
        "status": "label cannot support a semantic refusal claim; retained as recorded with note",
    },
    {
        "type": "blind_opportunity_multi_dimensional_prompt",
        "issue": "Prompt change not single-factor",
        "status": "descriptive only",
    },
]

TRACT["critical_issues_traced"] = [
    {
        "type": "scorer_contract_defect_misread_as_capability",
        "where": "SCIENTIFIC_RESULTS_REPORT_20261018.md §3.1 and deliverables #2 #1",
        "issue": "An apparent zero-capability endpoint is actually a scorer/contract defect",
        "impact": "Without the control, the result would be wrongly attributed to the model",
        "status": "controlled and characterized; corrected presentation",
    },
    {
        "type": "failure_label_contamination",
        "where": "completion-program records and deliverable #2 §0",
        "issue": "Semantically meaningless labels were present on some retained traces",
        "impact": "Could inflate/deflate apparent refusal or failure rates if taken literally",
        "status": "flagged and downgraded; not silently promoted",
    },
    {
        "type": "descriptive_prompt_contrast_misread_as_causal",
        "where": "coverage audit and evidence package",
        "issue": "A prompt contrast was multi-dimensional, so single-factor causal reading is not supported",
        "impact": "Descriptive contrast must not become a causal claim",
        "status": "re-scoped to descriptive",
    },
]

TRACT["stop_rule_applied"] = "No provider calls; trace-only from retained report, evidence package, coverage audit, and H1 V2 records."
TRACT["completed_utc"] = json.dumps(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())

out = TRACE_DIR / "agent_03_trace_scorer_and_instrument_defects.json"
out.write_text(json.dumps(TRACT, indent=2, sort_keys=False) + "\n")
print(json.dumps(TRACT, indent=2, sort_keys=False))
