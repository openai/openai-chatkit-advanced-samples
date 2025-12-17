from __future__ import annotations

from typing import Any

from chatkit.server import StreamingResult
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from starlette.responses import JSONResponse

from .server import CustomerSupportServer, create_chatkit_server

DEFAULT_THREAD_ID = "demo_default_thread"

app = FastAPI(title="ChatKit Customer Support API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

customer_support_server: CustomerSupportServer = create_chatkit_server()


def get_server() -> CustomerSupportServer:
    return customer_support_server


@app.post("/support/chatkit")
async def chatkit_endpoint(
    request: Request, server: CustomerSupportServer = Depends(get_server)
) -> Response:
    payload = await request.body()
    result = await server.process(payload, {"request": request})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


@app.api_route(
    "/support/attachments/{attachment_id}/upload",
    methods=["POST", "PUT"],
    name="upload_attachment",
)
async def upload_attachment(
    attachment_id: str,
    request: Request,
    server: CustomerSupportServer = Depends(get_server),
) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "").lower()
    data: bytes | None = None

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        file = form.get("file")
        if file is None or not hasattr(file, "read"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multipart uploads must include a 'file' field.",
            )
        data = await file.read()  # type: ignore[call-arg]
    else:
        data = await request.body()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attachment payload is required.",
        )

    attachment = await server.attachment_uploader.write_file(
        attachment_id, data, {"request": request}
    )
    return attachment.model_dump()


@app.get(
    "/support/attachments/{attachment_id}/content",
    name="download_attachment",
)
async def download_attachment(
    attachment_id: str,
    request: Request,
    server: CustomerSupportServer = Depends(get_server),
) -> Response:
    attachment, data = await server.attachment_uploader.read_file(
        attachment_id, {"request": request}
    )
    return Response(
        content=data,
        media_type=attachment.mime_type,
        headers={
            "Cache-Control": "private, max-age=600",
            "Content-Disposition": f'inline; filename="{attachment.name}"',
            "Access-Control-Allow-Origin": "*",
        },
    )


def _thread_param(thread_id: str | None) -> str:
    return thread_id or DEFAULT_THREAD_ID


@app.get("/support/customer")
async def customer_snapshot(
    thread_id: str | None = Query(
        None,
        description="ChatKit thread identifier",
    ),
    server: CustomerSupportServer = Depends(get_server),
) -> dict[str, Any]:
    key = _thread_param(thread_id)
    data = server.agent_state.to_dict(key)
    return {"customer": data}


@app.get("/support/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
