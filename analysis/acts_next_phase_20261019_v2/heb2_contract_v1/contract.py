#!/usr/bin/env python3
"""Contract V2 — the Stage 1 contract with an explicit execution-completion semantic.

The frozen Stage 1 aggregator is **not modified**.  V2 composes it by
subclassing and adds exactly one precondition, evaluated on the attribution
boundary (equivalent to evaluating it immediately before the terminal
predicate step — see ``heb2_contract_v1/PREREGISTRATION.md`` §3).

The module also exposes the soundness property as an executable check, so the
property can be re-verified against any bundle rather than merely asserted.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

STAGE1_ROOT = Path(__file__).resolve().parents[1] / "stage1_e2a"
sys.path.insert(0, str(STAGE1_ROOT))

from e2a import canonical, remediation  # noqa: E402
from e2a.aggregator import (  # noqa: E402
    DECISION_INCONCLUSIVE,
    DECISION_REJECT,
    DECISION_SUCCESS,
    Aggregator,
)

SEMANTIC_OUTPUT = "output"
SEMANTIC_COMPLETION = "completion"
SEMANTICS = (SEMANTIC_OUTPUT, SEMANTIC_COMPLETION)

REASON_EXECUTION_NOT_COMPLETED = "execution-not-completed"


class ContractV2(Aggregator):
    """The Stage 1 evaluator under one of two preregistered semantics."""

    def __init__(self, bundle_path: Path, policy_path: Path, ledger_path: Path | None,
                 semantic: str = SEMANTIC_OUTPUT):
        if semantic not in SEMANTICS:
            raise ValueError(f"unknown semantic {semantic!r}")
        super().__init__(bundle_path, policy_path, ledger_path)
        self.semantic = semantic

    def evaluate(self, bundle: dict[str, Any]) -> dict[str, Any]:
        """Evaluate under the configured semantic."""
        result = super().evaluate(bundle)
        if result["decision"] != DECISION_SUCCESS:
            return result
        if self.semantic == SEMANTIC_OUTPUT:
            return result
        status = _observation_status(bundle)
        if status == "EXECUTED":
            return result
        return {
            "decision": DECISION_REJECT,
            "reason": REASON_EXECUTION_NOT_COMPLETED,
            "reason_family": "contradicted_by_evidence",
            "check_order": list(result["check_order"]) + ["execution_completion"],
            "chain": [],
            "execution_status": status,
        }


def _observation_payload(bundle: dict[str, Any]) -> dict[str, Any] | None:
    evidence = bundle.get("certificate", {}).get("evidence")
    if not isinstance(evidence, dict):
        return None
    observation = evidence.get("observation")
    if not isinstance(observation, dict):
        return None
    record = observation.get("record")
    if not isinstance(record, dict):
        return None
    payload = record.get("payload")
    return payload if isinstance(payload, dict) else None


def _observation_status(bundle: dict[str, Any]) -> str | None:
    payload = _observation_payload(bundle)
    return payload.get("execution_status") if payload else None


def soundness_violations(bundle: dict[str, Any], semantic: str,
                          bundle_path: Path, policy_path: Path) -> list[str]:
    """Return the list of soundness-property clauses the bundle violates.

    An empty list means the bundle satisfies the property S1 of the
    preregistration.  The check is performed against the bundle's own
    contents, independently of the decision the contract reached.
    """
    violations: list[str] = []
    certificate = bundle.get("certificate", {})
    evidence = certificate.get("evidence", {}) if isinstance(certificate, dict) else {}
    observation = evidence.get("observation") if isinstance(evidence, dict) else None
    reference = evidence.get("reference") if isinstance(evidence, dict) else None
    if not isinstance(observation, dict) or not isinstance(reference, dict):
        return ["evidence-missing"]

    signing = remediation.protected_signing()
    policy, _document = remediation.load_policy(policy_path)

    for label, envelope in (("observation", observation), ("reference", reference)):
        try:
            signing.verify_record(envelope["record"], bundle_path, policy)
        except Exception:
            violations.append(f"{label}-record-does-not-verify")

    for label, envelope, kind, role in (
        ("observation", observation, canonical.OBSERVATION_KIND, remediation.ROLE_OBSERVER),
        ("reference", reference, canonical.REFERENCE_KIND, remediation.ROLE_REFERENCE),
    ):
        context = envelope.get("context")
        if not isinstance(context, dict):
            violations.append(f"{label}-context-missing")
            continue
        for field in ("target_id", "attempt_id", "epoch"):
            if context.get(field) != certificate.get(field):
                violations.append(f"{label}-context-not-bound-to-certificate-{field}")
        if envelope.get("kind") != kind or envelope.get("issuer_role") != role:
            violations.append(f"{label}-kind-or-role")

    observation_payload = observation["record"].get("payload", {})
    reference_payload = reference["record"].get("payload", {})
    if reference_payload.get("stdout_sha256") != observation_payload.get("stdout_sha256"):
        violations.append("stdout-pin-mismatch")
    if reference_payload.get("candidate_digest") != (
            observation_payload.get("parse", {}).get("parsed_candidate_sha256")):
        violations.append("candidate-digest-mismatch")
    if reference_payload.get("crypto_ok") is not True or reference_payload.get("verdict") != "ACCEPTED":
        violations.append("predicate-not-adjudicated-true")
    if semantic == SEMANTIC_COMPLETION and observation_payload.get("execution_status") != "EXECUTED":
        violations.append("execution-not-completed")
    return violations