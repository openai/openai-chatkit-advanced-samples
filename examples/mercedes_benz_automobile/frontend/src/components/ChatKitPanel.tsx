import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { useCallback } from "react";
import type { ColorScheme } from "../hooks/useColorScheme";
import type { VehicleStateAction } from "../hooks/useVehicleState";
import {
  CHATKIT_API_DOMAIN_KEY,
  CHATKIT_API_URL,
  GREETING,
  PLACEHOLDER_INPUT,
  STARTER_PROMPTS,
} from "../lib/config";

interface ChatKitPanelProps {
  theme: ColorScheme;
  onVehicleAction: (action: VehicleStateAction) => void;
  onResponseEnd?: () => void;
}

export function ChatKitPanel({ theme, onVehicleAction, onResponseEnd }: ChatKitPanelProps) {
  const handleClientTool = useCallback(
    async (invocation: { name: string; params: unknown }) => {
      console.log("Client tool invoked:", invocation);

      // Handle all client tool calls from the backend
      switch (invocation.name) {
        case "update_climate_ui":
        case "update_navigation_ui":
        case "update_vehicle_status_ui":
        case "update_media_ui":
        case "update_ambient_lighting_ui":
        case "update_assistance_ui":
        case "highlight_warning_ui":
        case "update_map_locations_ui":
          onVehicleAction({
            type: invocation.name,
            payload: invocation.params,
          });
          return { success: true };

        default:
          console.warn("Unknown client tool:", invocation.name);
          return { success: false };
      }
    },
    [onVehicleAction]
  );

  const chatkit = useChatKit({
    api: {
      url: CHATKIT_API_URL,
      domainKey: CHATKIT_API_DOMAIN_KEY,
    },
    theme,
    startScreen: {
      greeting: GREETING,
      prompts: STARTER_PROMPTS,
    },
    composer: {
      placeholder: PLACEHOLDER_INPUT,
    },
    onClientTool: handleClientTool,
    onResponseEnd: onResponseEnd,
    onError: ({ error }) => {
      console.error("ChatKit error:", error);
    },
  });

  return (
    <div className="h-full w-full bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 shadow-lg overflow-hidden">
      <ChatKit control={chatkit.control} className="h-full w-full" />
    </div>
  );
}
