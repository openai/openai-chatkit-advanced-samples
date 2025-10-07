"""FastAPI entrypoint wiring the ChatKit server and REST endpoints."""
from __future__ import annotations
from typing import Any

from fastapi import APIRouter, Body, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.responses import JSONResponse as StarletteJSONResponse  # only if you use it elsewhere

# Eğer facts endpointlerini kullanıyorsan tut; kullanmıyorsan kaldırabilirsin
from .facts import fact_store

app = FastAPI(title="ChatKit API")

# -----------------------------
# ⚠️ ESKİ STREAMING ENDPOINT KALDIRILDI
# Aşağıdaki blok DOSYADAN SİLİNDİ:
#   - _chatkit_server
#   - get_chatkit_server()
#   - @app.post("/chatkit") ... (StreamingResult / server.process)
# -----------------------------

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

# ---------- ChatKit SESSION ENDPOINTLERİ (TEK KOPYA) ----------
import os, httpx

router = APIRouter(prefix="/api")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WORKFLOW_ID    = os.environ["WORKFLOW_ID"]

OPENAI_SESSIONS_URL = "https://api.openai.com/v1/chatkit/sessions"
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
}

@router.post("/chatkit/start")
async def chatkit_start():
    """Yeni bir ChatKit oturumu oluşturur; client_secret döner."""
    payload = {
        "user": "web-user-1",
        "workflow": {"id": WORKFLOW_ID},
        # "expires_after": {"seconds": 3600},  # istersen aç
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OPENAI_SESSIONS_URL, headers=HEADERS, json=payload)
    data = resp.json()
    return JSONResponse(
        {"client_secret": data.get("client_secret"),
         "expires_at": data.get("expires_at")},
        status_code=resp.status_code,
    )

@router.post("/chatkit/refresh")
async def chatkit_refresh(body: dict = Body(...)):
    """Mevcut client_secret süresi dolmadan yeniler."""
    payload = {
        "user": "web-user-1",
        "workflow": {"id": WORKFLOW_ID},
        "current_client_secret": body.get("currentClientSecret"),
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OPENAI_SESSIONS_URL, headers=HEADERS, json=payload)
    data = resp.json()
    return JSONResponse(
        {"client_secret": data.get("client_secret"),
         "expires_at": data.get("expires_at")},
        status_code=resp.status_code,
    )

app.include_router(router)
# ---------- /SESSION ENDPOINTLERİ ----------
