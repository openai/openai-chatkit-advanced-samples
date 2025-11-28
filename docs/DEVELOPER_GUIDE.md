# ChatKit Developer Guide

A practical guide to building AI chat applications with OpenAI's ChatKit.

---

## How It All Fits Together

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Your Application                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────┐         ┌─────────────────────────────────┐  │
│   │       Frontend          │         │           Backend               │  │
│   │       (React)           │◄───────►│          (FastAPI)              │  │
│   │                         │   HTTP  │                                 │  │
│   │  ┌───────────────────┐  │         │  ┌───────────────────────────┐  │  │
│   │  │  ChatKit SDK      │  │         │  │   ChatKitServer           │  │  │
│   │  │  - Renders chat   │  │         │  │   - respond() → runs agent│  │  │
│   │  │  - Handles widgets│  │         │  │   - action() → handles UI │  │  │
│   │  │  - Sends actions  │  │         │  └───────────┬───────────────┘  │  │
│   │  └───────────────────┘  │         │              │                  │  │
│   │                         │         │              ▼                  │  │
│   │  ┌───────────────────┐  │         │  ┌───────────────────────────┐  │  │
│   │  │  Your UI          │  │         │  │   Agent(s)                │  │  │
│   │  │  - Status panels  │◄─┼─────────┼──┤   - Tools (functions)     │  │  │
│   │  │  - Canvas/maps    │  │ Client  │  │   - Instructions (prompt) │  │  │
│   │  │  - Custom views   │  │ Tools   │  │   - Model (gpt-4.1-mini)  │  │  │
│   │  └───────────────────┘  │         │  └───────────┬───────────────┘  │  │
│   │                         │         │              │                  │  │
│   │  ┌───────────────────┐  │         │              ▼                  │  │
│   │  │  State (Zustand)  │  │         │  ┌───────────────────────────┐  │  │
│   │  │  - Thread ID      │  │         │  │   Domain Stores           │  │  │
│   │  │  - Domain state   │  │         │  │   - Your data             │  │  │
│   │  │  - Theme prefs    │  │         │  │   - Thread-scoped state   │  │  │
│   │  └───────────────────┘  │         │  └───────────────────────────┘  │  │
│   │                         │         │                                 │  │
│   └─────────────────────────┘         └─────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Five-Minute Mental Model

**1. User sends message** → Frontend posts to `/chatkit` endpoint

**2. Server calls `respond()`** → Runs your agent with the conversation

**3. Agent reasons and calls tools** → Tools fetch data, update state, stream widgets

**4. Response streams back** → Text, widgets, and client tool calls

**5. Frontend renders everything** → ChatKit SDK handles the UI, your code handles custom updates

---

## Project Structure

Every ChatKit app follows this layout:

```
your-app/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app, /chatkit endpoint
│       ├── server.py            # ChatKitServer - the orchestrator
│       ├── agents/              # Your AI agents
│       │   └── my_agent.py      # Instructions + tools
│       ├── data/                # Domain stores
│       │   └── my_store.py      # Data access layer
│       ├── widgets/             # Widget builders
│       ├── memory_store.py      # Thread/message persistence
│       └── request_context.py   # Request-scoped context
├── frontend/
│   └── src/
│       ├── App.tsx              # Main app component
│       └── components/
│           └── ChatKitPanel.tsx # ChatKit integration
└── package.json                 # npm run your-app
```

---

## Building Blocks

### 1. The Agent

An agent is an LLM + instructions + tools:

```python
# backend/app/agents/my_agent.py

INSTRUCTIONS = """You are a helpful assistant for [your domain].

When users ask about X, use the get_data tool.
When they want to see details, use show_widget tool.
Always be friendly and concise."""

class MyAgentContext(AgentContext):
    """What the agent has access to"""
    store: Annotated[MemoryStore, Field(exclude=True)]
    data_store: Annotated[DataStore, Field(exclude=True)]
    thread: Thread

@function_tool(description_override="Fetches data matching the query")
async def get_data(ctx: RunContextWrapper[MyAgentContext], query: str) -> str:
    results = await ctx.context.data_store.search(query)
    return f"Found {len(results)} items: {results}"

@function_tool(description_override="Shows a widget with item details")
async def show_widget(ctx: RunContextWrapper[MyAgentContext], item_id: str):
    item = await ctx.context.data_store.get(item_id)
    widget = build_item_widget(item)
    await ctx.context.stream_widget(widget)
    return "Widget displayed"

my_agent = Agent[MyAgentContext](
    model="gpt-4.1-mini",
    name="My Agent",
    instructions=INSTRUCTIONS,
    tools=[get_data, show_widget],
)
```

### 2. The Server

The server orchestrates everything:

