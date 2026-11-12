#!/usr/bin/env python3
"""Amendment 3 — REGISTERED F1/F2/F3 machinery, per-label (DRAFT; freeze-blocking).

The preregistration defines F1 on the per-task representation contrast (RT
minus R0 acceptance, pp) after the offline triple regrade, separately for each
registered model label, and a cross-label reading (>=2 of 3 labels with F1 TRUE
and F3 PASSED).  This script computes those quantities from frozen inputs only
and emits the verdict fields the REPORT is allowed to quote.

Inputs (all hash-asserted):
  regrade_results_amend3.json    per-program rows with `label`, representation,
                                 oracle label, per-arm qualification and
                                 output_preserved
  sessions/programs/*.py         retained programs
  policies_amend3_draft/rule_a_permissive_v4.py       (declared arm)
  policies_amend3_draft/rule_b_stress_legacy_repaired.py (stress arm)
  policies_amend3_draft/rule_c_cleanup.py             (cleanup transform)

Per label:
  declared = rule_a_permissive_v4.qualify_source(src, "v3")
  stress   = rule_b_stress_legacy_repaired.qualify_source(src, "legacy")
  cleanup  = stress.qualify_source(transform(src), "legacy")
  acceptance(arm, rep) = (# oracle-correct among arm-qualified) /
                         (# arm-qualified) * 100  (undefined at n=0)
  contrast(arm) = RT acceptance - R0 acceptance (undefined if either is)
  movement = stress contrast - declared contrast (undefined if either is)
  F1 TRUE  iff movement is defined and |movement| > 10 pp on >= ceil(N/2)
  F2 TRUE  iff F1 is not TRUE (honest null band; undefined never counts)
  F3       PASSED_PRESERVATION iff every row's output_preserved is True;
           NOT_EVALUABLE if any row lacks the field; ANALYSIS_DEFECT otherwise
Cross-label:
  labels with F1 TRUE and F3 PASSED; replicable_across_labels iff >= 2 of 3.
  Per-label verdicts are reported side by side; no pooling.

Exit codes: 0 = all labels evaluable and F3 passed; 3 = any F3 not passed;
2 = input/gate failure.  The REPORT may quote only `verdicts`.
"""

import argparse
import collections
import hashlib
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
MARGIN_PP = 10.0
REGISTERED_LABEL_COUNT = 3
CROSS_LABEL_RULE = ">=2 of 3 registered labels with F1 TRUE and F3 PASSED"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arm_stats(rows, representation, key):
    selected = [r for r in rows[representation] if r[key]]
    correct = sum(1 for r in selected if r["oracle_match"])
    n = len(selected)
    return {"oracle_correct": correct, "qualified": n,
            "acceptance_pp": None if n == 0 else 100.0 * correct / n}


def contrast(rows, key):
    r0 = arm_stats(rows, "R0", key)
    rt = arm_stats(rows, "RT", key)
    value = None if (r0["acceptance_pp"] is None or rt["acceptance_pp"] is None) \
        else rt["acceptance_pp"] - r0["acceptance_pp"]
    return {"R0": r0, "RT": rt, "contrast_pp": value}


