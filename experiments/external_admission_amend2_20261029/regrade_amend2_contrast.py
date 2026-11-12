#!/usr/bin/env python3
"""Amendment 2 — registered-quantity addendum.

The Phase-2 preregistration defines F1 on the **per-task representation
contrast** (RT minus R0 acceptance, pp) after regrading, not on admission
rates. This script computes that quantity from frozen inputs only.

Scope decision recorded here (and in PREREGISTRATION.md §7): the read-boundary
repair is an *interface* fix, not a policy axis, so it is applied to both arms.
Leaving it out of rule (b) would confound the two and make the registered
contrast unevaluable by construction. This is a documented deviation from the
amendment's "rule (b) unchanged" wording, and the un-repaired stress decisions
are retained alongside for transparency.

Inputs (all frozen, hash-asserted):
  regrade_results_amend2.json          per-program representation + oracle label
  external_admission_amend1_20261024/sessions/programs/*.py
  policies/rule_a_permissive_v4.py     declared rule v3 + repaired boundary,
                                       and the "legacy" stress module set

Outputs: regrade_contrast_amend2.json
"""

import collections
import hashlib
import importlib.util
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
AMD1 = HERE.parent / "external_admission_amend1_20261024"
OUT = HERE / "regrade_contrast_amend2.json"
MARGIN_PP = 10.0


