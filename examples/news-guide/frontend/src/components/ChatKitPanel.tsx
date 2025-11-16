import { ChatKit, useChatKit, Widgets, type Entity } from "@openai/chatkit-react";
import clsx from "clsx";
import { useCallback, useEffect, useMemo, useRef } from "react";
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

export function ChatKitPanel({
  onChatKitReady,
  className,
}: ChatKitPanelProps) {
  const chatkitRef = useRef<ReturnType<typeof useChatKit> | null>(null);
  const actionedWidgetsRef = useRef<Set<string>>(new Set());
  const navigate = useNavigate();
  const { search, getPreview } = useTags();

  const theme = useAppStore((state) => state.scheme);
  const activeThread = useAppStore((state) => state.threadId);
  const setThreadId = useAppStore((state) => state.setThreadId);
  const articleId = useAppStore((state) => state.articleId);

  const activeArticleRef = useRef<string | null>(articleId);
  useEffect(() => {
    activeArticleRef.current = articleId ?? "featured";
  }, [articleId]);

  const customFetch = useMemo(() => {
    return async (input: RequestInfo | URL, init?: RequestInit) => {
      const headers = new Headers(init?.headers ?? {});
      const articleId = activeArticleRef.current;
      if (articleId) {
        headers.set("article-id", articleId);
      } else {
        headers.delete("article-id");
      }
      return fetch(input, {
        ...init,
        headers,
      });
    };
  }, []);

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
              // `open_article` can be invoked as many times as the user wants and we'll always
              // navigate to the article, BUT we only want to stream back a follow-up message
              // once per actioned article (otherwise it looks spammy).
              const key = `${widgetItem.id}:${id}`;
              if (!actionedWidgetsRef.current.has(key)) {
                await chatkit.sendCustomAction(action, widgetItem.id);
                actionedWidgetsRef.current.add(key);
              }
            }
          }
          break;
        }
      }
    },
    [navigate]
  );

  const handleEntityClick = useCallback(
    (entity: Entity) => {
      const rawId = entity.data?.["article_id"] ?? entity.id;
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
    entities: {
      onTagSearch: search,
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
