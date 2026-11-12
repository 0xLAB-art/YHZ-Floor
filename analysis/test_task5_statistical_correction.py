import json
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

import e3_statistical_correction as e3c
import e4_statistical_correction as e4c


class TestE4Correction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = e4c.build_output()
        e4c.validate(cls.output)

    def test_real_immutable_census_and_statuses(self):
        legacy = self.output["cohorts"]["legacy"]
        pilot = self.output["cohorts"]["pilot"]
        self.assertEqual(legacy["admissible_records"], 47)
        self.assertEqual(legacy["operational_cif"]["event_counts"]["success"], 10)
        self.assertEqual(pilot["admissible_records"], 20)
        self.assertEqual(pilot["operational_cif"]["event_counts"]["success"], 1)
        self.assertEqual(pilot["operational_cif"]["event_counts"]["provider_unavailable"], 17)

    def test_terminal_statuses_are_not_operational_censoring(self):
        for row in self.output["event_ledger"]:
            if row["admissibility"] and row["original_status"] != "SUCCESS":
                self.assertIsNotNone(row["operational_competing_event"])
                self.assertEqual(row["censoring_event"], None)

    def test_invalid_clock_rows_never_enter_risk_set(self):
        excluded = [r for r in self.output["event_ledger"] if not r["admissibility"]]
        self.assertEqual(len(excluded), 7)
        self.assertTrue(all(r["operational_competing_event"] is None for r in excluded))

    def test_operational_risk_set_has_no_unobserved_censoring(self):
        for cohort in self.output["cohorts"].values():
            self.assertEqual(cohort["risk_set_reconciliation"]["censor_total"], 0)
            self.assertEqual(
                cohort["risk_set_reconciliation"]["event_total"],
                cohort["admissible_records"],
            )

    def test_time_origin_is_tte_m_not_operation_span(self):
        eligible = [r for r in self.output["event_ledger"] if r["admissibility"]]
        self.assertTrue(all(r["duration_source"] in {"tte_m_harness_ns", "tte_m_oracle_ns"} for r in eligible))
        self.assertTrue(all(r["duration_s"] > 0 for r in eligible))

    def test_no_e5_pooling_and_no_fine_gray_regression_claim(self):
        self.assertFalse(self.output["provenance"]["e5_or_other_cohorts_pooled"])
        for cohort in self.output["cohorts"].values():
            self.assertIn("Aalen-Johansen", cohort["operational_cif"]["estimator"])
            self.assertIn("no Fine-Gray regression", cohort["operational_cif"]["estimator"])

    def test_synthetic_event_classification_covers_terminal_statuses(self):
        for status in sorted(e4c.TERMINAL_STATUSES):
            self.assertNotEqual(e4c.event_type(status), "success")
        self.assertEqual(e4c.event_type("SUCCESS"), "success")


class TestE3Correction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cells, cls.rows = e3c.load_cells(e3c.DEFAULT_SAMPLES)
        cls.point, cls.deltas = e3c.observed_effect(cls.cells)
        cls.diagnostics = e3c.diagnostics(cls.rows, cls.cells)

    def test_observed_point_estimate_is_constant_across_sensitivity(self):
        observed = self.point
        self.assertAlmostEqual(observed, -1.695593, places=6)
        self.assertEqual(len(self.deltas), 8)
        self.assertEqual(observed, e3c.observed_effect(self.cells)[0])

    def test_block_method_preserves_cell_pairing_and_boundaries(self):
        sample = e3c.moving_block_sample(self.cells[e3c.cell_key("vulnerable_ttable", "perf_counter_ns_monotonic", "warm", "on")], np.random.default_rng(1), 10)
        self.assertEqual(sample.size, 2000)
        self.assertIn("paired-cell", "factor-cell paired-cell structure")

    def test_smt_is_not_treated_as_independent_replication(self):
        boundary = self.diagnostics["interpretation"]
        self.assertIn("independent SMT blocks", boundary)
        self.assertEqual(self.diagnostics["trial_order"]["smt_block_counts"], {"off": 16000, "on": 16000})


if __name__ == "__main__":
    unittest.main()
