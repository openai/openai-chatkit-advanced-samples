"""
MetroMapServer implements the ChatKitServer interface for the metro-map demo.
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
    Attachment,
    HiddenContextItem,
    ThreadItemUpdated,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    WidgetItem,
    WidgetRootUpdated,
)
from openai.types.responses import ResponseInputContentParam
from pydantic import ValidationError

from .agents.metro_map_agent import MetroAgentContext, metro_map_agent
from .data.metro_map_store import MetroMapStore
from .memory_store import MemoryStore
from .request_context import RequestContext
from .thread_item_converter import MetroMapThreadItemConverter
from .widgets.line_select_widget import (
    LINE_SELECT_ACTION_TYPE,
    LineSelectPayload,
    build_line_select_widget,
)


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
        async for event in self._stream_agent(thread, item, context):
            yield event
        return

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        if action.type == LINE_SELECT_ACTION_TYPE:
            payload = self._parse_line_select_payload(action)
            if payload is None:
                return
            async for event in self._handle_line_select_action(thread, payload, sender, context):
                yield event
            return

        return

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported in this demo.")

    # -- Helpers ----------------------------------------------------
    async def _stream_agent(
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

    def _parse_line_select_payload(self, action: Action[str, Any]) -> LineSelectPayload | None:
        try:
            return LineSelectPayload.model_validate(action.payload or {})
        except ValidationError as exc:
            print(f"[WARN] Invalid line.select payload: {exc}")
            return None

    async def _handle_line_select_action(
        self,
        thread: ThreadMetadata,
        payload: LineSelectPayload,
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Update the widget to show the selected line and disable further clicks.
        updated_widget = build_line_select_widget(
            self.metro_map_store.list_lines(),
            selected=payload.id,
        )

        if sender:
            updated_widget_item = sender.model_copy(update={"widget": updated_widget})
            await self.store.save_item(thread.id, updated_widget_item, context=context)
            yield ThreadItemUpdated(
                item_id=sender.id,
                update=WidgetRootUpdated(widget=updated_widget),
            )

        # Add hidden context so the agent can pick up the chosen line id on the next run.
        await self.store.add_thread_item(
            thread.id,
            HiddenContextItem(
                id=self.store.generate_item_id("message", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=f"<LINE_SELECTED>{payload.id}</LINE_SELECTED>",
            ),
            context=context,
        )

        # Trigger a fresh agent run with the updated context so the assistant can respond.
        async for event in self._stream_agent(thread, None, context):
            yield event


def create_chatkit_server() -> MetroMapServer | None:
    try:
        return MetroMapServer()
    except ImportError:
        return None
