# Cozy Cat Lounge - Agentic Workflow

## Main Request/Response Flow

```mermaid
flowchart TB
    subgraph Frontend["Frontend (React + Zustand)"]
        UI[Chat UI]
        CatPanel[Cat Status Panel]
        Store[App Store]
        ChatKit[ChatKit SDK]
    end

    subgraph Backend["Backend (FastAPI)"]
        Server[CatAssistantServer]
        Agent[cat_agent<br/>GPT-4 Mini]
        CatStore[(CatStore)]
        MemStore[(MemoryStore)]
    end

    UI -->|"User message"| ChatKit
    ChatKit -->|"POST /chatkit"| Server
    Server -->|"Load thread items"| MemStore
    Server -->|"Run agent"| Agent
    Agent -->|"Tool calls"| Server
    Server -->|"Mutate state"| CatStore
    Server -->|"SSE Stream"| ChatKit
    ChatKit -->|"ClientToolCall"| Store
    Store -->|"State update"| CatPanel
    ChatKit -->|"Assistant message"| UI
```

## Agent Tool Architecture

```mermaid
flowchart LR
    subgraph Agent["cat_agent (GPT-4 Mini)"]
        Instructions[System Instructions:<br/>Cozy Cat Companion]
    end

    subgraph Tools["Available Tools"]
        get[get_cat_status<br/>📊 Read-only]
        feed[feed_cat<br/>🍽️ +3 energy, +1 happy]
        play[play_with_cat<br/>🎾 +2 happy, -1 energy]
        clean[clean_cat<br/>🛁 +3 clean, -1 happy?]
        name[set_cat_name<br/>✏️ Sets name + color]
        suggest[suggest_cat_names<br/>📝 Shows widget]
        profile[show_cat_profile<br/>🐱 Shows card]
        speak[speak_as_cat<br/>💬 Speech bubble]
    end

    Agent --> get
    Agent --> feed
    Agent --> play
    Agent --> clean
    Agent --> name
    Agent --> suggest
    Agent --> profile
    Agent --> speak
```

## State Mutation Flow (e.g., Feed Cat)

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant S as Server
    participant A as Agent
    participant CS as CatStore
    participant MS as MemoryStore

    U->>F: "Feed the cat"
    F->>S: POST /chatkit
    S->>MS: Load thread items
    S->>A: Run with context

    Note over A: Decides: call feed_cat

    A->>S: feed_cat(meal=None)
    S->>CS: mutate(state.feed())
    CS-->>S: Updated state
    S->>MS: Add HiddenContextItem<br/>"<FED_CAT>..."
    S-->>A: Tool result

    Note over A: StopAtTools prevents<br/>duplicate narration

    S->>F: ClientToolCall<br/>{name: "update_cat_status"}
    F->>F: Update Zustand store
    F->>F: Show flash message

    S->>F: Assistant message<br/>"Fluffy enjoyed the snack!"
    F->>U: Display response
```

## Widget Interaction Flow (Name Selection)

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant S as Server
    participant A as Agent
    participant CS as CatStore

    U->>F: "Name my cat"
    F->>S: POST /chatkit
    S->>A: Run agent

    Note over A: Calls suggest_cat_names

    A->>S: suggest_cat_names([...])
    S->>F: Stream ListView widget
    F->>U: Display name options

    U->>F: Click "Whiskers"
    F->>S: Action: cats.select_name
    S->>CS: mutate(state.rename("Whiskers"))

    Note over CS: Sets name + random color

    S->>MS: Add HiddenContextItem<br/>"<CAT_NAME_SELECTED>Whiskers"
    S->>S: Update thread.title
    S->>F: Updated widget + message
    F->>F: Trigger confetti 🎉
    F->>U: "Whiskers is a great name!"
```

## State Model

```mermaid
stateDiagram-v2
    [*] --> Unnamed: New thread

    state CatState {
        energy: 0-10
        happiness: 0-10
        cleanliness: 0-10
        name: string
        color_pattern: string?
    }

    Unnamed --> Named: set_cat_name

    state "Care Actions" as Care {
        [*] --> Feed: feed_cat
        Feed --> [*]: +3 energy<br/>+1 happiness<br/>-1 clean (50%)

        [*] --> Play: play_with_cat
        Play --> [*]: +2 happiness<br/>-1 energy<br/>-1 clean (50%)

        [*] --> Clean: clean_cat
        Clean --> [*]: +3 cleanliness<br/>-1 happiness (50%)
    }

    Named --> Care
    Unnamed --> Care
```

## Hidden Context Pattern

```mermaid
flowchart TB
    subgraph Turn1["Turn 1: User feeds cat"]
        U1[User: Feed the cat]
        T1[Tool: feed_cat]
        H1[Hidden: &lt;FED_CAT&gt;Fed Fluffy snacks&lt;/FED_CAT&gt;]
    end

    subgraph Turn2["Turn 2: User asks about cat"]
        U2[User: How is my cat?]
        Context[Agent sees:<br/>1. User message<br/>2. Hidden: FED_CAT<br/>3. New user message]
        Response[Agent: Fluffy is happy<br/>after that snack earlier!]
    end

    Turn1 --> Turn2
    H1 -.->|"Included in context"| Context
```

## ClientToolCall Mechanism

```mermaid
flowchart LR
    subgraph Backend
        Tool[Tool Function]
        CTX[AgentContext]
    end

    subgraph Protocol
        SSE[SSE Stream]
    end

    subgraph Frontend
        Handler[onClientTool]
        Store[Zustand Store]
        UI[React Components]
    end

    Tool -->|"ctx.client_tool_call ="| CTX
    CTX -->|"ClientToolCallEvent"| SSE
    SSE -->|"JSON payload"| Handler
    Handler -->|"update_cat_status"| Store
    Handler -->|"cat_say"| Store
    Store -->|"Re-render"| UI
```

## Complete Tool Reference

| Tool | Inputs | State Changes | UI Effect |
|------|--------|---------------|-----------|
| `get_cat_status` | none | none | none |
| `feed_cat` | meal? | energy+3, happy+1, clean-1? | Flash message |
| `play_with_cat` | activity? | happy+2, energy-1, clean-1? | Flash message |
| `clean_cat` | method? | clean+3, happy-1? | Flash message |
| `set_cat_name` | name | name, color_pattern | Confetti |
| `suggest_cat_names` | suggestions[] | none | ListView widget |
| `show_cat_profile` | age?, toy? | age | Card widget |
| `speak_as_cat` | line | none | Speech bubble |

## File Structure

```
examples/cat-lounge/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI + /chatkit endpoint
│       ├── server.py            # CatAssistantServer
│       ├── agents/
│       │   └── cat_agent.py     # Agent + all tools
│       ├── data/
│       │   └── cat_store.py     # CatState + CatStore
│       └── widgets/
│           └── cat_widgets.py   # Widget builders
└── frontend/
    └── src/
        ├── App.tsx
        ├── components/
        │   ├── ChatKitPanel.tsx
        │   └── CatStatusPanel.tsx
        └── store/
            └── useAppStore.ts   # Zustand state
```
