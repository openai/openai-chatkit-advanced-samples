# OpenAI ChatKit Examples

This repository collects scenario-driven ChatKit demos. Each example pairs a FastAPI backend with a Vite + React frontend, implementing a custom backend using ChatKit Python SDK and wiring it up with ChatKit.js client-side.

You can run the following examples:

- [**Cat Lounge**](examples/cat-lounge) - caretaker for a virtual cat that helps improve energy, happiness, and cleanliness stats.
- [**Customer Support**](examples/customer-support) – airline concierge with live itinerary data, timeline syncing, and domain-specific tools.
- [**News Guide**](examples/news-guide) – Foxhollow Dispatch newsroom assistant with article search, @-mentions, and page-aware responses.
- [**Metro Map**](examples/metro-map) – chat-driven metro planner with a React Flow network of lines and stations.

## Quickstart

1. Export `OPENAI_API_KEY`.
2. Make sure `uv` is installed.
3. Launch an example from the repo root, or with `npm run start` from the project directory:

| Example          | Command for repo root      | Command for project directory                              | URL                   |
| ---------------- | -------------------------- | ---------------------------------------------------------- | --------------------- |
| Cat Lounge       | `npm run cat-lounge`       | `cd examples/cat-lounge && npm install && npm run start`   | http://localhost:5170 |
| Customer Support | `npm run customer-support` | `cd examples/customer-support && npm install && npm start` | http://localhost:5171 |
| News Guide       | `npm run news-guide`       | `cd examples/news-guide && npm install && npm run start`   | http://localhost:5172 |
| Metro Map        | `npm run metro-map`        | `cd examples/metro-map && npm install && npm run start`    | http://localhost:5173 |

## Feature index

### Server tool calls to retrieve application data for inference

- **Cat Lounge**:
  - Function tool `get_cat_status` ([cat_agent.py](examples/cat-lounge/backend/app/cat_agent.py)) pulls the latest cat stats for the agent.
- **News Guide**:
  - The agent leans on a suite of retrieval tools—`list_available_tags_and_keywords`, `get_article_by_id`, `search_articles_by_tags/keywords/exact_text`, and `get_current_page`—before responding, and uses `show_article_list_widget` to present results ([news_agent.py](examples/news-guide/backend/app/agents/news_agent.py)).
  - Hidden context such as the featured landing page is normalized into agent input so summaries and recommendations stay grounded ([news_agent.py](examples/news-guide/backend/app/agents/news_agent.py)).
- **Metro Map**:
  - The metro agent syncs map data with `get_map` and surfaces line and station details via `list_lines`, `list_stations`, `get_line_route`, and `get_station` before giving directions ([metro_map_agent.py](examples/metro-map/backend/app/agents/metro_map_agent.py)).
  - `show_line_selector` presents the user a multiple-choice question using a widget.
  - Route-planning replies attach entity sources for the stations in the suggested path as annotations.
- **Customer Support**:
  - The concierge prepends a `<CUSTOMER_PROFILE>` snapshot (itinerary, loyalty, recent timeline) before each run and exposes tools to change seats, cancel trips, add bags, set meals, surface flight options, and request assistance against the per-thread `AirlineStateManager` state ([server.py](examples/customer-support/backend/app/server.py), [support_agent.py](examples/customer-support/backend/app/support_agent.py), [airline_state.py](examples/customer-support/backend/app/airline_state.py)).

### Client tool calls that mutate or fetch UI state

- **Metro Map**:
  - Client tool `get_selected_stations` pulls the currently selected nodes from the canvas so the agent can use client-side state in its response ([ChatKitPanel.tsx](examples/metro-map/frontend/src/components/ChatKitPanel.tsx), [metro_map_agent.py](examples/metro-map/backend/app/agents/metro_map_agent.py)).

### Fire-and-forget client effects

- **Cat Lounge**:
  - Client effects `update_cat_status` and `cat_say` are invoked by server tools to sync UI state and surface speech bubbles; handled via `onEffect` in [ChatKitPanel.tsx](examples/cat-lounge/frontend/src/components/ChatKitPanel.tsx).
- **Metro Map**:
  - Client effect `location_select_mode` is streamed within the server action handler ([server.py](examples/metro-map/backend/app/server.py)) after a line is chosen and updates the metro map canvas ([ChatKitPanel.tsx](examples/metro-map/frontend/src/components/ChatKitPanel.tsx)).
  - Client effect `add_station` is streamed by the agent after map updates to immediately sync the canvas and focus the newly created stop ([metro_map_agent.py](examples/metro-map/backend/app/agents/metro_map_agent.py), [ChatKitPanel.tsx](examples/metro-map/frontend/src/components/ChatKitPanel.tsx)).
