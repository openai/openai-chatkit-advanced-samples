# ChatKit Python Backend

> For the steps to run both frontend and backend apps in this repo, please refer to the README.md at the top directory instead.

This FastAPI service powers the **News Guide** ChatKit server. The agent keeps up with a local
article feed, exposes a REST API for the landing page, and streams responses to the ChatKit
React client.

## Features

- **Article data store** (`ArticleStore`) that hydrates itself on boot from `app/data`.
- **ChatKit endpoint** at `POST /chatkit` for conversational responses.
- **REST helpers**
  - `GET /articles` – list article metadata for the landing page.
  - `GET /articles/{article_id}` – return metadata + markdown content for a specific article.

## Getting started

To enable the realtime assistant you need to install both the ChatKit Python package and the OpenAI SDK, then provide an `OPENAI_API_KEY` environment variable.

```bash
uv sync
export OPENAI_API_KEY=sk-proj-...
uv run uvicorn app.main:app --reload
```
