"""Canonical serialization, digests and interval helpers.

Every digest in the E2A contract is computed over *canonical* bytes so that
two independent components agree on the same value without exchanging a
serialization format.  The canonical form is the same one used by the audited
remediation component ``protected_signing`` (sorted keys, compact separators)
so that signed records and digests are computed over identical bytes.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

# Domain / scheme identifiers.  These are frozen constants, not tunables.
DOMAIN = "e2a:evidence:v1"
OBSERVATION_KIND = "execution_observation"
REFERENCE_KIND = "reference_adjudication"
CLAIM_KIND = "attribution_claim"

ROLE_OBSERVER = "execution_observer"
ROLE_REFERENCE = "reference_verifier"
ROLE_AGGREGATOR = "aggregator"

# The policy allow-list context string.  It is a *fixed namespace* string; the
# per-case six-field binding is carried inside the signed payload and is
# additionally signed by ``context_validator`` (see E2A_PREREGISTRATION 3.1).
POLICY_CONTEXT = DOMAIN

DECISION_SUCCESS = "ATTRIBUTED_SUCCESS"
DECISION_REJECT = "REJECT"
DECISION_INCONCLUSIVE = "INCONCLUSIVE"


def canonical_bytes(value: Any) -> bytes:
    """Return the canonical UTF-8 byte encoding used for every digest."""
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_object(value: Any) -> str:
    return sha_bytes(canonical_bytes(value))


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_canonical_json(path: Path, value: Any) -> str:
    """Write *value* as canonical JSON and return the sha256 of the bytes."""
    payload = canonical_bytes(value)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return sha_bytes(payload)


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    """Wilson score interval for a binomial proportion (95% by default).

    Returns ``(None, None)`` when ``total == 0`` so that an empty denominator
    is never silently reported as a zero rate.
    """
    if total <= 0:
        return (None, None)
    phat = successes / total
    denominator = 1.0 + (z * z) / total
    centre = phat + (z * z) / (2.0 * total)
    margin = z * math.sqrt((phat * (1.0 - phat) / total) + (z * z) / (4.0 * total * total))
    return (max(0.0, (centre - margin) / denominator), min(1.0, (centre + margin) / denominator))


def rate_block(successes: int, total: int) -> dict:
    """Report a rate with its Wilson interval and an explicit denominator."""
    low, high = wilson_interval(successes, total)
    return {
        "numerator": successes,
        "denominator": total,
        "rate": (successes / total) if total else None,
        "wilson_95_low": low,
        "wilson_95_high": high,
    }
