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
        if action.type == "open_article":
            async for event in self._handle_open_article_action(thread, action, context):
                yield event
            return

        return

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

    async def _handle_open_article_action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        article_id = self._extract_article_id(action)
        if not article_id:
            return

        metadata = self.article_store.get_metadata(article_id)
        title = metadata["title"] if metadata else None
        message = (
            f'Want a quick summary of "{title}" or have any questions about it?'
            if title
            else "Want a quick summary or have any questions about this article?"
        )

        message_item = AssistantMessageItem(
            thread_id=thread.id,
            id=self.store.generate_item_id("message", thread, context),
            created_at=datetime.now(),
            content=[AssistantMessageContent(text=message)],
        )
        yield ThreadItemDoneEvent(item=message_item)

    def _extract_article_id(self, action: Action[str, Any]) -> str | None:
        payload = action.payload
        if isinstance(payload, dict):
            article_id = payload.get("id")
            if isinstance(article_id, str) and article_id.strip():
                return article_id
        return None


def create_chatkit_server() -> NewsAssistantServer | None:
    """Return a configured ChatKit server instance if dependencies are available."""
    return NewsAssistantServer()
