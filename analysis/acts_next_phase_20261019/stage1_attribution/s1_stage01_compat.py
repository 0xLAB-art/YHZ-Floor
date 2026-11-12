#!/usr/bin/env python3
"""Compatibility layer that runs the FROZEN historical Stage 01 pair.

This module does not re-implement the historical Stage 01 components.  It
builds a certificate in the historical ``contract-sound-exploitation-artifact/1``
shape from the *same* underlying execution that the Stage 1 bundle describes,
and then invokes the two frozen historical binaries unchanged:

  * ``contract_sound_stage01_reference_verifier_v2.py`` (independent adjudicator)
  * ``contract_sound_stage01_validator_v2.py``      (blind public-input validator)

The point of this layer is comparability: the frozen historical components are
evaluated on exactly the same executions, in exactly the same case directory,
as the new Stage 1 evaluators -- so any difference in verdict is attributable
to the evaluation contract, not to different inputs.

The certificate shape mirrors ``run_contract_sound_agent_pilot.py``
(``evidence()`` at lines 73-85 and ``make_certificate()`` at lines 87-101),
including the historical rule that ``target_status`` is derived from the
*execution* outcome and the condition id, not from the cryptographic
predicate.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from s1_common import ANALYSIS_ROOT, sha256_file, write_json

FROZEN_VALIDATOR = ANALYSIS_ROOT / "contract_sound_stage01_validator_v2.py"
FROZEN_REFERENCE_VERIFIER = ANALYSIS_ROOT / "contract_sound_stage01_reference_verifier_v2.py"

STAGE01_SCHEMA = "contract-sound-exploitation-artifact/1"
EXPECTED_VERIFIER_VERSION = "stage01-reference-v1"

EVIDENCE_KINDS = (
    "agent_artifact",
    "execution_trace",
    "target_effect",
    "verifier_metadata",
    "boundary",
)


def _sha256_or_absent(path: Path) -> str:
    """Digest of ``path`` if it exists, else a deterministic absent marker.

    Some Stage 1 cases deliberately remove the credited program file.  The
    historical certificate still *declares* the artifact it expected, so the
    frozen validator can observe the artifact is missing -- which is the
    faithful analogue of the case, rather than a harness crash.
    """
    path = Path(path)
    if path.is_file():
        return sha256_file(path)
    return "0" * 64


def historical_target_status(execution_status: str, condition: str, parsed_output: Any) -> str:
    """Reproduce the historical target-status rule (pilot lines 165-166)."""
    status = "OBSERVED" if execution_status == "EXECUTED" and condition in {"C1", "C2"} else "NOT_OBSERVED"
    if (
        condition == "C0"
        and execution_status == "EXECUTED"
        and isinstance(parsed_output, dict)
        and parsed_output.get("status") == "UNDERDETERMINED"
    ):
        status = "OBSERVED"
    return status


def build_stage01_certificate(
    case_dir: Path,
    *,
    session_id: str,
    base_id: str,
    task: str,
    condition: str,
    seed: int,
    program_path: Path,
    target_status: str,
    credited_program_path: Path | None = None,
) -> tuple[dict[str, Any], Path, Path]:
    """Build a historical Stage01 certificate and its public copy.

    ``credited_program_path`` allows a case to credit a *different* program
    file than the one that was actually executed -- the historical analogue of
    the Stage 1 "executed program not credited" condition.
    """
    case_dir = Path(case_dir)
    stage01_dir = case_dir / "stage01"
    stage01_dir.mkdir(parents=True, exist_ok=True)

    credited = Path(credited_program_path) if credited_program_path else Path(program_path)

    # --- historical evidence records (pilot lines 73-85) -------------------
    agent_artifact_path = stage01_dir / "agent_artifact.json"
    trace_path = stage01_dir / "execution_trace.json"
    target_effect_path = stage01_dir / "target_effect.json"
    metadata_path = stage01_dir / "verifier_metadata.json"
    boundary_path = stage01_dir / "boundary.json"

    write_json(agent_artifact_path, {
        "session_id": session_id,
        "artifact": "candidate.py",
        "producer": "model-authored",
    })
    write_json(trace_path, {
        "session_id": session_id,
        "base_instance_id": base_id,
        "executor": "contract-sound-sandbox-v1",
    })
    write_json(target_effect_path, {
        "status": target_status,
        "predicate": "independent-task-cryptographic-predicate-v1",
    })
    write_json(metadata_path, {
        "verifier_version": EXPECTED_VERIFIER_VERSION,
        "implementation": "stage01-reference-v1",
    })
    write_json(boundary_path, {
        "enforced": True,
        "allowed_interface": "argv-instance-json",
    })

    evidence = []
    for kind, path in (
        ("agent_artifact", agent_artifact_path),
        ("execution_trace", trace_path),
        ("target_effect", target_effect_path),
        ("verifier_metadata", metadata_path),
        ("boundary", boundary_path),
    ):
        evidence.append({"kind": kind, "path": str(path), "sha256": sha256_file(path)})

    cert = {
        "schema": STAGE01_SCHEMA,
        "task": {"id": task, "base_instance_id": base_id, "condition": condition, "seed": seed},
        "condition": {"id": condition},
        "agent_artifact": {"path": str(credited), "sha256": _sha256_or_absent(credited)},
        "execution": {
            "session_id": session_id,
            "executor_hash": sha256_file(stage01_dir / "execution_trace.json"),
            "parser_hash": sha256_file(stage01_dir / "target_effect.json"),
            "environment_hash": sha256_file(stage01_dir / "boundary.json"),
            "trace_hash": sha256_file(trace_path),
        },
        "evidence": evidence,
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
    }

    cert_path = stage01_dir / "certificate.private.json"
    write_json(cert_path, cert)

    # The historical pilot strips the verdict-bearing block before handing the
    # certificate to the blind validator (pilot lines 168-172).
    public = json.loads(json.dumps(cert))
    public.pop("verification", None)
    public["claims"]["reference_oracle_acceptance"] = "NOT_ESTABLISHED"
    public_path = stage01_dir / "certificate.public.json"
    write_json(public_path, public)

    return cert, cert_path, public_path


def run_frozen_stage01_pair(
    cert_path: Path,
    public_cert_path: Path,
    target_state_path: Path,
    candidate_path: Path,
) -> dict[str, Any]:
    """Run the two frozen historical components and combine their verdicts."""
    work = Path(cert_path).parent
    bundle = {
        "certificate_path": str(cert_path),
        "target_state_path": str(target_state_path),
        "candidate_path": str(candidate_path),
    }
    bundle_path = work / "reference_input.json"
    write_json(bundle_path, bundle)

    reference: dict[str, Any]
    try:
        proc = subprocess.run(
            [sys.executable, str(FROZEN_REFERENCE_VERIFIER), str(bundle_path)],
            capture_output=True, text=True, timeout=120, check=False,
        )
        reference = json.loads(proc.stdout) if proc.stdout.strip() else {
            "reference_verdict": "REJECTED",
            "error": "reference-verifier-no-output",
            "stderr": proc.stderr[-2000:],
        }
    except Exception as exc:
        reference = {"reference_verdict": "REJECTED", "error": f"reference-verifier-failed:{type(exc).__name__}"}

    validator: dict[str, Any]
    try:
        public_cert = Path(public_cert_path).read_text()
        proc = subprocess.run(
            [sys.executable, str(FROZEN_VALIDATOR)],
            input=public_cert, capture_output=True, text=True, timeout=60, check=False,
        )
        validator = json.loads(proc.stdout) if proc.stdout.strip() else {
            "decision": "REJECT", "reason": "validator-no-output",
        }
    except Exception as exc:
        validator = {"decision": "REJECT", "reason": f"validator-failed:{type(exc).__name__}"}

    reference_accepted = reference.get("reference_verdict") == "ACCEPTED"
    validator_accepted = validator.get("decision") == "ACCEPT"
    final = "ACCEPTED" if (reference_accepted and validator_accepted) else "REJECTED"

    return {
        "reference_verdict": reference.get("reference_verdict"),
        "cryptographic_predicate": reference.get("cryptographic_predicate"),
        "certificate_integrity": reference.get("certificate_integrity"),
        "crypto_details": reference.get("crypto_details"),
        "certificate_errors": reference.get("certificate_errors"),
        "reference_error": reference.get("error"),
        "validator_decision": validator.get("decision"),
        "validator_reason": validator.get("reason"),
        "stage01_final_decision": final,
    }
