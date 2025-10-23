"""ChatKit server implementation for Mercedes-Benz automobile assistant."""

from __future__ import annotations

import uuid
from typing import Annotated, Any, AsyncIterator

from agents import Agent, RunContextWrapper, function_tool
from chatkit.server import ChatKitServer, ClientToolCall
from chatkit.types import (
    InputTextItem,
    ThreadItem,
    ThreadMetadata,
    ThreadStreamEvent,
)
from pydantic import BaseModel, ConfigDict, Field

from .constants import INSTRUCTIONS, MODEL
from .memory_store import MemoryStore
from .vehicle_state import ChargingLocation, get_vehicle_state


def _gen_id(prefix: str = "item") -> str:
    """Generate a unique ID."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class VehicleAgentContext(BaseModel):
    """Context for vehicle assistant agent."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    thread: ThreadMetadata
    store: Annotated[MemoryStore, Field(exclude=True)]
    request_context: dict[str, Any]
    client_tool_call: ClientToolCall | None = None


# Feature 1: Climate Control
@function_tool(
    description_override="Adjust climate control settings including temperature, fan speed, seat heating, and seat ventilation"
)
async def adjust_climate(
    ctx: RunContextWrapper[VehicleAgentContext],
    temperature: float | None = None,
    fan_speed: int | None = None,
    mode: str | None = None,
    driver_seat_heating: int | None = None,
    passenger_seat_heating: int | None = None,
    driver_seat_ventilation: int | None = None,
    passenger_seat_ventilation: int | None = None,
) -> dict[str, Any]:
    """Adjust climate control settings.

    Args:
        temperature: Target temperature in Fahrenheit (60-85)
        fan_speed: Fan speed level (0-5)
        mode: Climate mode (auto, heat, cool, defrost)
        driver_seat_heating: Driver seat heating level (0-3)
        passenger_seat_heating: Passenger seat heating level (0-3)
        driver_seat_ventilation: Driver seat ventilation level (0-3)
        passenger_seat_ventilation: Passenger seat ventilation level (0-3)
    """
    vehicle = get_vehicle_state()
    changes = []

    if temperature is not None:
        vehicle.climate.temperature = max(60.0, min(85.0, temperature))
        changes.append(f"temperature to {vehicle.climate.temperature}°F")

    if fan_speed is not None:
        vehicle.climate.fan_speed = max(0, min(5, fan_speed))
        changes.append(f"fan speed to {vehicle.climate.fan_speed}")

    if mode is not None:
        vehicle.climate.mode = mode
        changes.append(f"mode to {mode}")

    if driver_seat_heating is not None:
        vehicle.climate.seat_heating["driver"] = max(0, min(3, driver_seat_heating))
        changes.append(f"driver seat heating to level {driver_seat_heating}")

    if passenger_seat_heating is not None:
        vehicle.climate.seat_heating["passenger"] = max(0, min(3, passenger_seat_heating))
        changes.append(f"passenger seat heating to level {passenger_seat_heating}")

    if driver_seat_ventilation is not None:
        vehicle.climate.seat_ventilation["driver"] = max(0, min(3, driver_seat_ventilation))
        changes.append(f"driver seat ventilation to level {driver_seat_ventilation}")

    if passenger_seat_ventilation is not None:
        vehicle.climate.seat_ventilation["passenger"] = max(
            0, min(3, passenger_seat_ventilation)
        )
        changes.append(f"passenger seat ventilation to level {passenger_seat_ventilation}")

    # Trigger UI update via client tool call
    ctx.context.client_tool_call = ClientToolCall(
        name="update_climate_ui",
        arguments={
            "temperature": vehicle.climate.temperature,
            "fan_speed": vehicle.climate.fan_speed,
            "mode": vehicle.climate.mode,
            "seat_heating": vehicle.climate.seat_heating,
            "seat_ventilation": vehicle.climate.seat_ventilation,
        },
    )

    return {
        "success": True,
        "changes": changes,
        "current_state": {
            "temperature": vehicle.climate.temperature,
            "fan_speed": vehicle.climate.fan_speed,
            "mode": vehicle.climate.mode,
            "seat_heating": vehicle.climate.seat_heating,
            "seat_ventilation": vehicle.climate.seat_ventilation,
        },
    }


