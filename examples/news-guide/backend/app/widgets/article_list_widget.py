"""
Defines a presentation widget that highlights a list of articles using the
same layout cues as the featured article card in the Newsroom panel.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from chatkit.actions import ActionConfig
from chatkit.widgets import Box, Button, Col, Image, ListView, ListViewItem, Row, Text

from ..data.article_store import ArticleMetadata

DEFAULT_TAG = "dispatch"


def _format_date(value: datetime) -> str:
    month = value.strftime("%b")
    return f"{month} {value.day}, {value.year}"


def _article_item(article: ArticleMetadata) -> ListViewItem:
    return ListViewItem(
        children=[
            Box(
                maxWidth=450,
                minWidth=300,
                padding=0,
                border={"color": "gray-900", "size": 1},
                children=[
                    Row(
                        align="stretch",
                        gap=0,
                        children=[
                            Image(
                                src=article.heroImageUrl,
                                alt=article.title,
                                fit="cover",
                                position="top",
                                height=200,
                                width=160,
                                radius="none",
                                frame=True,
                            ),
                            Col(
                                padding={"x": 4, "y": 3},
                                gap=2,
                                flex=1,
                                align="stretch",
                                justify="between",
                                children=[
                                    Col(
                                        gap=2,
                                        flex=1,
                                        children=[
                                            Text(
                                                value=_format_date(article.date),
                                                color="tertiary",
                                                size="xs",
                                            ),
                                            Text(
                                                value=article.title,
                                                size="sm",
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
                                    Row(
                                        justify="end",
                                        children=[
                                            Button(
                                                label="View",
                                                size="sm",
                                                iconSize="sm",
                                                pill=True,
                                                variant="ghost",
                                                color="warning",
                                                iconEnd="chevron-right",
                                                onClickAction=ActionConfig(
                                                    type="open_article",
                                                    payload={"id": article.id},
                                                    handler="client",
                                                ),
                                            )
                                        ],
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
