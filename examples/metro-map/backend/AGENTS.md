# Repository Guidelines

## Scope & Layout
- This guide applies to `examples/metro-map/backend`.
- FastAPI entry: `app/main.py`; server-side rendering helpers may use Jinja2 templates.

## Development & Tooling
- Install deps: `uv sync`.
- Run server: `uv run uvicorn app.main:app --reload --port 8000`.
- Static checks (optional): `uv run ruff check app` and `uv run mypy app`.

## Coding Style
- 4-space indentation, `snake_case` naming, type hints for key functions.
- Follow OpenAI ChatKit examples for agent composition and tools.
- Keep map domain logic separate from HTTP endpoints for reuse.

## Agent & Domain Logic
- Encode metro lines, stations, and paths in dedicated modules, not inline in routes.
- Ensure agents explain paths clearly and handle impossible routes gracefully.
- Treat this as deployable: input validation, safe defaults, and clear logging.

## Testing & QA
- Add tests around path-finding, data loading, and agent responses for tricky routes.
- Manually validate that responses remain consistent with the frontend’s map view.

