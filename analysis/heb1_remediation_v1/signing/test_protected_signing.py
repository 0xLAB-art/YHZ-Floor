#!/usr/bin/env python3
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from protected_signing import (
    IssuerPolicy, SignRequest, SigningError, generate_issuer, sign_record,
    verify_record, write_public_bundle,
)


POLICY = IssuerPolicy({
    "execution": {"kinds": ("execution_trace",), "contexts": ("attempt-a",)},
    "reference": {"kinds": ("reference_acceptance",), "contexts": ("attempt-a",)},
})


class ProtectedSigningTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.private = self.root / "private"
        self.public = self.root / "public-bundle.json"
        self.execution = generate_issuer(self.private, "execution")
        self.reference = generate_issuer(self.private, "reference")
        write_public_bundle(self.public, [self.execution, self.reference])

    def tearDown(self):
        self.tempdir.cleanup()

    def test_authorized_record_verifies_with_signed_context(self):
        record = sign_record(
            self.private / f"{self.execution['key_id']}.json",
            SignRequest("execution_trace", "attempt-a", {"candidate_sha256": "abc"}),
            POLICY,
        )
        self.assertEqual(verify_record(record, self.public, POLICY), {"candidate_sha256": "abc"})

    def test_unauthorized_role_is_rejected(self):
        with self.assertRaisesRegex(SigningError, "not authorized"):
            sign_record(
                self.private / f"{self.execution['key_id']}.json",
                SignRequest("reference_acceptance", "attempt-a", {}), POLICY,
            )

    def test_unauthorized_context_is_rejected(self):
        record = sign_record(
            self.private / f"{self.execution['key_id']}.json",
            SignRequest("execution_trace", "attempt-a", {}), POLICY,
        )
        record["context"] = "attempt-b"
        with self.assertRaisesRegex(SigningError, "not authorized|signature"):
            verify_record(record, self.public, POLICY)

    def test_public_bundle_has_no_private_key_material(self):
        public_text = self.public.read_text()
        self.assertNotIn("private_key_hex", public_text)
        self.assertNotIn("private", public_text.lower())
        self.assertEqual(self.public.stat().st_mode & 0o777, 0o644)
        for key_path in self.private.glob("*.json"):
            self.assertEqual(key_path.stat().st_mode & 0o777, 0o600)

    def test_private_directory_symlink_is_rejected(self):
        symlink = self.root / "private-link"
        symlink.symlink_to(self.private, target_is_directory=True)
        with self.assertRaisesRegex(SigningError, "must not be a symlink"):
            generate_issuer(symlink, "another")

    def test_private_key_symlink_is_rejected(self):
        real_key = self.private / f"{self.execution['key_id']}.json"
        link = self.root / "key-link.json"
        link.symlink_to(real_key)
        with self.assertRaisesRegex(SigningError, "regular non-symlink"):
            sign_record(link, SignRequest("execution_trace", "attempt-a", {}), POLICY)

    def test_altered_payload_and_signature_are_rejected(self):
        record = sign_record(
            self.private / f"{self.execution['key_id']}.json",
            SignRequest("execution_trace", "attempt-a", {"candidate_sha256": "abc"}),
            POLICY,
        )
        altered_payload = {**record, "payload": {"candidate_sha256": "changed"}}
        altered_signature = {**record, "signature_hex": "00" * 64}
        for altered in (altered_payload, altered_signature):
            with self.assertRaisesRegex(SigningError, "invalid record signature"):
                verify_record(altered, self.public, POLICY)

    def test_duplicate_issuer_ids_are_rejected(self):
        duplicate_bundle = self.root / "duplicate-bundle.json"
        duplicate_bundle.write_text(json.dumps({
            "format": "heb1-protected-signing-v1",
            "issuers": [self.execution, self.execution],
        }))
        record = sign_record(
            self.private / f"{self.execution['key_id']}.json",
            SignRequest("execution_trace", "attempt-a", {}), POLICY,
        )
        with self.assertRaisesRegex(SigningError, "duplicate key IDs"):
            verify_record(record, duplicate_bundle, POLICY)

    def test_inconsistent_public_key_id_is_rejected(self):
        inconsistent = dict(self.execution, public_key_hex="00" * 32)
        with self.assertRaisesRegex(SigningError, "does not match"):
            write_public_bundle(self.root / "bad-bundle.json", [inconsistent])

    def test_historical_fixture_key_is_publicly_derivable(self):
        session = "eb-sess-audit-public-key"
        private_bytes = hashlib.sha256(f"eb-iar-b|key|{session}".encode()).digest()
        old_fixture = Path(__file__).parents[2] / "experiment_b_20261019" / "eb_fixtures.py"
        source = old_fixture.read_text()
        self.assertIn("from_private_bytes", source)
        self.assertIn('f"eb-iar-b|key|{session}"', source)
        old_build = old_fixture.parent
        import sys
        sys.path.insert(0, str(old_build))
        try:
            import eb_fixtures
            expected = Ed25519PrivateKey.from_private_bytes(private_bytes).public_key()
            expected_hex = expected.public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw
            ).hex()
            self.assertEqual(eb_fixtures.pub_for(session), expected_hex)
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
