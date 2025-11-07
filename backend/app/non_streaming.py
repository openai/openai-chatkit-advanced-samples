"""Utilities for converting streaming ChatKit responses to non-streaming format."""

from __future__ import annotations

from typing import Any

from chatkit.server import StreamingResult
from chatkit.types import (
    AssistantMessageItem,
    ErrorEvent,
    ThreadItemDoneEvent,
    ThreadStreamEvent,
)


class ChatKitCompleteResponse:
    """Complete (non-streaming) response from ChatKit."""

    def __init__(
        self,
        text: str,
        thread_id: str,
        message_id: str,
        error: str | None = None,
    ):
        self.text = text
        self.thread_id = thread_id
        self.message_id = message_id
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        result: dict[str, Any] = {
            "text": self.text,
            "thread_id": self.thread_id,
            "message_id": self.message_id,
        }
        if self.error:
            result["error"] = self.error
        return result


async def buffer_streaming_response(
    streaming_result: StreamingResult,
) -> ChatKitCompleteResponse:
    """
    Buffer all streaming events and extract the final complete response.

    This function collects all events from a StreamingResult and extracts
    the final assistant message text, making it suitable for non-streaming
    integrations like WhatsApp.

    Args:
        streaming_result: The streaming result from ChatKitServer.process()

    Returns:
        ChatKitCompleteResponse with the complete message text

    Raises:
        ValueError: If no assistant message was found in the response
    """
    events: list[ThreadStreamEvent] = []
    thread_id: str | None = None
    error_message: str | None = None

    # Collect all events
    async for event_bytes in streaming_result:
        # Parse the SSE event format
        # Events come as bytes in format: "event: <type>\ndata: <json>\n\n"
        event_str = event_bytes.decode("utf-8")

        # Extract the JSON data from SSE format
        lines = event_str.strip().split("\n")
        data_line = None
        for line in lines:
            if line.startswith("data: "):
                data_line = line[6:]  # Remove "data: " prefix
                break

        if not data_line:
            continue

        # Parse the event JSON
        import json
        from pydantic import TypeAdapter

        event_data = json.loads(data_line)
        event = TypeAdapter(ThreadStreamEvent).validate_python(event_data)
        events.append(event)

        # Track thread_id from thread.created or thread.updated events
        if hasattr(event, "thread") and hasattr(event.thread, "id"):
            thread_id = event.thread.id

        # Track errors
        if isinstance(event, ErrorEvent):
            error_message = event.message or "An error occurred"

    # Extract the final assistant message from ThreadItemDoneEvent
    assistant_message: AssistantMessageItem | None = None
    for event in events:
        if isinstance(event, ThreadItemDoneEvent):
            if isinstance(event.item, AssistantMessageItem):
                assistant_message = event.item
                thread_id = thread_id or event.item.thread_id

    # Build the complete response
    if assistant_message:
        # Combine all content parts into a single text string
        text_parts = []
        for content in assistant_message.content:
            text_parts.append(content.text)

        complete_text = "".join(text_parts)

        return ChatKitCompleteResponse(
            text=complete_text,
            thread_id=thread_id or assistant_message.thread_id,
            message_id=assistant_message.id,
            error=error_message,
        )

    # If no assistant message was found, return error
    if error_message:
        return ChatKitCompleteResponse(
            text="",
            thread_id=thread_id or "unknown",
            message_id="error",
            error=error_message,
        )

    raise ValueError(
        "No assistant message found in streaming response. "
        "This may indicate an error in the response generation."
    )
