"""Vehicle state management for Mercedes-Benz automobile assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


@dataclass
class ClimateState:
    """Climate control state."""

    temperature: float = 72.0  # Fahrenheit
    fan_speed: int = 3  # 0-5
    mode: str = "auto"  # auto, heat, cool, defrost
    seat_heating: dict[str, int] = field(default_factory=lambda: {"driver": 0, "passenger": 0})
    seat_ventilation: dict[str, int] = field(
        default_factory=lambda: {"driver": 0, "passenger": 0}
    )


@dataclass
class NavigationState:
    """Navigation state."""

    destination: str | None = None
    route_active: bool = False
    next_maneuver: str | None = None
    distance_to_next: float | None = None
    eta_minutes: int | None = None
    current_location: str = "Downtown Los Angeles, CA"
    saved_routes: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class VehicleMetrics:
    """Vehicle status metrics."""

    battery_level: float = 85.0  # percent
    range_miles: float = 285.0
    tire_pressure: dict[str, float] = field(
        default_factory=lambda: {
            "front_left": 35.0,
            "front_right": 35.0,
            "rear_left": 35.0,
            "rear_right": 35.0,
        }
    )
    charging_status: str = "not_charging"  # not_charging, charging, fast_charging
    warnings: list[str] = field(default_factory=list)


@dataclass
class MediaState:
    """Media playback state."""

    playing: bool = False
    source: str = "bluetooth"  # bluetooth, radio, usb, streaming
    track_title: str | None = None
    artist: str | None = None
    volume: int = 15  # 0-30
    station: str | None = None


@dataclass
class ComfortState:
    """Comfort and personalization settings."""

    ambient_lighting_color: str = "white"  # white, blue, red, purple, amber, green
    ambient_lighting_brightness: int = 50  # 0-100
    massage_settings: dict[str, dict[str, int]] = field(
        default_factory=lambda: {"driver": {"intensity": 0, "program": 0}, "passenger": {"intensity": 0, "program": 0}}
    )


@dataclass
class AssistanceState:
    """Assistance and service state."""

    last_service_request: str | None = None
    service_status: str = "none"  # none, pending, in_progress, completed
    assistance_type: str | None = None  # roadside, concierge, service_appointment
    location_shared: bool = False


class VehicleState:
    """Manages the complete vehicle state."""

    def __init__(self) -> None:
        self.climate = ClimateState()
        self.navigation = NavigationState()
        self.metrics = VehicleMetrics()
        self.media = MediaState()
        self.comfort = ComfortState()
        self.assistance = AssistanceState()

        # Add some sample warnings
        self.metrics.warnings = ["Low windshield washer fluid"]

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for API responses."""
        return {
            "climate": {
                "temperature": self.climate.temperature,
                "fan_speed": self.climate.fan_speed,
                "mode": self.climate.mode,
                "seat_heating": self.climate.seat_heating,
                "seat_ventilation": self.climate.seat_ventilation,
            },
            "navigation": {
                "destination": self.navigation.destination,
                "route_active": self.navigation.route_active,
                "next_maneuver": self.navigation.next_maneuver,
                "distance_to_next": self.navigation.distance_to_next,
                "eta_minutes": self.navigation.eta_minutes,
                "current_location": self.navigation.current_location,
                "saved_routes": self.navigation.saved_routes,
            },
            "metrics": {
                "battery_level": self.metrics.battery_level,
                "range_miles": self.metrics.range_miles,
                "tire_pressure": self.metrics.tire_pressure,
                "charging_status": self.metrics.charging_status,
                "warnings": self.metrics.warnings,
            },
            "media": {
                "playing": self.media.playing,
                "source": self.media.source,
                "track_title": self.media.track_title,
                "artist": self.media.artist,
                "volume": self.media.volume,
                "station": self.media.station,
            },
            "comfort": {
                "ambient_lighting_color": self.comfort.ambient_lighting_color,
                "ambient_lighting_brightness": self.comfort.ambient_lighting_brightness,
                "massage_settings": self.comfort.massage_settings,
            },
            "assistance": {
                "last_service_request": self.assistance.last_service_request,
                "service_status": self.assistance.service_status,
                "assistance_type": self.assistance.assistance_type,
                "location_shared": self.assistance.location_shared,
            },
        }


class ChargingLocation(BaseModel):
    """Represents a nearby charging location."""

    name: str
    address: str
    distance_miles: float
    available_chargers: int
    charging_speed: str  # Level 2, DC Fast, Tesla Supercharger
    estimated_time_minutes: int


# Global vehicle state (in production, this would be per-user/session)
_vehicle_state = VehicleState()


def get_vehicle_state() -> VehicleState:
    """Get the global vehicle state."""
    return _vehicle_state
