import clsx from "clsx";
import { Outlet, Route, Routes } from "react-router-dom";

import { ChatKitPanel } from "./components/ChatKitPanel";
import { MapPanel } from "./components/MapPanel";
import { ThemeToggle } from "./components/ThemeToggle";
import { useAppStore } from "./store/useAppStore";

function AppShell() {
  const setChatkit = useAppStore((state) => state.setChatkit);

  return (
    <div className="h-full flex min-h-screen flex-col transition-colors duration-300 dark:bg-[#0d1117] dark:text-slate-100 bg-white/90 text-slate-900">
      <div className="sticky top-0 z-30 w-full text-slate-900 dark:text-slate-100">
        <div className="relative flex w-full flex-col gap-4 px-6 py-6 pr-24 sm:flex-row sm:items-center sm:gap-8">
          <span
            className="text-xl font-semibold uppercase tracking-[0.25em] text-slate-900 dark:text-slate-100"
          >
            Metro Map
          </span>
          <p className="mt-1 text-sm font-normal tracking-wide text-slate-800 dark:text-slate-200">
            Visualize metro lines and stations on the left, chat with the agent on the right.
          </p>
          <div className="absolute right-6 top-5">
            <ThemeToggle />
          </div>
        </div>
      </div>
      <div className="flex flex-1 min-h-0 flex-col md:flex-row">
        <div className="flex basis-full min-h-[320px] flex-col md:basis-[70%] md:min-h-0">
          <Outlet />
        </div>
        <div className="flex flex-1 min-h-0 bg-transparent">
          <ChatKitPanel
            className="flex-1"
            onChatKitReady={(chatkit) => {
              setChatkit(chatkit);
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppShell />}>
        <Route index element={<MapPanel />} />
        <Route path="*" element={<MapPanel />} />
      </Route>
    </Routes>
  );
}