def load_rule():
    spec = importlib.util.spec_from_file_location(
        "rule_v4", HERE / "policies/rule_a_permissive_v4.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rate(ok, n):
    return None if n == 0 else 100.0 * ok / n


def contrast(rows, key):
    """RT minus R0 acceptance over programs admitted under `key`."""
    arms = {}
    for arm in ("R0", "RT"):
        sel = [r for r in rows[arm] if r[key]]
        arms[arm] = {"ok": sum(1 for r in sel if r["oracle_match"]),
                     "n": len(sel)}
        arms[arm]["rate_pp"] = rate(arms[arm]["ok"], arms[arm]["n"])
    if arms["R0"]["rate_pp"] is None or arms["RT"]["rate_pp"] is None:
        return arms, None
    return arms, arms["RT"]["rate_pp"] - arms["R0"]["rate_pp"]


def main():
    rule = load_rule()
    base = json.loads((HERE / "regrade_results_amend2.json").read_text())
    rows = base["per_program"]

    by_task = collections.defaultdict(lambda: {"R0": [], "RT": []})
    for row in rows:
        path = AMD1 / row["program"]
        src = path.read_text()
        got = hashlib.sha256(src.encode()).hexdigest()
        if got != row["program_sha256"]:
            raise SystemExit(f"PROGRAM HASH MISMATCH: {row['program']}")
        row["_declared"] = rule.qualify_source(src, "v3")["qualified"]
        row["_stress_repaired"] = rule.qualify_source(src, "legacy")["qualified"]
        by_task[row["task_id"]][row["representation"]].append(row)

    per_task, moved, undefined = {}, [], []
    for task in sorted(by_task):
        rs = by_task[task]
        ref_arms, ref_c = contrast(rs, "program")          # all retained programs
        dec_arms, dec_c = contrast(rs, "_declared")
        st_arms, st_c = contrast(rs, "_stress_repaired")
        frozen_c = contrast(rs, "admitted_rule_b_frozen")[1]  # un-repaired (b)
        movement = None if (dec_c is None or st_c is None) else st_c - dec_c
        declared_change = None if (dec_c is None or ref_c is None) else dec_c - ref_c
        entry = {
            "n_programs": {"R0": len(rs["R0"]), "RT": len(rs["RT"])},
            "qualified_per_rule": {
                "declared_v4": sum(1 for r in rs["R0"] + rs["RT"] if r["_declared"]),
                "stress_repaired": sum(1 for r in rs["R0"] + rs["RT"]
                                       if r["_stress_repaired"]),
                "stress_frozen_boundary": sum(1 for r in rs["R0"] + rs["RT"]
                                              if r["admitted_rule_b_frozen"]),
            },
            "oracle_correct_programs": sum(1 for r in rs["R0"] + rs["RT"]
                                           if r["oracle_match"]),
            "reference_contrast": {"arms": ref_arms, "contrast_pp": ref_c},
            "declared_contrast": {"arms": dec_arms, "contrast_pp": dec_c},
            "stress_contrast": {"arms": st_arms, "contrast_pp": st_c},
            "stress_frozen_boundary_contrast_pp": frozen_c,
            "movement_stress_minus_declared_pp": movement,
            "declared_minus_reference_pp": declared_change,
        }
        per_task[task] = entry
        if movement is not None and abs(movement) > MARGIN_PP:
            moved.append(task)
        if movement is None:
            undefined.append(task)

    oracle_correct = [r for r in rows if r["oracle_match"]]
    admitted_declared = [r for r in rows if r["_declared"] and r["oracle_match"]]
    admitted_stress = [r for r in rows if r["_stress_repaired"] and r["oracle_match"]]

    out = {
        "schema": "external-admission-amend2-contrast/1",
        "namespace": base["namespace"],
        "derived_from": ["regrade_results_amend2.json",
                         "external_admission_amend1_20261024/sessions/programs"],
        "quantity": "per-task representation contrast (RT minus R0 acceptance, pp), "
                    "the registered F1",
        "margin_pp": MARGIN_PP,
        "per_task": per_task,
        "f1_registered": {
            "criterion": "regrade (b) moves the per-task representation contrast "
                         "outside +/-10pp on >= 2 of 4 tasks",
            "movement_defined_on": len(per_task) - len(undefined),
            "tasks_moved": moved,
            "tasks_undefined": undefined,
            "verdict": "TRUE" if len(moved) >= 2 else "FALSE",
            "note": "undefined = an arm admits no program, so the contrast has no "
                    "denominator; such a task is never counted as movement",
        },
        "declared_rule_effect": {
            "quantity": "declared-rule contrast minus the unregraded contrast",
            "per_task_pp": {t: per_task[t]["declared_minus_reference_pp"]
                            for t in per_task},
            "reading": "the only interpretable change is a composition effect: the "
                       "rule removes failing programs from an arm's denominator",
        },
        "admission": {
            "note": "admission is defined as qualification AND the session-time "
                    "oracle label, so a 'false admission' is impossible by "
                    "construction; the informative numbers are recall of correct "
                    "programs and how many oracle-failing programs also qualify",
            "oracle_correct_programs": len(oracle_correct),
            "oracle_correct_qualified_declared": len(admitted_declared),
            "oracle_correct_qualified_stress": len(admitted_stress),
            "declared_recall_of_correct": (len(admitted_declared)
                                           / len(oracle_correct)),
            "stress_recall_of_correct": (len(admitted_stress)
                                         / len(oracle_correct)),
            "oracle_failing_also_qualified": sum(
                1 for r in rows if r["_declared"] and not r["oracle_match"]),
            "stress_discards_correct": len(oracle_correct) - len(admitted_stress),
        },
        "boundaries": {
            "boundary_repair_applied_to_both_arms": True,
            "deviation_disclosed": "amendment wording kept rule (b) frozen; applying "
                                   "the interface fix to (b) as well is a "
                                   "post-outcome analysis deviation, recorded in "
                                   "PREREGISTRATION.md §7 and REPORT.md §6",
            "post_hoc": True,
            "no_new_execution": True,
            "undefined_is_not_zero": True,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")

    print(f"tasks {len(per_task)} · movement defined on {len(per_task)-len(undefined)} "
          f"· moved {len(moved)}")
    for task, e in per_task.items():
        name = task.split("__")[-1]
        fmt = lambda v: "undefined" if v is None else f"{v:+.1f}"  # noqa: E731
        print(f"  {name:<18} reference {fmt(e['reference_contrast']['contrast_pp']):>9}"
              f"  declared {fmt(e['declared_contrast']['contrast_pp']):>9}"
              f"  stress {fmt(e['stress_contrast']['contrast_pp']):>9}"
              f"  movement {fmt(e['movement_stress_minus_declared_pp']):>9}"
              f"  qualified {e['qualified_per_rule']['declared_v4']}/"
              f"{e['qualified_per_rule']['stress_repaired']}")
              
    print(f"F1 registered: {out['f1_registered']['verdict']} · "
          f"declared qualifies {len(admitted_declared)}/{len(oracle_correct)} "
          f"oracle-correct programs, stress {len(admitted_stress)}")
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
