import { Moon, Sun } from "lucide-react";
import clsx from "clsx";
import { useAppStore } from "../store/useAppStore";

export function ThemeToggle() {
  const scheme = useAppStore((state) => state.scheme);
  const setScheme = useAppStore((state) => state.setScheme);

  const toggle = () => setScheme(scheme === "dark" ? "light" : "dark");

  return (
    <button
      onClick={toggle}
      aria-label="Toggle theme"
      className={clsx(
        "rounded-full p-2 transition-colors",
        scheme === "dark"
          ? "bg-slate-800 text-slate-200 hover:bg-slate-700"
          : "bg-slate-200 text-slate-800 hover:bg-slate-300"
      )}
    >
      {scheme === "dark" ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  );
}
