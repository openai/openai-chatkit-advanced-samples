import clsx from "clsx";

import type { FlightSegment } from "../../hooks/useCustomerContext";
import { formatDate } from "./utils";

type FlightsListProps = {
  segments: FlightSegment[];
};

export function FlightsList({ segments }: FlightsListProps) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/70">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
        Upcoming flights
      </h3>
      <div className="mt-4 space-y-3">
        {segments.map((segment) => (
          <article
            key={segment.flight_number}
            className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-300 hover:shadow-md dark:border-slate-800/70 dark:bg-slate-900/70"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-400 dark:text-slate-500">
                  {segment.flight_number}
                </p>
                <h4 className="text-base font-semibold text-slate-900 dark:text-slate-100">
                  {segment.origin} → {segment.destination}
                </h4>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {formatDate(segment.date)} · {segment.departure_time} –{" "}
                  {segment.arrival_time}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-blue-600 dark:text-blue-300">
                  Seat {segment.seat}
                </p>
                <p
                  className={clsx(
                    "text-xs font-semibold uppercase tracking-wide",
                    segment.status === "Cancelled"
                      ? "text-rose-500"
                      : "text-emerald-500"
                  )}
                >
                  {segment.status}
                </p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

