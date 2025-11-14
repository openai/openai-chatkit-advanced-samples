from __future__ import annotations

from typing import Annotated, Any, List

from agents import Agent, RunContextWrapper, function_tool
from chatkit.agents import AgentContext
from pydantic import ConfigDict, Field

from .article_store import ArticleStore
from .memory_store import MemoryStore

INSTRUCTIONS = """
    You are News Guide, an editorial copilot that monitors internal news briefs and
    helps editors surface the right story for every situation. Keep responses concise,
    cite article titles, and recommend follow-up angles when appropriate.

    Always consult the latest newsroom feed via the provided tools before summarizing or quoting
    an article. When summarizing, include the publish date and note why the story matters for
    the reader. If a user asks for stories with certain tags or themes, filter the list before
    recommending anything.

    If an article references an image inside its markdown, mention it so the reader knows what
    to expect on the landing page.
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
    records = ctx.context.articles.list_metadata()
    if tags:
        seen_tags: set[str] = set()
        normalized: List[str] = []
        for tag in tags:
            normalized_tag = tag.lower()
            if normalized_tag in seen_tags:
                continue
            normalized.append(normalized_tag)
            seen_tags.add(normalized_tag)

        metadata_by_tag = ctx.context.articles.article_metdata_list_for_tags()
        filtered = []
        seen_ids = set()
        for tag in normalized:
            for record in metadata_by_tag.get(tag, []):
                article_id = record.get("id")
                if article_id in seen_ids:
                    continue
                seen_ids.add(article_id)
                filtered.append(record)
        records = filtered
    return {"articles": records}


@function_tool(description_override="Search newsroom articles by keyword within their content.")
async def search_articles_by_keyword(
    ctx: RunContextWrapper[NewsAgentContext],
    keyword: str,
) -> dict[str, Any]:
    trimmed = keyword.strip()
    print("[TOOL CALL] search_articles_by_keyword", trimmed)
    if not trimmed:
        raise ValueError("Please provide a non-empty keyword to search for.")
    records = ctx.context.articles.search_metadata_by_keyword(trimmed)
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


news_agent = Agent[NewsAgentContext](
    model=MODEL,
    name="News Guide",
    instructions=INSTRUCTIONS,
    tools=[list_articles_for_tags, search_articles_by_keyword, get_article],
)
