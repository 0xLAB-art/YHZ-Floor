"""Synthetic fixtures only: no test data constitutes collected human evidence."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from grade_human_reaudit import agreement, digest, load_ratings, utc


class HumanReauditTests(unittest.TestCase):
    def fixture(self, directory, change=None):
        root = Path(directory)
        cells = ["synthetic::" + str(n) for n in range(54)]
        packet = root / "packet.json"
        packet.write_text(json.dumps({"n_cells": 54, "cells_order": cells}))
        rows = [{"cell_id": cell, "rating": "yes", "evidence_pointer": "synthetic fixture only",
                 "rationale": "not a human result", "judged_utc": "2026-01-01T00:00:00Z"}
                for cell in cells]
        if change:
            change(rows)
        ratings = root / "ratings.csv"
        with ratings.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        declaration = {"rater_kind": "human", "rater_id": "synthetic-test-only",
                       "independently_completed": True, "used_ai_for_judgments": False,
                       "prior_exposure": "synthetic fixture; not a real rater",
                       "ratings_sha256": digest(ratings), "packet_sha256": digest(packet),
                       "committed_utc": "2026-01-02T00:00:00Z"}
        return ratings, declaration, packet, cells

    def test_complete_bound_fixture_validates(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(len(load_ratings(*self.fixture(directory))), 54)

    def test_blank_rating_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                load_ratings(*self.fixture(directory, lambda rows: rows[0].update(rating="")))

    def test_duplicate_cell_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                load_ratings(*self.fixture(directory, lambda rows: rows[0].update(cell_id=rows[1]["cell_id"])))

    def test_ai_declaration_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            arguments = self.fixture(directory)
            arguments[1]["used_ai_for_judgments"] = True
            with self.assertRaises(ValueError):
                load_ratings(*arguments)

    def test_changed_rating_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            arguments = self.fixture(directory)
            arguments[1]["ratings_sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                load_ratings(*arguments)

    def test_commitment_before_judgment_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            arguments = self.fixture(directory)
            arguments[1]["committed_utc"] = "2025-12-31T00:00:00Z"
            with self.assertRaises(ValueError):
                load_ratings(*arguments)

    def test_non_utc_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            utc("2026-01-01T00:00:00")

    def test_kappa_known_balanced_case(self):
        stats = agreement(dict(zip("abcd", ["yes", "yes", "no", "no"])),
                          dict(zip("abcd", ["yes", "no", "yes", "no"])))
        self.assertEqual(stats["raw_agreement"], .5)
        self.assertEqual(stats["cohen_kappa"], 0)

    def test_constant_categories_do_not_manufacture_kappa(self):
        stats = agreement({"a": "yes"}, {"a": "yes"})
        self.assertTrue(stats["kappa_undefined"])
        self.assertIsNone(stats["cohen_kappa"])


if __name__ == "__main__":
    unittest.main()
