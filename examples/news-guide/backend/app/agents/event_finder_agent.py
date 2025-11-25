from __future__ import annotations

import logging
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INSTRUCTIONS = """
    You help Foxhollow residents discover local happenings. When a reader asks for events,
    search the curated calendar, call out dates and notable details, and keep recommendations brief.

    Use the available tools deliberately:
      - Call `list_available_event_keywords` to get the full set of event keywords and categories,
        fuzzy match the reader's phrasing to the closest options (case-insensitive, partial matches are ok),
        then feed those terms into a keyword search instead of relying on hard-coded synonyms.
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


class EventKeywords(BaseModel):
    keywords: List[str]


@function_tool(
    description_override="Find scheduled events happening on a specific date (YYYY-MM-DD)."
)
async def search_events_by_date(
    ctx: RunContextWrapper[EventFinderContext],
    date: str,
) -> dict[str, Any]:
    logger.info("[TOOL CALL] search_events_by_date", date)
    if not date:
        raise ValueError("Provide a valid date in YYYY-MM-DD format.")
    await ctx.context.stream(ProgressUpdateEvent(text=f"Looking up events on {date}"))
    records = ctx.context.events.search_by_date(date)
    return {"events": _events_to_json(records)}


@function_tool(description_override="List events occurring on a given day of the week.")
async def search_events_by_day_of_week(
    ctx: RunContextWrapper[EventFinderContext],
    day: str,
) -> dict[str, Any]:
    logger.info("[TOOL CALL] search_events_by_day_of_week", day)
    if not day:
        raise ValueError("Provide a day of the week to search for (e.g., Saturday).")
    await ctx.context.stream(ProgressUpdateEvent(text=f"Checking {day} events"))
    records = ctx.context.events.search_by_day_of_week(day)
    return {"events": _events_to_json(records)}


@function_tool(
    description_override="Search events with general keywords (title, category, location, or details)."
)
async def search_events_by_keyword(
    ctx: RunContextWrapper[EventFinderContext],
    keywords: List[str],
) -> dict[str, Any]:
    logger.info("[TOOL CALL] search_events_by_keyword", keywords)
    tokens = [keyword.strip() for keyword in keywords if keyword and keyword.strip()]
    if not tokens:
        raise ValueError("Provide at least one keyword to search for.")
    label = ", ".join(tokens)
    await ctx.context.stream(ProgressUpdateEvent(text=f"Searching for: {label}"))
    records = ctx.context.events.search_by_keyword(tokens)
    return {"events": _events_to_json(records)}


@function_tool(description_override="List all unique event keywords and categories.")
async def list_available_event_keywords(
    ctx: RunContextWrapper[EventFinderContext],
) -> EventKeywords:
    logger.info("[TOOL CALL] list_available_event_keywords")
    await ctx.context.stream(ProgressUpdateEvent(text="Referencing available event keywords..."))
    return EventKeywords(keywords=ctx.context.events.list_available_keywords())


@function_tool(description_override="Show a timeline-styled widget for a provided set of events.")
async def show_event_list_widget(
    ctx: RunContextWrapper[EventFinderContext],
    events: List[EventRecord],
    message: str | None = None,
):
    logger.info("[TOOL CALL] show_event_list_widget", events)
    records: List[EventRecord] = [event for event in events if event]

    # Gracefully handle case where agent mistakenly calls this tool with no events.
    # Otherewise, since the agent is configured to stop running after this tool call, the user
    # will never see further output.
    if not records:
        fallback = message or "I couldn't find any events that match that search."
        await ctx.context.stream(
            ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=ctx.context.thread.id,
                    id=ctx.context.generate_id("message"),
                    created_at=datetime.now(),
                    content=[AssistantMessageContent(text=fallback)],
                ),
            )
        )

    try:
        widget = build_event_list_widget(records)
    except Exception as exc:
        logger.error(f"[ERROR] build_event_list_widget: {exc}")
        raise
    copy_text = ", ".join(filter(None, (event.title for event in records)))
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


def _events_to_json(events: List[EventRecord]) -> List[dict[str, Any]]:
    """Convert EventRecord models to JSON-safe dicts for tool responses."""
    return [event.model_dump(mode="json", by_alias=True) for event in events]


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
        list_available_event_keywords,
        show_event_list_widget,
    ],
    # Stop inference after showing the event list widget to prevent content from being repeated in a continued response.
    tool_use_behavior=StopAtTools(stop_at_tool_names=[show_event_list_widget.name]),
)
