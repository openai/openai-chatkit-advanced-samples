import { ArrowRight, Sparkles } from "lucide-react";

import type { CustomerProfile } from "../../hooks/useCustomerContext";
import type { SupportView } from "../../types/support";
import { TimelineList } from "./TimelineList";

type OverviewViewProps = {
  profile: CustomerProfile;
  onViewChange: (view: SupportView) => void;
};

export function OverviewView({
  profile,
  onViewChange,
}: OverviewViewProps): JSX.Element {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/70">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100">
              Today&apos;s snapshot
            </h3>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
              {profile.travel_summary}
            </p>
          </div>
          <button
            type="button"
            onClick={() => onViewChange("loyalty")}
            className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900"
          >
            Loyalty perks
            <ArrowRight className="h-4 w-4" aria-hidden />
          </button>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          {profile.spotlight.map((item) => (
            <span
              key={item}
              className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-200"
            >
              <Sparkles className="h-3 w-3 text-amber-500" aria-hidden />
              {item}
            </span>
          ))}
        </div>
      </div>

      <TimelineList timeline={profile.timeline} limit={3} />
    </div>
  );
}

