"""
This is an example of a store for non-chatkit application data.
"""

from __future__ import annotations

import asyncio
from typing import Callable, Dict

from .cat_state import CatState


class CatStore:
    """Thread-safe in-memory store for cat state keyed by thread id."""

    def __init__(self) -> None:
        self._states: Dict[str, CatState] = {}
        self._lock = asyncio.Lock()

    def _ensure(self, thread_id: str) -> CatState:
        state = self._states.get(thread_id)
        if state is None:
            state = CatState()
            self._states[thread_id] = state
        return state

    async def load(self, thread_id: str) -> CatState:
        async with self._lock:
            return self._ensure(thread_id).clone()

    async def mutate(self, thread_id: str, mutator: Callable[[CatState], None]) -> CatState:
        async with self._lock:
            state = self._ensure(thread_id)
            mutator(state)
            return state.clone()
