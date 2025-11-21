# Repository Guidelines

## Scope & Layout
- This guide applies to `examples/customer-support/backend`.
- FastAPI entry: `app/main.py`.
- Domain logic: `airline_state.py`, `support_agent.py`, `meal_preferences.py`, `thread_item_converter.py`.

## Development & Tooling
- Install deps: `uv sync`.
- Run server: `uv run uvicorn app.main:app --reload --port 8000`.
- Static checks (if used): `uv run ruff check app` and `uv run mypy app`.

## Coding Style
- Align with OpenAI ChatKit backend examples.
- 4-space indentation, `snake_case` naming, type hints for public APIs and agent functions.
- Keep HTTP handlers thin; push business logic into dedicated modules.

## Agent & Business Logic
- Model airline-specific concepts in `airline_state.py` and related modules, not in route handlers.
- Agents should be robust and deployable: validate inputs, handle missing data, and avoid leaking internal errors to users.
- Thread converters should produce stable, predictable structures for the frontend.

## Testing & QA
- Prefer tests under `backend/tests` for agents and key utilities.
- Manually verify: booking changes, meal preference flows, and edge cases like invalid confirmation numbers.

