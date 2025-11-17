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
        tag_data = tag.data or {}
        tag_type = tag_data.get("type")

        if tag_type == "author":
            author_name = (tag_data.get("author") or tag.text).strip()
            author_id = (tag_data.get("author_id") or tag.id or "").strip()
            marker = f"<AUTHOR_REFERENCE>{author_id}</AUTHOR_REFERENCE>"
            text = f"Tagged author: {author_name}\n{marker}"
        else:
            display_title = tag_data.get("title") or tag.text
            article_id = (tag_data.get("article_id") or tag.id or "").strip()
            marker = f"<ARTICLE_REFERENCE>{article_id}</ARTICLE_REFERENCE>"
            text = f"Tagged article: {display_title}\n{marker}"
        return ResponseInputTextParam(
            type="input_text",
            text=text,
        )
