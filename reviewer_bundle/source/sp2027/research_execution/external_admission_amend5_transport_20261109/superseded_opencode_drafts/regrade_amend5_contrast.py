#!/usr/bin/env python3
"""Amendment 5 — REGISTERED F1/F2/F3 machinery, per label AND per coding.

Adapted verbatim from the Amendment-4 registered machinery
(external_admission_amend4_frontier_20261106/regrade_amend4_contrast.py);
the Amendment-5 registered deltas:

  - policy modules point at this namespace's byte-identical copies
    (policies_amend5/, POLICIES_PROVENANCE_AMEND5.json);
  - the F1 bar is the REGISTERED one and does not shrink to the measurable
    subset: F1 TRUE iff movement |stress - declared| > 10 pp on >= 4 of the
    7 registered tasks. When fewer than 4 tasks have a defined movement
    (measured census boundaries: gateway content filter + reasoning-budget
    rumination overflow), F1 is ver NOT_EVALUABLE_REGISTERED_BAR with the
    census-derived measurable_upper_bound and the explicit flag
    f1_cannot_be_true_under_census — the measured panel limit, never a zero
    and never counted as movement;
  - F2 (honest null band): TRUE iff F1 is not TRUE and every task whose
    movement is defined lies within the margin and at least one task's
    movement is defined; NOT_EVALUABLE_NO_DEFINED_MOVEMENT otherwise;
  - F3 as registered: PASSED_PRESERVATION iff every row's output_preserved
    is True (NOT_EVALUABLE when there are no rows);
  - the census boundaries are carried into the output (frozen JSON only —
    the report may quote verdicts and boundaries verbatim from them).

Per-task quantity, per label, per coding:
  acceptance(arm, rep) = (# oracle-correct among arm-qualified) /
                         (# arm-qualified) * 100  (undefined at n=0)
  contrast(arm)      = RT acceptance - R0 acceptance (undefined if either)
  movement           = stress contrast - declared contrast
  reference contrast = the sessions' own programs (both codings)

Both codings' verdicts are the product (P024b); the C1-vs-C2 disagreement
is the registered answer-normalization-owner measurement. Per-label
verdicts side by side; no pooling across labels or codings; undefined is
never counted as movement.
"""

import argparse
import collections
import hashlib
import importlib.util
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
MARGIN_PP = 10.0
REGISTERED_TASK_COUNT = 7
REGISTERED_F1_TASKS = 4
REGISTERED_LABEL_COUNT = 3
CROSS_LABEL_RULE = ">=2 of 3 registered labels with F1 TRUE and F3 PASSED"
CODINGS = {"C1": "oracle_match", "C2": "oracle_match_c2"}
CENSUS = HERE / "COMPLETENESS_CENSUS_AMEND5.json"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arm_stats(rows, representation, key, oracle_field):
    selected = [r for r in rows[representation] if r[key]]
    correct = sum(1 for r in selected if r[oracle_field])
    n = len(selected)
    return {"oracle_correct": correct, "qualified": n,
            "acceptance_pp": None if n == 0 else 100.0 * correct / n}


def contrast(rows, key, oracle_field):
    r0 = arm_stats(rows, "R0", key, oracle_field)
    rt = arm_stats(rows, "RT", key, oracle_field)
    value = None if (r0["acceptance_pp"] is None or rt["acceptance_pp"] is None) \
        else rt["acceptance_pp"] - r0["acceptance_pp"]
    return {"R0": r0, "RT": rt, "contrast_pp": value}


def preservation_verdict(rows):
    values = [row.get("output_preserved") for row in rows]
    if not values or any(value is None for value in values):
        return "NOT_EVALUABLE"
    if all(value is True for value in values):
        return "PASSED_PRESERVATION"
    return "ANALYSIS_DEFECT_DO_NOT_PUBLISH"


