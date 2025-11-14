"""
Data models and store for News Guide demo articles.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

from pydantic import BaseModel, Field, ValidationError

SEARCH_SYNONYMS: dict[str, list[str]] = {
    "small town": ["neighborhood", "community"],
    "small town drama": ["neighborhood drama", "community drama"],
    "town drama": ["neighborhood drama"],
    "drama": ["controversy", "debate", "feud", "saga", "gossip", "dispute"],
    "gossip": ["drama", "rumor"],
    "trending": ["popular", "top", "hot", "new", "fresh"],
}


class ArticleMetadata(BaseModel):
    """Describes a published article without the markdown body."""

    id: str
    title: str
    heroImage: str
    heroImageUrl: str
    url: str
    filename: str
    date: datetime
    author: str
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class ArticleRecord(ArticleMetadata):
    """Metadata plus markdown content."""

    content: str


class ArticleStore:
    """
    Loads article metadata and markdown bodies from disk.
    Intended for demo use only; a production system would connect to a database.
    """

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self._articles: Dict[str, ArticleRecord] = {}
        self._order: List[str] = []
        self.reload()

    @property
    def articles_path(self) -> Path:
        return self.data_dir / "articles"

    @property
    def metadata_path(self) -> Path:
        return self.data_dir / "articles.json"

    def reload(self) -> None:
        """Hydrate articles from metadata + markdown files."""
        metadata_entries = self._load_metadata()
        articles: Dict[str, ArticleRecord] = {}
        order: List[str] = []

        for entry in metadata_entries:
            markdown = self._load_markdown(entry)
            record = ArticleRecord(**entry.model_dump(), content=markdown)
            articles[record.id] = record
            order.append(record.id)

        self._articles = articles
        self._order = order

    def _load_metadata(self) -> Iterable[ArticleMetadata]:
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Missing article metadata file: {self.metadata_path}")

        with self.metadata_path.open("r", encoding="utf-8") as file:
            raw = json.load(file)

        if not isinstance(raw, list):
            raise ValueError("articles.json must contain a list of article entries.")

        for idx, entry in enumerate(raw):
            try:
                yield ArticleMetadata.model_validate(entry)
            except ValidationError as exc:
                raise ValueError(f"Invalid article metadata at index {idx}: {exc}") from exc

    def _load_markdown(self, metadata: ArticleMetadata) -> str:
        markdown_path = self.articles_path / metadata.filename
        if not markdown_path.exists():
            raise FileNotFoundError(
                f"Article markdown file '{metadata.filename}' not found in {self.articles_path}"
            )
        return markdown_path.read_text(encoding="utf-8")

    def list_metadata(self) -> List[Dict[str, Any]]:
        """Return metadata for all articles in list order."""
        payload: List[Dict[str, Any]] = []
        for article_id in self._order:
            record = self._articles[article_id]
            data = record.model_dump(exclude={"content"})
            data["date"] = record.date.isoformat()
            payload.append(data)
        return payload

    def list_metadata_for_tags(self, tags: List[str] | None = None) -> List[Dict[str, Any]]:
        """
        Return ordered metadata filtered to articles that share any of the requested tags.
        """
        if not tags:
            return self.list_metadata()

        normalized = {tag.lower() for tag in tags if tag}
        if not normalized:
            return self.list_metadata()

        payload: List[Dict[str, Any]] = []
        for article_id in self._order:
            record = self._articles[article_id]
            record_tags = {tag.lower() for tag in record.tags}
            if not record_tags.intersection(normalized):
                continue
            metadata = record.model_dump(exclude={"content"})
            metadata["date"] = record.date.isoformat()
            metadata["matchedTags"] = sorted(record_tags.intersection(normalized))
            payload.append(metadata)

        return payload

    def get_article(self, article_id: str) -> Dict[str, Any] | None:
        record = self._articles.get(article_id)
        if not record:
            return None
        payload = record.model_dump()
        payload["date"] = record.date.isoformat()
        return payload

    def get_metadata(self, article_id: str) -> Dict[str, Any] | None:
        record = self._articles.get(article_id)
        if not record:
            return None
        data = record.model_dump(exclude={"content"})
        data["date"] = record.date.isoformat()
        return data

    def tags_index(self) -> Dict[str, List[str]]:
        """Return a map of tag -> ordered article ids containing that tag."""
        tags: Dict[str, List[str]] = {}
        for article_id in self._order:
            record = self._articles[article_id]
            for tag in record.tags:
                tags.setdefault(tag.lower(), []).append(article_id)
        return {tag: ids for tag, ids in tags.items()}

    def article_metdata_list_for_tags(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Return a map of tag -> ordered article metadata entries containing that tag.
        """
        tagged_metadata: Dict[str, List[Dict[str, Any]]] = {}
        for article_id in self._order:
            record = self._articles[article_id]
            metadata = record.model_dump(exclude={"content"})
            metadata["date"] = record.date.isoformat()
            for tag in record.tags:
                tagged_metadata.setdefault(tag.lower(), []).append(metadata)
        return tagged_metadata

    def search_metadata_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Return ordered article metadata for records whose metadata fields contain any of the provided keywords.
        """
        sanitized = [keyword.strip().lower() for keyword in keywords if keyword and keyword.strip()]
        if not sanitized:
            return []

        phrases: List[str] = sanitized.copy()
        combined_phrase = " ".join(sanitized).strip()
        if combined_phrase and combined_phrase not in phrases:
            phrases.append(combined_phrase)

        expanded_terms: set[str] = set()
        tokens: List[str] = []
        multi_word_query = any(" " in phrase for phrase in phrases)
        for phrase in phrases:
            expanded_terms.update(self._expanded_search_terms(phrase))
            tokens.extend(token for token in re.split(r"[^a-z0-9]+", phrase) if token)

        token_count = len(tokens)
        matches: List[tuple[int, int, Dict[str, Any]]] = []

        for order_idx, article_id in enumerate(self._order):
            record = self._articles[article_id]
            metadata_fields = self._metadata_search_fields(record)
            base_hits = sum(
                1
                for phrase in phrases
                if phrase and any(phrase in field for field in metadata_fields)
            )
            term_hits = {
                term for term in expanded_terms if any(term in field for field in metadata_fields)
            }
            phrase_hits = {term for term in term_hits if " " in term}
            single_hits = term_hits - phrase_hits
            if not base_hits and not term_hits:
                continue
            if (
                (multi_word_query or token_count > 1)
                and not base_hits
                and not phrase_hits
                and len(single_hits) < 2
            ):
                continue

            score = base_hits * 100
            for term in term_hits:
                score += 5 if " " in term else 1

            metadata = record.model_dump(exclude={"content"})
            metadata["date"] = record.date.isoformat()
            matches.append((score, order_idx, metadata))

        matches.sort(key=lambda item: (-item[0], item[1]))
        return [metadata for _, _, metadata in matches]

    def search_metadata_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Backward-compatible wrapper for single keyword searches.
        """
        if not keyword:
            return []
        return self.search_metadata_by_keywords([keyword])

    def search_content_by_exact_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Return ordered article metadata for records whose markdown content contains text exactly.
        """
        trimmed = text.strip()
        if not trimmed:
            return []

        matches: List[Dict[str, Any]] = []
        for article_id in self._order:
            record = self._articles[article_id]
            if trimmed not in record.content:
                continue
            metadata = record.model_dump(exclude={"content"})
            metadata["date"] = record.date.isoformat()
            matches.append(metadata)
        return matches

    def _expanded_search_terms(self, keyword: str) -> List[str]:
        """
        Break multi-word queries into tokens and enrich them with lightweight synonyms.
        """
        normalized = keyword.strip().lower()
        if not normalized:
            return []

        tokens = [token for token in re.split(r"[^a-z0-9]+", normalized) if token]
        phrases: List[str] = []
        for start in range(len(tokens)):
            for end in range(start + 2, len(tokens) + 1):
                phrases.append(" ".join(tokens[start:end]))

        terms = set(tokens)
        if normalized:
            terms.add(normalized)
        terms.update(phrases)

        for term in list(terms):
            for variant in SEARCH_SYNONYMS.get(term, []):
                if variant:
                    terms.add(variant.lower())

        return [term for term in terms if term]

    def _metadata_search_fields(self, record: ArticleRecord) -> List[str]:
        """
        Collect lowercase metadata strings for simple keyword search.
        """
        fields: List[str] = [
            record.id,
            record.title,
            record.author,
            record.url,
            record.filename,
        ]
        fields.extend(record.tags)
        fields.extend(record.keywords)
        fields.append(record.date.isoformat())
        return [field.lower() for field in fields if field]

    def list_available_tags_and_keywords(self) -> Dict[str, List[str]]:
        """
        Return sorted unique tags and keywords present across all articles.
        """
        tags: set[str] = set()
        keywords: set[str] = set()
        for article_id in self._order:
            record = self._articles[article_id]
            tags.update(tag for tag in record.tags if tag)
            keywords.update(keyword for keyword in record.keywords if keyword)
        return {
            "tags": sorted(tags),
            "keywords": sorted(keywords),
        }
