import { create } from "zustand";

import type { MetroMap } from "../lib/map";
import type { ReactFlowInstance } from "reactflow";

type MapState = {
  map: MetroMap | null;
  setMap: (map: MetroMap | null) => void;
  reactFlow: ReactFlowInstance | null;
  setReactFlow: (instance: ReactFlowInstance | null) => void;
  fitView: () => void;
};

export const useMapStore = create<MapState>((set, get) => ({
  map: null,
  setMap: (map) => set({ map }),
  reactFlow: null,
  setReactFlow: (instance) => set({ reactFlow: instance }),
  fitView: () => {
    const instance = get().reactFlow;
    if (!instance) return;
    instance.fitView({
      padding: 0.2,
      minZoom: 0.55,
      maxZoom: 1.4,
      includeHiddenNodes: true,
    });
  },
}));
