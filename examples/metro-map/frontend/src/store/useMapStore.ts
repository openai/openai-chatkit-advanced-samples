import { create } from "zustand";

import { X_UNIT, Y_UNIT, type MetroMap } from "../lib/map";
import type { ReactFlowInstance } from "reactflow";

type MapState = {
  map: MetroMap | null;
  setMap: (map: MetroMap | null) => void;
  reactFlow: ReactFlowInstance | null;
  setReactFlow: (instance: ReactFlowInstance | null) => void;
  fitView: () => void;
  focusStation: (stationId: string, map?: MetroMap) => void;
  locationSelectLineId: string | null;
  setLocationSelectLineId: (lineId: string | null) => void;
  clearLocationSelectMode: () => void;
  selectedStationId: string | null;
  setSelectedStationId: (stationId: string | null) => void;
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
      duration: 800,
    });
  },
  focusStation: (stationId, currentMap) => {
    const instance = get().reactFlow;
    const map = currentMap ?? get().map;
    if (!instance || !map) return;

    const station = map.stations.find((entry) => entry.id === stationId);
    if (!station) return;

    set({ selectedStationId: stationId });

    const x = station.x * X_UNIT;
    const y = station.y * Y_UNIT;
    const zoom = Math.max(1.05, Math.min(1.3, instance.getZoom() + 0.1));

    instance.setCenter(x, y, { zoom, duration: 800 });
  },
  locationSelectLineId: null,
  setLocationSelectLineId: (lineId) => {
    set({ locationSelectLineId: lineId, selectedStationId: null });
    if (lineId) {
      get().fitView();
    }
  },
  clearLocationSelectMode: () => set({ locationSelectLineId: null }),
  selectedStationId: null,
  setSelectedStationId: (stationId) => set({ selectedStationId: stationId }),
}));
