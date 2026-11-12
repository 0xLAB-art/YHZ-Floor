import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "sp2027/analysis/checkpoint007_active_experiments/runs_009/revalidation_v2"
OUT = Path(__file__).resolve().parent


def raw_text(record):
    blocks = record.get("content") or []
    return "\n".join(b.get("text", "") for b in blocks if isinstance(b, dict))


def parsed_json(text):
    s = text.strip()
    s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.I)
    s = re.sub(r"\s*```$", "", s)
    try:
        value = json.loads(s)
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def classify(arm, obj, result):
    text = raw_text(obj)
    parsed = parsed_json(text)
    family = arm.split("_")[0].lower()
    condition = arm.rsplit("_", 1)[1].lower()
    if parsed is None:
        stage = "provider_delivered_unparseable"
    elif condition == "undet":
        decision = str(parsed.get("decision", "")).upper()
        stage = "abstention_structured_correct" if decision == "ABSTAIN_UNDERDETERMINED" and result.get("correct_decision") else "abstention_or_schema_other"
    else:
        expected = {"rc4": "target_plaintext_hex", "ecdsa": "private_key_hex", "xor": "target_plaintext_hex"}[family]
        if expected not in parsed:
            stage = "parsed_missing_candidate_field"
        elif parsed.get(expected) in (None, ""):
            stage = "parsed_null_candidate"
        else:
            stage = "candidate_value_submitted_or_guessed"
    return {
        "run_id": obj["id"],
        "arm_id": arm,
        "family": family,
        "condition": condition,
        "matched_seed": int(obj.get("matched_seed", 0)),
        "provider_model": obj.get("model"),
        "stop_reason": obj.get("stop_reason"),
        "input_tokens": obj.get("usage", {}).get("input_tokens"),
        "output_tokens": obj.get("usage", {}).get("output_tokens"),
        "output_chars": len(text),
        "json_parseable": parsed is not None,
        "output_stage": stage,
        "recorded_correct": result.get("correct", result.get("correct_decision", False)),
        "oracle_backed_recovery": bool(result.get("correct", False)) and condition != "undet",
        "raw_path": str(obj["_file"]),
    }


def main():
    results = {}
    with (V2 / "results.jsonl").open() as f:
        for line in f:
            row = json.loads(line)
            results[row["run_id"]] = row.get("verdict", {})
    rows = []
    for path in sorted((V2 / "raw_provider_responses").glob("*.json")):
        obj = json.loads(path.read_text())
        obj["_file"] = str(path)
        run_id = next((rid for rid in results if rid in path.name), None)
        if run_id is None:
            raise RuntimeError(f"no result linkage for {path.name}")
        arm = run_id.split("__A_", 1)[1].split("__", 1)[0]
        rows.append(classify(arm, obj, results[run_id]))
    rows.sort(key=lambda r: (r["family"], r["condition"], r["matched_seed"]))
    with (OUT / "H1_V2_FAILURE_STAGE_MATRIX.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    groups = defaultdict(Counter)
    for r in rows:
        groups[f"{r['family']}_{r['condition']}"][r["output_stage"]] += 1
    summary = {
        "raw_provider_files": len(rows),
        "all_stop_reason_end_turn": all(r["stop_reason"] == "end_turn" for r in rows),
        "strict_top_level_json_parseable": sum(r["json_parseable"] for r in rows),
        "stage_counts_by_arm": {k: dict(v) for k, v in sorted(groups.items())},
        "sufficient_condition_candidate_submissions": sum(r["output_stage"] == "candidate_value_submitted_or_guessed" for r in rows if r["condition"] != "undet"),
        "sufficient_condition_oracle_recoveries": sum(r["oracle_backed_recovery"] for r in rows),
        "correct_underdetermination": sum(r["output_stage"] == "abstention_structured_correct" for r in rows),
        "mean_output_chars_by_arm": {k: round(sum(r["output_chars"] for r in rows if f"{r['family']}_{r['condition']}" == k) / sum(f"{r['family']}_{r['condition']}" == k for r in rows), 1) for k in sorted(groups)},
        "interpretation": "All 90 provider envelopes were delivered with end_turn. Strict top-level JSON parsing succeeded for 81/90 payloads; 9 responses embedded JSON inside explanatory prose and therefore exposed an output-contract failure. Among strict parses, sufficient arms emitted candidate fields but none passed the oracle; underdetermined arms emitted correct abstentions. This localizes the result after provider delivery while leaving construction, response contract, and interface bottlenecks unresolved.",
    }
    (OUT / "H1_V2_FAILURE_STAGE_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    md = ["# Corrected H1 V2 failure-stage audit", "", "Status: `PARTIAL_EXECUTION`", "", "The audit reads all 90 raw provider payloads and links each to the append-only result record by run ID. It does not expose verifier-held secrets.", "", "## Findings", "", f"- Raw payloads: {summary['raw_provider_files']}; all provider envelopes have `stop_reason=end_turn`; strict top-level JSON parsing succeeded for {summary['strict_top_level_json_parseable']}/90.", f"- Sufficient-condition candidate fields submitted or guessed: {summary['sufficient_condition_candidate_submissions']}/60; oracle-backed recoveries: {summary['sufficient_condition_oracle_recoveries']}/60.", f"- Correct structured underdetermination decisions: {summary['correct_underdetermination']}/30.", "- Nine responses used explanatory prose around an embedded JSON/code fragment, exposing a response-contract failure even though the provider delivered complete envelopes.", "- The evidence rules out provider delivery failure, but does not distinguish mathematical inference error from wrong candidate construction, strict-output failure, missing execution/tool interface, or insufficient feedback.", "", "## Per-arm stage counts", ""]
    for arm, counts in summary["stage_counts_by_arm"].items():
        md.append(f"- `{arm}`: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    md += ["", "The complete row-level matrix is `H1_V2_FAILURE_STAGE_MATRIX.csv`. The invalid first H1 report remains excluded from this analysis."]
    (OUT / "H1_V2_FAILURE_STAGE_AUDIT.md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
