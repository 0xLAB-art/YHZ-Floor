#!/usr/bin/env python3
"""Regression tests for the W3 manifest-to-record identity gate."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import w3_fill  # noqa: E402


def record(run_id="r1", status="SUCCESS", model="model-a", task="task-a",
           track="T1"):
    return {
        "run_id": run_id,
        "session": {"status": status},
        "model_config": {"model_id": model},
        "task_card": {"task_id": task, "starting_information": track},
    }


class TestIndexIdentityGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.corpus = Path(self.tmp.name)
        self.transcript = self.corpus / "transcripts" / "r1"
        self.transcript.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def row(self, **overrides):
        row = {
            "run_id": "r1", "status": "SUCCESS", "model": "model-a",
            "task": "task-a", "track": "T1",
            "transcript": str(self.transcript),
        }
        row.update(overrides)
        return row

    def write(self, rows, rec=None):
        (self.corpus / "r1.json").write_text(json.dumps(rec or record()))
        (self.corpus / "INDEX.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n")

    def test_clean_index_is_accepted(self):
        self.write([self.row()])
        self.assertEqual(w3_fill.validate_index(self.corpus), [])

    def test_duplicate_id_is_a_hard_identity_defect(self):
        self.write([self.row(), self.row(status="ORACLE_FAIL")])
        issues = w3_fill.validate_index(self.corpus)
        self.assertTrue(any("duplicate run_id" in issue for issue in issues))
        self.assertTrue(any("manifest='ORACLE_FAIL'" in issue for issue in issues))

    def test_stale_manifest_field_is_rejected(self):
        self.write([self.row(model="model-b")])
        issues = w3_fill.validate_index(self.corpus)
        self.assertTrue(any("model manifest='model-b'" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
