# OpenAI ChatKit Advanced Samples

This repository contains a few advanced examples, which serve a complete [ChatKit](https://github.com/openai/chatkit-js) playground that pairs a FastAPI backend with a Vite + React frontend.

The top-level [**backend**](backend) and [**frontend**](frontend) directories provide a basic project template that demonstrates ChatKit UI, widgets, and client tools.

- It runs a custom ChatKit server built with [ChatKit Python SDK](https://github.com/openai/chatkit-python) and [OpenAI Agents SDK for Python](https://github.com/openai/openai-agents-python).
- Available agent tools focus on caring for the virtual cat: status checks, feeding, playtime,
  cleaning, name selection, and a profile widget, plus client tools for switching the UI theme,
  updating the dashboard stats, and triggering cat speech bubbles.

The Vite server proxies all `/chatkit` traffic straight to the local FastAPI service so you can develop the client and server in tandem without extra wiring.

## Quickstart

1. Start FastAPI backend API.
2. Configure the frontend's domain key and launch the Vite app.
3. Explore the demo flow.

Each step is detailed below.

### 1. Start FastAPI backend API

From the repository root you can bootstrap the backend in one step:

```bash
npm run backend
```

This command runs `uv sync` for `backend/` and launches Uvicorn on `http://127.0.0.1:8000`. Make sure [uv](https://docs.astral.sh/uv/getting-started/installation/) is installed and `OPENAI_API_KEY` is exported beforehand.

If you prefer running the backend from inside `backend/`, follow the manual steps:

```bash
cd backend
uv sync
export OPENAI_API_KEY=sk-proj-...
uv run uvicorn app.main:app --reload --port 8000
```

If you don't have uv, you can do the same with:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
export OPENAI_API_KEY=sk-proj-...
uvicorn app.main:app --reload
```

The development API listens on `http://127.0.0.1:8000`.

### 2. Run Vite + React frontend

From the repository root you can start the frontend directly:

```bash
npm run frontend
```

This script launches Vite on `http://127.0.0.1:5170`.

To configure and run the frontend manually:

```bash
cd frontend
npm install
npm run dev
```

Optional configuration hooks live in [`frontend/src/lib/config.ts`](frontend/src/lib/config.ts) if you want to tweak API URLs or UI defaults.

To launch both the backend and frontend together from the repository root, you can use `npm start`. This command also requires `uv` plus the necessary environment variables (for example `OPENAI_API_KEY`) to be set beforehand.

The Vite dev server runs at `http://127.0.0.1:5170`, and this works fine for local development. However, for production deployments:

1. Host the frontend on infrastructure you control behind a managed domain.
2. Register that domain on the [domain allowlist page](https://platform.openai.com/settings/organization/security/domain-allowlist) and add it to [`frontend/vite.config.ts`](frontend/vite.config.ts) under `server.allowedHosts`.
3. Set `VITE_CHATKIT_API_DOMAIN_KEY` to the value returned by the allowlist page.

If you want to verify this remote access during development, temporarily expose the app with a tunnel (e.g. `ngrok http 5170` or `cloudflared tunnel --url http://localhost:5170`) and add that hostname to your domain allowlist before testing.

### 3. Explore the demo flow

With the app reachable locally or via a tunnel, open it in the browser and try a few interactions. Each ChatKit thread maintains its own cat state (energy, happiness, cleanliness, name, and age), so switching threads gives every conversation a unique pet without leaking stats between them. That per-thread state is what powers the meters, flash messages, and widgets on the dashboard.

Try these prompts:

- `Please give the cat a snack` or `Play with the cat for a few minutes` - invokes the `feed_cat` or `play_with_cat` server tool calls followed by the `update_cat_status` client tool call to update the cat's stats and render the new values.
- `I want to name the cat` - if you don't specify a name, the agent calls `suggest_cat_names` to render an interactive widget; picking an option fires the `cats.select_name` action, persists the name on the server, and retitles the thread for that cat going forward.
- `Name the cat Mr. Whiskers` - invokes the `set_cat_name` server tool call to update the cat's profile and the thread title, followed by the `update_cat_status` client tool call to reflect the changes client-side.
- `Show me the cat's profile card` - the `show_cat_profile` tool renders a static widget using the current cat name.
- `Hi, cat!` - the `speak_as_cat` tool invokes the `cat_say` client tool call to render a speech bubble for the cat.

Quick actions:

- Quick action buttons will send prompts on the user's behalf using ChatKit's `sendUserMessage` command.

## What's next

Under the [`examples`](examples) directory, you'll find three more sample apps that ground the starter kit in real-world scenarios:

1. [**Customer Support**](examples/customer-support): airline customer support workflow.
2. [**Knowledge Assistant**](examples/knowledge-assistant): knowledge-base agent backed by OpenAI's File Search tool.
3. [**Marketing Assets**](examples/marketing-assets): marketing creative workflow.

Each example under [`examples/`](examples) includes the helper scripts (`npm start`, `npm run frontend`, `npm run backend`) pre-configured with its dedicated ports, so you can `cd` into an example and run `npm start` to boot its backend and frontend together. Please note that when you run `npm start`, `uv` must already be installed and all required environment variables should be exported.
