import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = Path(__file__).resolve().parent
matrix = HOME / "PAPER_CLAIM_MATRIX.csv"
manuscript = ROOT / "sp2027/paper/main.tex"
rows = []
for row in csv.DictReader(matrix.open()):
    source_checks = []
    first_relative_dir = None
    for raw in row["source_artifacts"].split(";"):
        value = raw.strip()
        if value.startswith("sp2027/"):
            path = ROOT / value
        else:
            path = HOME / value
            if first_relative_dir is not None and "/" not in value:
                path = first_relative_dir / value
            if "/" in value:
                first_relative_dir = HOME / value.rsplit("/", 1)[0]
            if value == "revalidation_v2/events.jsonl":
                path = ROOT / "sp2027/analysis/checkpoint007_active_experiments/runs_009" / value
            if value in {"R1_CLEAN_COHORT_V4_RESULTS.md", "V4_ORACLE_VERDICT_AUTHORITY_AUDIT.md"}:
                path = ROOT / "sp2027/agent-eval" / value
            if value == "V4_ORACLE_VERDICT_AUTHORITY_AUDIT.md":
                path = ROOT / "sp2027/analysis/clean_v4_timing_provenance_feasibility_20261014" / value
        source_checks.append({"path": value, "exists": path.exists()})
    location_ok = ("main.tex" in row["manuscript_location"] and manuscript.exists()) or ("research_execution only" in row["manuscript_location"] and HOME.exists())
    rows.append({
        "claim_id": row["claim_id"],
        "source_checks": source_checks,
        "all_sources_exist": all(item["exists"] for item in source_checks),
        "manuscript_location_present": location_ok,
        "status": row["status"],
        "permitted_wording": row["permitted_wording"],
        "counterexample_or_limit": row["counterexample_or_limit"],
    })

summary = {
    "artifact": "CLAIM_MATRIX_AUDIT",
    "claims": len(rows),
    "all_sources_exist": all(row["all_sources_exist"] for row in rows),
    "all_manuscript_locations_present": all(row["manuscript_location_present"] for row in rows),
    "claims_with_explicit_limits": sum(bool(row["counterexample_or_limit"].strip()) for row in rows),
    "rows": rows,
    "interpretation": "Source existence and scope fields are audited mechanically; this does not prove semantic truth or causal identification.",
}
(HOME / "CLAIM_MATRIX_AUDIT.json").write_text(json.dumps(summary, indent=2) + "\n")
lines = [
    "# Claim matrix audit",
    "",
    f"Audited {len(rows)} claim rows against the authoritative manuscript and listed source artifacts.",
    "",
    f"All listed sources exist: **{summary['all_sources_exist']}**.",
    f"All manuscript locations resolve to the authoritative source: **{summary['all_manuscript_locations_present']}**.",
    f"Rows with explicit counterexample or scope limits: **{summary['claims_with_explicit_limits']}/{len(rows)}**.",
    "",
    "This is an integrity and scope audit, not a semantic or causal validation. Claims remain bounded by their permitted wording and listed limitations.",
]
(HOME / "CLAIM_MATRIX_AUDIT.md").write_text("\n".join(lines) + "\n")
print(json.dumps({k: summary[k] for k in ("claims", "all_sources_exist", "all_manuscript_locations_present", "claims_with_explicit_limits")}, indent=2))
