# Repository Guidelines

## Scope & Layout
- This guide applies to `examples/news-guide/backend`.
- FastAPI app entry: `app/main.py`.
- Agents live in `app/agents/*_agent.py`; widgets in `app/widgets`; article/event data and stores in `app/data`.

## Development & Tooling
- Install deps: `uv sync`.
- Run server: `uv run uvicorn app.main:app --reload --port 8000`.
- Static checks: `uv run ruff check app` and `uv run mypy app` when available.

## Coding Style
- 4-space indentation, `snake_case` naming, type hints for key functions and agent entrypoints.
- Follow OpenAI ChatKit newsroom example structure: thin routes, rich agent modules.

## Agents, Data & Widgets
- Keep agents focused: one concern per file (news, events, puzzles, titles).
- Treat `app/data` as the single source of truth for articles/events; avoid duplicating data structures.
- Keep widgets small and composable, returning predictable shapes for the frontend.

## Testing & QA
- Add tests for article lookup, event filtering, and agent behavior around edge cases.
- Manually verify that backend responses match frontend expectations for article lists, previews, and chat-driven navigation.

