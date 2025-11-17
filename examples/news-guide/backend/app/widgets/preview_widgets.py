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

from ..data.article_store import ArticleMetadata

AUTHOR_PROFILES: dict[str, dict[str, str]] = {
    "elowen-wilder": {
        "image": "https://i.imgur.com/ICeIhSc.png",
        "bio": "Local Features Editor who chases neighborly mysteries and parks department quirks.",
    },
    "marlow-keene": {
        "image": "https://i.imgur.com/xPC3ho0.png",
        "bio": "Community reporter spotlighting food stories, mutual aid, and small joys.",
    },
    "joan-li": {
        "image": "https://i.imgur.com/HrcN2Nx.png",
        "bio": "Human-interest writer covering serendipity, bulletin boards, and chance reunions.",
    },
    "todd-harris": {
        "image": "https://i.imgur.com/PVBBLF4.png",
        "bio": "Transit and traffic correspondent obsessed with slow buses and route lore.",
    },
    "maggie-wang": {
        "image": "https://i.imgur.com/XihDCd6.png",
        "bio": "City hall watcher translating policy updates into friendly neighborhood takeaways.",
    },
    "charley-oh": {
        "image": "https://i.imgur.com/GmYrNIV.png",
        "bio": "Education and parks beat writer with a soft spot for musical crosswalks.",
    },
    "sean-mcconnell": {
        "image": "https://i.imgur.com/eobRJpx.png",
        "bio": "Events scout cataloging pop-ups, parades, and unexpected happenings.",
    },
    "member-of-technical-staff": {
        "image": "https://i.imgur.com/yBy8LAB.png",
        "bio": "Staff engineer moonlighting as a newsroom copy editor and systems tinkerer.",
    },
}

DEFAULT_PROFILE = {
    "image": "https://i.imgur.com/eobRJpx.png",
    "bio": "Foxhollow Dispatch contributor.",
}


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


def _profile_for_author(author_slug: str) -> dict[str, str]:
    return AUTHOR_PROFILES.get(author_slug, DEFAULT_PROFILE)


def build_author_preview_widget(
    author_name: str,
    author_slug: str,
    article_count: int | None = None,
) -> BasicRoot:
    profile = _profile_for_author(author_slug)
    article_label = (
        f"{article_count} article{'s' if article_count != 1 else ''} in the archive"
        if article_count is not None
        else None
    )

    texts = [
        Text(value=profile["bio"], size="sm"),
    ]
    if article_label:
        texts.append(Text(value=article_label, size="xs"))

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
                                src=profile["image"],
                                alt=f"Profile for {author_name}",
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
                            Title(value=author_name, size="sm"),
                            *texts,
                        ],
                    ),
                ],
            ),
        ],
    )
