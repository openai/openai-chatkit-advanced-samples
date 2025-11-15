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
from chatkit.widgets import Button, ListView, WidgetComponentBase
from openai.types.responses import ResponseInputContentParam

from .article_store import ArticleStore
from .event_finder_agent import EventFinderContext, event_finder_agent
from .event_list_widget import build_event_list_widget
from .event_store import EventStore
from .memory_store import MemoryStore
from .news_agent import NewsAgentContext, news_agent
from .puzzle_agent import PuzzleAgentContext, puzzle_agent
from .thread_item_converter import BasicThreadItemConverter
from .title_agent import title_agent


class NewsAssistantServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server wired up with the News Guide editorial assistant."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)

        data_dir = Path(__file__).resolve().parent / "content"
        self.article_store = ArticleStore(data_dir)
        self.event_store = EventStore(data_dir)
        self.thread_item_converter = BasicThreadItemConverter()
        self.title_agent = title_agent

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
        if action.type == "view_event_details":
            async for event in self._handle_view_event_details_action(
                thread, action, sender, context
            ):
                yield event
            return

        return

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        updating_thread_title = asyncio.create_task(
            self.maybe_update_thread_title(thread, item)
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

        agent, agent_context = self._select_agent(thread, item, context)

        result = Runner.run_streamed(agent, input_items, context=agent_context)

        async for event in stream_agent_response(agent_context, result):
            yield event
        await updating_thread_title
        return

    async def maybe_update_thread_title(
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

    def _extract_article_id(self, action: Action[str, Any]) -> str | None:
        payload = action.payload
        if isinstance(payload, dict):
            article_id = payload.get("id")
            if isinstance(article_id, str) and article_id.strip():
                return article_id
        return None

    async def _handle_view_event_details_action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        event_id = self._extract_event_id(action)
        if not event_id:
            return

        record = self.event_store.get_event(event_id)
        if not record or not sender or not isinstance(sender.widget, ListView):
            message_item = AssistantMessageItem(
                thread_id=thread.id,
                id=self.store.generate_item_id("message", thread, context),
                created_at=datetime.now(),
                content=[
                    AssistantMessageContent(
                        text="I couldn't find details for that event, but feel free to ask about another one."
                    )
                ],
            )
            yield ThreadItemDoneEvent(item=message_item)
            return

        description = record.get("details")
        updated_widget = self._build_widget_with_description(
            sender.widget,
            event_id,
            description,
        )
        yield ThreadItemUpdated(
            item_id=sender.id,
            update=WidgetRootUpdated(widget=updated_widget),
        )

    def _extract_event_id(self, action: Action[str, Any]) -> str | None:
        payload = action.payload
        if isinstance(payload, dict):
            event_id = payload.get("id")
            if isinstance(event_id, str) and event_id.strip():
                return event_id
        return None

    def _build_widget_with_description(
        self,
        widget: ListView,
        selected_event_id: str,
        description: str,
    ) -> ListView | None:
        records = self._load_widget_event_records(widget)
        if not records:
            return None
        ids = {record.get("id") for record in records}
        if selected_event_id not in ids:
            return None
        return build_event_list_widget(
            records,
            selected_event_id=selected_event_id,
            selected_event_description=description,
        )

    def _load_widget_event_records(self, widget: ListView) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for event_id in self._collect_event_ids(widget):
            record = self.event_store.get_event(event_id)
            if record:
                records.append(record)
        return records

    def _collect_event_ids(self, component: WidgetComponentBase) -> list[str]:
        ids: list[str] = []
        self._gather_event_ids(component, ids)
        return ids

    def _gather_event_ids(
        self,
        component: WidgetComponentBase,
        output: list[str],
    ) -> None:
        action = getattr(component, "onClickAction", None)
        if isinstance(component, Button) and action:
            payload = getattr(action, "payload", None)
            if isinstance(payload, dict):
                event_id = payload.get("id")
                if isinstance(event_id, str):
                    normalized = event_id.strip()
                    if normalized:
                        output.append(normalized)

        children = getattr(component, "children", None)
        if not children:
            return

        if isinstance(children, list):
            for child in children:
                if isinstance(child, WidgetComponentBase):
                    self._gather_event_ids(child, output)
        elif isinstance(children, WidgetComponentBase):
            self._gather_event_ids(children, output)

    def _select_agent(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict[str, Any],
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
