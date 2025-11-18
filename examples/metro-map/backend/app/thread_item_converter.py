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

    async def tag_to_message_content(self, tag: UserMessageTagContent) -> ResponseInputTextParam:
        """
        Represent a tagged station or line in the model input so the agent can load it by id.
        """
        tag_data = tag.data or {}
        tag_type = tag_data.get("type")

        if tag_type == "line":
            line_id = (tag_data.get("line_id") or tag.id or "").strip()
            line = self.metro_map_store.find_line(line_id) if line_id else None
            line_name = (tag_data.get("label") or tag.text or line_id).strip()
            line_color = f"color: {line.color}" if line and getattr(line, "color", None) else None
            marker = f"<LINE_REFERENCE>{line_id}</LINE_REFERENCE>"
            details = "\n".join(
                part for part in [f"id: {line_id}", f"name: {line_name}", line_color, marker] if part
            )
            text = f"Tagged line:\n{details}"
        else:
            station_id = (tag_data.get("station_id") or tag.id or "").strip()
            station = self.metro_map_store.find_station(station_id) if station_id else None
            station_name = (tag_data.get("name") or tag.text or station_id).strip()
            line_details: list[str] = []
            if station:
                for line_id in station.lines:
                    line = self.metro_map_store.find_line(line_id)
                    if not line:
                        continue
                    line_details.append(f"{line.name} ({line.id}, {line.color})")
            else:
                line_names = (tag_data.get("line_names") or "").strip()
                if line_names:
                    line_details.append(line_names)

            station_lines = ", ".join(line_details) if line_details else None
            coordinates = f"coordinates: ({station.x}, {station.y})" if station else None
            parts = [
                "Tagged station:",
                "<STATION_TAG>",
                f"id: {station_id}" if station_id else None,
                f"name: {station_name}" if station_name else None,
                f"lines: {station_lines}" if station_lines else None,
                coordinates,
                "</STATION_TAG>",
            ]
            text = "\n".join(part for part in parts if part)
        return ResponseInputTextParam(
            type="input_text",
            text=text,
        )