# Feature 2: Navigation
@function_tool(
    description_override="Set navigation destination and route. Use this to start navigation to a location."
)
async def set_navigation(
    ctx: RunContextWrapper[VehicleAgentContext],
    destination: str,
    route_preference: str = "fastest",
) -> dict[str, Any]:
    """Set navigation destination and start routing.

    Args:
        destination: Destination address or place name
        route_preference: Route preference (fastest, shortest, eco)
    """
    vehicle = get_vehicle_state()

    # Set navigation state
    vehicle.navigation.destination = destination
    vehicle.navigation.route_active = True
    vehicle.navigation.next_maneuver = "Turn right onto Main Street"
    vehicle.navigation.distance_to_next = 0.3  # miles
    vehicle.navigation.eta_minutes = 15

    # Save to route history
    route_entry = {
        "destination": destination,
        "timestamp": "2025-10-23T14:30:00Z",
        "preference": route_preference,
    }
    vehicle.navigation.saved_routes.insert(0, route_entry)
    vehicle.navigation.saved_routes = vehicle.navigation.saved_routes[:5]  # Keep last 5

    # Trigger UI update
    ctx.context.client_tool_call = ClientToolCall(
        name="update_navigation_ui",
        arguments={
            "destination": destination,
            "route_active": True,
            "next_maneuver": vehicle.navigation.next_maneuver,
            "distance_to_next": vehicle.navigation.distance_to_next,
            "eta_minutes": vehicle.navigation.eta_minutes,
            "route_preference": route_preference,
        },
    )

    return {
        "success": True,
        "destination": destination,
        "route_active": True,
        "next_maneuver": vehicle.navigation.next_maneuver,
        "distance_to_next_miles": vehicle.navigation.distance_to_next,
        "eta_minutes": vehicle.navigation.eta_minutes,
    }


# Feature 3: Vehicle Status
@function_tool(
    description_override="Get current vehicle status including battery level, range, tire pressure, and warnings"
)
async def get_vehicle_status(
    ctx: RunContextWrapper[VehicleAgentContext],
) -> dict[str, Any]:
    """Get comprehensive vehicle status metrics."""
    vehicle = get_vehicle_state()

    # Trigger UI update to highlight dashboard metrics
    ctx.context.client_tool_call = ClientToolCall(
        name="update_vehicle_status_ui",
        arguments={
            "battery_level": vehicle.metrics.battery_level,
            "range_miles": vehicle.metrics.range_miles,
            "tire_pressure": vehicle.metrics.tire_pressure,
            "charging_status": vehicle.metrics.charging_status,
            "warnings": vehicle.metrics.warnings,
        },
    )

    return {
        "battery_level_percent": vehicle.metrics.battery_level,
        "range_miles": vehicle.metrics.range_miles,
        "tire_pressure_psi": vehicle.metrics.tire_pressure,
        "charging_status": vehicle.metrics.charging_status,
        "active_warnings": vehicle.metrics.warnings,
    }


