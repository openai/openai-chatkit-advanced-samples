"""
Widget helpers for presenting a list of events with timeline styling.
"""

from __future__ import annotations

from datetime import date, datetime
from itertools import groupby
from typing import Any, Iterable, Mapping, Sequence

from chatkit.actions import ActionConfig
from chatkit.widgets import (
    Borders,
    Box,
    Button,
    Col,
    ListView,
    ListViewItem,
    Row,
    Spacer,
    Text,
    Title,
    WidgetComponent,
)

from ..data.event_store import EventRecord

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


def build_event_list_widget(
    events: Iterable[EventLike],
    selected_event_id: str | None = None,
    selected_event_description: str | None = None,
) -> ListView:
    """Render an event list widget grouped by date."""
    records = [_coerce_event(event) for event in events]
    records.sort(key=lambda rec: rec.date)
    event_ids: list[str] = [record.id for record in records]

    items = []

    for event_date, group in groupby(records, key=lambda rec: rec.date):
        group_records = list(group)
        items.append(ListViewItem(children=[_group_header(event_date)]))
        for record in group_records:
            is_selected = selected_event_id == record.id if selected_event_id else False
            description_value = (
                selected_event_description
                if is_selected and selected_event_description is not None
                else (record.details if is_selected else None)
            )
            items.append(
                ListViewItem(
                    children=[
                        _event_card(
                            record,
                            is_selected=is_selected,
                            description_value=description_value,
                            event_ids=event_ids,
                        )
                    ]
                )
            )

    # Don't show the "show more" button, always cap at 6 items
    return ListView(children=items[:6], limit=6)


def _coerce_event(event: EventLike) -> EventRecord:
    if isinstance(event, EventRecord):
        return event
    return EventRecord.model_validate(event)


def _event_card(
    record: EventRecord,
    is_selected: bool,
    description_value: str | None = None,
    event_ids: Sequence[str] | None = None,
) -> Box:
    category = (record.category or "").strip().lower()
    color = CATEGORY_COLORS.get(category, DEFAULT_CATEGORY_COLOR)
    children: list[WidgetComponent] = [
        _event_header(record, color, is_selected=is_selected, event_ids=event_ids or []),
        Title(value=record.title, size="sm"),
        Text(value=_format_location(record), color="alpha-70", size="xs"),
    ]
    children.append(
        Text(
            id=f"{record.id}-details",
            key=f"{record.id}-details",
            value=description_value or "",
            size="sm",
            color="alpha-90",
            streaming=True,
        )
    )
    return Box(
        width=400,
        border=Borders(
            top={"size": 1, "color": "gray-900"},
            right={"size": 1, "color": "gray-900"},
            bottom={"size": 1, "color": "gray-900"},
            left={"size": 5, "color": color},
        ),
        children=[
            Col(
                flex=1,
                gap=2,
                padding={"left": 2, "y": 2},
                children=children,
            ),
        ],
    )


def _group_header(event_date: date) -> Box:
    return Box(
        padding={"bottom": 1, "top": 2},
        children=[
            Text(value=_format_date(event_date), weight="medium", size="sm"),
        ],
    )


def _event_header(
    record: EventRecord, color: str, is_selected: bool, event_ids: Sequence[str]
) -> Row:
    return Row(
        align="center",
        children=[
            Text(value=_format_time(record), color=color, size="sm"),
            Spacer(),
            Button(
                label="Show details ↓",
                size="sm",
                iconSize="sm",
                pill=True,
                variant="ghost",
                color=None if is_selected else "warning",
                onClickAction=ActionConfig(
                    type="view_event_details",
                    payload={
                        "id": record.id,
                        "event_ids": list(event_ids),
                        "is_selected": is_selected,
                    },
                    handler="server",
                ),
            ),
        ],
    )


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
