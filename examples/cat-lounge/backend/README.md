# ChatKit Python Backend

> For the steps to run both frontend and backend apps in this repo, please refer to the README.md at the top directory instead.

This FastAPI service wires up the **Cozy Cat Companion** ChatKit server. The agent keeps per-thread cat stats in sync, streams themed widgets (cat name picker + profile card), and exposes a REST endpoint the frontend uses to refresh the dashboard.

## Features

- **ChatKit endpoint** at `POST /chatkit` that streams responses using the ChatKit protocol.
- **Guardrail-ready system prompt** extracted into `app/constants.py` for easy iteration.
- **In-memory stores** for conversation history (`MemoryStore`) and cat stats (`CatStore`).
- **REST helpers**
  - `GET /cats/{thread_id}` – fetch the latest cat stats for a thread.

## Getting started

To enable the realtime assistant you need to install both the ChatKit Python package and the OpenAI SDK, then provide an `OPENAI_API_KEY` environment variable.

```bash
uv sync
export OPENAI_API_KEY=sk-proj-...
uv run uvicorn app.main:app --reload
```
