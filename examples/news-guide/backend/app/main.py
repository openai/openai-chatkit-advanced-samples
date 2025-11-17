"""FastAPI entrypoint wiring the ChatKit server and REST endpoints."""

from __future__ import annotations

from typing import Any

from chatkit.server import StreamingResult
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse
from starlette.responses import JSONResponse

from .data.article_store import ArticleMetadata
from .request_context import RequestContext
from .server import NewsAssistantServer, create_chatkit_server
from .widgets.preview_widgets import build_article_preview_widget, build_author_preview_widget

app = FastAPI(title="ChatKit API")

_chatkit_server: NewsAssistantServer | None = create_chatkit_server()


def get_chatkit_server() -> NewsAssistantServer:
    if _chatkit_server is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "ChatKit dependencies are missing. Install the ChatKit Python "
                "package to enable the conversational endpoint."
            ),
        )
    return _chatkit_server


@app.post("/chatkit")
async def chatkit_endpoint(
    request: Request, server: NewsAssistantServer = Depends(get_chatkit_server)
) -> Response:
    payload = await request.body()
    article_id = request.headers.get("article-id")
    context = RequestContext(request=request, article_id=article_id)
    result = await server.process(payload, context)
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


FEATURED_ARTICLE_IDS = [
    "unscheduled-parade-formation",
    "community-fridge-apple-pies",
    "missed-connection-reunion",
    "transit-pass-machine-updated",
]


@app.get("/articles/featured")
async def list_featured_articles(
    server: NewsAssistantServer = Depends(get_chatkit_server),
) -> dict[str, Any]:
    return {
        "articles": [
            server.article_store.get_metadata(article_id) for article_id in FEATURED_ARTICLE_IDS
        ]
    }


# Because this is a demo with a small number of articles and authors,
# we are returning all tags and authors in a single request to power
# entity tag search and preview requests within the client.
@app.get("/articles/tags")
async def list_article_tags(
    server: NewsAssistantServer = Depends(get_chatkit_server),
) -> dict[str, Any]:
    def _truncate_title(value: str, max_length: int = 30) -> str:
        if len(value) <= max_length:
            return value
        cutoff = max_length - 3
        if cutoff <= 0:
            return "..."[:max_length]
        return value[:cutoff].rstrip() + "..."

    def _build_article_tag(article: ArticleMetadata) -> dict[str, Any]:
        return {
            "entity": {
                "title": _truncate_title(article.title),
                "id": article.id,
                "icon": "document",
                "interactive": True,
                "group": "Articles",
                "data": {
                    "article_id": article.id,
                    "url": article.url,
                },
            },
            "preview": build_article_preview_widget(article).model_dump(),
        }

    def _build_author_tag(author: dict[str, Any]) -> dict[str, Any]:
        author_id = author["id"]
        author_name = author["name"]
        article_count = author.get("articleCount")
        data = {
            "author": author_name,
            "author_id": author_id,
            "type": "author",
        }
        return {
            "entity": {
                "title": author_name,
                "id": f"author:{author_id}",
                "icon": "profile-card",
                "interactive": True,
                "group": "Authors",
                "data": data,
            },
            "preview": build_author_preview_widget(
                author_name=author_name,
                author_slug=author_id,
                article_count=article_count,
            ).model_dump(),
        }

    articles = [_build_article_tag(entry) for entry in server.article_store.list_metadata()]
    authors = [_build_author_tag(entry) for entry in server.article_store.list_authors()]

    return {"tags": articles + authors}


@app.get("/articles/{article_id}")
async def read_article(
    article_id: str,
    server: NewsAssistantServer = Depends(get_chatkit_server),
) -> dict[str, Any]:
    article = server.article_store.get_article(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article '{article_id}' not found.",
        )
    return {"article": article}
