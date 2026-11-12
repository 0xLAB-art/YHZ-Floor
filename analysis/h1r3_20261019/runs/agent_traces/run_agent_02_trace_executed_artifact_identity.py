#!/usr/bin/env python3
"""Agent 2 of 5: trace executed-artifact identity defect.

Scope:
- Surrogate conversion attempt 3 identity mismatch.
- Use retained dossier/replay evidence only.
- No provider calls.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path("sp2027/analysis")
HERE = ROOT / "h1r3_20261019"
TRACE_DIR = HERE / "runs" / "agent_traces"
TRACE_DIR.mkdir(parents=True, exist_ok=True)

dossier = ROOT / "postfreeze_integrity_resolution_20261018"
TRACT = {
    "agent": "trace_agent_02_executed_artifact_identity",
    "scope": "surrogate attempt-3 identity defect and its resolution",
    "provider_calls": False,
    "started_utc": json.dumps(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()),
}

TRACT["dossier_dir_exists"] = dossier.exists()
TRACT["dossier_index"] = sorted(p.name for p in dossier.iterdir()) if dossier.exists() else []

def load(p):
    try:
        return json.loads(p.read_text())
    except Exception as e:
        return {"_load_error": str(e)}

evidence_candidates = {
    "executed_candidate_reconstructed_path": dossier / "evidence" / "executed_candidate_reconstructed.py",
    "replay_results": dossier / "evidence" / "replay_results.json",
    "replay_manifest": dossier / "evidence" / "SHA256SUMS",
}

TRACT["evidence_files"] = {k: str(v) for k, v in evidence_candidates.items()}
TRACT["evidence_present"] = {k: v.exists() for k, v in evidence_candidates.items()}

replay = load(evidence_candidates["replay_results"]) if evidence_candidates["replay_results"].exists() else {}
TRACT["replay_high_level"] = {
    "full_match": replay.get("full_match"),
    "claim_sha256": replay.get("claim_sha256"),
    "claim_sha_match_run_result": replay.get("claim_sha256") == replay.get("run_result_candidate_sha256"),
    "oracle_queries_replayed": replay.get("oracle_queries"),
}

recon = evidence_candidates["executed_candidate_reconstructed_path"]
if recon.exists():
    try:
        src = recon.read_text()
        TRACT["reconstructed_source_sha256"] = hashlib.sha256(src.encode()).hexdigest()
        TRACT["reconstructed_source_bytes"] = len(src.encode())
        TRACT["contains_code_markers"] = ("CODE_BEGIN" in src) or ("```" in src)
    except Exception as e:
        TRACT["reconstructed_read_error"] = str(e)

TRACT["recorded_executed_candidate_sha256"] = "a5e8ed51..."
TRACT["recorded_archived_candidate_sha256"] = "4fbd70a0..."
TRACT["recorded_claim_object_sha256"] = "919ca521..."

TRACT["defect_summary"] = {
    "what_diverged": "executed agent-bytes vs archived candidate file",
    "resolution_method": "recover executed candidate from generator transcript; bit-exact replay against recorded oracle replies; live re-grade of reconstructed candidate",
    "preserved_limit": "archived on-disk file is a post-run replacement and is not used as executed bytes",
    "why_this_matters": "results must stand on hash-proven executed bytes, not on a replaced archived file",
}

TRACT["critical_issues_traced"] = [
    {
        "type": "executed_vs_archived_mismatch",
        "where": "postfreeze_integrity_resolution_20261018 and surrounding completion records",
        "issue": "Executed candidate bytes and archived candidate file did not agree",
        "impact": "Could promote wrong bytes if archived file were treated as executed",
        "status": "resolved by reconstruction + replay + live grading; archived file documented as post-run replacement",
    },
    {
        "type": "claim_hash_identity",
        "where": "same dossier",
        "issue": "Claim-object hash is defined on canonical claim JSON, not on candidate source alone",
        "impact": "Source hash and claim hash must not be conflated",
        "status": "documented",
    },
]

TRACT["stop_rule_applied"] = "No provider calls; trace-only from retained integrity dossier and replay evidence."
TRACT["completed_utc"] = json.dumps(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())

out = TRACE_DIR / "agent_02_trace_executed_artifact_identity.json"
out.write_text(json.dumps(TRACT, indent=2, sort_keys=False) + "\n")
print(json.dumps(TRACT, indent=2, sort_keys=False))