def census_for_label(label):
    """Both-representation census-pass tasks for `label` (frozen JSON)."""
    try:
        census = json.loads(CENSUS.read_text())
    except FileNotFoundError:
        return {"error": "COMPLETENESS_CENSUS_AMEND5.json missing"}
    pass_set = {(task, rep) for task, rep, lab
                in census["pass_combinations"] if lab == label}
    tasks = sorted({task for task, _rep in pass_set})
    both = [task for task in tasks
            if (task, "R0") in pass_set and (task, "RT") in pass_set]
    return {
        "registered_cap": census.get("registered_cap"),
        "census_pass_pairs": sorted(f"{t}|{r}" for t, r in pass_set),
        "both_representation_tasks": both,
        "measurable_upper_bound": len(both),
        "frozen_blocked_pairs": census.get("frozen_blocked_pairs"),
        "note": ("a (task, representation) cell without a census PASS row is "
                 "a measured boundary (content filter / rumination "
                 "overflow); its sessions never existed, so no program can "
                 "defend or attack the thesis there"),
    }


def f1_verdict(moved, defined, measurable_upper_bound):
    """Registered F1: fixed bar over the 7 registered tasks."""
    if len(moved) >= REGISTERED_F1_TASKS:
        return "TRUE", {
            "bar": REGISTERED_F1_TASKS,
            "moved_tasks_defined": moved,
            "movement_defined_on": len(defined),
        }
    if len(defined) >= REGISTERED_F1_TASKS:
        return "FALSE", {
            "bar": REGISTERED_F1_TASKS,
            "moved_tasks_defined": moved,
            "movement_defined_on": len(defined),
        }
    return "NOT_EVALUABLE_REGISTERED_BAR", {
        "bar": REGISTERED_F1_TASKS,
        "moved_tasks_defined": moved,
        "movement_defined_on": len(defined),
        "measurable_upper_bound": measurable_upper_bound,
        "f1_cannot_be_true_under_census":(
                measurable_upper_bound < REGISTERED_F1_TASKS),
        "note": ("the registered bar needs 4 defined movements of the 7 "
                 "registered tasks; fewer than 4 tasks are measurable "
                 "under this route's measured boundaries, so F1 carries no "
                 "verdict on this route — its truth value in both "
                 "directions requires the route with no such boundaries"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default=str(HERE / "regrade_results_amend5.json"))
    parser.add_argument("--programs-root", default=str(HERE))
    parser.add_argument("--out", default=str(HERE / "regrade_contrast_amend5.json"))
    parser.add_argument("--allow-missing-preservation", action="store_true")
    args = parser.parse_args()

    declared_path = HERE / "policies_amend5/rule_a_permissive_v4.py"
    stress_path = HERE / "policies_amend5/rule_b_stress_legacy_repaired.py"
    cleanup_path = HERE / "policies_amend5/rule_c_cleanup.py"
    for path in (declared_path, stress_path, cleanup_path):
        if not path.is_file():
            raise SystemExit(f"missing policy module: {path}")
    declared = load_module(declared_path, "amend5_declared_v4")
    stress = load_module(stress_path, "amend5_stress_legacy_repaired")
    cleanup = load_module(cleanup_path, "amend5_cleanup")

    results_path = pathlib.Path(args.results)
    base = json.loads(results_path.read_text(encoding="utf-8"))
    rows = base["per_program"]
    programs_root = pathlib.Path(args.programs_root)
    grouped = collections.defaultdict(lambda: {"R0": [], "RT": []})

    for row in rows:
        source_path = programs_root / row["program"]
        source = source_path.read_text(encoding="utf-8")
        if hashlib.sha256(source.encode()).hexdigest() != row["program_sha256"]:
            raise SystemExit(f"PROGRAM HASH MISMATCH: {row['program']}")
        if row["representation"] not in ("R0", "RT"):
            raise SystemExit(f"bad representation: {row['representation']}")
        row["_label"] = row.get("label", "registered_route")
        row["_declared"] = declared.qualify_source(source, "v3")["qualified"]
        row["_stress"] = stress.qualify_source(source, "legacy")["qualified"]
        cleaned, _, _, _ = cleanup.transform(source, {"json", "sys", "base64"})
        row["_cleanup"] = stress.qualify_source(cleaned, "legacy")["qualified"]
        grouped[(row["_label"], row["task_id"])][row["representation"]].append(row)

    labels = sorted({label for label, _ in grouped})
    tasks = sorted({task for _, task in grouped})

    per_label, all_f3 = {}, {}
    for label in labels:
        per_task, coding_verdicts = {}, {}
        label_rows = [r for task in tasks for rep in ("R0", "RT")
                      for r in grouped[(label, task)][rep]]
        f3 = preservation_verdict(label_rows)
        all_f3[label] = f3
        cinfo = census_for_label(label)
        for coding, oracle_field in CODINGS.items():
            moved, defined, undefined = [], [], []
            for task in tasks:
                rs = grouped[(label, task)]
                ref = contrast(rs, "program", oracle_field)
                dec = contrast(rs, "_declared", oracle_field)
                st = contrast(rs, "_stress", oracle_field)
                cl = contrast(rs, "_cleanup", oracle_field)
                movement = None if (dec["contrast_pp"] is None or st["contrast_pp"] is None) \
                    else st["contrast_pp"] - dec["contrast_pp"]
                if task not in per_task:
                    per_task[task] = {}
                per_task[task][coding] = {
                    "n_programs": {"R0": len(rs["R0"]), "RT": len(rs["RT"])},
                    "oracle_correct_programs": sum(
                        1 for r in rs["R0"] + rs["RT"] if r[oracle_field]),
                    "qualified_per_arm": {
                        "declared_v4": sum(1 for r in rs["R0"] + rs["RT"] if r["_declared"]),
                        "stress_repaired": sum(1 for r in rs["R0"] + rs["RT"] if r["_stress"]),
                        "cleanup": sum(1 for r in rs["R0"] + rs["RT"] if r["_cleanup"]),
                    },
                    "reference_contrast": ref,
                    "declared_contrast": dec,
                    "stress_contrast": st,
                    "cleanup_contrast": cl,
                    "movement_stress_minus_declared_pp": movement,
                }
                if movement is None:
                    undefined.append(task)
                else:
                    defined.append(task)
                    if abs(movement) > MARGIN_PP:
                        moved.append(task)
            f1, f1_detail = f1_verdict(moved, defined,
                                       cinfo.get("measurable_upper_bound", 0))
            if f1 == "TRUE":
                f2 = "FALSE"
            elif not defined:
                f2 = "NOT_EVALUABLE_NO_DEFINED_MOVEMENT"
            else:
                within = [t for t in defined if abs(
                        per_task[t][coding]["movement_stress_minus_declared_pp"])
                        <= MARGIN_PP]
                f2 = "TRUE" if len(within) == len(defined) else "FALSE"
            coding_verdicts[coding] = {
                "F1": f1,
                "F1_detail": f1_detail,
                "F2": f2,
                "F3": f3,
                "N_registered_tasks": REGISTERED_TASK_COUNT,
                "bar_fixed": REGISTERED_F1_TASKS,
                "margin_pp": MARGIN_PP,
                "tasks_moved": moved,
                "tasks_undefined": undefined,
                "tasks_defined_within_margin": [t for t in defined if t not in moved],
                "undefined_not_zero": True,
                "coding_note": ("C2 accepted per the second admissible "
                                "normalization; the C1-vs-C2 gap is the "
                                "answer-normalization owner's registered "
                                "measurement"),
            }
        per_label[label] = {
            "per_task": per_task,
            "verdicts_by_coding": coding_verdicts,
            "admission": admission_block(label_rows),
            "census_boundaries": cinfo,
        }

    valid_labels = {coding: [label for label in labels
                             if per_label[label]["verdicts_by_coding"][coding]["F1"] == "TRUE"
                             and all_f3[label] == "PASSED_PRESERVATION"]
                    for coding in CODINGS}
    cross_label = {
        "rule": CROSS_LABEL_RULE,
        "registered_label_count": REGISTERED_LABEL_COUNT,
        "labels": labels,
        "by_coding": {coding: {
            "f1_true": [label for label in labels
                        if per_label[label]["verdicts_by_coding"][coding]["F1"] == "TRUE"],
            "f1_false": [label for label in labels
                         if per_label[label]["verdicts_by_coding"][coding]["F1"] == "FALSE"],
            "f1_not_evaluable": [label for label in labels
                                 if per_label[label]["verdicts_by_coding"][coding]["F1"]
                                 == "NOT_EVALUABLE_REGISTERED_BAR"],
            "replicable_across_labels": len(valid_labels[coding]) >= 2,
        } for coding in CODINGS},
        "applicable": len(labels) == REGISTERED_LABEL_COUNT,
        "note": ("per-label verdicts are reported side by side; no pooling "
                 "across labels or codings; undefined is never counted as "
                 "movement; NOT_EVALUABLE_REGISTERED_BAR never counts as TRUE"),
    }

    out = {
        "schema": "external-admission-amend5-contrast/1",
        "namespace": base.get("namespace",
                              "external_admission_amend5_transport_20261109"),
        "derived_from": [str(results_path), str(programs_root)],
        "quantity": ("per-label per-task representation contrast (RT minus R0 "
                     "acceptance, pp) under EACH registered oracle coding "
                     "(C1 primary, C2 second admissible normalization); "
                     "movement = stress contrast - declared contrast"),
        "margin_pp": MARGIN_PP,
        "f1_rule": ("movement outside +/-10pp on >= 4 of the 7 registered "
                    "tasks on at least one label (registered bar; fixed; "
                    "cannot shrink to the measurable subset)"),
        "labels": labels,
        "per_label": per_label,
        "cross_label": cross_label,
        "verdicts": {
            "per_label": {label: per_label[label]["verdicts_by_coding"]
                          for label in labels},
            "cross_label": cross_label,
        },
        "inputs_sha256": {
            "results": sha256_file(results_path),
            "declared_policy": sha256_file(declared_path),
            "stress_policy": sha256_file(stress_path),
            "cleanup_policy": sha256_file(cleanup_path),
        },
        "boundaries": {
            "registered_quantity_only": True,
            "undefined_is_not_zero": True,
            "both_codings_reported": True,
            "no_new_execution": True,
            "no_model_call": True,
            "no_benchmark_quality_claim": True,
            "no_cross_label_pooling": True,
            "no_cross_coding_pooling": True,
            "report_may_quote_only_verdicts": True,
            "f1_not_evaluable_is_never_true_nor_movement": True,
        },
    }
    pathlib.Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                                      encoding="utf-8")
    print(json.dumps(out["verdicts"], indent=2))
    print(f"-> {args.out}")
    if any(value != "PASSED_PRESERVATION" for value in all_f3.values()) \
            and not args.allow_missing_preservation:
        return 3
    return 0


def admission_block(rows):
    blocks = {}
    for coding, field in (("C1", "oracle_match"), ("C2", "oracle_match_c2")):
        oracle_correct = [r for r in rows if r[field]]
        admitted_declared = [r for r in rows if r["_declared"] and r[field]]
        admitted_stress = [r for r in rows if r["_stress"] and r[field]]
        blocks[coding] = {
            "oracle_correct_programs": len(oracle_correct),
            "oracle_correct_qualified_declared": len(admitted_declared),
            "oracle_correct_qualified_stress": len(admitted_stress),
            "declared_recall_of_correct": (len(admitted_declared) / len(oracle_correct))
                if oracle_correct else None,
            "stress_recall_of_correct": (len(admitted_stress) / len(oracle_correct))
                if oracle_correct else None,
            "stress_discards_correct": len(oracle_correct) - len(admitted_stress),
        }
    return {"note": ("admission is qualification AND the session-time oracle "
                     "label under the respective coding; informative numbers "
                     "are recall of correct programs and how many "
                     "oracle-failing programs also qualify"),
            "by_coding": blocks}


if __name__ == "__main__":
    raise SystemExit(main())
