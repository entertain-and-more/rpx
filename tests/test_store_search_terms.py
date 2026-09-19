"""Guard the bilingual Microsoft Store search terms before submission."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TITLES = (
    "D&D",
    "Dungeons and Dragons",
    "DSA",
    "Das Schwarze Auge",
    "The Dark Eye",
)


class StoreSearchTermsTests(unittest.TestCase):
    def test_bilingual_search_terms_follow_store_submission_limits(self):
        lines = (ROOT / "STORE_LISTING.md").read_text(encoding="utf-8").splitlines()
        for heading in ("### Schlüsselwörter", "### Keywords"):
            with self.subTest(heading=heading):
                index = lines.index(heading)
                terms = [term.strip() for term in lines[index + 1].split(",")]
                self.assertEqual(len(terms), 7)
                self.assertEqual(len(set(terms)), 7)
                self.assertTrue(all(term and len(term) <= 30 for term in terms))
                for term in terms:
                    for title in FORBIDDEN_TITLES:
                        self.assertNotIn(title.casefold(), term.casefold())


if __name__ == "__main__":
    unittest.main()