# Feature 4: Media Control
@function_tool(
    description_override="Control media playback including play/pause, volume, source selection, and track/station"
)
async def control_media(
    ctx: RunContextWrapper[VehicleAgentContext],
    action: str | None = None,
    volume: int | None = None,
    source: str | None = None,
    track_title: str | None = None,
    artist: str | None = None,
    station: str | None = None,
) -> dict[str, Any]:
    """Control media playback.

    Args:
        action: Playback action (play, pause, next, previous)
        volume: Volume level (0-30)
        source: Media source (bluetooth, radio, usb, streaming)
        track_title: Current track title
        artist: Current artist name
        station: Radio station (for radio source)
    """
    vehicle = get_vehicle_state()
    changes = []

    if action == "play":
        vehicle.media.playing = True
        changes.append("started playback")
    elif action == "pause":
        vehicle.media.playing = False
        changes.append("paused playback")
    elif action in ["next", "previous"]:
        changes.append(f"skipped to {action} track")

    if volume is not None:
        vehicle.media.volume = max(0, min(30, volume))
        changes.append(f"volume to {vehicle.media.volume}")

    if source is not None:
        vehicle.media.source = source
        changes.append(f"source to {source}")

    if track_title is not None:
        vehicle.media.track_title = track_title
        vehicle.media.playing = True

    if artist is not None:
        vehicle.media.artist = artist

    if station is not None:
        vehicle.media.station = station

    # Trigger UI update
    ctx.context.client_tool_call = ClientToolCall(
        name="update_media_ui",
        arguments={
            "playing": vehicle.media.playing,
            "source": vehicle.media.source,
            "track_title": vehicle.media.track_title,
            "artist": vehicle.media.artist,
            "volume": vehicle.media.volume,
            "station": vehicle.media.station,
        },
    )

    return {
        "success": True,
        "changes": changes,
        "current_state": {
            "playing": vehicle.media.playing,
            "source": vehicle.media.source,
            "track_title": vehicle.media.track_title,
            "artist": vehicle.media.artist,
            "volume": vehicle.media.volume,
            "station": vehicle.media.station,
        },
    }


# Feature 5: Assistance & Service
@function_tool(
    description_override="Request assistance or service including roadside help, concierge, or service appointments"
)
async def request_assistance(
    ctx: RunContextWrapper[VehicleAgentContext],
    assistance_type: str,
    share_location: bool = True,
    notes: str | None = None,
) -> dict[str, Any]:
    """Request assistance or service.

    Args:
        assistance_type: Type of assistance (roadside, concierge, service_appointment)
        share_location: Whether to share current location
        notes: Additional notes or details
    """
    vehicle = get_vehicle_state()

    vehicle.assistance.assistance_type = assistance_type
    vehicle.assistance.service_status = "pending"
    vehicle.assistance.location_shared = share_location
    vehicle.assistance.last_service_request = (
        f"{assistance_type}: {notes}" if notes else assistance_type
    )

    # Trigger UI update
    ctx.context.client_tool_call = ClientToolCall(
        name="update_assistance_ui",
        arguments={
            "assistance_type": assistance_type,
            "service_status": "pending",
            "location_shared": share_location,
            "current_location": vehicle.navigation.current_location if share_location else None,
            "notes": notes,
        },
    )

    return {
        "success": True,
        "assistance_type": assistance_type,
        "status": "pending",
        "location_shared": share_location,
        "message": f"{assistance_type.replace('_', ' ').title()} request initiated. Help is on the way.",
    }


# Feature 6: Warning Explanation
@function_tool(
    description_override="Explain a specific dashboard warning or indicator light"
)
async def explain_warning(
    ctx: RunContextWrapper[VehicleAgentContext],
    warning_id: str | None = None,
) -> dict[str, Any]:
    """Explain a dashboard warning or indicator.

    Args:
        warning_id: Specific warning identifier, or None to show all active warnings
    """
    vehicle = get_vehicle_state()

    # Warning database
    warning_details = {
        "low_washer_fluid": {
            "title": "Low Windshield Washer Fluid",
            "severity": "low",
            "explanation": "Your windshield washer fluid is running low. Please refill at your earliest convenience to maintain clear visibility.",
            "action": "Refill washer fluid reservoir",
        },
        "tire_pressure": {
            "title": "Tire Pressure Monitoring",
            "severity": "medium",
            "explanation": "One or more tires may have incorrect pressure. Check tire pressure when tires are cold.",
            "action": "Check and adjust tire pressures",
        },
        "service_due": {
            "title": "Service Due",
            "severity": "low",
            "explanation": "Your vehicle is due for scheduled maintenance. Service includes inspection, fluid top-offs, and system checks.",
            "action": "Schedule service appointment",
        },
    }

    # Match warning from active warnings
    active_warnings = vehicle.metrics.warnings
    matched_warning = None

    if warning_id:
        matched_warning = warning_details.get(warning_id)
    elif active_warnings:
        # Try to match first active warning
        for warning in active_warnings:
            if "washer" in warning.lower():
                matched_warning = warning_details["low_washer_fluid"]
                warning_id = "low_washer_fluid"
                break

    if matched_warning:
        # Highlight the warning in UI
        ctx.context.client_tool_call = ClientToolCall(
            name="highlight_warning_ui",
            arguments={
                "warning_id": warning_id,
                "title": matched_warning["title"],
                "severity": matched_warning["severity"],
                "explanation": matched_warning["explanation"],
                "action": matched_warning["action"],
            },
        )

        return {
            "success": True,
            "warning": matched_warning,
            "warning_id": warning_id,
        }

    return {
        "success": True,
        "message": "No active warnings at this time.",
        "active_warnings": active_warnings,
    }


