"""Offline author-search regressions using synthetic article metadata."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.data.article_store import ArticleStore


class AuthorSearchTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        (root / "articles").mkdir()
        entries = []
        for identity, author in (
            ("first", "例甲"),
            ("second", "示例乙"),
            ("third", "Example Author"),
        ):
            entries.append(
                {
                    "id": identity,
                    "title": f"Synthetic {identity}",
                    "heroImage": "fixture.png",
                    "heroImageUrl": "/fixture.png",
                    "url": f"/articles/{identity}",
                    "filename": f"{identity}.md",
                    "date": "2026-01-01T12:00:00Z",
                    "author": author,
                    "tags": [],
                    "keywords": [],
                }
            )
            (root / "articles" / f"{identity}.md").write_text(
                "Synthetic content.", encoding="utf-8"
            )
        (root / "articles.json").write_text(json.dumps(entries), encoding="utf-8")
        self.store = ArticleStore(root)

    def ids(self, query):
        return [entry["id"] for entry in self.store.search_metadata_by_author(query)]

    def test_distinct_names_without_ascii_slugs_do_not_match_each_other(self):
        for query, expected in (("例甲", ["first"]), ("示例乙", ["second"])):
            with self.subTest(query=query):
                self.assertEqual(self.ids(query), expected)

    def test_partial_unicode_names_still_match_the_actual_author_text(self):
        for query, expected in (("甲", ["first"]), ("乙", ["second"])):
            with self.subTest(query=query):
                self.assertEqual(self.ids(query), expected)

    def test_unrelated_empty_slug_queries_do_not_match_authors(self):
        for query in ("無関係", "!!!", "---"):
            with self.subTest(query=query):
                self.assertEqual(self.ids(query), [])

    def test_latin_names_and_nonempty_slug_aliases_still_work(self):
        for query in ("Example Author", "EXAMPLE AUTHOR", "example-author", "author"):
            with self.subTest(query=query):
                self.assertEqual(self.ids(query), ["third"])

    def test_empty_queries_keep_existing_empty_result(self):
        for query in ("", "   "):
            with self.subTest(query=query):
                self.assertEqual(self.ids(query), [])

    def test_shared_text_matches_keep_source_order(self):
        self.assertEqual(self.ids("例"), ["first", "second"])

    def test_author_text_is_preserved_in_results_and_stored_metadata(self):
        before = [entry.model_dump() for entry in self.store.list_metadata()]
        results = self.store.search_metadata_by_author("例甲")
        self.assertEqual(results[0]["author"], "例甲")
        self.assertEqual([entry.model_dump() for entry in self.store.list_metadata()], before)


if __name__ == "__main__":
    unittest.main()
