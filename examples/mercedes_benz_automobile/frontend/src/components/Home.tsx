import { Car } from "lucide-react";
import { useCallback } from "react";
import type { ColorScheme } from "../hooks/useColorScheme";
import { useVehicleState } from "../hooks/useVehicleState";
import { ChatKitPanel } from "./ChatKitPanel";
import { Dashboard } from "./Dashboard";
import { ThemeToggle } from "./ThemeToggle";

interface HomeProps {
  scheme: ColorScheme;
  onToggleTheme: () => void;
}

export default function Home({ scheme, onToggleTheme }: HomeProps) {
  const { vehicleState, refresh, performAction } = useVehicleState();

  const handleVehicleAction = useCallback(
    (action: { type: string; payload: unknown }) => {
      performAction(action);
    },
    [performAction]
  );

  const handleResponseEnd = useCallback(() => {
    // Optionally refresh vehicle state after AI response
    // For real-time updates, we rely on client tool calls instead
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Car className="w-8 h-8 text-gray-900 dark:text-white" />
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  Mercedes-Benz EQS
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">Voice Assistant</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <ThemeToggle scheme={scheme} onToggle={onToggleTheme} />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* ChatKit Panel - Left Side */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 h-[calc(100vh-8rem)]">
              <ChatKitPanel
                theme={scheme}
                onVehicleAction={handleVehicleAction}
                onResponseEnd={handleResponseEnd}
              />
            </div>
          </div>

          {/* Dashboard - Right Side */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 shadow-lg">
              <div className="p-6 border-b border-gray-200 dark:border-gray-800">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Vehicle Dashboard
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Real-time vehicle status and controls
                </p>
              </div>
              <Dashboard vehicleState={vehicleState} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
