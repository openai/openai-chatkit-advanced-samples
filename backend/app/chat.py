"""ChatKit server powering the virtual cat companion experience."""

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
    ThreadItemUpdated,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    WidgetItem,
    WidgetRootUpdated,
)
from openai.types.responses import ResponseInputContentParam
from pydantic import ValidationError

from .cat_agent import CatAgentContext, cat_agent
from .cat_name_widget import (
    SELECT_CAT_NAME_ACTION_TYPE,
    CatNameSelectionPayload,
    CatNameSuggestion,
    build_name_suggestions_widget,
)
from .cat_store import CatStore
from .memory_store import MemoryStore
from .thread_item_converter import BasicThreadItemConverter

logging.basicConfig(level=logging.INFO)


class CatAssistantServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server wired up with the virtual cat caretaker."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        self.cat_store = CatStore()
        super().__init__(self.store)
        self.assistant = cat_agent
        self.thread_item_converter = BasicThreadItemConverter()

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        if action.type == SELECT_CAT_NAME_ACTION_TYPE:
            payload = self._parse_select_name_payload(action)
            if payload is None:
                return
            async for event in self._handle_select_name_action(
                thread,
                payload,
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
        agent_context = CatAgentContext(
            thread=thread,
            store=self.store,
            cats=self.cat_store,
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
            self.assistant,
            input_items,
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event
        return

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported in this demo.")

    @staticmethod
    def _parse_select_name_payload(
        action: Action[str, Any],
    ) -> CatNameSelectionPayload | None:
        try:
            return CatNameSelectionPayload.model_validate(action.payload or {})
        except ValidationError as exc:
            logging.warning("Invalid select name payload: %s", exc)
            return None

    async def _handle_select_name_action(
        self,
        thread: ThreadMetadata,
        payload: CatNameSelectionPayload,
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        name = payload.name.strip()
        if not name or not sender:
            return

        options = payload.options or [CatNameSuggestion(name=name)]
        current_state = await self.cat_store.load(thread.id)
        is_already_named = current_state.name != "Unnamed Cat"
        selection = current_state.name if is_already_named else name
        widget = build_name_suggestions_widget(options, selected=selection)

        # Save the updated widget so that if the user views the thread again, they will
        # see the updated version of the widget.
        updated_widget_item = sender.model_copy(update={"widget": widget})
        await self.store.save_item(thread.id, updated_widget_item, context=context)

        # Stream back the update so that chatkit can render the updated widget,
        yield ThreadItemUpdated(
            item_id=sender.id,
            update=WidgetRootUpdated(widget=widget),
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
        # Make sure that any new message items are explicitly added to the thread - emitted items are not
        # automatically stored to the chatkit store when handling actions.
        # await self.store.add_thread_item(thread.id, message_item, context)
        yield ThreadItemDoneEvent(item=message_item)


def create_chatkit_server() -> CatAssistantServer | None:
    """Return a configured ChatKit server instance if dependencies are available."""
    return CatAssistantServer()
