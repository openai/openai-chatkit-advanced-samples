import base64
import logging

from chatkit.agents import ThreadItemConverter
from chatkit.types import Attachment, HiddenContextItem
from openai.types.responses import ResponseInputImageParam, ResponseInputTextParam
from openai.types.responses.response_input_item_param import Message

from .attachment_store import LocalAttachmentStore


class CustomerSupportThreadItemConverter(ThreadItemConverter):
    def __init__(self, attachment_store: LocalAttachmentStore) -> None:
        self._attachment_store = attachment_store
        self._logger = logging.getLogger(__name__)

    async def attachment_to_message_content(
        self, attachment: Attachment
    ) -> ResponseInputImageParam:
        if attachment.type != "image":
            raise RuntimeError("Only image attachments are supported in this demo.")
        try:
            stored, data = await self._attachment_store.read_file(attachment.id, context={})
            mime_type = (
                getattr(stored, "mime_type", None)
                or getattr(attachment, "mime_type", None)
                or "image/jpeg"
            )
            encoded = base64.b64encode(data).decode("ascii")
            image_url = f"data:{mime_type};base64,{encoded}"
        except Exception as exc:  # pragma: no cover - best-effort fallback
            self._logger.warning(
                "Unable to load attachment %s bytes: %s. Falling back to preview_url.",
                attachment.id,
                exc,
            )
            preview = getattr(attachment, "preview_url", None)
            image_url = str(preview) if preview is not None else attachment.id
        return ResponseInputImageParam(
            type="input_image",
            image_url=image_url,
            detail="auto",
        )

    async def hidden_context_to_input(self, item: HiddenContextItem):
        return Message(
            type="message",
            content=[
                ResponseInputTextParam(
                    type="input_text",
                    text=item.content,
                )
            ],
            role="user",
        )
