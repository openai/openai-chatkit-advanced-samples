# Repository Guidelines

## Scope & Layout
- This guide applies to `examples/customer-support/frontend`.
- Entry: `src/App.tsx`; ChatKit wrapper lives in `src/components/ChatKitPanel.tsx`.
- Hooks and shared logic live under `src/hooks`.

## Development & Build
- Dev server: `npm install && npm run dev`.
- Production build: `npm run build`.
- Linting: `npm run lint`; tests (when present): `npm test` or `npx vitest`.

## Coding Style
- Follow the official OpenAI ChatKit React examples.
- 2-space indentation, functional components, hooks for state and effects.
- `PascalCase` for React components (`SupportLayout.tsx`), `camelCase` for helpers and hooks (e.g., `useSomething`), `kebab-case` for CSS/Tailwind utility groups.
- Keep airline-specific logic in dedicated components or hooks, not in the ChatKit wrapper.

## Components & UX
- Let `ChatKitPanel` focus on conversation UI and ChatKit configuration.
- Keep customer-support specific UX (e.g., forms, summaries) in separate components.
- Use Tailwind utility classes consistently and avoid inline style objects.

## Testing & QA
- When adding features, create co-located tests for complex hooks or components.
- Smoke-test core flows: starting a conversation, updating preferences, and handling errors from the backend.

