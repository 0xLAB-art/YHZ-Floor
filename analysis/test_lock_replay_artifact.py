"""Registered replay may not trust a claimed success count or omit checks."""
import importlib.util
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "paper/artifact_tools"
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location("portable_lock", TOOLS / "run_lock.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LockReplayTests(unittest.TestCase):
    def test_exact_successful_inventory(self):
        lock = {"verified_claims": [{"id": "a", "status": "OK"}]}
        self.assertEqual(module.check_replay(lock, ["a"]), 1)

    def test_missing_claim_rejected(self):
        with self.assertRaises(ValueError):
            module.check_replay({"verified_claims": []}, ["a"])

    def test_duplicate_claim_rejected(self):
        with self.assertRaises(ValueError):
            module.check_replay({"verified_claims": [
                {"id": "a", "status": "OK"}, {"id": "a", "status": "OK"}]}, ["a"])

    def test_failed_claim_rejected(self):
        with self.assertRaises(ValueError):
            module.check_replay({"verified_claims": [{"id": "a", "status": "FAIL"}]}, ["a"])


if __name__ == "__main__":
    unittest.main()
