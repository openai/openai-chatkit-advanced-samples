"""ChatKit server wiring for the customer-support experience."""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime
from typing import Any, AsyncIterator, Callable

from agents import RunConfig, Runner
from agents.model_settings import ModelSettings
from chatkit.agents import AgentContext, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    Action,
    AssistantMessageContent,
    AssistantMessageItem,
    ClientEffectEvent,
    HiddenContextItem,
    ThreadItemDoneEvent,
    ThreadItemUpdated,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    WidgetItem,
    WidgetRootUpdated,
)
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputTextParam,
)
from pydantic import ValidationError

from .airline_state import AirlineStateManager, CustomerProfile
from .attachment_store import LocalAttachmentStore
from .flight_options import (
    FLIGHT_SELECT_ACTION_TYPE,
    FlightOption,
    FlightSearchRequest,
    FlightSelectPayload,
    build_flight_options_widget,
    describe_flight_option,
    generate_flight_options,
)
from .meal_preferences import (
    SET_MEAL_PREFERENCE_ACTION_TYPE,
    SetMealPreferencePayload,
    build_meal_preference_widget,
    meal_preference_label,
)
from .memory_store import MemoryStore
from .support_agent import build_support_agent, state_manager, support_agent
from .thread_item_converter import CustomerSupportThreadItemConverter
from .title_agent import title_agent

BOOKING_CONFIRM_ACTION_TYPE = "booking.confirm_selection"
BOOKING_MODIFY_ACTION_TYPE = "booking.modify_request"
UPSELL_ACCEPT_ACTION_TYPE = "upsell.accept"
UPSELL_DECLINE_ACTION_TYPE = "upsell.decline"
REBOOK_SELECT_ACTION_TYPE = "rebook.select_option"

logger = logging.getLogger(__name__)

ActionHandler = Callable[
    [ThreadMetadata, Action[str, Any], WidgetItem | None, dict[str, Any]],
    AsyncIterator[ThreadStreamEvent],
]


