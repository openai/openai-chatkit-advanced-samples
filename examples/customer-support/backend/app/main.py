from __future__ import annotations

import os
from typing import Any

from chatkit.server import StreamingResult
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from openai import OpenAI
from pydantic import BaseModel
from starlette.responses import JSONResponse

from .server import TPTHelpServer, create_chatkit_server

app = FastAPI(title="TPT Help Desk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tpt_help_server: TPTHelpServer = create_chatkit_server()
CHATBOT_PROMPT_ID = os.getenv(
    "OPENAI_SUPPORT_PROMPT_ID",
    "pmpt_69cd0f0626e88197ab6100e38b46b65a0ebc4aff65bc5102",
)
CHATBOT_PROMPT_VERSION = os.getenv("OPENAI_SUPPORT_PROMPT_VERSION", "1")


class ChatbotMessage(BaseModel):
    role: str
    content: str


class ChatbotRequest(BaseModel):
    messages: list[ChatbotMessage]
    usertype: str
    question: str
    previous_response_id: str | None = None


class ChatbotResponse(BaseModel):
    answer: str
    response_id: str | None = None
    handoffSuggested: bool = False


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY is not configured for chatbot requests.",
        )
    return OpenAI(api_key=api_key)


def get_server() -> TPTHelpServer:
    return tpt_help_server


@app.post("/support/chatkit")
async def chatkit_endpoint(
    request: Request, server: TPTHelpServer = Depends(get_server)
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
    server: TPTHelpServer = Depends(get_server),
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
    server: TPTHelpServer = Depends(get_server),
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


@app.get("/support/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/support/chatbot", response_model=ChatbotResponse)
async def chatbot_endpoint(payload: ChatbotRequest) -> ChatbotResponse:
    if not payload.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is required.",
        )

    prompt = {
        "id": CHATBOT_PROMPT_ID,
        "version": CHATBOT_PROMPT_VERSION,
        "variables": {
            "usertype": payload.usertype,
        },
    }

    request_args: dict[str, Any] = {
        "prompt": prompt,
    }

    if payload.previous_response_id:
        request_args["previous_response_id"] = payload.previous_response_id
        request_args["input"] = [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": payload.question}],
            }
        ]
    else:
        request_args["input"] = [
            {
                "role": message.role,
                "content": [{"type": "input_text", "text": message.content}],
            }
            for message in payload.messages
        ]

    try:
        response = get_openai_client().responses.create(**request_args)
    except Exception as exc:  # pragma: no cover - surface API failure clearly
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Chatbot request failed: {exc}",
        ) from exc

    answer = (response.output_text or "").strip()
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Chatbot response did not contain text output.",
        )

    return ChatbotResponse(answer=answer, response_id=response.id)
