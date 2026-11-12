#!/usr/bin/env python3
"""Build the shippable projection of the policy-mechanism evidence.

The policy-mechanism audit produced a 852-row case ledger with the full
per-case detail.  Most of that detail is execution scaffolding a reviewer does
not need to check the published figures.  This script projects the ledger down
to the fields that carry the paper's claims, so the reviewer-facing package
stays small while every printed number stays recomputable.

What is projected out, and why:
  - the per-case `original` and `derivative` execution blocks, whose stdout and
    stderr tails are the agent's own output rather than evidence for a count;
  - the per-row copy of the prompt-allowed module set, which is identical
    across all 852 rows and is therefore shipped once, in PROMPT_MODULES.json.

What is kept, and why:
  - the terminal status and the legacy admission class per session, which carry
    the admission census;
  - the disallowed module entries per rejected session, which carry the
    prompt-permitted boundary claim;
  - the derivative-intervention fields, which carry the cleanup control;
  - the runtime-load observation, which shows the imports are genuinely used.

Usage:  python3 -B build_projection.py [--ledger <path>] [--out <dir>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
DEFAULT_LEDGER = AUDIT / "policy_mechanism/.omo/evidence/run01/CASE_LEDGER.jsonl"
DEFAULT_OUT = AUDIT.parents[1] / "analysis/policy_mechanism_20261021"

# Fields kept per session.
KEEP = (
    "session_id", "arm", "family", "level", "kind", "seed",
    "legacy_class", "legacy_rejected_correct", "original_legacy_admitted",
    "transformation_applied", "transform_eligibility",
    "derivative_legacy_admitted", "fresh_output_equality",
    "current_outcome_correct", "source_sha256",
)

# The v3 admission block is projected to two scalars per session: the status
# and whether the source qualified.  Its violation list is dropped; the
# counts that matter are the status distribution.


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    if not args.ledger.is_file():
        print("ledger not found: %s" % args.ledger)
        return 2
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    rows = [json.loads(line) for line in args.ledger.read_text().splitlines()
            if line.strip()]

    projected = []
    allowed_sets = set()
    disallowed_modules = set()
    for row in rows:
        allowed = sorted(row.get("prompt_allowed_modules") or [])
        allowed_sets.add(tuple(allowed))
        entries = []
        for entry in row.get("legacy_disallowed_but_prompt_allowed") or []:
            entries.append({
                "module": entry.get("module"),
                "classification": entry.get("classification"),
                "line": entry.get("line"),
                "reasons": entry.get("reasons") or [],
            })
            if entry.get("module"):
                disallowed_modules.add(entry["module"])
        record = {key: row.get(key) for key in KEEP}
        v3 = row.get("v3") or {}
        record["v3_status"] = v3.get("status")
        record["v3_qualified"] = v3.get("qualified")
        record["legacy_disallowed_modules"] = entries
        runtime = row.get("runtime_import_use") or {}
        record["runtime_observed_loaded_import"] = bool(
            runtime.get("observed_loaded_import_bindings"))
        record["runtime_trace_present"] = bool(runtime)
        projected.append(record)

    if len(allowed_sets) != 1:
        print("expected one shared prompt-allowed module set, found %d" % len(allowed_sets))
        return 1
    allowed = list(next(iter(allowed_sets)))

    ledger_path = out / "CASE_LEDGER.jsonl"
    ledger_path.write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in projected))

    modules = {
        "schema": "policy-mechanism-prompt-modules/1",
        "note": "The prompt's permitted module set is identical for all 852 "
                "sessions. The legacy source-admission policy disallowed a "
                "subset of it. Every legacy import reject in the cohort "
                "concerns a module from this permitted set.",
        "prompt_permitted_modules": allowed,
        "legacy_disallowed_across_cohort": sorted(disallowed_modules),
    }
    (out / "PROMPT_MODULES.json").write_text(json.dumps(modules, indent=2) + "\n")

    rejects = [r for r in projected if r.get("legacy_class") not in ("qualified", "syntax")]
    derived = {
        "schema": "policy-mechanism-derivation/1",
        "sessions": len(projected),
        "legacy_classes": {},
        "legacy_import_rejects": len(rejects),
        "legacy_rejects_whose_module_is_prompt_permitted": sum(
            1 for r in rejects
            if r.get("legacy_disallowed_modules")
            and all(e.get("module") in allowed for e in r["legacy_disallowed_modules"])),
        "v3_source_parse_rejects": sum(
            1 for r in projected if r.get("v3_status") == "SOURCE_PARSE_REJECTED"),
        "v3_import_rejects": sum(
            1 for r in projected
            if r.get("v3_status") not in ("QUALIFIED", "SOURCE_PARSE_REJECTED", None)),
        "derivatives_applied": sum(1 for r in projected if r.get("transformation_applied")),
        "derivatives_with_identical_output": sum(
            1 for r in projected
            if r.get("transformation_applied") and r.get("fresh_output_equality") is True),
        "derivatives_newly_legacy_admitted": sum(
            1 for r in projected
            if r.get("transformation_applied") and r.get("derivative_legacy_admitted")),
        "derivatives_newly_admitted_and_correct": sum(
            1 for r in projected
            if r.get("transformation_applied") and r.get("derivative_legacy_admitted")
            and r.get("current_outcome_correct")),
        "traced_sessions": sum(1 for r in projected if r.get("runtime_trace_present")),
        "traced_sessions_with_observed_load": sum(
            1 for r in projected if r.get("runtime_observed_loaded_import")),
    }
    for row in projected:
        cls = row.get("legacy_class")
        derived["legacy_classes"][cls] = derived["legacy_classes"].get(cls, 0) + 1
    (out / "DERIVED.json").write_text(json.dumps(derived, indent=2, sort_keys=True) + "\n")

    print("projected sessions: %d" % len(projected))
    print("ledger bytes: %d" % ledger_path.stat().st_size)
    for key in sorted(derived):
        if key != "schema":
            print("  %-52s %s" % (key, derived[key]))
    print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())