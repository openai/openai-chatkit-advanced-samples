interface FlightSegment {
  flight_number: string;
  date: string;
  origin: string;
  destination: string;
  departure_time: string;
  arrival_time: string;
  seat: string;
  status: string;
}

interface TimelineEntry {
  timestamp: string;
  kind: string;
  entry: string;
}

export interface CustomerProfile {
  customer_id: string;
  name: string;
  loyalty_status: string;
  loyalty_id: string;
  email: string;
  phone: string;
  tier_benefits: string[];
  segments: FlightSegment[];
  bags_checked: number;
  meal_preference: string | null;
  special_assistance: string | null;
  timeline: TimelineEntry[];
}

function nowIso(): string {
  return new Date().toISOString();
}

class FlightSegmentClass {
  flight_number: string;
  date: string;
  origin: string;
  destination: string;
  departure_time: string;
  arrival_time: string;
  seat: string;
  status: string;

  constructor(data: Omit<FlightSegment, 'status'>) {
    this.flight_number = data.flight_number;
    this.date = data.date;
    this.origin = data.origin;
    this.destination = data.destination;
    this.departure_time = data.departure_time;
    this.arrival_time = data.arrival_time;
    this.seat = data.seat;
    this.status = 'Scheduled';
  }

  cancel(): void {
    this.status = 'Cancelled';
  }

  changeSeat(newSeat: string): void {
    this.seat = newSeat;
  }

  toDict(): FlightSegment {
    return {
      flight_number: this.flight_number,
      date: this.date,
      origin: this.origin,
      destination: this.destination,
      departure_time: this.departure_time,
      arrival_time: this.arrival_time,
      seat: this.seat,
      status: this.status,
    };
  }
}

class CustomerProfileClass {
  customer_id: string;
  name: string;
  loyalty_status: string;
  loyalty_id: string;
  email: string;
  phone: string;
  tier_benefits: string[];
  segments: FlightSegmentClass[];
  bags_checked: number;
  meal_preference: string | null;
  special_assistance: string | null;
  timeline: TimelineEntry[];

  constructor(data: Omit<CustomerProfile, 'timeline'>) {
    this.customer_id = data.customer_id;
    this.name = data.name;
    this.loyalty_status = data.loyalty_status;
    this.loyalty_id = data.loyalty_id;
    this.email = data.email;
    this.phone = data.phone;
    this.tier_benefits = data.tier_benefits;
    this.segments = data.segments.map(
      (s) =>
        new FlightSegmentClass({
          flight_number: s.flight_number,
          date: s.date,
          origin: s.origin,
          destination: s.destination,
          departure_time: s.departure_time,
          arrival_time: s.arrival_time,
          seat: s.seat,
        })
    );
    this.bags_checked = data.bags_checked;
    this.meal_preference = data.meal_preference;
    this.special_assistance = data.special_assistance;
    this.timeline = [];
  }

  log(entry: string, kind: string = 'info'): void {
    this.timeline.unshift({
      timestamp: nowIso(),
      kind,
      entry,
    });
  }

  toDict(): CustomerProfile {
    return {
      customer_id: this.customer_id,
      name: this.name,
      loyalty_status: this.loyalty_status,
      loyalty_id: this.loyalty_id,
      email: this.email,
      phone: this.phone,
      tier_benefits: this.tier_benefits,
      segments: this.segments.map((s) => s.toDict()),
      bags_checked: this.bags_checked,
      meal_preference: this.meal_preference,
      special_assistance: this.special_assistance,
      timeline: this.timeline,
    };
  }
}

export class AirlineStateManager {
  private states: Map<string, CustomerProfileClass>;

  constructor() {
    this.states = new Map();
  }

