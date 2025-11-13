# OpenAI ChatKit Examples

This repository collects scenario-driven ChatKit demos. Each example pairs a FastAPI backend with a Vite + React frontend, implementing a custom backend using ChatKit Python SDK and wiring it up with ChatKit.js client-side.

You can run the following examples:

- [**Cat Lounge**](examples/cat-lounge) - caretaker for a virtual cat that helps improve energy, happiness, and cleanliness stats.
- [**Customer Support**](examples/customer-support) – airline concierge with live itinerary data, timeline syncing, and domain-specific tools.

## Quickstart

1. Export `OPENAI_API_KEY`.
2. Make sure `uv` is installed.
3. Launch an example from the repo root, or with `npm run start` from the project directory:

| Example          | Command for repo root      | Command for project directory                              | URL                   |
| ---------------- | -------------------------- | ---------------------------------------------------------- | --------------------- |
| Cat Lounge       | `npm run cat-lounge`       | `cd examples/cat-lounge && npm install && npm run start`   | http://localhost:5170 |
| Customer Support | `npm run customer-support` | `cd examples/customer-support && npm install && npm start` | http://localhost:5171 |

## Feature index

### Server tool calls to retrieve application data for inference

- **Cat Lounge**:
  - Function tool `get_cat_status` ([cat_agent.py](examples/cat-lounge/backend/app/cat_agent.py)) pulls the latest cat stats for the agent.

### Client tool calls that mutate UI state

- **Cat Lounge**:
  - Client tool `update_cat_status` is invoked by server tools `feed_cat`, `play_with_cat`, `clean_cat`, and `speak_as_cat` to sync UI state.
  - When invoked, it is handled client-side with the `handleClientToolCall` callback in [ChatKitPanel.tsx](examples/cat-lounge/frontend/src/components/ChatKitPanel.tsx).

### Widgets without actions

- **Cat Lounge**:
  - Server tool `show_cat_profile` streams a presentation widget defined in [profile_card_widget.py](examples/cat-lounge/backend/app/profile_card_widget.py).

### Widgets with actions

- **Cat Lounge**:
  - Server tool `suggest_cat_names` streams a widget with action configs that specify `cats.select_name` and `cats.more_names` client-handled actions.
  - When the user clicks the widget, these actions are handled with the `handleWidgetAction` callback in [ChatKitPanel.tsx](examples/cat-lounge/frontend/src/components/ChatKitPanel.tsx).

### Server-handled widget actions

- **Cat Lounge**:
  - The `cats.select_name` action is also handled server-side to reflect updates to data and stream back an updated version of the name suggestions widget in [server.py](examples/cat-lounge/backend/app/server.py).
  - It is invoked using `chatkit.sendAction()` from `handleWidgetAction` callback in [ChatKitPanel.tsx](examples/cat-lounge/frontend/src/components/ChatKitPanel.tsx).
