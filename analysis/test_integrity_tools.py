"""Offline evidence tools must retain honest provenance and masked sources."""
import unittest

from build_human_reaudit_packet import neutral_sources
from experiment_integrity_audit import comparison_scope, filename_identity


class IntegrityToolsTests(unittest.TestCase):
    def test_tracks_parse_without_task_truncation(self):
        parsed = filename_identity("v2_O2__ecdsa_nonce_reuse__T1_known__rep3")
        self.assertEqual(parsed, {"slot": "O2", "task": "ecdsa_nonce_reuse",
                                  "track": "T1_known", "rep": 3})

    def test_invalid_identity_not_guessed(self):
        self.assertIsNone(filename_identity("old-run"))

    def test_masking_excludes_verdict_and_later_answers(self):
        sources = neutral_sources("Auditor: AI\n```\nhttps://example.org/repo\n"
                                  + "a" * 40 + "\nNONE FOUND; F1=no\n```\n"
                                  "Verdict yes https://example.org/answer")
        self.assertEqual(sources["urls"], ["https://example.org/repo"])
        self.assertEqual(sources["commit_hashes"], ["a" * 40])
        self.assertNotIn("no", str(sources))

    def test_missing_snapshot_rejected(self):
        with self.assertRaises(ValueError):
            neutral_sources("no source snapshot")

    def test_schema_pass_alone_cannot_support_comparisons(self):
        scope = comparison_scope([], ["track"], [], [], {}, [])
        self.assertFalse(scope["track_comparison_supported"])
        self.assertFalse(scope["frozen_backend_comparison_supported"])

    def test_mixed_provenance_and_missing_clock_block_backend(self):
        for clocks, mixed in (({"clock_missing": 1}, []), ({}, ["O1"])):
            scope = comparison_scope([], [], [], [], clocks, mixed)
            self.assertFalse(scope["frozen_backend_comparison_supported"])

    def test_clean_offline_screen_does_not_authorize_population_inference(self):
        scope = comparison_scope([], [], [], [], {}, [])
        self.assertTrue(scope["semantic_identity_screen_passed"])
        self.assertFalse(scope["campaign_population_estimates_authorized"])


if __name__ == "__main__":
    unittest.main()
