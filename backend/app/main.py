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
# --- ADD: ChatKit session endpoint (no-code friendly) ---
import os, httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WORKFLOW_ID = os.environ["WORKFLOW_ID"]

@router.post("/chatkit")
async def create_chatkit_session():
    """
    ChatKit frontend bu endpoint'e POST eder.
    Biz de OpenAI'den session oluşturup client_secret'i geri döneriz.
    """
    url = "https://api.openai.com/v1/chatkit/sessions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    # 'user' serbest bir son-kullanıcı kimliği. Kullanıcı başına sabit bir değer verebilirsin.
    payload = {
        "user": "web-user-1",
        "workflow": { "id": WORKFLOW_ID },  # Agent Builder'dan aldığın ID
        # İstersen burada chatkit_configuration / history / file_upload vb. opsiyonları açabilirsin.
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=headers, json=payload)
    data = r.json()
    # ChatKit'in beklediği alan: client_secret
    # (frontend bu secret'ı alıp widget'ı başlatır)
    return JSONResponse(
        {
            "client_secret": data.get("client_secret"),
            "expires_at": data.get("expires_at"),
        },
        status_code=r.status_code,
    )

# Mevcut FastAPI app'ine router'ı bağla:
# app.include_router(router) satırı zaten varsa gerek yok; yoksa ekleyin:
try:
    app.include_router(router)
except Exception:
    pass
# --- /ADD ---
