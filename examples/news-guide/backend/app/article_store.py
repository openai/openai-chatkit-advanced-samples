"""
Data models and store for News Guide demo articles.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

from pydantic import BaseModel, Field, ValidationError


class ArticleMetadata(BaseModel):
    """Describes a published article without the markdown body."""

    id: str
    title: str
    heroImage: str
    url: str
    filename: str
    date: datetime
    author: str
    tags: List[str] = Field(default_factory=list)


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

    def search_metadata_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Return ordered article metadata for records whose markdown content contains keyword.
        """
        if not keyword:
            return []

        needle = keyword.lower()
        matches: List[Dict[str, Any]] = []
        for article_id in self._order:
            record = self._articles[article_id]
            if needle not in record.content.lower():
                continue
            metadata = record.model_dump(exclude={"content"})
            metadata["date"] = record.date.isoformat()
            matches.append(metadata)
        return matches
