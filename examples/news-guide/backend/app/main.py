"""FastAPI entrypoint wiring the ChatKit server and REST endpoints."""

from __future__ import annotations

from typing import Any

from chatkit.server import StreamingResult
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse
from starlette.responses import JSONResponse

from .server import NewsAssistantServer, create_chatkit_server

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
    context: dict[str, Any] = {"request": request}
    if article_id:
        context["article_id"] = article_id.strip()
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
