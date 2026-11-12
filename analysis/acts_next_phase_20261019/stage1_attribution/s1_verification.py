#!/usr/bin/env python3
"""Shared verification primitives for the Stage 1 evaluator family.

These helpers are deliberately factored out so that the full evaluator and
every baseline evaluator perform *exactly* the same bundle loading, file
integrity and record-verification steps.  The only thing that differs between
evaluators is which layers they switch on, which is what makes the ablation
ladder interpretable:

    E0  digest-only                 file digests only
    E1  + signed records            + Ed25519 record signatures, role/kind
                                    authorization
    E2  + signed context            + target/attempt/epoch/role context
                                    binding and the replay ledger
    E3  + causal joins              (the full evaluator) + cross-record
                                    causal joins between layers
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from context_validator import ContextValidationError, confine_bundle_path
from context_validator import validate_signed_context
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from protected_signing import verify_record

from s1_common import BUNDLE_SCHEMA, CONTEXT_DOMAIN, read_json, sha256_file


@dataclass
class BundleLoad:
    ok: bool = True
    bundle: dict[str, Any] = field(default_factory=dict)
    bundle_root: Path | None = None
    index: dict[str, dict[str, Any]] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def load_bundle(bundle_path: Path) -> BundleLoad:
    """Load and index a bundle.  Structural problems are classified here."""
    bundle_path = Path(bundle_path)
    root = bundle_path.parent
    out = BundleLoad(bundle_root=root)

    if not bundle_path.is_file():
        out.ok = False
        out.missing.append("bundle")
        out.reasons.append("bundle-unreadable")
        return out
    try:
        bundle = read_json(bundle_path)
    except (json.JSONDecodeError, OSError):
        out.ok = False
        out.missing.append("bundle")
        out.reasons.append("bundle-unparseable")
        return out
    if not isinstance(bundle, dict):
        out.ok = False
        out.missing.append("bundle")
        out.reasons.append("bundle-unparseable")
        return out
    if bundle.get("schema") != BUNDLE_SCHEMA:
        out.ok = False
        out.contradictions.append("bundle-schema")
        out.reasons.append("bundle-schema-mismatch")
        return out
    entries = bundle.get("entries")
    if not isinstance(entries, list):
        out.ok = False
        out.contradictions.append("bundle-entries")
        out.reasons.append("bundle-entries-malformed")
        return out

    out.bundle = bundle
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("kind"), str):
            out.ok = False
            out.contradictions.append("bundle-entry")
            out.reasons.append("bundle-entry-malformed")
            return out
        kind = entry["kind"]
        if kind in out.index:
            code = "duplicate-record-kind" if out.index[kind] == entry else "conflicting-record-kind"
            out.ok = False
            out.contradictions.append(code)
            out.reasons.append(code)
            return out
        out.index[kind] = entry
    return out


def check_files(bundle_root: Path, index: dict[str, dict[str, Any]]):
    """Check that every declared evidence file is present, safe and intact.

    Returns ``(digests, missing, contradictions, reasons)``.  A declared file
    that is absent is *missing* (INCONCLUSIVE); a file that is present but
    whose digest does not match the declaration, or that escapes the bundle
    root, is a *contradiction* (REJECT).
    """
    digests: dict[str, str] = {}
    missing: list[str] = []
    contradictions: list[str] = []
    reasons: list[str] = []
    for kind, entry in index.items():
        declared = entry.get("path")
        if not isinstance(declared, str) or not declared:
            contradictions.append(f"path-malformed:{kind}")
            reasons.append(f"path-malformed:{kind}")
            continue
        candidate = Path(bundle_root) / declared
        if not candidate.exists():
            missing.append(f"file:{kind}")
            reasons.append(f"missing-evidence-file:{kind}")
            continue
        try:
            confined = confine_bundle_path(Path(bundle_root), declared)
        except Exception:
            contradictions.append(f"path-escape:{kind}")
            reasons.append(f"path-escape:{kind}")
            continue
        actual = sha256_file(confined)
        digests[kind] = actual
        if actual != entry.get("sha256"):
            contradictions.append(f"digest-mismatch:{kind}")
            reasons.append(f"evidence-digest-mismatch:{kind}")
    return digests, missing, contradictions, reasons


def verify_signed_record(
    kind: str,
    record: dict[str, Any],
    *,
    trust_bundle_path: Path,
    policy,
    expected_context: dict[str, Any],
    expected_role: str,
    signing_context: str,
    bundle_root: Path,
    bundle_path: Path,
    replay_state=None,
):
    """Verify one signed evidence record.

    Returns ``(payload, problems)``.  ``payload`` is ``None`` when the record
    could not be verified.  ``problems`` are classified as
    ``("missing", code)`` or ``("contradiction", code)``.
    """
    problems: list[tuple[str, str]] = []
    try:
        payload = verify_record(record, trust_bundle_path, policy)
    except Exception as exc:
        return None, [("contradiction", f"record-verification-failed:{kind}:{type(exc).__name__}")]

    if record.get("kind") != kind:
        problems.append(("contradiction", f"record-kind-mismatch:{kind}"))
    if record.get("issuer_role") != expected_role:
        problems.append(("contradiction", f"record-role-mismatch:{kind}"))
    if record.get("context") != signing_context:
        problems.append(("contradiction", f"record-domain-mismatch:{kind}"))

    context = payload.get("context") if isinstance(payload, dict) else None
    context_sig = payload.get("context_signature_hex") if isinstance(payload, dict) else None
    if not isinstance(context, dict) or not isinstance(context_sig, str):
        problems.append(("contradiction", f"context-missing:{kind}"))
        return None, problems

    issuers = read_json(trust_bundle_path)["issuers"]
    issuer = next((i for i in issuers if i["key_id"] == record.get("key_id")), None)
    if issuer is None:
        problems.append(("contradiction", f"unknown-issuer:{kind}"))
        return None, problems

    public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(issuer["public_key_hex"]))
    try:
        # ``bundle_path`` is the *declared* (bundle-relative) path.  The vetted
        # context validator resolves it under ``bundle_root`` and rejects
        # absolute paths, so it must not be given an absolute one.
        validate_signed_context(
            context,
            bytes.fromhex(context_sig),
            public_key,
            expected_context,
            bundle_root=Path(bundle_root),
            bundle_path=str(bundle_path),
            replay_state=replay_state,
        )
    except ContextValidationError as exc:
        message = str(exc)
        if message.startswith("signed context binding mismatch:"):
            field_name = message.rsplit(":", 1)[-1].strip()
            problems.append(("contradiction", f"context-binding-mismatch:{kind}:{field_name}"))
        elif "replay limit exceeded" in message:
            problems.append(("contradiction", f"context-replay-exceeded:{kind}"))
        else:
            problems.append(("contradiction", f"context-invalid:{kind}"))
    except Exception as exc:
        problems.append(("contradiction", f"context-verification-failed:{kind}:{type(exc).__name__}"))
    return payload, problems


def expected_context_for(kind: str, expectation, role: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "domain": CONTEXT_DOMAIN,
        "target_id": expectation.target_id,
        "attempt_id": expectation.attempt_id,
        "epoch": int(expectation.epoch),
        "role": role,
    }
