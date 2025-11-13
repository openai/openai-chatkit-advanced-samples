# OpenAI ChatKit Examples

This repository collects scenario-driven ChatKit demos. Each example pairs a FastAPI backend with a Vite + React frontend, implementing a custom backend using ChatKit Python SDK and wiring it up with ChatKit.js client-side.

You can run the following examples:

- [**Cat Lounge**](examples/cat-lounge) - caretaker for a virtual cat that helps improve energy, happiness, and cleanliness stats.
- [**Customer Support**](examples/customer-support) – airline concierge with live itinerary data, timeline syncing, and domain-specific tools.

## Quickstart

1. Export `OPENAI_API_KEY` and `VITE_CHATKIT_API_DOMAIN_KEY` (any non-empty placeholder works locally).
2. Make sure `uv` is installed
3. Launch an example from the repo root, or with `npm run start` from the project directory:

| Example          | Command for repo root      | Command for project directory                              | URL                   |
| ---------------- | -------------------------- | ---------------------------------------------------------- | --------------------- |
| Cat Lounge       | `npm run cat-lounge`       | `cd examples/cat-lounge && npm install && npm run start`   | http://localhost:5170 |
| Customer Support | `npm run customer-support` | `cd examples/customer-support && npm install && npm start` | http://localhost:5171 |

## Feature index

| ChatKit capability                                           | Cat Lounge                                                                                                                                              | Customer Support |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Server tool calls to retrieve application data for inference | Function tool:<br>- `get_cat_status`                                                                                                                    |                  |
| Client tool calls that mutate UI state                       | The client tool `update_cat_status` is invoked by the following server tools:<br>- `feed_cat`<br>- `play_with_cat`<br>- `clean_cat`<br>- `speak_as_cat` |                  |
| Interactive widgets, follow-up actions                       | The `suggest_cat_names` tool call outputs a widget with action handlers.<br><br>The `cats.select_name` action is handled client-side.                   |                  |
| Presentation widgets                                         | The `show_cat_profile` tool call outputs a non-interactive widget to present application data.                                                          |                  |
