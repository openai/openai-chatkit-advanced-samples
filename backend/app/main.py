"""FastAPI entrypoint wiring the ChatKit server and REST endpoints."""

from __future__ import annotations

from typing import Any

from chatkit.server import StreamingResult
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse
from starlette.responses import JSONResponse

from .chat import (
    FactAssistantServer,
    create_chatkit_server,
)
from .facts import fact_store
from .non_streaming import buffer_streaming_response

app = FastAPI(title="ChatKit API")

_chatkit_server: FactAssistantServer | None = create_chatkit_server()


def get_chatkit_server() -> FactAssistantServer:
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
    request: Request, server: FactAssistantServer = Depends(get_chatkit_server)
) -> Response:
    payload = await request.body()
    result = await server.process(payload, {"request": request})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


@app.post("/chatkit/complete")
async def chatkit_complete_endpoint(
    request: Request, server: FactAssistantServer = Depends(get_chatkit_server)
) -> JSONResponse:
    """
    Non-streaming ChatKit endpoint for integrations like WhatsApp.

    This endpoint accepts the same ChatKit protocol messages as /chatkit,
    but returns a complete JSON response instead of streaming events.
    Suitable for platforms that don't support server-sent events.

    Returns:
        JSON response with:
        - text: The complete assistant message
        - thread_id: The thread identifier
        - message_id: The message identifier
        - error: Error message if any (optional)
    """
    payload = await request.body()
    result = await server.process(payload, {"request": request})

    # Handle streaming results by buffering them
    if isinstance(result, StreamingResult):
        complete_response = await buffer_streaming_response(result)
        return JSONResponse(complete_response.to_dict())

    # Handle non-streaming results (shouldn't happen for message operations)
    if hasattr(result, "json"):
        return JSONResponse({"raw_response": result.json})

    return JSONResponse(result)


@app.get("/facts")
async def list_facts() -> dict[str, Any]:
    facts = await fact_store.list_saved()
    return {"facts": [fact.as_dict() for fact in facts]}


@app.post("/facts/{fact_id}/save")
async def save_fact(fact_id: str) -> dict[str, Any]:
    fact = await fact_store.mark_saved(fact_id)
    if fact is None:
        raise HTTPException(status_code=404, detail="Fact not found")
    return {"fact": fact.as_dict()}


@app.post("/facts/{fact_id}/discard")
async def discard_fact(fact_id: str) -> dict[str, Any]:
    fact = await fact_store.discard(fact_id)
    if fact is None:
        raise HTTPException(status_code=404, detail="Fact not found")
    return {"fact": fact.as_dict()}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