def _profile_to_input_item(profile: CustomerProfile) -> EasyInputMessageParam:
    """Render the customer profile into a single agent input message."""
    segments = [
        (
            f"- {segment.flight_number} {segment.origin}->"
            f"{segment.destination}"
            f" on {segment.date} seat {segment.seat} ({segment.status})"
        )
        for segment in profile.segments
    ]
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
    """ChatKit server that powers the customer-support demo."""

    def __init__(
        self,
        agent_state: AirlineStateManager | None = None,
        agent=None,
    ) -> None:
        store = MemoryStore()
        attachment_store = LocalAttachmentStore(store)
        super().__init__(store, attachment_store=attachment_store)
        self.store = store
        self._local_attachment_store = attachment_store
        self.agent_state = agent_state or state_manager
        if agent is not None:
            self.agent = agent
        elif self.agent_state is state_manager:
            self.agent = support_agent
        else:
            self.agent = build_support_agent(self.agent_state)
        self.title_agent = title_agent
        self.thread_item_converter = CustomerSupportThreadItemConverter(
            attachment_store=attachment_store
        )
        self._action_handlers: dict[str, ActionHandler] = {
            SET_MEAL_PREFERENCE_ACTION_TYPE: (self._handle_meal_preference_action),
            FLIGHT_SELECT_ACTION_TYPE: self._handle_flight_select_action,
            BOOKING_CONFIRM_ACTION_TYPE: self._handle_booking_confirm_action,
            BOOKING_MODIFY_ACTION_TYPE: self._handle_booking_modify_action,
            UPSELL_ACCEPT_ACTION_TYPE: self._handle_upgrade_accept_action,
            UPSELL_DECLINE_ACTION_TYPE: self._handle_upgrade_decline_action,
            REBOOK_SELECT_ACTION_TYPE: self._handle_rebook_action,
        }

    @property
    def attachment_uploader(self) -> LocalAttachmentStore:
        return self._local_attachment_store

    # -------------------------------------------------------------- Actions
    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        handler = self._action_handlers.get(action.type)
        if handler is None:
            return

        async for event in handler(thread, action, sender, context):
            yield event

    async def _handle_meal_preference_action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        payload = self._parse_meal_preference_payload(action)
        if payload is None:
            return

        meal_label = meal_preference_label(payload.meal)
        self.agent_state.set_meal(thread.id, meal_label)

        if sender is not None:
            widget = build_meal_preference_widget(selected=payload.meal)
            yield ThreadItemUpdated(
                item_id=sender.id,
                update=WidgetRootUpdated(widget=widget),
            )
            yield ThreadItemDoneEvent(
                item=self._assistant_message(
                    thread,
                    (f'Your meal preference has been updated to "{meal_label}".'),
                    context,
                ),
            )
            hidden = HiddenContextItem(
                id=self.store.generate_item_id("message", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=(
                    f"<WIDGET_ACTION widgetId={sender.id}>"
                    f"{action.type} payload: {payload.meal}</WIDGET_ACTION>"
                ),
            )
            await self.store.add_thread_item(thread.id, hidden, context)

        yield self._profile_effect(thread.id)

    async def _handle_flight_select_action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        payload = self._parse_flight_select_payload(action)
        if payload is None:
            return

        if sender is not None and self.agent_state.is_widget_consumed(thread.id, sender.id):
            return

        try:
            options = [FlightOption.model_validate(opt) for opt in payload.options]
        except ValidationError as exc:
            logger.warning("Invalid flight options in payload: %s", exc)
            options = []

        if not options:
            options = generate_flight_options(payload.request)

        selected = next((opt for opt in options if opt.id == payload.id), None)
        if selected is None:
            return

        depart_label = (
            f"{payload.request.depart_date} "
            f"{selected.from_airport}→{selected.to_airport} {selected.dep_time}"
        )
        return_label = (
            f"{payload.request.return_date} {payload.request.destination}→{payload.request.origin}"
        )

        self.agent_state.record_booking_hold(
            thread.id,
            payload.request.normalized_destination(),
            depart_label,
            return_label,
        )

        seat_assignment = _pick_default_seat(payload.request.cabin)
        booking = self.agent_state.record_flight_booking(
            thread.id,
            flight_number=_generate_flight_number(payload.leg),
            date=payload.request.depart_date,
            origin=payload.request.normalized_origin(),
            destination=payload.request.normalized_destination(),
            depart_time=selected.dep_time,
            arrival_time=selected.arr_time,
            status="Scheduled",
            seat=seat_assignment,
        )

        summary = describe_flight_option(selected, payload.request)
        action_text = (
            "You're scheduled on that option. I'll surface a few returns now."
            if payload.leg == "outbound"
            else "Return scheduled. Want me to watch for upgrades?"
        )
        yield ThreadItemDoneEvent(
            item=self._assistant_message(
                thread,
                (f"Scheduled: {summary}. Seat {booking.seat} for now; {action_text}"),
                context,
            ),
        )

        # Lock the current widget to the chosen option.
        if sender is not None:
            selected_widget = build_flight_options_widget(
                [selected],
                payload.request,
                selected_id=selected.id,
                leg=payload.leg,
            )
            yield ThreadItemUpdated(
                item_id=sender.id,
                update=WidgetRootUpdated(widget=selected_widget),
            )
            self.agent_state.mark_widget_consumed(thread.id, sender.id)

        if payload.leg == "outbound":
            return_request = FlightSearchRequest(
                origin=payload.request.normalized_destination(),
                destination=payload.request.normalized_origin(),
                depart_date=payload.request.return_date,
                return_date=payload.request.depart_date,
                cabin=payload.request.cabin,
            )
            return_options = generate_flight_options(return_request)
            yield ThreadItemDoneEvent(
                item=self._assistant_message(
                    thread,
                    "Here are return options that line up with your trip:",
                    context,
                ),
            )
            new_widget = build_flight_options_widget(
                return_options,
                return_request,
                leg="return",
            )
            return_widget_id = self.store.generate_item_id("message", thread, context)
            yield ThreadItemDoneEvent(
                item=WidgetItem(
                    thread_id=thread.id,
                    id=return_widget_id,
                    created_at=datetime.now(),
                    widget=new_widget,
                )
            )

        hidden = HiddenContextItem(
            id=self.store.generate_item_id("message", thread, context),
            thread_id=thread.id,
            created_at=datetime.now(),
            content=(
                f"<WIDGET_ACTION widgetId={sender.id if sender else 'unknown'}>"
                f"{action.type} payload: {payload.model_dump_json()}"
                "</WIDGET_ACTION>"
            ),
        )
        await self.store.add_thread_item(thread.id, hidden, context)

        yield self._profile_effect(thread.id)

    async def _handle_booking_confirm_action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        _sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        payload = action.payload or {}
        destination = payload.get("destination", "the trip")
        depart_label = payload.get("depart_label", "outbound flight")
        return_label = payload.get("return_label", "return flight")
        confirmation = self.agent_state.record_booking_hold(
            thread.id,
            destination,
            depart_label,
            return_label,
        )

        yield ThreadItemDoneEvent(
            item=self._assistant_message(
                thread,
                (
                    f"{confirmation} I’ll keep monitoring inventory and "
                    "let you know if something better opens."
                ),
                context,
            ),
        )
        yield self._profile_effect(thread.id)

    async def _handle_booking_modify_action(
        self,
        thread: ThreadMetadata,
        _action: Action[str, Any],
        _sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        yield ThreadItemDoneEvent(
            item=self._assistant_message(
                thread,
                (
                    "Happy to tweak the plan. Let me know what you'd like to "
                    "change and feel free to attach a new inspiration photo "
                    "if it helps."
                ),
                context,
            ),
        )

    async def _handle_upgrade_accept_action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        _sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        async for event in self._handle_upgrade_action(
            thread,
            action,
            context,
            accepted=True,
        ):
            yield event

    async def _handle_upgrade_decline_action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        _sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        async for event in self._handle_upgrade_action(
            thread,
            action,
            context,
            accepted=False,
        ):
            yield event

    async def _handle_upgrade_action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        context: dict[str, Any],
        *,
        accepted: bool,
    ) -> AsyncIterator[ThreadStreamEvent]:
        cabin = (action.payload or {}).get("cabin_name", "the upgrade")
        price = (action.payload or {}).get("price", "the quoted amount")
        if accepted:
            confirmation = self.agent_state.record_upgrade(
                thread.id,
                cabin,
                price,
            )
            yield ThreadItemDoneEvent(
                item=self._assistant_message(thread, confirmation, context),
            )
            yield self._profile_effect(thread.id)
            return

        yield ThreadItemDoneEvent(
            item=self._assistant_message(
                thread,
                (
                    "No worries—I'll keep the current cabin and continue "
                    f"helping with {cabin.lower()} availability."
                ),
                context,
            ),
        )

    async def _handle_rebook_action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        _sender: WidgetItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        payload = action.payload or {}
        flight_number = payload.get("flight_number")
        option_id = payload.get("option_id")
        depart_time = payload.get("depart_time")
        arrival_time = payload.get("arrival_time")
        note = payload.get("option_note", "Selected alternate time")
        if not flight_number or option_id is None:
            return

        if option_id == "keep":
            yield ThreadItemDoneEvent(
                item=self._assistant_message(
                    thread,
                    "Sounds good — we'll keep the original departure on file.",
                    context,
                ),
            )
            return

        try:
            confirmation = self.agent_state.rebook_segment(
                thread.id,
                flight_number,
                depart_time or "",
                arrival_time or "",
                note,
            )
        except ValueError as exc:
            confirmation = str(exc)

        yield ThreadItemDoneEvent(
            item=self._assistant_message(thread, confirmation, context),
        )
        yield self._profile_effect(thread.id)

    # ------------------------------------------------------------- Responses
    async def respond(
        self,
        thread: ThreadMetadata,
        user_message: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        title_task: asyncio.Task[None] | None = None
        if user_message is not None and thread.title is None:
            # Start title generation alongside the first assistant reply so it
            # does not delay streaming.
            title_task = asyncio.create_task(self._maybe_update_thread_title(thread, user_message))

        items_page = await self.store.load_thread_items(
            thread.id,
            None,
            20,
            "desc",
            context,
        )
        items = list(reversed(items_page.data))

        profile_item = _profile_to_input_item(self.agent_state.get_profile(thread.id))
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

        if title_task:
            await title_task

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

    # ------------------------------------------------------------- Attachments
    # ----------------------------------------------------------------- Helpers
    @staticmethod
    def _parse_meal_preference_payload(action: Action[str, Any]) -> SetMealPreferencePayload | None:
        try:
            return SetMealPreferencePayload.model_validate(action.payload or {})
        except ValidationError as exc:
            logger.warning("Invalid meal preference payload: %s", exc)
            return None

    @staticmethod
    def _parse_flight_select_payload(action: Action[str, Any]) -> FlightSelectPayload | None:
        try:
            return FlightSelectPayload.model_validate(action.payload or {})
        except ValidationError as exc:
            logger.warning("Invalid flight selection payload: %s", exc)
            return None

    def _assistant_message(
        self,
        thread: ThreadMetadata,
        text: str,
        context: dict[str, Any],
    ) -> AssistantMessageItem:
        return AssistantMessageItem(
            thread_id=thread.id,
            id=self.store.generate_item_id("message", thread, context),
            created_at=datetime.now(),
            content=[AssistantMessageContent(text=text)],
        )

    def _profile_effect(self, thread_id: str) -> ClientEffectEvent:
        return ClientEffectEvent(
            name="customer_profile/update",
            data={"profile": self.agent_state.to_dict(thread_id)},
        )


def create_chatkit_server() -> CustomerSupportServer:
    """Return a configured ChatKit server instance."""
    return CustomerSupportServer(
        agent_state=state_manager,
        agent=support_agent,
    )


def _generate_flight_number(leg: str) -> str:
    suffix = "1" if leg == "outbound" else "2"
    return f"OA9{suffix}7"


def _pick_default_seat(cabin: str) -> str:
    """Return a randomized seat assignment biased by fare class."""

    normalized = cabin.lower().strip()
    seat_letters = {
        "first": ["A", "D"],
        "business": ["A", "C", "D", "F"],
        "premium economy": list("ABCDEF"),
        "economy": list("ABCDEF"),
    }
    row_ranges = {
        "first": (1, 3),
        "business": (4, 9),
        "premium economy": (10, 19),
        "economy": (20, 45),
    }
    letters = seat_letters.get(normalized, list("ABCDEF"))
    start, end = row_ranges.get(normalized, (12, 38))
    row = random.randint(start, end)
    return f"{row}{random.choice(letters)}"
