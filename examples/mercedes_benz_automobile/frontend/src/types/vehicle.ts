export interface ClimateState {
  temperature: number;
  fan_speed: number;
  mode: string;
  seat_heating: {
    driver: number;
    passenger: number;
  };
  seat_ventilation: {
    driver: number;
    passenger: number;
  };
}

export interface NavigationState {
  destination: string | null;
  route_active: boolean;
  next_maneuver: string | null;
  distance_to_next: number | null;
  eta_minutes: number | null;
  current_location: string;
  saved_routes: Array<{
    destination: string;
    timestamp: string;
    preference: string;
  }>;
}

export interface VehicleMetrics {
  battery_level: number;
  range_miles: number;
  tire_pressure: {
    front_left: number;
    front_right: number;
    rear_left: number;
    rear_right: number;
  };
  charging_status: string;
  warnings: string[];
}

export interface MediaState {
  playing: boolean;
  source: string;
  track_title: string | null;
  artist: string | null;
  volume: number;
  station: string | null;
}

export interface ComfortState {
  ambient_lighting_color: string;
  ambient_lighting_brightness: number;
  massage_settings: {
    driver: {
      intensity: number;
      program: number;
    };
    passenger: {
      intensity: number;
      program: number;
    };
  };
}

export interface AssistanceState {
  last_service_request: string | null;
  service_status: string;
  assistance_type: string | null;
  location_shared: boolean;
}

export interface VehicleState {
  climate: ClimateState;
  navigation: NavigationState;
  metrics: VehicleMetrics;
  media: MediaState;
  comfort: ComfortState;
  assistance: AssistanceState;
}

export interface ChargingLocation {
  name: string;
  address: string;
  distance_miles: number;
  available_chargers?: number;
  charging_speed?: string;
  estimated_time_minutes?: number;
}
