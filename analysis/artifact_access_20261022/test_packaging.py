import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from offline_checks import verify


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = self.root / "data.json"
        self.payload.write_bytes(b"retained-bytes\n")
        self.manifest = {"files": {"data.json": {"sha256": hashlib.sha256(self.payload.read_bytes()).hexdigest(),
                                                "bytes": self.payload.stat().st_size}}}
        self.write_manifest()

    def write_manifest(self):
        (self.root / "MANIFEST.json").write_text(json.dumps(self.manifest))

    def test_unchanged_payload(self):
        self.assertEqual(verify(self.root)["integrity"], "PASS")

    def test_tampered_payload(self):
        self.payload.write_bytes(b"changed-bytes\n")
        self.assertEqual(verify(self.root)["integrity"], "FAIL")

    def test_missing_payload(self):
        self.payload.unlink()
        self.assertEqual(verify(self.root)["integrity"], "FAIL")

    def test_unlisted_payload(self):
        (self.root / "unexpected.json").write_text("{}")
        self.assertEqual(verify(self.root)["integrity"], "FAIL")

    def test_unlisted_nested_manifest(self):
        (self.root / "extra").mkdir()
        (self.root / "extra/MANIFEST.json").write_text("{}")
        self.assertEqual(verify(self.root)["integrity"], "FAIL")

    def test_manifest_traversal(self):
        self.manifest["files"]["../outside.json"] = {"sha256": "0" * 64, "bytes": 0}
        self.write_manifest()
        self.assertTrue(any(e["error"] == "unsafe path" for e in verify(self.root)["errors"]))


if __name__ == "__main__":
    unittest.main()
