import clsx from "clsx";

import type { TimelineEntry } from "../../hooks/useCustomerContext";

type TimelineListProps = {
  timeline: TimelineEntry[];
  limit?: number;
};

export function TimelineList({ timeline, limit }: TimelineListProps) {
  const entries = limit ? timeline.slice(0, limit) : timeline;
  if (!entries.length) {
    return null;
  }

  return (
    <section className="rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/70">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
        Service timeline
      </h3>
      <ul className="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
        {entries.map((entry) => (
          <li
            key={`${entry.timestamp}-${entry.entry}`}
            className="flex items-start gap-3 rounded-2xl border border-slate-200/60 bg-white/90 px-4 py-3 dark:border-slate-800/60 dark:bg-slate-900/60"
          >
            <span
              className={clsx("mt-1 h-2 w-2 rounded-full", {
                "bg-emerald-400": entry.kind === "success",
                "bg-amber-400": entry.kind === "warning",
                "bg-slate-400": entry.kind === "info",
                "bg-rose-400": entry.kind === "error",
              })}
            />
            <div>
              <p className="font-medium text-slate-800 dark:text-slate-100">
                {entry.entry}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {new Date(entry.timestamp).toLocaleString()}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

