# OpenAI ChatKit Examples

This repository collects scenario-driven ChatKit demos. Each example pairs a FastAPI backend with a Vite + React frontend, implementing a custom backend using ChatKit Python SDK and wiring it up with ChatKit.js client-side.

You can run the following examples:

- [**Cat Lounge**](examples/cat-lounge) - caretaker for a virtual cat that helps improve energy, happiness, and cleanliness stats.
- [**Customer Support**](examples/customer-support) – airline concierge with live itinerary data, timeline syncing, and domain-specific tools.
- [**News Guide**](examples/news-guide) – Foxhollow Dispatch newsroom assistant with article search, @-mentions, and page-aware responses.

## Quickstart

1. Export `OPENAI_API_KEY`.
2. Make sure `uv` is installed.
3. Launch an example from the repo root, or with `npm run start` from the project directory:

| Example          | Command for repo root      | Command for project directory                              | URL                   |
| ---------------- | -------------------------- | ---------------------------------------------------------- | --------------------- |
| Cat Lounge       | `npm run cat-lounge`       | `cd examples/cat-lounge && npm install && npm run start`   | http://localhost:5170 |
| Customer Support | `npm run customer-support` | `cd examples/customer-support && npm install && npm start` | http://localhost:5171 |
| News Guide       | `npm run news-guide`       | `cd examples/news-guide && npm install && npm run start`   | http://localhost:5172 |

## Feature index

### Server tool calls to retrieve application data for inference

- **Cat Lounge**:
  - Function tool `get_cat_status` ([cat_agent.py](examples/cat-lounge/backend/app/cat_agent.py)) pulls the latest cat stats for the agent.
- **News Guide**:
  - The agent leans on a suite of retrieval tools—`list_available_tags_and_keywords`, `get_article_by_id`, `search_articles_by_tags/keywords/exact_text`, and `get_current_page`—before responding, and uses `show_article_list_widget` to present results ([news_agent.py](examples/news-guide/backend/app/agents/news_agent.py)).
  - Hidden context such as the featured landing page is normalized into agent input so summaries and recommendations stay grounded ([news_agent.py](examples/news-guide/backend/app/agents/news_agent.py)).

### Client tool calls that mutate UI state

- **Cat Lounge**:
  - Client tool `update_cat_status` is invoked by server tools `feed_cat`, `play_with_cat`, `clean_cat`, and `speak_as_cat` to sync UI state.
  - When invoked, it is handled client-side with the `handleClientToolCall` callback in [ChatKitPanel.tsx](examples/cat-lounge/frontend/src/components/ChatKitPanel.tsx).
- **News Guide**:
  - The `open_article` widget action triggers client-side navigation to the selected story and forwards the action back to the server via `sendCustomAction` to follow up with context-aware prompts ([ChatKitPanel.tsx](examples/news-guide/frontend/src/components/ChatKitPanel.tsx)).

### Page-aware model responses

- **News Guide**:
  - The ChatKit client forwards the currently open article id in an `article-id` header so the backend can scope responses to “this page” ([ChatKitPanel.tsx](examples/news-guide/frontend/src/components/ChatKitPanel.tsx)).
  - The server reads that request context and exposes `get_current_page` so the agent can load full content without asking the user to paste it ([main.py](examples/news-guide/backend/app/main.py), [news_agent.py](examples/news-guide/backend/app/agents/news_agent.py)).

### Progress updates

- **News Guide**:
  - Retrieval tools stream `ProgressUpdateEvent` messages while searching tags, authors, keywords, exact text, or loading the current page so the UI surfaces “Searching…”/“Loading…” states ([news_agent.py](examples/news-guide/backend/app/agents/news_agent.py)).
  - The event finder emits progress as it scans dates, days of week, or keywords to keep users informed during longer lookups ([event_finder_agent.py](examples/news-guide/backend/app/agents/event_finder_agent.py)).

### Widgets without actions

- **Cat Lounge**:
  - Server tool `show_cat_profile` streams a presentation widget defined in [profile_card_widget.py](examples/cat-lounge/backend/app/profile_card_widget.py).

### Widgets with actions

- **Cat Lounge**:
  - Server tool `suggest_cat_names` streams a widget with action configs that specify `cats.select_name` and `cats.more_names` client-handled actions.
  - When the user clicks the widget, these actions are handled with the `handleWidgetAction` callback in [ChatKitPanel.tsx](examples/cat-lounge/frontend/src/components/ChatKitPanel.tsx).
- **News Guide**:
  - Article list widgets render “View” buttons that dispatch `open_article` actions for client navigation and engagement ([news_agent.py](examples/news-guide/backend/app/agents/news_agent.py), [article_list_widget.py](examples/news-guide/backend/app/widgets/article_list_widget.py)).
  - The event finder streams a timeline widget with `view_event_details` buttons configured for server handling so users can expand items inline ([event_finder_agent.py](examples/news-guide/backend/app/agents/event_finder_agent.py), [event_list_widget.py](examples/news-guide/backend/app/widgets/event_list_widget.py)).

### Server-handled widget actions

- **Cat Lounge**:
  - The `cats.select_name` action is also handled server-side to reflect updates to data and stream back an updated version of the name suggestions widget in [server.py](examples/cat-lounge/backend/app/server.py).
  - It is invoked using `chatkit.sendAction()` from `handleWidgetAction` callback in [ChatKitPanel.tsx](examples/cat-lounge/frontend/src/components/ChatKitPanel.tsx).
- **News Guide**:
  - The `view_event_details` action is processed server-side to update the timeline widget with expanded descriptions without a round trip to the model ([server.py](examples/news-guide/backend/app/server.py)).

### Entity tags (@-mentions)

- **News Guide**:
  - Entity search and previews power @-mentions for articles/authors in the composer and render hover previews via `/articles/tags` ([ChatKitPanel.tsx](examples/news-guide/frontend/src/components/ChatKitPanel.tsx), [main.py](examples/news-guide/backend/app/main.py)).
  - Tagged entities are converted into model-readable markers so the agent can fetch the right records (`<ARTICLE_REFERENCE>` / `<AUTHOR_REFERENCE>`) ([thread_item_converter.py](examples/news-guide/backend/app/thread_item_converter.py)).
  - Article reference tags are resolved into full articles via the instructed `get_article_by_id` tool before the agent cites details ([news_agent.py](examples/news-guide/backend/app/agents/news_agent.py)).

### Tool choice (composer menu)

- **News Guide**:
  - The ChatKit client is configured with a `composer.tools` option that specifies options in the composer menu ([ChatKitPanel.tsx](examples/news-guide/frontend/src/components/ChatKitPanel.tsx))
  - Composer tool buttons let users force specific agents (`event_finder`, `puzzle`), setting `tool_choice` on the request ([config.ts](examples/news-guide/frontend/src/lib/config.ts)).
  - The backend routes these tool choices to specialized agents before falling back to the News Guide agent ([server.py](examples/news-guide/backend/app/server.py)).
