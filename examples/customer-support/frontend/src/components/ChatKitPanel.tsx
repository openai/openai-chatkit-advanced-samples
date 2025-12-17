import { ChatKit, useChatKit } from "@openai/chatkit-react";
import type { StartScreenPrompt } from "@openai/chatkit";
import { useCallback, useRef } from "react";

import type { CustomerProfile } from "../hooks/useCustomerContext";
import type { ColorScheme } from "../hooks/useColorScheme";
import {
  SUPPORT_CHATKIT_API_DOMAIN_KEY,
  SUPPORT_CHATKIT_API_URL,
} from "../lib/config";
import { IMAGE_ATTACHMENT_ACCEPT, MAX_UPLOAD_BYTES } from "../lib/uploads";

export type ChatKitInstance = ReturnType<typeof useChatKit>;

type ChatKitPanelProps = {
  theme: ColorScheme;
  greeting: string;
  prompts: StartScreenPrompt[];
  onThreadChange: (threadId: string | null) => void;
  onResponseCompleted: () => void;
  onProfileUpdate: (profile: CustomerProfile) => void;
  onWidgetActionComplete?: () => void;
  onChatKitReady?: (chatkit: ChatKitInstance) => void;
};

export function ChatKitPanel({
  theme,
  greeting,
  prompts,
  onThreadChange,
  onResponseCompleted,
  onProfileUpdate,
  onWidgetActionComplete,
  onChatKitReady,
}: ChatKitPanelProps) {
  const chatkitRef = useRef<ReturnType<typeof useChatKit> | null>(null);

  const handleWidgetAction = useCallback(
    async (
      action: { type: string; payload?: Record<string, unknown> },
      widgetItem: { id: string }
    ): Promise<void> => {
      const instance = chatkitRef.current;
      if (!instance) {
        return;
      }

      await instance.sendCustomAction(action, widgetItem.id);
      onWidgetActionComplete?.();
    },
    [onWidgetActionComplete]
  );

  const handleEffect = useCallback(
    ({ name, data }: { name: string; data: Record<string, unknown> }) => {
      if (name === "customer_profile/update") {
        const nextProfile = data.profile as CustomerProfile | undefined;
        if (nextProfile) {
          onProfileUpdate(nextProfile);
        }
      }
    },
    [onProfileUpdate]
  );

  const chatkit = useChatKit({
    api: {
      url: SUPPORT_CHATKIT_API_URL,
      domainKey: SUPPORT_CHATKIT_API_DOMAIN_KEY,
      uploadStrategy: { type: "two_phase" },
    },
    theme: {
      colorScheme: theme,
      color: {
        grayscale: {
          hue: 220,
          tint: 6,
          shade: theme === "dark" ? -1 : -4,
        },
        accent: {
          primary: theme === "dark" ? "#f8fafc" : "#0f172a",
          level: 1,
        },
      },
      radius: "round",
    },
    startScreen: {
      greeting,
      prompts,
    },
    composer: {
      placeholder: "Ask the concierge a question",
      attachments: {
        enabled: true,
        maxSize: MAX_UPLOAD_BYTES,
        accept: IMAGE_ATTACHMENT_ACCEPT,
      },
    },
    threadItemActions: {
      feedback: false,
    },
    widgets: {
      onAction: handleWidgetAction,
    },
    onResponseEnd: () => {
      onResponseCompleted();
    },
    onThreadChange: ({ threadId }) => {
      onThreadChange(threadId ?? null);
    },
    onError: ({ error }) => {
      console.error("ChatKit error", error);
    },
    onReady: () => {
      onChatKitReady?.(chatkit);
    },
    onEffect: handleEffect,
  });
  chatkitRef.current = chatkit;

  return (
    <div className="relative h-full w-full overflow-hidden border border-slate-200/60 bg-white shadow-card dark:border-slate-800/70 dark:bg-slate-900">
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
