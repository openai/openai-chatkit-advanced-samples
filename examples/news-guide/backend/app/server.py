"""
NewsAssistantServer implements the ChatKitServer interface for the News Guide demo.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator

from agents import Agent, Runner
from chatkit.agents import stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    Action,
    AssistantMessageContent,
    AssistantMessageItem,
    Attachment,
    ThreadItemDoneEvent,
    ThreadItemUpdated,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    WidgetItem,
    WidgetRootUpdated,
)
from chatkit.widgets import ListView
from openai.types.responses import ResponseInputContentParam

from .agents.event_finder_agent import EventFinderContext, event_finder_agent
from .agents.news_agent import NewsAgentContext, news_agent
from .agents.puzzle_agent import PuzzleAgentContext, puzzle_agent
from .agents.title_agent import title_agent
from .data.article_store import ArticleStore
from .data.event_store import EventRecord, EventStore
from .memory_store import MemoryStore
from .request_context import RequestContext
from .thread_item_converter import NewsGuideThreadItemConverter
from .widgets.event_list_widget import build_event_list_widget


class NewsAssistantServer(ChatKitServer[RequestContext]):
    """ChatKit server wired up with the News Guide editorial assistant."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)

        data_dir = Path(__file__).resolve().parent / "data"
        self.article_store = ArticleStore(data_dir)
        self.event_store = EventStore(data_dir)
        self.thread_item_converter = NewsGuideThreadItemConverter()
        self.title_agent = title_agent

    # -- Required overrides ----------------------------------------------------
    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        updating_thread_title = asyncio.create_task(self._maybe_update_thread_title(thread, item))
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=20,
            order="desc",
            context=context,
        )
        items = list(reversed(items_page.data))
        input_items = await self.thread_item_converter.to_agent_input(items)

        agent, agent_context = self._select_agent(thread, item, context)

        result = Runner.run_streamed(agent, input_items, context=agent_context)

        async for event in stream_agent_response(agent_context, result):
            yield event
        await updating_thread_title
        return

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        if action.type == "open_article":
            async for event in self._handle_open_article_action(thread, action, context):
                yield event
            return
        if action.type == "view_event_details":
            async for event in self._handle_view_event_details_action(action, sender):
                yield event
            return

        return

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported in this demo.")

    # -- Helpers ----------------------------------------------------
    async def _maybe_update_thread_title(
        self, thread: ThreadMetadata, user_message: UserMessageItem | None
    ) -> None:
        if user_message is None or thread.title is not None:
            return

        run = await Runner.run(
            self.title_agent,
            input=await self.thread_item_converter.to_agent_input(user_message),
        )
        model_result: str = run.final_output
        model_result = model_result[:1].upper() + model_result[1:]
        thread.title = model_result.strip(".")

    async def _handle_open_article_action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        article_id = action.payload.get("id")
        if not article_id:
            return

        metadata = self.article_store.get_metadata(article_id)
        title = metadata["title"] if metadata else None
        message = (
            f"Want a quick summary of _{title}_ or have any questions about it?"
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

    async def _handle_view_event_details_action(
        self,
        action: Action[str, Any],
        sender: WidgetItem | None,
    ) -> AsyncIterator[ThreadStreamEvent]:
        selected_event_id = action.payload.get("id")
        event_ids = [
            event
            for event in (action.payload.get("event_ids") or [])
            if isinstance(event, str) and event
        ]
        is_selected = bool(action.payload.get("is_selected"))
        record = self.event_store.get_event(selected_event_id) if selected_event_id else None

        # If the event is already selected, no need to show the details again.
        if (
            is_selected
            or not record
            or not event_ids
            or not sender
            or not isinstance(sender.widget, ListView)
        ):
            return

        records: list[EventRecord] = []
        for event_id in event_ids:
            record = self.event_store.get_event(event_id)
            if record:
                records.append(record)

        updated_widget = build_event_list_widget(
            records,
            selected_event_id=selected_event_id,
        )

        if not updated_widget:
            return

        yield ThreadItemUpdated(
            item_id=sender.id,
            update=WidgetRootUpdated(widget=updated_widget),
        )

    def _select_agent(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: RequestContext,
    ) -> tuple[
        Agent,
        NewsAgentContext | EventFinderContext | PuzzleAgentContext,
    ]:
        tool_choice = self._resolve_tool_choice(item)
        if tool_choice == "event_finder":
            event_context = EventFinderContext(
                thread=thread,
                store=self.store,
                events=self.event_store,
                request_context=context,
            )
            return event_finder_agent, event_context
        if tool_choice == "puzzle":
            puzzle_context = PuzzleAgentContext(
                thread=thread,
                store=self.store,
                request_context=context,
            )
            return puzzle_agent, puzzle_context

        news_context = NewsAgentContext(
            thread=thread,
            store=self.store,
            articles=self.article_store,
            request_context=context,
        )
        return news_agent, news_context

    def _resolve_tool_choice(self, item: UserMessageItem | None) -> str | None:
        if not item or not item.inference_options:
            return None
        tool_choice = item.inference_options.tool_choice
        if tool_choice and isinstance(tool_choice.id, str):
            return tool_choice.id
        return None


def create_chatkit_server() -> NewsAssistantServer | None:
    """Return a configured ChatKit server instance if dependencies are available."""
    return NewsAssistantServer()
