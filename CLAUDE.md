# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **lab environment** for developing OpenAI-powered applications using OpenAI's ChatKit examples as battle-tested templates. The examples should not be modified unnecessarily - use them as reference patterns when building new projects.

## Development Commands

```bash
# Required: Export API key before running any example
export OPENAI_API_KEY=sk-...

# Run an example (frontend + backend together)
npm run news-guide      # http://localhost:5172 + http://127.0.0.1:8002
npm run metro-map       # Different ports per example
npm run cat-lounge
npm run customer-support

# Ctrl+C stops both frontend and backend (managed by concurrently)
```

## Architecture

Each example follows the same full-stack pattern:

```
examples/{name}/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint with /chatkit POST endpoint
│   │   ├── server.py         # ChatKitServer subclass - the core orchestrator
│   │   ├── agents/           # Agent definitions with tools
│   │   │   └── *_agent.py    # INSTRUCTIONS, context model, @function_tool decorators
│   │   ├── data/             # Domain data stores
│   │   ├── widgets/          # Widget builders
│   │   ├── memory_store.py   # Thread/message persistence (in-memory for demos)
│   │   └── request_context.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/ChatKitPanel.tsx  # ChatKit SDK integration
│   │   └── store/                       # Zustand/Jotai state
│   └── vite.config.ts
└── package.json
```

## Key Patterns

### Agent Definition (`agents/*_agent.py`)

```python
INSTRUCTIONS = """System prompt describing agent behavior..."""

class MyAgentContext(AgentContext):
    store: Annotated[MemoryStore, Field(exclude=True)]
    # Domain-specific fields

@function_tool(description_override="...")
async def my_tool(ctx: RunContextWrapper[MyAgentContext], param: str) -> Result:
    # Tool implementation

my_agent = Agent[MyAgentContext](
    model="gpt-4.1-mini",
    name="My Agent",
    instructions=INSTRUCTIONS,
    tools=[my_tool, ...],
    tool_use_behavior=StopAtTools(stop_at_tool_names=[...])
)
```

### Server Implementation (`server.py`)

- Extends `ChatKitServer[RequestContext]`
- Implements `respond()` for agent inference
- Implements `action()` for widget interactions
- Manages domain stores and memory

### Common Tool Patterns

- **Data retrieval**: Return structured data for agent reasoning
- **Widget display**: `ctx.context.stream_widget(widget)` to show UI
- **Hidden context**: `HiddenContextItem` to persist state across turns
- **Client tool calls**: `ClientToolCall` for frontend-only updates

## Creating New Projects

1. Copy an existing example that's closest to your use case
2. Modify `request_context.py` for your domain context
3. Create agents in `agents/` with your tools and instructions
4. Create data stores in `data/` for your domain
5. Update `server.py` to wire everything together
6. Update `main.py` with any REST endpoints you need
7. Add your example to root `package.json` scripts

## Important Notes

- Environment variables must be exported in the shell running npm (not just in .env)
- Each example runs on different ports - check the console output
- The openai-agents SDK handles OpenAI API calls
- Widgets use `.widget` JSON files with Jinja2 templates
