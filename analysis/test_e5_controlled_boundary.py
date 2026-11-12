import json
import importlib.util
import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e5_controlled_boundary import (  # noqa: E402
    EscrowAuthority,
    NAMESPACE,
    ProtectedGrader,
    TASK_ID,
    TrustedReference,
    request,
    run_controls,
)

ESCROW_PATH = Path(__file__).resolve().parents[2] / "ACTS-ATTACK/targets/e5/escrow.py"
SPEC = importlib.util.spec_from_file_location("e5_escrow_controller", ESCROW_PATH)
ESCROW_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ESCROW_MODULE)


class E5ControlledBoundaryTests(unittest.TestCase):
    def setUp(self):
        key = bytes.fromhex("00112233445566778899aabbccddeeff")
        other = bytes.fromhex("ffeeddccbbaa99887766554433221100")
        self.sessions = {
            "a": EscrowAuthority("a", key),
            "b": EscrowAuthority("b", other),
        }
        self.grader = ProtectedGrader(self.sessions)
        self.reference = TrustedReference(self.sessions)
        self.key = key

    def test_valid_candidate_is_independently_accepted(self):
        item = request("a", "one", self.key.hex())
        self.assertEqual(self.reference.expected("a", self.key.hex()), "ACCEPT")
        self.assertEqual(self.grader.submit(item)["verdict"], "ACCEPT")

    def test_invalid_and_malformed_candidates_are_rejected(self):
        for index, value in enumerate(("00", "not-hex", "")):
            with self.subTest(value=value):
                item = request("a", f"bad-{index}", value)
                self.assertEqual(self.grader.submit(item)["verdict"], "REJECT")

    def test_session_binding_and_replay_are_rejected(self):
        first = request("a", "same", self.key.hex())
        self.assertEqual(self.grader.submit(first)["verdict"], "ACCEPT")
        self.assertEqual(self.grader.submit(first)["reason"], "duplicate_request_id")
        cross = request("b", "cross", self.key.hex())
        self.assertEqual(self.grader.submit(cross)["verdict"], "REJECT")

    def test_agent_cannot_read_or_modify_grading_state(self):
        self.assertEqual(self.sessions["a"].agent_read()["verdict"], "DENY")
        self.assertEqual(self.sessions["a"].agent_write(b"x")["verdict"], "DENY")

    def test_control_run_has_no_false_acceptance(self):
        result = run_controls()
        self.assertTrue(result["summary"]["expected_observed_agreement"])
        self.assertEqual(result["summary"]["invalid_candidate_acceptances"], 0)
        self.assertEqual(result["network_or_provider_calls"], 0)
        self.assertFalse(result["historical_records_touched"])

    def test_output_is_secret_free_and_names_new_namespace(self):
        result = run_controls()
        blob = json.dumps(result)
        self.assertEqual(result["namespace"], "E5-CONTROLLED-2026-10")
        self.assertNotIn(self.key.hex(), blob)
        self.assertIn(NAMESPACE, blob)
        self.assertIn(TASK_ID, json.dumps(request("a", "x", "00")))

    def test_existing_escrow_refuses_early_reveal_and_verifies_after_submission(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "escrow.jsonl"
            escrow = ESCROW_MODULE.Escrow(log_path)
            key = bytes(escrow._key)
            early = escrow.reveal("agent")
            self.assertIn("error", early)
            self.assertFalse(any("key_hex" in line for line in log_path.read_text().splitlines()))
            wrong = escrow.verify("00" * 16, "agent")
            self.assertFalse(wrong["success"])
            right = escrow.verify(key.hex(), "grader")
            self.assertTrue(right["success"])
            revealed = escrow.reveal("auditor")
            self.assertEqual(revealed["key_hex"], key.hex())
            records = [json.loads(line) for line in log_path.read_text().splitlines()]
            verify_sequences = [record["seq"] for record in records if record["op"] == "verify"]
            reveal_record = next(record for record in records if record["op"] == "reveal")
            self.assertGreater(reveal_record["seq"], max(verify_sequences))


if __name__ == "__main__":
    unittest.main()
