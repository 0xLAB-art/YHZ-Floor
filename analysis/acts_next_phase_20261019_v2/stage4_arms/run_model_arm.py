#!/usr/bin/env python3
"""Execute the E2A evaluator with model-authored producers (Stage 4 matched arm).

The only substituted component is the *producer*: the scripted source function
is replaced by the approved model route.  The screen, the trusted execution
observer, the independent reference adjudicator, the aggregator, the attack
fixtures, the Stage 01 baseline and the result schema are the frozen Stage 1
components, used unmodified.

Trust material is provisioned fresh for this arm (the Stage 1 issuer keys were
ephemeral and are gone), so the frozen Stage 1 trust bundle is not modified.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any

ARM_ROOT = Path(__file__).resolve().parent
PHASE_ROOT = ARM_ROOT.parent
STAGE1_ROOT = PHASE_ROOT / "stage1_e2a"
RUNS_ROOT = ARM_ROOT / "runs"
TRUST_DIR = ARM_ROOT / "trust"
KEYS_DIR = Path("/tmp/acts_stage4_keys")
LEDGER_PATH = ARM_ROOT / "provider_calls.jsonl"
ARM_MANIFEST_PATH = ARM_ROOT / "model_arm_manifest.json"
SCRIPTED_RUN = STAGE1_ROOT / "runs" / "20261020T065943Z_confirmatory"
DECISION_SUCCESS = "ATTRIBUTED_SUCCESS"

sys.path.insert(0, str(STAGE1_ROOT))

from e2a import producers  # noqa: E402
from e2a import prepare  # noqa: E402
from e2a import runner as e2a_runner  # noqa: E402

from model_producer import (  # noqa: E402
    APPROVED_ENDPOINT,
    APPROVED_MODEL,
    ModelProducer,
    ProgramRequest,
    credential_from_environment,
)


class ProducerContext:
    """Tracks the instance the producer is currently being asked about."""

    def __init__(self) -> None:
        self.task = ""
        self.seed = 0
        self.condition = ""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["case_id"]] = row
    return rows


def install_model_producer(producer: ModelProducer) -> None:
    """Route the frozen producer hooks at the approved model route."""
    context = ProducerContext()
    original_build_instance = e2a_runner.build_instance
    original_public_instance = e2a_runner.public_instance

    def build_instance(task: str, seed: int) -> dict[str, Any]:
        instance = original_build_instance(task, seed)
        context.task = task
        context.seed = seed
        return instance

    def public_instance(instance: dict[str, Any], condition: str) -> dict[str, Any]:
        context.condition = condition
        return original_public_instance(instance, condition)

    def current_artifact():
        key = (context.task, context.seed, context.condition, producer.last_variant)
        return producer.artifacts[key]

    def produce_source(task: str, variant: str) -> str:
        producer.last_variant = variant
        instance = original_build_instance(task, context.seed)
        public = original_public_instance(instance, context.condition)
        artifact = producer.program_for(
            ProgramRequest(
                task=task,
                seed=context.seed,
                condition=context.condition,
                variant=variant,
                instance=public,
            )
        )
        return artifact.source_text

    def producer_identity(case_id: str) -> dict[str, Any]:
        artifact = current_artifact()
        return {
            "producer_id": "e2a-model-producer-v1",
            "producer_kind": "model",
            "case_id": case_id,
            "provider_route": APPROVED_MODEL,
            "provider_endpoint": APPROVED_ENDPOINT,
            "provider_response_sha256": artifact.response_sha256,
            "provider_call_index": artifact.provider_call_index,
        }

    def producer_nonce(case_id: str, task: str, seed: int, variant: str) -> str:
        artifact = current_artifact()
        material = f"{case_id}|{task}|{seed}|{variant}|{artifact.response_sha256}"
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    e2a_runner.build_instance = build_instance
    e2a_runner.public_instance = public_instance
    producers.produce_source = produce_source
    producers.producer_identity = producer_identity
    producers.producer_nonce = producer_nonce


def case_rows(model_rows: dict[str, dict[str, Any]],
              scripted_rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Join the two arms case by case."""
    rows = []
    for case_id, model_row in model_rows.items():
        scripted_row = scripted_rows.get(case_id)
        scripted_decision = scripted_row["e2a"]["decision"] if scripted_row else None
        rows.append({
            "case_id": case_id,
            "case_class": model_row["case_class"],
            "gt_success": model_row["gt_success"],
            "task": model_row["task"],
            "seed": model_row["seed"],
            "condition": model_row["condition"],
            "producer_variant": model_row["producer_variant"],
            "attack": model_row["attack"],
            "model_decision": model_row["e2a"]["decision"],
            "model_reason": model_row["e2a"]["reason"],
            "model_reason_family": model_row["e2a"]["reason_family"],
            "model_execution_status": model_row["execution_status"],
            "model_screen": model_row["screen"],
            "model_parse_status": model_row["parse_status"],
            "model_reference_verdict": model_row["reference"]["verdict"],
            "model_baseline_validator": model_row["baseline"]["validator"].get("decision"),
            "scripted_decision": scripted_decision,
            "scripted_reason": scripted_row["e2a"]["reason"] if scripted_row else None,
            "decisions_agree": scripted_decision is not None
            and model_row["e2a"]["decision"] == scripted_decision,
        })
    return rows


