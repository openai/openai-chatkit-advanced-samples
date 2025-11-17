from __future__ import annotations

import json
from dataclasses import dataclass
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

PIXELS_PER_X_UNIT = 200
PIXELS_PER_Y_UNIT = 80
GRID_X_SPACING = 1.0  # spacing between columns, in grid units
GRID_Y_SPACING = 1.0  # spacing between rows, in grid units

SOLARIZED_COLORS = [
    "#268bd2",
    "#2aa198",
    "#859900",
    "#b58900",
    "#cb4b16",
    "#dc322f",
    "#d33682",
    "#6c71c4",
]


class Station(BaseModel):
    id: str
    name: str
    x: int
    y: int
    lines: list[str] = Field(default_factory=list)


class Line(BaseModel):
    id: str
    name: str
    color: str
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
            raw_data = json.load(script)

        # Support multiple starter maps while keeping a single active map loaded.
        if isinstance(raw_data, dict) and "maps" in raw_data:
            catalog = {
                entry["id"]: entry
                for entry in raw_data.get("maps", [])
                if isinstance(entry, dict) and entry.get("id")
            }
            if not catalog:
                raise ValueError("metro_map.json did not contain any maps.")

            requested_id = raw_data.get("defaultMapId")
            selected = catalog.get(requested_id) if requested_id else None
            selected_map = selected or next(iter(catalog.values()))
        else:
            catalog = {}
            selected_map = raw_data

        self.available_maps = catalog
        self.update_map(selected_map)

    def get_map(self) -> MetroMap:
        return self.map

    def update_map(self, map_data: MetroMap | dict) -> MetroMap:
        """Replace the current map and rebuild lookups."""
        metro_map = (
            map_data
            if isinstance(map_data, MetroMap)
            else MetroMap.model_validate(map_data)
        )
        self._validate_spacing(metro_map)
        self.map = metro_map
        self._station_lookup: dict[str, Station] = {
            station.id: station for station in metro_map.stations
        }
        self._line_lookup: dict[str, Line] = {line.id: line for line in metro_map.lines}
        return metro_map

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

    def interchanges(self) -> list[Station]:
        return [station for station in self.map.stations if len(station.lines) > 1]

    def dump_for_client(self) -> dict:
        return self.map.model_dump(mode="json")

    # -- Mutations ------------------------------------------------------------
    def add_station(
        self,
        *,
        line_id: str,
        station_name: str,
        line_name: str | None = None,
        line_color: str | None = None,
        after_station_id: str | None = None,
    ) -> tuple[Station, Line]:
        normalized_line_id = self._normalize_id(line_id, fallback="line")
        line = self._line_lookup.get(line_id) or self._line_lookup.get(
            normalized_line_id
        )
        if line is None:
            for candidate in self.map.lines:
                if self._normalize_id(candidate.name) == normalized_line_id:
                    line = candidate
                    break

        if line is None:
            color = self._pick_line_color(line_color)
            name = line_name or f"{normalized_line_id.title()} Line"
            line = Line(id=normalized_line_id, name=name, color=color, stations=[])
            self.map.lines.append(line)
            self._line_lookup[line.id] = line

        insertion_index = len(line.stations)
        anchor_station: Station | None = None
        if line.stations:
            anchor_id = after_station_id or line.stations[-1]
            anchor_station = self._station_lookup.get(anchor_id)
            if anchor_station is None:
                raise ValueError(f"Station '{anchor_id}' is not on the {line.name}.")
            insertion_index = line.stations.index(anchor_station.id) + 1

        station_id = self._next_station_id(station_name)
        orientation, direction = self._infer_orientation(line, insertion_index)
        x, y = self._plan_coordinates(anchor_station, orientation, direction)

        station = Station(
            id=station_id,
            name=station_name,
            x=x,
            y=y,
            lines=[line.id],
        )

        self.map.stations.append(station)
        self._station_lookup[station.id] = station

        line.stations.insert(insertion_index, station.id)
        return station, line

    # -- Helpers --------------------------------------------------------------
    def _validate_spacing(self, metro_map: MetroMap) -> None:
        """Ensure no two stations occupy the same grid cell."""
        occupied: set[tuple[float, float]] = set()
        for station in metro_map.stations:
            coord = (station.x, station.y)
            if coord in occupied:
                raise ValueError(
                    f"Spacing conflict: multiple stations share the cell ({station.x}, {station.y})."
                )
            occupied.add(coord)

    def _normalize_id(self, value: str, fallback: str = "id") -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        if not slug:
            slug = fallback
        return slug

    def _next_station_id(self, station_name: str) -> str:
        base = self._normalize_id(station_name, fallback="station")
        candidate = base
        counter = 2
        while candidate in self._station_lookup:
            candidate = f"{base}-{counter}"
            counter += 1
        return candidate

    def _pick_line_color(self, requested: str | None) -> str:
        if requested:
            return requested
        used = {line.color.lower() for line in self.map.lines}
        for color in SOLARIZED_COLORS:
            if color.lower() not in used:
                return color
        return SOLARIZED_COLORS[len(self.map.lines) % len(SOLARIZED_COLORS)]

    def _infer_orientation(
        self, line: Line, insertion_index: int
    ) -> tuple[Literal["horizontal", "vertical"], int]:
        if len(line.stations) >= 2:
            idx = max(1, insertion_index - 1)
            first_id = line.stations[idx - 1]
            second_id = (
                line.stations[idx]
                if idx < len(line.stations)
                else line.stations[idx - 1]
            )
            first = self._station_lookup[first_id]
            second = self._station_lookup[second_id]
            dx = second.x - first.x
            dy = second.y - first.y
            if abs(dx) >= abs(dy):
                return "horizontal", 1 if dx >= 0 else -1
            return "vertical", 1 if dy >= 0 else -1
        return "horizontal", 1

    def _has_spacing_conflict(self, x: float, y: float) -> bool:
        for station in self.map.stations:
            # Direct overlap
            if abs(station.x - x) < 1e-6 and abs(station.y - y) < 1e-6:
                return True
            # Same y-plane: enforce at least one column of spacing
            if abs(station.y - y) < 1e-6 and abs(station.x - x) < GRID_X_SPACING:
                return True
            # Same x-plane: enforce at least one row of spacing
            if abs(station.x - x) < 1e-6 and abs(station.y - y) < GRID_Y_SPACING:
                return True
        return False

    def _map_bounds(self) -> tuple[float, float, float, float]:
        xs = [station.x for station in self.map.stations]
        ys = [station.y for station in self.map.stations]
        return (
            min(xs, default=0),
            max(xs, default=0),
            min(ys, default=0),
            max(ys, default=0),
        )

    def _starting_position(self) -> tuple[float, float]:
        _, max_x, min_y, _ = self._map_bounds()
        if not self.map.stations:
            return 0, 0
        return max_x + GRID_X_SPACING, min_y

    def _plan_coordinates(
        self,
        anchor: Station | None,
        orientation: Literal["horizontal", "vertical"],
        direction: int,
    ) -> tuple[float, float]:
        step = GRID_X_SPACING if orientation == "horizontal" else GRID_Y_SPACING
        base_x, base_y = (anchor.x, anchor.y) if anchor else self._starting_position()
        preferred = direction or 1
        directions = [preferred, -preferred]
        start_offset = 1 if anchor else 0

        for sign in directions:
            for offset in range(start_offset, 16):
                candidate_x = base_x + (
                    step * offset * sign if orientation == "horizontal" else 0
                )
                candidate_y = base_y + (
                    0 if orientation == "horizontal" else step * offset * sign
                )
                if not self._has_spacing_conflict(candidate_x, candidate_y):
                    return candidate_x, candidate_y

        # As a fallback, walk diagonally away from the map bounds until we find space.
        min_x, max_x, min_y, max_y = self._map_bounds()
        for delta in range(1, 20):
            candidate_x = max_x + (delta * GRID_X_SPACING)
            candidate_y = max_y + (delta * GRID_Y_SPACING)
            if not self._has_spacing_conflict(candidate_x, candidate_y):
                return candidate_x, candidate_y

        raise ValueError(
            "Unable to place station while respecting spacing requirements."
        )
