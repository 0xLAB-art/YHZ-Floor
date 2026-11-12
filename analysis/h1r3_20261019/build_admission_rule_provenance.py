#!/usr/bin/env python3
"""Derive the admission-rule provenance record.

The manuscript's evaluator-policy result is a counterfactual over admission
rules.  To say which rule a prompt declared, when, and what a rule would have
rejected, a reviewer needs the prompt text and the source checker's own
allowlist.  This script extracts both from the retained sources and records
their digests, so the claim is checkable against shipped bytes rather than
against the manuscript's prose.

It reads only retained files.  It makes no provider call and contacts no
target.

Usage:  python3 -B build_admission_rule_provenance.py [--root <dir>] [--out <file>]
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Where the sources live, relative to the project root.
SOURCES = {
    "contract_policy": "sp2027/analysis/h1r3_20261019/h1r3_contract.py",
    "prompt_builder": "sp2027/analysis/h1r3_20261019/h1r3_core.py",
    "earlier_checker_runner": "sp2027/analysis/run_contract_sound_agent_pilot.py",
    "earlier_source_checker": "sp2027/analysis/contract_sound_repaired_pipeline.py",
    "earlier_lane_prompt": "sp2027/research_execution/info_contract_2x2_20261018/PREREGISTRATION.md",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module_allowlist(path: Path, name: str) -> list[str] | None:
    """Read a module allowlist from a python source by attribute name."""
    try:
        tree = ast.parse(path.read_text(errors="replace"))
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            value = node.value
            if isinstance(value, ast.Set) and name in targets:
                return sorted(e.value for e in value.elts
                              if isinstance(e, ast.Constant)
                              and isinstance(e.value, str))
            if isinstance(value, ast.Dict):
                # a policy table: {"name": {modules}}
                for k, v in zip(value.keys, value.values):
                    if (isinstance(k, ast.Constant) and k.value == name
                            and isinstance(v, ast.Set)):
                        return sorted(e.value for e in v.elts
                                      if isinstance(e, ast.Constant)
                                      and isinstance(e.value, str))
            # a plain assignment whose value is a literal list
            if name in targets and isinstance(value, (ast.List, ast.Tuple)):
                return sorted(e.value for e in value.elts
                              if isinstance(e, ast.Constant)
                              and isinstance(e.value, str))
    return None


def prompt_allowed_line(path: Path) -> str | None:
    """The prompt line that names the permitted imports, if there is one."""
    for line in path.read_text(errors="replace").splitlines():
        if "Allowed imports" in line:
            return line.strip()
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=HERE.parent.parent,
                    help="the sp2027 project root")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    root = args.root.resolve()
    out = args.out or (root / "sp2027/analysis/h1r3_20261019/ADMISSION_RULE_PROVENANCE.json")

    src = {k: root / v for k, v in SOURCES.items()}
    for k, p in src.items():
        if not p.is_file():
            print("missing source %s: %s" % (k, p))
            return 2

    contract_allowed = module_allowlist(src["contract_policy"], "v3")
    legacy_allowed = module_allowlist(src["earlier_source_checker"], "ALLOWED_IMPORTS")
    runner_allowed = module_allowlist(src["earlier_checker_runner"], "allowed")

    h1r3_prompt = prompt_allowed_line(src["prompt_builder"])
    lane_prompt = prompt_allowed_line(src["earlier_lane_prompt"])

    def listed(line):
        if not line:
            return None
        m = re.search(r"Allowed imports(?: are)?[: ]+(.+?)\.", line)
        if not m:
            return None
        out = []
        for x in m.group(1).split(","):
            x = x.strip()
            if x.lower().startswith("and "):
                x = x[4:].strip()
            if x:
                out.append(x)
        return sorted(out)

    record = {
        "schema": "h1r3-admission-rule-provenance/1",
        "boundary": (
            "The record states which prompt declared which import set and when, "
            "and what each source checker's own allowlist was. The freeze "
            "timestamp of the protocol is the project's own record; the "
            "digests below are of the retained source files, so a reviewer can "
            "check each statement against the bytes."
        ),
        "rules": {
            "in_force": {
                "name": "v3",
                "declared_in_prompt": True,
                "prompt_line": h1r3_prompt,
                "prompt_permitted_modules": listed(h1r3_prompt),
                "checker_allowlist": contract_allowed,
                "source": SOURCES["contract_policy"],
                "source_sha256": sha256(src["contract_policy"]),
                "prompt_source": SOURCES["prompt_builder"],
                "prompt_source_sha256": sha256(src["prompt_builder"]),
                "consistent_with_prompt": bool(
                    contract_allowed and listed(h1r3_prompt)
                    and set(contract_allowed) == set(listed(h1r3_prompt))),
            },
            "earlier": {
                "name": "legacy-2026-10-18",
                "declared_in_prompt": False,
                "checker_allowlist": legacy_allowed,
                "runner_allowlist": runner_allowed,
                "source": SOURCES["earlier_source_checker"],
                "source_sha256": sha256(src["earlier_source_checker"]),
                "runner_source": SOURCES["earlier_checker_runner"],
                "runner_source_sha256": sha256(src["earlier_checker_runner"]),
                "in_one_2026_10_18_lane": {
                    "prompt_line": lane_prompt,
                    "prompt_permitted_modules": listed(lane_prompt),
                    "prompt_source": SOURCES["earlier_lane_prompt"],
                    "prompt_source_sha256": sha256(src["earlier_lane_prompt"]),
                    "declared_but_rejected_by_checker": sorted(
                        set(listed(lane_prompt) or []) - set(legacy_allowed or [])),
                    "allowed_but_not_declared": sorted(
                        set(legacy_allowed or []) - set(listed(lane_prompt) or [])),
                },
            },
        },
    }
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print("wrote %s" % out)
    r = record["rules"]
    print("  in force: prompt-consistent = %s (%d modules)"
          % (r["in_force"]["consistent_with_prompt"],
             len(r["in_force"]["checker_allowlist"] or [])))
    print("  earlier : prompt-consistent = False, %d modules"
          % len(r["earlier"]["checker_allowlist"] or []))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())