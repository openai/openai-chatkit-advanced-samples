from __future__ import annotations

from datetime import datetime
from typing import Annotated

from agents import Agent, RunContextWrapper, StopAtTools, function_tool
from chatkit.agents import AgentContext, ClientToolCall
from chatkit.types import (
    Annotation,
    AssistantMessageContent,
    AssistantMessageItem,
    EntitySource,
    ProgressUpdateEvent,
    ThreadItemDoneEvent,
)
from pydantic import BaseModel, ConfigDict, Field

from ..data.metro_map_store import Line, MetroMap, MetroMapStore, Station
from ..memory_store import MemoryStore
from ..request_context import RequestContext
from ..widgets.line_select_widget import build_line_select_widget

INSTRUCTIONS = """
    You are a concise metro planner helping city planners update the Orbital Transit map.
    Give short answers, list 2–3 options, and highlight the lines or interchanges involved.

    Before recommending a route, sync the latest map with the provided tools. Cite line
    colors when helpful (e.g., "take Red then Blue at Central Exchange").

    When the user asks what to do next, reply with 2 concise follow-up ideas and pick one to lead with.
    Default to actionable options like adding another station on the same line or explaining how to travel
    from the newly added station to a nearby destination.

    When the user mentions a station, always call the `get_map` tool to sync the latest map before responding.

    When a user wants to add a station (e.g. "I would like to add a new metro station." or "Add another station"):
    - If the user did not specify a line, you MUST call `show_line_selector` with a message prompting them to choose one
      from the list of lines. You must NEVER ask the user to choose a line without calling `show_line_selector` first.
      This applies even if you just added a station—treat each new "add a station" turn as needing a fresh line selection
      unless the user explicitly included the line in that same turn or in the latest message via <LINE_SELECTED>.
    - If the user replies with a number to pick one of your follow-up options AND that option involves adding a station,
      treat this as a fresh station-add request and immediately call `show_line_selector` before asking anything else.
    - If the user did not specify a station name, ask them to enter a name.
    - If the user did not specify whether to add the station to the end of the line or the beginning, ask them to choose one.
    - When you have all the information you need, call the `add_station` tool with the station name, line id, and append flag.

    Describing:
    - After a new station has been added, describe it to the user in a whimsical and poetic sentence.
    - When describing a station to the user, omit the station id and coordinates.
    - When describing a line to the user, omit the line id and color.

    When a user wants to plan a route:
    - If the user did not specify a starting or detination station, ask them to choose them from the list of stations.
    - You MUST call the `plan_route` tool with the list of stations in the route and a one-sentence message describing the route.
    - The message describing the route should include the estimated travel time in light years (e.g. "10.6 light years"),
      and points of interest along the way.
    - Avoid over-explaining and stay within the given station list.

    Every time your response mentions a list of stations (e.g. "the stations on the Blue Line are..." or "to get from Titan Border to
    Lyra Verge..."), you MUST call the `cite_stations_for_route` tool with the list of stations.

    Custom tags:
    - <LINE_SELECTED>{line_id}</LINE_SELECTED> - when the user has selected a line, you can use this tag to reference the line id.
      When this is the latest message, acknowledge the selection.
    - <STATION_TAG>...</STATION_TAG> - contains full station details (id, name, description, coordinates, and served lines with ids/colors/orientations).
      Use the data inside the tag directly; do not call `get_station` just to resolve a tagged station.
"""


