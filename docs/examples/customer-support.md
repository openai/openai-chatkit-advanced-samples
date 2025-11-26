# Customer Support Example

## Overview

Customer Support is an airline concierge assistant system demonstrating a real-world multi-panel application where an AI agent helps customers manage their travel itinerary. It showcases context-aware assistance, live data updates, and reactive UI synchronization based on agent actions. The app combines task-driven agent interactions with detailed customer profile visualization.

**Domain**: OpenSkies Airline - elite flyer concierge support

## Frontend Architecture

### Two-Panel Layout

**Home Component** (`Home.tsx`): Responsive grid layout with two main panels:
- **Left (320-420px)**: Chat panel for concierge interaction
- **Right (1fr)**: Customer context panel showing live customer data

**Panel Synchronization**:
- When chat thread changes, customer context fetches updated profile
- After agent completes response, profile refreshes to reflect changes
- Timeline shows recent concierge actions (seat changes, bag additions, etc.)

### Customer Context Panel

The `CustomerContextPanel` component displays rich customer data in three states:

**1. Loading State**
- Shows "Fetching the latest itinerary and services…"
- Allows agent to work while UI prepares data

**2. Error State**
- Displays error message in rose/error styling
- Gracefully handles missing customer data

**3. Data State** (Full Profile)

**Header Section**:
- Customer name and tier status (e.g., "Aviator Platinum")
- Loyalty ID badge
- Email and phone contact info

**Upcoming Itinerary** (Flight Segments):
- Flight number, route (SFO → JFK)
- Date and departure/arrival times
- Current seat assignment
- Status badge (Scheduled / Cancelled)
- Hover effects for interactivity

**Quick Stats** (3-column grid):
- **Luggage icon**: Checked bags count
- **Utensils icon**: Meal preference (or "Not set")
- **Calendar icon**: Special assistance needs

**Recent Concierge Actions** (Timeline):
- Scrollable list of recent service actions
- Color-coded by type:
  - **Green (success)**: Seat change, bag added
  - **Amber (warning)**: Trip cancelled
  - **Default (info)**: Other actions
- Shows timestamp in friendly format

**Tier Benefits**:
- List of loyalty program benefits
- Example: "Complimentary upgrades when available"

### State Management

Zustand store (`useColorScheme`, `useCustomerContext`):
- **threadId**: Current chat thread
- **profile**: Customer data (refreshed after agent actions)
- **loading**: Profile loading state
- **error**: Fetch errors
- **scheme**: Dark/light theme

### Key Libraries

- **Lucide React**: Icons (Mail, Phone, Luggage, Utensils, Calendar)
- **Zustand**: State management
- **Tailwind CSS**: Responsive styling
- **ChatKit React SDK**: Agent communication

## Backend Architecture

### State Management: Per-Thread Customer Profile

Unlike cat-lounge (per-thread pet state) or news-guide (shared article library), customer-support maintains **per-thread airline customer state**.

**AirlineStateManager** (`airline_state.py`):
- Thread-safe in-memory storage keyed by thread ID
- Each thread gets a default customer profile ("Jordan Miles")
- Methods for modifying customer state

**CustomerProfile** dataclass:
- Name, loyalty tier, contact info
- Flight segments (list of flights)
- Bags checked, meal preference, special assistance
- Timeline of service actions

**FlightSegment** dataclass:
- Flight number, date, origin/destination
- Departure/arrival times, seat, status
- Methods: `cancel()`, `change_seat(new_seat)`

### Support Agent (`support_agent.py`)

**Role**: "Airline customer support agent for OpenSkies"

