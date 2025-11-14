"""
Defines a presentation widget that highlights a list of articles using the
same layout cues as the featured article card in the Newsroom panel.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from chatkit.widgets import Box, Col, Image, ListView, ListViewItem, Row, Text

from .article_store import ArticleMetadata

DEFAULT_TAG = "dispatch"


def _format_date(value: datetime) -> str:
    month = value.strftime("%b")
    return f"{month} {value.day}, {value.year}"


def _article_item(article: ArticleMetadata) -> ListViewItem:
    return ListViewItem(
        height=180,
        children=[
            Box(
                padding=0,
                variant="surface",
                border={"color": "gray-900", "size": 1},
                children=[
                    Row(
                        align="start",
                        gap=0,
                        children=[
                            Image(
                                src=article.heroImageUrl,
                                alt=article.title,
                                fit="cover",
                                position="top",
                                height=180,
                                width=160,
                                radius="none",
                                frame=True,
                            ),
                            Col(
                                padding={"x": 4, "y": 3},
                                gap=2,
                                children=[
                                    Text(
                                        value=_format_date(article.date),
                                        color="tertiary",
                                        size="xs",
                                    ),
                                    Text(
                                        value=article.title,
                                        size="md",
                                        weight="semibold",
                                        maxLines=4,
                                    ),
                                    Text(
                                        value=f"by {article.author}",
                                        color="tertiary",
                                        size="xs",
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            )
        ],
    )


def build_article_list_widget(articles: Iterable[ArticleMetadata]) -> ListView:
    """Render an article list widget using featured-card styling."""
    items: List[ListViewItem] = [_article_item(article) for article in articles]
    return ListView(children=items)
