import { ChatKit, useChatKit, Widgets, type Entity } from "@openai/chatkit-react";
import type { Command } from "@openai/chatkit";
import clsx from "clsx";
import { useCallback, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  CHATKIT_API_DOMAIN_KEY,
  CHATKIT_API_URL,
  GREETING,
  STARTER_PROMPTS,
  TOOL_CHOICES,
  getPlaceholder,
} from "../lib/config";
import { LORA_SOURCES } from "../lib/fonts";
import { useTags } from "../hooks/useTags";
import { useAppStore } from "../store/useAppStore";

export type ChatKit = ReturnType<typeof useChatKit>;

type ChatKitPanelProps = {
  onChatKitReady: (chatkit: ChatKit) => void;
  className?: string;
};

const FIND_EVENTS_COMMAND: Command = {
  id: "find-events",
  label: "Find events",
  description: "Search Foxhollow events by date range",
  icon: "calendar",
};

const EVENT_RANGE_COMMANDS: Command[] = [
  { id: "find-events-today", label: "Today", icon: "calendar" },
  { id: "find-events-weekend", label: "This weekend", icon: "calendar" },
  { id: "find-events-next-week", label: "Next week", icon: "calendar" },
  { id: "find-events-custom", label: "Choose dates", icon: "calendar" },
];

const EVENT_RANGE_PROMPTS: Record<string, string> = {
  "find-events-today": "Find events happening today.",
  "find-events-weekend": "Find events happening this weekend.",
  "find-events-next-week": "Find events happening next week.",
  "find-events-custom": "Find events between [start date] and [end date].",
};

const commandMatchesQuery = (command: Command, query: string) => {
  const normalizedQuery = query.trim().toLowerCase();
  return (
    normalizedQuery.length === 0 ||
    command.id.toLowerCase().includes(normalizedQuery) ||
    command.label.toLowerCase().includes(normalizedQuery) ||
    command.description?.toLowerCase().includes(normalizedQuery)
  );
};

export function ChatKitPanel({
  onChatKitReady,
  className,
}: ChatKitPanelProps) {
  const chatkitRef = useRef<ReturnType<typeof useChatKit> | null>(null);
  const [lastActionedArticle, setLastActionedArticle] = useState<string | null>(null);
  const navigate = useNavigate();
  const { search, getPreview } = useTags();

  const theme = useAppStore((state) => state.scheme);
  const activeThread = useAppStore((state) => state.threadId);
  const setThreadId = useAppStore((state) => state.setThreadId);
  const articleId = useAppStore((state) => state.articleId);

  const customFetch = useMemo(() => {
    return async (input: RequestInfo | URL, init?: RequestInit) => {
      const headers = new Headers(init?.headers ?? {});
      const currentArticleId = articleId ?? "featured";
      if (currentArticleId) {
        headers.set("article-id", currentArticleId);
      } else {
        headers.delete("article-id");
      }
      return fetch(input, {
        ...init,
        headers,
      });
    };
  }, [articleId]);

  const handleWidgetAction = useCallback(
    async (
      action: { type: string; payload?: Record<string, unknown> },
      widgetItem: { id: string; widget: Widgets.Card | Widgets.ListView }
    ) => {
      switch (action.type) {
        case "open_article": {
          const id = action.payload?.id;
          if (typeof id === "string" && id) {
            navigate(`/article/${id}`);
            const chatkit = chatkitRef.current;

              if (chatkit) {
                if (id !== lastActionedArticle) {
                  await chatkit.sendCustomAction(action, widgetItem.id);
                  setLastActionedArticle(id);
                }
              }
            }
            break;
        }
      }
    },
    [navigate, lastActionedArticle]
  );

  const handleEntityClick = useCallback(
    (entity: Entity) => {
      const rawId = entity.data?.["article_id"];
      const articleId = typeof rawId === "string" ? rawId.trim() : "";
      if (articleId) {
        navigate(`/article/${articleId}`);
      }
    },
    [navigate]
  );

  const chatkit = useChatKit({
    api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY, fetch: customFetch },
    theme: {
      density: "spacious",
      colorScheme: theme,
      color: {
        grayscale: {
          hue: 0,
          tint: 0,
          shade: theme === "dark" ? -1 : 0,
        },
        accent: {
          primary: "#ff5f42",
          level: 1,
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
      tools: TOOL_CHOICES,
    },
    commands: {
      enabled: true,
      onSearch: async (query) =>
        commandMatchesQuery(FIND_EVENTS_COMMAND, query)
          ? [FIND_EVENTS_COMMAND]
          : [],
      onSelect: async (command) => {
        if (command.id === "find-events") {
          return { type: "menu", commands: EVENT_RANGE_COMMANDS };
        }

        const prompt = EVENT_RANGE_PROMPTS[command.id];
        if (prompt) {
          await chatkitRef.current?.setComposerValue({
            text: prompt,
            selectedToolId: "event_finder",
          });
        }
      },
    },
    entities: {
      onTagSearch: search,
      showComposerMenu: true,
      onRequestPreview: getPreview,
      onClick: handleEntityClick,
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
    <div className={clsx("relative h-full w-full overflow-hidden", className)}>
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
