import { ChatKit, useChatKit } from "@openai/chatkit-react";
import type { StartScreenPrompt } from "@openai/chatkit";

import type { ColorScheme } from "../hooks/useColorScheme";
import {
  SUPPORT_CHATKIT_API_DOMAIN_KEY,
  SUPPORT_CHATKIT_API_URL,
} from "../lib/config";
import { IMAGE_ATTACHMENT_ACCEPT, MAX_UPLOAD_BYTES } from "../lib/uploads";

type ChatKitPanelProps = {
  theme: ColorScheme;
  greeting: string;
  prompts: StartScreenPrompt[];
};

export function ChatKitPanel({ theme, greeting, prompts }: ChatKitPanelProps) {
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
      placeholder: "Ask a question about TPT...",
      attachments: {
        enabled: true,
        maxSize: MAX_UPLOAD_BYTES,
        accept: IMAGE_ATTACHMENT_ACCEPT,
      },
      dictation: { enabled: true },
    },
    threadItemActions: {
      feedback: false,
    },
    onError: ({ error }) => {
      console.error("ChatKit error", error);
    },
  });

  return (
    <div className="relative h-full w-full overflow-hidden border border-slate-200/60 bg-white shadow-card dark:border-slate-800/70 dark:bg-slate-900">
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
