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

| ChatKit capability                                                 | Example reference                                                                                              |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| Server tool calls to retrieve application data for inference       | Cat Lounge:<br>- `get_cat_status`                                                                              |
| Client tool calls that mutate UI state                             | Cat Lounge:<br>- `feed_cat`<br>- `play_with_cat`<br>- `clean_cat`<br>- `speak_as_cat`<br>- `update_cat_status` |
| Widget + action flows (interactive cards, follow-up actions)       | Cat Lounge widgets/actions:<br>- `suggest_cat_names`<br>- `cats.select_name`<br>- `show_cat_profile`           |
| Domain-integrated workflows (seat changes, cancellations, baggage) | Customer Support tools:<br>- `change_seat`<br>- `cancel_trip`<br>- `add_checked_bag`<br>- `request_assistance` |
| Agent-triggered widgets streaming into an existing UI panel        | Customer Support widget tool:<br>- `meal_preference_list`                                                      |
