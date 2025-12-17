import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

type InfoPillProps = {
  icon: LucideIcon;
  label: string;
  children: ReactNode;
};

export function InfoPill({ icon: Icon, label, children }: InfoPillProps) {
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

