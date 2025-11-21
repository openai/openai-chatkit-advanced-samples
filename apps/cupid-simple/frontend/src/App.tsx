import clsx from "clsx";
import { ChatKitPanel } from "./components/ChatKitPanel";
import { ThemeToggle } from "./components/ThemeToggle";
import { useAppStore } from "./store/useAppStore";

export default function App() {
  const scheme = useAppStore((state) => state.scheme);

  const containerClass = clsx(
    "h-full bg-gradient-to-br transition-colors duration-300",
    scheme === "dark"
      ? "from-slate-900 via-slate-950 to-slate-850 text-slate-100"
      : "from-slate-100 via-white to-slate-200 text-slate-900"
  );

  const headerBarClass = clsx(
    "sticky top-0 z-30 w-full border-b backdrop-blur",
    scheme === "dark"
      ? "bg-slate-950/80 border-slate-800/70 text-slate-100"
      : "bg-white/90 border-slate-200/70 text-slate-900"
  );

  return (
    <div className={containerClass}>
      <div className={headerBarClass}>
        <div className="relative mx-auto flex w-full max-w-4xl items-center gap-4 px-6 py-4">
          <h1 className="text-lg font-semibold">CUPID</h1>
          <p className="flex-1 text-sm text-slate-600 dark:text-slate-300">
            Divine matchmaking powered by the stars
          </p>
          <ThemeToggle />
        </div>
      </div>
      <div className="mx-auto w-full max-w-4xl px-6 pb-10 pt-6" style={{ height: "calc(100vh - 80px)" }}>
        <ChatKitPanel className="relative w-full h-full overflow-hidden rounded-3xl bg-white/80 shadow-lg ring-1 ring-slate-200/60 backdrop-blur dark:bg-slate-900/70 dark:ring-slate-800/60" />
      </div>
    </div>
  );
}
