# Repository Guidelines

## Scope & Layout
- This guide applies to `examples/cat-lounge/frontend`.
- Entry point: `src/main.tsx`; main UI in `src/App.tsx` and `src/components/*`.
- Shared UI state lives in `src/store/*`; ChatKit wiring in `src/lib/config.ts`.

## Development & Build
- Dev server: `npm install && npm run dev`.
- Production build: `npm run build`.
- Linting: `npm run lint` (ESLint + TypeScript, aligned with OpenAI examples).

## Coding Style & Naming
- Use functional React components and hooks.
- 2-space indentation, no semicolon changes from defaults.
- `PascalCase` for component files (`CatStatusPanel.tsx`), `camelCase` for variables and functions.
- Keep ChatKit-related config small and composable; avoid duplicating logic across components.

## Components & State
- `ChatKitPanel.tsx` owns the chat surface; keep it focused on layout and high-level orchestration.
- Store app-specific state in `src/store/useAppStore.ts`; avoid ad-hoc React context.
- Put reusable UI pieces in `src/components`, domain helpers in `src/lib`.

## Testing & QA
- When adding features, prefer co-located tests under `src/**/__tests__` (Vitest) following the patterns in other examples.
- Manually verify message streaming, widget rendering, and theme toggling in the browser before shipping.

