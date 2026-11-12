import unittest

from outcome_eligibility_v2 import classify, summarize


def row(status, drift=0, invalid=False):
    return {"run_id": "r", "session": {"status": status}, "task_card": {"task_id": "t"},
            "legacy": {"exclusion_reason": "harness_defect_session_invalid" if invalid else None},
            "clocks": {"dual_clock_max_drift_ns": drift}}


class OutcomeEligibilityTests(unittest.TestCase):
    def test_clock_disagreement_does_not_remove_a_graded_failure(self):
        result = classify(row("ORACLE_FAIL", 1_300_000_000))
        self.assertTrue(result["outcome_conditional_eligible"])
        self.assertTrue(result["outcome_operational_eligible"])
        self.assertFalse(result["historical_strict_conditional_eligible"])
        self.assertFalse(result["success"])

    def test_provider_interruption_only_enters_operational_population(self):
        result = classify(row("PROVIDER_UNAVAILABLE"))
        self.assertFalse(result["outcome_conditional_eligible"])
        self.assertTrue(result["outcome_operational_eligible"])

    def test_relay_invalid_is_excluded_for_record_validity_not_clock(self):
        result = classify(row("AGENT_GIVEUP", invalid=True))
        self.assertFalse(result["outcome_conditional_eligible"])
        self.assertFalse(result["outcome_operational_eligible"])

    def test_giveup_does_not_become_a_submitted_candidate_rejection(self):
        result = classify(row("AGENT_GIVEUP"))
        self.assertTrue(result["outcome_conditional_eligible"])
        self.assertFalse(result["candidate_rejection_observed"])

    def test_unknown_status_requires_review(self):
        with self.assertRaises(ValueError):
            classify(row("UNKNOWN"))

    def test_duplicate_identity_cannot_inflate_denominator(self):
        with self.assertRaises(ValueError):
            summarize([row("SUCCESS"), row("SUCCESS")])


if __name__ == "__main__":
    unittest.main()
