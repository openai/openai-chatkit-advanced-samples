from typing import Any

from chatkit.widgets import BasicRoot, WidgetTemplate

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

article_preview_widget_template = WidgetTemplate.from_file("article_preview.widget")
author_preview_widget_template = WidgetTemplate.from_file("author_preview.widget")


def build_article_preview_widget(article: ArticleMetadata) -> BasicRoot:
    payload = {
        "id": article.id,
        "title": article.title,
        "author": article.author,
        "heroImageUrl": article.heroImageUrl,
        "date": article.date.strftime("%b %d, %Y"),
    }
    return article_preview_widget_template.build_basic(payload)


def _profile_for_author(author_slug: str) -> dict[str, str]:
    return AUTHOR_PROFILES.get(author_slug, DEFAULT_PROFILE)


def build_author_preview_widget(
    author_name: str,
    author_slug: str,
    article_count: int,
) -> BasicRoot:
    profile = _profile_for_author(author_slug)
    payload: dict[str, Any] = {
        "slug": author_slug,
        "name": author_name,
        "image": profile["image"],
        "bio": profile["bio"],
        "articleCount": article_count,
    }
    return author_preview_widget_template.build_basic(payload)
