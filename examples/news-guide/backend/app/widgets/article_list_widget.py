"""
Defines a presentation widget that highlights a list of articles using the
same layout cues as the featured article card in the Newsroom panel.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from chatkit.widgets import WidgetRoot

from ..data.article_store import ArticleMetadata
from .widget_template import WidgetTemplate


def _format_date(value: datetime) -> str:
    month = value.strftime("%b")
    return f"{month} {value.day}, {value.year}"


article_list_widget_template = WidgetTemplate.from_file("article_list.widget")


def build_article_list_widget(articles: list[ArticleMetadata]) -> WidgetRoot:
    """Render an article list widget using the .widget template."""
    payload = {"articles": [_serialize_article(article) for article in articles]}
    return article_list_widget_template.build(payload)


def _serialize_article(article: ArticleMetadata) -> dict[str, Any]:
    return {
        "id": article.id,
        "title": article.title,
        "author": article.author,
        "heroImageUrl": article.heroImageUrl,
        "date": _format_date(article.date),
    }