  private createDefaultState(): CustomerProfileClass {
    const segments: FlightSegment[] = [
      {
        flight_number: 'OA476',
        date: '2025-10-02',
        origin: 'SFO',
        destination: 'JFK',
        departure_time: '08:05',
        arrival_time: '16:35',
        seat: '14A',
        status: 'Scheduled',
      },
      {
        flight_number: 'OA477',
        date: '2025-10-10',
        origin: 'JFK',
        destination: 'SFO',
        departure_time: '18:50',
        arrival_time: '22:15',
        seat: '15C',
        status: 'Scheduled',
      },
    ];

    const profile = new CustomerProfileClass({
      customer_id: 'cus_98421',
      name: 'Jordan Miles',
      loyalty_status: 'Aviator Platinum',
      loyalty_id: 'APL-204981',
      email: 'jordan.miles@example.com',
      phone: '+1 (415) 555-9214',
      tier_benefits: [
        'Complimentary upgrades when available',
        'Unlimited lounge access',
        'Priority boarding group 1',
      ],
      segments,
      bags_checked: 0,
      meal_preference: null,
      special_assistance: null,
    });

    profile.log('Itinerary imported from confirmation LL0EZ6.', 'system');
    return profile;
  }

  getProfile(threadId: string): CustomerProfileClass {
    if (!this.states.has(threadId)) {
      this.states.set(threadId, this.createDefaultState());
    }
    return this.states.get(threadId)!;
  }

  changeSeat(threadId: string, flightNumber: string, seat: string): string {
    const profile = this.getProfile(threadId);
    if (!this.isValidSeat(seat)) {
      throw new Error('Seat must be a row number followed by a letter, for example 12C.');
    }

    const segment = this.findSegment(profile, flightNumber);
    if (!segment) {
      throw new Error(`Flight ${flightNumber} is not on the customer's itinerary.`);
    }

    const previous = segment.seat;
    segment.changeSeat(seat.toUpperCase());
    profile.log(
      `Seat changed on ${segment.flight_number} from ${previous} to ${segment.seat}.`,
      'success'
    );
    return `Seat updated to ${segment.seat} on flight ${segment.flight_number}.`;
  }

  cancelTrip(threadId: string): string {
    const profile = this.getProfile(threadId);
    for (const segment of profile.segments) {
      segment.cancel();
    }
    profile.log('Trip cancelled at customer request.', 'warning');
    return 'The reservation has been cancelled. Refund processing will begin immediately.';
  }

  addBag(threadId: string): string {
    const profile = this.getProfile(threadId);
    profile.bags_checked += 1;
    profile.log(`Added checked bag. Total bags now ${profile.bags_checked}.`, 'info');
    return `Checked bag added. You now have ${profile.bags_checked} bag(s) checked.`;
  }

  setMeal(threadId: string, meal: string): string {
    const profile = this.getProfile(threadId);
    profile.meal_preference = meal;
    profile.log(`Meal preference updated to ${meal}.`, 'info');
    return `We'll note ${meal} as the meal preference.`;
  }

  requestAssistance(threadId: string, note: string): string {
    const profile = this.getProfile(threadId);
    profile.special_assistance = note;
    profile.log(`Special assistance noted: ${note}.`, 'info');
    return 'Assistance request recorded. Airport staff will be notified.';
  }

  toDict(threadId: string): CustomerProfile {
    return this.getProfile(threadId).toDict();
  }

  private isValidSeat(seat: string): boolean {
    const trimmed = seat.trim().toUpperCase();
    if (trimmed.length < 2) {
      return false;
    }
    const row = trimmed.slice(0, -1);
    const letter = trimmed.slice(-1);
    return /^\d+$/.test(row) && /^[A-Z]$/.test(letter);
  }

  private findSegment(
    profile: CustomerProfileClass,
    flightNumber: string
  ): FlightSegmentClass | null {
    const normalizedFlightNumber = flightNumber.toUpperCase().trim();
    for (const segment of profile.segments) {
      if (segment.flight_number.toUpperCase() === normalizedFlightNumber) {
        return segment;
      }
    }
    return null;
  }
}