def preservation_verdict(rows):
    values = [row.get("output_preserved") for row in rows]
    if any(value is None for value in values):
        return "NOT_EVALUABLE"
    if all(value is True for value in values):
        return "PASSED_PRESERVATION"
    return "ANALYSIS_DEFECT_DO_NOT_PUBLISH"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default=str(HERE / "regrade_results_amend3.json"))
    parser.add_argument("--programs-root", default=str(HERE))
    parser.add_argument("--out", default=str(HERE / "regrade_contrast_amend3.json"))
    parser.add_argument("--expected-tasks", default=None)
    parser.add_argument("--allow-missing-preservation", action="store_true")
    parser.add_argument("--allow-small-grid", action="store_true")
    args = parser.parse_args()

    declared_path = HERE / "policies_amend3_draft/rule_a_permissive_v4.py"
    stress_path = HERE / "policies_amend3_draft/rule_b_stress_legacy_repaired.py"
    cleanup_path = HERE / "policies_amend3_draft/rule_c_cleanup.py"
    for path in (declared_path, stress_path, cleanup_path):
        if not path.is_file():
            raise SystemExit(f"missing policy module: {path}")
    declared = load_module(declared_path, "amend3_declared_v4")
    stress = load_module(stress_path, "amend3_stress_legacy_repaired")
    cleanup = load_module(cleanup_path, "amend3_cleanup")

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
    if args.expected_tasks:
        expected = sorted(t.strip() for t in args.expected_tasks.split(",") if t.strip())
        if expected != tasks:
            raise SystemExit(f"grid mismatch: expected {expected}, got {tasks}")
    if len(tasks) < 6 and not args.allow_small_grid:
        raise SystemExit(f"grid too small: {len(tasks)} tasks (quorum 6)")

    threshold = (len(tasks) + 1) // 2
    per_label, all_f3 = {}, {}
    for label in labels:
        per_task, moved, defined, undefined = {}, [], [], []
        for task in tasks:
            rs = grouped[(label, task)]
            ref = contrast(rs, "program")
            dec = contrast(rs, "_declared")
            st = contrast(rs, "_stress")
            cl = contrast(rs, "_cleanup")
            movement = None if (dec["contrast_pp"] is None or st["contrast_pp"] is None) \
                else st["contrast_pp"] - dec["contrast_pp"]
            per_task[task] = {
                "n_programs": {"R0": len(rs["R0"]), "RT": len(rs["RT"])},
                "oracle_correct_programs": sum(
                    1 for r in rs["R0"] + rs["RT"] if r["oracle_match"]),
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
        label_rows = [r for task in tasks for rep in ("R0", "RT")
                      for r in grouped[(label, task)][rep]]
        f3 = preservation_verdict(label_rows)
        all_f3[label] = f3
        f1 = len(moved) >= threshold
        per_label[label] = {
            "per_task": per_task,
            "verdicts": {
                "F1": "TRUE" if f1 else "FALSE",
                "F2": "FALSE" if f1 else "TRUE",
                "F3": f3,
                "N": len(tasks),
                "threshold_M": threshold,
                "margin_pp": MARGIN_PP,
                "movement_defined_on": len(defined),
                "tasks_moved": moved,
                "tasks_undefined": undefined,
                "tasks_defined_within_margin": [t for t in defined if t not in moved],
                "undefined_not_zero": True,
            },
            "admission": admission_block(label_rows),
        }

    valid_labels = [label for label in labels
                    if per_label[label]["verdicts"]["F1"] == "TRUE"
                    and all_f3[label] == "PASSED_PRESERVATION"]
    cross_label = {
        "rule": CROSS_LABEL_RULE,
        "registered_label_count": REGISTERED_LABEL_COUNT,
        "labels": labels,
        "f1_true": [label for label in labels
                    if per_label[label]["verdicts"]["F1"] == "TRUE"],
        "f1_false": [label for label in labels
                     if per_label[label]["verdicts"]["F1"] == "FALSE"],
        "f1_true_and_f3_passed": valid_labels,
        "applicable": len(labels) == REGISTERED_LABEL_COUNT,
        "replicable_across_labels": (len(valid_labels) >= 2
                                     if len(labels) == REGISTERED_LABEL_COUNT
                                     else None),
        "note": ("per-label verdicts are reported side by side; no pooling; "
                 "undefined is never counted as movement"),
    }

    out = {
        "schema": "external-admission-amend3-contrast/2-draft",
        "namespace": base.get("namespace", "external_admission_amend3_20261105"),
        "derived_from": [str(results_path), str(programs_root)],
        "quantity": ("per-label per-task representation contrast (RT minus R0 "
                     "acceptance, pp), the registered F1"),
        "margin_pp": MARGIN_PP,
        "labels": labels,
        "per_label": per_label,
        "cross_label": cross_label,
        "verdicts": {
            "per_label": {label: per_label[label]["verdicts"] for label in labels},
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
            "no_new_execution": True,
            "no_benchmark_quality_claim": True,
            "no_cross_label_pooling": True,
            "report_may_quote_only_verdicts": True,
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
    oracle_correct = [r for r in rows if r["oracle_match"]]
    admitted_declared = [r for r in rows if r["_declared"] and r["oracle_match"]]
    admitted_stress = [r for r in rows if r["_stress"] and r["oracle_match"]]
    return {
        "note": ("admission is qualification AND the session-time oracle label; "
                 "informative numbers are recall of correct programs and how "
                 "many oracle-failing programs also qualify"),
        "oracle_correct_programs": len(oracle_correct),
        "oracle_correct_qualified_declared": len(admitted_declared),
        "oracle_correct_qualified_stress": len(admitted_stress),
        "declared_recall_of_correct": (len(admitted_declared) / len(oracle_correct))
            if oracle_correct else None,
        "stress_recall_of_correct": (len(admitted_stress) / len(oracle_correct))
            if oracle_correct else None,
        "stress_discards_correct": len(oracle_correct) - len(admitted_stress),
    }


if __name__ == "__main__":
    raise SystemExit(main())
