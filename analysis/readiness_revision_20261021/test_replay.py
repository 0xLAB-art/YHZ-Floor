import json
import shutil
import tempfile
import unittest
from pathlib import Path

import replay


HERE = Path(__file__).resolve().parent
ROOT = HERE / "h1r3_replay_candidate_v2"


class ReplayEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = [json.loads(line) for line in (ROOT / "runs/confirmatory/results.jsonl").read_text().splitlines()]
        cls.row = next(row for row in rows if row["reference"]["verdict"] == "ACCEPTED" and row["kind"] == "primary")
        cls.reference = replay.load_module(ROOT / "code/h1r3_reference.py", "test_reference")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.case = self.root / "runs/confirmatory/sessions" / self.row["session_id"]
        shutil.copytree(ROOT / "runs/confirmatory/sessions" / self.row["session_id"], self.case)
        self.work = self.root / "work"
        self.work.mkdir()

    def result(self):
        return replay.adjudicate(self.root, self.row, self.reference, self.work)

    def test_relocated_original_is_accepted(self):
        self.assertEqual(self.result()["verdict"], "ACCEPTED")

    def test_wrong_output_is_rejected_despite_recorded_acceptance(self):
        (self.case / "candidate_output.json").write_text(json.dumps({"plaintext": "00"}))
        result = self.result()
        self.assertFalse(result["cryptographic_predicate"])
        self.assertEqual(result["verdict"], "REJECTED")

    def test_missing_output_is_rejected(self):
        (self.case / "candidate_output.json").unlink()
        self.assertEqual(self.result()["verdict"], "REJECTED")

    def test_modified_program_breaks_certificate_integrity(self):
        path = self.case / "candidate.py"
        path.write_bytes(path.read_bytes() + b"\n")
        result = self.result()
        self.assertTrue(result["cryptographic_predicate"])
        self.assertFalse(result["certificate_integrity"])
        self.assertEqual(result["verdict"], "REJECTED")

    def test_path_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            replay.relocate("runs/confirmatory/sessions/../../../outside", self.root)


if __name__ == "__main__":
    unittest.main()