class MetroAgentContext(AgentContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    store: Annotated[MemoryStore, Field(exclude=True)]
    metro: Annotated[MetroMapStore, Field(exclude=True)]
    request_context: Annotated[RequestContext, Field(exclude=True)]


class MapResult(BaseModel):
    map: MetroMap


class LineListResult(BaseModel):
    lines: list[Line]


class StationListResult(BaseModel):
    stations: list[Station]


class LineDetailResult(BaseModel):
    line: Line
    stations: list[Station]


class StationDetailResult(BaseModel):
    station: Station
    lines: list[Line]


@function_tool(description_override="Show a clickable widget listing metro lines.")
async def show_line_selector(ctx: RunContextWrapper[MetroAgentContext], message: str):
    widget = build_line_select_widget(ctx.context.metro.list_lines())
    await ctx.context.stream(
        ThreadItemDoneEvent(
            item=AssistantMessageItem(
                thread_id=ctx.context.thread.id,
                id=ctx.context.generate_id("message"),
                created_at=datetime.now(),
                content=[AssistantMessageContent(text=message)],
            ),
        )
    )
    await ctx.context.stream_widget(widget)


@function_tool(description_override="Load the latest metro map with lines and stations.")
async def get_map(ctx: RunContextWrapper[MetroAgentContext]) -> MapResult:
    print("[TOOL CALL] get_map")
    metro_map = ctx.context.metro.get_map()
    await ctx.context.stream(ProgressUpdateEvent(text="Retrieving the latest metro map..."))
    return MapResult(map=metro_map)


@function_tool(description_override="List all metro lines with their colors and endpoints.")
async def list_lines(ctx: RunContextWrapper[MetroAgentContext]) -> LineListResult:
    print("[TOOL CALL] list_lines")
    return LineListResult(lines=ctx.context.metro.list_lines())


@function_tool(description_override="List all stations and which lines serve them.")
async def list_stations(ctx: RunContextWrapper[MetroAgentContext]) -> StationListResult:
    print("[TOOL CALL] list_stations")
    return StationListResult(stations=ctx.context.metro.list_stations())


@function_tool(description_override="Show the user the planned route.")
async def plan_route(
    ctx: RunContextWrapper[MetroAgentContext],
    route: list[Station],
    message: str,
):
    print("[TOOL CALL] plan_route", route)
    sources = [
        EntitySource(
            id=station.id,
            icon="map-pin",
            title=station.name,
            description=station.description,
            data={"type": "station", "station_id": station.id, "name": station.name},
        )
        for station in route
    ]

    await ctx.context.stream(
        ThreadItemDoneEvent(
            item=AssistantMessageItem(
                thread_id=ctx.context.thread.id,
                id=ctx.context.generate_id("message"),
                created_at=datetime.now(),
                content=[
                    AssistantMessageContent(
                        text=message,
                        annotations=[Annotation(source=source, index=0) for source in sources],
                    )
                ],
            )
        )
    )


@function_tool(description_override="Look up a single station and the lines serving it.")
async def get_station(
    ctx: RunContextWrapper[MetroAgentContext],
    station_id: str,
) -> StationDetailResult:
    print("[TOOL CALL] get_station", station_id)
    station = ctx.context.metro.find_station(station_id)
    if not station:
        raise ValueError(f"Station '{station_id}' was not found.")
    lines = [ctx.context.metro.find_line(line_id) for line_id in station.lines]
    return StationDetailResult(
        station=station,
        lines=[line for line in lines if line],
    )


@function_tool(
    description_override=(
        """Add a new station to the metro map.
        - `station_name`: The name of the station to add.
        - `line_id`: The id of the line to add the station to. Should be one of the ids returned by list_lines.
        - `append`: Whether to add the station to the end of the line or the beginning. Defaults to True.
        """
    )
)
async def add_station(
    ctx: RunContextWrapper[MetroAgentContext],
    station_name: str,
    line_id: str,
    append: bool = True,
) -> MapResult:
    station_name = station_name.strip().title()
    print(f"[TOOL CALL] add_station: {station_name} to {line_id}")
    await ctx.context.stream(ProgressUpdateEvent(text="Adding station..."))
    try:
        updated_map, new_station = ctx.context.metro.add_station(station_name, line_id, append)
        ctx.context.client_tool_call = ClientToolCall(
            name="add_station",
            arguments={
                "stationId": new_station.id,
                "map": updated_map.model_dump(mode="json"),
            },
        )
        return MapResult(map=updated_map)
    except Exception as e:
        print(f"[ERROR] add_station: {e}")
        await ctx.context.stream(
            ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=ctx.context.thread.id,
                    id=ctx.context.generate_id("message"),
                    created_at=datetime.now(),
                    content=[
                        AssistantMessageContent(
                            text=f"There was an error adding **{station_name}**"
                        )
                    ],
                ),
            )
        )
        raise


metro_map_agent = Agent[MetroAgentContext](
    name="metro_map",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[
        # Retrieve map data
        get_map,
        list_lines,
        list_stations,
        get_station,
        # Response with entity sources
        plan_route,
        # Respond with a widget
        show_line_selector,
        # Update the metro map
        add_station,
    ],
    # Stop inference after client tool call or widget output
    tool_use_behavior=StopAtTools(
        stop_at_tool_names=[
            add_station.name,
            show_line_selector.name,
        ]
    ),
)
