import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";

import "./NewsroomPanel.css";

import {
  Article,
  ArticleMetadata,
  fetchArticle,
  fetchArticles,
  formatArticleDate,
} from "../lib/articles";
import { useAppStore } from "../store/useAppStore";

const markdownComponents: Components = {
  h1: (props) => (
    <h1 {...props} className="mb-4 text-2xl font-semibold text-slate-900 dark:text-white" />
  ),
  h2: (props) => (
    <h2 {...props} className="mt-8 mb-3 text-xl font-semibold text-slate-900 dark:text-white" />
  ),
  p: (props) => (
    <p {...props} className="mb-4 text-base leading-relaxed text-slate-700 dark:text-slate-200" />
  ),
  ul: (props) => (
    <ul
      {...props}
      className="mb-4 list-disc space-y-2 pl-5 text-slate-700 marker:text-slate-400 dark:text-slate-200"
    />
  ),
  ol: (props) => (
    <ol
      {...props}
      className="mb-4 list-decimal space-y-2 pl-5 text-slate-700 marker:text-slate-400 dark:text-slate-200"
    />
  ),
  li: (props) => <li {...props} className="leading-relaxed" />,
  strong: (props) => <strong {...props} className="font-semibold" />,
  em: (props) => <em {...props} className="italic text-slate-600 dark:text-slate-200" />,
  img: (props) => (
    <img {...props} className="mb-4 w-full border border-slate-200 object-cover dark:border-slate-700" />
  ),
};

function getTagModifierClass(tag: string): string {
  const normalized = tag.toLowerCase().replace(/[^a-z0-9-]/g, "-");
  return `tag-${normalized}`;
}

export function NewsroomPanel() {
  const navigate = useNavigate();
  const { articleId } = useParams<{ articleId?: string }>();
  const setArticleId = useAppStore((state) => state.setArticleId);

  const [articles, setArticles] = useState<ArticleMetadata[]>([]);
  const [listError, setListError] = useState<string | null>(null);
  const [loadingList, setLoadingList] = useState(true);

  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [articleError, setArticleError] = useState<string | null>(null);
  const [loadingArticle, setLoadingArticle] = useState(false);

  useEffect(() => {
    setArticleId(articleId ?? "featured");
  }, [articleId, setArticleId]);

  useEffect(() => {
    let cancelled = false;
    async function loadArticles() {
      try {
        setLoadingList(true);
        setListError(null);
        const data = await fetchArticles();
        if (!cancelled) {
          setArticles(data);
        }
      } catch (error) {
        if (!cancelled) {
          const message = error instanceof Error ? error.message : "Failed to load articles.";
          setListError(message);
        }
      } finally {
        if (!cancelled) {
          setLoadingList(false);
        }
      }
    }
    void loadArticles();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!articleId) {
      setSelectedArticle(null);
      setArticleError(null);
      setLoadingArticle(false);
      return;
    }

    let cancelled = false;
    async function loadArticle() {
      try {
        setLoadingArticle(true);
        setArticleError(null);
        const data = await fetchArticle(articleId);
        if (!cancelled) {
          setSelectedArticle(data);
        }
      } catch (error) {
        if (!cancelled) {
          const message = error instanceof Error ? error.message : "Failed to load article.";
          setArticleError(message);
        }
      } finally {
        if (!cancelled) {
          setLoadingArticle(false);
        }
      }
    }
    void loadArticle();
    return () => {
      cancelled = true;
    };
  }, [articleId]);

  const lastUpdated = useMemo(() => {
    if (!articles.length) {
      return null;
    }
    return formatArticleDate(articles[0].date);
  }, [articles]);

  const handleSelectArticle = (id: string) => navigate(`/article/${id}`);
  const handleClearSelection = () => navigate("/");

  const showLanding = !articleId;

  return (
    <div className="h-full w-full min-h-0 bg-white text-slate-900 dark:bg-[#1c1c1c] dark:text-slate-100">
      {showLanding ? (
        <LandingGrid
          articles={articles}
          loading={loadingList}
          error={listError}
          lastUpdated={lastUpdated}
          onSelect={handleSelectArticle}
        />
      ) : (
        <ArticleDetail
          article={selectedArticle}
          loading={loadingArticle}
          error={articleError}
          onBack={handleClearSelection}
        />
      )}
    </div>
  );
}

type LandingGridProps = {
  articles: ArticleMetadata[];
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  onSelect: (id: string) => void;
};

