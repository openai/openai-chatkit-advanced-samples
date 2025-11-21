# Architecture

Understanding the patterns used in ChatKit applications.

## Overview

Each app is a full-stack application with:
- **Backend**: Python FastAPI server using `openai-chatkit` and `openai-agents`
- **Frontend**: React app using `@openai/chatkit-react`

```
┌─────────────────┐     HTTP/SSE      ┌─────────────────┐
│                 │ ←───────────────→ │                 │
│    Frontend     │                   │    Backend      │
│  (React/Vite)   │   POST /chatkit   │   (FastAPI)     │
│                 │                   │                 │
│  ChatKit SDK    │                   │  ChatKitServer  │
│                 │                   │  + Agent SDK    │
└─────────────────┘                   └─────────────────┘
```

## Backend Architecture

### ChatKitServer

The server extends `ChatKitServer` and implements two methods:

```python
class MyServer(ChatKitServer[dict[str, Any]]):
    def __init__(self):
        self.store = MemoryStore()
        super().__init__(self.store)

    async def respond(self, thread, item, context):
        # Called when user sends a message
        # Run agent and stream response
        yield events...

    async def action(self, thread, action, sender, context):
        # Called when user interacts with a widget
        yield events...
```

### Agent Context

The agent context carries data accessible in tool calls:

```python
class MyAgentContext(AgentContext):
    store: Annotated[MemoryStore, Field(exclude=True)]
    request_context: dict[str, Any]
    # Add your custom fields here
```

### The respond() Flow

1. Create agent context with thread metadata
2. Load conversation history from store
3. Convert items to agent input format
4. Run agent with streaming
5. Yield events back to client

```python
async def respond(self, thread, item, context):
    agent_context = MyAgentContext(
        thread=thread,
        store=self.store,
        request_context=context,
    )

    items_page = await self.store.load_thread_items(thread.id, ...)
    items = list(reversed(items_page.data))
    input_items = await self.converter.to_agent_input(items)

    result = Runner.run_streamed(my_agent, input_items, context=agent_context)

    async for event in stream_agent_response(agent_context, result):
        yield event
```

### Memory Store

The store interface handles thread and message persistence:

```python
class MemoryStore(Store[dict[str, Any]]):
    # Thread operations
    async def load_thread(thread_id, context) -> ThreadMetadata
    async def save_thread(thread, context)
    async def load_threads(limit, after, order, context) -> Page[ThreadMetadata]
    async def delete_thread(thread_id, context)

    # Item operations
    async def load_thread_items(thread_id, ...) -> Page[ThreadItem]
    async def add_thread_item(thread_id, item, context)
    async def save_item(thread_id, item, context)
```

For production, implement a persistent store (database-backed).

### Agent Definition

Agents are defined using the OpenAI Agents SDK:

```python
from agents import Agent, function_tool

@function_tool(description_override="...")
async def my_tool(ctx: RunContextWrapper[MyAgentContext], param: str):
    # Access context
    thread_id = ctx.context.thread.id
    store = ctx.context.store
    # Do work and return result
    return {"result": "value"}

my_agent = Agent(
    name="MyAgent",
    instructions="System prompt...",
    model="gpt-4.1",
    tools=[my_tool],
)
```

## Frontend Architecture

### ChatKit Integration

The frontend uses the ChatKit SDK:

```tsx
import { ChatKit, useChatKit } from "@openai/chatkit-react";

function ChatKitPanel() {
  const chatkit = useChatKit({
    api: { url: "/chatkit", domainKey: "domain_pk_localhost_dev" },
    theme: { colorScheme: "light", density: "spacious" },
    startScreen: { greeting: "Hello!", prompts: [...] },
    onThreadChange: ({ threadId }) => setThreadId(threadId),
    onClientTool: (toolCall) => { /* handle client tools */ },
    onError: ({ error }) => console.error(error),
  });

  return <ChatKit control={chatkit.control} />;
}
```

### State Management

Apps use Zustand for simple state:

```tsx
import { create } from "zustand";

type AppState = {
  scheme: "light" | "dark";
  setScheme: (scheme: "light" | "dark") => void;
  threadId: string | null;
  setThreadId: (id: string | null) => void;
};

export const useAppStore = create<AppState>((set) => ({
  scheme: "light",
  setScheme: (scheme) => set({ scheme }),
  threadId: null,
  setThreadId: (threadId) => set({ threadId }),
}));
```

### Vite Proxy

The frontend proxies `/chatkit` to the backend:

```ts
// vite.config.ts
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      "/chatkit": {
        target: "http://127.0.0.1:8003",
        changeOrigin: true,
      },
    },
  },
});
```

## Advanced Patterns

### Client Tool Calls

Tools that update the frontend without server action:

```python
# Backend
ctx.context.client_tool_call = ClientToolCall(
    name="update_ui",
    arguments={"data": {...}},
)
```

```tsx
// Frontend
onClientTool: (toolCall) => {
  if (toolCall.name === "update_ui") {
    applyUpdate(toolCall.params.data);
    return { success: true };
  }
}
```

### Widgets

Interactive UI elements streamed from the backend:

```python
# Stream a widget
await ctx.context.stream_widget(widget_data)

# Handle widget action in server.action()
async def action(self, thread, action, sender, context):
    if action.type == "my_action":
        # Handle the action
        yield response_event
```

### Hidden Context

Persist state across turns without showing to user:

```python
await store.add_thread_item(
    thread_id,
    HiddenContextItem(
        id=generate_id(),
        thread_id=thread_id,
        created_at=datetime.now(),
        content="<STATE>data</STATE>",
    ),
    context,
)
```

## Dependencies

### Backend (pyproject.toml)
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai` - OpenAI Python SDK
- `openai-chatkit` - ChatKit server library
- `python-dotenv` - Environment variable loading

### Frontend (package.json)
- `@openai/chatkit-react` - ChatKit React SDK
- `react` / `react-dom` - React 19
- `zustand` - State management
- `vite` - Build tool
- `tailwindcss` - Styling