# Feature 7: Find Nearby (Chargers, etc.)
@function_tool(
    description_override="Find nearby locations such as charging stations, parking, restaurants, or other points of interest"
)
async def find_nearby(
    ctx: RunContextWrapper[VehicleAgentContext],
    search_type: str,
    radius_miles: float = 5.0,
    max_results: int = 5,
) -> dict[str, Any]:
    """Find nearby locations and services.

    Args:
        search_type: Type of location to search (charger, parking, restaurant, gas_station, hotel)
        radius_miles: Search radius in miles
        max_results: Maximum number of results to return
    """
    vehicle = get_vehicle_state()

    # Mock nearby results (in production, this would call a real location API)
    if search_type == "charger":
        locations = [
            ChargingLocation(
                name="EVgo Fast Charging - Downtown LA",
                address="123 S Figueroa St, Los Angeles, CA 90012",
                distance_miles=0.8,
                available_chargers=4,
                charging_speed="DC Fast",
                estimated_time_minutes=25,
            ),
            ChargingLocation(
                name="ChargePoint Station - Grand Park",
                address="200 N Grand Ave, Los Angeles, CA 90012",
                distance_miles=1.2,
                available_chargers=6,
                charging_speed="Level 2",
                estimated_time_minutes=120,
            ),
            ChargingLocation(
                name="Tesla Supercharger - Union Station",
                address="800 N Alameda St, Los Angeles, CA 90012",
                distance_miles=1.5,
                available_chargers=8,
                charging_speed="DC Fast",
                estimated_time_minutes=20,
            ),
        ]
        results = [loc.model_dump() for loc in locations[:max_results]]
    else:
        # Generic location results
        results = [
            {
                "name": f"{search_type.title()} Location {i+1}",
                "address": f"{100+i*100} Example St, Los Angeles, CA",
                "distance_miles": round(0.5 + i * 0.4, 1),
            }
            for i in range(max_results)
        ]

    # Trigger UI update to show map with locations
    ctx.context.client_tool_call = ClientToolCall(
        name="update_map_locations_ui",
        arguments={
            "search_type": search_type,
            "locations": results,
            "current_location": vehicle.navigation.current_location,
        },
    )

    return {
        "success": True,
        "search_type": search_type,
        "locations": results,
        "count": len(results),
    }


