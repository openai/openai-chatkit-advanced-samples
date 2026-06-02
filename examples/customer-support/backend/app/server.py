"""ChatKit server wiring for the TPT helpdesk experience."""

from __future__ import annotations

import io
import logging
import os
from typing import Any, AsyncIterator

from chatkit.agents import AgentContext, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    AudioInput,
    ThreadMetadata,
    ThreadStreamEvent,
    TranscriptionResult,
    UserMessageItem,
)
from fastapi import HTTPException
from openai import OpenAI

from .attachment_store import LocalAttachmentStore
from .memory_store import MemoryStore
from .support_agent import tpt_agent
from .thread_item_converter import CustomerSupportThreadItemConverter

from agents import Runner

logger = logging.getLogger(__name__)


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not set for transcription requests.",
        )
    return OpenAI(api_key=api_key)


class TPTHelpServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server that powers the TPT helpdesk demo."""

    def __init__(self) -> None:
        store = MemoryStore()
        attachment_store = LocalAttachmentStore(store)
        super().__init__(store, attachment_store=attachment_store)
        self.store = store
        self._local_attachment_store = attachment_store
        self.agent = tpt_agent
        self.thread_item_converter = CustomerSupportThreadItemConverter(
            attachment_store=attachment_store
        )

    @property
    def attachment_uploader(self) -> LocalAttachmentStore:
        return self._local_attachment_store

    async def respond(
        self,
        thread: ThreadMetadata,
        user_message: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        items_page = await self.store.load_thread_items(
            thread.id,
            None,
            20,
            "desc",
            context,
        )
        items = list(reversed(items_page.data))
        input_items = await self.thread_item_converter.to_agent_input(items)

        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        result = Runner.run_streamed(
            self.agent,
            input_items,
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event

    async def transcribe(
        self, audio_input: AudioInput, context: dict[str, Any]
    ) -> TranscriptionResult:
        ext = {
            "audio/webm": "webm",
            "audio/mp4": "m4a",
            "audio/ogg": "ogg",
        }.get(audio_input.media_type)
        if not ext:
            raise HTTPException(status_code=400, detail="Unexpected audio format")

        audio_file = io.BytesIO(audio_input.data)
        audio_file.name = f"audio.{ext}"
        transcription = get_openai_client().audio.transcriptions.create(
            model="gpt-4o-transcribe", file=audio_file
        )
        return TranscriptionResult(text=transcription.text)


def create_chatkit_server() -> TPTHelpServer:
    """Return a configured ChatKit server instance."""
    return TPTHelpServer()
