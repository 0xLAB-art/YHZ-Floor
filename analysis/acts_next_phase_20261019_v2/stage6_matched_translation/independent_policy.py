#!/usr/bin/env python3
"""Independent verification policy for the in-toto arms.

This program is the *inspection* an in-toto layout runs.  It is deliberately
**independent of the ACTS aggregator**: it imports nothing from
``e2a.aggregator`` and re-derives every check from the contract, and it
adjudicates the cryptographic predicate with the project's own **frozen Stage
01 reference verifier** (``contract_sound_stage01_reference_verifier_v2.py``),
which uses pure-Python elliptic-curve arithmetic rather than the E2A
reference's ``cryptography`` path.

The optional ledger makes the inspection *stateful*: it records each consumed
observation context and refuses a context it has already admitted.  The
stateless variant (no ledger) cannot express cross-case replay protection —
which is a property of the *inspection*, not of in-toto, since in-toto
inspections may run arbitrary external programs.

Usage:
    independent_policy.py <case_dir> <bundle> <policy> <ledger_path|->
Exit 0 iff the claim is attributable under this policy, 1 otherwise.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

STAGE1_REFERENCE = Path(__file__).resolve().parents[2] / "contract_sound_stage01_reference_verifier_v2.py"

FORMAT = "heb1-protected-signing-v1"
DOMAIN = "heb1:evidence:v1"


def canonical_bytes(value: Any) -> bytes:
    """The canonical encoding used for every digest."""
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def signing_bytes(value: Any) -> bytes:
    """The canonical encoding the signing implementation signs.

    The signing code appends a trailing newline; the digest form does not.
    """
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def canonical_context_bytes(value: Any) -> bytes:
    """The context canonicalisation used by the context validator."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha_object(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_public_keys(bundle_path: Path) -> dict[str, dict[str, str]]:
    bundle = json.loads(bundle_path.read_text())
    return {issuer["key_id"]: issuer for issuer in bundle["issuers"]}


def verify_envelope_signature(envelope: dict[str, Any], issuers: dict[str, dict[str, str]],
                              policy: dict[str, Any]) -> tuple[bool, str]:
    """Verify one signed record and its role/kind authorization."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    record = envelope.get("record", {})
    required = {"format", "domain", "kind", "context", "issuer_role", "key_id",
                "payload", "signature_hex"}
    if set(record) != required:
        return False, "record-shape"
    if record["format"] != FORMAT or record["domain"] != DOMAIN:
        return False, "record-domain"
    issuer = issuers.get(record["key_id"])
    if issuer is None or issuer["role"] != record["issuer_role"]:
        return False, "unknown-issuer"
    role_policy = policy.get("roles", {}).get(record["issuer_role"])
    if not role_policy or record["kind"] not in role_policy.get("kinds", []):
        return False, "role-not-authorized"
    unsigned = {key: record[key] for key in required if key != "signature_hex"}
    try:
        public = Ed25519PublicKey.from_public_bytes(bytes.fromhex(issuer["public_key_hex"]))
        public.verify(bytes.fromhex(record["signature_hex"]), signing_bytes(unsigned))
    except (InvalidSignature, ValueError):
        return False, "bad-signature"
    return True, "ok"


def check_context_binding(envelope: dict[str, Any], certificate: dict[str, Any],
                          issuers: dict[str, dict[str, str]]) -> tuple[bool, str]:
    """The context signature must verify and bind to the certificate's identity."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    context = envelope.get("context")
    if not isinstance(context, dict):
        return False, "context-missing"
    for field in ("target_id", "attempt_id", "epoch"):
        if context.get(field) != certificate.get(field):
            return False, f"context-{field}-mismatch"
    issuer = next((entry for entry in issuers.values()
                   if entry["role"] == envelope.get("issuer_role")), None)
    signature_hex = envelope.get("context_signature_hex")
    if issuer is None or not isinstance(signature_hex, str):
        return False, "context-signature-unavailable"
    try:
        public = Ed25519PublicKey.from_public_bytes(bytes.fromhex(issuer["public_key_hex"]))
        public.verify(bytes.fromhex(signature_hex), canonical_context_bytes(context))
    except (InvalidSignature, ValueError):
        return False, "context-bad-signature"
    return True, "ok"


