# Repository Guidelines

## Scope & Layout
- This guide applies to `examples/cat-lounge/backend`.
- FastAPI app entry: `app/main.py`.
- Agent, state, and storage logic live in `app/*_agent.py`, `app/*_state.py`, and `app/*_store.py`.

## Development & Tooling
- Environment: Python 3.11+, `uv` for dependency management.
- Install deps: `uv sync`.
- Run server: `uv run uvicorn app.main:app --reload --port 8000`.
- Lint/format (when used): `uv run ruff check app` and `uv run mypy app`.

## Coding Style
- Follow OpenAI ChatKit backend examples.
- 4-space indentation, `snake_case` for functions and variables, `PascalCase` for classes.
- Use type hints for public functions and agent entrypoints.
- Keep agents small and composable: separate state, tools, and response shaping into dedicated modules.

## Agent & Widget Design
- Keep system prompts close to the agent code (`*_agent.py`) for clarity.
- Widgets such as profile cards or suggestions should live in dedicated widget modules.
- Ensure tools and widgets are deterministic, robust, and safe to deploy (explicit error handling, clear log messages).

## Testing & QA
- Add tests under `backend/tests` if you extend behavior, focusing on agent routing, state transitions, and widget outputs.
- Manually verify that the backend and frontend stay in sync for event names and payload shapes.

