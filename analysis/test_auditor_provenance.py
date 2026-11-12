"""Researcher conduct and AI diagnostic consistency remain distinct."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import results_lock


class AuditorProvenanceTests(unittest.TestCase):
    def report(self, text, one_human_label=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("cybench", "nyu_ctf_bench", "cve_bench", "incalmo",
                         "agentharm", "websp_eval"):
                worksheet = root / "sp2027/benchmarks" / name / "fields.md"
                worksheet.parent.mkdir(parents=True)
                label = "human" if one_human_label and name == "cybench" else "Buffy (AI, first pass)"
                worksheet.write_text("**Auditor:** " + label + "\n")
            clarification = root / "sp2027/paper/AUTHOR_AUDIT_CLARIFICATION.json"
            clarification.parent.mkdir(parents=True)
            clarification.write_text(json.dumps({
                "research_conduct": "researcher-conducted",
                "human_primary_rating_provenance_confirmed": False,
                "independently_verified": False, "historical_records_rewritten": False,
                "independent_human_inter_rater_validation_established": False}))
            with patch.object(results_lock, "ROOT", root):
                return results_lock.claim_e1_auditor_provenance(SimpleNamespace(norm=text))

    def test_distinct_research_and_tool_roles_pass(self):
        text = ("researcher-conducted experimental research; "
                "these labels describe tool provenance, not who conducted the research; "
                "The separate AI re-derivation is used only as a diagnostic consistency check; "
                "the primary E1 claims remain grounded in retained evidence pointers and pinned release artifacts")
        self.assertTrue(self.report(text)["ok"])

    def test_researcher_label_alone_does_not_establish_ratings(self):
        text = "researcher-conducted experimental research"
        self.assertFalse(self.report(text)["ok"])

    def test_changed_source_provenance_requires_review(self):
        text = ("researcher-conducted experimental research; "
                "these labels describe tool provenance, not who conducted the research; "
                "The separate AI re-derivation is used only as a diagnostic consistency check; "
                "the primary E1 claims remain grounded in retained evidence pointers and pinned release artifacts")
        self.assertFalse(self.report(text, one_human_label=True)["ok"])


if __name__ == "__main__":
    unittest.main()
