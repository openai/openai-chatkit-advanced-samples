"""CupidServer implements the ChatKitServer interface for the Cupid matchmaking game."""

from __future__ import annotations

import logging
import yaml
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, AsyncIterator

from agents import Runner
from chatkit.agents import AgentContext, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    Action,
    Attachment,
    InferenceOptions,
    ThreadItemDoneEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    UserMessageTextContent,
    WidgetItem,
)
from openai.types.responses import ResponseInputContentParam
from pydantic import Field

from .agents.cupid_agent import cupid_agent
from .memory_store import MemoryStore
from .request_context import RequestContext
from .thread_item_converter import BasicThreadItemConverter
from .widgets.profilecard_widget import build_profilecard_widget

logging.basicConfig(level=logging.INFO)


class CupidAgentContext(AgentContext):
    """Context for the Cupid game agent."""

    store: Annotated[MemoryStore, Field(exclude=True)]
    request_context: RequestContext


class CupidServer(ChatKitServer[RequestContext]):
    """ChatKit server for Cupid romantic matchmaking game."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)
        self.thread_item_converter = BasicThreadItemConverter()

        # Load character data from YAML files
        data_dir = Path(__file__).parent / "data"
        with open(data_dir / "mortal.yaml", "r", encoding="utf-8") as f:
            self.mortal_data = yaml.safe_load(f)
        with open(data_dir / "match.yaml", "r", encoding="utf-8") as f:
            self.match_data = yaml.safe_load(f)

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Handle widget action (MATCH button click)."""
        # The MATCH button sends type="conversation.message" with payload text="yes"
        # We need to create a user message and then call respond() to advance to next chapter

        if action.type == "conversation.message":
            # Get the message text from the payload
            message_text = action.payload.get("text", "yes")

            # Create a user message item
            user_message = UserMessageItem(
                thread_id=thread.id,
                id=self.store.generate_item_id("message", thread, context),
                created_at=datetime.now(),
                content=[UserMessageTextContent(text=message_text)],
                inference_options=InferenceOptions(),
            )

            # Add the message to the store
            await self.store.add_thread_item(thread.id, user_message, context)

            # Yield the message event
            yield ThreadItemDoneEvent(item=user_message)

            # Call respond to generate the next chapter
            async for event in self.respond(thread, user_message, context):
                yield event
        return
        yield  # Make this an async generator

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Handle conversation turns with chapter-based logic."""

        # Initialize chapter tracking if needed
        if "chapter" not in context:
            context["chapter"] = 1
            context["mortal_data"] = self.mortal_data
            context["match_data"] = self.match_data

        # Create agent context
        agent_context = CupidAgentContext(
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

        # Chapter-based logic
        chapter = context.get("chapter", 1)

        if chapter == 1:
            # Chapter 1: Present Zara (mortal)
            # Run cupid agent for narrative introduction
            result = Runner.run_streamed(
                cupid_agent,
                input_items,
                context=agent_context,
            )

            async for event in stream_agent_response(agent_context, result):
                yield event

            # Stream ProfileCard widget for mortal character
            profilecard_widget = build_profilecard_widget(self.mortal_data)
            widget_item = WidgetItem(
                thread_id=thread.id,
                id=f"widget_{thread.id}_{datetime.now().timestamp()}",
                created_at=datetime.now(),
                widget=profilecard_widget,
                copy_text=f"{self.mortal_data['name']}, {self.mortal_data['age']}, {self.mortal_data['occupation']}",
            )
            yield ThreadItemDoneEvent(item=widget_item)

            # Increment chapter
            context["chapter"] = 2

        elif chapter == 2:
            # Chapter 2: Present Sam (match)
            # Run cupid agent for match introduction
            result = Runner.run_streamed(
                cupid_agent,
                input_items,
                context=agent_context,
            )

            async for event in stream_agent_response(agent_context, result):
                yield event

            # Stream ProfileCard widget for match character
            profilecard_widget = build_profilecard_widget(self.match_data)
            widget_item = WidgetItem(
                thread_id=thread.id,
                id=f"widget_{thread.id}_{datetime.now().timestamp()}",
                created_at=datetime.now(),
                widget=profilecard_widget,
                copy_text=f"{self.match_data['name']}, {self.match_data['age']}, {self.match_data['occupation']}",
            )
            yield ThreadItemDoneEvent(item=widget_item)

            # Increment chapter
            context["chapter"] = 3

        else:
            # Chapter 3+: Normal game conversation following instructions
            result = Runner.run_streamed(
                cupid_agent,
                input_items,
                context=agent_context,
            )

            async for event in stream_agent_response(agent_context, result):
                yield event

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported.")


def create_chatkit_server() -> CupidServer:
    """Return a configured ChatKit server instance."""
    return CupidServer()
