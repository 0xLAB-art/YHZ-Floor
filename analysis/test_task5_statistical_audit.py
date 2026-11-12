import unittest

from task5_statistical_audit import build_audit, validate


class Task5StatisticalAuditTests(unittest.TestCase):
    def test_task5_audit_validates_locked_claims_and_denominators(self):
        audit = build_audit()
        self.assertTrue(validate(audit))
        self.assertEqual(audit["number_lock_claims_audited"], 56)
        self.assertEqual(audit["e4_raw_reconstruction"]["pilot"]["success_numerator"], 1)
        self.assertEqual(audit["e4_raw_reconstruction"]["pilot"]["attack_denominator"], 3)
        self.assertEqual(audit["e4_raw_reconstruction"]["legacy"]["success_numerator"], 10)
        self.assertEqual(audit["e4_raw_reconstruction"]["legacy"]["attack_denominator"], 19)

    def test_task5_audit_keeps_incomplete_and_controlled_evidence_separate(self):
        audit = build_audit()
        self.assertFalse(audit["e2"]["primary_is_result"])
        self.assertFalse(audit["e2"]["pooling_with_pilot_or_e4"])
        self.assertFalse(audit["e5"]["historical_pooling"])
        self.assertEqual(audit["task4_control"]["cases"], 20)
        self.assertFalse(audit["task4_control"]["inferential_interval_supported"])

    def test_task5_audit_records_e3_block_sensitivity_boundary(self):
        audit = build_audit()
        e3 = audit["e3"]
        self.assertEqual(e3["trials_total"], 32000)
        self.assertEqual(e3["cells"], 16)
        self.assertEqual(e3["trials_per_cell"], [2000])
        self.assertEqual(e3["smt_block_counts"], {"off": 16000, "on": 16000})
        self.assertTrue(e3["moving_block_effects_all_negative"])
        self.assertIn("independent-host", e3["inference_boundary"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
