from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, AsyncIterator

from agents import RunConfig, Runner
from agents.model_settings import ModelSettings
from chatkit.agents import AgentContext, stream_agent_response
from chatkit.server import ChatKitServer, StreamingResult
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
from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputContentParam,
    ResponseInputTextParam,
)
from pydantic import ValidationError
from starlette.responses import JSONResponse

from .airline_state import AirlineStateManager, CustomerProfile
from .meal_preferences import (
    SET_MEAL_PREFERENCE_ACTION_TYPE,
    SetMealPreferencePayload,
    build_meal_preference_widget,
    meal_preference_label,
)
from .memory_store import MemoryStore
from .support_agent import state_manager, support_agent
from .thread_item_converter import CustomerSupportThreadItemConverter
from .title_agent import title_agent

DEFAULT_THREAD_ID = "demo_default_thread"
logger = logging.getLogger(__name__)


def _get_customer_profile_as_input_item(profile: CustomerProfile):
    segments = []
    for segment in profile.segments:
        segments.append(
            f"- {segment.flight_number} {segment.origin}->{segment.destination}"
            f" on {segment.date} seat {segment.seat} ({segment.status})"
        )
    summary = "\n".join(segments)
    timeline = profile.timeline[:3]
    recent = "\n".join(f"  * {entry['entry']} ({entry['timestamp']})" for entry in timeline)
    content = (
        "<CUSTOMER_PROFILE>\n"
        f"Name: {profile.name} ({profile.loyalty_status})\n"
        f"Loyalty ID: {profile.loyalty_id}\n"
        f"Contact: {profile.email}, {profile.phone}\n"
        f"Checked Bags: {profile.bags_checked}\n"
        f"Meal Preference: {profile.meal_preference or 'Not set'}\n"
        f"Special Assistance: {profile.special_assistance or 'None'}\n"
        "Upcoming Segments:\n"
        f"{summary}\n"
        "Recent Service Timeline:\n"
        f"{recent or '  * No service actions recorded yet.'}\n"
        "</CUSTOMER_PROFILE>"
    )

    return EasyInputMessageParam(
        type="message",
        role="user",
        content=[ResponseInputTextParam(type="input_text", text=content)],
    )


class CustomerSupportServer(ChatKitServer[dict[str, Any]]):
    def __init__(
        self,
        agent_state: AirlineStateManager,
    ) -> None:
        store = MemoryStore()
        super().__init__(store)
        self.store = store
        self.agent_state = agent_state
        self.agent = support_agent
        self.title_agent = title_agent
        self.thread_item_converter = CustomerSupportThreadItemConverter()

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        if action.type != SET_MEAL_PREFERENCE_ACTION_TYPE:
            return

        payload = self._parse_meal_preference_payload(action)
        if payload is None:
            return

        meal_label = meal_preference_label(payload.meal)
        self.agent_state.set_meal(thread.id, meal_label)

        if sender is not None:
            widget = build_meal_preference_widget(
                selected=payload.meal,
            )
            yield ThreadItemUpdated(
                item_id=sender.id,
                update=WidgetRootUpdated(widget=widget),
            )
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("message", thread, context),
                    created_at=datetime.now(),
                    content=[
                        AssistantMessageContent(
                            text=f'Your meal preference has been updated to "{meal_label}".'
                        )
                    ],
                ),
            )

            hidden = HiddenContextItem(
                id=self.store.generate_item_id("message", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=f"<WIDGET_ACTION widgetId={sender.id}>{action.type} was performed with payload: {payload.meal}</WIDGET_ACTION>",
            )
            await self.store.add_thread_item(thread.id, hidden, context)

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Load all items from the thread to send as agent input.
        # Needed to ensure that the agent is aware of the full conversation
        # when generating a response.
        items_page = await self.store.load_thread_items(thread.id, None, 20, "desc", context)
        updating_thread_title = asyncio.create_task(
            self.maybe_update_thread_title(thread, input_user_message)
        )
        items = list(reversed(items_page.data))  # Runner expects last message last

        # Prepend customer profile as part of the agent input
        profile = self.agent_state.get_profile(thread.id)
        profile_item = _get_customer_profile_as_input_item(profile)
        input_items = [profile_item] + (await self.thread_item_converter.to_agent_input(items))

        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )
        result = Runner.run_streamed(
            self.agent,
            input_items,
            context=agent_context,
            run_config=RunConfig(model_settings=ModelSettings(temperature=0.4)),
        )

        async for event in stream_agent_response(agent_context, result):
            yield event

        await updating_thread_title

    async def maybe_update_thread_title(
        self, thread: ThreadMetadata, user_message: UserMessageItem | None
    ) -> None:
        if user_message is None or thread.title is not None:
            return

        run = await Runner.run(
            title_agent,
            input=await self.thread_item_converter.to_agent_input(user_message),
        )
        model_result: str = run.final_output
        # Capitalize the first letter only
        model_result = model_result[:1].upper() + model_result[1:]
        thread.title = model_result.strip(".")

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported in this demo.")

    @staticmethod
    def _parse_meal_preference_payload(action: Action[str, Any]) -> SetMealPreferencePayload | None:
        try:
            return SetMealPreferencePayload.model_validate(action.payload or {})
        except ValidationError as exc:
            logger.warning("Invalid meal preference payload: %s", exc)
            return None


support_server = CustomerSupportServer(agent_state=state_manager)


app = FastAPI(title="ChatKit Customer Support API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_server() -> CustomerSupportServer:
    return support_server


@app.post("/support/chatkit")
async def chatkit_endpoint(
    request: Request, server: CustomerSupportServer = Depends(get_server)
) -> Response:
    payload = await request.body()
    result = await server.process(payload, {"request": request})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


def _thread_param(thread_id: str | None) -> str:
    return thread_id or DEFAULT_THREAD_ID


@app.get("/support/customer")
async def customer_snapshot(
    thread_id: str | None = Query(None, description="ChatKit thread identifier"),
    server: CustomerSupportServer = Depends(get_server),
) -> dict[str, Any]:
    key = _thread_param(thread_id)
    data = server.agent_state.to_dict(key)
    return {"customer": data}


@app.get("/support/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
