import { ChatKit, useChatKit, type Entity } from "@openai/chatkit-react";
import clsx from "clsx";
import { useCallback, useMemo, useRef } from "react";

import {
  CHATKIT_API_DOMAIN_KEY,
  CHATKIT_API_URL,
  GREETING,
  STARTER_PROMPTS,
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

export function ChatKitPanel({
  onChatKitReady,
  className,
}: ChatKitPanelProps) {
  const chatkitRef = useRef<ReturnType<typeof useChatKit> | null>(null);

  const theme = useAppStore((state) => state.scheme);
  const activeThread = useAppStore((state) => state.threadId);
  const setThreadId = useAppStore((state) => state.setThreadId);
  const setMap = useMapStore((state) => state.setMap);
  const currentMap = useMapStore((state) => state.map);
  const focusStation = useMapStore((state) => state.focusStation);

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
    (toolCall: { name: string; params: Record<string, unknown> }) => {
      if (toolCall.name === "add_station") {
        const stationId = toolCall.params.stationId as string | undefined;
        const nextMap = toolCall.params.map as MetroMap | undefined;

        if (nextMap) {
          setMap(nextMap);
        }

        if (stationId) {
          requestAnimationFrame(() => focusStation(stationId, nextMap));
        }
        return { success: true };
      }
      return { success: false };
    },
    [focusStation, setMap]
  );

  const chatkit = useChatKit({
    api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY },
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
    startScreen: {
      greeting: GREETING,
      prompts: STARTER_PROMPTS,
    },
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
    onThreadChange: ({ threadId }) => setThreadId(threadId),
    onError: ({ error }) => {
      console.error("ChatKit error", error);
    },
    onReady: () => {
      onChatKitReady?.(chatkit);
    },
  });
  chatkitRef.current = chatkit;

  return (
    <div className={clsx("relative h-full w-full overflow-hidden", className)}>
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
