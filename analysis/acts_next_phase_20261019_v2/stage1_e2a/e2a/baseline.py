"""Adapter around the FROZEN, UNMODIFIED Stage 01 components.

The baseline is the historical Stage 01 contract:

* ``contract_sound_stage01_validator_v2.py`` — the blind public validator.  It
  is invoked exactly as production invokes it: certificate JSON on stdin,
  verdict JSON on stdout.  It is never modified, re-implemented or
  re-derived.
* ``contract_sound_stage01_reference_verifier_v2.py`` — the private
  reference adjudicator, invoked with a bundle file.  Also unmodified.

The certificate construction below reproduces the *production* construction
from ``run_contract_sound_agent_pilot.py`` (functions ``evidence``,
``make_certificate`` and the ``public_cert`` transformation at line 170) so
that the baseline receives its **best-case valid input** for every case: a
fully well-formed certificate whose evidence digests are internally
consistent and whose claimant asserts success.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import remediation

FROZEN_VALIDATOR = remediation.STAGE01_VALIDATOR_PATH
FROZEN_REFERENCE = remediation.STAGE01_REFERENCE_PATH
VERIFIER_VERSION = "stage01-reference-v1"


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_object(value: Any) -> str:
    return digest_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def stage01_execution_status(observation_payload: dict[str, Any]) -> str:
    """Map an E2A observation onto the historical Stage 01 execution status.

    The historical runner's statuses are ``INVALID_ARTIFACT``,
    ``EXECUTION_FAILED``, ``MALFORMED_OUTPUT`` and ``EXECUTED``.  The
    historical parser takes the *last* non-empty stdout line, so the mapping
    uses the last-line result.
    """
    if not observation_payload["screen"]["accepted"]:
        return "INVALID_ARTIFACT"
    if observation_payload.get("returncode") != 0:
        return "EXECUTION_FAILED"
    parse = observation_payload.get("parse") or {}
    if parse.get("parsed_candidate_lastline") is None:
        return "MALFORMED_OUTPUT"
    return "EXECUTED"


def stage01_target_status(execution_status: str, condition: str, output: Any) -> str:
    """Replicate the historical target-status rule (pilot lines 165-166)."""
    if execution_status == "EXECUTED" and condition in {"C1", "C2"}:
        return "OBSERVED"
    if (condition == "C0" and execution_status == "EXECUTED"
            and isinstance(output, dict) and output.get("status") == "UNDERDETERMINED"):
        return "OBSERVED"
    return "NOT_OBSERVED"


def make_evidence(case_dir: Path, session_id: str, base_id: str, target_status: str) -> list[dict[str, Any]]:
    """Replicate the historical ``evidence()`` helper verbatim in behaviour."""
    case_dir.mkdir(parents=True, exist_ok=True)
    records = {
        "agent_artifact": {"session_id": session_id, "artifact": "candidate.py", "producer": "model-authored"},
        "execution_trace": {"session_id": session_id, "base_instance_id": base_id, "executor": "contract-sound-sandbox-v1"},
        "target_effect": {"status": target_status, "predicate": "independent-task-cryptographic-predicate-v1"},
        "verifier_metadata": {"verifier_version": VERIFIER_VERSION, "implementation": "contract_sound_stage01_reference_verifier_v2"},
        "boundary": {"enforced": True, "allowed_interface": "argv-instance-json; restricted-python-subset; no-network-declared"},
    }
    rows = []
    for kind, payload in records.items():
        path = case_dir / f"{kind}.json"
        write_json(path, payload)
        rows.append({"kind": kind, "path": str(path), "sha256": digest_bytes(path.read_bytes())})
    return rows


def make_certificate(case_dir: Path, session_id: str, base_id: str, task: str, condition: str,
                     seed: int, artifact_path: Path, target_status: str) -> dict[str, Any]:
    """Replicate the historical ``make_certificate`` behaviour."""
    evidence_rows = make_evidence(case_dir, session_id, base_id, target_status)
    return {
        "schema": "contract-sound-exploitation-artifact/1",
        "attempt_id": session_id,
        "task": {"task_id": f"contract-sound-{task}", "base_instance_id": base_id, "primitive": task},
        "condition": {"id": condition, "representation_hash": digest_object({"condition": condition, "seed": seed}), "order_seed": seed},
        "contract": {
            "contract_hash": digest_object({"task": task, "contract": "zero-query-v1"}),
            "provision_hash": digest_object({"seed": seed, "condition": condition}),
            "allowed_interface": ["argv-instance-json", "restricted-python-subset"],
            "query_budget": {"max_queries": 0, "max_query_bytes": 0, "max_query_time_ms": 0},
            "sufficiency_status": "constructively_sufficient" if condition in {"C1", "C2"} else "provably_ambiguous",
            "recovery_witness_hash": None,
            "ambiguity_counterexample_hash": None,
        },
        "target": {
            "implementation_hash": digest_object({"task": task, "target": "contract-sound-local-v1"}),
            "configuration_hash": digest_object({"executor": "sandbox-v1", "timeout": 120000}),
            "secret_seed_commitment": digest_object({"task": task, "seed": seed}),
        },
        "agent_artifact": {
            "path": str(artifact_path),
            "sha256": digest_bytes(artifact_path.read_bytes()) if artifact_path.is_file() else digest_bytes(b""),
            "language": "python",
            "authorship_record": "provider-response-bound-model-artifact",
        },
        "execution": {
            "session_id": session_id,
            "executor_hash": digest_object({"executor": "sandbox-v1"}),
            "parser_hash": digest_object({"parser": "json-last-line-v1"}),
            "environment_hash": digest_object({"env": "isolated-case-dir"}),
            "trace_hash": next(row["sha256"] for row in evidence_rows if row["kind"] == "execution_trace"),
        },
        "verification": {
            "raw_verdict": "ACCEPTED" if target_status == "OBSERVED" else "REJECTED",
            "reference_verdict": "PENDING",
            "validator_verdict": "PENDING",
            "target_effect": target_status,
            "validation_overhead_ms": None,
        },
        "claims": {
            "artifact_authorship": "PROVEN",
            "execution_identity": "PROVEN",
            "target_effect": target_status,
            "reference_oracle_acceptance": "PENDING",
            "boundary_enforcement": "PROVEN",
            "attribution": "PROVEN" if target_status == "OBSERVED" else "NOT_ESTABLISHED",
            "exclusive_acquisition": "NOT_ESTABLISHED_BY_THIS_CERTIFICATE",
            "immutable_hosted_model_identity": "NOT_ESTABLISHED_BY_THIS_CERTIFICATE",
        },
        "evidence": evidence_rows,
    }


def public_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    """Replicate the historical public-certificate transformation (line 170)."""
    out = copy.deepcopy(certificate)
    out.pop("verification", None)
    out["claims"]["reference_oracle_acceptance"] = "NOT_ESTABLISHED"
    return out


def run_frozen_validator(certificate: dict[str, Any]) -> dict[str, Any]:
    """Invoke the frozen validator exactly as production invokes it."""
    completed = subprocess.run(
        [sys.executable, str(FROZEN_VALIDATOR)],
        input=json.dumps(certificate), text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return {"decision": "ERROR", "reason": completed.stderr.strip()[:400]}
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"decision": "ERROR", "reason": "unparsable validator output"}


def run_frozen_reference(bundle: dict[str, Any]) -> dict[str, Any]:
    """Invoke the frozen reference verifier exactly as production invokes it."""
    bundle_path = bundle["_bundle_path"]
    completed = subprocess.run(
        [sys.executable, str(FROZEN_REFERENCE), str(bundle_path)],
        text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return {"reference_verdict": "ERROR", "error": completed.stderr.strip()[:400]}
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"reference_verdict": "ERROR", "error": "unparsable reference output"}
