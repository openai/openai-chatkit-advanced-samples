import clsx from "clsx";
import { Moon, Sun } from "lucide-react";
import { useAppStore } from "../store/useAppStore";

const buttonBase =
  "inline-flex h-9 w-9 items-center justify-center rounded-full text-[0.7rem] transition-colors duration-200";

export function ThemeToggle() {
  const scheme = useAppStore((state) => state.scheme);
  const setScheme = useAppStore((state) => state.setScheme);
  return (
    <div className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white/60 p-1 shadow-sm backdrop-blur-sm dark:border-slate-800 dark:bg-slate-900/60">
      <button
        type="button"
        onClick={() => setScheme("light")}
        className={clsx(
          buttonBase,
          scheme === "light"
            ? "bg-slate-900 text-white shadow-sm dark:bg-slate-100 dark:text-slate-900"
            : "text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-100"
        )}
        aria-label="Use light theme"
        aria-pressed={scheme === "light"}
      >
        <Sun className="h-4 w-4" aria-hidden />
      </button>
      <button
        type="button"
        onClick={() => setScheme("dark")}
        className={clsx(
          buttonBase,
          scheme === "dark"
            ? "bg-slate-900 text-white shadow-sm dark:bg-slate-100 dark:text-slate-900"
            : "text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-100"
        )}
        aria-label="Use dark theme"
        aria-pressed={scheme === "dark"}
      >
        <Moon className="h-4 w-4" aria-hidden />
      </button>
    </div>
  );
}
