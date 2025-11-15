import clsx from "clsx";
import { useRef } from "react";
import { Link, Outlet, Route, Routes } from "react-router-dom";

import { ChatKitPanel } from "./components/ChatKitPanel";
import type { ChatKit } from "./components/ChatKitPanel";
import { NewsroomPanel } from "./components/NewsroomPanel";
import { ThemeToggle } from "./components/ThemeToggle";
import { useAppStore } from "./store/useAppStore";

function AppShell() {
  const chatkitRef = useRef<ChatKit | null>(null);
  const scheme = useAppStore((state) => state.scheme);

  const containerClass = clsx(
    "h-full flex min-h-screen flex-col transition-colors duration-300",
    scheme === "dark" ? "bg-[#1c1c1c] text-slate-100" : "bg-slate-100 text-slate-900"
  );
  const headerBarClass = clsx(
    "sticky top-0 z-30 w-full border-b shadow-sm",
    scheme === "dark"
      ? "border-slate-200 bg-[#1c1c1c] text-slate-100"
      : "border-slate-800 bg-white text-slate-900"
  );

  return (
    <div className={containerClass}>
      <div className={headerBarClass}>
        <div className="relative flex w-full flex-col gap-4 px-6 py-6 pr-24 sm:flex-row sm:items-center sm:gap-8">
          <span
            className="text-xl font-semibold uppercase tracking-[0.45em] text-slate-900 dark:text-slate-100"
          >
            The Foxhollow Dispatch
          </span>
          <p className="mt-1 text-sm font-normal tracking-wide text-slate-800 dark:text-slate-200">
            Daily field reports routed through the newsroom agent.
          </p>
          <div className="absolute right-6 top-5">
            <ThemeToggle />
          </div>
        </div>
      </div>
      <div className="flex flex-1 min-h-0 flex-col md:flex-row">
        <div className="flex basis-full min-h-[320px] flex-col border-b border-slate-800 bg-white dark:border-slate-200 dark:bg-slate-950 md:basis-[32%] md:min-h-0 md:border-b-0 md:border-r">
          <ChatKitPanel
            className="flex-1"
            onChatKitReady={(chatkit) => (chatkitRef.current = chatkit)}
          />
        </div>
        <div className="flex flex-1 min-h-0 bg-white dark:bg-[#1c1c1c]">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppShell />}>
        <Route index element={<NewsroomPanel />} />
        <Route path="article/:articleId" element={<NewsroomPanel />} />
        <Route path="*" element={<NewsroomPanel />} />
      </Route>
    </Routes>
  );
}