# Feature 8: Ambient Lighting
@function_tool(
    description_override="Set ambient interior lighting color and brightness"
)
async def set_ambient_lighting(
    ctx: RunContextWrapper[VehicleAgentContext],
    color: str | None = None,
    brightness: int | None = None,
) -> dict[str, Any]:
    """Set ambient lighting color and brightness.

    Args:
        color: Lighting color (white, blue, red, purple, amber, green)
        brightness: Brightness level (0-100)
    """
    vehicle = get_vehicle_state()
    changes = []

    if color is not None:
        valid_colors = ["white", "blue", "red", "purple", "amber", "green"]
        if color.lower() in valid_colors:
            vehicle.comfort.ambient_lighting_color = color.lower()
            changes.append(f"color to {color}")

    if brightness is not None:
        vehicle.comfort.ambient_lighting_brightness = max(0, min(100, brightness))
        changes.append(f"brightness to {vehicle.comfort.ambient_lighting_brightness}%")

    # Trigger UI update with visual transition
    ctx.context.client_tool_call = ClientToolCall(
        name="update_ambient_lighting_ui",
        arguments={
            "color": vehicle.comfort.ambient_lighting_color,
            "brightness": vehicle.comfort.ambient_lighting_brightness,
        },
    )

    return {
        "success": True,
        "changes": changes,
        "current_state": {
            "color": vehicle.comfort.ambient_lighting_color,
            "brightness": vehicle.comfort.ambient_lighting_brightness,
        },
    }


# Feature 9: Restore Context
@function_tool(
    description_override="Restore previous context such as a saved route, media state, or comfort settings from an earlier interaction"
)
async def restore_context(
    ctx: RunContextWrapper[VehicleAgentContext],
    context_type: str,
    identifier: str | None = None,
) -> dict[str, Any]:
    """Restore previous context or settings.

    Args:
        context_type: Type of context to restore (route, media, comfort, all)
        identifier: Specific identifier for the context (e.g., "earlier", "last", "route_1")
    """
    vehicle = get_vehicle_state()
    restored = []

    if context_type in ["route", "all"] and vehicle.navigation.saved_routes:
        # Restore most recent route
        last_route = vehicle.navigation.saved_routes[0]
        vehicle.navigation.destination = last_route["destination"]
        vehicle.navigation.route_active = True
        vehicle.navigation.next_maneuver = "Calculating route..."
        vehicle.navigation.eta_minutes = 15
        restored.append(f"route to {last_route['destination']}")

        # Trigger navigation UI update
        ctx.context.client_tool_call = ClientToolCall(
            name="update_navigation_ui",
            arguments={
                "destination": last_route["destination"],
                "route_active": True,
                "next_maneuver": vehicle.navigation.next_maneuver,
                "eta_minutes": vehicle.navigation.eta_minutes,
                "restored": True,
            },
        )

    if context_type in ["media", "all"]:
        # Could restore last played track/station
        restored.append("media preferences")

    if context_type in ["comfort", "all"]:
        # Could restore comfort settings
        restored.append("comfort settings")

    return {
        "success": True,
        "restored": restored,
        "message": f"Restored {', '.join(restored)}",
    }


class MercedesServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server for Mercedes-Benz automobile assistant."""

    def __init__(self) -> None:
        self.store = MemoryStore()
        super().__init__(self.store)

        # Initialize agent with all tools
        self.assistant = Agent[VehicleAgentContext](
            model=MODEL,
            name="Mercedes Assistant",
            instructions=INSTRUCTIONS,
            tools=[
                adjust_climate,
                set_navigation,
                get_vehicle_status,
                control_media,
                request_assistance,
                explain_warning,
                find_nearby,
                set_ambient_lighting,
                restore_context,
            ],
        )

    async def respond(
        self,
        thread: ThreadMetadata,
        input: ThreadItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Process user input and generate responses."""
        if input is None or not isinstance(input, InputTextItem):
            return

        # Create agent context
        agent_context = VehicleAgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # Get conversation history
        history_page = await self.store.load_thread_items(
            thread.id, limit=20, offset=0, context=context
        )
        messages = [item for item in history_page.items if isinstance(item, InputTextItem)]

        # Run agent and stream events
        async with self.assistant.run_stream(
            str(input.content), agent_context, history=messages
        ) as stream:
            async for event in stream.stream_events():
                # Check for client tool calls
                if agent_context.client_tool_call:
                    yield agent_context.client_tool_call
                    agent_context.client_tool_call = None

                # Forward agent events
                yield event


def create_chatkit_server() -> MercedesServer:
    """Create and return a ChatKit server instance."""
    return MercedesServer()
