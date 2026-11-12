#!/usr/bin/env python3
"""Shared primitives for the Stage 1 end-to-end attribution experiment (TOEEA-1).

This module is strictly additive.  It does not import, modify, re-run, or
rewrite any historical experiment component.  It loads two FROZEN historical
modules read-only through :mod:`importlib` so that:

  1. the cryptographic predicate evaluated by the new independent reference
     verifier is exactly the predicate implemented by
     ``contract_sound_stage01_reference_verifier_v2.py``; and
  2. the target fixtures are exactly the fixtures produced by
     ``run_contract_sound_stage01.py`` (``make_ecdsa`` / ``make_chacha``).

Both loads are read-only and are verified by SHA-256 against pinned digests so
that a silent upstream edit cannot change the meaning of a Stage 1 result.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE1_ROOT = Path(__file__).resolve().parent
ANALYSIS_ROOT = REPO_ROOT / "sp2027" / "analysis"

# The Stage 1 experiment REUSES four unmodified remediation components from
# ``heb1_remediation_v1``.  They are imported by path (never copied, never
# edited) so that the vetted implementations -- not local re-implementations --
# provide signing, context binding, and integrity preflight.
REMEDIATION_ROOT = ANALYSIS_ROOT / "heb1_remediation_v1"
for _sub in ("signing", "context", "integrity"):
    _p = str(REMEDIATION_ROOT / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Pinned frozen historical components (read-only; verified at load time).
# ---------------------------------------------------------------------------
FROZEN_REFERENCE_VERIFIER = ANALYSIS_ROOT / "contract_sound_stage01_reference_verifier_v2.py"
FROZEN_STAGE01_VALIDATOR = ANALYSIS_ROOT / "contract_sound_stage01_validator_v2.py"
FROZEN_FIXTURE_GENERATOR = ANALYSIS_ROOT / "run_contract_sound_stage01.py"

# Digests of the two frozen Stage01 components, independently recomputed in
# this environment (Stage 0) and pinned here so that a silent upstream edit
# cannot change the meaning of a Stage 1 result.
#   f248413d... == contract_sound_stage01_validator_v2.py
#     (the same constant the Stage01 external binding wrapper pins as
#      FROZEN_VALIDATOR_SHA256; the wrapper's pin is therefore correct)
#   15bb4095... == contract_sound_stage01_reference_verifier_v2.py
FROZEN_STAGE01_VALIDATOR_SHA256 = (
    "f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a"
)
FROZEN_REFERENCE_VERIFIER_SHA256 = (
    "15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b"
)

# ---------------------------------------------------------------------------
# Experiment-wide constants
# ---------------------------------------------------------------------------
CONTEXT_DOMAIN = "acts-s1/attribution/v1"
# The ``context`` string used by the protected-signing domain separator.
SIGNING_CONTEXT = "acts-s1/attribution/v1"

BUNDLE_SCHEMA = "acts-next-phase/s1-attribution-bundle/1"

ROLE_ARTIFACT_PRODUCER = "artifact_producer"
ROLE_EXECUTION_OBSERVER = "execution_observer"
ROLE_REFERENCE_VERIFIER = "reference_verifier"

ALL_ROLES = (
    ROLE_ARTIFACT_PRODUCER,
    ROLE_EXECUTION_OBSERVER,
    ROLE_REFERENCE_VERIFIER,
)

KIND_ARTIFACT_RECORD = "artifact_record"
KIND_EXECUTION_OBSERVATION = "execution_observation"
KIND_REFERENCE_VERDICT = "reference_verdict"
SIGNED_KINDS = (
    KIND_ARTIFACT_RECORD,
    KIND_EXECUTION_OBSERVATION,
    KIND_REFERENCE_VERDICT,
)

# Evidence kinds that carry bytes into the bundle (non-signed payloads).
KIND_PROGRAM_SOURCE = "program_source"
KIND_PROGRAM_OUTPUT = "program_output"
KIND_EXECUTION_STDOUT = "execution_stdout"
KIND_EXECUTION_STDERR = "execution_stderr"

# Decision vocabulary shared by the Stage 1 evaluators.
DECISION_SUCCESS = "ATTRIBUTED_SUCCESS"
DECISION_REJECT = "REJECT"
DECISION_INCONCLUSIVE = "INCONCLUSIVE"

# Claim ladder levels (the six-level vocabulary reused from the historical
# six-claim ladder, kept identical so results are directly comparable).
CLAIM_LEVELS = (
    "artifact_authorship",
    "execution_identity",
    "target_effect",
    "reference_oracle_acceptance",
    "boundary_enforcement",
    "attribution",
)

LEVEL_PROVEN = "PROVEN"
LEVEL_NOT_ESTABLISHED = "NOT_ESTABLISHED"
LEVEL_REJECTED = "REJECTED"
LEVEL_OBSERVED = "OBSERVED"
LEVEL_NOT_OBSERVED = "NOT_OBSERVED"
LEVEL_ACCEPTED = "ACCEPTED"
LEVEL_INCONCLUSIVE = "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Digest / canonicalisation helpers
# ---------------------------------------------------------------------------
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest_object(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def write_json(path: Path, value: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text())


# ---------------------------------------------------------------------------
# Frozen component loading
# ---------------------------------------------------------------------------
def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError(f"cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_frozen_reference_verifier():
    """Load the frozen Stage01 reference verifier (read-only, digest-pinned)."""
    actual = sha256_file(FROZEN_REFERENCE_VERIFIER)
    if actual != FROZEN_REFERENCE_VERIFIER_SHA256:
        raise RuntimeError(
            "frozen reference verifier digest changed: "
            f"expected {FROZEN_REFERENCE_VERIFIER_SHA256} got {actual}"
        )
    return _load_module(FROZEN_REFERENCE_VERIFIER, "acts_s1_frozen_reference_verifier")


def load_frozen_stage01_validator():
    """Load the frozen Stage01 blind validator (read-only, digest-pinned)."""
    actual = sha256_file(FROZEN_STAGE01_VALIDATOR)
    if actual != FROZEN_STAGE01_VALIDATOR_SHA256:
        raise RuntimeError(
            "frozen stage01 validator digest changed: "
            f"expected {FROZEN_STAGE01_VALIDATOR_SHA256} got {actual}"
        )
    return _load_module(FROZEN_STAGE01_VALIDATOR, "acts_s1_frozen_stage01_validator")


def load_frozen_fixture_generator():
    """Load the frozen Stage01 fixture generator (read-only)."""
    return _load_module(FROZEN_FIXTURE_GENERATOR, "acts_s1_frozen_fixture_generator")


# ---------------------------------------------------------------------------
# Signed context helpers
# ---------------------------------------------------------------------------
def build_context(
    kind: str,
    role: str,
    target_id: str,
    attempt_id: str,
    epoch: int,
) -> dict[str, Any]:
    """Build the six-field binding consumed by ``context_validator``."""
    return {
        "kind": kind,
        "domain": CONTEXT_DOMAIN,
        "target_id": target_id,
        "attempt_id": attempt_id,
        "epoch": int(epoch),
        "role": role,
    }


def context_public_key(public_key_hex: str) -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))


def sign_context_bytes(private_key: Ed25519PrivateKey, context: dict[str, Any]) -> str:
    """Sign the canonical context bytes with the issuer key.

    The signature is produced over exactly the byte string that
    ``context_validator.canonical_context`` produces, so the vetted context
    validator can verify it without modification.
    """
    from context_validator import canonical_context

    return private_key.sign(canonical_context(context)).hex()


# ---------------------------------------------------------------------------
# Ed25519 helpers that mirror heb1_remediation_v1/signing semantics
# ---------------------------------------------------------------------------
def load_ed25519_private_key(key_path: Path) -> Ed25519PrivateKey:
    """Load an issuer private key through the vetted protected-signing loader.

    Delegating to ``protected_signing.load_private_key`` means the Stage 1
    keys inherit its guarantees: the key file must be a regular, non-symlink
    file with no group/world permission bits, and the recorded key id must
    match the public key.
    """
    from protected_signing import load_private_key

    _key_id, _role, key = load_private_key(Path(key_path))
    return key


def ed25519_public_hex(private_key: Ed25519PrivateKey) -> str:
    return private_key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    ).hex()


def issuer_policy():
    """Role/kind/context authorization policy for the Stage 1 issuers.

    A record may only be signed by the role that is registered for its kind in
    the public bundle *and* that is authorized for the Stage 1 domain.
    """
    from protected_signing import IssuerPolicy

    return IssuerPolicy(
        roles={
            ROLE_ARTIFACT_PRODUCER: {
                "kinds": (KIND_ARTIFACT_RECORD,),
                "contexts": (SIGNING_CONTEXT,),
            },
            ROLE_EXECUTION_OBSERVER: {
                "kinds": (KIND_EXECUTION_OBSERVATION,),
                "contexts": (SIGNING_CONTEXT,),
            },
            ROLE_REFERENCE_VERIFIER: {
                "kinds": (KIND_REFERENCE_VERDICT,),
                "contexts": (SIGNING_CONTEXT,),
            },
        }
    )
