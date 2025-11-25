"""
Widget helpers for presenting a list of events with timeline styling.
"""

from __future__ import annotations

from datetime import date, datetime
from itertools import groupby
from typing import Any, Iterable, Mapping

from chatkit.widgets import WidgetRoot

from ..data.event_store import EventRecord
from .widget_template import WidgetTemplate

CATEGORY_COLORS: dict[str, str] = {
    "community": "purple-400",
    "civics": "blue-400",
    "arts": "pink-400",
    "outdoors": "green-400",
    "music": "orange-400",
    "family": "yellow-400",
    "food": "red-400",
    "fitness": "teal-400",
}
DEFAULT_CATEGORY_COLOR = "gray-400"


EventLike = EventRecord | Mapping[str, Any]
event_list_widget_template = WidgetTemplate.from_file("event_list.widget")


def build_event_list_widget(
    events: Iterable[EventLike],
    selected_event_id: str | None = None,
) -> WidgetRoot:
    """Render an event list widget grouped by date using the .widget template."""
    records = [_coerce_event(event) for event in events]
    records.sort(key=lambda rec: rec.date)
    event_ids: list[str] = [record.id for record in records]

    groups: list[dict[str, Any]] = []
    for event_date, group in groupby(records, key=lambda rec: rec.date):
        group_records = list(group)
        events_data = [_serialize_event(record) for record in group_records]
        groups.append({"dateLabel": _format_date(event_date), "events": events_data})

    payload = {
        "groups": groups,
        "selectedEventId": selected_event_id,
        "eventIds": event_ids,
    }

    return event_list_widget_template.build(payload)


def _coerce_event(event: EventLike) -> EventRecord:
    if isinstance(event, EventRecord):
        return event
    return EventRecord.model_validate(event)


def _serialize_event(record: EventRecord) -> dict[str, Any]:
    category = (record.category or "").strip().lower()
    color = CATEGORY_COLORS.get(category, DEFAULT_CATEGORY_COLOR)
    payload: dict[str, Any] = {
        "id": record.id,
        "title": record.title,
        "location": _format_location(record),
        "timeLabel": _format_time(record),
        "dateLabel": _format_date(record.date),
        "color": color,
        "details": record.details,
    }
    return {key: value for key, value in payload.items() if value is not None}


def _format_date(event_date: date) -> str:
    month = event_date.strftime("%b")
    weekday = event_date.strftime("%A")
    return f"{weekday}, {month} {event_date.day}"


def _format_time(record: EventRecord) -> str:
    value = datetime.combine(record.date, record.time)
    formatted = value.strftime("%I:%M %p")
    return formatted.lstrip("0")


def _format_location(record: EventRecord) -> str:
    return record.location
