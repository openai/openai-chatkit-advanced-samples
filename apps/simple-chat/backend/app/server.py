"""SimpleChatServer implements the ChatKitServer interface."""

from __future__ import annotations

import logging
from typing import Annotated, Any, AsyncIterator

from agents import Runner
from chatkit.agents import AgentContext, stream_agent_response
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
from pydantic import Field

from .agents.simple_agent import simple_agent
from .memory_store import MemoryStore
from .thread_item_converter import BasicThreadItemConverter

logging.basicConfig(level=logging.INFO)


class SimpleAgentContext(AgentContext):
    """Context for the simple chat agent."""
    store: Annotated[MemoryStore, Field(exclude=True)]
    request_context: dict[str, Any]


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
        # Create agent context
        agent_context = SimpleAgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

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
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported.")


def create_chatkit_server() -> SimpleChatServer:
    """Return a configured ChatKit server instance."""
    return SimpleChatServer()
