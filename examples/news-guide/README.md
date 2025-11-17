# News Guide

Foxhollow Dispatch newsroom assistant showcasing retrieval-heavy ChatKit flows and rich widgets.

## Quickstart

1. Export `OPENAI_API_KEY` (and `VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_local_dev` for local).
2. From the repo root run `npm run news-guide` (or `cd examples/news-guide && npm install && npm run start`).
3. Go to: http://localhost:5172

## Example prompts

- "What's trending right now?" (article search + list widget)
- "Summarize this page for me." (page-aware `get_current_page`)
- "Show me everything tagged parks and outdoor events." (information retrieval using tools)
- "@Elowen latest stories?" (author @-mention lookup; only works when manually typing @, no copy paste)
- "What events are happening this Saturday?" (select the "Event finder" tool from the composer menu first)
- "Give me a quick puzzle break." (select the "Coffee break puzzle" tool from the composer menu)

## Features

- Retrieval tool suite for metadata and content (`list_available_tags_and_keywords`, `search_articles_by_tags/keywords/exact_text`, `search_articles_by_author`), plus article list widgets to present results.
- Page-aware context via `article-id` request header and `get_current_page` tool for grounded answers about the open article, using the custom fetch ChatKit option.
- Entity tags with previews; tagged articles/authors become `<ARTICLE_REFERENCE>` / `<AUTHOR_REFERENCE>` markers that drive `get_article_by_id`.
- Progress streaming (`ProgressUpdateEvent`) during searches and page loads to keep the UI responsive.
- Composer tool options for explicit agent routing (`event_finder`, `puzzle`) using `tool_choice`.
- Widgets with client and server actions: article list "View" buttons (`open_article`) and event timeline with server-handled `view_event_details` updates.
