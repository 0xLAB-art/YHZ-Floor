import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "sp2027/benchmarks"
DEST = ROOT / "sp2027/analysis/reviewer_resolution_20261015/R8/APPLICABILITY.json"
DIRECTORIES = {"Cybench": "cybench", "NYU CTF Bench": "nyu_ctf_bench", "CVE-Bench": "cve_bench",
               "Incalmo": "incalmo", "AgentHarm": "agentharm", "WebSP-Eval": "websp_eval"}
FIELDS = [("clock", 1), ("oracle_independence", 3), ("failure_retention", 4), ("trace", 5),
          ("generated_artifacts", 6), ("weakness_attribution", 8), ("discovery_vs_execution", 9),
          ("query_accounting", 10), ("reconstruction_probe", None)]


def main():
    rows = list(csv.DictReader((BASE / "summary.csv").open()))
    output = []
    inputs = [BASE / "summary.csv", BASE / "RUBRIC.md"]
    for benchmark, directory in DIRECTORIES.items():
        source = BASE / directory / "fields.md"
        inputs.append(source)
        text = source.read_text()
        worksheet = {}
        for line in text.splitlines():
            match = re.match(r"\|\s*(\d+)\s*\|", line)
            if match:
                number = int(match.group(1))
                parts = line.split("|", 4)
                worksheet[number] = {"value": parts[3].strip(), "evidence": parts[4].strip().rstrip("|").strip()}
        row = next(r for r in rows if r["benchmark"] == benchmark)
        for index, (field, number) in enumerate(FIELDS, 1):
            cell = worksheet.get(number, {}) if number else {}
            domain_flag = "domain-n/a" in cell.get("value", "").lower() or "d-n/a" in row[field].lower()
            output.append({"benchmark": benchmark, "field": f"F{index}", "raw_frozen_value": row[field],
                           "worksheet_row": number, "worksheet_value": cell.get("value"),
                           "applicability": "worksheet_explicit_domain_na" if domain_flag else "not_separately_adjudicated",
                           "scope": "Applicability metadata extracted from existing judgments, not new independent ratings",
                           "evidence_pointer": str(source.relative_to(ROOT)) + (f"#worksheet-row-{number}" if number else "#reconstruction-probe"),
                           "evidence_note": cell.get("evidence", "See worksheet reconstruction-probe section")})
    flagged = [(r["benchmark"], r["field"]) for r in output if r["applicability"] == "worksheet_explicit_domain_na"]
    expected = [("AgentHarm", "F5"), ("AgentHarm", "F6"), ("WebSP-Eval", "F6")]
    if len(output) != 54 or flagged != expected:
        raise ValueError(f"Unexpected frozen applicability extraction: {flagged}")
    result = {"scope": "Frozen semantic status, applicability note and provenance are separate axes; no benchmark quality aggregate computed",
              "cells": output, "explicit_domain_na": flagged,
              "other_applicability": "Not separately adjudicated, not assumed applicable",
              "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"cells": len(output), "explicit_domain_na_notes": flagged, "remaining_applicability_not_separately_adjudicated": len(output)-len(flagged)}))


if __name__ == "__main__":
    main()
