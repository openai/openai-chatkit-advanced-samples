"""
MetroMapServer implements the ChatKitServer interface for the metro-map demo.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, AsyncIterator

from agents import Runner
from chatkit.agents import stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import Action, Attachment, ThreadMetadata, ThreadStreamEvent, UserMessageItem, WidgetItem
from openai.types.responses import ResponseInputContentParam

from .agents.metro_map_agent import MetroAgentContext, metro_map_agent
from .data.metro_map_store import MetroMapStore
from .memory_store import MemoryStore
from .request_context import RequestContext
from .thread_item_converter import MetroMapThreadItemConverter


class MetroMapServer(ChatKitServer[RequestContext]):
    """ChatKit server wired up with the metro map assistant."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)

        data_dir = Path(__file__).resolve().parent / "data"
        self.metro_map_store = MetroMapStore(data_dir)
        self.thread_item_converter = MetroMapThreadItemConverter()

    # -- Required overrides ----------------------------------------------------
    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        if item and not thread.title:
            thread.title = "Metro Planner"
            await self.store.save_thread(thread, context=context)

        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=20,
            order="desc",
            context=context,
        )
        items = list(reversed(items_page.data))
        input_items = await self.thread_item_converter.to_agent_input(items)

        agent_context = MetroAgentContext(
            thread=thread,
            store=self.store,
            metro=self.metro_map_store,
            request_context=context,
        )

        result = Runner.run_streamed(metro_map_agent, input_items, context=agent_context)

        async for event in stream_agent_response(agent_context, result):
            yield event
        return

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # No custom widget actions yet.
        return

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported in this demo.")


def create_chatkit_server() -> MetroMapServer | None:
    try:
        return MetroMapServer()
    except ImportError:
        return None
