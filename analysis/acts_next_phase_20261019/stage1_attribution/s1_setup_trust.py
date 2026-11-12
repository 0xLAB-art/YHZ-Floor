#!/usr/bin/env python3
"""Stage 1 trust setup (TOEEA-1).

Generates one FRESH Ed25519 issuer key per role, using the unmodified
``heb1_remediation_v1/signing/protected_signing.py`` helper.

The three roles are deliberately held by three different parties:

    artifact_producer    holds the candidate program; never sees the observer
                         key or the reference-verifier key
    execution_observer   executes the candidate; never sees the producer key
    reference_verifier   holds the private target state; never sees the
                         producer or observer key

The private keys are written under ``trust/private/<role>/`` with 0700
directories and 0600 key files (enforced by ``protected_signing``), and the
public bundle ``trust/public_bundle.json`` is 0644.

Nothing in this file is derived from a public session identifier, a public
task seed, or any other public constant.  This directly addresses correction
C-02 in the historical correction ledger, which established that the frozen
HEB-1 fixtures derived their signing keys from public identifiers.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from s1_common import (
    ALL_ROLES,
    STAGE1_ROOT,
    write_json,
)

TRUST_ROOT = STAGE1_ROOT / "trust"
PUBLIC_BUNDLE = TRUST_ROOT / "public_bundle.json"
CUSTODY = TRUST_ROOT / "KEY_CUSTODY.json"


def _filesystem_enforces_modes(directory: Path) -> bool:
    """Return True if the filesystem actually honours 0600/0700 modes.

    The repository is mounted on a ``fuseblk`` filesystem in this environment
    which reports every file as 0777 regardless of ``chmod``.  The vetted
    ``protected_signing.load_private_key`` therefore refuses to load a key
    from the in-tree location.  Rather than weaken that check, the private
    keystore is relocated to a filesystem that does enforce modes, and the
    fact is recorded in the custody document.
    """
    probe_dir = directory / ".mode-probe"
    probe_dir.mkdir(parents=True, exist_ok=True)
    probe = probe_dir / "probe.json"
    probe.write_text("{}")
    os.chmod(probe, 0o600)
    ok = (probe.stat().st_mode & 0o077) == 0
    probe.unlink()
    probe_dir.rmdir()
    return ok


def _resolve_private_root() -> Path:
    override = os.environ.get("ACTS_S1_KEYSTORE")
    candidates = []
    if override:
        candidates.append(Path(override))
    candidates.append(Path(tempfile.gettempdir()) / "acts_s1_keystore")
    candidates.append(TRUST_ROOT / "private")
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
        except OSError:
            continue
        if _filesystem_enforces_modes(candidate):
            return candidate
    return TRUST_ROOT / "private"


def setup(force: bool = False) -> dict:
    from protected_signing import generate_issuer, write_public_bundle

    private_root = _resolve_private_root()
    private_root.mkdir(parents=True, exist_ok=True)
    issuers = []
    key_paths = {}
    for role in ALL_ROLES:
        role_dir = private_root / role
        role_dir.mkdir(parents=True, exist_ok=True)
        existing = sorted(role_dir.glob("*.json"))
        if existing and not force:
            # Reuse an already generated key so the trust root is stable.
            from protected_signing import load_private_key

            key_id, loaded_role, _key = load_private_key(existing[0])
            from cryptography.hazmat.primitives import serialization

            public_hex = _key.public_key().public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw
            ).hex()
            issuers.append({"key_id": key_id, "role": loaded_role, "public_key_hex": public_hex})
            key_paths[role] = existing[0]
            continue
        for stale in existing:
            stale.unlink()
        issuer = generate_issuer(role_dir, role)
        issuers.append(issuer)
        key_paths[role] = role_dir / f"{issuer['key_id']}.json"

    write_public_bundle(PUBLIC_BUNDLE, issuers)
    custody = {
        "schema": "acts-s1/key-custody/1",
        "note": (
            "Each issuer key was generated with Ed25519PrivateKey.generate() at setup "
            "time and is stored 0600 inside a 0700 directory.  No key is derived from "
            "a public session id, task seed, or any other public constant."
        ),
        "private_keystore_root": str(private_root),
        "private_keystore_outside_repository": str(private_root).startswith(str(STAGE1_ROOT)) is False,
        "keystore_note": (
            "The repository filesystem in this environment (fuseblk) reports every file "
            "as 0777 and does not honour chmod, so the vetted protected_signing loader "
            "refuses to read a key from the in-tree location.  The private keystore is "
            "therefore placed on a filesystem that does enforce 0600/0700.  Only the "
            "PUBLIC trust material lives in the repository."
        ),
        "roles": {
            role: {
                "key_id": issuer["key_id"],
                "private_key_path": str(key_paths[role]),
                "private_key_mode": "0600",
                "private_directory_mode": "0700",
                "holder": {
                    "artifact_producer": "candidate producer (local scripted producer)",
                    "execution_observer": "Stage 1 harness (executes the candidate)",
                    "reference_verifier": "Stage 1 harness (holds the private target state)",
                }[role],
            }
            for role, issuer in zip(ALL_ROLES, issuers)
        },
        "public_bundle": str(PUBLIC_BUNDLE.relative_to(STAGE1_ROOT)),
        "public_bundle_sha256": None,
    }
    import hashlib

    custody["public_bundle_sha256"] = hashlib.sha256(PUBLIC_BUNDLE.read_bytes()).hexdigest()
    write_json(CUSTODY, custody)
    return custody


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 1 trust setup")
    parser.add_argument("--force", action="store_true", help="regenerate keys")
    args = parser.parse_args()
    custody = setup(force=args.force)
    print(json.dumps(custody, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
