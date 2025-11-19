# Metro Map

Chat-driven GUI updates for a metro map using a React Flow canvas that lets the user extend lines with new stations.

## Quickstart

1. Export `OPENAI_API_KEY` (and `VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_local_dev` for local).
2. From the repo root run `npm run metro-map` (or `cd examples/metro-map && npm install && npm run start`).
3. Go to http://localhost:5173

## Example prompts

- "Add a new station named Aurora" (line picker widget will appear)
- "Plan a route from Titan Border to Lyra Verge."
- "Tell me about @Cinderia station." (@-mention stations; need to type @ manually, copy paste won't work)

## Features

- Map sync + lookup tools: `get_map`, `list_lines`, `list_stations`, `get_line_route`, `get_station` keep the agent grounded in the latest network data.
- Plan-a-route responses attach entity sources for each station in the recommended path so ChatKit can keep the canvas focused on the stops being discussed.
- Station creation flow: `show_line_selector` streams a clickable `line.select` widget, the server stashes `<LINE_SELECTED>`, and `add_station` triggers a widget update and a client tool call to refresh the canvas and focus the new stop.
- Location placement helper: after a line is chosen, a `location_select_mode` client tool call flips the UI into placement mode so users pick start/end of line for insertion.
- Progress updates: initial map fetch streams a quick progress event while loading line data.
- Entity tags: station @-mentions in the composer add `<STATION_TAG>` content for the agent and can be clicked to focus the station on the canvas.
- Custom header action: a right-side icon toggles dark/light themes in the ChatKit header.
