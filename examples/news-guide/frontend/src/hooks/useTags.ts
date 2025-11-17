import { useCallback, useEffect, useState } from "react";
import type { Entity } from "@openai/chatkit";

import { fetchArticleTags, type TagResult } from "../lib/articles";

export function useTags() {
  const [tags, setTags] = useState<TagResult[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetchArticleTags()
      .then(setTags)
      .catch((error) => {
        console.error("Failed to fetch article tags", error);
        setTags([]);
      })
      .finally(() => setLoaded(true));
  }, []);

  const search = useCallback(
    async (query: string) => {
      if (!loaded) {
        return [];
      }
      const normalized = query.trim().toLowerCase();
      const matchingTags = normalized
        ? tags.filter(({ entity }) => {
            const titleMatch = entity.title.toLowerCase().includes(normalized);
            const idMatch = entity.id.toLowerCase().includes(normalized);
            const groupMatch = entity.group?.toLowerCase().includes(normalized);
            return titleMatch || idMatch || groupMatch;
          })
        : tags;
      return matchingTags.map((tag) => tag.entity);
    },
    [loaded, tags]
  );

  const getPreview = useCallback(
    async (entity: Entity) => {
      if (!loaded) {
        return { preview: null };
      }
      const match = tags.find((tag) => tag.entity.id === entity.id);
      return { preview: match?.preview ?? null };
    },
    [loaded, tags]
  );

  return { search, getPreview };
}
