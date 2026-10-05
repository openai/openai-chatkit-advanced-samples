"""Offline regressions for streamed flight selections.

Run from this backend directory with:
    python -m unittest discover -s tests -p 'test_booking_idempotency.py'
"""

from __future__ import annotations

import os
import unittest
from datetime import UTC, datetime
from unittest.mock import patch

# Construct the sample's client without reading credentials or making API calls.
with patch.dict(os.environ, {"OPENAI_API_KEY": "synthetic-test-key"}):
    from app.airline_state import AirlineStateManager
    from app.flight_options import (
        FlightSearchRequest,
        build_flight_options_widget,
        generate_flight_options,
    )
    from app.server import CustomerSupportServer
    from chatkit.types import Action, ThreadMetadata, WidgetItem


class BookingIdempotencyTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.state = AirlineStateManager()
        self.server = CustomerSupportServer(agent_state=self.state, agent=object())
        self.thread = ThreadMetadata(
            id="synthetic-thread", created_at=datetime(2026, 1, 1, tzinfo=UTC)
        )
        request = FlightSearchRequest(
            origin="LHR",
            destination="CDG",
            depart_date="2026-11-01",
            return_date="2026-11-08",
            cabin="economy",
        )
        options = generate_flight_options(request)
        self.sender = WidgetItem(
            id="synthetic-widget",
            thread_id=self.thread.id,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            widget=build_flight_options_widget(options, request),
        )
        self.action = Action(
            type="flight.select",
            payload={
                "id": options[0].id,
                "options": [option.model_dump() for option in options],
                "request": request.model_dump(),
                "leg": "outbound",
            },
        )
        self.original_count = len(self.state.get_profile(self.thread.id).segments)

    def selection(self, sender=None, action=None):
        return self.server.action(self.thread, action or self.action, sender or self.sender, {})

    async def test_retry_while_first_confirmation_is_paused_does_not_book_twice(self):
        first = self.selection()
        try:
            await anext(first)
            self.assertEqual(
                len(self.state.get_profile(self.thread.id).segments), self.original_count + 1
            )
            repeated = [event async for event in self.selection()]
            self.assertEqual(repeated, [])
            self.assertEqual(
                len(self.state.get_profile(self.thread.id).segments), self.original_count + 1
            )
        finally:
            await first.aclose()

    async def test_retry_after_response_disconnect_does_not_book_twice(self):
        for leg in ("outbound", "return"):
            for count in (1, 2):
                with self.subTest(leg=leg, emitted_events=count):
                    sender = self.sender.model_copy(update={"id": f"widget-{leg}-{count}"})
                    action = self.action.model_copy(
                        update={"payload": {**self.action.payload, "leg": leg}}
                    )
                    before = len(self.state.get_profile(self.thread.id).segments)
                    first = self.selection(sender=sender, action=action)
                    try:
                        for _ in range(count):
                            await anext(first)
                    finally:
                        await first.aclose()
                    self.assertEqual(
                        [event async for event in self.selection(sender=sender, action=action)], []
                    )
                    self.assertEqual(
                        len(self.state.get_profile(self.thread.id).segments), before + 1
                    )

    async def test_completed_selection_remains_idempotent(self):
        events = [event async for event in self.selection()]
        self.assertTrue(events)
        self.assertEqual([event async for event in self.selection()], [])
        self.assertEqual(
            len(self.state.get_profile(self.thread.id).segments), self.original_count + 1
        )

    async def test_invalid_option_does_not_consume_widget(self):
        invalid = self.action.model_copy(
            update={"payload": {**self.action.payload, "id": "missing"}}
        )
        self.assertEqual([event async for event in self.selection(action=invalid)], [])
        self.assertFalse(self.state.is_widget_consumed(self.thread.id, self.sender.id))
        self.assertTrue([event async for event in self.selection()])
        self.assertEqual(
            len(self.state.get_profile(self.thread.id).segments), self.original_count + 1
        )

    async def test_other_widget_can_make_an_independent_booking(self):
        self.assertTrue([event async for event in self.selection()])
        other = self.sender.model_copy(update={"id": "other-widget"})
        self.assertTrue([event async for event in self.selection(sender=other)])
        self.assertEqual(
            len(self.state.get_profile(self.thread.id).segments), self.original_count + 2
        )


if __name__ == "__main__":
    unittest.main()
