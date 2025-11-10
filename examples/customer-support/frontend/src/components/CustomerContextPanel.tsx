import { CalendarDays, Luggage, Mail, Phone, Utensils } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import clsx from "clsx";

import type { CustomerProfile, TimelineEntry } from "../hooks/useCustomerContext";

type CustomerContextPanelProps = {
  profile: CustomerProfile | null;
  loading: boolean;
  error: string | null;
};

export function CustomerContextPanel({ profile, loading, error }: CustomerContextPanelProps) {
  if (loading) {
    return (
      <section className="flex h-full flex-col gap-4 rounded-3xl border border-slate-200/60 bg-white/80 p-6 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.5)] ring-1 ring-slate-200/60 backdrop-blur dark:border-slate-800/70 dark:bg-slate-900/70 dark:shadow-[0_45px_95px_-55px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
        <header>
          <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-100">
            Customer profile
          </h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">
            Loading customer data…
          </p>
        </header>
        <div className="flex flex-1 items-center justify-center">
          <span className="text-sm text-slate-500 dark:text-slate-400">
            Fetching the latest itinerary and services…
          </span>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="flex h-full flex-col gap-4 rounded-3xl border border-rose-200 bg-rose-50/60 p-6 text-rose-700 shadow-sm dark:border-rose-900/60 dark:bg-rose-950/40 dark:text-rose-200">
        <header>
          <h2 className="text-xl font-semibold">Customer profile</h2>
        </header>
        <p className="text-sm">{error}</p>
      </section>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <section className="flex h-full flex-col gap-6 overflow-auto rounded-3xl border border-slate-200/60 bg-white/80 p-6 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.5)] ring-1 ring-slate-200/60 backdrop-blur dark:border-slate-800/70 dark:bg-slate-900/70 dark:shadow-[0_45px_95px_-55px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
      <header className="space-y-3">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-blue-500 dark:text-blue-300">
              Concierge customer
            </p>
            <h2 className="text-2xl font-semibold text-slate-800 dark:text-slate-100">
              {profile.name}
            </h2>
            <p className="text-sm text-blue-600 dark:text-blue-200">
              {profile.loyalty_status}
            </p>
          </div>
          <div className="rounded-2xl border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 dark:border-blue-900/60 dark:bg-blue-950/30 dark:text-blue-200">
            Loyalty ID: {profile.loyalty_id}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600 dark:text-slate-300">
          <span className="inline-flex items-center gap-2">
            <Mail className="h-4 w-4" aria-hidden /> {profile.email}
          </span>
          <span className="inline-flex items-center gap-2">
            <Phone className="h-4 w-4" aria-hidden /> {profile.phone}
          </span>
        </div>
      </header>

      <section className="rounded-2xl bg-slate-50/80 p-4 dark:bg-slate-900/60">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-300">
          Upcoming itinerary
        </h3>
        <div className="mt-4 space-y-3">
          {profile.segments.map((segment) => (
            <article
              key={segment.flight_number}
              className="rounded-xl border border-slate-200 bg-white/90 p-4 shadow-sm transition hover:border-blue-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900/70"
            >
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
                    {segment.flight_number}
                  </p>
                  <h4 className="text-base font-semibold text-slate-800 dark:text-slate-100">
                    {segment.origin} → {segment.destination}
                  </h4>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {formatDate(segment.date)} · {segment.departure_time} – {segment.arrival_time}
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
                        : "text-emerald-500",
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

      <section className="grid gap-3 sm:grid-cols-3">
        <InfoPill icon={Luggage} label="Checked bags">
          {profile.bags_checked}
        </InfoPill>
        <InfoPill icon={Utensils} label="Meal preference">
          {profile.meal_preference || "Not set"}
        </InfoPill>
        <InfoPill icon={CalendarDays} label="Assistance">
          {profile.special_assistance || "None"}
        </InfoPill>
      </section>

      <section className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200/70 bg-white/90 dark:border-slate-800/70 dark:bg-slate-900/70">
        <header className="border-b border-slate-200/70 px-4 py-3 text-sm font-semibold uppercase tracking-wide text-slate-500 dark:border-slate-800/70 dark:text-slate-300">
          Recent concierge actions
        </header>
        <Timeline entries={profile.timeline} />
      </section>

      <section>
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-300">
          Tier benefits
        </h3>
        <ul className="mt-3 grid gap-2 text-sm text-slate-600 dark:text-slate-300 sm:grid-cols-2">
          {profile.tier_benefits.map((benefit) => (
            <li
              key={benefit}
              className="rounded-xl border border-slate-200/70 bg-white/90 px-3 py-2 shadow-sm dark:border-slate-800/70 dark:bg-slate-900/70"
            >
              {benefit}
            </li>
          ))}
        </ul>
      </section>
    </section>
  );
}

function InfoPill({
  icon: Icon,
  label,
  children,
}: {
  icon: LucideIcon;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-slate-200/60 bg-white/90 px-4 py-3 shadow-sm dark:border-slate-800/70 dark:bg-slate-900/70">
      <Icon className="h-5 w-5 text-blue-500 dark:text-blue-300" aria-hidden />
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
          {label}
        </p>
        <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">
          {children}
        </p>
      </div>
    </div>
  );
}

function Timeline({ entries }: { entries: TimelineEntry[] }) {
  if (!entries.length) {
    return (
      <div className="flex flex-1 items-center justify-center px-6 text-sm text-slate-500 dark:text-slate-400">
        No concierge actions recorded yet.
      </div>
    );
  }

  return (
    <ul className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
      {entries.map((entry) => (
        <li
          key={`${entry.timestamp}-${entry.entry}`}
          className={clsx(
            "rounded-xl border px-4 py-3 text-sm leading-relaxed",
            timelineTone(entry.kind),
          )}
        >
          <p className="font-medium text-slate-700 dark:text-slate-100">{entry.entry}</p>
          <p className="text-xs uppercase tracking-wide text-slate-400 dark:text-slate-500">
            {formatTimestamp(entry.timestamp)}
          </p>
        </li>
      ))}
    </ul>
  );
}

function timelineTone(kind: string | undefined) {
  switch (kind) {
    case "success":
      return "border-emerald-200/70 bg-emerald-50/80 text-emerald-700 dark:border-emerald-900/40 dark:bg-emerald-900/30 dark:text-emerald-200";
    case "warning":
      return "border-amber-200/70 bg-amber-50/80 text-amber-700 dark:border-amber-900/40 dark:bg-amber-900/30 dark:text-amber-200";
    case "error":
      return "border-rose-200/70 bg-rose-50/80 text-rose-700 dark:border-rose-900/40 dark:bg-rose-900/30 dark:text-rose-200";
    default:
      return "border-slate-200/70 bg-slate-50/90 text-slate-600 dark:border-slate-800/70 dark:bg-slate-900/60 dark:text-slate-200";
  }
}

function formatTimestamp(value: string): string {
  try {
    const date = new Date(value);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  } catch (err) {
    return value;
  }
}

function formatDate(value: string): string {
  try {
    return new Date(value).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch (err) {
    return value;
  }
}

