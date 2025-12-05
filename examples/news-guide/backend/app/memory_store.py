"""
Simple in-memory store compatible with the ChatKit Store interface.
A production app would implement this using a persistant database.
"""

from __future__ import annotations

from collections import defaultdict

from chatkit.store import NotFoundError, Store
from chatkit.types import Attachment, Page, ThreadItem, ThreadMetadata

from .request_context import RequestContext


class MemoryStore(Store[RequestContext]):
    def __init__(self):
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, list[ThreadItem]] = defaultdict(list)

    async def load_thread(self, thread_id: str, context: RequestContext) -> ThreadMetadata:
        if thread_id not in self.threads:
            raise NotFoundError(f"Thread {thread_id} not found")
        return self.threads[thread_id]

    async def save_thread(self, thread: ThreadMetadata, context: RequestContext) -> None:
        self.threads[thread.id] = thread

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: RequestContext
    ) -> Page[ThreadMetadata]:
        threads = list(self.threads.values())
        return self._paginate(
            threads, after, limit, order, sort_key=lambda t: t.created_at, cursor_key=lambda t: t.id
        )

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: RequestContext
    ) -> Page[ThreadItem]:
        items = self.items.get(thread_id, [])
        return self._paginate(
            items, after, limit, order, sort_key=lambda i: i.created_at, cursor_key=lambda i: i.id
        )

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: RequestContext
    ) -> None:
        self.items[thread_id].append(item)

    async def save_item(self, thread_id: str, item: ThreadItem, context: RequestContext) -> None:
        items = self.items[thread_id]
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item
                return
        items.append(item)

    async def load_item(self, thread_id: str, item_id: str, context: RequestContext) -> ThreadItem:
        for item in self.items.get(thread_id, []):
            if item.id == item_id:
                return item
        raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")

    async def delete_thread(self, thread_id: str, context: RequestContext) -> None:
        self.threads.pop(thread_id, None)
        self.items.pop(thread_id, None)

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> None:
        self.items[thread_id] = [
            item for item in self.items.get(thread_id, []) if item.id != item_id
        ]

    def _paginate(
        self, rows: list, after: str | None, limit: int, order: str, sort_key, cursor_key
    ):
        sorted_rows = sorted(rows, key=sort_key, reverse=order == "desc")
        start = 0
        if after:
            for idx, row in enumerate(sorted_rows):
                if cursor_key(row) == after:
                    start = idx + 1
                    break
        data = sorted_rows[start : start + limit]
        has_more = start + limit < len(sorted_rows)
        next_after = cursor_key(data[-1]) if has_more and data else None
        return Page(data=data, has_more=has_more, after=next_after)

    # Attachments are not implemented in the quickstart store

    async def save_attachment(self, attachment: Attachment, context: RequestContext) -> None:
        raise NotImplementedError()

    async def load_attachment(self, attachment_id: str, context: RequestContext) -> Attachment:
        raise NotImplementedError()

    async def delete_attachment(self, attachment_id: str, context: RequestContext) -> None:
        raise NotImplementedError()
