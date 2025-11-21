# Repository Guidelines

## Scope & Layout
- This guide applies to all example apps under `examples/*`.
- Each example has a `backend/` (FastAPI + agents) and `frontend/` (Vite + React + ChatKit SDK).
- Keep new examples consistent with the existing ones (`cat-lounge`, `customer-support`, `metro-map`, `news-guide`).

## Frontend (Vite + React)
- Entry point: `frontend/src/main.tsx`; main UI in `frontend/src/App.tsx` and `frontend/src/components/*`.
- Use functional components, hooks, and 2-space indentation.
- Naming: `PascalCase` for components (`ChatKitPanel.tsx`), `camelCase` for variables and functions, `kebab-case` for CSS files.
- Local dev: `cd examples/<app>/frontend && npm install && npm run dev`.
- Build: `cd examples/<app>/frontend && npm run build`.

## Backend (FastAPI + Agents)
- Entry point: `backend/app/main.py`; agent logic in `backend/app/*_agent.py` and `widgets` or `components` modules.
- Follow OpenAI ChatKit example patterns for tools, widgets, and state handling.
- Use 4-space indentation, type hints where practical, and `snake_case` for functions/variables.
- Local dev: `cd examples/<app>/backend && uv sync && uv run uvicorn app.main:app --reload --port 8000`.

## Testing & Validation
- Prefer small, focused tests (e.g., `backend/tests`, `frontend/src/**/__tests__`) when extending examples.
- Ensure core chat flows, tool calls, and widget behavior are covered.
- Manually verify end-to-end: start backend + frontend and exercise key user journeys.

## Agent-Specific Practices
- Keep prompts and system messages close to the agent code for clarity.
- Design agents to be robust and deployable: explicit error handling, clear logging, and safe defaults.
- Avoid hard-coding secrets; rely on environment variables and documented configuration.

