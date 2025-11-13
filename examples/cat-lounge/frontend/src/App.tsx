import clsx from "clsx";
import { useCallback, useRef } from "react";

import { CatStatusPanel } from "./components/CatStatusPanel";
import { ChatKitPanel } from "./components/ChatKitPanel";
import type { ChatKit } from "./components/ChatKitPanel";
import { ThemeToggle } from "./components/ThemeToggle";
import { useAppStore } from "./store/useAppStore";

export default function App() {
  const chatkitRef = useRef<ChatKit | null>(null);

  const scheme = useAppStore((state) => state.scheme);
  const handleQuickAction = useCallback(
    async (message: string) => {
      if (!chatkitRef.current) {
        return;
      }
      await chatkitRef.current.sendUserMessage({ text: message });
    },
    []
  );

  const containerClass = clsx(
    "h-full bg-gradient-to-br transition-colors duration-300",
    scheme === "dark"
      ? "from-slate-900 via-slate-950 to-slate-850 text-slate-100"
      : "from-slate-100 via-white to-slate-200 text-slate-900"
  );
  const headerBarClass = clsx(
    "sticky top-0 z-30 w-full border-b backdrop-blur",
    scheme === "dark"
      ? "bg-slate-950/80 border-slate-800/70 text-slate-100"
      : "bg-white/90 border-slate-200/70 text-slate-900"
  );

  return (
    <div className={containerClass}>
      <header className={headerBarClass}>
        <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-4 px-6 py-5 pr-20 sm:flex-row sm:items-center sm:gap-6 lg:py-6">
          <h1 className="text-lg font-semibold uppercase tracking-wide">Cozy cat lounge</h1>
          <p className="flex-1 text-sm text-slate-600 dark:text-slate-300">
            Chat with the agent to keep the cat happy.
          </p>
          <div className="absolute right-6 top-4">
            <ThemeToggle />
          </div>
        </div>
      </header>
      <div className="mx-auto flex w-full max-w-6xl flex-col-reverse gap-10 px-6 pb-10 pt-6 md:py-10 lg:flex-row">
        <div className="relative w-full md:w-[45%] flex h-[calc(90vh-100px)] items-stretch overflow-hidden rounded-3xl bg-white/80 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.6)] ring-1 ring-slate-200/60 backdrop-blur md:h-[calc(90vh-100px)] dark:bg-slate-900/70 dark:shadow-[0_45px_90px_-45px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
          <ChatKitPanel onChatKitReady={(chatkit) => chatkitRef.current = chatkit} />
        </div>
        <div className="relative flex-1 w-full md:w-[45%] flex h-[calc(90vh-100px)] items-stretch overflow-hidden rounded-3xl bg-white/80 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.6)] ring-1 ring-slate-200/60 backdrop-blur md:h-[calc(90vh-100px)] dark:bg-slate-900/70 dark:shadow-[0_45px_90px_-45px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
          <CatStatusPanel onQuickAction={handleQuickAction} />
        </div>
      </div>
    </div>
  );
}