def arm_stats(rows: list[dict[str, Any]], decision_key: str) -> dict[str, Any]:
    """Attribution, false-negative and false-positive counts for one arm."""
    truthy = [row for row in rows if row["gt_success"]]
    falsy = [row for row in rows if not row["gt_success"]]
    false_negatives = [row["case_id"] for row in truthy if row[decision_key] != DECISION_SUCCESS]
    false_positives = [row["case_id"] for row in falsy if row[decision_key] == DECISION_SUCCESS]
    return {
        "cases": len(rows),
        "attributed_success": sum(1 for row in rows if row[decision_key] == DECISION_SUCCESS),
        "false_negatives": len(false_negatives),
        "false_positives": len(false_positives),
        "false_negative_cases": false_negatives,
        "false_positive_cases": false_positives,
    }


def agreement_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """How often the evaluator reached the same verdict across producers."""
    disagreeing = [row for row in rows if not row["decisions_agree"]]
    return {
        "cases": len(rows),
        "agreeing": len(rows) - len(disagreeing),
        "disagreeing": len(disagreeing),
        "disagreeing_cases": [
            {"case_id": row["case_id"], "model": row["model_decision"],
             "scripted": row["scripted_decision"]}
            for row in disagreeing
        ],
    }


def count_values(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row[key])
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def screen_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Producer-side execution outcomes in the model arm."""
    return {
        "screen_rejected": [row["case_id"] for row in rows
                            if not row["model_screen"].get("accepted")],
        "execution_status_counts": count_values(rows, "model_execution_status"),
        "parse_status_counts": count_values(rows, "model_parse_status"),
    }


def baseline_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """How the frozen Stage 01 baseline scored the model-authored artifacts."""
    accepts = [row for row in rows if row["model_baseline_validator"] == "ACCEPT"]
    return {
        "accepts": len(accepts),
        "accept_cases": [row["case_id"] for row in accepts],
        "false_promotions": [row["case_id"] for row in accepts if not row["gt_success"]],
    }


def compare_arms(model_rows: dict[str, dict[str, Any]],
                 scripted_rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Compare the model arm against the scripted arm case by case."""
    rows = case_rows(model_rows, scripted_rows)
    return {
        "per_case": rows,
        "model_arm": arm_stats(rows, "model_decision"),
        "scripted_arm": arm_stats(rows, "scripted_decision"),
        "decision_agreement": agreement_stats(rows),
        "model_arm_screen": screen_stats(rows),
        "model_arm_stage01_baseline": baseline_stats(rows),
    }


