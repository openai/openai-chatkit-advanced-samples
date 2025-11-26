# Cat Lounge Example

## Overview

Cat Lounge is a virtual pet care simulator where users interact with an AI agent ("Cozy Cat Companion") to care for a unique procedurally-generated cat. It demonstrates how ChatKit agents can manage stateful interactions, trigger client-side updates, and coordinate between backend game logic and frontend visualization.

The cat's color pattern is hidden until the user names it—rewarding engagement with a discovery mechanic.

## Frontend Architecture

### Two-Panel Layout

**App.tsx** presents a split-screen design:
- **Left (45%)**: Chat panel with agent responses
- **Right (45%)**: Cat status panel with visualization and quick actions
- **Header**: Title and description

### Cat Status Panel

The `CatStatusPanel` component (`CatStatusPanel.tsx`) is the main UI for interacting with the cat:

**Visual Components:**

1. **Cat Name** (h2, 3xl)
   - Large centered name (e.g., "Whiskers", "Unnamed Cat")

2. **Cat Image** (SVG/PNG illustrations)
   - Displays based on color pattern (black, calico, colorpoint, tabby, white)
   - Falls back to "who's that cat?" if unnamed
   - 48×48 size with drop shadow

3. **Speech Bubble** (optional, animated)
   - Shows fleeting messages when agent calls `speak_as_cat`
   - Auto-animates with fade-in effect
   - Example: "meow (I'm sleepy!)"

4. **Flash Message** (optional, orange notification)
   - Shows action outcomes ("Fed!") with 1-second animation

5. **Status Meters** (3 bars, 0-10 scale)
   - **Energy**: Green/yellow/orange/red based on value
   - **Happiness**: Same color scheme
   - **Cleanliness**: Same color scheme
   - Each shows current value / 10

6. **Quick Actions** (3 buttons)
   - **Give snack**: Increases happiness + energy
   - **Play with toy**: Burns energy, increases happiness
   - **Freshen up**: Improves cleanliness
   - Each button sends a pre-formatted prompt to the agent

### State Management

Uses Zustand store (`useAppStore`) to track:
- `cat`: Current cat state (name, energy, happiness, cleanliness, age, colorPattern)
- `speech`: Agent speech bubbles from `speak_as_cat` tool
- `flashMessage`: Quick action feedback
- `scheme`: Dark/light theme

### Key Libraries

- **Zustand**: Client state management
- **Tailwind CSS**: Responsive layout and styling
- **Lucide React**: Icons (if used)
- **ChatKit React SDK**: Agent communication

## Backend Architecture

### Stateful Pet Simulation

Unlike news-guide (content-driven) or metro-map (structural), Cat Lounge is **game-state-driven**:
- Each thread (user session) has a unique cat instance
- Cat state persists across messages
- State changes based on actions (feed, play, clean)
- State changes have random elements to keep gameplay interesting

### Cat State Model (`cat_state.py`)

```python
@dataclass
class CatState:
    name: str = "Unnamed Cat"
    energy: int = 6
    happiness: int = 6
    cleanliness: int = 6
    age: int = 2
    color_pattern: str | None = None
    updated_at: datetime
```

**State Transitions:**

- **feed()**: energy +3, happiness +1, random cleanliness -1
- **play()**: happiness +2, energy -1, random cleanliness -1
- **clean()**: cleanliness +3, random happiness -1
- **rename()**: Sets name, randomly assigns color pattern (once)

All values are clamped between 0-10. Randomness allows all three stats to reach 10/10/10.

### Cat Store (`cat_store.py`)

**Thread-safe in-memory storage:**
- Each thread gets its own `CatState` instance
- `load(thread_id)`: Retrieve a clone of current cat state
- `mutate(thread_id, mutator_fn)`: Atomically update cat state using a callback

Uses `asyncio.Lock()` for thread safety.

### Cat Agent (`cat_agent.py`)

**Role**: "Cozy Cat Companion" — playful caretaker

**Key Instructions**:
- Keep interactions light, imaginative, focused on cat wellbeing
- Always sync stats with tools before planning (`get_cat_status`)
- Color pattern stays hidden until cat is named

**Tools**:
- `get_cat_status`: Fetch current cat state
- `feed_cat`: Call when user asks to feed; describe food used
- `play_with_cat`: Call when user asks to play; describe toys used
- `clean_cat`: Call when user asks to clean; describe method used
- `set_cat_name`: Officially name the cat (once only)
- `suggest_cat_names`: Provide 3-4 name suggestions with reasoning
- `show_cat_profile`: Display profile card widget (after naming)
- `speak_as_cat`: Have cat respond directly (triggers speech bubble)

**Tool Validation**:
- Don't fire multiple tool calls for same action unless user explicitly asks
- Prompt unnamed cats to choose a name
- Suggest names if user wants to name but doesn't specify
- Reveal color pattern on naming
- Never rename after first naming

### Agent-Frontend Sync

The agent communicates state changes to the frontend via **ClientToolCall**:

```python
ctx.context.client_tool_call = ClientToolCall(
    name="update_cat_status",
    arguments={
        "state": state.to_payload(thread_id),
        "flash": "Flash message text"
    }
)
```

This tells the frontend:
1. Update cat state display
2. Show optional flash message (action confirmation)

### Widget System

