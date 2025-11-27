## Core Architecture Pattern

All ChatKit applications follow a consistent full-stack architecture:

```
Frontend (React + Vite)
├── UI Component (game display, map, article viewer)
├── ChatKit Panel (chat interface)
└── Zustand Store (shared state)

Backend (FastAPI + openai-agents)
├── ChatKitServer (orchestrates requests)
├── Agent (AI with tools)
├── Memory Store (conversation history)
└── Domain Store (game state, map data, articles)
```

**Key Principle**: The agent controls all domain logic via tools. The UI is a reactive view of that state.

---

## Communication Mechanisms

### 1. Client Tool Calls (Agent → UI)

**What**: Structured messages from agent to frontend that update UI state instantly.

**How it works**:
```python
# Backend: Agent tool emits client tool call
ctx.context.client_tool_call = ClientToolCall(
    name="update_cat_status",
    arguments={
        "state": cat_state.to_payload(),
        "flash": "Fed Whiskers a treat!"
    }
)
```

```typescript
// Frontend: ChatKit handler intercepts and updates state
const handleClientToolCall = (toolCall) => {
    if (toolCall.name === "update_cat_status") {
        applyCatUpdate(toolCall.params.state);
        setFlashMessage(toolCall.params.flash);
        return { success: true };
    }
};
```

**When to use**: Real-time UI updates (stat changes, notifications, state sync)

---

### 2. Widgets (Agent → UI)

**What**: Rendered HTML/JSON components that display in the chat with interactive elements.

**How it works**:
```python
# Backend: Agent streams widget
widget = build_article_list_widget(articles)
ctx.context.stream_widget(widget)
```

```typescript
// Frontend: ChatKit automatically renders widget
// Widgets can have onClickAction handlers
{
    type: "open_article",
    payload: { id: "article-123" }
}
```

**When to use**: Displaying lists, forms, selections, or rich content in chat

---

### 3. Custom Actions (UI → Agent)

**What**: User interactions on widgets or UI components that trigger backend handlers.

**How it works**:
```typescript
// Frontend: Send custom action
chatkit.sendCustomAction({
    type: "cats.select_name",
    payload: { name: "Whiskers" }
})
```

```python
# Backend: server.action() handles it
async def action(self, thread, action, sender, context):
    if action.type == "cats.select_name":
        await self._handle_select_name_action(...)
```

**When to use**: Widget button clicks, form submissions, interactive selections

---

### 4. Request Context Headers (UI → Agent)

**What**: HTTP headers that pass current UI context to backend.

**How it works**:
```typescript
// Frontend: Add context header to all requests
headers.set("article-id", currentArticleId ?? "featured");
```

```python
# Backend: Agent accesses via request context
article_id = ctx.context.request_context.article_id
current_article = await store.load(article_id)
```

**When to use**: Enabling "this article", "current page" references without explicit user mention

---

## Example 1: Cat-Lounge (Game State Management)

### Architecture Overview

**Frontend Components**:
- `CatStatusPanel` - Displays cat image, stats bars (energy, happiness, cleanliness), quick action buttons
- `ChatKitPanel` - Chat interface with agent
- Zustand store - Holds `CatStatePayload` with name, stats, age, colorPattern

**Backend**:
- `CatAgent` - 7 tools (feed, play, clean, set_name, suggest_names, show_profile, speak_as_cat)
- `CatStore` - Per-thread cat state (in-memory)
- `MemoryStore` - Conversation history

### Interaction Flow: Feeding the Cat

```
1. User clicks "Give snack" button
   ↓
2. CatStatusPanel calls onQuickAction("Please give Whiskers a crunchy fish treat")
   ↓
3. chatkit.sendUserMessage() → Backend receives message
   ↓
4. Agent decides to call feed_cat("crunchy fish treat") tool
   ↓
5. Tool mutates server state:
   - state.energy = min(10, state.energy + 3)
   - state.happiness = min(10, state.happiness + 1)
   ↓
6. Tool emits ClientToolCall:
   {
     name: "update_cat_status",
     arguments: {
       state: {energy: 9, happiness: 8, ...},
       flash: "Fed Whiskers a crunchy fish treat"
     }
   }
   ↓
7. ChatKitPanel.handleClientToolCall() receives it
   ↓
8. Zustand store.applyCatUpdate() merges new state
   ↓
9. CatStatusPanel re-renders with updated bars
   ↓
10. Flash message appears: "Fed Whiskers a crunchy fish treat"
```

