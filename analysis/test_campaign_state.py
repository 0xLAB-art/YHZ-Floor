#!/usr/bin/env python3
"""Regression tests for the terminal E2/W3 campaign guard."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "campaign_guard", ROOT / "sp2027" / "ops" / "campaign_guard.py")
guard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(guard)


class TestCampaignState(unittest.TestCase):
    def test_repository_state_is_terminal_and_non_authorizing(self):
        state = guard.load_state()
        self.assertEqual(state["status"], "failed_to_complete")
        self.assertEqual(state["completed_graded_sessions"], 33)
        self.assertEqual(state["scheduled_sessions"], 270)
        self.assertFalse(state["provider_calls_allowed"])
        self.assertFalse(state["continuation_artifacts_allowed"])

    def test_provider_calls_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError, "failed to complete"):
            guard.require_provider_authorized("test provider launch")

    def test_continuation_artifacts_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError, "audit-only non-result"):
            guard.require_continuation_authorized("test fill")

    def test_partial_r230_state_is_quota_terminal_and_non_authorizing(self):
        state_path = ROOT / "sp2027" / "ledger" / "CAMPAIGN_STATE_E2_R230.json"
        state = guard.load_state(state_path)
        self.assertEqual(state["campaign_id"], "E2-R230")
        self.assertEqual(state["status"], "halted_provider_quota")
        self.assertEqual(state["completed_graded_sessions"], 19)
        self.assertEqual(state["scheduled_sessions"], 230)
        self.assertFalse(state["provider_calls_allowed"])
        with self.assertRaisesRegex(RuntimeError, "E2-R230 state"):
            guard.require_provider_authorized(
                "E2-R230 resume", state_file=state_path)

    def test_r230_continuation_state_is_terminal_and_non_authorizing(self):
        state_path = (ROOT / "sp2027" / "ledger" /
                      "CAMPAIGN_STATE_E2_R230_CONTINUATION.json")
        state = guard.load_state(state_path)
        self.assertEqual(state["campaign_id"], "E2-R230-CONT-01")
        self.assertEqual(state["status"],
                         "halted_manual_after_provider_instability")
        self.assertEqual(state["completed_graded_sessions"], 35)
        self.assertEqual(state["scheduled_sessions"], 230)
        self.assertFalse(state["provider_calls_allowed"])
        self.assertFalse(state["continuation_artifacts_allowed"])
        with self.assertRaisesRegex(RuntimeError, "E2-R230-CONT-01 state"):
            guard.require_provider_authorized(
                "E2-R230 continuation", state_file=state_path)

    def test_malformed_state_is_rejected(self):
        original = guard.STATE
        with tempfile.TemporaryDirectory() as td:
            state_path = Path(td) / "CAMPAIGN_STATE.json"
            state_path.write_text(json.dumps({"status": "authorized"}))
            guard.STATE = state_path
            with self.assertRaisesRegex(RuntimeError, "missing"):
                guard.load_state()
        guard.STATE = original


if __name__ == "__main__":
    unittest.main()
