"""FastAPI main application for Mercedes-Benz automobile assistant."""

from __future__ import annotations

from typing import Any

from chatkit.server import StreamingResult
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

from .chat import MercedesServer, create_chatkit_server
from .vehicle_state import get_vehicle_state

app = FastAPI(
    title="Mercedes-Benz Automobile Assistant API",
    description="ChatKit-powered voice assistant for Mercedes-Benz vehicles",
    version="0.1.0",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChatKit server singleton
_chatkit_server: MercedesServer | None = None


def get_chatkit_server() -> MercedesServer:
    """Get or create the ChatKit server instance."""
    global _chatkit_server
    if _chatkit_server is None:
        _chatkit_server = create_chatkit_server()
    return _chatkit_server


@app.post("/mercedes/chatkit")
async def chatkit_endpoint(
    request: Request,
    server: MercedesServer = Depends(get_chatkit_server),
) -> Response:
    """ChatKit streaming endpoint."""
    payload = await request.body()
    result = await server.process(payload, {"request": request})

    if isinstance(result, StreamingResult):
        return StreamingResponse(
            result,
            media_type="text/event-stream",
        )

    if hasattr(result, "json"):
        return Response(
            content=result.json,
            media_type="application/json",
        )

    return JSONResponse(content=result)


@app.get("/mercedes/vehicle-state")
async def get_vehicle_state_endpoint() -> dict[str, Any]:
    """Get current vehicle state for UI display."""
    vehicle = get_vehicle_state()
    return vehicle.to_dict()


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
