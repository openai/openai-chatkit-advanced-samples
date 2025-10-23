import { useEffect, useState } from "react";
import { THEME_STORAGE_KEY } from "../lib/config";

export type ColorScheme = "light" | "dark";

function getInitialScheme(): ColorScheme {
  // Check localStorage first
  const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === "light" || stored === "dark") {
    return stored;
  }

  // Fall back to system preference
  if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }

  return "light";
}

export function useColorScheme() {
  const [scheme, setScheme] = useState<ColorScheme>(getInitialScheme);

  useEffect(() => {
    // Apply theme to document
    if (scheme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }

    // Persist to localStorage
    window.localStorage.setItem(THEME_STORAGE_KEY, scheme);
  }, [scheme]);

  const toggle = () => {
    setScheme((current) => (current === "light" ? "dark" : "light"));
  };

  return {
    scheme,
    setScheme,
    toggle,
  };
}