### Code Examples

**Frontend: Client Tool Handler**
```typescript
// ChatKitPanel.tsx
const handleClientToolCall = useCallback((toolCall: {
    name: string;
    params: Record<string, unknown>;
}) => {
    if (toolCall.name === "update_cat_status") {
        const data = toolCall.params.state as CatStatePayload | undefined;
        if (data) {
            handleStatusUpdate(data, toolCall.params.flash as string | undefined);
        }
        return { success: true };
    }
    if (toolCall.name === "cat_say") {
        const message = String(toolCall.params.message ?? "");
        setSpeech({message, mood: toolCall.params.mood as string | undefined});
        return { success: true };
    }
    return { success: false };
}, []);
```

**Backend: Agent Tool**
```python
# cat_agent.py
@function_tool
async def feed_cat(ctx: RunContextWrapper[CatAgentContext], meal: str) -> str:
    thread_id = ctx.context.request_context.thread_id

    # Mutate state
    state = await _update_state(ctx, lambda s: s.feed())

    # Sync to frontend
    flash = f"Fed {state.name} {meal}"
    await _sync_status(ctx, state, flash)

    # Add hidden context for agent memory
    await _add_hidden_context(ctx, f"<FED_CAT>{flash}</FED_CAT>")

    return f"Successfully fed {state.name}"

async def _sync_status(ctx, state, flash):
    ctx.context.client_tool_call = ClientToolCall(
        name="update_cat_status",
        arguments={
            "state": state.to_payload(thread_id),
            "flash": flash
        }
    )
```

### Widget Interaction: Name Selection

```
1. Agent calls suggest_cat_names(["Whiskers", "Mittens", "Shadow"])
   ↓
2. Widget renders with 3 name cards + "Select" buttons
   ↓
3. User clicks "Select" on "Whiskers"
   ↓
4. Widget onClickAction → chatkit.sendCustomAction({
     type: "cats.select_name",
     payload: { name: "Whiskers" }
   })
   ↓
5. Backend server.action() receives it
   ↓
6. Updates cat state, thread title, emits update_cat_status
   ↓
7. Frontend refreshCat() fetches new state
   ↓
8. CatStatusPanel shows name + confetti animation
```

**Widget Definition** (`name_suggest.widget`):
```json
{
  "type": "ListView",
  "items": [
    {
      "title": "Whiskers",
      "actions": [{
        "label": "Select",
        "onClickAction": {
          "type": "cats.select_name",
          "payload": {"name": "Whiskers"}
        }
      }]
    }
  ]
}
```

---

## Example 2: Metro-Map (Visualization State)

### Architecture Overview

**Frontend Components**:
- `MetroMapCanvas` - ReactFlow visualization (nodes = stations, edges = lines)
- `MapPanel` - Container with "Add station" modal
- `ChatKitPanel` - Chat interface
- Zustand stores: `useMapStore` (map data, reactFlow instance), `useAppStore` (theme, threadId)

**Backend**:
- `MetroMapAgent` - Tools for get_map, add_station, plan_route, show_line_selector
- `MetroMapStore` - In-memory metro map data structure

### Interaction Flow: Adding a Station

```
1. User clicks "Add station" button in MapPanel
   ↓
2. Modal shows: station name input + line selector
   ↓
3. User enters "Union Square", selects Red Line
   ↓
4. Frontend calls updateMetroMap() API (optimistic update)
   ↓
5. chatkit.sendUserMessage("Add Union Square station to Red Line")
   ↓
6. Agent receives, calls show_line_selector() tool
   ↓
7. Widget renders with line options
   ↓
8. User clicks Red Line
   ↓
9. Widget action → server.action() receives "line.select"
   ↓
10. Backend emits location_select_mode ClientToolCall
   ↓
11. Frontend sets locationSelectLineId = "red"
   ↓
12. Map shows directional arrows on Red Line endpoints
   ↓
13. User clicks endpoint station
   ↓
14. chatkit.sendUserMessage("Add after Downtown")
   ↓
15. Agent calls add_station() tool
   ↓
16. Tool emits add_station ClientToolCall with full map data
   ↓
17. Frontend updates map state, ReactFlow re-renders
   ↓
18. Camera animates to new station
```

### Code Examples

