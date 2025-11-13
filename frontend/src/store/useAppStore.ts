import { create } from "zustand";

import { CAT_STATE_API_URL, THEME_STORAGE_KEY } from "../lib/config";
import type { CatSpeechPayload, CatStatePayload } from "../lib/cat";
import { DEFAULT_CAT_STATE } from "../lib/cat";
import confetti from "canvas-confetti";

export type ColorScheme = "light" | "dark";

type SpeechState = (CatSpeechPayload & { id: number }) | null;

type AppState = {
  scheme: ColorScheme;
  setScheme: (scheme: ColorScheme) => void;
  threadId: string | null;
  setThreadId: (threadId: string | null) => void;
  cat: CatStatePayload;
  refreshCat: (overrideId?: string | null) => Promise<CatStatePayload | undefined>;
  applyCatUpdate: (update: Partial<CatStatePayload>) => void;
  speech: SpeechState;
  setSpeech: (payload: CatSpeechPayload) => void;
  flashMessage: string | null;
  setFlashMessage: (message: string | null) => void;
};

const SPEECH_TIMEOUT_MS = 10_000;
const FLASH_TIMEOUT_MS = 10_000;

let speechTimer: ReturnType<typeof setTimeout> | null = null;
let flashTimer: ReturnType<typeof setTimeout> | null = null;

function clearSpeechTimer() {
  if (speechTimer) {
    clearTimeout(speechTimer);
    speechTimer = null;
  }
}

function clearFlashTimer() {
  if (flashTimer) {
    clearTimeout(flashTimer);
    flashTimer = null;
  }
}

function getInitialScheme(): ColorScheme {
  if (typeof window === "undefined") {
    return "light";
  }
  const stored = window.localStorage.getItem(THEME_STORAGE_KEY) as ColorScheme | null;
  if (stored === "light" || stored === "dark") {
    return stored;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function syncSchemeWithDocument(scheme: ColorScheme) {
  if (typeof document === "undefined" || typeof window === "undefined") {
    return;
  }
  const root = document.documentElement;
  if (scheme === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
  window.localStorage.setItem(THEME_STORAGE_KEY, scheme);
}

function celebrateReveal() {
  confetti({
    particleCount: 50,
    spread: 100,
    origin: { y: 0.7 },
    zIndex: 1000,
    scalar: 0.9,
  });
}

export const useAppStore = create<AppState>((set, get) => {
  const initialScheme = getInitialScheme();
  syncSchemeWithDocument(initialScheme);

  return {
    scheme: initialScheme,
    setScheme: (scheme) => {
      syncSchemeWithDocument(scheme);
      set({ scheme });
    },
    threadId: null,
    setThreadId: (threadId) => {
      const previousId = get().threadId;
      if (previousId === threadId) {
        return;
      }
      clearSpeechTimer();
      clearFlashTimer();
      set({ threadId, speech: null, flashMessage: null });
      void get().refreshCat(threadId ?? null);
    },
    cat: DEFAULT_CAT_STATE,
    applyCatUpdate: (update) => {
      const prev = get().cat
      if (prev.name === "Unnamed Cat" && update.name !== prev.name) {
        celebrateReveal();
      }

      if (
        (prev.energy < 10 || prev.happiness < 10 || prev.cleanliness < 10) &&
        (update.energy === 10 && update.happiness === 10 && update.cleanliness === 10)) {
        const heart = confetti.shapeFromText({ text: '❤️', scalar: 2 });
        confetti({
          scalar: 2,
          particleCount: 10,
          flat: true,
          gravity: 0.5,
          spread: 120,
          origin: { y: 0.7 },
          zIndex: 1000,
          shapes: [heart],
        });
      }

      set((state) => ({
        cat: {
          ...state.cat,
          ...update,
          updatedAt: update.updatedAt ?? new Date().toISOString(),
        },
      }));
    },
    refreshCat: async (overrideId) => {
      const id = overrideId ?? get().threadId;
      if (!id) {
        set({
          cat: {
            ...DEFAULT_CAT_STATE,
            threadId: null,
            updatedAt: new Date().toISOString(),
          },
        });
        return;
      }
      try {
        const response = await fetch(`${CAT_STATE_API_URL}/${encodeURIComponent(id)}`);
        if (!response.ok) {
          throw new Error(`Failed to load cat state (${response.status})`);
        }
        const data = (await response.json()) as { cat?: CatStatePayload };
        if (data?.cat) {
          const prev = get().cat
          if (prev.name === "Unnamed Cat" && data.cat.name !== prev.name) {
            celebrateReveal();
          }

          set({ cat: data.cat });
          return data.cat;
        }
      } catch (error) {
        console.error("Failed to fetch cat state", error);
      }
    },
    speech: null,
    setSpeech: (payload) => {
      const speechPayload: SpeechState =
        payload ? { ...payload, id: Date.now() } : null;

      clearSpeechTimer();
      clearFlashTimer();
      set({ speech: speechPayload, flashMessage: null });

      if (!speechPayload) {
        return;
      }

      speechTimer = setTimeout(() => {
        set({ speech: null });
        speechTimer = null;
      }, SPEECH_TIMEOUT_MS);
    },
    flashMessage: null,
    setFlashMessage: (message) => {
      if (!message) {
        clearFlashTimer();
        set({ flashMessage: null });
        return;
      }

      clearFlashTimer();
      clearSpeechTimer();
      set({ flashMessage: message, speech: null });

      flashTimer = setTimeout(() => {
        set({ flashMessage: null });
        flashTimer = null;
      }, FLASH_TIMEOUT_MS);
    },
  };
});
