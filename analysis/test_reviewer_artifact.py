"""Regression tests for honest, fail-closed reviewer artifact checks."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "reviewer_verify", ROOT / "sp2027/paper/artifact_tools/verify.py")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class ReviewerArtifactTests(unittest.TestCase):
    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                verify.within(Path(directory), "../outside")

    def test_tamper_and_unlisted_files_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "payload.txt").write_text("original")
            manifest = {"files": [{"path": "payload.txt",
                                   "sha256": verify.digest(root / "payload.txt")} ]}
            (root / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest))
            self.assertEqual(verify.verify(root), [])
            (root / "payload.txt").write_text("tampered")
            self.assertTrue(verify.verify(root))
            (root / "unlisted.txt").write_text("extra")
            self.assertTrue(any("unlisted" in x for x in verify.verify(root)))

    def test_missing_generator_cannot_certify_full_reconstruction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            analysis = root / "sp2027/analysis"
            analysis.mkdir(parents=True)
            lock = {"generator": "sp2027/analysis/results_lock.py",
                    "verified_claims": [{"id": "example", "artifacts": [
                        {"path": "absent.json", "kind": "file", "sha256": "0" * 64}]}]}
            (analysis / "RESULTS_LOCK.json").write_text(json.dumps(lock))
            report = verify.coverage(root)
            self.assertFalse(report["full_reconstruction_demonstrated"])
            self.assertFalse(report["lock_generator_present"])
            self.assertEqual(report["missing_file_dependencies"], ["absent.json"])

    def test_duplicate_manifest_entry_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "payload.txt").write_text("original")
            entry = {"path": "payload.txt", "sha256": verify.digest(root / "payload.txt")}
            (root / "PACKAGE_MANIFEST.json").write_text(json.dumps({"files": [entry, entry]}))
            self.assertTrue(any("duplicate" in x for x in verify.verify(root)))


if __name__ == "__main__":
    unittest.main()
