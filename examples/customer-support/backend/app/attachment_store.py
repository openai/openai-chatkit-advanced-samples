from __future__ import annotations

import base64
from typing import Any

from chatkit.store import AttachmentStore, NotFoundError
from chatkit.types import Attachment, AttachmentCreateParams, ImageAttachment
from fastapi import HTTPException, status
from starlette.requests import Request

from .memory_store import MemoryStore

MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024


class LocalAttachmentStore(AttachmentStore[dict[str, Any]]):
    """In-memory attachment store suitable for local demos."""

    def __init__(
        self,
        store: MemoryStore,
        max_bytes: int = MAX_ATTACHMENT_BYTES,
    ) -> None:
        self.store = store
        self.max_bytes = max_bytes
        self._files: dict[str, bytes] = {}

    async def create_attachment(
        self,
        input: AttachmentCreateParams,
        context: dict[str, Any],
    ) -> Attachment:
        self._validate_size(input.size)
        self._validate_mime_type(input.mime_type)
        request = self._require_request(context)

        attachment_id = self.generate_attachment_id(input.mime_type, context)
        upload_url = self._build_url(request, "upload_attachment", attachment_id)
        preview_url = self._build_url(request, "download_attachment", attachment_id)

        attachment = ImageAttachment(
            id=attachment_id,
            name=input.name,
            mime_type=input.mime_type,
            upload_url=upload_url,
            preview_url=preview_url,
        )
        await self.store.save_attachment(attachment, context=context)
        self._files.pop(attachment_id, None)
        return attachment

    async def delete_attachment(self, attachment_id: str, context: dict[str, Any]) -> None:
        self._files.pop(attachment_id, None)

    async def write_file(
        self,
        attachment_id: str,
        data: bytes,
        context: dict[str, Any],
    ) -> Attachment:
        self._validate_size(len(data))
        attachment = await self._load_attachment_or_404(attachment_id, context)
        self._files[attachment_id] = data
        # Use data URL previews to avoid mixed-content / private-network issues
        mime_type = getattr(attachment, "mime_type", "image/jpeg")
        encoded = base64.b64encode(data).decode("ascii")
        preview_url = "data:" + mime_type + ";base64," + encoded
        if attachment.upload_url is not None:
            attachment = attachment.model_copy(update={"upload_url": None})
        if getattr(attachment, "preview_url", None) != preview_url:
            attachment = attachment.model_copy(update={"preview_url": preview_url})
        await self.store.save_attachment(attachment, context=context)
        return attachment

    async def read_file(
        self, attachment_id: str, context: dict[str, Any]
    ) -> tuple[Attachment, bytes]:
        attachment = await self._load_attachment_or_404(attachment_id, context)
        if attachment_id not in self._files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment has not been uploaded yet.",
            )
        return attachment, self._files[attachment_id]

    def _build_url(self, request: Request, route_name: str, attachment_id: str):
        return request.url_for(route_name, attachment_id=attachment_id)

    def _validate_mime_type(self, mime_type: str) -> None:
        if not mime_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image attachments are supported in this demo.",
            )

    def _validate_size(self, size: int) -> None:
        if size > self.max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Attachments are limited to 5 MB in this demo.",
            )

    def _require_request(self, context: dict[str, Any]) -> Request:
        request = context.get("request")
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Attachment requests must include HTTP context.",
            )
        return request

    async def _load_attachment_or_404(
        self, attachment_id: str, context: dict[str, Any]
    ) -> Attachment:
        try:
            return await self.store.load_attachment(attachment_id, context=context)
        except NotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attachment {attachment_id} does not exist.",
            ) from exc
