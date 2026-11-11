import hashlib
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from context_validator import (
    ContextValidationError,
    ReplayState,
    canonical_context,
    confine_bundle_path,
    validate_signed_context,
)


def context(**overrides):
    value = {
        "kind": "execution_trace",
        "domain": "heb1",
        "target_id": "target-a",
        "attempt_id": "attempt-1",
        "epoch": 3,
        "role": "executor",
    }
    value.update(overrides)
    return value


@pytest.fixture
def signed():
    key = Ed25519PrivateKey.generate()
    value = context()
    return value, key, key.sign(canonical_context(value))


def test_bundle_paths_reject_absolute_traversal_and_symlink(tmp_path: Path):
    root = tmp_path / "bundle"
    root.mkdir()
    (root / "ok.json").write_text("{}")
    outside = tmp_path / "outside.json"
    outside.write_text("outside")
    (root / "link.json").symlink_to(outside)
    linked_dir = tmp_path / "linked-dir"
    linked_dir.mkdir()
    (linked_dir / "nested.json").write_text("nested")
    (root / "link-dir").symlink_to(linked_dir, target_is_directory=True)

    assert confine_bundle_path(root, "ok.json") == root / "ok.json"
    for bad in (str(outside), "../outside.json", "link.json", "link-dir/nested.json"):
        with pytest.raises(ContextValidationError):
            confine_bundle_path(root, bad)

    root_alias = tmp_path / "bundle-alias"
    root_alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(ContextValidationError, match="root must not be a symlink"):
        confine_bundle_path(root_alias, "ok.json")


def test_exact_signed_context_binding_and_signature(signed):
    value, key, signature = signed
    expected = dict(value)
    result = validate_signed_context(value, signature.hex(), key.public_key(), expected)
    assert result.context == value

    for field in ("kind", "domain", "target_id", "attempt_id", "epoch", "role"):
        altered = dict(value)
        altered[field] = (altered[field] + "-other") if field != "epoch" else 4
        with pytest.raises(ContextValidationError):
            validate_signed_context(altered, signature, key.public_key(), expected)

    with pytest.raises(ContextValidationError):
        validate_signed_context({**value, "extra": "not signed"}, signature, key.public_key(), expected)

    with pytest.raises(ContextValidationError, match="expected binding.*epoch"):
        validate_signed_context(value, signature, key.public_key(), {**expected, "epoch": True})


def test_duplicate_context_is_rejected_by_explicit_replay_state(signed):
    value, key, signature = signed
    state = ReplayState(max_uses=1)
    validate_signed_context(value, signature, key.public_key(), value, replay_state=state)
    assert state.uses(value) == 1
    with pytest.raises(ContextValidationError, match="replay"):
        validate_signed_context(value, signature, key.public_key(), value, replay_state=state)


def test_stateless_validation_does_not_claim_freshness(signed):
    value, key, signature = signed
    validate_signed_context(value, signature, key.public_key(), value)
    validate_signed_context(value, signature, key.public_key(), value)


def test_replay_state_rejects_boolean_limit():
    with pytest.raises(ValueError, match="positive integer"):
        ReplayState(max_uses=True)


def test_context_can_bind_a_confined_bundle_path(tmp_path: Path, signed):
    value, key, signature = signed
    root = tmp_path / "bundle"
    root.mkdir()
    (root / "record.json").write_text(json.dumps(value))
    result = validate_signed_context(
        value, signature, key.public_key(), value,
        bundle_root=root, bundle_path="record.json",
    )
    assert result.bundle_path == root / "record.json"
