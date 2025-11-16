"""Helpers that convert ChatKit thread items into model-friendly inputs."""

from __future__ import annotations

from chatkit.agents import ThreadItemConverter
from chatkit.types import HiddenContextItem, UserMessageTagContent
from openai.types.responses import ResponseInputTextParam
from openai.types.responses.response_input_item_param import Message


class NewsGuideThreadItemConverter(ThreadItemConverter):
    """Adds support for hidden context and @-mention tags."""

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
        Represent a tagged article in the model input so the agent can load it by id.
        """
        display_title = tag.text

        marker = f"<ARTICLE_REFERENCE>{tag.id}</ARTICLE_REFERENCE>"
        text = f"Tagged article: {display_title}\n{marker}"
        return ResponseInputTextParam(
            type="input_text",
            text=text,
        )
