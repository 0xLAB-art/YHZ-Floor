#!/usr/bin/env python3
"""Regression coverage for fail-closed campaign identity controls."""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "schema"))
from corpus_identity import record_identity, validate_index  # noqa: E402


def record(run_id="v2_O1__task__T1__rep1", status="SUCCESS"):
    return {"run_id": run_id, "session": {"status": status},
            "model_config": {"model_id": "model-a"},
            "task_card": {"task_id": "task", "starting_information": "T1"}}


class TestReconciliationInventory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.corpus = Path(self.tmp.name)
        self.rid = "v2_O1__task__T1__rep1"
        (self.corpus / "transcripts" / self.rid).mkdir(parents=True)
        (self.corpus / f"{self.rid}.json").write_text(json.dumps(record(self.rid)))
        self.row = {"run_id": self.rid, "status": "SUCCESS", "model": "model-a",
                    "task": "task", "track": "T1",
                    "transcript": str(self.corpus / "transcripts" / self.rid)}

    def tearDown(self):
        self.tmp.cleanup()

    def test_source_duplicate_stays_invalid(self):
        (self.corpus / "INDEX.jsonl").write_text(
            json.dumps(self.row) + "\n" + json.dumps(self.row) + "\n")
        self.assertTrue(any("duplicate run_id" in item
                            for item in validate_index(self.corpus)))

    def test_reconciliation_is_a_derived_inventory_not_a_repair(self):
        spec = importlib.util.spec_from_file_location(
            "reconcile_w3_manifest", HERE / "reconcile_w3_manifest.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        rows, report = module.reconciled_rows(self.corpus, [(1, self.row)])
        self.assertEqual(report["physical_record_count"], 1)
        self.assertEqual(rows[0]["reconciliation_state"],
                         "DERIVED_AUDIT_ONLY_NOT_ANALYSIS_ELIGIBLE")
        self.assertEqual(rows[0]["source_index_lines"], [1])

    def test_explicit_session_track_beats_card_starting_information(self):
        row = record(self.rid)
        row["task_card"]["track"] = "T3_blackbox"
        self.assertEqual(record_identity(row)["track"], "T3_blackbox")


class TestDriverReservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        driver_path = PROJECT_ROOT / "ACTS-ATTACK" / "harness" / "v2" / "run_agent_operations_v2.py"
        spec = importlib.util.spec_from_file_location("acts_campaign_driver", driver_path)
        cls.driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.driver)

    def test_reservation_and_index_append_refuse_duplicates(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            claim = self.driver.reserve_run_id(out, "r1")
            self.assertTrue(claim.exists())
            with self.assertRaises(RuntimeError):
                self.driver.reserve_run_id(out, "r1")
            row = {"run_id": "r1", "status": "SUCCESS"}
            self.driver.append_index_once(out / "INDEX.jsonl", row)
            with self.assertRaises(RuntimeError):
                self.driver.append_index_once(out / "INDEX.jsonl", row)

    def test_reservation_refuses_an_orphan_physical_record(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            (out / "r1.json").write_text("{}\n")
            with self.assertRaises(RuntimeError):
                self.driver.reserve_run_id(out, "r1")


if __name__ == "__main__":
    unittest.main()
