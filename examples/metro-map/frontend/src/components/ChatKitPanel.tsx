import { ChatKit, HeaderIcon, HeaderOption, StartScreenPrompt, useChatKit, type Entity } from "@openai/chatkit-react";
import clsx from "clsx";
import { useCallback, useMemo } from "react";

import {
  CHATKIT_API_DOMAIN_KEY,
  CHATKIT_API_URL,
  getGreeting,
  getStartScreenPrompts,
  getPlaceholder,
} from "../lib/config";
import { OPENAI_SANS_SOURCES } from "../lib/fonts";
import type { MetroMap } from "../lib/map";
import { useAppStore } from "../store/useAppStore";
import { useMapStore } from "../store/useMapStore";

export type ChatKit = ReturnType<typeof useChatKit>;

type ChatKitPanelProps = {
  onChatKitReady: (chatkit: ChatKit) => void;
  className?: string;
};

const useStartScreenOption = () => {
  const selectedStationIds = useMapStore((state) => state.selectedStationIds);
  const prompts = useMemo(() => {
    return getStartScreenPrompts(selectedStationIds);
  }, [selectedStationIds]);

  const greeting = useMemo(() => {
    return getGreeting(selectedStationIds);
  }, [selectedStationIds]);

  return { prompts, greeting };
};

export function ChatKitPanel({
  onChatKitReady,
  className,
}: ChatKitPanelProps) {
  const theme = useAppStore((state) => state.scheme);
  const activeThread = useAppStore((state) => state.threadId);
  const setThreadId = useAppStore((state) => state.setThreadId);
  const setMap = useMapStore((state) => state.setMap);
  const currentMap = useMapStore((state) => state.map);
  const selectedStationIds = useMapStore((state) => state.selectedStationIds);
  const focusStation = useMapStore((state) => state.focusStation);
  const setLocationSelectLineId = useMapStore((state) => state.setLocationSelectLineId);
  const clearLocationSelectMode = useMapStore((state) => state.clearLocationSelectMode);
  const lockInteraction = useMapStore((state) => state.lockInteraction);
  const unlockInteraction = useMapStore((state) => state.unlockInteraction);
  const scheme = useAppStore((state) => state.scheme);
  const setScheme = useAppStore((state) => state.setScheme);
  const setChatkit = useAppStore((state) => state.setChatkit);

  const headerRightAction = useMemo((): HeaderOption['rightAction'] => {
    if (scheme === "dark") {
      return {
        icon: "dark-mode",
        onClick: () => {
          setScheme("light");
        }
      }
    }
    return {
      icon: "light-mode",
      onClick: () => {
        setScheme("dark");
      }
    }
  }, [scheme, setScheme]);

  const stationEntities = useMemo<Entity[]>(() => {
    if (!currentMap) return [];
    return currentMap.stations.map((station) => {
      return {
        id: station.id,
        title: station.name,
        interactive: true,
        group: "Stations",
        data: {
          type: "station",
          station_id: station.id,
          name: station.name,
        },
      };
    });
  }, [currentMap]);

  const searchStations = useCallback(
    async (query: string) => {
      if (!stationEntities.length) return [];
      const normalized = query.trim().toLowerCase();
      if (!normalized) return stationEntities;
      return stationEntities.filter((entity) => {
        const lineNames = entity.data?.line_names?.toLowerCase() ?? "";
        return (
          entity.title.toLowerCase().includes(normalized) ||
          entity.id.toLowerCase().includes(normalized) ||
          lineNames.includes(normalized)
        );
      });
    },
    [stationEntities]
  );

  const startScreenOption = useStartScreenOption();

  const handleEntityClick = useCallback(
    (entity: Entity) => {
      const stationId = (entity.data?.station_id || entity.id || "").trim();
      if (stationId) {
        focusStation(stationId, currentMap ?? undefined);
      }
    },
    [currentMap, focusStation]
  );

  const handleClientTool = useCallback(
    ({name}: { name: string; params: Record<string, unknown> }) => {
      // Return the station ids that are currently selected on the canvas
      // so that the agent can take them as input for the continued response.
      if (name === "get_selected_stations") {
        return { stationIds: selectedStationIds };
      }
    },
    [clearLocationSelectMode, focusStation, selectedStationIds, setMap]
  );

  const handleClientEffect = useCallback(
    ({name, data}: { name: string; data: Record<string, unknown> }) => {
      if (name === "location_select_mode") {
        const lineId = data.lineId as string | undefined;
        if (lineId) {
          setLocationSelectLineId(lineId);
        }
      }
      if (name === "add_station") {
        const stationId = data.stationId as string | undefined;
        const nextMap = data.map as MetroMap | undefined;
        clearLocationSelectMode();

        if (nextMap) {
          setMap(nextMap);
        }

        if (stationId) {
          requestAnimationFrame(() => focusStation(stationId, nextMap));
        }
      }
    },
    [clearLocationSelectMode, focusStation, setLocationSelectLineId, setMap]
  );

  const chatkit = useChatKit({
    api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY },
    header: {
      title: {enabled: false},
      rightAction: headerRightAction,
    },
    theme: {
      density: "spacious",
      colorScheme: theme,
      color: {
        ...(theme === "dark" ? {
          surface: {
            background: "#0d1117",
            foreground: "#1d222b"
          }
        } : null),
        accent: {
          primary: "#0ea5e9",
          level: 1,
        },
      },
      typography: {
        fontFamily: "OpenAI Sans, sans-serif",
        fontSources: OPENAI_SANS_SOURCES,
      },
      radius: "pill",
    },
    startScreen: startScreenOption,
    composer: {
      placeholder: getPlaceholder(Boolean(activeThread)),
    },
    entities: {
      onTagSearch: searchStations,
      onClick: handleEntityClick,
    },
    threadItemActions: {
      feedback: false,
    },
    onClientTool: handleClientTool,
    onThreadChange: ({ threadId }) => {
      setThreadId(threadId);
    },
    onError: ({ error }) => {
      console.error("ChatKit error", error);
    },
    onReady: () => {
      onChatKitReady?.(chatkit);
      setChatkit(chatkit);
    },
    onEffect: handleClientEffect,
    onResponseStart: () => {
      lockInteraction();
    },
    onResponseEnd: () => {
      unlockInteraction();
    },
  });

  return (
    <div className="flex-1 relative h-full w-full overflow-hidden py-1 pr-1">
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
