from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, List

from agents import Agent, RunContextWrapper, StopAtTools, function_tool
from chatkit.agents import AgentContext
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    ProgressUpdateEvent,
    ThreadItemDoneEvent,
)
from pydantic import ConfigDict, Field

from .article_list_widget import build_article_list_widget
from .article_store import ArticleMetadata, ArticleStore
from .memory_store import MemoryStore

INSTRUCTIONS = """
    You are News Guide, a service-forward assistant focused on helping readers quickly
    discover the most relevant news for their needs. Prioritize clarity, highlight how
    each story serves the reader, and keep answers concise with skimmable structure.

    Before recommending or summarizing, always consult the latest article metadata via
    the available tools. When summarizing, cite the article title and give a one-line takeaway
    that explains why it matters to the reader right now.

    If the reader provides desired topics, locations, or tags, filter results before responding
    and call out any notable gaps.
    
    Unless the reader explicitly asks for a set number of articles, default to suggesting 2 articles.

    Use the tools deliberately:
      - Call `list_available_tags_and_keywords` to get a list of all unique tags and keywords available to search by.
      - Use `list_articles_for_tags` only when the reader explicitly references tags/sections (e.g., "show me everything tagged parks"); otherwise skip it.
      - Default to `search_articles_by_keywords` to match metadata (titles, subtitles, tags, keywords) to the reader's asks.
      - Use `search_articles_by_exact_text` when the reader quote a phrase or wants an exact content match.
      - After fetching story candidates, prefer `show_article_list_widget` with the returned articles fetched using
        `list_articles_for_tags` or `search_articles_by_keywords` or `search_articles_by_exact_text` and a message
        that explains why these articles were selected for the reader right now.

        so readers can skim quickly.

    Suggest a next step—such as related articles or follow-up angles—whenever it adds value.
"""

MODEL = "gpt-4.1-mini"


class NewsAgentContext(AgentContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    store: Annotated[MemoryStore, Field(exclude=True)]
    articles: Annotated[ArticleStore, Field(exclude=True)]
    request_context: dict[str, Any]


@function_tool(description_override="List newsroom articles, optionally filtered by tags.")
async def list_articles_for_tags(
    ctx: RunContextWrapper[NewsAgentContext],
    tags: List[str] | None = None,
) -> dict[str, Any]:
    print("[TOOL CALL] list_articles_for_tags", tags)
    if tags:
        tag_label = ", ".join(tags)
    else:
        tag_label = "all tags"
    await ctx.context.stream(ProgressUpdateEvent(text=f"Searching for tags: {tag_label}"))
    records = ctx.context.articles.list_metadata_for_tags(tags)
    return {"articles": records}


@function_tool(
    description_override="List all unique tags and keywords available across the newsroom archive."
)
async def list_available_tags_and_keywords(
    ctx: RunContextWrapper[NewsAgentContext],
) -> dict[str, Any]:
    print("[TOOL CALL] list_available_tags_and_keywords")
    await ctx.context.stream(ProgressUpdateEvent(text="Referencing available tags and keywords"))
    return ctx.context.articles.list_available_tags_and_keywords()


@function_tool(
    description_override="Search newsroom articles by keywords within their metadata (title, tags, keywords, etc.)."
)
async def search_articles_by_keywords(
    ctx: RunContextWrapper[NewsAgentContext],
    keywords: List[str],
) -> dict[str, Any]:
    cleaned = [keyword.strip() for keyword in keywords if keyword and keyword.strip()]
    print("[TOOL CALL] search_articles_by_keywords", cleaned)
    if not cleaned:
        raise ValueError("Please provide at least one non-empty keyword to search for.")
    formatted = ", ".join(cleaned)
    await ctx.context.stream(ProgressUpdateEvent(text=f"Searching for keywords: {formatted}"))
    records = ctx.context.articles.search_metadata_by_keywords(cleaned)
    return {"articles": records}


@function_tool(
    description_override="Search newsroom articles for an exact text match within their content."
)
async def search_articles_by_exact_text(
    ctx: RunContextWrapper[NewsAgentContext],
    text: str,
) -> dict[str, Any]:
    trimmed = text.strip()
    print("[TOOL CALL] search_articles_by_exact_text", trimmed)
    if not trimmed:
        raise ValueError("Please provide a non-empty text string to search for.")
    records = ctx.context.articles.search_content_by_exact_text(trimmed)
    return {"articles": records}


@function_tool(description_override="Fetch the markdown content for a specific article.")
async def get_article(
    ctx: RunContextWrapper[NewsAgentContext],
    article_id: str,
) -> dict[str, Any]:
    print("[TOOL CALL] get_article", article_id)
    record = ctx.context.articles.get_article(article_id)
    if not record:
        raise ValueError(f"Article '{article_id}' does not exist.")
    return {"article": record}


@function_tool(
    description_override="Show a Newsroom-style article list widget for a provided set of articles."
)
async def show_article_list_widget(
    ctx: RunContextWrapper[NewsAgentContext],
    articles: List[ArticleMetadata],
    message: str,
) -> dict[str, Any]:
    print("[TOOL CALL] show_article_list_widget", len(articles))
    if not articles:
        raise ValueError("Provide at least one article metadata entry before calling this tool.")

    try:
        await ctx.context.stream(
            ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=ctx.context.thread.id,
                    id=ctx.context.generate_id("message"),
                    created_at=datetime.now(),
                    content=[AssistantMessageContent(text=message)],
                ),
            )
        )

        widget = build_article_list_widget(articles)
        titles = ", ".join(article.title for article in articles)
        await ctx.context.stream_widget(widget, copy_text=titles)
        return {
            "result": f"Shared {len(articles)} article(s) via the Newsroom widget.",
            "articles": [
                {
                    "id": article.id,
                    "title": article.title,
                    "author": article.author,
                    "date": article.date.isoformat(),
                    "tags": article.tags,
                    "url": article.url,
                }
                for article in articles
            ],
        }

    except Exception as e:
        print(f"Error building article list widget: {e}")
        raise


news_agent = Agent[NewsAgentContext](
    model=MODEL,
    name="News Guide",
    instructions=INSTRUCTIONS,
    tools=[
        list_articles_for_tags,
        list_available_tags_and_keywords,
        search_articles_by_keywords,
        search_articles_by_exact_text,
        get_article,
        show_article_list_widget,
    ],
    tool_use_behavior=StopAtTools(stop_at_tool_names=[show_article_list_widget.name]),
)
