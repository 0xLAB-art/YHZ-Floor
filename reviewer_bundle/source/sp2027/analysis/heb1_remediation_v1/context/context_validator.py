"""Small, standalone validation primitives for future signed bundles.

This module is deliberately not imported by the frozen V3-full verifier.  It
validates a context envelope before a future runner consumes bundle material:
paths are confined to the bundle, the signed context is compared field for
field with the expected run binding, and replay protection is supplied only
by an explicit mutable ledger.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature


CONTEXT_FIELDS = frozenset(
    {"kind", "domain", "target_id", "attempt_id", "epoch", "role"}
)


class ContextValidationError(ValueError):
    """Raised when a signed context or bundle path is not acceptable."""


def confine_bundle_path(bundle_root: Path, declared_path: str) -> Path:
    """Return a regular file under *bundle_root*, rejecting traversal/symlinks.

    Both the requested path and every existing component are checked.  The
    latter prevents a seemingly relative path from escaping through a
    symlinked directory.  A missing path is invalid because this helper is a
    pre-consumption check, not a path normalizer.
    """
    if not isinstance(declared_path, str) or not declared_path or "\x00" in declared_path:
        raise ContextValidationError("bundle path must be a non-empty string")
    relative = Path(declared_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ContextValidationError(f"bundle path is not confined: {declared_path!r}")

    root_input = Path(bundle_root)
    if root_input.is_symlink():
        raise ContextValidationError("bundle root must not be a symlink")
    try:
        root = root_input.resolve(strict=True)
    except OSError as exc:
        raise ContextValidationError("bundle root is missing") from exc
    candidate = root / relative
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ContextValidationError(f"bundle path contains symlink: {declared_path!r}")

    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ContextValidationError(f"bundle path is missing or escapes: {declared_path!r}") from exc
    if not resolved.is_file() or resolved.is_symlink():
        raise ContextValidationError(f"bundle path is not a regular file: {declared_path!r}")
    return resolved


def canonical_context(context: Mapping[str, Any]) -> bytes:
    """Serialize exactly the context object that a signer must authenticate."""
    return json.dumps(
        dict(context), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _context_key(context: Mapping[str, Any]) -> tuple[Any, ...]:
    return tuple(context[field] for field in sorted(CONTEXT_FIELDS))


def _check_binding_shape(context: Mapping[str, Any], expected: Mapping[str, Any]) -> None:
    if not isinstance(context, Mapping) or set(context) != CONTEXT_FIELDS:
        raise ContextValidationError("context must contain exactly the six binding fields")
    if not isinstance(expected, Mapping) or set(expected) != CONTEXT_FIELDS:
        raise ContextValidationError("expected binding must contain exactly the six fields")
    for field_name in CONTEXT_FIELDS:
        _check_field(field_name, context[field_name], "context")
        _check_field(field_name, expected[field_name], "expected binding")
        if context[field_name] != expected[field_name]:
            raise ContextValidationError(f"signed context binding mismatch: {field_name}")


def _check_field(field_name: str, field_value: Any, source: str) -> None:
    if field_name == "epoch":
        valid = isinstance(field_value, int) and not isinstance(field_value, bool) and field_value >= 0
        message = "epoch must be a non-negative integer"
    else:
        valid = isinstance(field_value, str) and bool(field_value)
        message = f"{field_name} must be a non-empty string"
    if not valid:
        raise ContextValidationError(f"{source}: {message}")


def _signature_bytes(signature: bytes | str) -> bytes:
    if isinstance(signature, bytes):
        return signature
    if not isinstance(signature, str):
        raise ContextValidationError("signature must be bytes or hexadecimal text")
    try:
        return bytes.fromhex(signature)
    except ValueError as exc:
        raise ContextValidationError("signature is not hexadecimal") from exc


def _verify_signature(public_key: Any, signature: bytes | str, context: Mapping[str, Any]) -> None:
    try:
        public_key.verify(_signature_bytes(signature), canonical_context(context))
    except (InvalidSignature, TypeError, ValueError) as exc:
        raise ContextValidationError("signed context verification failed") from exc


@dataclass
class ReplayState:
    """Explicit replay ledger; no wall-clock or stateless freshness claim."""

    max_uses: int = 1
    _uses: dict[tuple[Any, ...], int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.max_uses, bool) or not isinstance(self.max_uses, int) or self.max_uses < 1:
            raise ValueError("max_uses must be a positive integer")

    def record(self, context: Mapping[str, Any]) -> None:
        key = _context_key(context)
        uses = self._uses.get(key, 0)
        if uses >= self.max_uses:
            raise ContextValidationError("signed context replay limit exceeded")
        self._uses[key] = uses + 1

    def uses(self, context: Mapping[str, Any]) -> int:
        return self._uses.get(_context_key(context), 0)


@dataclass(frozen=True)
class ValidatedContext:
    context: dict[str, Any]
    bundle_path: Path | None


def validate_signed_context(
    context: Mapping[str, Any],
    signature: bytes | str,
    public_key: Any,
    expected: Mapping[str, Any],
    *,
    bundle_root: Path | None = None,
    bundle_path: str | None = None,
    replay_state: ReplayState | None = None,
) -> ValidatedContext:
    """Verify signature, exact run binding, optional confined path, then replay.

    ``public_key`` must expose ``verify(signature, canonical_context)`` (for
    example ``cryptography``'s Ed25519 public key).  The expected binding is
    exact: all six context fields are required and no additional fields are
    accepted.  Replay protection is absent unless the caller supplies the
    explicit ``ReplayState`` instance.
    """
    _check_binding_shape(context, expected)
    _verify_signature(public_key, signature, context)

    confined = None
    if bundle_path is not None:
        if bundle_root is None:
            raise ContextValidationError("bundle_root is required with bundle_path")
        confined = confine_bundle_path(bundle_root, bundle_path)
    if replay_state is not None:
        replay_state.record(context)
    return ValidatedContext(dict(context), confined)
