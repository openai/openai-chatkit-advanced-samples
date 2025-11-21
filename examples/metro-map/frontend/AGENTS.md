# Repository Guidelines

## Scope & Layout
- This guide applies to `examples/metro-map/frontend`.
- Entry point: `src/main.tsx`; main app shell in `src/App.tsx`.
- Map and UI composition live in `src/components` and `src/lib` (e.g., `map.ts`, `fonts.ts`).

## Development & Build
- Dev server: `npm install && npm run dev`.
- Production build: `npm run build`.
- Linting: `npm run lint`.

## Coding Style & Patterns
- Follow the OpenAI Metro Map ChatKit example style.
- 2-space indentation, functional React components, hooks for state.
- `PascalCase` for components (`MetroMapCanvas.tsx`), `camelCase` for helpers and hooks, `kebab-case` for CSS modules.
- Keep routing-related code in one place (`react-router-dom` usage) and avoid duplicating route constants.

## State & Components
- Store map state in `src/store` (`useMapStore.ts`, `useAppStore.ts`); avoid prop drilling for global state.
- Keep ChatKit-specific logic in dedicated components and helpers so the map UI remains reusable.

## Testing & QA
- Add tests for complex map interactions and store logic when extending behavior.
- Manually verify: node selection, path generation, and chat explanations of the map.

