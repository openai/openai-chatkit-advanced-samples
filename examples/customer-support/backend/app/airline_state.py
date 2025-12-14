from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass(slots=True)
class FlightSegment:
    flight_number: str
    date: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    seat: str
    status: str = "Scheduled"

    def cancel(self) -> None:
        self.status = "Cancelled"

    def change_seat(self, new_seat: str) -> None:
        self.seat = new_seat

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CustomerProfile:
    customer_id: str
    name: str
    loyalty_status: str
    loyalty_id: str
    email: str
    phone: str
    tier_benefits: List[str]
    segments: List[FlightSegment]
    bags_checked: int = 0
    meal_preference: str | None = None
    special_assistance: str | None = None
    timeline: List[Dict[str, Any]] = field(default_factory=list)

    def log(self, entry: str, kind: str = "info") -> None:
        self.timeline.insert(0, {"timestamp": _now_iso(), "kind": kind, "entry": entry})

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["segments"] = [segment.to_dict() for segment in self.segments]
        return data


class AirlineStateManager:
    """Manages per-thread airline customer state."""

    def __init__(self) -> None:
        self._states: Dict[str, CustomerProfile] = {}

    def _create_default_state(self) -> CustomerProfile:
        segments = [
            FlightSegment(
                flight_number="OA476",
                date="2025-10-02",
                origin="SFO",
                destination="JFK",
                departure_time="08:05",
                arrival_time="16:35",
                seat="14A",
            ),
            FlightSegment(
                flight_number="OA477",
                date="2025-10-10",
                origin="JFK",
                destination="SFO",
                departure_time="18:50",
                arrival_time="22:15",
                seat="15C",
            ),
        ]
        profile = CustomerProfile(
            customer_id="cus_98421",
            name="Jordan Miles",
            loyalty_status="Aviator Platinum",
            loyalty_id="APL-204981",
            email="jordan.miles@example.com",
            phone="+1 (415) 555-9214",
            tier_benefits=[
                "Complimentary upgrades when available",
                "Unlimited lounge access",
                "Priority boarding group 1",
            ],
            segments=segments,
        )
        profile.log("Itinerary imported from confirmation LL0EZ6.", kind="system")
        return profile

    def get_profile(self, thread_id: str) -> CustomerProfile:
        if thread_id not in self._states:
            self._states[thread_id] = self._create_default_state()
        return self._states[thread_id]

    def change_seat(self, thread_id: str, flight_number: str, seat: str) -> str:
        profile = self.get_profile(thread_id)
        if not self._is_valid_seat(seat):
            raise ValueError("Seat must be a row number followed by a letter, for example 12C.")

        segment = self._find_segment(profile, flight_number)
        if segment is None:
            raise ValueError(f"Flight {flight_number} is not on the customer's itinerary.")

        previous = segment.seat
        segment.change_seat(seat.upper())
        profile.log(
            f"Seat changed on {segment.flight_number} from {previous} to {segment.seat}.",
            kind="success",
        )
        return f"Seat updated to {segment.seat} on flight {segment.flight_number}."

    def cancel_trip(self, thread_id: str, flight_number: str) -> str:
        profile = self.get_profile(thread_id)
        segment = self._find_segment(profile, flight_number)
        if segment is None:
            raise ValueError(f"Flight {flight_number} is not on the customer's itinerary.")
        segment.cancel()
        profile.log("Trip cancelled at customer request.", kind="warning")
        return "The reservation has been cancelled. Refund processing will begin immediately."

    def add_bag(self, thread_id: str) -> str:
        profile = self.get_profile(thread_id)
        profile.bags_checked += 1
        profile.log(f"Added checked bag. Total bags now {profile.bags_checked}.", kind="info")
        return f"Checked bag added. You now have {profile.bags_checked} bag(s) checked."

    def set_meal(self, thread_id: str, meal: str) -> str:
        profile = self.get_profile(thread_id)
        profile.meal_preference = meal
        profile.log(f"Meal preference updated to {meal}.", kind="info")
        return f"We'll note {meal} as the meal preference."

    def request_assistance(self, thread_id: str, note: str) -> str:
        profile = self.get_profile(thread_id)
        profile.special_assistance = note
        profile.log(f"Special assistance noted: {note}.", kind="info")
        return "Assistance request recorded. Airport staff will be notified."

    def to_dict(self, thread_id: str) -> Dict[str, Any]:
        return self.get_profile(thread_id).to_dict()

    @staticmethod
    def _is_valid_seat(seat: str) -> bool:
        seat = seat.strip().upper()
        if len(seat) < 2:
            return False
        row = seat[:-1]
        letter = seat[-1]
        return row.isdigit() and letter.isalpha()

    @staticmethod
    def _find_segment(profile: CustomerProfile, flight_number: str) -> FlightSegment | None:
        flight_number = flight_number.upper().strip()
        for segment in profile.segments:
            if segment.flight_number.upper() == flight_number:
                return segment
        return None