**Frontend: Map Update Handler**
```typescript
// ChatKitPanel.tsx
const handleClientTool = useCallback((toolCall) => {
    if (toolCall.name === "add_station") {
        const stationId = toolCall.params.stationId;
        const nextMap = toolCall.params.map;

        setMap(nextMap);  // Updates useMapStore
        focusStation(stationId, nextMap);  // Animate camera

        return { success: true };
    }

    if (toolCall.name === "location_select_mode") {
        setLocationSelectLineId(toolCall.params.lineId);
        return { success: true };
    }
}, []);
```

**Frontend: Map Visualization**
```typescript
// MetroMapCanvas.tsx
const graph = useMemo(() => {
    if (!map) return { nodes: [], edges: [] };
    return buildGraph(map, selectedStationId);
}, [map, selectedStationId]);

return (
    <ReactFlow
        nodes={graph.nodes}
        edges={graph.edges}
        onNodeClick={(e, node) => {
            onSelectStation(node.id);
            chatkit.sendUserMessage(`Tell me about ${node.data.label}`);
        }}
    />
);
```

**Backend: Add Station Tool**
```python
# metro_map_agent.py
@function_tool
async def add_station(
    ctx: RunContextWrapper[MetroAgentContext],
    station_name: str,
    line_id: str,
    position: str
) -> MapResult:
    # Mutate map
    updated_map, new_station = ctx.context.metro.add_station(
        station_name, line_id, position
    )

    # Emit client tool call with FULL map data
    ctx.context.client_tool_call = ClientToolCall(
        name="add_station",
        arguments={
            "stationId": new_station.id,
            "map": updated_map.model_dump(mode="json")
        }
    )

    return MapResult(map=updated_map)
```

### Station Click Interaction

```
User clicks station in map
  ↓
MetroMapCanvas.onNodeClick() fires
  ↓
onSelectStation(stationId) → Updates selectedStationId in store
  ↓
chatkit.sendUserMessage("Tell me about Downtown Station")
  ↓
Agent receives, calls get_map() to load context
  ↓
Agent responds with station info
```

---

## Example 3: News-Guide (Content Navigation)

### Architecture Overview

**Frontend Components**:
- `NewsroomPanel` - Article display (landing grid + detail view)
- `ChatKitPanel` - Chat interface with entity search
- React Router - `/` (landing) and `/article/:articleId` (detail)
- Zustand store - `articleId` synced with URL

**Backend**:
- `NewsAgent` - Tools for search, get_article, show_article_list_widget
- `ArticleStore` - Article data (markdown content, metadata, tags)

### Interaction Flow: Article Search and View

```
1. User types "Show me articles about urban parks"
   ↓
2. chatkit.sendUserMessage() → Backend receives
   ↓
3. Agent calls search_articles_by_keywords(["urban", "parks"])
   ↓
4. Tool returns matching ArticleMetadata[]
   ↓
5. Agent calls show_article_list_widget(articles, "Here are articles about urban parks")
   ↓
6. Widget streams to frontend with ListView of article cards
   ↓
7. Each card has "View" button with action:
   {
     type: "open_article",
     payload: { id: "article-123" }
   }
   ↓
8. User clicks "View"
   ↓
9. handleWidgetAction() in ChatKitPanel fires
   ↓
10. navigate(`/article/${id}`) → URL changes
   ↓
11. NewsroomPanel detects route param change
   ↓
12. Fetches full article via fetchArticle(id)
   ↓
13. Renders ArticleDetail with markdown content
   ↓
14. Simultaneously, widget action sent to backend
   ↓
15. server.action() handles "open_article"
   ↓
16. Streams follow-up message: "Want a quick summary of this article?"
```

### Code Examples

**Frontend: Article Navigation**
```typescript
// NewsroomPanel.tsx
const { articleId } = useParams();

useEffect(() => {
    if (articleId) {
        fetchArticle(articleId).then(setArticle);
        setArticleId(articleId);  // Sync to Zustand
    }
}, [articleId]);

// ArticleDetail renders markdown + tags
return (
    <div>
        <h1>{article.title}</h1>
        <ReactMarkdown>{article.content}</ReactMarkdown>
        <div className="tags">
            {article.tags.map(tag => <Tag key={tag}>{tag}</Tag>)}
        </div>
    </div>
);
```

**Frontend: Request Context Header**
```typescript
// ChatKitPanel.tsx - Custom fetch wrapper
const customFetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const headers = new Headers(init?.headers);

    // Pass current article context to backend
    headers.set("article-id", currentArticleId ?? "featured");

    return fetch(input, { ...init, headers });
};
```

