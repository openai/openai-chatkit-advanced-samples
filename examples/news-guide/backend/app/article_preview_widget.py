from typing import Literal

from chatkit.widgets import (
    Box,
    Col,
    Icon,
    Image,
    Justification,
    Row,
    Spacing,
    Text,
    Title,
    WidgetComponent,
    WidgetComponentBase,
)
from pydantic import Field

from .article_store import ArticleMetadata


# TODO: Add this to chatkit.widgets
class BasicRoot(WidgetComponentBase):
    type: Literal["Basic"] = Field(default="Basic", frozen=True)  # pyright: ignore
    direction: Literal["row", "col"] | None = None
    theme: Literal["light", "dark"] | None = None
    children: list[WidgetComponent] | None = None
    gap: int | str | None = None
    padding: float | str | Spacing | None = None
    align: Literal["start", "center", "end"] | None = None
    justify: Justification | None = None


def build_article_preview_widget(article: ArticleMetadata) -> BasicRoot:
    return BasicRoot(
        children=[
            Row(
                gap=3,
                padding=0,
                align="start",
                children=[
                    Box(
                        border={"color": "gray-900", "size": 1},
                        width=100,
                        children=[
                            Image(
                                src=article.heroImageUrl,
                                alt=article.title,
                                fit="cover",
                                position="top",
                                width=98,
                                height=98,
                                frame=True,
                            ),
                        ],
                    ),
                    Col(
                        gap=1,
                        children=[
                            Title(
                                value=article.title,
                                size="sm",
                            ),
                            Row(
                                gap=1,
                                children=[
                                    Text(
                                        value=f"by {article.author}",
                                        size="xs",
                                    ),
                                    Icon(name="dot", size="sm"),
                                    Text(
                                        value=f"{article.date.strftime('%b %d, %Y')}",
                                        size="xs",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
