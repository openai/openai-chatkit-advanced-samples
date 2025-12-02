"""
MetroMapServer implements the ChatKitServer interface for the metro-map demo.
"""

from __future__ import annotations

import asyncio
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
    ClientEffectEvent,
    HiddenContextItem,
    ThreadItemDoneEvent,
    ThreadItemReplacedEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    WidgetItem,
)
from openai.types.responses import ResponseInputContentParam

from .agents.metro_map_agent import MetroAgentContext, metro_map_agent
from .agents.title_agent import title_agent
from .data.metro_map_store import MetroMapStore
from .memory_store import MemoryStore
from .request_context import RequestContext
from .thread_item_converter import MetroMapThreadItemConverter
from .widgets.line_select_widget import build_line_select_widget


class MetroMapServer(ChatKitServer[RequestContext]):
    """ChatKit server wired up with the metro map assistant."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)

        data_dir = Path(__file__).resolve().parent / "data"
        self.metro_map_store = MetroMapStore(data_dir)
        self.thread_item_converter = MetroMapThreadItemConverter(self.metro_map_store)
        self.title_agent = title_agent

    # -- Required overrides ----------------------------------------------------
    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        updating_thread_title = asyncio.create_task(
            self._maybe_update_thread_title(thread, item, context)
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

        agent_context = MetroAgentContext(
            thread=thread,
            store=self.store,
            metro=self.metro_map_store,
            request_context=context,
        )

        result = Runner.run_streamed(metro_map_agent, input_items, context=agent_context)

        async for event in stream_agent_response(agent_context, result):
            yield event
        await updating_thread_title

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        if action.type == "line.select":
            if action.payload is None:
                return
            async for event in self._handle_line_select_action(
                thread, action.payload, sender, context
            ):
                yield event
            return

        return

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported in this demo.")

    # -- Helpers ----------------------------------------------------
    async def _handle_line_select_action(
        self,
        thread: ThreadMetadata,
        payload: dict[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        line_id = payload["id"]

        # Update the widget to show the selected line and disable further clicks.
        updated_widget = build_line_select_widget(
            self.metro_map_store.list_lines(),
            selected=line_id,
        )

        if sender:
            updated_widget_item = sender.model_copy(update={"widget": updated_widget})
            yield ThreadItemReplacedEvent(
                item=updated_widget_item,
            )

        # Add hidden context so the agent can pick up the chosen line id on the next run.
        await self.store.add_thread_item(
            thread.id,
            HiddenContextItem(
                id=self.store.generate_item_id("message", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=f"<LINE_SELECTED>{line_id}</LINE_SELECTED>",
            ),
            context=context,
        )

        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                thread_id=thread.id,
                id=self.store.generate_item_id("message", thread, context),
                created_at=datetime.now(),
                content=[
                    AssistantMessageContent(
                        text="Would you like to add the station to the beginning or end of the line?"
                    )
                ],
            ),
        )

        yield ClientEffectEvent(
            name="location_select_mode",
            data={"lineId": line_id},
        )

    async def _maybe_update_thread_title(
        self,
        thread: ThreadMetadata,
        user_message: UserMessageItem | None,
        context: RequestContext,
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
        await self.store.save_thread(thread, context=context)


def create_chatkit_server() -> MetroMapServer | None:
    try:
        return MetroMapServer()
    except ImportError:
        return None
