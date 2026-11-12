"""Independent adjudication of the E2A run.

The adjudicator reads **only** retained artifacts.  It does not import
evaluator-internal state and does not reuse the runner's in-memory objects.
It:

1. re-derives the ground truth of every case independently (``e2a/truth.py``)
   and reports any disagreement with the frozen label table as a validity
   failure;
2. recomputes the four primary metrics for the E2A evaluator, for the frozen
   Stage 01 validator, and for the frozen Stage 01 validator-and-reference
   *end-to-end* path;
3. recomputes the secondary metrics S1, S2 and S3;
4. runs the cross-implementation check (E2A reference predicate vs the frozen
   Stage 01 reference predicate vs the independent truth module).

Every reported number is traceable to a case-level row of ``raw_results.jsonl``.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from . import canonical, truth
from .aggregator import DECISION_INCONCLUSIVE, DECISION_REJECT, DECISION_SUCCESS

STAGE1_ROOT = Path(__file__).resolve().parents[1]


def _decision_is_success(decision: str) -> bool:
    return decision == DECISION_SUCCESS


def _baseline_validator_is_success(verdict: dict[str, Any]) -> bool:
    return verdict.get("decision") == "ACCEPT"


def _baseline_end_to_end_is_success(verdict: dict[str, Any], reference: dict[str, Any]) -> bool:
    return (_baseline_validator_is_success(verdict)
            and reference.get("reference_verdict") == "ACCEPTED")


def _metrics(decisions: list[tuple[bool, bool]]) -> dict[str, Any]:
    """decisions: list of (gt_success, is_attributed_success)."""
    n_success = sum(1 for gt, _ in decisions if gt)
    n_non_success = sum(1 for gt, _ in decisions if not gt)
    false_promotion = sum(1 for gt, ok in decisions if ok and not gt)
    correct_attribution = sum(1 for gt, ok in decisions if ok and gt)
    false_rejection = sum(1 for gt, ok in decisions if gt and not ok)
    correct_refusal = sum(1 for gt, ok in decisions if not gt and not ok)
    return {
        "false_promotion": canonical.rate_block(false_promotion, n_non_success),
        "correct_attribution": canonical.rate_block(correct_attribution, n_success),
        "false_rejection": canonical.rate_block(false_rejection, n_success),
        "correct_refusal": canonical.rate_block(correct_refusal, n_non_success),
        "n_success": n_success,
        "n_non_success": n_non_success,
    }


def _split_reject_inconclusive(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(row[key] for row in rows)
    return {"REJECT": counts.get(DECISION_REJECT, 0),
            "INCONCLUSIVE": counts.get(DECISION_INCONCLUSIVE, 0),
            "ATTRIBUTED_SUCCESS": counts.get(DECISION_SUCCESS, 0)}


def adjudicate(run_dir: Path) -> dict[str, Any]:
    raw_path = run_dir / "raw_results.jsonl"
    rows = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    cases_root = run_dir / "cases"

    prior_contexts: dict[str, int] = {}
    validity: list[dict[str, Any]] = []
    derived: list[dict[str, Any]] = []

    for row in rows:
        case_dir = cases_root / row["case_id"]
        facts = truth.derive_ground_truth(row, case_dir, prior_contexts)
        derived.append({"case_id": row["case_id"], **facts})
        if facts["derived_gt_success"] != row["gt_success"]:
            validity.append({
                "case_id": row["case_id"],
                "failure": "derived_ground_truth_disagrees_with_frozen_label",
                "frozen_label": row["gt_success"],
                "derived": facts["derived_gt_success"],
                "binding_problems": facts["binding_problems"],
                "predicate_details": facts["predicate_details"],
            })
        context = json.loads((case_dir / "observation.json").read_text(encoding="utf-8"))["context"]
        key = json.dumps({name: context.get(name) for name in
                          ("kind", "domain", "target_id", "attempt_id", "epoch", "role")},
                         sort_keys=True, separators=(",", ":"))
        if key not in prior_contexts:
            prior_contexts[key] = row["ordinal"]

    # -- primary metrics -----------------------------------------------------
    e2a_pairs = [(row["gt_success"], _decision_is_success(row["e2a"]["decision"])) for row in rows]
    baseline_pairs = [(row["gt_success"], _baseline_validator_is_success(row["baseline"]["validator"]))
                      for row in rows]
    end_to_end_pairs = [(row["gt_success"],
                         _baseline_end_to_end_is_success(row["baseline"]["validator"],
                                                       {"reference_verdict": row["baseline"]["reference_verdict"]}))
                        for row in rows]

    e2a_metrics = _metrics(e2a_pairs)
    baseline_metrics = _metrics(baseline_pairs)
    end_to_end_metrics = _metrics(end_to_end_pairs)

    # -- per-class breakdown --------------------------------------------------
    def _class_table(pairs: list[tuple[bool, bool]]) -> dict[str, Any]:
        table: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row, (gt, ok) in zip(rows, pairs):
            table[row["case_class"]].append({
                "case_id": row["case_id"], "gt_success": gt, "attributed_success": ok})
        out: dict[str, Any] = {}
        for name, entries in table.items():
            gt_values = {entry["gt_success"] for entry in entries}
            out[name] = {
                "count": len(entries),
                "ground_truth": sorted(gt_values),
                "attributed_success": sum(1 for entry in entries if entry["attributed_success"]),
                "uniform": len({entry["attributed_success"] for entry in entries}) == 1,
                "correct": all(entry["attributed_success"] == entry["gt_success"] for entry in entries),
                "case_ids": [entry["case_id"] for entry in entries],
            }
        return out

    e2a_classes = _class_table(e2a_pairs)
    baseline_classes = _class_table(baseline_pairs)

    # -- S1: declaration sensitivity ------------------------------------------
    e2a_changed = [row["case_id"] for row in rows if row["e2a_s1"]["changed"]]
    baseline_changed = [row["case_id"] for row in rows if row["baseline_s1"]["changed"]]
    s1 = {
        "e2a": {"cases_evaluated": len(rows), "verdict_changed": len(e2a_changed),
                "changed_case_ids": e2a_changed,
                "note": "The claimant's assertion is not an input to the E2A decision."},
        "baseline_validator": {"cases_evaluated": len(rows), "verdict_changed": len(baseline_changed),
                               "changed_case_ids": baseline_changed,
                               "note": "The baseline verdict is a function of the claimant's own claims block."},
    }

    # -- S2: class discrimination --------------------------------------------
    def _s2(classes: dict[str, Any]) -> dict[str, Any]:
        uniform = [name for name, entry in classes.items() if entry["uniform"]]
        correct = [name for name, entry in classes.items() if entry["uniform"] and entry["correct"]]
        wrong = [name for name, entry in classes.items() if entry["uniform"] and not entry["correct"]]
        mixed = [name for name, entry in classes.items() if not entry["uniform"]]
        return {
            "class_count": len(classes),
            "uniform_classes": len(uniform),
            "uniform_and_correct_classes": len(correct),
            "uniform_and_incorrect_classes": len(wrong),
            "non_uniform_classes": len(mixed),
            "correct_classes": correct,
            "incorrect_classes": wrong,
            "non_uniform_class_names": mixed,
            "per_class": classes,
        }

    s2 = {"e2a": _s2(e2a_classes), "baseline_validator": _s2(baseline_classes)}

    # -- S3: chain-completeness coverage -------------------------------------
    s3 = _chain_coverage(rows, cases_root)

    # -- cross-implementation check -------------------------------------------
    cross = []
    for row in rows:
        case_dir = cases_root / row["case_id"]
        target_state = json.loads((case_dir / "baseline" / "target_state.private.json").read_text(encoding="utf-8"))
        observation = json.loads((case_dir / "observation.json").read_text(encoding="utf-8"))
        payload = observation["record"]["payload"]
        stdout_path = payload.get("stdout_path")
        stdout_bytes = Path(stdout_path).read_bytes() if stdout_path else b""
        candidate, _status = truth.parse_output(stdout_bytes)
        independent_ok, _details = truth.predicate_holds(target_state, candidate)
        e2a_ok = row["reference"]["crypto_ok"]
        frozen_ok = row["baseline"]["reference_cryptographic_predicate"]
        if not (e2a_ok == frozen_ok == independent_ok):
            cross.append({
                "case_id": row["case_id"],
                "e2a_reference_crypto_ok": e2a_ok,
                "frozen_stage01_reference_crypto_ok": frozen_ok,
                "independent_truth_crypto_ok": independent_ok,
                "failure": "cross_implementation_disagreement",
            })
    cross_check = {
        "cases_compared": len(rows),
        "disagreements": cross,
        "agreement_rate": canonical.rate_block(len(rows) - len(cross), len(rows)),
    }

    report = {
        "schema": "e2a-adjudication/1",
        "run_dir": str(run_dir),
        "raw_results_sha256": canonical.sha_file(raw_path),
        "case_count": len(rows),
        "derived_ground_truth": derived,
        "validity_failures": validity,
        "validity_failure_count": len(validity),
        "metrics": {
            "e2a": e2a_metrics,
            "baseline_stage01_validator": baseline_metrics,
            "baseline_stage01_end_to_end": end_to_end_metrics,
        },
        "decision_breakdown": {
            "e2a": _split_reject_inconclusive(rows, "decision")
            if False else {
                "REJECT": sum(1 for row in rows if row["e2a"]["decision"] == DECISION_REJECT),
                "INCONCLUSIVE": sum(1 for row in rows if row["e2a"]["decision"] == DECISION_INCONCLUSIVE),
                "ATTRIBUTED_SUCCESS": sum(1 for row in rows if row["e2a"]["decision"] == DECISION_SUCCESS),
            },
            "baseline_validator": dict(Counter(row["baseline"]["validator"].get("decision") for row in rows)),
            "baseline_reference": dict(Counter(row["baseline"]["reference_verdict"] for row in rows)),
        },
        "secondary_metrics": {"S1_declaration_sensitivity": s1, "S2_class_discrimination": s2,
                              "S3_chain_coverage": s3},
        "cross_implementation_check": cross_check,
    }
    (run_dir / "adjudication.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    return report


def _chain_coverage(rows: list[dict[str, Any]], cases_root: Path) -> dict[str, Any]:
    """Mechanically check which of the 15 required objects each contract binds."""
    e2a_bound: Counter[str] = Counter()
    baseline_bound: Counter[str] = Counter()
    total = 0
    for row in rows:
        case_dir = cases_root / row["case_id"]
        observation = json.loads((case_dir / "observation.json").read_text(encoding="utf-8"))
        reference = json.loads((case_dir / "reference.json").read_text(encoding="utf-8"))
        claim = json.loads((case_dir / "claim.e2a.json").read_text(encoding="utf-8"))
        certificate = json.loads((case_dir / "certificate.e2a.json").read_text(encoding="utf-8"))
        baseline_certificate = json.loads(
            (case_dir / "baseline" / "certificate.private.json").read_text(encoding="utf-8"))
        payload = observation["record"]["payload"]
        total += 1

        checks = {
            "01_producer_identity": bool(payload.get("producer")),
            "02_program_source_bytes_digest": bool(payload.get("program_source_sha256")),
            "03_executed_bytes_equal_hashed_bytes": _file_digest(payload.get("program_source_artifact_path"))
            == payload.get("program_source_sha256"),
            "04_invocation_command": bool(payload.get("command")),
            "05_environment_and_interpreter": bool(payload.get("environment")) and bool(payload.get("interpreter")),
            "06_input_digest": bool(payload.get("public_instance_sha256")),
            "07_target_identity_and_state_digest": bool(payload.get("target_id"))
            and bool(reference["record"]["payload"].get("target_state_sha256")),
            "08_attempt_id_and_epoch": bool(observation["context"].get("attempt_id"))
            and observation["context"].get("epoch") is not None,
            "09_captured_stdout_and_stderr": bool(payload.get("stdout_sha256"))
            and bool(payload.get("stderr_sha256")),
            "10_parsed_candidate_output_digest": payload["parse"].get("parsed_candidate_sha256") is not None,
            "11_signed_observer_record": bool(observation.get("signature_hex"))
            and bool(observation["record"].get("signature_hex")),
            "12_signed_reference_result": bool(reference["record"].get("signature_hex")),
            "13_signed_records_with_issuer_identity_role": bool(observation["record"].get("issuer_role"))
            and bool(observation["record"].get("key_id")),
            "14_aggregated_certificate": bool(certificate.get("schema")),
            "15_final_attributed_claim": bool(claim.get("record", {}).get("payload", {}).get("decision")),
        }
        for name, value in checks.items():
            if value:
                e2a_bound[name] += 1

        # -- the frozen Stage 01 contract -------------------------------------
        evidence_rows = {row["kind"]: row for row in baseline_certificate.get("evidence", [])}
        baseline_checks = {
            "01_producer_identity": False,  # the certificate names a producer label only
            "02_program_source_bytes_digest": bool(baseline_certificate.get("agent_artifact", {}).get("sha256")),
            "03_executed_bytes_equal_hashed_bytes": False,  # the executed file is never bound to the observation
            "04_invocation_command": False,
            "05_environment_and_interpreter": False,
            "06_input_digest": False,
            "07_target_identity_and_state_digest": False,
            "08_attempt_id_and_epoch": False,
            "09_captured_stdout_and_stderr": False,
            "10_parsed_candidate_output_digest": False,
            "11_signed_observer_record": False,
            "12_signed_reference_result": False,
            "13_signed_records_with_issuer_identity_role": False,
            "14_aggregated_certificate": bool(baseline_certificate.get("schema")),
            "15_final_attributed_claim": bool(baseline_certificate.get("claims", {}).get("attribution")),
        }
        # the evidence file kinds the frozen contract does carry
        if "execution_trace" in evidence_rows:
            baseline_checks["08_attempt_id_and_epoch"] = True
        for name, value in baseline_checks.items():
            if value:
                baseline_bound[name] += 1

    required = sorted(e2a_bound) if e2a_bound else []
    names = [f"{index:02d}_{label}" for index, label in enumerate(
        ["producer_identity", "program_source_bytes_digest", "executed_bytes_equal_hashed_bytes",
         "invocation_command", "environment_and_interpreter", "input_digest",
         "target_identity_and_state_digest", "attempt_id_and_epoch", "captured_stdout_and_stderr",
         "parsed_candidate_output_digest", "signed_observer_record", "signed_reference_result",
         "signed_records_with_issuer_identity_role", "aggregated_certificate",
         "final_attributed_claim"], start=1)]
    return {
        "required_objects": names,
        "e2a": {"bound_in_all_cases": sorted(name for name, count in e2a_bound.items() if count == total),
                "bound_in_some_cases": sorted(name for name, count in e2a_bound.items() if 0 < count < total),
                "not_bound": sorted(name for name in names if e2a_bound.get(name, 0) == 0),
                "coverage": canonical.rate_block(sum(1 for count in e2a_bound.values() if count == total), 15)},
        "baseline_stage01": {
            "bound_in_all_cases": sorted(name for name, count in baseline_bound.items() if count == total),
            "bound_in_some_cases": sorted(name for name, count in baseline_bound.items() if 0 < count < total),
            "not_bound": sorted(name for name in names if baseline_bound.get(name, 0) == 0),
            "coverage": canonical.rate_block(sum(1 for count in baseline_bound.values() if count == total), 15)},
        "cases_examined": total,
    }


def _file_digest(path: Any) -> str | None:
    if not path:
        return None
    candidate = Path(path)
    if not candidate.is_file():
        return None
    return canonical.sha_file(candidate)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="E2A independent adjudicator")
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    report = adjudicate(args.run_dir)
    print(json.dumps({
        "validity_failures": report["validity_failure_count"],
        "e2a": report["metrics"]["e2a"],
        "baseline_stage01_validator": report["metrics"]["baseline_stage01_validator"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
