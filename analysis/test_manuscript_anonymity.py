"""Blinded references must not retain searchable identifiers."""
import unittest
from types import SimpleNamespace
from results_lock import claim_anonymity


class ManuscriptAnonymityTests(unittest.TestCase):
    def check(self, bibliography):
        return claim_anonymity(SimpleNamespace(
            norm="Anonymous submission double-blind " + bibliography))

    def test_blinded_doi_rejected(self):
        self.assertFalse(self.check(
            r"\bibitem{x} Anonymous, prior work, doi:10.1234/example. \end{thebibliography}")["ok"])

    def test_blinded_article_identifier_rejected(self):
        self.assertFalse(self.check(
            r"\bibitem{x} Anonymous, prior work, art. 123456. \end{thebibliography}")["ok"])

    def test_ordinary_third_person_doi_allowed(self):
        self.assertTrue(self.check(
            r"\bibitem{x} A. Researcher, prior work, doi:10.1234/example. \end{thebibliography}")["ok"])

    def test_blinded_reference_without_identifiers_allowed(self):
        self.assertTrue(self.check(
            r"\bibitem{x} Anonymous, prior work, 2027. \end{thebibliography}")["ok"])


if __name__ == "__main__":
    unittest.main()
