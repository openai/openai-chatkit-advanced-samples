import { useCallback, useEffect, useState } from "react";
import { VEHICLE_STATE_API_URL } from "../lib/config";
import type { VehicleState } from "../types/vehicle";

export interface VehicleStateAction {
  type: string;
  payload: unknown;
}

export function useVehicleState() {
  const [vehicleState, setVehicleState] = useState<VehicleState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchVehicleState = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(VEHICLE_STATE_API_URL);
      if (!response.ok) {
        throw new Error(`Failed to fetch vehicle state: ${response.statusText}`);
      }
      const data = await response.json();
      setVehicleState(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchVehicleState();
  }, [fetchVehicleState]);

  const performAction = useCallback((action: VehicleStateAction) => {
    // Update local state based on action type
    setVehicleState((current) => {
      if (!current) return current;

      switch (action.type) {
        case "update_climate_ui": {
          const payload = action.payload as {
            temperature?: number;
            fan_speed?: number;
            mode?: string;
            seat_heating?: { driver: number; passenger: number };
            seat_ventilation?: { driver: number; passenger: number };
          };
          return {
            ...current,
            climate: {
              ...current.climate,
              ...payload,
            },
          };
        }

        case "update_navigation_ui": {
          const payload = action.payload as {
            destination?: string;
            route_active?: boolean;
            next_maneuver?: string;
            distance_to_next?: number;
            eta_minutes?: number;
          };
          return {
            ...current,
            navigation: {
              ...current.navigation,
              ...payload,
            },
          };
        }

        case "update_vehicle_status_ui": {
          const payload = action.payload as {
            battery_level?: number;
            range_miles?: number;
            tire_pressure?: Record<string, number>;
            charging_status?: string;
            warnings?: string[];
          };
          return {
            ...current,
            metrics: {
              ...current.metrics,
              ...payload,
            },
          };
        }

        case "update_media_ui": {
          const payload = action.payload as {
            playing?: boolean;
            source?: string;
            track_title?: string;
            artist?: string;
            volume?: number;
            station?: string;
          };
          return {
            ...current,
            media: {
              ...current.media,
              ...payload,
            },
          };
        }

        case "update_ambient_lighting_ui": {
          const payload = action.payload as {
            color?: string;
            brightness?: number;
          };
          return {
            ...current,
            comfort: {
              ...current.comfort,
              ambient_lighting_color: payload.color ?? current.comfort.ambient_lighting_color,
              ambient_lighting_brightness:
                payload.brightness ?? current.comfort.ambient_lighting_brightness,
            },
          };
        }

        case "update_assistance_ui": {
          const payload = action.payload as {
            assistance_type?: string;
            service_status?: string;
            location_shared?: boolean;
          };
          return {
            ...current,
            assistance: {
              ...current.assistance,
              ...payload,
            },
          };
        }

        default:
          return current;
      }
    });
  }, []);

  return {
    vehicleState,
    loading,
    error,
    refresh: fetchVehicleState,
    performAction,
  };
}
