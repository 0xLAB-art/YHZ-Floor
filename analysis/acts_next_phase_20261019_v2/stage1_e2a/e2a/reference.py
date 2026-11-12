"""TRUSTED independent reference adjudicator.

The reference adjudicator holds the private target state and recomputes the
cryptographic predicate.  Two properties matter for the experiment:

* it consumes the **captured stdout**, pinned by the TEO's signed digest, and
  never an unreferenced output file written by the program.  It recomputes the
  digest of the bytes it is given and refuses to adjudicate if the digest
  does not match the TEO's pin;
* it parses the candidate output itself, with its own implementation of the
  strict single-object rule, so that the aggregator's cross-check
  ``reference.candidate_digest == observation.parsed_candidate_sha256`` is a
  genuine cross-implementation agreement test rather than a copy.

The predicate implementation below deliberately uses a *different* code path
from the frozen Stage 01 reference verifier: ECDSA public-key derivation and
signature verification go through ``cryptography``'s SECP256K1 implementation
instead of the frozen verifier's pure-Python curve arithmetic.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # pragma: no cover - direct execution support
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from e2a import canonical, remediation
else:
    from . import canonical, remediation

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

STATUS_ADJUDICATED = "ADJUDICATED"
STATUS_PIN_MISMATCH = "STDOUT_PIN_MISMATCH"
STATUS_UNPARSEABLE = "STDOUT_UNPARSEABLE"
STATUS_OBSERVATION_UNVERIFIED = "OBSERVATION_UNVERIFIED"


def _inv(value: int, modulus: int) -> int:
    return pow(value % modulus, -1, modulus)


def parse_candidate_independently(stdout_bytes: bytes) -> tuple[dict | None, str]:
    """Independent re-implementation of the strict single-object output rule."""
    text = stdout_bytes.decode("utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) != 1:
        return None, "EMPTY" if not lines else "AMBIGUOUS_MULTIPLE_LINES"
    try:
        parsed = json.loads(lines[0])
    except json.JSONDecodeError:
        return None, "NON_JSON"
    if not isinstance(parsed, dict):
        return None, "NOT_AN_OBJECT"
    return parsed, "OK"


def ecdsa_predicate(target: dict, candidate: dict) -> tuple[bool, dict]:
    """Independent ECDSA nonce-reuse predicate."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec, utils
    from cryptography.exceptions import InvalidSignature

    details: dict[str, Any] = {}
    try:
        d = int(candidate["d"], 16)
        k = int(candidate["k"], 16)
    except (KeyError, TypeError, ValueError):
        return False, {"candidate_lacks_d_or_k": True}
    try:
        sig1 = target["signature_1"]
        sig2 = target["signature_2"]
        r1 = int(sig1["r"], 16)
        r2 = int(sig2["r"], 16)
        z1 = int(sig1["z"], 16)
        z2 = int(sig2["z"], 16)
        s1 = int(sig1["s"], 16)
        s2 = int(sig2["s"], 16)
    except (KeyError, TypeError, ValueError):
        return False, {"target_missing_fields": True}
    try:
        expected = bytes.fromhex(target["public_key"][0]) + bytes.fromhex(target["public_key"][1])
        derived = ec.derive_private_key(d, ec.SECP256K1()).public_key().public_bytes(
            serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        public_key_matches = derived == b"\x04" + expected
        details["public_key_matches"] = public_key_matches
        details["repeated_r"] = r1 == r2
        recovered_k = ((z1 - z2) * _inv((s1 - s2) % N, N)) % N
        recovered_d = ((s1 * k - z1) * _inv(r1, N)) % N
        details["recovered_k_matches"] = recovered_k == k
        details["recovered_d_matches"] = recovered_d == d
        signatures_verify = True
        public = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), b"\x04" + expected)
        # `z` is the raw 32-byte message representative used by the fixture
        # generator, so it must be verified as a *prehash*; the default
        # ECDSA(Prehashed(SHA256)) algorithm would otherwise hash it again.
        algorithm = ec.ECDSA(utils.Prehashed(hashes.SHA256()))
        for z, r, s in ((z1, r1, s1), (z2, r2, s2)):
            try:
                public.verify(utils.encode_dss_signature(r, s), z.to_bytes(32, "big"), algorithm)
            except (InvalidSignature, ValueError):
                signatures_verify = False
                break
        details["signatures_verify"] = signatures_verify
        ok = (public_key_matches and details["repeated_r"] and details["recovered_k_matches"]
              and details["recovered_d_matches"] and signatures_verify)
        return ok, details
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False, {"parse_or_math_error": True}


