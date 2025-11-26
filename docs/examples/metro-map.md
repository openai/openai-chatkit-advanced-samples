# Metro Map Example

## Overview

Metro Map is an interactive subway/metro system designer where users collaborate with an AI agent to build, modify, and explore fictional metro networks. It demonstrates how to integrate interactive visualizations with ChatKit agents for real-time map manipulation.

## Frontend Architecture

### Visualization: Reactflow

The app uses **[Reactflow](https://reactflow.dev/)** (`^11.11.3`), a React library specialized for rendering node-and-edge diagrams. It's perfect for graph-based visualizations like subway maps.

**How it works:**
- **Nodes** represent metro stations (circular colored dots with names)
- **Edges** represent metro lines connecting adjacent stations
- Stations can be interactive (clickable, selectable)
- The canvas supports panning, zooming, and grid snapping

### Custom Station Nodes

The `StationNode` component (`MetroMapCanvas.tsx:156`) defines the visual appearance of each station:

**Features:**
- Colored circle (primary color of the line)
- Multiple colored dots for interchange/exchange stations
- Rotated station names positioned below
- 8 hidden "handles" (connection points on all sides) for flexible edge routing
- Location selection arrows that appear during line extension mode

**Location Selection**:
- When a user wants to add a new station to a metro line, directional arrows appear at line endpoints
- Users click arrows to confirm where to place the station (beginning or end)
- This triggers a message to the agent: `"I would like to add the station to the [beginning/end] of the [Line] line."`

### Graph Construction

The map data is converted to Reactflow format:
- **buildNodes()**: Maps stations to positioned nodes (coordinates × scale factors)
- **buildEdges()**: Connects adjacent stations on each line with colored strokes
- Edge colors match the metro line color
- Edges automatically connect to the nearest side of each station node

### Key Components

- **MetroMapCanvas**: Main Reactflow container with background grid
- **MapPanel**: Wrapper component with "Add station" button and modal
- **MetroMapCanvasContents**: Renders the actual nodes and edges

## Backend Architecture

### Server Implementation

`server.py` extends `ChatKitServer` and manages:
- **respond()**: Handles user messages and agent inference
- **action()**: Handles widget interactions (clicking on map elements)

### Domain Stores

- **MetroMap data model**: Stations + Lines
- Each station has: `id`, `name`, `x`, `y` (grid position), `description`, `lines` (which lines pass through)
- Each line has: `id`, `name`, `color`, `stations` (ordered list of station IDs)

### Agent-Frontend Interaction

**Frontend → Agent** (user sends from map):

1. **Station click** → Sends message to agent asking about that station
   ```typescript
   `Tell me about ${stationName}`
   ```

2. **Location confirmation** → When extending a line, user selects where to add station
   ```typescript
   `I would like to add the station to the [beginning/end] of the [Line] line.`
   ```

**Agent → Frontend** (triggers map updates):

The agent doesn't directly modify the map. Instead:
1. User submits new station via modal form (name + line selection)
2. Frontend calls `updateMetroMap()` API to persist changes
3. Backend agent processes the request and can suggest descriptions
4. Frontend updates `useMapStore` state with the new map
5. `MetroMapCanvas` re-renders with new nodes and edges

### State Management

Uses Zustand stores:
- `useMapStore`: Map data, selected station, location selection mode
- `useAppStore`: ChatKit instance and selected article

## Data Flow

```
User clicks station
        ↓
Station click handler → chatkit.sendUserMessage()
        ↓
ChatKit → Backend agent
        ↓
Agent responds with description/analysis
        ↓
Chat displays response

---

User wants to add station
        ↓
Opens "Add station" modal
        ↓
Enters name + selects line
        ↓
Clicks arrow at line endpoint
        ↓
Sends location confirmation to agent
        ↓
Frontend updates map (setMap)
        ↓
MetroMapCanvas re-renders with new station node and edge
```

## Key Libraries

- **Reactflow**: Graph visualization and interaction
- **Zustand**: Client-side state management
- **Lucide React**: Icons (arrows for direction selection)
- **ChatKit React SDK**: Agent communication
- **Tailwind CSS**: Styling

## Files Structure

```
examples/metro-map/
├── frontend/
│   └── src/components/
│       ├── MetroMapCanvas.tsx    # Reactflow setup and station nodes
│       ├── MapPanel.tsx          # Map container with add station modal
│       └── ChatKitPanel.tsx      # Chat interface
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── server.py            # ChatKitServer implementation
│   │   └── ...data/widgets/     # Domain stores and widgets
│   └── pyproject.toml
└── package.json
```

## How to Run

```bash
export OPENAI_API_KEY=sk-...
npm run metro-map
# Frontend: http://localhost:5173
# Backend: http://127.0.0.1:8003
```
