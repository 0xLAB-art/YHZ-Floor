"""INDEPENDENT ground-truth re-derivation (adjudicator side).

This module shares no code with ``e2a/reference.py`` or with the frozen Stage
01 reference verifier.  It re-derives, for every case, whether the *executed
program* actually satisfied the target predicate, and whether the presented
certificate's declarations are consistent with the execution that produced
them.  The conjunction of the two is the independently derived ground truth.

The adjudicator therefore never has to trust either evaluator's verdict, and
never has to trust the frozen label table: it recomputes the label and then
reports any disagreement with the frozen table as a validity failure.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha_object(value: Any) -> str:
    import hashlib
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def parse_output(stdout_bytes: bytes) -> tuple[dict | None, str]:
    """Independent parse of the captured stdout (single JSON object rule)."""
    text = stdout_bytes.decode("utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) != 1:
        return None, "NO_SINGLE_CLAIM"
    try:
        parsed = json.loads(lines[0])
    except json.JSONDecodeError:
        return None, "NOT_JSON"
    if not isinstance(parsed, dict):
        return None, "NOT_AN_OBJECT"
    return parsed, "OK"


def ecdsa_truth(target: dict[str, Any], candidate: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Independent ECDSA nonce-reuse verification."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec, utils

    details: dict[str, Any] = {}
    try:
        d = int(candidate["d"], 16)
        k = int(candidate["k"], 16)
        sig1, sig2 = target["signature_1"], target["signature_2"]
        r1, r2 = int(sig1["r"], 16), int(sig2["r"], 16)
        z1, z2 = int(sig1["z"], 16), int(sig2["z"], 16)
        s1, s2 = int(sig1["s"], 16), int(sig2["s"], 16)
    except (KeyError, TypeError, ValueError):
        return False, {"candidate_fields_missing": True}

    expected_x = int(target["public_key"][0], 16)
    expected_y = int(target["public_key"][1], 16)
    derived = ec.derive_private_key(d, ec.SECP256K1()).public_key().public_numbers()
    details["public_key_matches"] = (derived.x == expected_x and derived.y == expected_y)
    details["repeated_r"] = r1 == r2
    recovered_k = ((z1 - z2) * pow((s1 - s2) % N, -1, N)) % N
    recovered_d = ((s1 * k - z1) * pow(r1, -1, N)) % N
    details["recovered_k_matches"] = recovered_k == k
    details["recovered_d_matches"] = recovered_d == d

    signatures_verify = True
    try:
        public = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256K1(),
            b"\x04" + int(expected_x).to_bytes(32, "big") + int(expected_y).to_bytes(32, "big"))
        for z, r, s in ((z1, r1, s1), (z2, r2, s2)):
            public.verify(utils.encode_dss_signature(r, s), z.to_bytes(32, "big"),
                          ec.ECDSA(utils.Prehashed(hashes.SHA256())))
    except (InvalidSignature, ValueError, TypeError):
        signatures_verify = False
    details["signatures_verify"] = signatures_verify
    ok = all(details.values())
    return ok, details


def chacha_truth(target: dict[str, Any], candidate: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Independent ChaCha20 nonce-repeat verification (plaintext formulation)."""
    try:
        c1 = bytes.fromhex(target["ciphertext_1"])
        c2 = bytes.fromhex(target["ciphertext_2"])
        p1 = bytes.fromhex(target["known_plaintext_1"])
        p2 = bytes.fromhex(candidate["plaintext_2"])
    except (KeyError, TypeError, ValueError):
        return False, {"candidate_fields_missing": True}
    if not (len(c1) == len(c2) == len(p1) == len(p2)):
        return False, {"lengths_match": False}
    recovered = bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))
    details = {"recovered_plaintext_matches": recovered == p2, "lengths_match": True}
    return all(details.values()), details