- **Customer Support**:
  - The server streams `customer_profile/update` effects after tools or widget actions so the side panel mirrors the latest itinerary, loyalty, and timeline data ([support_agent.py](examples/customer-support/backend/app/support_agent.py), [server.py](examples/customer-support/backend/app/server.py)).

### Page-aware model responses

- **News Guide**:
  - The ChatKit client forwards the currently open article id in an `article-id` header so the backend can scope responses to “this page” ([ChatKitPanel.tsx](examples/news-guide/frontend/src/components/ChatKitPanel.tsx)).
  - The server reads that request context and exposes `get_current_page` so the agent can load full content without asking the user to paste it ([main.py](examples/news-guide/backend/app/main.py), [news_agent.py](examples/news-guide/backend/app/agents/news_agent.py)).

### Progress updates

- **News Guide**:
  - Retrieval tools stream `ProgressUpdateEvent` messages while searching tags, authors, keywords, exact text, or loading the current page so the UI surfaces “Searching…”/“Loading…” states ([news_agent.py](examples/news-guide/backend/app/agents/news_agent.py)).
  - The event finder emits progress as it scans dates, days of week, or keywords to keep users informed during longer lookups ([event_finder_agent.py](examples/news-guide/backend/app/agents/event_finder_agent.py)).
- **Metro Map**:
  - The metro agent emits a progress update while retrieving map information in `get_map`; it also emits a progress update while waiting for a client tool call to complete in `get_selected_stations` ([metro_map_agent.py](examples/metro-map/backend/app/agents/metro_map_agent.py)).

### Response lifecycle UI state

- **Metro Map**:
  - The client locks map interaction at response start and unlocks when the stream ends so canvas state doesn’t drift during agent updates by adding `onResponseStart` and `onResponseEnd` handlers ([ChatKitPanel.tsx](examples/metro-map/frontend/src/components/ChatKitPanel.tsx)).

### Widgets without actions

- **Cat Lounge**:
  - Server tool `show_cat_profile` streams a presentation widget defined in [profile_card_widget.py](examples/cat-lounge/backend/app/profile_card_widget.py).

### Widgets with actions

- **Cat Lounge**:
  - Server tool `suggest_cat_names` streams a widget with action configs that specify `cats.select_name` and `cats.more_names` client-handled actions.
  - When the user clicks the widget, these actions are handled with the `handleWidgetAction` callback in [ChatKitPanel.tsx](examples/cat-lounge/frontend/src/components/ChatKitPanel.tsx).
- **Customer Support**:
  - Flight and meal widgets stream with action payloads (`flight.select`, `support.set_meal_preference`) to capture choices before booking, built from `.widget` templates ([flight_options.py](examples/customer-support/backend/app/flight_options.py), [meal_preferences.py](examples/customer-support/backend/app/meal_preferences.py), [support_agent.py](examples/customer-support/backend/app/support_agent.py)).
- **News Guide**:
  - Article list widgets render “View” buttons that dispatch `open_article` actions for client navigation and engagement ([news_agent.py](examples/news-guide/backend/app/agents/news_agent.py), [article_list_widget.py](examples/news-guide/backend/app/widgets/article_list_widget.py)).
  - The event finder streams a timeline widget with `view_event_details` buttons configured for server handling so users can expand items inline ([event_finder_agent.py](examples/news-guide/backend/app/agents/event_finder_agent.py), [event_list_widget.py](examples/news-guide/backend/app/widgets/event_list_widget.py)).
- **Metro Map**:
  - The server tool `show_line_selector` streams a widget with the `line.select` action configured to fire on list item click ([metro_map_agent.py](examples/metro-map/backend/app/agents/metro_map_agent.py), [line_select_widget.py](examples/metro-map/backend/app/widgets/line_select_widget.py)).

### Server-handled widget actions

- **Cat Lounge**:
  - The `cats.select_name` action is also handled server-side to reflect updates to data and stream back an updated version of the name suggestions widget in [server.py](examples/cat-lounge/backend/app/server.py).
  - It is invoked using `chatkit.sendAction()` from `handleWidgetAction` callback in [ChatKitPanel.tsx](examples/cat-lounge/frontend/src/components/ChatKitPanel.tsx).
- **Customer Support**:
  - Action handlers persist bookings, meals, upsells, and rebooks; lock widgets; log hidden context; and refresh the profile when users click `flight.select`, `support.set_meal_preference`, `booking.*`, `upsell.*`, or `rebook.select_option` ([server.py](examples/customer-support/backend/app/server.py)).
