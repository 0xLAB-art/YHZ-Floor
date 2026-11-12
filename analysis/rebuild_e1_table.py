#!/usr/bin/env python3
"""Reconstruct E1 verdicts from retained worksheets, not human re-grading."""
import argparse
import json
import re
from pathlib import Path

BENCHMARKS = {"Cybench": "cybench", "NYU CTF Bench": "nyu_ctf_bench",
              "CVE-Bench": "cve_bench", "Incalmo": "incalmo",
              "AgentHarm": "agentharm", "WebSP-Eval": "websp_eval"}
WORKSHEET_ROWS = [1, 3, 4, 5, 6, 8, 9, 10]


def worksheet_values(text):
    values = {}
    for line in text.splitlines():
        match = re.match(r"\|\s*(\d+)\s*\|[^|]+\|\s*\*\*(yes|partial|no)\*\*", line)
        if match and int(match[1]) in WORKSHEET_ROWS:
            number = int(match[1])
            if number in values:
                raise ValueError("duplicate worksheet field")
            values[number] = match[2]
    if set(values) != set(WORKSHEET_ROWS):
        raise ValueError("missing graded worksheet field")
    outcome = re.search(r"^- Outcome:\s*`([^`]+)`", text, re.M)
    if not outcome:
        raise ValueError("missing reconstruction-probe outcome")
    value = outcome[1]
    if value.startswith("cannot_reconstruct"):
        reconstruction = "no"
    elif value.startswith("partial("):
        reconstruction = "partial"
    elif value.startswith("reconstructed("):
        reconstruction = "yes"
    else:
        raise ValueError("unrecognized reconstruction outcome")
    return [values[key] for key in WORKSHEET_ROWS] + [reconstruction]


def printed_values(tex):
    table = tex.split(r"\label{tab:audit}", 1)[1].split(r"\bottomrule", 1)[0]
    verdicts = {}
    for name in BENCHMARKS:
        matches = [line for line in table.splitlines() if line.startswith(name + "~")]
        if len(matches) != 1:
            raise ValueError("missing or duplicate manuscript row: " + name)
        values = re.findall(r"\\f(yes|part|no)\b", matches[0])
        if len(values) != 9:
            raise ValueError("expected nine printed verdicts")
        verdicts[name] = ["partial" if value == "part" else value for value in values]
    return verdicts


def retained_worksheet_matrix(root):
    evidence = {name: worksheet_values((root / "sp2027/benchmarks" / directory / "fields.md").read_text())
                for name, directory in BENCHMARKS.items()}
    return {"cells": sum(map(len, evidence.values())), "rows": evidence,
            "all_nine_satisfied": [name for name, values in evidence.items() if set(values) == {"yes"}],
            "printed_table_checked": False,
            "boundary": "Mechanical reconstruction of retained judgments, not printed-table alignment or independent semantic/human re-audit."}


def reconstruct(root, require_alignment=True):
    retained = retained_worksheet_matrix(root)
    evidence = retained["rows"]
    printed = printed_values((root / "sp2027/paper/main.tex").read_text())
    differences = [{"benchmark": name, "field": f"F{number + 1}",
                    "worksheet": evidence[name][number], "printed": printed[name][number]}
                   for name in evidence for number in range(9)
                   if evidence[name][number] != printed[name][number]]
    if require_alignment and differences:
        raise ValueError("E1 printed table differs from retained worksheets: " + json.dumps(differences))
    return {**retained, "printed_table_differences": differences, "printed_table_checked": True,
            "boundary": "Mechanical reconstruction of retained judgments, not independent semantic or human re-audit. Historical first-pass CSV is retained separately for the AI diagnostic."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--show-differences", action="store_true")
    args = parser.parse_args()
    print(json.dumps(reconstruct(args.root, not args.show_differences), indent=2))