def predicate_holds(target_state: dict[str, Any], candidate: dict | None) -> tuple[bool, dict[str, Any]]:
    if candidate is None:
        return False, {"candidate_absent": True}
    primitive = target_state.get("primitive")
    if primitive == "ECDSA_Nonce_Reuse":
        return ecdsa_truth(target_state, candidate)
    if primitive == "ChaCha20_Nonce_Repeat":
        return chacha_truth(target_state, candidate)
    return False, {"unsupported_primitive": True}


def derive_ground_truth(case: dict[str, Any], case_dir: Path,
                         prior_contexts: dict[str, int]) -> dict[str, Any]:
    """Independently derive the ground truth for one case from retained artifacts.

    *case* is the raw-results row; *case_dir* is the directory holding the
    retained artifacts; *prior_contexts* maps an already-consumed
    (target, attempt, epoch, role, kind) binding to the case that consumed it.
    """
    facts: dict[str, Any] = {}
    observation = json.loads((case_dir / "observation.json").read_text(encoding="utf-8"))
    reference = json.loads((case_dir / "reference.json").read_text(encoding="utf-8"))
    target_state = json.loads((case_dir / "baseline" / "target_state.private.json").read_text(encoding="utf-8"))
    certificate = json.loads((case_dir / "certificate.e2a.json").read_text(encoding="utf-8"))

    observation_payload = observation["record"]["payload"]
    stdout_path = observation_payload.get("stdout_path")
    stdout_bytes = Path(stdout_path).read_bytes() if stdout_path else b""
    candidate, parse_status = parse_output(stdout_bytes)
    solved, predicate_details = predicate_holds(target_state, candidate)
    facts["executed_program_solved_target"] = solved
    facts["executed_output_parse_status"] = parse_status
    facts["predicate_details"] = predicate_details

    # -- binding facts ------------------------------------------------------
    evidence = certificate.get("evidence") or {}
    bindings_ok = True
    binding_problems: list[str] = []

    if "observation" not in evidence:
        bindings_ok = False
        binding_problems.append("observation-record-absent")
    if "reference" not in evidence:
        bindings_ok = False
        binding_problems.append("reference-record-absent")

    presented_observation = evidence.get("observation") or observation
    presented_reference = evidence.get("reference") or reference
    observation_payload = presented_observation["record"]["payload"]

    if certificate.get("agent_artifact", {}).get("sha256") != observation_payload.get("program_source_sha256"):
        bindings_ok = False
        binding_problems.append("declared-program-is-not-the-executed-program")
    if certificate.get("candidate_output", {}).get("sha256") != observation_payload.get("parsed_candidate_sha256"):
        bindings_ok = False
        binding_problems.append("declared-candidate-output-is-not-the-observed-output")
    if presented_reference["record"]["payload"].get("observation_record_sha256") != sha_object(presented_observation):
        bindings_ok = False
        binding_problems.append("reference-does-not-adjudicate-the-presented-observation")
    if presented_reference["record"]["payload"].get("stdout_sha256") != observation_payload.get("stdout_sha256"):
        bindings_ok = False
        binding_problems.append("reference-pins-a-different-stdout")
    context = presented_observation.get("context") or {}
    if (certificate.get("attempt_id") != context.get("attempt_id")
            or certificate.get("target_id") != context.get("target_id")
            or certificate.get("epoch") != context.get("epoch")):
        bindings_ok = False
        binding_problems.append("certificate-context-differs-from-signed-observation-context")

    context_key = json.dumps({key: context.get(key) for key in
                              ("kind", "domain", "target_id", "attempt_id", "epoch", "role")},
                             sort_keys=True, separators=(",", ":"))
    if context_key in prior_contexts:
        bindings_ok = False
        binding_problems.append(f"observation-context-replayed-from-{prior_contexts[context_key]}")
    facts["binding_problems"] = binding_problems
    facts["bindings_ok"] = bindings_ok

    derived_gt_success = bool(solved and bindings_ok)
    facts["derived_gt_success"] = derived_gt_success
    facts["derived_decision_class"] = "attributable" if derived_gt_success else "not_attributable"
    return facts