def chacha_predicate(target: dict, candidate: dict) -> tuple[bool, dict]:
    """Independent ChaCha20 nonce-repeat predicate (keystream formulation)."""
    try:
        c1 = bytes.fromhex(target["ciphertext_1"])
        c2 = bytes.fromhex(target["ciphertext_2"])
        p1 = bytes.fromhex(target["known_plaintext_1"])
        p2 = bytes.fromhex(candidate["plaintext_2"])
    except (KeyError, TypeError, ValueError):
        return False, {"candidate_lacks_plaintext_2": True}
    if not (len(c1) == len(c2) == len(p1) == len(p2)):
        return False, {"lengths_match": False}
    keystream_1 = bytes(a ^ b for a, b in zip(c1, p1))
    keystream_2 = bytes(a ^ b for a, b in zip(c2, p2))
    return keystream_1 == keystream_2, {
        "keystream_recovery_matches": keystream_1 == keystream_2,
        "lengths_match": True,
    }


def evaluate_predicate(target_state: dict, candidate: dict | None) -> tuple[bool, dict]:
    if candidate is None:
        return False, {"candidate_absent": True}
    primitive = target_state.get("primitive")
    if primitive == "ECDSA_Nonce_Reuse":
        return ecdsa_predicate(target_state, candidate)
    if primitive == "ChaCha20_Nonce_Repeat":
        return chacha_predicate(target_state, candidate)
    return False, {"unsupported_primitive": True}


def adjudicate(spec: dict[str, Any], keys_dir: Path, bundle_path: Path, policy_path: Path) -> dict[str, Any]:
    """Adjudicate one case and return the signed reference envelope."""
    signing = remediation.protected_signing()
    context_module = remediation.context_validator()
    policy, _document = remediation.load_policy(policy_path)

    observation_envelope = json.loads(Path(spec["observation_path"]).read_text(encoding="utf-8"))
    observation_payload = observation_envelope["record"]["payload"]

    # Defence in depth: the reference does not adjudicate an observation whose
    # signature does not verify or whose context does not bind.
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

    candidate, parse_status = parse_candidate_independently(stdout_bytes)
    candidate_digest = canonical.sha_object(candidate) if candidate is not None else None

    status = STATUS_ADJUDICATED
    crypto_ok = False
    crypto_details: dict[str, Any] = {}
    if not observation_signature_valid or not context_signature_valid:
        status = STATUS_OBSERVATION_UNVERIFIED
        crypto_details = {"observation_signature_valid": observation_signature_valid,
                          "observation_context_signature_valid": context_signature_valid}
    elif stdout_pin is None:
        status = STATUS_UNPARSEABLE
        crypto_details = {"no_stdout_pin": True}
    elif stdout_recomputed != stdout_pin:
        status = STATUS_PIN_MISMATCH
        crypto_details = {"stdout_pin_mismatch": True}
    elif parse_status != "OK":
        status = STATUS_UNPARSEABLE
        crypto_details = {"parse_status": parse_status}
    else:
        crypto_ok, crypto_details = evaluate_predicate(spec["target_state"], candidate)

    verdict = "ACCEPTED" if (status == STATUS_ADJUDICATED and crypto_ok) else "REJECTED"

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
    key_path = _key_path_for_role(keys_dir, remediation.ROLE_REFERENCE)
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


def _key_path_for_role(keys_dir: Path, role: str) -> Path:
    for candidate in sorted(Path(keys_dir).glob("*.json")):
        record = json.loads(candidate.read_text(encoding="utf-8"))
        if record.get("role") == role:
            return candidate
    raise KeyError(f"no private key for role {role!r} in {keys_dir}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="E2A independent reference adjudicator")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--keys", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    args = parser.parse_args(argv)

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    envelope = adjudicate(spec, args.keys, args.bundle, args.policy)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical.canonical_bytes(envelope))
    payload = envelope["record"]["payload"]
    print(json.dumps({"case_id": payload["case_id"], "status": payload["status"],
                      "verdict": payload["verdict"], "crypto_ok": payload["crypto_ok"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
