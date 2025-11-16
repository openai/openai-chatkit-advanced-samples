import { useCallback, useRef } from "react";
import type { Entity } from "@openai/chatkit";

import { fetchArticleTags, type ArticleTag } from "../lib/articles";

export function useTags() {
  const tagsRef = useRef<ArticleTag[] | null>(null);
  const loadingRef = useRef<Promise<ArticleTag[]> | null>(null);

  const loadTags = useCallback(async () => {
    if (tagsRef.current) {
      return tagsRef.current;
    }

    if (!loadingRef.current) {
      loadingRef.current = fetchArticleTags()
        .then((tags) => {
          tagsRef.current = tags;
          return tags;
        })
        .catch((error) => {
          console.error("Failed to fetch article tags", error);
          tagsRef.current = [];
          return [];
        });
    }

    return loadingRef.current;
  }, []);

  const search = useCallback(
    async (query: string) => {
      const tags = await loadTags();
      const normalized = query.trim().toLowerCase();
      const matchingTags = normalized
        ? tags.filter(({ entity }) => {
            const titleMatch = entity.title.toLowerCase().includes(normalized);
            const idMatch = entity.id.toLowerCase().includes(normalized);
            return titleMatch || idMatch;
          })
        : tags;
      return matchingTags.map((tag) => tag.entity);
    },
    [loadTags]
  );

  const getPreview = useCallback(
    async (entity: Entity) => {
      const tags = await loadTags();
      const match = tags.find((tag) => tag.entity.id === entity.id);
      return { preview: match?.preview ?? null };
    },
    [loadTags]
  );

  return { search, getPreview };
}