**Frontend: Widget Action Handler**
```typescript
// ChatKitPanel.tsx
const handleWidgetAction = useCallback((action: ChatKitAction) => {
    if (action.type === "open_article") {
        const articleId = action.payload.id;
        navigate(`/article/${articleId}`);

        // Notify backend
        chatkit.sendCustomAction(action);
    }
}, [chatkit, navigate]);
```

**Backend: Article List Widget Tool**
```python
# news_agent.py
@function_tool
async def show_article_list_widget(
    ctx: RunContextWrapper[NewsAgentContext],
    articles: List[ArticleMetadata],
    message: str
) -> str:
    # Stream explanation message
    ctx.context.stream_message(
        AssistantMessageItem(content=[TextPart(text=message)])
    )

    # Build widget
    widget = build_article_list_widget(articles)
    ctx.context.stream_widget(widget)

    return f"Displayed {len(articles)} articles"
```

**Backend: Widget Definition**
```python
# article_list_widget.py
def build_article_list_widget(articles: List[ArticleMetadata]) -> WidgetComponent:
    items = []
    for article in articles:
        items.append(ListViewItem(
            title=article.title,
            subtitle=f"By {article.author} · {article.date}",
            hero=ImageComponent(src=article.image_url, width=160, height=200),
            actions=[ButtonComponent(
                label="View",
                onClickAction=Action(
                    type="open_article",
                    payload={"id": article.id}
                )
            )]
        ))

    return ListView(items=items)
```

**Backend: Custom Action Handler**
```python
# server.py
async def action(self, thread, action, sender, context):
    if action.type == "open_article":
        article_id = action.payload.get("id")
        article = await self.article_store.load(article_id)

        # Stream follow-up message
        message = AssistantMessageItem(
            content=[TextPart(
                text=f"Want a quick summary of _{article.title}_ or questions about it?"
            )]
        )
        yield ThreadItemCreatedEvent(item=message)
        yield ThreadItemDoneEvent(item=message)
```

### Request Context: "This Article" References

```
User viewing article "Parks Revival Initiative"
  ↓
All ChatKit requests include header: article-id: article-789
  ↓
User types "Summarize this article"
  ↓
Backend receives request, sets RequestContext.article_id = "article-789"
  ↓
Agent calls get_current_page() tool
  ↓
Tool reads ctx.context.request_context.article_id
  ↓
Loads article from store
  ↓
Returns full article content to agent
  ↓
Agent summarizes
```

**Backend Implementation**:
```python
# news_agent.py
@function_tool
async def get_current_page(
    ctx: RunContextWrapper[NewsAgentContext]
) -> CurrentPageResult:
    article_id = ctx.context.request_context.article_id

    if not article_id or article_id == "featured":
        return CurrentPageResult(
            is_article=False,
            message="User is on landing page"
        )

    article = await ctx.context.articles.load(article_id)
    return CurrentPageResult(
        is_article=True,
        article=article,
        content=article.content  # Full markdown
    )
```

---

## Key Patterns Summary

### 1. State Synchronization Pattern

**Use case**: Game stats, map data, real-time updates

**Implementation**:
- Backend tool mutates domain store
- Tool emits `ClientToolCall` with updated state
- Frontend handler updates local store (Zustand/Jotai)
- UI components re-render reactively

**Example**: Cat feeding (cat-lounge), map updates (metro-map)

---

### 2. Widget Display Pattern

**Use case**: Lists, selections, forms, rich content

**Implementation**:
- Backend tool builds widget (ListView, Form, etc.)
- Tool calls `ctx.context.stream_widget(widget)`
- Widget renders in chat with interactive elements
- Button clicks trigger custom actions → backend handlers

**Example**: Article lists (news-guide), name selection (cat-lounge), line picker (metro-map)

---

### 3. Navigation Sync Pattern

**Use case**: Article views, page navigation, deep linking

**Implementation**:
- Frontend routes (React Router)
- Widget actions trigger navigation + backend notification
- Backend action handler streams follow-up content
- Request headers pass current context to agent

**Example**: Article navigation (news-guide)

---

### 4. Quick Action Pattern

**Use case**: One-click shortcuts for common tasks

**Implementation**:
- UI button triggers `chatkit.sendUserMessage(prompt)`
- Agent receives as natural language
- Agent calls appropriate tool
- State updates via ClientToolCall

**Example**: "Give snack", "Play", "Freshen up" buttons (cat-lounge)

---

### 5. Hidden Context Pattern

