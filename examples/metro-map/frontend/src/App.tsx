import clsx from "clsx";
import { Outlet, Route, Routes } from "react-router-dom";

import { ChatKitPanel } from "./components/ChatKitPanel";
import { MapPanel } from "./components/MapPanel";
import { useAppStore } from "./store/useAppStore";

function AppShell() {
  const setChatkit = useAppStore((state) => state.setChatkit);

  return (
    <div className="h-full flex min-h-screen flex-col dark:bg-[#0d1117] dark:text-slate-100 bg-white/90 text-slate-900">
      <div className="flex flex-1 min-h-0 flex-col md:flex-row">
        <div className="flex basis-full min-h-[320px] flex-col md:basis-[70%] md:min-h-0">
          <Outlet />
        </div>
        <div className="flex flex-1 min-h-0 bg-transparent">
          <ChatKitPanel onChatKitReady={(chatkit) => { setChatkit(chatkit) }}
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
