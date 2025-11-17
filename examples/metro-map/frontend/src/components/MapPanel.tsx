import { useEffect } from "react";

import { fetchMetroMap } from "../lib/map";
import { useMapStore } from "../store/useMapStore";
import { MetroMapCanvas } from "./MetroMapCanvas";

export function MapPanel() {
  const map = useMapStore((state) => state.map);
  const setMap = useMapStore((state) => state.setMap);

  useEffect(() => {
    fetchMetroMap().then(setMap);
  }, [setMap]);

  return (
    <div className="flex h-full w-full flex-col bg-white text-slate-900 transition-colors duration-300 dark:bg-[#0d1117] dark:text-slate-100">
      <div className="flex flex-1 min-h-0 items-center justify-center px-6 pb-10 pt-2">
        <div className="relative flex h-full w-full max-h-[840px] max-w-[1280px] flex-col overflow-hidden rounded-3xl border-2 border-white bg-gradient-to-br from-slate-100 via-white to-slate-100 shadow-[0_10px_20px_rgba(15,23,42,0.16)] dark:from-slate-900 dark:via-slate-900/70 dark:to-slate-900">
          {map && <MetroMapCanvas map={map} />}
        </div>
      </div>
    </div>
  );
}
