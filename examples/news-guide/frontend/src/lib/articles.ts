import { ARTICLES_API_URL } from "./config";

export type ArticleMetadata = {
  id: string;
  title: string;
  heroImage: string;
  url: string;
  filename: string;
  date: string;
  author: string;
  tags: string[];
};

export type Article = ArticleMetadata & {
  content: string;
};

export async function fetchArticles(): Promise<ArticleMetadata[]> {
  const response = await fetch(`${ARTICLES_API_URL}/featured`);
  if (!response.ok) {
    throw new Error(`Failed to load articles (${response.status})`);
  }
  const data = (await response.json()) as { articles?: ArticleMetadata[] };
  return data.articles ?? [];
}

export async function fetchArticle(articleId: string): Promise<Article> {
  const response = await fetch(`${ARTICLES_API_URL}/${encodeURIComponent(articleId)}`);
  if (!response.ok) {
    throw new Error(`Failed to load article (${response.status})`);
  }
  const data = (await response.json()) as { article?: Article };
  if (!data.article) {
    throw new Error("Article payload missing in response.");
  }
  return data.article;
}

export function formatArticleDate(value: string): string {
  const date = new Date(value);
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
