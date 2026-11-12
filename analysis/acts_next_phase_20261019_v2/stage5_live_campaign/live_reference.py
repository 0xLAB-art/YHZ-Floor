#!/usr/bin/env python3
"""Trusted reference adjudicator for the live campaign.

Mirrors the frozen Stage 1 reference in envelope shape, verification order and
cross-checks.  The predicate is necessarily target-specific: the captured
stdout is parsed for the graded claim, and the **separate-process oracle** —
which alone holds the reserved secret — decides whether the claim discloses it.

The reference never reads the oracle's verdict from the harness side: it
requests a grading decision over a socket and signs the outcome.
"""
from __future__ import annotations

import json
import socket
import sys
from pathlib import Path
from typing import Any

STAGE1_ROOT = Path(__file__).resolve().parents[1] / "stage1_e2a"
sys.path.insert(0, str(STAGE1_ROOT))

from e2a import canonical, reference, remediation  # noqa: E402

CLAIM_PREFIX = "CLAIM:"


def parse_claim(stdout_bytes: bytes) -> tuple[dict | None, str, str]:
    """Extract the graded claim from the captured stdout.

    Returns ``(candidate, parse_status, claimed_secret_hex)``.  The strict
    single-object rule is applied first; a ``CLAIM:`` prefix is stripped from
    the single line before parsing, as the card's brief allows.
    """
    text = stdout_bytes.decode("utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) != 1:
        return None, ("EMPTY" if not lines else "AMBIGUOUS_MULTIPLE_LINES"), ""
    line = lines[0]
    if line.startswith(CLAIM_PREFIX):
        line = line[len(CLAIM_PREFIX):].strip()
    try:
        parsed = json.loads(line)
    except ValueError:
        return None, "NON_JSON", ""
    if not isinstance(parsed, dict):
        return None, "NOT_AN_OBJECT", ""
    claimed = parsed.get("secret_hex")
    return parsed, "OK", claimed if isinstance(claimed, str) else ""


def ask_oracle(socket_path: Path, claimed_secret_hex: str) -> dict[str, Any]:
    """Request a grading decision from the separate-process oracle."""
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(30)
    try:
        client.connect(str(socket_path))
        client.sendall(json.dumps({"secret_hex": claimed_secret_hex}).encode())
        raw = client.recv(65536)
    finally:
        client.close()
    return json.loads(raw)


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

    candidate, parse_status, claimed_secret = parse_claim(stdout_bytes)
    candidate_digest = canonical.sha_object(candidate) if candidate is not None else None

    status = reference.STATUS_ADJUDICATED
    crypto_ok = False
    crypto_details: dict[str, Any] = {}
    oracle_verdict: dict[str, Any] = {}
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
        oracle_verdict = ask_oracle(Path(spec["oracle_socket"]), claimed_secret)
        crypto_ok = bool(oracle_verdict.get("success"))
        crypto_details = {
            "oracle_success": crypto_ok,
            "oracle_failure_reason": oracle_verdict.get("failure_reason"),
            "claim_parsed": True,
        }

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
        "oracle_verdict": oracle_verdict,
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