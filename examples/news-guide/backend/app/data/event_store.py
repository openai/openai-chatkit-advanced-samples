"""
Data models and search helpers for News Guide events.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class EventRecord(BaseModel):
    """Represents a scheduled event with metadata used by the demo."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    date: date
    day_of_week: str = Field(alias="dayOfWeek")
    time: time
    location: str
    title: str
    details: str
    category: str
    keywords: List[str] = Field(default_factory=list)


class EventStore:
    """
    Loads event metadata and supports filtering by date, day of week, time, or keywords.
    Intended for demo use only; a production system would connect to a database.
    """

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self._events: Dict[str, EventRecord] = {}
        self._order: List[str] = []
        self.reload()

    @property
    def events_path(self) -> Path:
        return self.data_dir / "events.json"

    def reload(self) -> None:
        """Hydrate events from the JSON file."""
        if not self.events_path.exists():
            raise FileNotFoundError(f"Missing events metadata file: {self.events_path}")

        with self.events_path.open("r", encoding="utf-8") as file:
            raw = json.load(file)

        if not isinstance(raw, list):
            raise ValueError("events.json must contain a list of event entries.")

        events: Dict[str, EventRecord] = {}
        order: List[str] = []
        for idx, entry in enumerate(raw):
            try:
                record = EventRecord.model_validate(entry)
            except ValidationError as exc:
                raise ValueError(f"Invalid event metadata at index {idx}: {exc}") from exc
            events[record.id] = record
            order.append(record.id)

        self._events = events
        self._order = order

    def list_events(self) -> List[Dict[str, Any]]:
        """Return all events in list order."""
        return [self._serialize_event(self._events[event_id]) for event_id in self._order]

    def get_event(self, event_id: str) -> Dict[str, Any] | None:
        record = self._events.get(event_id)
        if not record:
            return None
        return self._serialize_event(record)

    def search_by_date(self, value: str | date | datetime) -> List[Dict[str, Any]]:
        target = self._parse_date(value)
        if not target:
            return []
        return [
            self._serialize_event(self._events[event_id])
            for event_id in self._order
            if self._events[event_id].date == target
        ]

    def search_by_day_of_week(self, day: str) -> List[Dict[str, Any]]:
        normalized = day.strip().lower()
        if not normalized:
            return []
        return [
            self._serialize_event(self._events[event_id])
            for event_id in self._order
            if self._events[event_id].day_of_week.strip().lower() == normalized
        ]

    def search_by_time(self, value: str | time | datetime) -> List[Dict[str, Any]]:
        target = self._parse_time(value)
        if not target:
            return []
        return [
            self._serialize_event(self._events[event_id])
            for event_id in self._order
            if self._events[event_id].time == target
        ]

    def search_by_keyword(self, terms: str | Sequence[str]) -> List[Dict[str, Any]]:
        normalized_terms = self._normalize_keywords(terms)
        if not normalized_terms:
            return []

        def _fields(record: EventRecord) -> List[str]:
            combined_keywords = " ".join(record.keywords)
            return [
                record.id,
                record.day_of_week,
                record.location,
                record.title,
                record.details,
                record.category,
                combined_keywords,
            ]

        matches: List[Dict[str, Any]] = []
        for event_id in self._order:
            record = self._events[event_id]
            haystack = [field.lower() for field in _fields(record)]
            if any(term in field for term in normalized_terms for field in haystack):
                matches.append(self._serialize_event(record))

        return matches

    # -- Helpers ---------------------------------------------------------
    def _serialize_event(self, record: EventRecord) -> Dict[str, Any]:
        payload = record.model_dump(by_alias=True)
        payload["date"] = record.date.isoformat()
        payload["time"] = record.time.strftime("%H:%M")
        return payload

    def _parse_date(self, value: str | date | datetime) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            try:
                return datetime.fromisoformat(text).date()
            except ValueError:
                return None
        return None

    def _parse_time(self, value: str | time | datetime) -> time | None:
        if isinstance(value, datetime):
            return value.time().replace(second=0, microsecond=0)
        if isinstance(value, time):
            return value.replace(second=0, microsecond=0)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            try:
                parsed = datetime.strptime(text, "%H:%M")
                return parsed.time()
            except ValueError:
                return None
        return None

    def _normalize_keywords(self, terms: str | Sequence[str]) -> List[str]:
        values: Iterable[str]
        if isinstance(terms, str):
            values = [terms]
        else:
            values = terms
        normalized: List[str] = []
        for value in values:
            text = value.strip().lower()
            if text:
                normalized.append(text)
                normalized.extend(token for token in re.split(r"[^a-z0-9]+", text) if token)
        return list(dict.fromkeys(normalized))  # dedupe while preserving order
