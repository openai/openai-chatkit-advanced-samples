import { useAppStore } from "../store/useAppStore";

export function useCatState() {
  const cat = useAppStore((state) => state.cat);
  const refresh = useAppStore((state) => state.refreshCat);
  const applyUpdate = useAppStore((state) => state.applyCatUpdate);

  return { cat, refresh, applyUpdate };
}
