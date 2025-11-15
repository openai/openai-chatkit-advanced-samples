"""
NewsAssistantServer implements the ChatKitServer interface for the News Guide demo.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator

from agents import Runner
from chatkit.agents import stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    Action,
    AssistantMessageContent,
    AssistantMessageItem,
    Attachment,
    ThreadItemDoneEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    WidgetItem,
)
from openai.types.responses import ResponseInputContentParam

from .article_store import ArticleStore
from .memory_store import MemoryStore
from .news_agent import NewsAgentContext, news_agent
from .thread_item_converter import BasicThreadItemConverter


class NewsAssistantServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server wired up with the News Guide editorial assistant."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)

        data_dir = Path(__file__).resolve().parent / "content"
        self.article_store = ArticleStore(data_dir)
        self.thread_item_converter = BasicThreadItemConverter()

    # -- Required overrides ----------------------------------------------------
    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        # TODO: handle server actions
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                thread_id=thread.id,
                id=self.store.generate_item_id("message", thread, context),
                created_at=datetime.now(),
                content=[AssistantMessageContent(text="")],
            ),
        )

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        agent_context = NewsAgentContext(
            thread=thread,
            store=self.store,
            articles=self.article_store,
            request_context=context,
        )

        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=20,
            order="desc",
            context=context,
        )
        items = list(reversed(items_page.data))
        input_items = await self.thread_item_converter.to_agent_input(items)

        result = Runner.run_streamed(
            news_agent,
            input_items,
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event
        return

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported in this demo.")


def create_chatkit_server() -> NewsAssistantServer | None:
    """Return a configured ChatKit server instance if dependencies are available."""
    return NewsAssistantServer()
