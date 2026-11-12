import unittest

from e3_wall_reporting import summarize


class E3WallReportingTests(unittest.TestCase):
    def test_zero_cpu_values_are_included_in_median(self):
        rows = [{"t_s": 1.0, "ru_utime_s": 0.0}, {"t_s": 2.0, "ru_utime_s": 2.0}, {"t_s": 3.0, "ru_utime_s": 0.0}]
        result = summarize(rows)
        self.assertEqual(result["user_cpu_descriptive"]["median_ms"], 0)
        self.assertEqual(result["user_cpu_descriptive"]["zero_samples"], 2)
        self.assertEqual(result["user_cpu_descriptive"]["median_fraction_of_paired_wall"], 0)
        self.assertEqual(result["wall_median_ms"], 2000)

    def test_cpu_fraction_preserves_corresponding_trial(self):
        result = summarize([{"t_s": 1.0, "ru_utime_s": 0.0}, {"t_s": 10.0, "ru_utime_s": 5.0}])
        self.assertEqual(result["user_cpu_descriptive"]["median_fraction_of_paired_wall"], 0.25)

    def test_wall_only_arm_has_no_cpu_summary(self):
        self.assertNotIn("user_cpu_descriptive", summarize([{"t_s": 0.1, "ru_utime_s": None}]))

    def test_partial_cpu_capture_is_rejected(self):
        with self.assertRaises(ValueError):
            summarize([{"t_s": 0.1, "ru_utime_s": None}, {"t_s": 0.2, "ru_utime_s": 0.0}])

    def test_invalid_wall_is_not_silently_filtered(self):
        for value in (0, -1, float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                summarize([{"t_s": value, "ru_utime_s": None}])

    def test_invalid_cpu_is_rejected(self):
        for value in (-1, float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                summarize([{"t_s": 0.1, "ru_utime_s": value}])


if __name__ == "__main__":
    unittest.main()
