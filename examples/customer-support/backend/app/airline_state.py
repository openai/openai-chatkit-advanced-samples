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
class LoyaltyProgress:
    current_tier: str
    next_tier: str
    points_earned: int
    points_required: int
    segments_flown: int
    segments_required: int
    renewal_date: str


@dataclass(slots=True)
class CustomerProfile:
    customer_id: str
    name: str
    loyalty_status: str
    loyalty_id: str
    email: str
    phone: str
    home_airport: str
    preferred_routes: List[str]
    travel_summary: str
    tier_benefits: List[str]
    loyalty_progress: LoyaltyProgress
    segments: List[FlightSegment]
    bags_checked: int = 0
    meal_preference: str | None = None
    special_assistance: str | None = None
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    spotlight: List[str] = field(default_factory=list)
    booked_widget_ids: List[str] = field(default_factory=list)

    def log(self, entry: str, kind: str = "info") -> None:
        self.timeline.insert(0, {"timestamp": _now_iso(), "kind": kind, "entry": entry})

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["segments"] = [segment.to_dict() for segment in self.segments]
        data["loyalty_progress"] = asdict(self.loyalty_progress)
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
            loyalty_status="Aviator Gold",
            loyalty_id="APL-204981",
            email="jordan.miles@example.com",
            phone="+1 (415) 555-9214",
            home_airport="SFO",
            preferred_routes=["SFO → JFK", "SFO → CDG", "SFO → HND"],
            travel_summary="Product leader splitting time between San Francisco and New York with quarterly long-haul art trips.",
            tier_benefits=[
                "Complimentary Premium Plus upgrades on transcon routes",
                "4 lounge guest passes every quarter",
                "15% off buy-on-board food & beverage",
                "Dedicated rebooking desk with WhatsApp follow-up",
            ],
            loyalty_progress=LoyaltyProgress(
                current_tier="Gold",
                next_tier="Platinum",
                points_earned=42000,
                points_required=60000,
                segments_flown=18,
                segments_required=32,
                renewal_date="2026-02-01",
            ),
            segments=segments,
            spotlight=[
                "Prefers window seats on daytime flights",
                "Collects modern art city guides",
                "Enjoys Michelin Bib Gourmand discoveries",
            ],
        )
        profile.log("Itinerary imported from confirmation LL0EZ6.", kind="system")
        profile.log("Waived change fees for October trip.", kind="success")
        profile.log("Added note: enjoys single-origin drip coffee.", kind="info")
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

    def cancel_trip(self, thread_id: str) -> str:
        profile = self.get_profile(thread_id)
        for segment in profile.segments:
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

    def record_upgrade(self, thread_id: str, cabin: str, price_text: str) -> str:
        profile = self.get_profile(thread_id)
        profile.log(
            f"Accepted {cabin} upgrade ({price_text}). We'll finalize payment at the airport.",
            kind="info",
        )
        return f"{cabin} upgrade confirmed. {price_text} will be charged at ticketing."

    def record_booking_hold(
        self,
        thread_id: str,
        destination: str,
        depart_label: str,
        return_label: str,
    ) -> str:
        profile = self.get_profile(thread_id)
        profile.log(
            f"Placed hold for {destination}: {depart_label} / {return_label}.",
            kind="success",
        )
        return f"Flights to {destination} are on hold: {depart_label} outbound and {return_label} return."

    def record_flight_booking(
        self,
        thread_id: str,
        flight_number: str,
        date: str,
        origin: str,
        destination: str,
        depart_time: str,
        arrival_time: str,
        *,
        seat: str = "TBD",
        status: str = "Scheduled",
    ) -> FlightSegment:
        profile = self.get_profile(thread_id)
        segment = FlightSegment(
            flight_number=flight_number,
            date=date,
            origin=origin,
            destination=destination,
            departure_time=depart_time,
            arrival_time=arrival_time,
            seat=seat,
            status=status,
        )
        profile.segments.append(segment)
        profile.log(
            f"{status}: {flight_number} {origin}->{destination} on {date} "
            f"{depart_time}-{arrival_time} seat {seat}.",
            kind="success",
        )
        return segment

    def mark_widget_consumed(self, thread_id: str, widget_id: str) -> None:
        profile = self.get_profile(thread_id)
        if widget_id not in profile.booked_widget_ids:
            profile.booked_widget_ids.append(widget_id)

    def is_widget_consumed(self, thread_id: str, widget_id: str) -> bool:
        profile = self.get_profile(thread_id)
        return widget_id in profile.booked_widget_ids

    def record_trip_dates(
        self,
        thread_id: str,
        origin: str,
        destination: str,
        depart_date: str,
        return_date: str,
    ) -> str:
        profile = self.get_profile(thread_id)
        profile.log(
            (f"Booking request for {origin} → {destination} ({depart_date} to {return_date})."),
            kind="info",
        )
        return (
            f"I'll check flights from {origin} to {destination} departing {depart_date} "
            f"and returning {return_date}."
        )

    def rebook_segment(
        self,
        thread_id: str,
        flight_number: str,
        depart_time: str,
        arrival_time: str,
        note: str,
    ) -> str:
        profile = self.get_profile(thread_id)
        segment = self._find_segment(profile, flight_number)
        if segment is None:
            raise ValueError(f"Flight {flight_number} is not on the customer's itinerary.")
        previous_depart = segment.departure_time
        previous_arrive = segment.arrival_time
        segment.departure_time = depart_time
        segment.arrival_time = arrival_time
        profile.log(
            f"Rebooked {flight_number} from {previous_depart}-{previous_arrive} to {depart_time}-{arrival_time} ({note}).",
            kind="success",
        )
        return f"You're now set for {flight_number} departing at {depart_time}. I'll keep the seat assignment the same."

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
