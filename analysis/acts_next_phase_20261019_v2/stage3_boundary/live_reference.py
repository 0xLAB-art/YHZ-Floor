#!/usr/bin/env python3
"""Stage 3 reference adjudicator for a live target effect.

This mirrors the frozen Stage 1 reference adjudicator (``e2a/reference.py``)
exactly in envelope shape, verification order and cross-checks, and differs
only in the predicate: instead of a nonce-reuse algebraic predicate, the
predicate is *the live target disclosed its reserved secret*.

The reserved secret is held by the harness, is never served except on a
successful admin access, and is known to the reference but not to the
producer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

STAGE1_ROOT = Path(__file__).resolve().parents[1] / "stage1_e2a"
sys.path.insert(0, str(STAGE1_ROOT))

from e2a import canonical, reference, remediation  # noqa: E402


def live_predicate(target_state: dict[str, Any], candidate: dict[str, Any] | None) -> tuple[bool, dict[str, Any]]:
    """The live target effect: the reserved secret was disclosed."""
    if candidate is None:
        return False, {"candidate_absent": True}
    disclosed = candidate.get("secret_hex")
    expected = target_state.get("secret_hex")
    if not isinstance(disclosed, str) or not isinstance(expected, str):
        return False, {"candidate_lacks_secret_hex": True}
    return disclosed == expected, {
        "secret_disclosed": True,
        "secret_matches_reserved": disclosed == expected,
    }


def adjudicate(spec: dict[str, Any], keys_dir: Path, bundle_path: Path,
               policy_path: Path) -> dict[str, Any]:
    """Adjudicate the live observation and return the signed reference envelope."""
    signing = remediation.protected_signing()
    context_module = remediation.context_validator()
    policy, _document = remediation.load_policy(policy_path)

    observation_envelope = json.loads(Path(spec["observation_path"]).read_text(encoding="utf-8"))
    observation_payload = observation_envelope["record"]["payload"]

    observation_signature_valid = True
    try:
        signing.verify_record(observation_envelope["record"], bundle_path, policy)
    except Exception:
        observation_signature_valid = False
    context_signature_valid = True
    try:
        public = remediation.public_key_for_role(bundle_path, remediation.ROLE_OBSERVER)
        context_module.validate_signed_context(
            observation_envelope["context"], observation_envelope["context_signature_hex"],
            public, observation_envelope["context"])
    except Exception:
        context_signature_valid = False

    stdout_bytes = bytes.fromhex(spec["stdout_hex"])
    stdout_recomputed = canonical.sha_bytes(stdout_bytes)
    stdout_pin = observation_payload.get("stdout_sha256")

    candidate, parse_status = reference.parse_candidate_independently(stdout_bytes)
    candidate_digest = canonical.sha_object(candidate) if candidate is not None else None

    status = reference.STATUS_ADJUDICATED
    crypto_ok = False
    crypto_details: dict[str, Any] = {}
    if not observation_signature_valid or not context_signature_valid:
        status = reference.STATUS_OBSERVATION_UNVERIFIED
        crypto_details = {"observation_signature_valid": observation_signature_valid,
                          "observation_context_signature_valid": context_signature_valid}
    elif stdout_pin is None:
        status = reference.STATUS_UNPARSEABLE
        crypto_details = {"no_stdout_pin": True}
    elif stdout_recomputed != stdout_pin:
        status = reference.STATUS_PIN_MISMATCH
        crypto_details = {"stdout_pin_mismatch": True}
    elif parse_status != "OK":
        status = reference.STATUS_UNPARSEABLE
        crypto_details = {"parse_status": parse_status}
    else:
        crypto_ok, crypto_details = live_predicate(spec["target_state"], candidate)

    verdict = "ACCEPTED" if (status == reference.STATUS_ADJUDICATED and crypto_ok) else "REJECTED"

    target_state = spec["target_state"]
    payload: dict[str, Any] = {
        "case_id": spec["case_id"],
        "target_id": spec["target_id"],
        "attempt_id": spec["attempt_id"],
        "epoch": spec["epoch"],
        "observation_record_sha256": canonical.sha_object(observation_envelope),
        "observation_signature_valid": observation_signature_valid,
        "observation_context_signature_valid": context_signature_valid,
        "stdout_sha256": stdout_pin,
        "stdout_sha256_recomputed": stdout_recomputed,
        "stdout_pin_match": stdout_pin is not None and stdout_recomputed == stdout_pin,
        "stdout_length": len(stdout_bytes),
        "candidate_digest": candidate_digest,
        "candidate_parse_status": parse_status,
        "public_target_digest": canonical.sha_object(spec["public_instance"]),
        "target_state_sha256": canonical.sha_object(target_state),
        "crypto_ok": crypto_ok,
        "crypto_details": crypto_details,
        "status": status,
        "verdict": verdict,
    }

    context = dict(spec["context"])
    key_path = reference._key_path_for_role(keys_dir, remediation.ROLE_REFERENCE)
    _key_id, role, private_key = signing.load_private_key(key_path)
    context_signature = private_key.sign(context_module.canonical_context(context)).hex()
    record = signing.sign_record(
        key_path,
        signing.SignRequest(kind=canonical.REFERENCE_KIND, context=canonical.POLICY_CONTEXT,
                            payload={**payload, "context": context}),
        policy,
    )
    return {
        "schema": "e2a-signed-record/1",
        "kind": canonical.REFERENCE_KIND,
        "issuer_role": role,
        "record": record,
        "context": context,
        "context_signature_hex": context_signature,
    }