#### Name Suggestions Widget
- Shows 3-4 suggested names
- User clicks a button to select one
- Triggers `select_name` action
- Sets cat name and reveals color pattern

#### Profile Card Widget
- Shows cat's profile (name, age, favorite toy)
- Displays in formatted card style

#### Speech Bubble
- Not a traditional widget, but a `ClientToolCall` message
- Triggers animated speech bubble on cat image
- Example: "meow (I'm hungry!)"

## Data Flow

```
User lands on cat-lounge
        ↓
Backend creates new CatState for this thread
        ↓
Frontend displays "Unnamed Cat" with unknown image
        ↓
User types message: "Hi, let's play"
        ↓
Agent receives message
        ↓
Agent calls play_with_cat tool
        ↓
Backend updates cat state:
  - happiness +2
  - energy -1
  - (random) cleanliness -1
        ↓
Agent sends ClientToolCall update_cat_status
        ↓
Frontend updates CatStatusPanel display
        ↓
Agent may call speak_as_cat
        ↓
Frontend shows speech bubble: "purr (that was fun!)"

---

User clicks "Give snack" button
        ↓
CatStatusPanel.onQuickAction called
        ↓
Sends pre-formatted prompt: "Please give Whiskers a fish treat"
        ↓
ChatKit sends to agent
        ↓
Agent calls feed_cat tool
        ↓
Backend: energy +3, happiness +1, (random) cleanliness -1
        ↓
Agent sends ClientToolCall with flash message "Nom nom!"
        ↓
Frontend shows flash message, updates meters

---

User wants to name cat (still "Unnamed Cat")
        ↓
User types: "Let's name it Whiskers"
        ↓
Agent detects naming intent
        ↓
Agent calls suggest_cat_names (or directly set_cat_name)
        ↓
If suggesting, shows widget with options
        ↓
User clicks a name
        ↓
Action triggers select_name with chosen name
        ↓
Backend calls cat.rename("Whiskers")
        ↓
Backend randomly assigns color_pattern
        ↓
ClientToolCall updates frontend
        ↓
Cat image changes to reveal pattern (e.g., "calico" cat image)
        ↓
Agent offers to show profile card
```

## Key Mechanisms

### Procedural Color Pattern

When a cat is named, a random color pattern is assigned:
```python
self.color_pattern = choice(["black", "calico", "colorpoint", "tabby", "white"])
```

This creates discovery: users name the cat to find out what it looks like.

### Stat Balancing Challenge

Each action has trade-offs:
- **Feed**: boosts energy but might reduce cleanliness
- **Play**: boosts happiness but drains energy
- **Clean**: boosts cleanliness but might reduce happiness

Randomness prevents any single action from maxing all stats, encouraging varied gameplay.

### Quick Actions

Pre-formatted buttons allow users to interact without typing:
- Generate templated prompts with cat name
- Send to agent via `onQuickAction` callback
- Similar to slash commands in chat apps

## Files Structure

```
examples/cat-lounge/
├── frontend/
│   ├── src/
│   │   ├── App.tsx                      # Main layout (chat + cat panel)
│   │   ├── components/
│   │   │   ├── CatStatusPanel.tsx       # Cat visualization + status meters + quick actions
│   │   │   ├── ChatKitPanel.tsx         # Chat interface
│   │   │   └── ThemeToggle.tsx
│   │   ├── store/
│   │   │   └── useAppStore.ts           # Cat state, speech, flash message
│   │   ├── lib/
│   │   │   └── cat.ts                   # Type definitions
│   │   └── assets/
│   │       ├── black-cat.png
│   │       ├── calico-cat.png
│   │       ├── rag-doll-cat.png
│   │       ├── maine-coon-cat.png
│   │       ├── white-cat.png
│   │       └── whos-that-cat.png
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI entrypoint
│   │   ├── server.py                    # ChatKitServer implementation
│   │   ├── cat_agent.py                 # Agent definition with tools
│   │   ├── cat_state.py                 # State model
│   │   ├── cat_store.py                 # Thread-safe state storage
│   │   ├── memory_store.py              # Thread/message persistence
│   │   ├── name_suggestions_widget.py   # Name widget builder
│   │   ├── profile_card_widget.py       # Profile widget builder
│   │   └── thread_item_converter.py
│   └── pyproject.toml
└── package.json
```

## How to Run

```bash
export OPENAI_API_KEY=sk-...
npm run cat-lounge
# Frontend: http://localhost:5170
# Backend: http://127.0.0.1:8000
```

## Unique Aspects

| Aspect | Metro Map | News Guide | Cat Lounge |
|--------|-----------|-----------|-----------|
| **Type** | Diagram editor | Content library | Game state |
| **Visualization** | Reactflow graph | Article landing + detail | Status meters + cat avatar |
| **State** | Map structure | Article metadata | Per-thread pet stats |
| **Agent Role** | Map expert | Content curator | Pet caretaker |
| **Interaction** | Direct map edits | Article search | Actions + chat |
| **Persistence** | Map persists across threads | Read-only articles | Cat state per thread |
| **Gamification** | None | None | **Stat tracking + color discovery** |

**Cat Lounge stands out** for combining:
- Stateful game mechanics (stats change based on actions)
- Client-side updates via `ClientToolCall`
- Discovery mechanics (hidden color pattern)
- Light, playful tone and narration