- **News Guide**:
  - The `view_event_details` action is processed server-side to update the timeline widget with expanded descriptions without a round trip to the model ([server.py](examples/news-guide/backend/app/server.py)).
- **Metro Map**:
  - The `line.select` action is handled server-side to stream an updated widget, add a `<LINE_SELECTED>` hidden context item to thread, stream an assistant message to ask the user whether to add the station at the line’s start or end, and trigger the `location_select_mode` client effect for the UI to sync ([server.py](examples/metro-map/backend/app/server.py)).

### Attachments

- **Customer Support**:
  - End-to-end image attachments: the backend issues upload/download URLs, enforces image/size limits, and converts uploads to data URLs for the model ([attachment_store.py](examples/customer-support/backend/app/attachment_store.py), [main.py](examples/customer-support/backend/app/main.py), [thread_item_converter.py](examples/customer-support/backend/app/thread_item_converter.py)). The React panel registers `attachments.create`, uploads via the signed URL, and drops the attachment into the composer when travellers share inspiration photos ([CustomerContextPanel.tsx](examples/customer-support/frontend/src/components/CustomerContextPanel.tsx)).

### Annotations

- **Metro Map**:
  - The `plan_route` tool renders each station in a planned route as an entity source on the assistant message; the client’s entity click handler pans the React Flow canvas to the clicked station ([ChatKitPanel.tsx](examples/metro-map/frontend/src/components/ChatKitPanel.tsx), [metro_map_agent.py](examples/metro-map/backend/app/agents/metro_map_agent.py)).

### Thread titles

- **Cat Lounge**:
  - After the user names the cat, the `set_cat_name` tool locks in the name and updates the thread title to `{name}’s Lounge` before saving it ([cat_agent.py](examples/cat-lounge/backend/app/cat_agent.py)).
- **Customer Support**:
  - A lightweight title agent names the conversation on the first user message without delaying the first reply ([title_agent.py](examples/customer-support/backend/app/title_agent.py), [server.py](examples/customer-support/backend/app/server.py)).
- **News Guide**:
  - The `title_agent` runs on the first user message to generate a short newsroom-friendly title when none exists ([server.py](examples/news-guide/backend/app/server.py), [title_agent.py](examples/news-guide/backend/app/agents/title_agent.py)).
- **Metro Map**:
  - The metro server uses a dedicated `title_agent` to set a brief metro-planning title on the first turn and persists it to thread metadata ([server.py](examples/metro-map/backend/app/server.py), [title_agent.py](examples/metro-map/backend/app/agents/title_agent.py)).

### Entity tags (@-mentions)

- **News Guide**:
  - Entity search and previews power @-mentions for articles/authors in the composer and render hover previews via `/articles/tags` ([ChatKitPanel.tsx](examples/news-guide/frontend/src/components/ChatKitPanel.tsx), [main.py](examples/news-guide/backend/app/main.py)).
  - Tagged entities are converted into model-readable markers so the agent can fetch the right records (`<ARTICLE_REFERENCE>` / `<AUTHOR_REFERENCE>`) ([thread_item_converter.py](examples/news-guide/backend/app/thread_item_converter.py)).
  - Article reference tags are resolved into full articles via the instructed `get_article_by_id` tool before the agent cites details ([news_agent.py](examples/news-guide/backend/app/agents/news_agent.py)).
- **Metro Map**:
  - The composer’s entity search lists stations so users can @-mention them; clicking a tag also focuses the station on the canvas ([ChatKitPanel.tsx](examples/metro-map/frontend/src/components/ChatKitPanel.tsx)).
  - Tagged stations are converted into `<STATION_TAG>` blocks with full line metadata so the agent can answer without another lookup ([thread_item_converter.py](examples/metro-map/backend/app/thread_item_converter.py), [server.py](examples/metro-map/backend/app/server.py)).

### Tool choice (composer menu)

- **News Guide**:
  - The ChatKit client is configured with a `composer.tools` option that specifies options in the composer menu ([ChatKitPanel.tsx](examples/news-guide/frontend/src/components/ChatKitPanel.tsx))
  - Composer tool buttons let users force specific agents (`event_finder`, `puzzle`), setting `tool_choice` on the request ([config.ts](examples/news-guide/frontend/src/lib/config.ts)).
  - The backend routes these tool choices to specialized agents before falling back to the News Guide agent ([server.py](examples/news-guide/backend/app/server.py)).

### Custom header actions

- **Metro Map**:
  - The chat header uses a right-side icon toggle (`dark-mode` / `light-mode`) to flip the app’s color scheme client-side ([ChatKitPanel.tsx](examples/metro-map/frontend/src/components/ChatKitPanel.tsx)).
