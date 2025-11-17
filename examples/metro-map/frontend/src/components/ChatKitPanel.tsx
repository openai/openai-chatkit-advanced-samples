import { ChatKit, useChatKit } from "@openai/chatkit-react";
import clsx from "clsx";
import { useCallback, useRef } from "react";

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
  const fitView = useMapStore((state) => state.fitView);

  const handleClientTool = useCallback(
    (toolCall: { name: string; params: Record<string, unknown> }) => {
      if (toolCall.name === "update_map") {
        const nextMap = toolCall.params.map as MetroMap | undefined;
        if (nextMap) {
          const mapChanged = !currentMap || currentMap.id !== nextMap.id;
          setMap(nextMap);
          if (mapChanged) {
            requestAnimationFrame(() => fitView());
          }
        }
        return { success: true };
      }
      return { success: false };
    },
    [currentMap, fitView, setMap]
  );

  const chatkit = useChatKit({
    api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY },
    theme: {
      density: "spacious",
      colorScheme: theme,
      color: {
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
