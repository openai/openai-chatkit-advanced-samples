"""Helpers that convert ChatKit thread items into model-friendly inputs."""

from __future__ import annotations

from chatkit.agents import ThreadItemConverter
from chatkit.types import HiddenContextItem, UserMessageTagContent
from openai.types.responses import ResponseInputTextParam
from openai.types.responses.response_input_item_param import Message


class MetroMapThreadItemConverter(ThreadItemConverter):
    """Adds HiddenContextItem support and tags for metro references."""

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
            line_name = tag_data.get("label") or tag.text or line_id
            marker = f"<LINE_REFERENCE>{line_id}</LINE_REFERENCE>"
            text = f"Tagged line: {line_name}\n{marker}"
        else:
            station_id = (tag_data.get("station_id") or tag.id or "").strip()
            station_name = tag.text or station_id
            marker = f"<STATION_REFERENCE>{station_id}</STATION_REFERENCE>"
            text = f"Tagged station: {station_name}\n{marker}"
        return ResponseInputTextParam(
            type="input_text",
            text=text,
        )
