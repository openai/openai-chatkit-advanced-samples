"""FastAPI entrypoint wiring the ChatKit server and REST endpoints."""

from __future__ import annotations

from typing import Any

from chatkit.server import StreamingResult
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from starlette.responses import JSONResponse

from .data.metro_map_store import MetroMap
from .request_context import RequestContext
from .server import MetroMapServer, create_chatkit_server

app = FastAPI(title="Metro Map API")

_chatkit_server: MetroMapServer | None = create_chatkit_server()


def get_chatkit_server() -> MetroMapServer:
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
    request: Request, server: MetroMapServer = Depends(get_chatkit_server)
) -> Response:
    payload = await request.body()
    map_id = request.headers.get("map-id") or "solstice-metro"
    context = RequestContext(request=request, map_id=map_id)
    result = await server.process(payload, context)
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


@app.get("/map")
async def read_map(
    server: MetroMapServer = Depends(get_chatkit_server),
) -> dict[str, Any]:
    return {"map": server.metro_map_store.dump_for_client()}


class MapUpdatePayload(BaseModel):
    map: MetroMap


@app.post("/map")
async def write_map(
    payload: MapUpdatePayload, server: MetroMapServer = Depends(get_chatkit_server)
) -> dict[str, Any]:
    try:
        server.metro_map_store.set_map(payload.map)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"map": payload.map.model_dump(mode="json")}
