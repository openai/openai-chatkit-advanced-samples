import clsx from "clsx";
import { useCallback, useMemo, useState } from "react";

import blackCatImage from "../assets/black-cat.png";
import calicoCatImage from "../assets/calico-cat.png";
import ragDollCatImage from "../assets/rag-doll-cat.png";
import maineCoonCatImage from "../assets/maine-coon-cat.png";
import whiteCatImage from "../assets/white-cat.png";
import unknownCatImage from "../assets/whos-that-cat.png";
import type { CatColorPattern, CatStatePayload } from "../lib/cat";
import { useAppStore } from "../store/useAppStore";

const STATUS_CONFIG = [
  { key: "energy", label: "Energy"},
  { key: "happiness", label: "Happiness"},
  { key: "cleanliness", label: "Cleanliness"},
];

type CatStatusPanelProps = {
  onQuickAction?: (message: string) => Promise<void> | void;
};

type QuickAction = {
  id: string;
  label: string;
  description: string;
  prompt: (cat: CatStatePayload) => string;
};

const CAT_IMAGE_BY_PATTERN: Record<CatColorPattern, string> = {
  black: blackCatImage,
  calico: calicoCatImage,
  colorpoint: ragDollCatImage,
  tabby: maineCoonCatImage,
  white: whiteCatImage,
};

const QUICK_ACTIONS: QuickAction[] = [
  {
    id: "treat",
    label: "Give snack",
    description: "+happiness, +energy",
    prompt: (cat) => `Please give ${cat.name} a crunchy fish treat so they feel cared for.`,
  },
  {
    id: "play",
    label: "Play with toy",
    description: "Burn zoomies",
    prompt: (cat) => `Start a quick play session with ${cat.name} using their favorite ribbon toy.`,
  },
  {
    id: "groom",
    label: "Freshen up",
    description: "Improve cleanliness",
    prompt: (cat) => `Give ${cat.name} a bath to freshen up.`,
  },
];

export function CatStatusPanel({
  onQuickAction,
}: CatStatusPanelProps) {
  const speech = useAppStore((state) => state.speech);
  const flashMessage = useAppStore((state) => state.flashMessage);
  const cat = useAppStore((state) => state.cat);

  const handleQuickAction = useCallback(
    (action: QuickAction) => onQuickAction(action.prompt(cat)),
    [cat]
  );

  const catImage = useMemo(() => {
    if (!cat.colorPattern) {
      return unknownCatImage;
    }
    return CAT_IMAGE_BY_PATTERN[cat.colorPattern] ?? unknownCatImage;
  }, [cat.colorPattern]);

  return (
    <div className="w-full relative flex flex-col h-full items-center gap-8 p-8 text-center">
      <header className="space-y-2">
        <h2 className="text-3xl font-semibold text-slate-900 dark:text-white">
          {cat.name}
        </h2>
      </header>

      <div className="relative w-full flex items-center justify-center">
        <img
          src={catImage}
          alt="Illustrated cat"
          className="h-48 w-48 object-contain drop-shadow-xl"
        />
        {speech ? (
          <div
            key={speech.id}
            className="absolute flex animate-fade-in items-center justify-center -bottom-10 w-40 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-800 shadow-lg dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          >
            {speech.message}
            <span
              aria-hidden
              className="pointer-events-none absolute -top-2 left-10 block h-4 w-4 rotate-45 border-l border-t border-slate-200 bg-white shadow-[-4px_-4px_10px_-3px_rgba(15,23,42,0.4)] dark:border-slate-700 dark:bg-slate-800"
            />
          </div>
        ) : null}
        {flashMessage ? (
          <div className="absolute flex items-center justify-center -bottom-1">
            <div
              key={flashMessage}
              className="animate-fade-in rounded-full border px-4 py-1 text-sm font-medium"
              style={{
                backgroundColor: "#fff5f0",
                color: "#923b0f",
                borderColor: "#ff9e6c",
              }}
            >
              {flashMessage}
            </div>
          </div>
        ) : null}
      </div>

      <dl className="w-full space-y-4">
        {STATUS_CONFIG.map((status) => (
          <StatusMeter
            key={status.key}
            label={status.label}
            value={cat[status.key as keyof CatStatePayload] as number}
          />
        ))}
      </dl>

      <div className="mt-auto w-full border-t border-slate-200/80 pt-4 text-left dark:border-slate-800/60">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Quick actions
        </p>
        <div className="mt-3 flex flex-col gap-3 sm:flex-row">
          {QUICK_ACTIONS.map((action) => {
            return (
              <button
                key={action.id}
                type="button"
                onClick={() => handleQuickAction(action)}
                className={clsx(
                  "flex-1 rounded-2xl border px-4 py-3 text-left shadow-sm transition-colors",
                  "border-slate-200 bg-white/80 text-slate-800 hover:border-slate-300 hover:bg-white dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-100 dark:hover:border-slate-600",
                )}
              >
                <div className="text-sm font-semibold">
                  {action.label}
                </div>
                <div className="text-xs text-slate-500 dark:text-slate-400">{action.description}</div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

type StatusMeterProps = {
  label: string;
  value: number;
};

function StatusMeter({ label, value }: StatusMeterProps) {
  const normalized = Math.max(0, Math.min(10, Number(value) || 0));
  const percentage = (normalized / 10) * 100;
  const colorClass = getColor(normalized);

  return (
    <div>
      <div className="flex items-center justify-between text-sm font-medium text-slate-600 dark:text-slate-300">
        <span>{label}</span>
        <span className="text-xs text-slate-400 dark:text-slate-500">
          {normalized} / 10
        </span>
      </div>
      <div className="mt-2 h-3 w-full rounded-full bg-slate-200/70 dark:bg-slate-800">
        <div
          className={clsx("h-full rounded-full transition-all", colorClass)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function getColor(value: number) {
  if (value >= 7) return "bg-green-500";
  if (value >= 5) return "bg-yellow-400";
  if (value >= 3) return "bg-orange-400";
  return "bg-red-500";
}
