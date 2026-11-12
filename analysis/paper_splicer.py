#!/usr/bin/env python3
"""Mechanically splice validated W3/W4 evidence into a paper copy.

Every inserted numeric value is loaded at runtime from the named evidence
artifact; this script transports values and does not interpret results.
Never edit main.tex or evidence files here.  The downstream results_lock.py
re-derives claims after a splice.  Usage: python3 paper_splicer.py --plan
or python3 paper_splicer.py --apply (writes main_spliced.tex only).
"""

import argparse
import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PAPER = HERE.parent / "paper" / "main.tex"
OUTPUT = HERE.parent / "paper" / "main_spliced.tex"
W3_PATH = HERE / "w3_fill_evidence.json"
BOUNDS_PATH = HERE / "bounds_tier_evidence.json"
AOR_PATH = HERE / "aor_runs_e2.json"
E4_PATH = HERE / "e4_sensitivity_results.json"


class SpliceError(Exception):
    """Raised when source marks or evidence cannot support a splice."""


def load_json(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def require_number(value, source):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SpliceError(f"{source}: expected a numeric value, got {value!r}")
    return value


def fixed(value, digits, source):
    return f"{require_number(value, source):.{digits}f}"


def ci_text(value, source):
    if not isinstance(value, list) or len(value) != 2:
        raise SpliceError(f"{source}: expected a two-value confidence interval")
    return f"[{fixed(value[0], 2, source)}, {fixed(value[1], 2, source)}]"


def make_table_values(w3):
    result = {}
    slots = w3.get("slots")
    if not isinstance(slots, dict):
        raise SpliceError("w3_fill_evidence.json: missing slots object")
    for slot in ("O1", "O2", "O3"):
        data = slots.get(slot)
        if not isinstance(data, dict):
            raise SpliceError(f"w3_fill_evidence.json: missing slots.{slot}")
        asr = data.get("asr", {})
        fsr = data.get("fsr", {})
        if "value" not in asr or "ci" not in asr or "fsr" not in fsr:
            raise SpliceError(f"w3_fill_evidence.json: incomplete ASR/FSR for {slot}")
        if "median_t_agent_s" not in data:
            raise SpliceError(f"w3_fill_evidence.json: missing median for {slot}")
        result[slot] = (
            f"{fixed(asr['value'], 3, f'{slot}.asr.value')} "
            f"{ci_text(asr['ci'], f'{slot}.asr.ci')}",
            fixed(fsr["fsr"], 3, f"{slot}.fsr.fsr"),
            f"{fixed(data['median_t_agent_s'], 1, f'{slot}.median_t_agent_s')}\\,s",
        )
    return result


def replacement_map(lines, w3):
    """Return 1-based line replacements and their artifact/key provenance."""
    tables = make_table_values(w3)
    replacements = {}
    sources = {}
    mark_values = {}
    table_rows = 0
    for index, line in enumerate(lines, 1):
        match = re.match(r"^(O[123])\b.*& \[PENDING-W3\] & \[PENDING-W3\] & \[PENDING-W3\] \\\\$", line.rstrip("\n"))
        if match:
            slot = match.group(1)
            vals = tables[slot]
            new_line = line
            for value in vals:
                new_line = new_line.replace("[PENDING-W3]", value, 1)
            replacements[index] = new_line
            mark_values[index] = list(vals)
            sources[index] = [
                f"w3_fill_evidence.json:slots.{slot}.asr.value/ci",
                f"w3_fill_evidence.json:slots.{slot}.fsr.fsr",
                f"w3_fill_evidence.json:slots.{slot}.median_t_agent_s",
            ]
            table_rows += 1
        elif "estimands and neither is optional~[PENDING-W3]" in line:
            clauses = []
            for slot in ("O1", "O2", "O3"):
                d = w3["slots"][slot]["operational_yield"]
                clauses.append(f"{slot} {d['num']}/{d['denom']}")
            value = " (" + "; ".join(clauses) + ")"
            replacements[index] = line.replace("~[PENDING-W3]", value, 1)
            mark_values[index] = [value.strip()]
            sources[index] = "w3_fill_evidence.json:slots.{O1,O2,O3}.operational_yield.num/denom"
        elif "against the independent oracle per" in (lines[index - 2] if index >= 2 else "") and "session~[PENDING-W3]" in line:
            clauses = []
            for slot in ("O1", "O2", "O3"):
                value = w3["slots"][slot]["fsr"]["fsr"]
                clauses.append(f"{slot} {fixed(value, 3, f'{slot}.fsr.fsr')}")
            replacements[index] = line.replace("~[PENDING-W3]", " (" + "; ".join(clauses) + ")", 1)
            mark_values[index] = ["(" + "; ".join(clauses) + ")"]
            sources[index] = "w3_fill_evidence.json:slots.{O1,O2,O3}.fsr.fsr"
    if table_rows != 3:
        raise SpliceError(f"expected 3 Table 3 slot rows, found {table_rows}")
    return replacements, sources, mark_values


def locate_marks(lines):
    marks = []
    text = "".join(lines)
    for match in re.finditer(r"\[PENDING-W[34][^\]]*\]", text):
        line_no = text.count("\n", 0, match.start()) + 1
        line = lines[line_no - 1]
        # Ignore explanatory comments; only inline manuscript marks are spliced.
        if line.lstrip().startswith("%"):
            continue
        marks.append((line_no, match.group(0), line.strip()))
    return marks


def build_plan():
    lines = PAPER.read_text(encoding="utf-8").splitlines(keepends=True)
    w3 = load_json(W3_PATH)
    # Load all requested artifacts during planning, even when a mark is held
    # for a human round. Their schemas are checked only for fields used here.
    bounds = load_json(BOUNDS_PATH)
    _aor = load_json(AOR_PATH)
    e4 = load_json(E4_PATH)
    replacements, sources, mark_values = replacement_map(lines, w3)
    marks = locate_marks(lines)
    plan = []
    mark_offsets = {}
    for line_no, tag, text in marks:
        if line_no in replacements:
            offset = mark_offsets.get(line_no, 0)
            values = mark_values[line_no]
            replacement = values[offset] if len(values) > 1 else values[0]
            mark_offsets[line_no] = offset + 1
            source = sources[line_no]
            if isinstance(source, list):
                source = source[offset]
            plan.append((line_no, tag, replacement, source))
    mapped = {line for line, _, _, _ in plan}
    human = []
    # These prose insertions are deliberately reserved for a wording round.
    anchors = (
        ("curves that keep outages visible", "w3_fill_evidence.json"),
        ("visible~[PENDING-W3] (Section", "w3_fill_evidence.json"),
        ("at $\\Delta$median $-1.70$\\,ms~[PENDING-W3", "aor_runs_e2.json"),
        ("corpus is itself a reported number~[PENDING-W3]", "w3_fill_evidence.json"),
        ("harness-timed $T_{\\mathrm{op}}$) fill at W3~[PENDING-W3]", "aor_runs_e2.json"),
        ("buys~[PENDING-W3]", "bounds_tier_evidence.json"),
        ("paper~[PENDING-W3:", "bounds_tier_evidence.json"),
        ("session~[PENDING-W3: full distribution", "aor_runs_e2.json"),
    )
    for line_no, tag, text in marks:
        if line_no in mapped:
            continue
        if tag.startswith("[PENDING-W4]"):
            campaign = e4.get("campaign") or e4.get("cohorts", {}).get("campaign")
            if not isinstance(campaign, dict):
                human.append((line_no, tag, "e4_sensitivity_results.json:campaign (campaign keys absent)"))
            else:
                human.append((line_no, tag, "e4_sensitivity_results.json:campaign (format review required)"))
            continue
        if not tag.startswith("[PENDING-W3"):
            continue
        artifact = next((src for anchor, src in anchors if anchor in text), None)
        if artifact is None:
            # KM and outage-band marks may move as manuscript text evolves.
            if "PENDING-W3" in text and ("censoring" in text or "competing risk" in text):
                artifact = "bounds_tier_evidence.json"
            else:
                raise SpliceError(f"unclassified W3 mark on line {line_no}: {text}")
        human.append((line_no, tag, artifact))
    expected_inline = 20  # 19 W3 marks plus the one W4 mark in this manuscript.
    if len(marks) != expected_inline:
        raise SpliceError(f"expected {expected_inline} inline W3/W4 marks, found {len(marks)}")
    return lines, replacements, sources, plan, sorted(human)


def print_plan(plan, human):
    print("MECHANICAL PLAN")
    for number, (line_no, tag, replacement, source) in enumerate(plan, 1):
        print(f"{number}. line {line_no} {tag} -> {replacement}  [source: {source}]")
    print("HUMAN WORDING NEEDED")
    for line_no, tag, source in human:
        print(f"- line {line_no} {tag}  [suggested source: {source}]")


def apply_plan(lines, replacements):
    output = list(lines)
    for line_no, replacement in replacements.items():
        output[line_no - 1] = replacement
    OUTPUT.write_text("".join(output), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true", help="print planned substitutions without writing")
    mode.add_argument("--apply", action="store_true", help="write the spliced paper copy")
    args = parser.parse_args()
    try:
        lines, replacements, _sources, plan, human = build_plan()
        if args.plan:
            print_plan(plan, human)
            return 0
        apply_plan(lines, replacements)
        counts = {"W3": 0, "W4": 0}
        for line_no, _tag, _replacement, _source in plan:
            counts["W4" if "PENDING-W4" in lines[line_no - 1] else "W3"] += 1
        print(f"W3 replacements: {counts['W3']}; W4 replacements: {counts['W4']}")
        print(f"W3/W4 marks retained for human wording: {len(human)}")
        print(f"Wrote {OUTPUT}")
        return 0
    except (OSError, json.JSONDecodeError, SpliceError, KeyError, TypeError) as exc:
        print(f"paper_splicer: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
