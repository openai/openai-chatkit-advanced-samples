import {
  AlertTriangle,
  Battery,
  Gauge,
  Navigation,
  ThermometerSun,
  Volume2,
} from "lucide-react";
import type { VehicleState } from "../types/vehicle";

interface DashboardProps {
  vehicleState: VehicleState | null;
}

export function Dashboard({ vehicleState }: DashboardProps) {
  if (!vehicleState) {
    return (
      <div className="p-6 text-center text-gray-500 dark:text-gray-400">
        Loading vehicle data...
      </div>
    );
  }

  const { metrics, climate, navigation, media } = vehicleState;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
      {/* Battery & Range */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-3">
          <Battery className="w-5 h-5 text-green-600" />
          <h3 className="font-semibold text-gray-900 dark:text-white">Battery & Range</h3>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">Battery Level</span>
            <span className="text-lg font-bold text-gray-900 dark:text-white">
              {metrics.battery_level}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all"
              style={{ width: `${metrics.battery_level}%` }}
            />
          </div>
          <div className="flex justify-between items-center pt-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">Range</span>
            <span className="text-lg font-bold text-gray-900 dark:text-white">
              {metrics.range_miles} mi
            </span>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {metrics.charging_status === "charging" && "⚡ Charging..."}
            {metrics.charging_status === "fast_charging" && "⚡ Fast Charging..."}
          </div>
        </div>
      </div>

      {/* Climate Control */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-3">
          <ThermometerSun className="w-5 h-5 text-orange-600" />
          <h3 className="font-semibold text-gray-900 dark:text-white">Climate</h3>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">Temperature</span>
            <span className="text-2xl font-bold text-gray-900 dark:text-white">
              {climate.temperature}°F
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">Fan Speed</span>
            <span className="text-gray-900 dark:text-white">{climate.fan_speed} / 5</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">Mode</span>
            <span className="text-gray-900 dark:text-white capitalize">{climate.mode}</span>
          </div>
          {climate.seat_heating.driver > 0 && (
            <div className="text-xs text-orange-500 pt-1">
              🔥 Driver seat heating: Level {climate.seat_heating.driver}
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-3">
          <Navigation className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900 dark:text-white">Navigation</h3>
        </div>
        <div className="space-y-2">
          {navigation.route_active ? (
            <>
              <div className="text-sm text-gray-600 dark:text-gray-400">Destination</div>
              <div className="text-md font-semibold text-gray-900 dark:text-white">
                {navigation.destination}
              </div>
              <div className="flex justify-between items-center pt-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">ETA</span>
                <span className="text-gray-900 dark:text-white">{navigation.eta_minutes} min</span>
              </div>
              {navigation.next_maneuver && (
                <div className="text-xs text-blue-600 dark:text-blue-400 pt-1">
                  ➜ {navigation.next_maneuver}
                </div>
              )}
            </>
          ) : (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              No active route
              <div className="text-xs pt-1">Current: {navigation.current_location}</div>
            </div>
          )}
        </div>
      </div>

      {/* Media */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-3">
          <Volume2 className="w-5 h-5 text-purple-600" />
          <h3 className="font-semibold text-gray-900 dark:text-white">Media</h3>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">Status</span>
            <span className="text-gray-900 dark:text-white">
              {media.playing ? "▶ Playing" : "⏸ Paused"}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">Source</span>
            <span className="text-gray-900 dark:text-white capitalize">{media.source}</span>
          </div>
          {media.track_title && (
            <div className="pt-2">
              <div className="text-sm font-semibold text-gray-900 dark:text-white">
                {media.track_title}
              </div>
              {media.artist && (
                <div className="text-xs text-gray-500 dark:text-gray-400">{media.artist}</div>
              )}
            </div>
          )}
          {media.station && (
            <div className="text-sm text-gray-900 dark:text-white">{media.station}</div>
          )}
          <div className="flex items-center gap-2 pt-2">
            <Volume2 className="w-4 h-4 text-gray-500" />
            <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
              <div
                className="bg-purple-600 h-1.5 rounded-full transition-all"
                style={{ width: `${(media.volume / 30) * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-600 dark:text-gray-400">{media.volume}</span>
          </div>
        </div>
      </div>

      {/* Tire Pressure */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-3">
          <Gauge className="w-5 h-5 text-gray-600" />
          <h3 className="font-semibold text-gray-900 dark:text-white">Tire Pressure</h3>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="text-center p-2 bg-gray-100 dark:bg-gray-700 rounded">
            <div className="text-xs text-gray-600 dark:text-gray-400">Front Left</div>
            <div className="font-semibold text-gray-900 dark:text-white">
              {metrics.tire_pressure.front_left} PSI
            </div>
          </div>
          <div className="text-center p-2 bg-gray-100 dark:bg-gray-700 rounded">
            <div className="text-xs text-gray-600 dark:text-gray-400">Front Right</div>
            <div className="font-semibold text-gray-900 dark:text-white">
              {metrics.tire_pressure.front_right} PSI
            </div>
          </div>
          <div className="text-center p-2 bg-gray-100 dark:bg-gray-700 rounded">
            <div className="text-xs text-gray-600 dark:text-gray-400">Rear Left</div>
            <div className="font-semibold text-gray-900 dark:text-white">
              {metrics.tire_pressure.rear_left} PSI
            </div>
          </div>
          <div className="text-center p-2 bg-gray-100 dark:bg-gray-700 rounded">
            <div className="text-xs text-gray-600 dark:text-gray-400">Rear Right</div>
            <div className="font-semibold text-gray-900 dark:text-white">
              {metrics.tire_pressure.rear_right} PSI
            </div>
          </div>
        </div>
      </div>

      {/* Warnings */}
      {metrics.warnings && metrics.warnings.length > 0 && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg shadow-md p-4 border border-yellow-200 dark:border-yellow-800">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-500" />
            <h3 className="font-semibold text-gray-900 dark:text-white">Active Warnings</h3>
          </div>
          <ul className="space-y-1">
            {metrics.warnings.map((warning, idx) => (
              <li key={idx} className="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-2">
                <span className="text-yellow-600">•</span>
                <span>{warning}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
