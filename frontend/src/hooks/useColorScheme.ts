import { useAppStore } from "../store/useAppStore";

export type { ColorScheme } from "../store/useAppStore";

export function useColorScheme() {
  const scheme = useAppStore((state) => state.scheme);
  const setScheme = useAppStore((state) => state.setScheme);

  return { scheme, setScheme };
}
