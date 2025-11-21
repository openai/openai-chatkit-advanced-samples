"""SimpleChatServer implements the ChatKitServer interface."""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from agents import Runner
from chatkit.agents import stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    Action,
    Attachment,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    WidgetItem,
)
from openai.types.responses import ResponseInputContentParam

from .agents.simple_agent import simple_agent
from .memory_store import MemoryStore
from .thread_item_converter import BasicThreadItemConverter

logging.basicConfig(level=logging.INFO)


class SimpleChatServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server for simple conversation."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)
        self.thread_item_converter = BasicThreadItemConverter()

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        # No widget actions in simple chat
        return
        yield  # Make this an async generator

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Load all thread items for conversation history
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=50,
            order="desc",
            context=context,
        )

        # Reverse to get chronological order
        items = list(reversed(items_page.data))

        # Convert to agent input format
        input_items = await self.thread_item_converter.to_agent_input(items)

        # Run agent with streaming
        result = Runner.run_streamed(
            simple_agent,
            input_items,
        )

        async for event in stream_agent_response(None, result):
            yield event

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported.")


def create_chatkit_server() -> SimpleChatServer:
    """Return a configured ChatKit server instance."""
    return SimpleChatServer()