def check_cross_record_consistency(observation: dict[str, Any], reference: dict[str, Any],
                                   certificate: dict[str, Any]) -> tuple[bool, str]:
    """The reference must adjudicate this observation, and the digests must agree."""
    observation_payload = observation["record"]["payload"]
    reference_payload = reference["record"]["payload"]
    if reference_payload.get("observation_record_sha256") != sha_object(observation):
        return False, "reference-adjudicates-other-observation"
    if reference_payload.get("stdout_sha256") != observation_payload.get("stdout_sha256"):
        return False, "stdout-pin-mismatch"
    observed_digest = observation_payload.get("parse", {}).get("parsed_candidate_sha256")
    if reference_payload.get("candidate_digest") != observed_digest:
        return False, "candidate-digest-mismatch"
    if certificate.get("agent_artifact", {}).get("sha256") != observation_payload.get("program_source_sha256"):
        return False, "declared-source-mismatch"
    if certificate.get("candidate_output", {}).get("sha256") != observed_digest:
        return False, "declared-candidate-mismatch"
    return True, "ok"


def adjudicate_predicate_independently(case_dir: Path) -> tuple[bool, str]:
    """Adjudicate the predicate with the frozen Stage 01 reference verifier.

    That verifier implements its own pure-Python curve arithmetic, so it is an
    implementation independent of the E2A reference.  Its certificate check
    concerns the Stage 01 certificate schema and is therefore not used here;
    only its recomputed cryptographic predicate is taken.
    """
    baseline = case_dir / "baseline"
    bundle = {
        "case_id": case_dir.name,
        "certificate_path": str(baseline / "certificate.private.json"),
        "target_state_path": str(baseline / "target_state.private.json"),
        "candidate_path": str(case_dir / "candidate_output.json"),
    }
    bundle_path = case_dir / "stage01_reference_bundle.json"
    bundle_path.write_text(json.dumps(bundle))
    try:
        completed = subprocess.run([sys.executable, str(STAGE1_REFERENCE), str(bundle_path)],
                                   capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return False, "reference-timeout"
    try:
        verdict = json.loads(completed.stdout)
    except ValueError:
        return False, "reference-unparseable"
    if verdict.get("cryptographic_predicate") is True:
        return True, "predicate-true"
    return False, "predicate-false"


def context_fingerprint(envelope: dict[str, Any]) -> str:
    context = envelope.get("context", {})
    material = "|".join(str(context.get(field)) for field in
                         ("target_id", "attempt_id", "epoch", "role", "kind"))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def ledger_admits(ledger_path: Path, envelope: dict[str, Any]) -> tuple[bool, str]:
    """Stateful replay protection: a context may be admitted only once."""
    fingerprint = context_fingerprint(envelope)
    if ledger_path.exists():
        for line in ledger_path.read_text().splitlines():
            if line.strip() and json.loads(line).get("context") == fingerprint:
                return False, "context-already-consumed"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"context": fingerprint}, sort_keys=True) + "\n")
    return True, "ok"


def main() -> int:
    if len(sys.argv) != 5:
        print(json.dumps({"error": "usage: independent_policy.py <case_dir> <bundle> <policy> <ledger|->"}))
        return 2
    case_dir = Path(sys.argv[1])
    bundle_path = Path(sys.argv[2])
    policy_path = Path(sys.argv[3])
    ledger_arg = sys.argv[4]

    issuers = load_public_keys(bundle_path)
    policy = json.loads(policy_path.read_text())
    certificate = json.loads((case_dir / "certificate.e2a.json").read_text())
    evidence = certificate.get("evidence", {})
    observation = evidence.get("observation")
    reference = evidence.get("reference")
    checks = []
    if not isinstance(observation, dict) or not isinstance(reference, dict):
        # The claim presents no evidence record: the policy has nothing to bind.
        missing = "observation" if not isinstance(observation, dict) else "reference"
        checks.append({"check": "evidence-present", "ok": False, "reason": f"{missing}-missing"})
        print(json.dumps({"attributable": False, "checks": checks}, sort_keys=True))
        return 1
    checks.append({"check": "evidence-present", "ok": True, "reason": "ok"})
    for label, envelope in (("observation", observation), ("reference", reference)):
        ok, reason = verify_envelope_signature(envelope, issuers, policy)
        checks.append({"check": f"{label}-signature", "ok": ok, "reason": reason})
    for label, envelope in (("observation", observation), ("reference", reference)):
        ok, reason = check_context_binding(envelope, certificate, issuers)
        checks.append({"check": f"{label}-context-binding", "ok": ok, "reason": reason})
    ok, reason = check_cross_record_consistency(observation, reference, certificate)
    checks.append({"check": "cross-record-consistency", "ok": ok, "reason": reason})
    ok, reason = adjudicate_predicate_independently(case_dir)
    checks.append({"check": "predicate-independent", "ok": ok, "reason": reason})
    if ledger_arg != "-":
        ok, reason = ledger_admits(Path(ledger_arg), observation)
        checks.append({"check": "replay-ledger", "ok": ok, "reason": reason})

    attributable = all(check["ok"] for check in checks)
    print(json.dumps({"attributable": attributable, "checks": checks}, sort_keys=True))
    return 0 if attributable else 1


if __name__ == "__main__":
    raise SystemExit(main())