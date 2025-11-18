import type { UseChatKitReturn } from "@openai/chatkit-react";
import { create } from "zustand";

export type ColorScheme = "light" | "dark";

type AppState = {
  scheme: ColorScheme;
  setScheme: (scheme: ColorScheme) => void;
  threadId: string | null;
  setThreadId: (threadId: string | null) => void;
  chatkit: UseChatKitReturn | null;
  setChatkit: (chatkit: UseChatKitReturn | null) => void;
};

function getInitialScheme(): ColorScheme {
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function syncSchemeWithDocument(scheme: ColorScheme) {
  const root = document.documentElement;
  if (scheme === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
}

export const useAppStore = create<AppState>((set) => {
  const initialScheme = getInitialScheme();
  syncSchemeWithDocument(initialScheme);

  return {
    scheme: initialScheme,
    setScheme: (scheme) => {
      syncSchemeWithDocument(scheme);
      set({ scheme });
    },
    threadId: null,
    setThreadId: (threadId) => set({ threadId }),
    chatkit: null,
    setChatkit: (chatkit) => set({ chatkit }),
  };
});
