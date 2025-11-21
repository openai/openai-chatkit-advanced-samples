# Repository Guidelines

## Project Structure & Modules
- `frontend/`: Vite + React ChatKit client (entry: `frontend/src/main.tsx`).
- `backend/`: FastAPI server powering agent responses (entry: `backend/app/main.py`).
- `examples/`: Sample flows, prompts, and integration patterns.
- Root `package.json` / tooling scripts: shared dev utilities and lint/test runners.

## Build, Test, and Development
- Frontend dev: `cd frontend && npm install && npm run dev` (starts Vite on `http://127.0.0.1:5170`).
- Frontend build: `cd frontend && npm run build` (production bundle).
- Backend dev: `cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000`.
- Backend tests (when present): `cd backend && uv run pytest`.

## Coding Style & Naming
- Follow OpenAI ChatKit official examples and coding patterns.
- TypeScript/JavaScript: 2-space indentation, prefer functional React components, `PascalCase` for components, `camelCase` for variables and functions.
- Python: 4-space indentation, type hints where practical, `snake_case` for functions and variables, `PascalCase` for classes.
- Use existing formatters/linters (e.g., `npm run lint`, `npm run format`, or `uv run`-based tools) instead of introducing new ones.

## Testing Guidelines
- Prefer small, focused tests near the relevant code (e.g., `frontend/src/**/__tests__` or `backend/tests`).
- Name tests descriptively (e.g., `chat_session.spec.ts`, `test_chat_routes.py`).
- Ensure core chat flows, error handling, and configuration parsing are covered before shipping.

## Commits & Pull Requests
- Write concise, imperative commit messages (e.g., `feat: add message streaming`, `fix: handle missing api key`).
- Keep PRs scoped: one feature or fix per PR when possible.
- PR description should include: overview, implementation notes, testing steps, and any screenshots or logs relevant to ChatKit behavior.

## Security & Configuration
- Never commit secrets; use env vars such as `OPENAI_API_KEY` and `VITE_CHATKIT_API_DOMAIN_KEY`.
- Mirror allowed domains in `frontend/vite.config.ts` and the OpenAI domain allowlist.
- Treat this repo as production-bound: prioritize robustness, clear error messages, and deploy-safe defaults.

