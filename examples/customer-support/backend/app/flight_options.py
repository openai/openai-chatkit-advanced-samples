from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from chatkit.actions import Action
from chatkit.widgets import WidgetRoot, WidgetTemplate
from pydantic import BaseModel

FlightCabin = Literal["economy", "premium economy", "business", "first"]

FLIGHT_SELECT_ACTION_TYPE = "flight.select"
FlightLeg = Literal["outbound", "return"]


class FlightSearchRequest(BaseModel):
    """Minimal search context used to render flight options."""

    origin: str
    destination: str
    depart_date: str
    return_date: str
    cabin: str

    def normalized_origin(self) -> str:
        return _sanitize_airport_code(self.origin)

    def normalized_destination(self) -> str:
        return _sanitize_airport_code(self.destination)


class FlightOption(BaseModel):
    """Single flight option shown in the picker."""

    id: str
    from_airport: str
    to_airport: str
    dep_time: str
    arr_time: str
    date_label: str
    cabin: str

    model_config = {"populate_by_name": True}


class FlightSelectPayload(BaseModel):
    """Payload sent when the user taps a flight option."""

    id: str
    options: list[FlightOption]
    request: FlightSearchRequest
    leg: FlightLeg = "outbound"


FlightSelectAction = Action[Literal["flight.select"], FlightSelectPayload]
flight_options_template = WidgetTemplate.from_file("flight_options.widget")


def _sanitize_airport_code(raw: str) -> str:
    code = raw.strip().upper()
    if len(code) == 3 and code.isalpha():
        return code
    return code[:3]


def _format_date_label(raw_date: str) -> str:
    """Convert YYYY-MM-DD into a friendly label, otherwise return the input."""

    try:
        parsed = datetime.fromisoformat(raw_date)
        return f"{parsed.strftime('%a, %b ')}{parsed.day}"
    except Exception:
        return raw_date


def generate_flight_options(
    request: FlightSearchRequest,
) -> list[FlightOption]:
    """Return a small set of plausible flight options for the widget."""

    date_label = _format_date_label(request.depart_date)
    cabin_label = request.cabin.title()
    return [
        FlightOption(
            id="flight-morning",
            from_airport=request.normalized_origin(),
            to_airport=request.normalized_destination(),
            dep_time="08:10",
            arr_time="16:40",
            date_label=date_label,
            cabin=cabin_label,
        ),
        FlightOption(
            id="flight-midday",
            from_airport=request.normalized_origin(),
            to_airport=request.normalized_destination(),
            dep_time="12:35",
            arr_time="21:05",
            date_label=date_label,
            cabin=cabin_label,
        ),
        FlightOption(
            id="flight-late",
            from_airport=request.normalized_origin(),
            to_airport=request.normalized_destination(),
            dep_time="21:55",
            arr_time="06:20 (+1)",
            date_label=date_label,
            cabin=cabin_label,
        ),
    ]


def _serialize_option(option: FlightOption) -> dict[str, Any]:
    """Return a template-friendly dict for a flight option."""

    return {
        "id": option.id,
        "from_airport": option.from_airport,
        "to_airport": option.to_airport,
        "dep_time": option.dep_time,
        "arr_time": option.arr_time,
        "date_label": option.date_label,
        "cabin": option.cabin,
    }


def describe_flight_option(option: FlightOption, request: FlightSearchRequest) -> str:
    """Human-readable summary used in assistant replies and logs."""

    return (
        f"{option.cabin} {option.from_airport} → {option.to_airport} on "
        f"{_format_date_label(request.depart_date)} departing "
        f"{option.dep_time} (arrives {option.arr_time}); "
        f"return on {request.return_date}"
    )


def build_flight_options_widget(
    options: list[FlightOption],
    request: FlightSearchRequest,
    *,
    selected_id: str | None = None,
    leg: FlightLeg = "outbound",
) -> WidgetRoot:
    """Render the flight picker widget with the .widget template."""

    payload = {
        "options": [_serialize_option(option) for option in options],
        "request": request.model_dump(mode="json"),
        "selectedId": selected_id,
        "leg": leg,
        "actionType": FLIGHT_SELECT_ACTION_TYPE,
    }
    return flight_options_template.build(payload)
