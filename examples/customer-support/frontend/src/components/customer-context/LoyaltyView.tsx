import { Star } from "lucide-react";

import type { CustomerProfile } from "../../hooks/useCustomerContext";
import { formatDate } from "./utils";

type LoyaltyViewProps = {
  profile: CustomerProfile;
};

export function LoyaltyView({ profile }: LoyaltyViewProps) {
  const progress = profile.loyalty_progress;
  const percent = Math.min(
    100,
    Math.round((progress.points_earned / progress.points_required) * 100)
  );

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/70">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-slate-500 dark:text-slate-400">
              Status track
            </p>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              {progress.current_tier} → {progress.next_tier}
            </h3>
          </div>
          <span className="inline-flex items-center gap-2 rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800 dark:bg-amber-500/20 dark:text-amber-200">
            <Star className="h-4 w-4" aria-hidden />
            {percent}% to Platinum
          </span>
        </div>
        <div className="mt-4 h-2 rounded-full bg-slate-100 dark:bg-slate-800">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500"
            style={{ width: `${percent}%` }}
          />
        </div>
        <div className="mt-4 grid gap-3 text-sm text-slate-600 dark:text-slate-300 sm:grid-cols-2">
          <div className="rounded-2xl border border-slate-200/70 bg-white/90 px-4 py-3 dark:border-slate-800/70 dark:bg-slate-900/70">
            <p className="text-xs uppercase tracking-wide text-slate-400 dark:text-slate-500">
              Points
            </p>
            <p className="text-base font-semibold text-slate-900 dark:text-slate-100">
              {progress.points_earned.toLocaleString()} /{" "}
              {progress.points_required.toLocaleString()}
            </p>
          </div>
          <div className="rounded-2xl border border-slate-200/70 bg-white/90 px-4 py-3 dark:border-slate-800/70 dark:bg-slate-900/70">
            <p className="text-xs uppercase tracking-wide text-slate-400 dark:text-slate-500">
              Segments
            </p>
            <p className="text-base font-semibold text-slate-900 dark:text-slate-100">
              {progress.segments_flown} / {progress.segments_required}
            </p>
          </div>
        </div>
        <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
          Renewal on {formatDate(progress.renewal_date)}
        </p>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/70">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Gold perks
        </h3>
        <ul className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-300">
          {profile.tier_benefits.map((benefit) => (
            <li
              key={benefit}
              className="flex items-start gap-3 rounded-2xl border border-slate-200/60 bg-white/90 px-4 py-3 dark:border-slate-800/60 dark:bg-slate-900/60"
            >
              <Star className="mt-0.5 h-4 w-4 text-amber-400" aria-hidden />
              <span>{benefit}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
