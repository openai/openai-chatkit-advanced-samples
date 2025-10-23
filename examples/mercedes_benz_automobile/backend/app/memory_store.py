"""In-memory store implementation for Mercedes-Benz automobile assistant."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from chatkit.server import Store
from chatkit.types import Page, ThreadItem, ThreadMetadata


@dataclass
class _ThreadState:
    """Internal thread state storage."""

    metadata: ThreadMetadata
    items: list[ThreadItem]


class MemoryStore(Store[dict[str, Any]]):
    """Simple in-memory implementation of the ChatKit Store interface."""

    def __init__(self) -> None:
        self._threads: dict[str, _ThreadState] = {}

    async def load_thread(
        self, thread_id: str, context: dict[str, Any]
    ) -> ThreadMetadata | None:
        """Load thread metadata."""
        state = self._threads.get(thread_id)
        return state.metadata if state else None

    async def save_thread(
        self, thread: ThreadMetadata, context: dict[str, Any]
    ) -> None:
        """Save thread metadata."""
        if thread.id not in self._threads:
            self._threads[thread.id] = _ThreadState(
                metadata=thread,
                items=[],
            )
        else:
            self._threads[thread.id].metadata = thread

    async def delete_thread(self, thread_id: str, context: dict[str, Any]) -> None:
        """Delete a thread."""
        self._threads.pop(thread_id, None)

    async def load_thread_items(
        self,
        thread_id: str,
        limit: int,
        offset: int,
        context: dict[str, Any],
    ) -> Page[ThreadItem]:
        """Load thread items with pagination."""
        state = self._threads.get(thread_id)
        if not state:
            return Page(items=[], total=0, limit=limit, offset=offset)

        items = state.items
        total = len(items)
        page_items = items[offset : offset + limit]

        return Page(items=page_items, total=total, limit=limit, offset=offset)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: dict[str, Any]
    ) -> None:
        """Add an item to a thread."""
        if thread_id not in self._threads:
            thread = ThreadMetadata(id=thread_id)
            self._threads[thread_id] = _ThreadState(
                metadata=thread,
                items=[],
            )

        self._threads[thread_id].items.append(item)

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: dict[str, Any]
    ) -> None:
        """Delete an item from a thread."""
        state = self._threads.get(thread_id)
        if state:
            state.items = [item for item in state.items if item.id != item_id]
