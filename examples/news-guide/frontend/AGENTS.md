# Repository Guidelines

## Scope & Layout
- This guide applies to `examples/news-guide/frontend`.
- Entry point: `src/main.tsx`; app shell in `src/App.tsx`.
- ChatKit integration is centered in `src/components/ChatKitPanel.tsx`; newsroom UI in `src/components/NewsroomPanel.tsx` and `src/components/ThemeToggle.tsx`.

## Development & Build
- Dev server: `npm install && npm run dev`.
- Production build: `npm run build`.
- Linting: `npm run lint`.

## Coding Style
- Follow OpenAI ChatKit newsroom example patterns.
- 2-space indentation, functional components, hooks for state and routing.
- `PascalCase` for components, `camelCase` for helpers and hooks, `kebab-case` for CSS files like `NewsroomPanel.css`.
- Keep article data helpers and fonts in `src/lib`; keep state in `src/store`.

## Testing & QA
- Add tests for tag filtering, article selection, and any non-trivial hooks.
- Manually verify: navigating between views, loading articles, and interacting with the ChatKit panel.