```python
# backend/app/server.py

class MyServer(ChatKitServer[RequestContext]):
    def __init__(self, store: MemoryStore, data_store: DataStore):
        super().__init__(store)
        self.data_store = data_store

    async def respond(self, thread, item, context) -> AsyncIterator[ThreadStreamEvent]:
        """Called when user sends a message"""

        # Build agent context
        agent_context = MyAgentContext(
            store=self.store,
            data_store=self.data_store,
            thread=thread,
        )

        # Run the agent
        async for event in Runner.run_streamed(
            my_agent,
            input=convert_thread_to_input(thread),
            context=agent_context,
        ):
            yield event

    async def action(self, thread, action, sender, context) -> AsyncIterator[ThreadStreamEvent]:
        """Called when user clicks a widget button"""

        if action.type == "item.select":
            item_id = action.payload["item_id"]
            # Handle the selection...
            yield ThreadItemCreatedEvent(item=response_item)
```

### 3. The Frontend

Connect ChatKit to your backend:

```typescript
// frontend/src/components/ChatKitPanel.tsx

export function ChatKitPanel() {
  const { threadId, setThreadId, stats, setStats } = useAppStore();

  const chatkit = useChatKit({
    api: {
      url: "/chatkit",
      domainKey: "my-app",
    },

    // Handle thread changes
    onThreadChange: ({ threadId }) => setThreadId(threadId),

    // Handle client tool calls from the agent
    onClientToolCall: (toolCall) => {
      if (toolCall.name === "update_stats") {
        setStats(toolCall.arguments);
      }
    },

    // Handle widget button clicks
    onWidgetAction: async (action, widget) => {
      if (action.type === "item.select") {
        await chatkit.sendCustomAction(action, widget.id);
      }
    },
  });

  return <ChatKit control={chatkit.control} />;
}
```

---

## Communication Patterns

There are four ways the agent and UI communicate:

### Pattern 1: Client Tool Calls (Agent → UI)

For real-time UI updates without user seeing a widget:

```python
# Backend: Agent tool
@function_tool
async def feed_cat(ctx: RunContextWrapper[CatAgentContext]):
    new_stats = ctx.context.cat_store.feed(ctx.context.thread.id)

    # Send update directly to frontend
    ctx.context.client_tool_call = ClientToolCall(
        name="update_cat_status",
        arguments={"hunger": new_stats.hunger, "happiness": new_stats.happiness}
    )
    return "Fed the cat!"
```

```typescript
// Frontend: Handle the update
onClientToolCall: (toolCall) => {
  if (toolCall.name === "update_cat_status") {
    setCatStats(toolCall.arguments);
  }
}
```

**Used in:** Cat Lounge (stat updates), Metro Map (add stations)

### Pattern 2: Widgets (Agent → UI)

For interactive content in the chat:

```python
# Backend: Build and stream widget
@function_tool
async def show_articles(ctx: RunContextWrapper[NewsAgentContext], topic: str):
    articles = await ctx.context.article_store.search(topic)

    widget = ListView(
        items=[
            ListItem(
                title=a.title,
                description=a.summary,
                action=Button(
                    label="Read",
                    onClickAction={"type": "open_article", "payload": {"id": a.id}}
                )
            )
            for a in articles
        ]
    )

    await ctx.context.stream_widget(widget)
    return f"Showing {len(articles)} articles"
```

**Used in:** News Guide (article lists), Cat Lounge (name suggestions)

### Pattern 3: Custom Actions (UI → Agent)

For handling widget interactions:

```typescript
// Frontend: Send action when widget button clicked
onWidgetAction: async (action, widget) => {
  if (action.type === "select_name") {
    // Server handles this
    await chatkit.sendCustomAction(action, widget.id);
  }
  if (action.type === "more_options") {
    // Just send a message
    await chatkit.sendUserMessage({ text: "Show me more options" });
  }
}
```

```python
# Backend: Handle in server.action()
async def action(self, thread, action, sender, context):
    if action.type == "select_name":
        name = action.payload["name"]
        self.cat_store.set_name(thread.id, name)
        yield ThreadItemCreatedEvent(item=TextItem(text=f"Named your cat {name}!"))
```

**Used in:** Cat Lounge (name selection), Metro Map (line selection)

### Pattern 4: Hidden Context (Persisting State)

For remembering state across conversation turns:

```python
# Add hidden context the agent can see but user can't
hidden_item = HiddenContextItem(
    content="<USER_PREFERENCE>dark_mode</USER_PREFERENCE>"
)
await store.add_thread_item(thread.id, hidden_item)

# Later, agent sees this in its context and can reference it
```

**Used in:** Cat Lounge (recent actions), Metro Map (selected line)

---

## Working with the Examples

