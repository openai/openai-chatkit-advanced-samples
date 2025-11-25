"""
CatAssistantServer implements the ChatKitServer interface.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, AsyncIterator

from agents import Runner
from chatkit.agents import stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    Action,
    AssistantMessageContent,
    AssistantMessageItem,
    Attachment,
    HiddenContextItem,
    ThreadItemDoneEvent,
    ThreadItemReplacedEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    WidgetItem,
)
from openai.types.responses import ResponseInputContentParam

from .cat_agent import CatAgentContext, cat_agent
from .cat_store import CatStore
from .memory_store import MemoryStore
from .thread_item_converter import BasicThreadItemConverter
from .widgets.name_suggestions_widget import (
    CatNameSuggestion,
    build_name_suggestions_widget,
)

logging.basicConfig(level=logging.INFO)


class CatAssistantServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server wired up with the virtual cat caretaker."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)

        # Define additional instance variables for convenience.
        self.cat_store = CatStore()
        self.thread_item_converter = BasicThreadItemConverter()

    # -- Required overrides ----------------------------------------------------
    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        if action.type == "cats.select_name":
            async for event in self._handle_select_name_action(
                thread,
                action.payload,
                sender,
                context,
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
        # The agent context includes information that we'll be able to access in tool calls.
        # This is NOT sent to the model as input.
        agent_context = CatAgentContext(
            thread=thread,
            store=self.store,
            cats=self.cat_store,
            request_context=context,
        )

        # All items in the thread are loaded and sent to the agent as input
        # so that the agent is aware of the full conversation when generating a response.
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=20,
            order="desc",
            context=context,
        )

        # Runner expects the most recent message to be last.
        items = list(reversed(items_page.data))

        # Translate ChatKit thread items into agent input.
        input_items = await self.thread_item_converter.to_agent_input(items)

        result = Runner.run_streamed(
            cat_agent,
            input_items,
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event
        return

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported in this demo.")

    # -- Helpers ----------------------------------------------------
    async def _handle_select_name_action(
        self,
        thread: ThreadMetadata,
        payload: dict[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        name = payload["name"].strip()
        if not name or not sender:
            return

        options = [CatNameSuggestion(**option) for option in payload["options"]]
        current_state = await self.cat_store.load(thread.id)
        is_already_named = current_state.name != "Unnamed Cat"
        selection = current_state.name if is_already_named else name
        widget = build_name_suggestions_widget(options, selected=selection)

        yield ThreadItemReplacedEvent(
            item=sender.model_copy(update={"widget": widget}),
        )

        if is_already_named:
            message_item = AssistantMessageItem(
                id=self.store.generate_item_id("message", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[
                    AssistantMessageContent(
                        text=f"{current_state.name} already has a name, so we can't rename them."
                    )
                ],
            )
            yield ThreadItemDoneEvent(item=message_item)
            return

        # Save the name in the cat store and update the thread title in the chatkit store.
        state = await self.cat_store.mutate(thread.id, lambda s: s.rename(name))
        title = f"{state.name}’s Lounge"
        thread.title = title
        await self.store.save_thread(thread, context)

        # Add a hidden context item so that future agent input will know that the user
        # has selected a name from the suggestions list.
        await self.store.add_thread_item(
            thread.id,
            HiddenContextItem(
                id=self.store.generate_item_id("message", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=f"<CAT_NAME_SELECTED>{state.name}</CAT_NAME_SELECTED>",
            ),
            context=context,
        )

        message_item = AssistantMessageItem(
            id=self.store.generate_item_id("message", thread, context),
            thread_id=thread.id,
            created_at=datetime.now(),
            content=[
                AssistantMessageContent(
                    text=f"Love that choice. {state.name}’s profile card is now ready. Would you like to check it out?"
                )
            ],
        )
        # No need to explicitly save the assistant message item in the store.
        # It will be automatically saved when the agent response is streamed.
        yield ThreadItemDoneEvent(item=message_item)


def create_chatkit_server() -> CatAssistantServer | None:
    """Return a configured ChatKit server instance if dependencies are available."""
    return CatAssistantServer()