def corrected_run_manifest(run_manifest_path: Path, provider_calls: int) -> dict[str, Any]:
    """Record the true provider-call counters in the runner's run manifest."""
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    run_manifest.update({
        "model_calls": provider_calls,
        "network_calls": provider_calls,
        "provider_calls": provider_calls,
        "provider_route": APPROVED_MODEL,
        "provider_endpoint": APPROVED_ENDPOINT,
        "provider_call_counter_note": (
            "The frozen runner hardcodes zero provider counters; this arm corrects "
            "them from the provider ledger."
        ),
        "provider_ledger": str(LEDGER_PATH),
    })
    run_manifest_path.write_text(json.dumps(run_manifest, sort_keys=True, indent=2) + "\n")
    return run_manifest


def build_arm_manifest(run_dir: Path, producer: ModelProducer, comparison: dict[str, Any]) -> dict[str, Any]:
    """Assemble the self-describing record of this arm."""
    run_manifest_path = run_dir / "run_manifest.json"
    raw_results_path = run_dir / "raw_results.jsonl"
    bundle_path = TRUST_DIR / "issuers_public.json"
    policy_path = TRUST_DIR / "trust_policy.json"
    return {
        "schema": "acts-stage4-model-arm/1",
        "run_dir": str(run_dir),
        "arm": "model-authored producer, frozen E2A evaluator",
        "provider_route": APPROVED_MODEL,
        "provider_endpoint": APPROVED_ENDPOINT,
        "provider_calls": producer.provider_calls,
        "distinct_program_requests": len(producer.artifacts),
        "no_retry": True,
        "no_fallback": True,
        "no_seed_replacement": True,
        "trust_bundle": str(bundle_path),
        "trust_bundle_sha256": sha256_file(bundle_path),
        "trust_policy": str(policy_path),
        "trust_policy_sha256": sha256_file(policy_path),
        "raw_results": str(raw_results_path),
        "raw_results_sha256": sha256_file(raw_results_path),
        "provider_ledger": str(LEDGER_PATH),
        "provider_ledger_sha256": sha256_file(LEDGER_PATH),
        "run_manifest_sha256": sha256_file(run_manifest_path),
        "scripted_baseline_run": str(SCRIPTED_RUN),
        "scripted_baseline_raw_results_sha256": sha256_file(
            SCRIPTED_RUN / "raw_results.jsonl"),
        "harness_sha256": {
            "model_producer": sha256_file(ARM_ROOT / "model_producer.py"),
            "run_model_arm": sha256_file(ARM_ROOT / "run_model_arm.py"),
        },
        "comparison": comparison,
    }


def main() -> int:
    for existing in (LEDGER_PATH, ARM_MANIFEST_PATH):
        if existing.exists():
            raise SystemExit(f"refusing to overwrite {existing}")
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    run_dir = RUNS_ROOT / (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "_model_arm")

    if KEYS_DIR.exists():
        # The issuer directory must hold exactly the keys for this run: a
        # stale key would be picked up by role lookup while the trust bundle
        # describes only the current one.
        shutil.rmtree(KEYS_DIR)
    trust = prepare.provision_trust(KEYS_DIR, TRUST_DIR)
    keys_dir = Path(trust["keys_dir"])

    producer = ModelProducer(credential_from_environment(), LEDGER_PATH)
    install_model_producer(producer)

    e2a_runner.execute_run(run_dir, keys_dir, TRUST_DIR)
    corrected_run_manifest(run_dir / "run_manifest.json", producer.provider_calls)

    comparison = compare_arms(
        load_rows(run_dir / "raw_results.jsonl"),
        load_rows(SCRIPTED_RUN / "raw_results.jsonl"),
    )
    arm_manifest = build_arm_manifest(run_dir, producer, comparison)
    ARM_MANIFEST_PATH.write_text(json.dumps(arm_manifest, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "run_dir": str(run_dir),
        "provider_calls": producer.provider_calls,
        "model_arm": comparison["model_arm"],
        "scripted_arm": comparison["scripted_arm"],
        "decision_agreement": comparison["decision_agreement"],
        "model_arm_screen": comparison["model_arm_screen"],
        "model_arm_stage01_baseline": comparison["model_arm_stage01_baseline"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())