### Cat Lounge: Game State

The simplest example - one agent managing per-thread game state.

**Key pattern: Client tool calls for stat synchronization**

```python
# Every mutation updates the UI
ctx.context.client_tool_call = ClientToolCall(
    name="update_cat_status",
    arguments=cat_state.model_dump()
)
```

### News Guide: Multi-Agent + Rich Retrieval

Complex example with 4 specialized agents and entity references.

**Key pattern: Agent routing via tool_choice**

```python
# Composer menu lets user pick which agent
tools=[
    {"type": "function", "name": "news_agent", "description": "General news"},
    {"type": "function", "name": "event_finder", "description": "Find events"},
]

# Server routes based on selection
if tool_choice == "event_finder":
    agent = event_finder_agent
```

### Metro Map: Canvas Integration

Chat-driven updates to a React Flow canvas.

**Key pattern: Early return after client tool**

```python
# If we just triggered a UI mode, don't continue inference
if ctx.context.client_tool_call and ctx.context.client_tool_call.name == "location_select_mode":
    return  # Let user interact with canvas first
```

### Customer Support: Transactional

Stateful booking operations with domain validation.

**Key pattern: Domain state manager**

```python
class AirlineStateManager:
    def change_seat(self, booking_id: str, new_seat: str) -> Result:
        booking = self.get_booking(booking_id)
        if not self.is_seat_available(new_seat):
            raise ValueError(f"Seat {new_seat} is not available")
        booking.seat = new_seat
        return Result(success=True, message=f"Changed to seat {new_seat}")
```

---

## Quick Start: Creating a New App

### 1. Copy the closest example

```bash
cp -r examples/cat-lounge apps/my-app
```

### 2. Update the agent

Edit `backend/app/agents/my_agent.py`:
- Write your `INSTRUCTIONS`
- Define your `AgentContext`
- Create your `@function_tool` functions

### 3. Create your data store

Edit `backend/app/data/my_store.py`:
- Define your data models
- Implement load/save/search methods

### 4. Wire it up in server.py

```python
class MyServer(ChatKitServer[RequestContext]):
    def __init__(self, store, my_store):
        super().__init__(store)
        self.my_store = my_store
```

### 5. Add to package.json

```json
"scripts": {
  "my-app": "concurrently \"npm run my-app:fe\" \"npm run my-app:be\"",
  "my-app:fe": "cd apps/my-app/frontend && npm run dev",
  "my-app:be": "cd apps/my-app/backend && uv run uvicorn app.main:app --port 8010"
}
```

### 6. Run it

```bash
export OPENAI_API_KEY=sk-...
npm run my-app
```

---

## Common Patterns Reference

### Widget Building

```python
from chatkit.widgets import Card, Text, Button, Row, ListView

# Simple card
widget = Card(children=[
    Text(value="Hello!", style="heading"),
    Text(value="Some content here"),
    Button(label="Click me", onClickAction={"type": "my_action"})
])

# List view
widget = ListView(items=[
    ListItem(title="Item 1", action=Button(label="Select", onClickAction={...})),
    ListItem(title="Item 2", action=Button(label="Select", onClickAction={...})),
])

await ctx.context.stream_widget(widget)
```

### Progress Updates

```python
@function_tool
async def search(ctx: RunContextWrapper[MyContext], query: str):
    await ctx.context.stream(ProgressUpdateEvent(text="Searching..."))
    results = await slow_search(query)
    await ctx.context.stream(ProgressUpdateEvent(text=""))  # Clear
    return results
```

### Thread Titles

```python
async def _maybe_update_title(self, thread, context):
    if not thread.title:
        result = await Runner.run(title_agent, input=thread_summary)
        thread.title = result.final_output
        await self.store.save_thread(thread, context)
```

### Request Context

```python
# backend/app/request_context.py
class RequestContext(BaseModel):
    request: Annotated[Request | None, Field(default=None, exclude=True)]
    page_id: str | None = None  # From headers

# backend/app/main.py
context = RequestContext(
    request=request,
    page_id=request.headers.get("x-page-id"),
)
```

---

## Debugging Tips

1. **Check the backend logs** - FastAPI logs show all requests and errors

2. **Use browser DevTools** - Network tab shows /chatkit requests/responses

3. **Add logging to tools** - `logging.info(f"Tool called with {param}")`

4. **Test agents standalone** - Run agent without server to debug prompts

5. **Check widget JSON** - Malformed widgets fail silently

---

## What's Next

- **Deep dive into examples**: Read the example-specific docs in `docs/examples/`
- **Widget customization**: See `docs/chatkit-customization.md`
- **Architecture details**: See `docs/architecture.md`
- **Communication patterns**: See `docs/ui-agent-interaction.md`