**Use case**: Agent memory across conversation turns

**Implementation**:
- Tool adds `HiddenContextItem` to thread after mutations
- Uses XML tags like `<FED_CAT>...</FED_CAT>`
- Agent can reference in future responses without re-querying
- Not visible to user, only to agent

**Example**: Remembering fed/played actions (cat-lounge), selected line (metro-map)

```python
await _add_hidden_context(ctx, f"<FED_CAT>Fed {state.name} a treat</FED_CAT>")
```

---

## Architecture Decision Guide

### When to use Client Tool Calls vs Widgets

**Client Tool Calls** when:
- Updating existing UI state (stats, maps, counters)
- Triggering animations or effects
- Syncing backend mutations to frontend
- No user interaction needed

**Widgets** when:
- Displaying new content (lists, cards)
- User needs to select from options
- Showing rich formatted content
- Creating interactive forms

### When to use Custom Actions vs User Messages

**Custom Actions** when:
- Widget button clicks
- Programmatic interactions
- Need to pass structured data
- Backend needs to differentiate from natural language

**User Messages** when:
- User typing in chat
- Quick action buttons (natural language prompts)
- Conversational interactions
- Agent should interpret intent

### State Management Approaches

**Frontend State (Zustand/Jotai)**:
- UI preferences (theme, layout)
- Current view context (articleId, threadId)
- Transient UI (speech bubbles, flash messages)

**Backend Domain Store**:
- Authoritative game/app state
- Persisted data
- Multi-user shared state

**Sync via Client Tool Calls** for reactive updates without polling.

---

## Common Pitfalls

### 1. Forgetting Request Context
**Problem**: Agent can't reference "this article" or "current page"
**Solution**: Pass context via headers, use request_context in tools

### 2. Polling for State Updates
**Problem**: Inefficient, delayed updates
**Solution**: Use ClientToolCall for push-based updates

### 3. Frontend Logic Duplication
**Problem**: Game logic in both frontend and backend
**Solution**: Backend tools own all mutations, frontend is view-only

### 4. Missing Hidden Context
**Problem**: Agent repeats actions or forgets what happened
**Solution**: Add HiddenContextItem after each mutation with semantic tags

### 5. Widget Action Not Handled
**Problem**: Button clicks do nothing
**Solution**: Implement server.action() handler for custom action types

---

## Testing Interaction Flows

### Frontend Testing
```typescript
// Test client tool call handler
const mockToolCall = {
    name: "update_cat_status",
    params: { state: { energy: 10 }, flash: "Fed!" }
};

const result = handleClientToolCall(mockToolCall);
expect(result.success).toBe(true);
expect(store.getState().cat.energy).toBe(10);
```

### Backend Testing
```python
# Test tool emits correct client tool call
context = CatAgentContext(...)
await feed_cat(context, "treat")

assert context.client_tool_call.name == "update_cat_status"
assert context.client_tool_call.arguments["flash"] == "Fed Whiskers a treat"
```

---

## References

### File Locations

**Cat-Lounge**:
- Frontend: `examples/cat-lounge/frontend/src/`
- Backend: `examples/cat-lounge/backend/app/`
- Agent: `backend/app/agents/cat_agent.py`

**Metro-Map**:
- Frontend: `examples/metro-map/frontend/src/`
- Backend: `examples/metro-map/backend/app/`
- Agent: `backend/app/agents/metro_map_agent.py`

**News-Guide**:
- Frontend: `examples/news-guide/frontend/src/`
- Backend: `examples/news-guide/backend/app/`
- Agent: `backend/app/agents/news_agent.py`

### Key Classes & Types

- `ClientToolCall` - openai-agents SDK class for agent→UI messages
- `WidgetComponent` - Base class for chat widgets
- `ChatKitServer` - Base server class, implement `respond()` and `action()`
- `Agent[T]` - Generic agent with typed context
- `RunContextWrapper[T]` - Tool execution context with domain context access
- `@function_tool` - Decorator for agent tool definitions

---

## Summary

The ChatKit architecture creates a clean separation between:
1. **UI (Frontend)** - Reactive view layer
2. **Agent (Backend)** - Business logic and AI
3. **Stores (Backend)** - Authoritative state

Communication flows bidirectionally:
- **UI → Agent**: User messages, widget actions, request headers
- **Agent → UI**: Client tool calls, widgets, streamed messages

This enables natural, conversational interfaces where the AI agent orchestrates complex application state while the UI remains simple and responsive.
