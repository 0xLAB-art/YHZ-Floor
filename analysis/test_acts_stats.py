"""Unit tests for acts_stats.py — every expected value is hand-computed and
written literally (no reimplementation of the formula inside the test).

Run:  cd sp2027/analysis && python3 -m unittest test_acts_stats -v
"""

import math
import unittest

import acts_stats as S


class TestWilson(unittest.TestCase):
    def test_known_value_1_of_1(self):
        # Standard Wilson score interval, x=1, n=1, z=1.96 -> [0.2065, 1]
        lo, hi = S.wilson(1, 1)
        self.assertAlmostEqual(lo, 0.2065, places=3)
        self.assertEqual(hi, 1.0)

    def test_known_value_0_of_10(self):
        # x=0, n=10 -> [0, 0.2775]
        lo, hi = S.wilson(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.2775, places=3)

    def test_symmetric_example_7_of_10(self):
        # x=7, n=10: centre=0.644494, half=0.247714
        # (matches R prop.test(7,10) to 4 dp: [0.3968, 0.8922])
        lo, hi = S.wilson(7, 10)
        self.assertAlmostEqual((lo + hi) / 2, 0.64449, places=4)
        self.assertAlmostEqual(hi - lo, 0.49543, places=4)
        self.assertAlmostEqual(lo, 0.39678, places=4)
        self.assertAlmostEqual(hi, 0.89221, places=4)

    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            S.wilson(3, 2)
        with self.assertRaises(ValueError):
            S.wilson(1, 0)


class TestASRCell(unittest.TestCase):
    def test_denominator_rule_excludes_provider_and_harness(self):
        statuses = ["SUCCESS", "ORACLE_FAIL", "PROVIDER_UNAVAILABLE",
                    "HARNESS_ERROR", "TIMEOUT"]
        cell = S.asr_cell(statuses)
        self.assertEqual(cell["num"], 1)
        self.assertEqual(cell["denom"], 3)          # 5 - 2 excluded
        self.assertEqual(cell["excluded_provider_or_harness"], 2)
        self.assertAlmostEqual(cell["asr"], 1 / 3)

    def test_ci_matches_direct_wilson(self):
        statuses = ["SUCCESS"] * 8 + ["ORACLE_FAIL"] * 2
        cell = S.asr_cell(statuses)
        lo, hi = S.wilson(8, 10)
        self.assertEqual(cell["ci"], (lo, hi))


class TestFSR(unittest.TestCase):
    def test_definition_and_interval(self):
        r = S.fsr(self_reported_successes=11, rejected_by_independent_oracle=7)
        self.assertAlmostEqual(r["fsr"], 7 / 11)
        lo, hi = S.wilson(7, 11)
        self.assertEqual(r["ci"], (lo, hi))

    def test_zero_denominator(self):
        r = S.fsr(0, 0)
        self.assertIsNone(r["fsr"])


class TestAOR(unittest.TestCase):
    def test_orders_of_magnitude(self):
        # 8.4 s vs 0.21 ms -> log10(40000) = 4.60206
        r = S.aor_log10([8.4], [0.00021])
        self.assertAlmostEqual(r["median_log10_aor"], math.log10(40000.0), places=6)

    def test_rejects_nonpositive(self):
        with self.assertRaises(ValueError):
            S.aor_log10([1.0], [0.0])


class TestDecompose(unittest.TestCase):
    def test_shares_sum_to_one_and_median(self):
        comp = {
            "model": [6.0, 3.0],
            "exec": [2.0, 1.0],
            "wait": [2.0, 6.0],
        }
        # shares: model=[0.6,0.3] exec=[0.2,0.1] wait=[0.2,0.6]
        # even-count median = mean of the two middle values
        d = S.decompose_tte_m(comp)
        self.assertAlmostEqual(d["model"]["median_share"], 0.45)
        self.assertAlmostEqual(d["exec"]["median_share"], 0.15)
        self.assertAlmostEqual(d["wait"]["median_share"], 0.4)


class TestKaplanMeier(unittest.TestCase):
    def test_tiny_classic_example(self):
        # Times 1,2,3,4; events T,T,F,T.
        # t=1: S=1-1/4=0.75 ; t=2: S=0.75*(1-1/3)=0.5 ; t=4: S=0.5*(1-1/1)=0
        km = S.kaplan_meier([1, 2, 3, 4], [True, True, False, True])
        self.assertEqual((km.n, km.events, km.censored), (4, 3, 1))
        self.assertAlmostEqual(km.times[0], 1.0)
        self.assertAlmostEqual(km.survival[0], 0.75)
        self.assertAlmostEqual(km.survival[1], 0.5)
        self.assertAlmostEqual(km.survival[-1], 0.0)
        self.assertEqual(km.median, 2.0)

    def test_all_censored_has_no_median(self):
        km = S.kaplan_meier([1, 2, 3], [False, False, False])
        self.assertEqual(km.events, 0)
        self.assertIsNone(km.median)
        self.assertEqual(km.times, [])

    def test_censoring_after_last_event_does_not_lower_survival(self):
        # Event at t=1 with n=3 at risk: S=1-1/3=2/3; censoring after never
        # lowers S, so the median is never reached.
        km = S.kaplan_meier([1, 2, 3], [True, False, False])
        self.assertIsNone(km.median)
        self.assertAlmostEqual(km.survival[-1], 2.0 / 3.0)

    def test_median_reached_when_events_dominate(self):
        # Events at t=1 (S=1-2/3=1/3) among 3 at risk -> median=1.0.
        km = S.kaplan_meier([1, 1, 2], [True, True, False])
        self.assertEqual(km.median, 1.0)
        self.assertAlmostEqual(km.survival[0], 1.0 / 3.0)


class TestRankFlip(unittest.TestCase):
    def test_identical_ranking(self):
        tau, conc, disc = S.rank_flip(["m1", "m2", "m3"], ["m1", "m2", "m3"])
        self.assertEqual((tau, conc, disc), (1.0, 3, 0))

    def test_full_reversal(self):
        tau, conc, disc = S.rank_flip(["m1", "m2", "m3"], ["m3", "m2", "m1"])
        self.assertEqual(tau, -1.0)
        self.assertEqual(disc, 3)


class TestFleiss(unittest.TestCase):
    def test_fleiss_1973_landis_koch_example(self):
        # Landis & Koch (1977) Fleiss example: 10 items, 14 raters, 5 categories.
        counts = [
            [0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6],
            [0, 3, 9, 2, 0], [2, 2, 8, 1, 1], [7, 7, 0, 0, 0],
            [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0],
            [0, 2, 2, 3, 7],
        ]
        ratings = [[c for c, k in enumerate(row) for _ in range(k)] for row in counts]
        kappa = S.fleiss_kappa(ratings)
        self.assertAlmostEqual(kappa, 0.210, places=3)

    def test_unanimous_is_one(self):
        ratings = [[0, 0], [1, 1], [2, 2], [0, 0]]
        self.assertEqual(S.fleiss_kappa(ratings), 1.0)

    def test_chance_agreement_is_exactly_zero(self):
        # Hand-verified: items [00],[11],[01],[10] with 2 raters.
        # P_i = 1,1,0,0 -> Pbar=0.5; votes p=[0.5,0.5] -> Pe=0.5; kappa=0.
        ratings = [[0, 0], [1, 1], [0, 1], [1, 0]]
        self.assertAlmostEqual(S.fleiss_kappa(ratings), 0.0, places=12)


if __name__ == "__main__":
    unittest.main()
