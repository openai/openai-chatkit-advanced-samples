from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated, List

from agents import Agent, RunContextWrapper, StopAtTools, function_tool
from chatkit.agents import AgentContext
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    ProgressUpdateEvent,
    ThreadItemDoneEvent,
)
from pydantic import BaseModel, ConfigDict, Field

from ..agents.event_finder_agent import event_finder_agent
from ..agents.puzzle_agent import puzzle_agent
from ..data.article_store import ArticleMetadata, ArticleRecord, ArticleStore
from ..memory_store import MemoryStore
from ..request_context import RequestContext
from ..widgets.article_list_widget import build_article_list_widget

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INSTRUCTIONS = """
    You are News Guide, a service-forward assistant focused on helping readers quickly
    discover the most relevant news for their needs. Prioritize clarity, highlight how
    each story serves the reader, and keep answers concise with skimmable structure.

    Before recommending or summarizing, always consult the latest article metadata via
    the available tools.

    If the reader provides desired topics, locations, or tags, filter results before responding
    and call out any notable gaps.

    Unless the reader explicitly asks for a set number of articles, default to suggesting 2 articles.

    When the reader references "this article," "this story," or "this page," treat that as a request
    about the currently open article. Load it with `get_current_page`, review the content, and answer
    their question directly using specific details instead of asking them to copy anything over.

    When summarizing:
      - Cite the article title.
      - The summary should be 2-4 sentences long.
      - Do NOT explicitly mention the word "summary" in your response.
      - After summarizing, ask the reader if they have any questions about the article.

    Formatting output:
      - Default to italicizing article titles when you mention them, and wrap any direct excerpts from the article content in
        Markdown blockquotes so they stand out.
      - Add generous paragraph breaks for readability.

    Use the tools deliberately:
      - Call `list_available_tags_and_keywords` to get a list of all unique tags and keywords available to search by. Fuzzy match
        the reader's phrasing to these tags/keywords (case-insensitive, partial matches are ok) and pick the closest ones—instead
        of relying on any hard-coded synonym map—before running a search.
      - Use `get_current_page` to fetch the full article the reader currently has open whenever they need deeper details
        or ask questions about "this page".
      - Use `search_articles_by_tags` only when the reader explicitly references tags/sections (e.g., "show me everything tagged parks"); otherwise skip it.
      - Default to `search_articles_by_keywords` to match metadata (titles, subtitles, tags, keywords) to the reader's asks.
      - Use `search_articles_by_exact_text` when the reader quote a phrase or wants an exact content match.
      - After fetching story candidates, prefer `show_article_list_widget` with the returned articles fetched using
        `search_articles_by_tags` or `search_articles_by_keywords` or `search_articles_by_exact_text` and a message
        that explains why these articles were selected for the reader right now.
      - If the reader explicitly asks about events, happenings, or things to do, call `delegate_to_event_finder`
        with their request so the Foxhollow Event Finder agent can take over.
      - If the reader wants a Foxhollow-flavored puzzle, coffee-break brain teaser, or mentions the puzzle tool,
        call `delegate_to_puzzle_keeper` so the Foxhollow Puzzle Keeper can lead with Two Truths and the mini crossword.

    Custom tags:
     - When you see an <ARTICLE_REFERENCE>{article_id}</ARTICLE_REFERENCE> tag in the context, call `get_article_by_id`
       with that id before citing details so your answer can reference the tagged article accurately.
     - When you see an <AUTHOR_REFERENCE>{author}</AUTHOR_REFERENCE> tag in the context, or the reader names an author,
       call `search_articles_by_author` with that author before recommending pieces so you feature their work first.

    Suggest a next step—such as related articles or follow-up angles—whenever it adds value.
"""

MODEL = "gpt-4.1-mini"
FEATURED_PAGE_ID = "featured"


