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
# backend/app/main.py  (dosyanın SONUNA ekleyin; varsa eski denemeleri kaldırın)
import os, httpx
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WORKFLOW_ID    = os.environ["WORKFLOW_ID"]

OPENAI_SESSIONS_URL = "https://api.openai.com/v1/chatkit/sessions"
HEADERS = {"Authorization": f"Bearer {OPENAI_API_KEY}",
           "Content-Type": "application/json"}

@router.post("/chatkit/start")
async def chatkit_start():
    payload = {
        "user": "web-user-1",                 # kullanıcıyı istediğin gibi tanımla
        "workflow": { "id": WORKFLOW_ID },    # Agent Builder > Workflow ID
        # Örnek: daha uzun süre istersen
        # "expires_after": { "seconds": 3600 }
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OPENAI_SESSIONS_URL, headers=HEADERS, json=payload)
    data = resp.json()
    return JSONResponse(
      {"client_secret": data.get("client_secret"),
       "expires_at":   data.get("expires_at")},
      status_code=resp.status_code
    )

@router.post("/chatkit/refresh")
async def chatkit_refresh(body: dict = Body(...)):
    current = body.get("currentClientSecret")
    # Çoğu kurulumda aynı endpoint ile refresh yapılır:
    payload = {
        "user": "web-user-1",
        "workflow": { "id": WORKFLOW_ID },
        "current_client_secret": current
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OPENAI_SESSIONS_URL, headers=HEADERS, json=payload)
    data = resp.json()
    return JSONResponse(
      {"client_secret": data.get("client_secret"),
       "expires_at":   data.get("expires_at")},
      status_code=resp.status_code
    )

app.include_router(router)
# backend/app/main.py  (dosyanın SONUNA ekleyin; varsa eski denemeleri kaldırın)
import os, httpx
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WORKFLOW_ID    = os.environ["WORKFLOW_ID"]

OPENAI_SESSIONS_URL = "https://api.openai.com/v1/chatkit/sessions"
HEADERS = {"Authorization": f"Bearer {OPENAI_API_KEY}",
           "Content-Type": "application/json"}

@router.post("/chatkit/start")
async def chatkit_start():
    payload = {
        "user": "web-user-1",                 # kullanıcıyı istediğin gibi tanımla
        "workflow": { "id": WORKFLOW_ID },    # Agent Builder > Workflow ID
        # Örnek: daha uzun süre istersen
        # "expires_after": { "seconds": 3600 }
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OPENAI_SESSIONS_URL, headers=HEADERS, json=payload)
    data = resp.json()
    return JSONResponse(
      {"client_secret": data.get("client_secret"),
       "expires_at":   data.get("expires_at")},
      status_code=resp.status_code
    )

@router.post("/chatkit/refresh")
async def chatkit_refresh(body: dict = Body(...)):
    current = body.get("currentClientSecret")
    # Çoğu kurulumda aynı endpoint ile refresh yapılır:
    payload = {
        "user": "web-user-1",
        "workflow": { "id": WORKFLOW_ID },
        "current_client_secret": current
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OPENAI_SESSIONS_URL, headers=HEADERS, json=payload)
    data = resp.json()
    return JSONResponse(
      {"client_secret": data.get("client_secret"),
       "expires_at":   data.get("expires_at")},
      status_code=resp.status_code
    )

app.include_router(router)
