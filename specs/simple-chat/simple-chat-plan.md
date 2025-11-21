# Simple Chat Implementation Plan

## Overview

A minimal ChatKit application providing pure conversation functionality with OpenAI's GPT-4.1 model with reasoning capabilities.

## Architecture

```
apps/simple-chat/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI with /chatkit endpoint
│   │   ├── server.py            # SimpleChatServer (ChatKitServer subclass)
│   │   ├── memory_store.py      # In-memory thread/message storage
│   │   ├── thread_item_converter.py
│   │   └── agents/
│   │       └── simple_agent.py  # GPT-4.1 agent with reasoning
│   ├── scripts/
│   │   └── run-backend.sh       # Uvicorn launcher (port 8003)
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main layout with header
│   │   ├── main.tsx             # Entry point
│   │   ├── index.css            # Tailwind styles
│   │   ├── components/
│   │   │   ├── ChatKitPanel.tsx # ChatKit SDK integration
│   │   │   └── ThemeToggle.tsx  # Light/dark mode toggle
│   │   ├── store/
│   │   │   └── useAppStore.ts   # Zustand (theme, threadId)
│   │   └── lib/
│   │       └── config.ts        # API URL, greeting, prompts
│   ├── vite.config.ts           # Port 5173, proxy to backend
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
└── package.json                  # Concurrently launcher
```

## Key Implementation Details

### Agent Configuration
- Model: `gpt-4.1` with reasoning (`effort: "low"`, `summary: "auto"`)
- No custom tools - pure conversation
- Instructions: "You are a helpful assistant."

### Backend
- FastAPI POST `/chatkit` endpoint
- SimpleChatServer extends ChatKitServer
- In-memory store for thread/message persistence
- No widget actions (simple respond-only)

### Frontend
- React 19 with Vite
- ChatKit SDK via `@openai/chatkit-react`
- Zustand for state (theme, threadId)
- Tailwind CSS with dark mode support
- Starter prompts for quick actions

### Ports
- Frontend: 5173
- Backend: 8003

## Running

```bash
export OPENAI_API_KEY=sk-...
npm run simple-chat
```

Opens at http://localhost:5173
