#!/usr/bin/env python3
"""Standalone offline Ed25519 issuer and signed-record utility.

This is a versioned remediation artifact, not a replacement for the frozen
HEB-1 validators. Private key files are protected local state; public bundles
contain only trust metadata and public keys.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.exceptions import InvalidSignature

FORMAT = "heb1-protected-signing-v1"
DOMAIN = "heb1:evidence:v1"


class SigningError(ValueError):
    """Raised when a record or issuer authorization is invalid."""


@dataclass(frozen=True)
class SignRequest:
    kind: str
    context: str
    payload: dict


@dataclass(frozen=True)
class IssuerPolicy:
    roles: dict[str, dict[str, tuple[str, ...]]]

    def permits(self, role: str, kind: str, context: str) -> bool:
        authorization = self.roles.get(role)
        return bool(authorization and kind in authorization["kinds"] and
                    context in authorization["contexts"])


def _canonical(record: dict) -> bytes:
    return (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _public_bytes(key: Ed25519PrivateKey) -> bytes:
    return key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )


def _key_id(public_bytes: bytes) -> str:
    return "ed25519-" + hashlib.sha256(public_bytes).hexdigest()[:24]


def _secure_directory(directory: Path) -> None:
    if directory.is_symlink():
        raise SigningError("private key directory must not be a symlink")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not directory.is_dir() or directory.is_symlink():
        raise SigningError("private key directory is not a trusted directory")
    os.chmod(directory, 0o700)


def generate_issuer(private_directory: Path, role: str) -> dict[str, str]:
    """Generate one random issuer key and return public trust metadata."""
    if not role or "/" in role or "\\" in role:
        raise SigningError("role must be a non-empty path-safe identifier")
    _secure_directory(private_directory)
    key = Ed25519PrivateKey.generate()
    public_bytes = _public_bytes(key)
    key_id = _key_id(public_bytes)
    key_path = private_directory / f"{key_id}.json"
    private_record = {"format": FORMAT, "key_id": key_id, "role": role,
                      "private_key_hex": key.private_bytes(
                          serialization.Encoding.Raw,
                          serialization.PrivateFormat.Raw,
                          serialization.NoEncryption(),
                      ).hex()}
    key_bytes = _canonical(private_record)
    try:
        descriptor = os.open(
            key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
        )
        with os.fdopen(descriptor, "wb") as key_file:
            key_file.write(key_bytes)
    except FileExistsError as exc:
        raise SigningError("issuer key path already exists") from exc
    return {"key_id": key_id, "role": role, "public_key_hex": public_bytes.hex()}


def load_private_key(key_path: Path) -> tuple[str, str, Ed25519PrivateKey]:
    """Load protected key state; reject group/world-readable key files."""
    key_stat = key_path.lstat()
    if stat.S_ISLNK(key_stat.st_mode) or not stat.S_ISREG(key_stat.st_mode):
        raise SigningError("private key path must be a regular non-symlink file")
    if key_stat.st_mode & 0o077:
        raise SigningError("private key permissions must be 0600 or stricter")
    record = json.loads(key_path.read_text())
    private_bytes = bytes.fromhex(record["private_key_hex"])
    key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    if _key_id(_public_bytes(key)) != record["key_id"]:
        raise SigningError("private key identity mismatch")
    return record["key_id"], record["role"], key


def write_public_bundle(bundle_path: Path, issuers: list[dict[str, str]]) -> None:
    """Write trust metadata without accepting or emitting private key fields."""
    public_issuers = []
    seen_key_ids = set()
    for issuer in issuers:
        if set(issuer) != {"key_id", "role", "public_key_hex"}:
            raise SigningError("public issuer metadata contains unexpected fields")
        if issuer["key_id"] in seen_key_ids:
            raise SigningError("public issuer metadata contains duplicate key IDs")
        _validate_issuer_metadata(issuer)
        seen_key_ids.add(issuer["key_id"])
        public_issuers.append(dict(issuer))
    bundle_path.write_text(
        _canonical({"format": FORMAT, "issuers": public_issuers}).decode()
    )
    os.chmod(bundle_path, 0o644)


def sign_record(key_path: Path, request: SignRequest, policy: IssuerPolicy) -> dict:
    """Sign a domain-separated record only under an authorized role/context."""
    key_id, role, private_key = load_private_key(key_path)
    if not policy.permits(role, request.kind, request.context):
        raise SigningError("issuer role is not authorized for kind/context")
    unsigned = {"format": FORMAT, "domain": DOMAIN, "kind": request.kind,
                "context": request.context, "issuer_role": role,
                "key_id": key_id, "payload": request.payload}
    return {**unsigned, "signature_hex": private_key.sign(_canonical(unsigned)).hex()}


def verify_record(record: dict, bundle_path: Path, policy: IssuerPolicy) -> dict:
    """Verify trust, role authorization, signed domain/kind/context, and payload."""
    bundle = json.loads(bundle_path.read_text())
    if bundle.get("format") != FORMAT or not isinstance(bundle.get("issuers"), list):
        raise SigningError("public bundle format mismatch")
    issuer_by_id = _issuer_index(bundle["issuers"])
    required = {"format", "domain", "kind", "context", "issuer_role", "key_id",
                "payload", "signature_hex"}
    if set(record) != required or record["format"] != FORMAT or record["domain"] != DOMAIN:
        raise SigningError("record format or signed domain mismatch")
    issuer = issuer_by_id.get(record["key_id"])
    if not issuer or issuer["role"] != record["issuer_role"]:
        raise SigningError("unknown issuer or role mismatch")
    if not policy.permits(record["issuer_role"], record["kind"], record["context"]):
        raise SigningError("issuer role is not authorized for kind/context")
    unsigned = {key: record[key] for key in required if key != "signature_hex"}
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(issuer["public_key_hex"])).verify(
            bytes.fromhex(record["signature_hex"]), _canonical(unsigned)
        )
    except (InvalidSignature, ValueError, KeyError) as exc:
        raise SigningError("invalid record signature") from exc
    return record["payload"]


def _validate_issuer_metadata(issuer: dict[str, str]) -> None:
    if not issuer["role"] or "/" in issuer["role"] or "\\" in issuer["role"]:
        raise SigningError("issuer role is invalid")
    try:
        public_bytes = bytes.fromhex(issuer["public_key_hex"])
    except ValueError as exc:
        raise SigningError("issuer public key is not hexadecimal") from exc
    if len(public_bytes) != 32 or _key_id(public_bytes) != issuer["key_id"]:
        raise SigningError("issuer key ID does not match public key")


def _issuer_index(issuers: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    index = {}
    for issuer in issuers:
        if not isinstance(issuer, dict) or set(issuer) != {"key_id", "role", "public_key_hex"}:
            raise SigningError("malformed public issuer metadata")
        _validate_issuer_metadata(issuer)
        key_id = issuer["key_id"]
        if key_id in index:
            raise SigningError("public bundle contains duplicate key IDs")
        index[key_id] = issuer
    return index
