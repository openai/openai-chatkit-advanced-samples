import { FormEvent, useEffect, useMemo, useState } from "react";
import ReactModal from "react-modal";
import { ChevronDown } from "lucide-react";

import { fetchMetroMap, Station, updateMetroMap, type Line, type MetroMap } from "../lib/map";
import { useMapStore } from "../store/useMapStore";
import { useAppStore } from "../store/useAppStore";
import { MetroMapCanvas } from "./MetroMapCanvas";

function toTitleCase(name: string) {
  return name.toLowerCase().replace(/\b\w/g, function(char) {
    return char.toUpperCase();
  });
}

export function MapPanel() {
  const map = useMapStore((state) => state.map);
  const setMap = useMapStore((state) => state.setMap);
  const focusStation = useMapStore((state) => state.focusStation);
  const clearLocationSelectMode = useMapStore((state) => state.clearLocationSelectMode);
  const chatkit = useAppStore((state) => state.chatkit);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newStationName, setNewStationName] = useState("");
  const [selectedLineId, setSelectedLineId] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const lines = useMemo(() => map?.lines ?? [], [map]);

  useEffect(() => {
    ReactModal.setAppElement("#root");
  }, []);

  useEffect(() => {
    fetchMetroMap().then(setMap);
  }, [setMap]);

  useEffect(() => {
    if (lines.length && !selectedLineId) {
      setSelectedLineId(lines[0].id);
    }
  }, [lines, selectedLineId]);

  const computePosition = (line: Line, currentMap: MetroMap) => {
    const lastStationId = line.stations[line.stations.length - 1];
    const anchor = currentMap.stations.find((station) => station.id === lastStationId);
    if (!anchor) {
      return { x: 0, y: 0 };
    }

    const name = line.name.toLowerCase();
    const isOrange = name.includes("orange");
    const isBlue = name.includes("blue");
    const isPurple = name.includes("purple");

    if (isOrange) {
      return { x: anchor.x, y: anchor.y + 1 };
    }
    if (isBlue || isPurple) {
      return { x: anchor.x + 1, y: anchor.y };
    }

    return { x: anchor.x + 1, y: anchor.y };
  };

  const normalizeId = (value: string) =>
    value
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "station";

  const nextStationId = (name: string, currentMap: MetroMap) => {
    const base = normalizeId(name);
    const existing = new Set(currentMap.stations.map((station) => station.id));
    if (!existing.has(base)) return base;
    let counter = 2;
    let candidate = `${base}-${counter}`;
    while (existing.has(candidate)) {
      counter += 1;
      candidate = `${base}-${counter}`;
    }
    return candidate;
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setNewStationName("");
    setSaveError(null);
    setIsSaving(false);
  };

  const handleAddStation = async (event: FormEvent) => {
    event.preventDefault();
    if (!map) return;
    const trimmedName = toTitleCase(newStationName.trim());
    if (!trimmedName) {
      setSaveError("Please enter a station name.");
      return;
    }
    const line = lines.find((entry) => entry.id === selectedLineId);
    if (!line) {
      setSaveError("Choose a line for the new station.");
      return;
    }

    const stationId = nextStationId(trimmedName, map);
    const position = computePosition(line, map);

    const updatedLine: Line = {
      ...line,
      stations: [...line.stations, stationId],
    };

    const station: Station = {
      id: stationId,
      name: trimmedName,
      x: position.x,
      y: position.y,
      description: "",
      lines: [line.id],
    }

    const updatedMap: MetroMap = {
      ...map,
      stations: [
        ...map.stations,
        station,
      ],
      lines: map.lines.map((entry) => (entry.id === line.id ? updatedLine : entry)),
    };

    setIsSaving(true);
    setSaveError(null);
    try {
      const saved = await updateMetroMap(updatedMap);
      setMap(saved);
      clearLocationSelectMode();
      closeModal();
      requestAnimationFrame(() => focusStation(stationId, saved));
      if (chatkit) {
        const followUpPrompt = `How would you describe the ${trimmedName} station?`;
        chatkit.sendUserMessage({ text: followUpPrompt, newThread: true })
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to update the metro map.";
      setSaveError(message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex h-full w-full flex-col bg-white text-slate-900 dark:bg-[#0d1117] dark:text-slate-100">
      <div className="flex flex-1 min-h-0 items-center justify-center px-6 py-5">
        <div className="relative flex h-full w-full flex-col overflow-hidden rounded-3xl border-2 border-white bg-gradient-to-br from-slate-100 via-white to-slate-100 shadow-[0_10px_20px_rgba(15,23,42,0.16)] dark:from-slate-900 dark:via-slate-900/70 dark:to-slate-900">
          <button
            type="button"
            onClick={() => setIsModalOpen(true)}
            className="absolute bottom-4 left-4 z-10 rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-lg ring-2 ring-white transition hover:translate-y-[-1px] hover:bg-slate-800 focus:outline-none focus:ring-4 focus:ring-sky-400 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100"
          >
            Add station
          </button>
          {map && <MetroMapCanvas map={map} />}

          <ReactModal
            isOpen={isModalOpen}
            onRequestClose={closeModal}
            contentLabel="Add a station"
            className="relative w-full max-w-md rounded-2xl bg-white px-5 pt-3 pb-5 shadow-2xl ring-1 ring-slate-200 outline-none dark:bg-slate-900 dark:ring-slate-700"
            overlayClassName="fixed inset-0 z-20 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm"
            bodyOpenClassName="overflow-hidden"
            shouldCloseOnOverlayClick={!isSaving}
            shouldCloseOnEsc={!isSaving}
          >
            <div className="flex items-center justify-between pb-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                Add a station
              </h3>
              <button
                type="button"
                onClick={closeModal}
                className="rounded-full p-2 -mr-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 w-[40px] h-[40px]"
                aria-label="Close add station dialog"
              >
                ✕
              </button>
            </div>
            <form className="flex flex-col gap-4" onSubmit={handleAddStation}>
              <label className="flex flex-col gap-2 text-sm font-medium text-slate-700 dark:text-slate-200">
                Station name
                <input
                  type="text"
                  value={newStationName}
                  onChange={(event) => setNewStationName(event.target.value)}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-inner focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50 dark:focus:border-sky-500 dark:focus:ring-slate-700"
                  placeholder="Solstice Point"
                  autoFocus
                />
              </label>

              <label className="flex flex-col gap-2 text-sm font-medium text-slate-700 dark:text-slate-200">
                Line
                <div className="relative">
                  <select
                    value={selectedLineId}
                    onChange={(event) => setSelectedLineId(event.target.value)}
                    className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-3 py-2 pr-10 text-sm text-slate-900 shadow-inner focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50 dark:focus:border-sky-500 dark:focus:ring-slate-700"
                  >
                    {lines.map((line) => (
                      <option key={line.id} value={line.id}>
                        {line.name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown
                    className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500"
                    aria-hidden
                  />
                </div>
              </label>

              {saveError && (
                <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm font-medium text-rose-600 dark:bg-rose-950 dark:text-rose-200">
                  {saveError}
                </p>
              )}

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={closeModal}
                  className="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSaving}
                  className="rounded-full bg-sky-500 px-4 py-2 text-sm font-semibold text-white shadow-lg transition hover:bg-sky-400 focus:outline-none focus:ring-4 focus:ring-sky-200 disabled:cursor-not-allowed disabled:opacity-70 dark:bg-sky-600 dark:hover:bg-sky-500 dark:focus:ring-sky-800"
                >
                  {isSaving ? "Adding..." : "Add station"}
                </button>
              </div>
            </form>
          </ReactModal>
        </div>
      </div>
    </div>
  );
}
