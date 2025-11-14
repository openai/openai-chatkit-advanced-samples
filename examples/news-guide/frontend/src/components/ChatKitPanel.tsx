import { ChatKit, useChatKit, Widgets } from "@openai/chatkit-react";
import { useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";

import {
  CHATKIT_API_DOMAIN_KEY,
  CHATKIT_API_URL,
  GREETING,
  STARTER_PROMPTS,
  getPlaceholder,
} from "../lib/config";
import { LORA_SOURCES } from "../lib/fonts";
import { useAppStore } from "../store/useAppStore";

export type ChatKit = ReturnType<typeof useChatKit>;

type ChatKitPanelProps = {
  onChatKitReady: (chatkit: ChatKit) => void;
};

export function ChatKitPanel({
  onChatKitReady,
}: ChatKitPanelProps) {
  const chatkitRef = useRef<ReturnType<typeof useChatKit> | null>(null);
  const navigate = useNavigate();

  const theme = useAppStore((state) => state.scheme);
  const activeThread = useAppStore((state) => state.threadId);
  const setThreadId = useAppStore((state) => state.setThreadId);

  const handleWidgetAction = useCallback(
    async (action: { type: string; payload?: Record<string, unknown>}, widgetItem: { id: string; widget: Widgets.Card | Widgets.ListView }) => {
      switch (action.type) {
        case "open_article":
          const articleId = action.payload?.id
          if (articleId) {
            navigate(`/article/${articleId}`);
          }
          break;
      }
    },
    [navigate]
  );

  const chatkit = useChatKit({
    api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY },
    theme: {
      density: "spacious",
      colorScheme: theme,
      color: {
        grayscale: {
          hue: 210,
          tint: 6,
          shade: theme === "dark" ? -1 : -4,
        },
        accent: {
          primary: theme === "dark" ? "#f8fafc" : "#020817",
          level: 2,
        },
      },
      typography: {
        fontFamily: "Lora, serif",
        fontSources: LORA_SOURCES,
      },
      radius: "sharp",
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
    widgets: {
      onAction: handleWidgetAction,
    },
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
    <div className="relative h-full w-full overflow-hidden">
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
