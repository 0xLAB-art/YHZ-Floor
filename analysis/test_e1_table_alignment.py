"""The printed audit table must not drift from its evidence worksheets."""
import unittest
from rebuild_e1_table import worksheet_values, printed_values, BENCHMARKS, WORKSHEET_ROWS


def fixture():
    return "\n".join(f"| {number} | field | **partial** | evidence |" for number in WORKSHEET_ROWS) + "\n- Outcome: `cannot_reconstruct(no run records)`"


class E1TableAlignmentTests(unittest.TestCase):
    def test_missing_reconstruction_not_partial(self):
        values = worksheet_values(fixture())
        self.assertEqual(values, ["partial"] * 8 + ["no"])

    def test_missing_field_fails_closed(self):
        with self.assertRaises(ValueError):
            worksheet_values(fixture().replace("| 1 | field | **partial** | evidence |", ""))

    def test_duplicate_field_rejected(self):
        with self.assertRaises(ValueError):
            worksheet_values(fixture() + "\n| 1 | field | **yes** | other |")

    def test_printed_footnotes_preserve_verdict(self):
        tex = r"\label{tab:audit}" + "\n" + "\n".join(
            name + r"~\cite{example} & " + " & ".join([r"\fpart$^{a}$"] * 9) + r" \\"
            for name in BENCHMARKS) + "\n" + r"\bottomrule"
        self.assertTrue(all(value == ["partial"] * 9 for value in printed_values(tex).values()))


if __name__ == "__main__":
    unittest.main()
