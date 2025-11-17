from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, List

from agents import Agent, RunContextWrapper, StopAtTools, function_tool
from chatkit.agents import AgentContext
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    ProgressUpdateEvent,
    ThreadItemDoneEvent,
)
from pydantic import BaseModel, ConfigDict, Field

from ..data.event_store import EventRecord, EventStore
from ..memory_store import MemoryStore
from ..request_context import RequestContext
from ..widgets.event_list_widget import build_event_list_widget

INSTRUCTIONS = """
    You help Foxhollow residents discover local happenings. When a reader asks for events,
    search the curated calendar, call out dates and notable details, and keep recommendations brief.

    Use the available tools deliberately:
      - If they mention a specific date (YYYY-MM-DD), start with `search_events_by_date`.
      - If they reference a day of the week, try `search_events_by_day_of_week`.
      - For general vibes (e.g., “family friendly night markets”), use `search_events_by_keyword`
        so the search spans titles, categories, locations, and curated keywords.

    Whenever a search tool returns more than one event immediately call `show_event_list_widget`
    with those results before sending your final text, along with a 1-sentence message explaining why these events were selected.
    This ensures every response ships with the timeline widget.
    Cite event titles in bold, mention the date, and highlight one delightful detail when replying.

    When the user explicitly asks for more details on the events, you MUST describe the events in natural language
    without using the `show_event_list_widget` tool.
"""

MODEL = "gpt-4.1-mini"


class EventFinderContext(AgentContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    store: Annotated[MemoryStore, Field(exclude=True)]
    events: Annotated[EventStore, Field(exclude=True)]
    request_context: Annotated[RequestContext, Field(exclude=True, default_factory=RequestContext)]


class EventWidgetEntry(BaseModel):
    """Schema for events passed to the widget tool."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    title: str
    date: str
    day_of_week: str = Field(alias="dayOfWeek")
    time: str
    location: str
    details: str
    category: str
    keywords: List[str] = Field(default_factory=list)


@function_tool(
    description_override="Find scheduled events happening on a specific date (YYYY-MM-DD)."
)
async def search_events_by_date(
    ctx: RunContextWrapper[EventFinderContext],
    date: str,
) -> dict[str, Any]:
    print("[TOOL CALL] search_events_by_date", date)
    normalized = date.strip()
    if not normalized:
        raise ValueError("Provide a valid date in YYYY-MM-DD format.")
    await ctx.context.stream(ProgressUpdateEvent(text=f"Looking up events on {normalized}"))
    records = ctx.context.events.search_by_date(normalized)
    return {"events": records}


@function_tool(description_override="List events occurring on a given day of the week.")
async def search_events_by_day_of_week(
    ctx: RunContextWrapper[EventFinderContext],
    day: str,
) -> dict[str, Any]:
    print("[TOOL CALL] search_events_by_day_of_week", day)
    normalized = day.strip()
    if not normalized:
        raise ValueError("Provide a day of the week to search for (e.g., Saturday).")
    await ctx.context.stream(ProgressUpdateEvent(text=f"Checking {normalized} events"))
    records = ctx.context.events.search_by_day_of_week(normalized)
    return {"events": records}


@function_tool(
    description_override="Search events with general keywords (title, category, location, or details)."
)
async def search_events_by_keyword(
    ctx: RunContextWrapper[EventFinderContext],
    keywords: List[str],
) -> dict[str, Any]:
    print("[TOOL CALL] search_events_by_keyword", keywords)
    tokens = [keyword.strip() for keyword in keywords if keyword and keyword.strip()]
    if not tokens:
        raise ValueError("Provide at least one keyword to search for.")
    label = ", ".join(tokens)
    await ctx.context.stream(ProgressUpdateEvent(text=f"Searching for: {label}"))
    records = ctx.context.events.search_by_keyword(tokens)
    return {"events": records}


@function_tool(description_override="Show a timeline-styled widget for a provided set of events.")
async def show_event_list_widget(
    ctx: RunContextWrapper[EventFinderContext],
    events: List[EventWidgetEntry],
    message: str | None = None,
) -> dict[str, Any]:
    print("[TOOL CALL] show_event_list_widget", events)
    normalized: List[dict[str, Any]] = [
        event.model_dump(by_alias=True) for event in events if event
    ]
    if not normalized:
        raise ValueError("Provide at least one event before calling this tool.")

    widget = build_event_list_widget(normalized)
    copy_text = ", ".join(filter(None, (_event_title(event) for event in normalized)))
    await ctx.context.stream_widget(widget, copy_text=copy_text or "Local events")

    summary = message or "Here are the events that match your request."
    await ctx.context.stream(
        ThreadItemDoneEvent(
            item=AssistantMessageItem(
                thread_id=ctx.context.thread.id,
                id=ctx.context.generate_id("message"),
                created_at=datetime.now(),
                content=[AssistantMessageContent(text=summary)],
            ),
        )
    )
    return {"events": normalized}


def _event_title(event: EventRecord | dict[str, Any]) -> str | None:
    if isinstance(event, EventRecord):
        return event.title
    if isinstance(event, dict):
        title = event.get("title")
        return str(title) if title else None


class EventSummaryContext(AgentContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    store: Annotated[MemoryStore, Field(exclude=True)]
    events: Annotated[EventStore, Field(exclude=True)]
    request_context: Annotated[RequestContext, Field(exclude=True, default_factory=RequestContext)]


event_finder_agent = Agent[EventFinderContext](
    model=MODEL,
    name="Foxhollow Event Finder",
    instructions=INSTRUCTIONS,
    tools=[
        search_events_by_date,
        search_events_by_day_of_week,
        search_events_by_keyword,
        show_event_list_widget,
    ],
    # Stop inference after showing the event list widget to prevent content from being repeated in a continued response.
    tool_use_behavior=StopAtTools(stop_at_tool_names=[show_event_list_widget.name]),
)
