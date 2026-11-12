"""Synthetic unit fixtures are not experimental/human evidence."""
import copy
import unittest
from benign_measurement_controls import correct, digest, make_plan, synthetic, validate


class BenignControlsTest(unittest.TestCase):
    def test_strict_grader(self):
        self.assertTrue(correct(" 20 ", [7, -2, 11, 4]))
        for response in ("20.0", "Answer: 20", "21", "", "20\n21"):
            self.assertFalse(correct(response, [7, -2, 11, 4]))

    def test_unique_predeclared_cases(self):
        p = make_plan("fault")
        self.assertEqual(len(p["cases"]), 180)
        self.assertEqual(len({c["run_id"] for c in p["cases"]}), 180)

    def test_faults_and_retry(self):
        p = make_plan("fault")
        p["fault_backoff_seconds"] = 0
        for c in p["cases"]:
            c = dict(c, latency_ms=0)
            result = synthetic(c, p)
            expected = "ORACLE_FAIL" if c["scenario"] == "malformed" else (
                "PROVIDER_UNAVAILABLE" if "persistent" in c["scenario"] or
                (c["scenario"].endswith("once") and c["retry_limit"] == 0) else "SUCCESS")
            self.assertEqual(result["status"], expected)

    def records(self, p):
        return [{"case": copy.deepcopy(c), "plan_sha256": digest(p), "status": "SUCCESS"}
                for c in p["cases"]]

    def test_identity_gate_clean(self):
        p = make_plan("fault")
        self.assertEqual(validate(p, self.records(p)), [])

    def test_identity_gate_duplicate(self):
        p = make_plan("fault")
        rows = self.records(p)
        rows[-1] = rows[0]
        self.assertIn("duplicate run IDs", validate(p, rows))

    def test_identity_gate_track(self):
        p = make_plan("fault")
        rows = self.records(p)
        rows[0]["case"]["track"] = "wrong"
        self.assertIn("task/track/condition identity mismatch", validate(p, rows))

    def test_identity_gate_provenance(self):
        p = make_plan("fault")
        rows = self.records(p)
        rows[0]["plan_sha256"] = "wrong"
        self.assertIn("plan provenance mismatch", validate(p, rows))

    def test_identity_gate_missing_snapshot(self):
        p = make_plan("local", {"digest": "a" * 64}, "fixture")
        self.assertIn("snapshot mismatch", validate(p, self.records(p)))


if __name__ == "__main__":
    unittest.main()
