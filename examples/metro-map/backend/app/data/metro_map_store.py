from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class Station(BaseModel):
    id: str
    name: str
    x: int
    y: int
    description: str
    lines: list[str] = Field(default_factory=list)


class Line(BaseModel):
    id: str
    name: str
    color: str
    orientation: Literal["horizontal", "vertical"]
    stations: list[str]


class MetroMap(BaseModel):
    id: str
    name: str
    summary: str
    stations: list[Station]
    lines: list[Line]


@dataclass
class MetroMapStore:
    """Loads the reference metro map used by the metro-map demo."""

    data_dir: Path

    def __post_init__(self) -> None:
        map_path = self.data_dir / "metro_map.json"
        with map_path.open(encoding="utf-8") as script:
            map_data = json.load(script)

        self.map = MetroMap.model_validate(map_data)
        self._station_lookup: dict[str, Station] = {
            station.id: station for station in self.map.stations
        }
        self._line_lookup: dict[str, Line] = {line.id: line for line in self.map.lines}

    # -- Queries --------------------------------------------------------------
    def get_map(self) -> MetroMap:
        return self.map

    def list_lines(self) -> list[Line]:
        return list(self.map.lines)

    def list_stations(self) -> list[Station]:
        return list(self.map.stations)

    def find_station(self, station_id: str) -> Station | None:
        return self._station_lookup.get(station_id)

    def find_line(self, line_id: str) -> Line | None:
        return self._line_lookup.get(line_id)

    def stations_for_line(self, line_id: str) -> list[Station]:
        line = self._line_lookup.get(line_id)
        if not line:
            return []
        stations: list[Station] = []
        for station_id in line.stations:
            station = self._station_lookup.get(station_id)
            if station:
                stations.append(station)
        return stations

    def dump_for_client(self) -> dict:
        return self.map.model_dump(mode="json")

    # -- Mutations ------------------------------------------------------------
    def set_map(self, map: MetroMap):
        self.map = map
        self._station_lookup = {station.id: station for station in self.map.stations}
        self._line_lookup = {line.id: line for line in self.map.lines}

    def add_station(
        self,
        station_name: str,
        line_id: str,
        append: bool = True,
        description: str = "",
    ) -> tuple[MetroMap, Station]:
        normalized_line_id = self._normalize_id(line_id)
        line = self._line_lookup.get(line_id) or self._line_lookup.get(normalized_line_id)
        if line is None or len(line.stations) == 0:
            raise ValueError(f"Line '{line_id}' is not found.")

        station_id = self._next_station_id(station_name)
        insertion_index = len(line.stations) if append else 0
        x, y = self._get_coordinates_for_new_station(line, append)
        station = Station(
            id=station_id,
            name=station_name,
            x=x,
            y=y,
            description=description,
            lines=[line.id],
        )

        self.map.stations.append(station)
        self._station_lookup[station.id] = station

        line.stations.insert(insertion_index, station.id)
        return self.map, station

    # -- Helpers --------------------------------------------------------------
    def _normalize_id(self, value: str, fallback: str = "id") -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        if not slug:
            slug = fallback
        return slug

    def _next_station_id(self, station_name: str) -> str:
        base = self._normalize_id(station_name)
        candidate = base
        counter = 2
        while candidate in self._station_lookup:
            candidate = f"{base}-{counter}"
            counter += 1
        return candidate

    def _get_coordinates_for_new_station(self, line: Line, append: bool) -> tuple[int, int]:
        if append:
            prev_id = line.stations[-1]
            prev_station = self._station_lookup.get(prev_id)
            prev_x, prev_y = (prev_station.x, prev_station.y) if prev_station else (0, 0)
            return (
                (prev_x + 1, prev_y) if line.orientation == "horizontal" else (prev_x, prev_y + 1)
            )

        next_id = line.stations[0]
        next_station = self._station_lookup.get(next_id)
        next_x, next_y = (next_station.x, next_station.y) if next_station else (0, 0)
        return (next_x - 1, next_y) if line.orientation == "horizontal" else (next_x, next_y - 1)
