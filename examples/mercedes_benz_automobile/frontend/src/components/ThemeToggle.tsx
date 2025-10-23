import { Moon, Sun } from "lucide-react";
import type { ColorScheme } from "../hooks/useColorScheme";

interface ThemeToggleProps {
  scheme: ColorScheme;
  onToggle: () => void;
}

export function ThemeToggle({ scheme, onToggle }: ThemeToggleProps) {
  return (
    <button
      onClick={onToggle}
      className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      aria-label="Toggle theme"
    >
      {scheme === "light" ? (
        <Moon className="w-5 h-5 text-gray-700 dark:text-gray-300" />
      ) : (
        <Sun className="w-5 h-5 text-gray-700 dark:text-gray-300" />
      )}
    </button>
  );
}