function LandingGrid({ articles, loading, error, lastUpdated, onSelect }: LandingGridProps) {
  let content: ReactNode;

  if (loading) {
    content = <StatusMessage message="Syncing the front page…" />;
  } else if (error) {
    content = <StatusMessage message={error} tone="error" />;
  } else if (!articles.length) {
    content = (
      <StatusMessage message="No dispatches yet. Add entries to backend/app/content/articles.json." />
    );
  } else {
    const [featured, ...rest] = articles;
    const secondary = rest.slice(0, 3);
    content = (
      <>
        {featured ? <FeaturedArticleCard article={featured} onSelect={onSelect} /> : null}
        {secondary.length ? (
          <div className="flex-grow grid gap-4 md:grid-cols-3">
            {secondary.map((article) => (
              <SecondaryArticleCard key={article.id} article={article} onSelect={onSelect} />
            ))}
          </div>
        ) : null}
      </>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <div className="flex h-full flex-col gap-6 px-6 py-8 lg:px-10">{content}</div>
    </div>
  );
}

type ArticleCardProps = {
  article: ArticleMetadata;
  onSelect: (id: string) => void;
};

function FeaturedArticleCard({ article, onSelect }: ArticleCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(article.id)}
      className="group flex w-full flex-col gap-0 overflow-hidden border border-slate-800 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 dark:border-slate-300 dark:hover:border-slate-200 dark:focus-visible:outline-slate-100 md:flex-row md:items-stretch md:min-h-[20rem]"
    >
      <img
        src={article.heroImage}
        className="h-64 w-full object-cover md:h-auto md:w-1/2 md:self-stretch"
      />
      <div className="flex flex-1 flex-col gap-3 px-6 pb-6 pt-6 md:p-6">
        <div className="text-xs font-sans font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">
          {article.tags[0] ?? "dispatch"}
        </div>
        <h3 className="text-3xl font-semibold text-slate-900 group-hover:text-slate-700 dark:text-white dark:group-hover:text-slate-200">
          {article.title}
        </h3>
        <div className="text-sm font-semibold text-slate-600 dark:text-slate-300">
          By {article.author} · {formatArticleDate(article.date)}
        </div>
      </div>
    </button>
  );
}

function SecondaryArticleCard({ article, onSelect }: ArticleCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(article.id)}
      className="group flex flex-col overflow-hidden border border-slate-800 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 dark:border-slate-300 dark:hover:border-slate-200 dark:focus-visible:outline-slate-100"
    >
      <img src={article.heroImage} alt="" className="h-36 w-full object-cover object-top" />
      <div className="flex flex-1 flex-col gap-2 px-4 pb-4 pt-4">
        <span className="text-[0.65rem] font-sans font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">
          {article.tags[0] ?? "dispatch"}
        </span>
        <h3 className="text-lg font-semibold text-slate-900 group-hover:text-slate-700 dark:text-white dark:group-hover:text-slate-100">
          {article.title}
        </h3>
        <span className="mt-auto text-xs font-semibold text-slate-600 dark:text-slate-300">
          {article.author}
        </span>
      </div>
    </button>
  );
}

type StatusMessageProps = {
  message: string;
  tone?: "default" | "error";
};

function StatusMessage({ message, tone = "default" }: StatusMessageProps) {
  const toneClass =
    tone === "error"
      ? "text-rose-600 dark:text-rose-300"
      : "text-slate-600 dark:text-slate-300";
  return <p className={`text-sm font-semibold ${toneClass}`}>{message}</p>;
}

type ArticleDetailProps = {
  article: Article | null;
  loading: boolean;
  error: string | null;
  onBack: () => void;
};

function ArticleDetail({ article, loading, error, onBack }: ArticleDetailProps) {
  return (
    <div className="flex h-full flex-col relative">
      <button
          type="button"
          onClick={onBack}
          className="
            absolute top-3 left-3
            text-xs font-semibold text-slate-900 dark:text-slate-100
            underline-offset-4 hover:underline
            bg-white/70 dark:bg-white/20   /* semi-transparent */
            backdrop-blur-sm               /* optional: glassy look */
            px-3 py-1.5                    /* padding to form the pill */
            rounded-full                   /* pill shape */
          "
        >
          ← Back to landing
      </button>
      {!loading && article && (
        <div className="flex-1 overflow-y-auto px-20 py-8">
          {error ? (
            <p className="text-sm font-semibold text-rose-600 dark:text-rose-300">{error}</p>
          ) : article ? (
            <div>
              <div className="flex flex-col gap-5 items-center justify-center text-center w-[70%] mx-auto">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">
                  {formatArticleDate(article.date)}
                </p>
                <h3 className="mt-3 text-4xl font-semibold text-slate-900 dark:text-white">
                  {article.title}
                </h3>
                <p className="mt-2 text-sm font-semibold text-slate-600 dark:text-slate-300">
                  By {article.author}
                </p>
                <div className="w-full border border-slate-800 dark:border-slate-200">
                  <img
                    src={`http://localhost:5172/${article.heroImage}`}
                    className="w-full object-cover"
                  />
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {article.tags.map((tag) => {
                    const modifier = getTagModifierClass(tag);
                    return (
                      <span key={tag} className={`newsroom-tag ${modifier}`} data-tag={tag}>
                        {tag}
                      </span>
                    );
                  })}
                </div>
              </div>
              <ReactMarkdown className="mt-6" remarkPlugins={[remarkGfm]} components={markdownComponents}>
                {article.content}
              </ReactMarkdown>
            </div>
          ) : (
            <p className="text-sm font-semibold text-slate-600 dark:text-slate-300">
              Choose a dispatch from the landing grid to load the full brief.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