**Key Instructions**:
- Acknowledge customer loyalty status and recent travel
- When a task requires action, call the tool immediately (don't describe hypothetically)
- Ask for confirmation on destructive actions (cancellations, bag additions)
- Keep responses concise (2-3 sentences)
- Use information from customer context; don't invent details

**Tools**:
- `change_seat(flight_number, seat)`: Move passenger to new seat
- `cancel_trip()`: Cancel upcoming reservation and note refund
- `add_checked_bag()`: Add one checked bag to itinerary
- `meal_preference_list()`: Show meal options for selection
- `request_assistance(note)`: Record special assistance request

**Tool Validation**:
- Seat format: row number + letter (e.g., "12C")
- Flight must exist in customer's itinerary
- Returns updated profile info and confirmation messages
- All actions logged to timeline with timestamp and status

### Server Implementation (`main.py`)

**CustomerSupportServer** extends ChatKitServer:

**respond()** (agent inference):
1. Loads thread history (last 20 items)
2. Retrieves customer profile for this thread
3. **Prepends customer profile as context** to agent input:
   ```
   <CUSTOMER_PROFILE>
   Name: Jordan Miles (Aviator Platinum)
   Loyalty ID: APL-204981
   Contact: jordan.miles@example.com, +1 (415) 555-9214
   Upcoming Segments:
   - OA476 SFO->JFK on 2025-10-02 seat 14A (Scheduled)
   - OA477 JFK->SFO on 2025-10-10 seat 15C (Scheduled)
   Recent Service Timeline:
   * Itinerary imported from confirmation LL0EZ6.
   </CUSTOMER_PROFILE>
   ```
4. Runs agent with customer context + thread history
5. Streams agent response

**action()** (widget interactions):
- Handles meal preference widget selections
- Updates customer profile with selected meal
- Replaces widget with confirmation
- Adds hidden context item for tracking

**GET /support/customer**:
- Fetches current customer snapshot for UI refresh
- Takes optional `thread_id` parameter
- Returns full customer profile as JSON

**GET /support/health**:
- Simple health check

### Context Injection Pattern

This app demonstrates **prepending rich context to agent input**:

**Why**:
- Agent doesn't need to fetch customer data via tool call
- Full context available for every response
- Faster decision-making without tool overhead
- Profile is already loaded by server

**How**:
1. Server loads profile using `AirlineStateManager.get_profile(thread_id)`
2. Formats as `<CUSTOMER_PROFILE>` XML-style block
3. Creates `EasyInputMessageParam` with profile text
4. Prepends to agent input items: `[profile_item] + thread_items`
5. Agent has immediate access to latest customer data

**Trade-off**: Larger input context, but simpler agent logic

## Data Flow

```
User opens chat
        ↓
Frontend creates new thread
        ↓
Home component calls useCustomerContext(threadId)
        ↓
Fetches GET /support/customer?thread_id=...
        ↓
CustomerSupportServer.agent_state loads profile
        ↓
Creates default profile ("Jordan Miles")
        ↓
Frontend displays profile panel

---

User: "Can I change my seat on flight OA476 to 12C?"
        ↓
ChatKitPanel sends message
        ↓
Backend respond() method:
  1. Loads thread history
  2. Gets customer profile
  3. Prepends <CUSTOMER_PROFILE> block
  4. Runs agent with full context
        ↓
Agent sees profile includes OA476, seat 14A
        ↓
Agent calls change_seat("OA476", "12C")
        ↓
AirlineStateManager validates and updates:
  - Finds segment with flight OA476
  - Changes seat 14A → 12C
  - Logs to timeline: "Seat changed... from 14A to 12C"
        ↓
Tool returns confirmation message
        ↓
Agent responds: "Seat updated to 12C on flight OA476."
        ↓
ChatKit sends response to frontend
        ↓
Home.handleResponseCompleted() triggers refresh()
        ↓
useCustomerContext refetches /support/customer
        ↓
Frontend updates seat display and timeline
        ↓
UI shows new seat + green success message in timeline
```

## Key Patterns

### 1. Context Injection
Pre-load rich business context (customer profile) into agent input, avoiding tool overhead.

### 2. Per-Thread State
Each chat thread maintains independent customer state. Multiple threads = multiple customers.

### 3. Timeline Tracking
All agent actions (seat changes, cancellations, bag additions) are logged with:
- Timestamp
- Action description
- Severity level (success, warning, error)

### 4. Widget Actions
Meal preference widget → action handler → state update → widget refresh → confirmation message

### 5. UI Sync
Frontend explicitly refreshes customer profile after agent completes. No WebSocket push; polling via GET.

## Files Structure

```
examples/customer-support/
├── frontend/
│   ├── src/
│   │   ├── App.tsx                          # Theme router
│   │   ├── components/
│   │   │   ├── Home.tsx                     # Main layout (chat + context)
│   │   │   ├── ChatKitPanel.tsx             # Chat interface
│   │   │   ├── CustomerContextPanel.tsx     # Customer profile display
│   │   │   └── ThemeToggle.tsx
│   │   ├── hooks/
│   │   │   ├── useColorScheme.ts
│   │   │   └── useCustomerContext.ts        # Fetches customer profile
│   │   └── main.tsx
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── main.py                          # FastAPI + CustomerSupportServer
│   │   ├── support_agent.py                 # Agent with tools
│   │   ├── airline_state.py                 # Customer profile + state manager
│   │   ├── meal_preferences.py              # Meal widget builder
│   │   ├── memory_store.py                  # Thread/message persistence
│   │   ├── thread_item_converter.py         # Thread item formatting
│   │   └── title_agent.py                   # Title generation
│   └── pyproject.toml
└── package.json
```

## How to Run

```bash
export OPENAI_API_KEY=sk-...
npm run customer-support
# Frontend: http://localhost:5171
# Backend: http://127.0.0.1:8001
```

## Comparison with Other Examples

| Aspect | Metro Map | News Guide | Cat Lounge | Customer Support |
|--------|-----------|-----------|-----------|-----------------|
| **Type** | Diagram editor | Content library | Game state | Business process |
| **Visualization** | Reactflow graph | Article listing | Status meters | Customer profile |
| **State** | Map structure | Article metadata | Per-thread pet | **Per-thread customer** |
| **Agent Role** | Map designer | Content curator | Pet caretaker | **Concierge** |
| **Interaction** | Map manipulation | Article search | Care actions | Task-driven requests |
| **Context Passing** | Hidden items | Built-in tools | State sync | **Prepended context block** |
| **UI Refresh** | Real-time graph update | Navigation | ClientToolCall | **Post-response polling** |

**Customer Support's Unique Strength**:
- Real-world business domain (airline concierge)
- Complex customer state with multiple data types
- Action logging for audit trails
- Context-aware agent (customer profile always available)
- Multi-step workflows (e.g., select meal → update widget → refresh UI)

**Key Learning**: Shows how to structure a stateful business application where the agent performs concrete actions that update both backend state and frontend display.