class NewsAgentContext(AgentContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    store: Annotated[MemoryStore, Field(exclude=True)]
    articles: Annotated[ArticleStore, Field(exclude=True)]
    request_context: Annotated[RequestContext, Field(exclude=True)]


# -- Structured results for tool calls --------------------------------------


class ArticleSearchResult(BaseModel):
    articles: list[ArticleMetadata]


class AuthorSearchResult(BaseModel):
    author: str
    articles: list[ArticleMetadata]


class TagsAndKeywords(BaseModel):
    tags: list[str]
    keywords: list[str]


class ArticleRecordResult(BaseModel):
    article: ArticleRecord


class CurrentPageResult(BaseModel):
    page: str
    articles: list[ArticleRecord]
    article_id: str | None = None


# -- Tool definitions -------------------------------------------------------


@function_tool(
    description_override=(
        "List newsroom articles, optionally filtered by tags.\n"
        "- `tags`: One or more tags to filter by."
    )
)
async def search_articles_by_tags(
    ctx: RunContextWrapper[NewsAgentContext],
    tags: List[str],
) -> ArticleSearchResult:
    logger.info("[TOOL CALL] search_articles_by_tags %s", tags)
    if not tags:
        raise ValueError("Please provide at least one tag to search for.")
    tags = [tag.strip().lower() for tag in tags if tag and tag.strip()]
    tag_label = ", ".join(tags)
    await ctx.context.stream(ProgressUpdateEvent(text=f"Searching for tags: {tag_label}"))
    records = ctx.context.articles.list_metadata_for_tags(tags)
    articles = [ArticleMetadata.model_validate(record) for record in records]
    return ArticleSearchResult(articles=articles)


@function_tool(
    description_override=(
        "Find articles written by a specific author.\n"
        "- `author`: Author name to search for (case-insensitive)."
    )
)
async def search_articles_by_author(
    ctx: RunContextWrapper[NewsAgentContext],
    author: str,
) -> AuthorSearchResult:
    author = author.strip()
    logger.info("[TOOL CALL] search_articles_by_author %s", author)
    if not author:
        raise ValueError("Please provide an author name to search for.")
    display_name = " ".join(author.split("-")).title()
    await ctx.context.stream(ProgressUpdateEvent(text=f"Looking for articles by {display_name}..."))
    records = ctx.context.articles.search_metadata_by_author(author)
    articles = [ArticleMetadata.model_validate(record) for record in records]
    return AuthorSearchResult(author=author, articles=articles)


@function_tool(
    description_override=(
        "List all unique tags and keywords available across the newsroom archive. No parameters."
    )
)
async def list_available_tags_and_keywords(
    ctx: RunContextWrapper[NewsAgentContext],
) -> TagsAndKeywords:
    logger.info("[TOOL CALL] list_available_tags_and_keywords")
    await ctx.context.stream(ProgressUpdateEvent(text="Referencing available tags and keywords..."))
    return TagsAndKeywords.model_validate(ctx.context.articles.list_available_tags_and_keywords())


@function_tool(
    description_override=(
        "Search newsroom articles by keywords within their metadata (title, tags, keywords, etc.).\n"
        "- `keywords`: List of keywords to match against metadata."
    )
)
async def search_articles_by_keywords(
    ctx: RunContextWrapper[NewsAgentContext],
    keywords: List[str],
) -> ArticleSearchResult:
    cleaned = [keyword.strip().lower() for keyword in keywords if keyword and keyword.strip()]
    logger.info("[TOOL CALL] search_articles_by_keywords %s", cleaned)
    if not cleaned:
        raise ValueError("Please provide at least one non-empty keyword to search for.")
    formatted = ", ".join(cleaned)
    await ctx.context.stream(ProgressUpdateEvent(text=f"Searching for keywords: {formatted}"))
    records = ctx.context.articles.search_metadata_by_keywords(cleaned)
    articles = [ArticleMetadata.model_validate(record) for record in records]
    return ArticleSearchResult(articles=articles)


@function_tool(
    description_override=(
        "Search newsroom articles for an exact text match within their content.\n"
        "- `text`: Exact string to find inside article bodies."
    )
)
async def search_articles_by_exact_text(
    ctx: RunContextWrapper[NewsAgentContext],
    text: str,
) -> ArticleSearchResult:
    trimmed = text.strip()
    logger.info("[TOOL CALL] search_articles_by_exact_text %s", trimmed)
    if not trimmed:
        raise ValueError("Please provide a non-empty text string to search for.")
    await ctx.context.stream(ProgressUpdateEvent(text=f"Scanning articles for: {trimmed}"))
    records = ctx.context.articles.search_content_by_exact_text(trimmed)
    articles = [ArticleMetadata.model_validate(record) for record in records]
    return ArticleSearchResult(articles=articles)


@function_tool(
    description_override=(
        "Fetch the markdown content for a specific article.\n"
        "- `article_id`: Identifier of the article to load."
    )
)
async def get_article_by_id(
    ctx: RunContextWrapper[NewsAgentContext],
    article_id: str,
) -> ArticleRecordResult:
    logger.info("[TOOL CALL] get_article_by_id %s", article_id)
    await ctx.context.stream(ProgressUpdateEvent(text="Loading article..."))
    record = ctx.context.articles.get_article(article_id)
    if not record:
        raise ValueError(f"Article '{article_id}' does not exist.")
    article = ArticleRecord.model_validate(record)
    return ArticleRecordResult(article=article)


@function_tool(
    description_override=(
        "Load the full content for the page the reader currently has open. No parameters."
    )
)
async def get_current_page(
    ctx: RunContextWrapper[NewsAgentContext],
) -> CurrentPageResult:
    article_id = ctx.context.request_context.article_id
    if not article_id:
        raise ValueError("No article id is available in the current request context.")
    page_type, articles = _load_current_page_records(ctx.context.articles, article_id)
    payload = CurrentPageResult(page=page_type, articles=articles)
    if page_type == FEATURED_PAGE_ID:
        await ctx.context.stream(ProgressUpdateEvent(text="Page contents retrieved"))
    else:
        await ctx.context.stream(ProgressUpdateEvent(text="Full article retrieved"))
        payload.article_id = article_id

    return payload


@function_tool(
    description_override=(
        "Show a Newsroom-style article list widget for a provided set of articles.\n"
        "- `articles`: Article metadata entries to display.\n"
        "- `message`: Introductory text explaining why these were selected."
    )
)
async def show_article_list_widget(
    ctx: RunContextWrapper[NewsAgentContext],
    articles: List[ArticleMetadata],
    message: str,
):
    logger.info("[TOOL CALL] show_article_list_widget %s", len(articles))
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
    except Exception as exc:
        logger.error("[ERROR] show_article_list_widget: %s", exc)
        raise


# -- Helper functions -------------------------------------------------------


def _load_featured_articles(store: ArticleStore) -> list[ArticleRecord]:
    metadata_entries = store.list_metadata_for_tags([FEATURED_PAGE_ID])
    articles: list[ArticleRecord] = []
    seen: set[str] = set()

    for entry in metadata_entries:
        article_id = entry.id
        if not article_id or article_id in seen:
            continue

        record = store.get_article(article_id)
        if record:
            articles.append(ArticleRecord.model_validate(record))
            seen.add(article_id)

    return articles


def _load_current_page_records(
    store: ArticleStore, article_id: str
) -> tuple[str, list[ArticleRecord]]:
    if article_id == FEATURED_PAGE_ID:
        articles = _load_featured_articles(store)
        if not articles:
            raise ValueError("Unable to locate any featured articles to load.")
        return FEATURED_PAGE_ID, articles

    record = store.get_article(article_id)
    if not record:
        raise ValueError(f"Article '{article_id}' does not exist.")
    return "article", [ArticleRecord.model_validate(record)]


# -- Agent definition -------------------------------------------------------


news_agent = Agent[NewsAgentContext](
    model=MODEL,
    name="Foxhollow Dispatch News Guide",
    instructions=INSTRUCTIONS,
    tools=[
        # Simple retrieval tools
        list_available_tags_and_keywords,
        get_article_by_id,
        get_current_page,
        # Search tools
        search_articles_by_author,
        search_articles_by_tags,
        search_articles_by_keywords,
        search_articles_by_exact_text,
        # Presentation tools
        show_article_list_widget,
        event_finder_agent.as_tool(
            tool_name="delegate_to_event_finder",
            tool_description="Delegate event-specific requests to the Foxhollow Event Finder agent.",
        ),
        puzzle_agent.as_tool(
            tool_name="delegate_to_puzzle_keeper",
            tool_description="Delegate coffee break puzzle requests to the Foxhollow Puzzle Keeper agent.",
        ),
    ],
    # Stop after showing the article list widget to prevent content from being repeated in a continued response.
    tool_use_behavior=StopAtTools(
        stop_at_tool_names=[
            show_article_list_widget.name,
            "delegate_to_event_finder",
            "delegate_to_puzzle_keeper",
        ]
    ),
)
