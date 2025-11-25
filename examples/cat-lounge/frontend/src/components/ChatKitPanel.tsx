import { ChatKit, useChatKit } from "@openai/chatkit-react";
import clsx from "clsx";
import type { Widgets } from "@openai/chatkit";
import { useCallback, useRef } from "react";

import {
  CHATKIT_API_DOMAIN_KEY,
  CHATKIT_API_URL,
  GREETING,
  STARTER_PROMPTS,
  getPlaceholder,
} from "../lib/config";
import type { CatStatePayload } from "../lib/cat";
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

  // Select state
  const theme = useAppStore((state) => state.scheme);
  const activeThread = useAppStore((state) => state.threadId);
  const setSpeech = useAppStore((state) => state.setSpeech);
  const setFlashMessage = useAppStore((state) => state.setFlashMessage);
  const setThreadId = useAppStore((state) => state.setThreadId);
  const cat = useAppStore((state) => state.cat);
  const refresh = useAppStore((state) => state.refreshCat);
  const applyUpdate = useAppStore((state) => state.applyCatUpdate);

  const handleStatusUpdate = useCallback(
    (state: CatStatePayload, flash?: string) => {
      applyUpdate(state);

      if (flash) {
        setFlashMessage(flash);
      }
    },
    [applyUpdate, setFlashMessage]
  );

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
          handleStatusUpdate(data, `Now called ${data.name}`);
        }
        return;
      }
    },
    [refresh, handleStatusUpdate, activeThread]
  );

  const handleClientEffect = useCallback(({name, data}: {
    name: string;
    data: Record<string, unknown>;
  }) => {
      if (name === "update_cat_status") {
        const catState = data.state as CatStatePayload | undefined;
        if (catState) {
          handleStatusUpdate(catState, data.flash as string | undefined);
        }
      }

      if (name === "cat_say") {
        const message = String(data.message ?? "");
        if (message) {
          setSpeech({message});
        }
      }
    }, [])

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
    onThreadChange: ({ threadId }) => setThreadId(threadId),
    onError: ({ error }) => {
      // ChatKit handles displaying the error to the user
      console.error("ChatKit error", error);
    },
    onReady: () => {
      onChatKitReady?.(chatkit);
    },
    onEffect: handleClientEffect,
  });
  chatkitRef.current = chatkit;

  return (
    <div className={clsx("relative h-full w-full overflow-hidden", className)}>
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
