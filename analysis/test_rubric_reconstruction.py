"""The all-nine census must include F9, not replace it with environment."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import results_lock


class RubricReconstructionTests(unittest.TestCase):
    def check(self, reconstruction):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "sp2027/benchmarks/summary.csv"
            path.parent.mkdir(parents=True)
            row = {key: "yes" for key in [
                "clock", "oracle_independence", "failure_retention", "trace",
                "generated_artifacts", "environment", "weakness_attribution",
                "discovery_vs_execution", "query_accounting"]}
            row.update(benchmark="Synthetic", status="first_pass",
                       reconstruction_probe=reconstruction)
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(row))
                writer.writeheader()
                writer.writerow(row)
            with patch.object(results_lock, "ROOT", root):
                return results_lock.claim_e1_zero_satisfy(None)

    def test_missing_reconstruction_prevents_all_nine(self):
        report = self.check("no")
        self.assertTrue(report["ok"])
        self.assertEqual(report["value"]["Synthetic"], 8)

    def test_complete_reconstruction_changes_census(self):
        report = self.check("yes")
        self.assertFalse(report["ok"])
        self.assertEqual(report["value"]["Synthetic"], 9)


if __name__ == "__main__":
    unittest.main()
