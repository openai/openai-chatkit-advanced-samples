"""Helpers that convert ChatKit thread items into model-friendly inputs."""

from __future__ import annotations

from chatkit.agents import ThreadItemConverter
from chatkit.types import HiddenContextItem, UserMessageTagContent
from openai.types.responses import ResponseInputTextParam
from openai.types.responses.response_input_item_param import Message

from .data.metro_map_store import MetroMapStore


class MetroMapThreadItemConverter(ThreadItemConverter):
    """Adds HiddenContextItem support and tags for metro references."""

    def __init__(self, metro_map_store: MetroMapStore):
        self.metro_map_store = metro_map_store

    async def hidden_context_to_input(self, item: HiddenContextItem):
        return Message(
            type="message",
            content=[
                ResponseInputTextParam(
                    type="input_text",
                    text=item.content,
                )
            ],
            role="user",
        )

    async def tag_to_message_content(
        self, tag: UserMessageTagContent
    ) -> ResponseInputTextParam:
        """Represent a tagged station so the agent can load it by id."""
        tag_data = tag.data or {}
        station_id = (tag_data.get("station_id") or tag.id or "").strip()
        station_name = (tag_data.get("name") or tag.text or station_id).strip()

        station = self.metro_map_store.find_station(station_id) if station_id else None
        if not station:
            return ResponseInputTextParam(
                type="input_text",
                text=f"Tagged station: {station_name} (not found)",
            )

        line_details: list[str] = []
        for line_id in station.lines:
            line = self.metro_map_store.find_line(line_id)
            if line:
                line_details.append(f"{line.name} ({line.id}, {line.color})")

        station_lines = ", ".join(line_details)
        text = "\n".join(
            [
                "Tagged station:",
                "<STATION_TAG>",
                f"id: {station.id}",
                f"name: {station.name}",
                f"lines: {station_lines}",
                "</STATION_TAG>",
            ]
        )
        return ResponseInputTextParam(
            type="input_text",
            text=text,
        )
