from __future__ import annotations

from datetime import datetime
from typing import Annotated

from agents import Agent, RunContextWrapper, StopAtTools, function_tool
from chatkit.agents import AgentContext, ClientToolCall
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    ProgressUpdateEvent,
    ThreadItemDoneEvent,
)
from pydantic import BaseModel, ConfigDict, Field

from ..data.metro_map_store import Line, MetroMap, MetroMapStore, Station
from ..memory_store import MemoryStore
from ..request_context import RequestContext

INSTRUCTIONS = """
    You are a concise metro planner helping city planners update the Orbital Transit map.
    Give short answers, list 2–3 options, and highlight the lines or interchanges involved.

    Before recommending a route, sync the latest map with the provided tools. Cite line
    colors when helpful (e.g., "take Red then Blue at Central Exchange").

    When the user asks what to do next, reply with 2 concise follow-up ideas and pick one to lead with.
    Default to actionable options like adding another station on the same line or explaining how to travel
    from the newly added station to a nearby destination.

    When a user wants to add a station:
    - If the user did not specify a line, ask them to choose one from the list of lines.
    - If the user did not specify a station name, ask them to enter a name.
    - If the user did not specify whether to add the station to the end of the line or the beginning, ask them to choose one.
    - When you have all the information you need, call the `add_station` tool with the station name, line id, and append flag.

    When a user wants to plan a route:
    - If the user did not specify a starting or detination station, ask them to choose them from the list of stations.
    - Provide a one-sentence route, the estimated travel time, and points of interest along the way.
    - Avoid over-explaining and stay within the given station list.
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


class StationAddResult(BaseModel):
    station: Station
    line: Line
    map: MetroMap


@function_tool(
    description_override="Load the latest metro map with lines and stations."
)
async def get_map(ctx: RunContextWrapper[MetroAgentContext]) -> MapResult:
    metro_map = ctx.context.metro.get_map()
    await ctx.context.stream(
        ProgressUpdateEvent(
            text=f"Synced {metro_map.name} with {len(metro_map.lines)} lines."
        )
    )
    return MapResult(map=metro_map)


@function_tool(
    description_override="List all metro lines with their colors and endpoints."
)
async def list_lines(ctx: RunContextWrapper[MetroAgentContext]) -> LineListResult:
    return LineListResult(lines=ctx.context.metro.list_lines())


@function_tool(description_override="List all stations and which lines serve them.")
async def list_stations(ctx: RunContextWrapper[MetroAgentContext]) -> StationListResult:
    return StationListResult(stations=ctx.context.metro.list_stations())


@function_tool(description_override="Get the ordered stations for a specific line.")
async def get_line_route(
    ctx: RunContextWrapper[MetroAgentContext],
    line_id: str,
) -> LineDetailResult:
    line = ctx.context.metro.find_line(line_id)
    if not line:
        raise ValueError(f"Line '{line_id}' was not found.")
    stations = ctx.context.metro.stations_for_line(line_id)
    return LineDetailResult(line=line, stations=stations)


@function_tool(
    description_override="Look up a single station and the lines serving it."
)
async def get_station(
    ctx: RunContextWrapper[MetroAgentContext],
    station_id: str,
) -> StationDetailResult:
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
        updated_map = ctx.context.metro.add_station(station_name, line_id, append)
        ctx.context.client_tool_call = ClientToolCall(
            name="update_map",
            arguments={"map": updated_map.model_dump(mode="json")},
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
                            text=f"There was an error adding _{station_name}_, {e.message}"
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
        # Retrieval tools
        get_map,
        list_lines,
        list_stations,
        get_line_route,
        get_station,
        # Tools to update the map
        add_station,
    ],
    # Stop inference after client tool call
    tool_use_behavior=StopAtTools(stop_at_tool_names=[add_station.name]),
)
