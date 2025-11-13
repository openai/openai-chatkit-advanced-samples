import { ChatKit, useChatKit } from "@openai/chatkit-react";
import type { Widgets } from "@openai/chatkit";
import { useCallback, useRef } from "react";
import { useCatState } from "../hooks/useCatState";

import {
  CHATKIT_API_DOMAIN_KEY,
  CHATKIT_API_URL,
  GREETING,
  STARTER_PROMPTS,
  getPlaceholder,
} from "../lib/config";
import type { ColorScheme } from "../hooks/useColorScheme";
import type { CatSpeechPayload, CatStatePayload } from "../lib/cat";

export type ChatKit = ReturnType<typeof useChatKit>;

type ChatKitPanelProps = {
  theme: ColorScheme;
  activeThread: string | null;
  onThreadChange: (threadId: string | null) => void;
  onStatusUpdate: (state: CatStatePayload, flash?: string, named?: boolean) => void;
  onSpeech: (payload: CatSpeechPayload) => void;
  onChatKitReady: (chatkit: ChatKit) => void;
};

export function ChatKitPanel({
  theme,
  activeThread,
  onThreadChange,
  onStatusUpdate,
  onSpeech,
  onChatKitReady,
}: ChatKitPanelProps) {
  const chatkitRef = useRef<ReturnType<typeof useChatKit> | null>(null);
  const { cat, refresh } = useCatState();

  const handleWidgetAction = useCallback(
    async (
      action: { type: string; payload?: Record<string, unknown> },
      widgetItem: { id: string; widget: Widgets.Card | Widgets.ListView }
    ) => {
      const chatkit = chatkitRef.current;
      if (!chatkit) {
        return;
      }
      // When the user clicks "Suggest more names", the client action handler simply
      // sends a user message using a chatkit command.
      if (action.type === "cats.more_names") {
        await chatkit.sendUserMessage({ text: "More name suggestions, please" });
        return;
      }
      // This is a more complex client action handler that:
      // - Invokes the server action handler
      // - Then fetches the latest post-server-action cat status
      if (action.type === "cats.select_name") {
        if (!activeThread) {
          console.warn("Ignoring name selection without an active thread.");
          return;
        }
        // Send the server action.
        await chatkit.sendCustomAction(action, widgetItem.id);
        // Then fetch the latest cat status so that we can reflect the update client-side.
        const data = await refresh();
        if (data) {
          onStatusUpdate(data, `Now called ${data.name}`);
        }
        return;
      }
    },
    [refresh, onStatusUpdate, activeThread]
  );

  const handleClientToolCall = useCallback((toolCall: {
    name: string;
    params: Record<string, unknown>;
  }) => {
      if (toolCall.name === "update_cat_status") {
        const data = toolCall.params.state as CatStatePayload | undefined;
        if (data) {
          onStatusUpdate(data, toolCall.params.flash as string | undefined);
        }
        return { success: true };
      }

      if (toolCall.name === "cat_say") {
        const message = String(toolCall.params.message ?? "");
        if (message) {
          onSpeech({
            message,
            mood: toolCall.params.mood as string | undefined,
          });
        }
        return { success: true };
      }
      return { success: false };
    }, [cat.name])

  const chatkit = useChatKit({
    api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY },
    theme: {
      density: "spacious",
      colorScheme: theme,
      color: {
        grayscale: {
          hue: 220,
          tint: 6,
          shade: theme === "dark" ? -1 : -4,
        },
        accent: {
          primary: theme === "dark" ? "#f1f5f9" : "#0f172a",
          level: 1,
        },
      },
      radius: "round",
    },
    startScreen: {
      greeting: GREETING,
      prompts: STARTER_PROMPTS,
    },
    composer: {
      placeholder: getPlaceholder(cat.name),
    },
    threadItemActions: {
      feedback: false,
    },
    widgets: {
      onAction: handleWidgetAction,
    },
    onClientTool: handleClientToolCall,
    onThreadChange: ({ threadId }) => onThreadChange(threadId),
    onError: ({ error }) => {
      // ChatKit handles displaying the error to the user
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
