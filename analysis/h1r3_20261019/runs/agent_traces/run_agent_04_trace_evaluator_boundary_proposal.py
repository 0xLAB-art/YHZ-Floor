#!/usr/bin/env python3
"""Agent 4 of 5: trace HEB-1 evaluator-boundary novelty proposal.

Scope:
- Read the proposal/design records for HEB-1.
- Identify the gating requirements, missing pieces, and open risks.
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
    "agent": "trace_agent_04_evaluator_boundary_proposal",
    "scope": "HEB-1 cross-boundary verdict promotion proposal/design",
    "provider_calls": False,
    "started_utc": json.dumps(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()),
}

proposal = ROOT / "EVALUATOR_BOUNDARY_NOVELTY_PROPOSAL.md"
TRACT["proposal_exists"] = proposal.exists()
TRACT["proposal_bytes"] = proposal.stat().st_size if proposal.exists() else None

def load_text(p):
    try:
        return p.read_text()
    except Exception as e:
        return ""

txt = load_text(proposal)

TRACT["headings_found"] = [ln.strip() for ln in txt.splitlines() if ln.strip().startswith("#")][:40]

# Pull the decision/overall position lines if present
def extract_section(title, text, max_len=1800):
    i = text.find(title)
    if i < 0:
        return None
    j = text.find("\n## ", i + len(title))
    if j < 0:
        j = len(text)
    return text[i:j].strip()

TRACT["status_from_review_response"] = (
    "HEB-1 is a proposal; no implementation campaign, no provider calls, no result"
    if "proposal" in txt.lower() or "proposal" in load_text(HERE / "NOVELTY_REVIEW_RESPONSE_20261018.md").lower()
    else None
)

TRACT["gates_and_requirements_traced"] = [
    {
        "type": "novelty_must_be_narrower_than_oracle_integrity",
        "issue": "The proposal must differentiate from generic oracle-integrity/evidence-binding defects",
        "note": "Prior-art matrix handles existential overlap",
    },
    {
        "type": "verdict_and_attribution_must_be_separate",
        "issue": "Cryptographic reference verdict and exploitation-attribution claim must be evaluated separately",
        "note": "Certificate must carry per-class status and explicit non-claims",
    },
    {
        "type": "false_attribution_promotion_is_the_hypothesis",
        "issue": "Primary endpoint is the false attribution-promotion rate under bad cross-run/artifact joins",
        "note": "Falsification condition exists",
    },
    {
        "type": "fair_validator_comparison_required",
        "issue": "Schema-only, hash-based, and claim-specific validators must be compared fairly with equivalent evidence inputs",
        "note": "Blind trust model must be stated",
    },
    {
        "type": "ground_truth_must_be_recomputed",
        "issue": "Independent adjudicator must recompute predicate from immutable target + candidate, not copy stored labels",
        "note": "Mislabeled fixtures should be overruled",
    },
    {
        "type": "held_out_variation_required",
        "issue": "Held-out set must include at least one composition pattern not used during validator development",
        "note": "Current held-out limitation recorded",
    },
    {
        "type": "no_all_reject_validator",
        "issue": "Validator must preserve legitimate successful cases",
        "note": "Secondary endpoints include false rejection",
    },
    {
        "type": "no_perfect_synthetic_only_novelty_claim",
        "issue": "Perfect detection on self-generated faults alone is not sufficient for novelty",
        "note": "Requires closest-prior-art review + independent reproduction",
    },
]

TRACT["current_status_summary"] = {
    "implementation": "none",
    "provider_calls": "none",
    "completed_experiment": "none",
    "novelty_result": "none",
    "recommended_next_action_from_review": "offline prior-art verification + protocol freeze, then implementation against gates; no provider calls until gates approved",
}

TRACT["critical_issues_traced"] = [
    {
        "type": "proposal_not_yet_validated",
        "issue": "HEB-1 remains design-stage; it is not a validated security finding yet",
        "status": "tracked as blocked pending offline gates",
    },
    {
        "type": "novelty_requires_beyond_generic_warning",
        "issue": "Any future claim must demonstrate a security-specific consequence beyond a generic evaluator warning",
        "status": "open requirement",
    },
    {
        "type": "prior_art_overlap_must_be_ruled_out",
        "issue": "Multiple relevant evaluator/benchmark works already exist",
        "status": "open requirement before novelty framing",
    },
]

TRACT["stop_rule_applied"] = "No provider calls; trace-only from proposal/design records and review-response artifacts."
TRACT["completed_utc"] = json.dumps(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())

out = TRACE_DIR / "agent_04_trace_evaluator_boundary_proposal.json"
out.write_text(json.dumps(TRACT, indent=2, sort_keys=False) + "\n")
print(json.dumps(TRACT, indent=2, sort_keys=False))
