# Mercedes-Benz Automobile Voice Assistant

An advanced ChatKit example application demonstrating a sophisticated voice assistant for a Mercedes-Benz EQ electric vehicle. This application showcases real-time UI synchronization with AI-powered voice commands across 9 key vehicle features.

## Features

This example implements a comprehensive in-vehicle voice assistant with the following capabilities:

### 1. Climate Control
- **Voice Command**: "Set cabin temperature to 72 degrees"
- **UI Updates**: Climate panel visually updates temperature, fan speed, and seat heating settings
- **Verbal Confirmation**: AI confirms changes with natural language

### 2. Navigation
- **Voice Command**: "Navigate to Santa Monica Beach"
- **UI Updates**: Map updates with route, next maneuver is highlighted, ETA displayed
- **Visual Feedback**: Active route with turn-by-turn guidance

### 3. Vehicle Status
- **Voice Command**: "What's my battery level and range?"
- **UI Updates**: Dashboard surfaces live metrics (battery %, range, tire pressure)
- **Real-time Data**: Current charging status and warnings

### 4. Media Control
- **Voice Command**: "Play my favorite playlist" or "Turn up the volume"
- **UI Updates**: Media player shows track, artist, source, and playback state
- **Synchronized Display**: Volume slider and play/pause state update in real-time

### 5. Assistance & Service
- **Voice Command**: "Request roadside assistance"
- **UI Updates**: Assistance panel displays confirmation, shared location, and call status
- **Service Types**: Roadside, concierge, and service appointment requests

### 6. Warning Explanation
- **Voice Command**: "What's that warning light?"
- **UI Updates**: Dashboard highlights the specific warning being explained
- **Detailed Info**: Severity, explanation, and recommended action

### 7. Location-Based Services
- **Voice Command**: "Find nearby charging stations"
- **UI Updates**: Map displays ranked charging options with availability and speed
- **Instant Results**: Distance, available chargers, and estimated charging time

### 8. Comfort Personalization
- **Voice Command**: "Set ambient lighting to blue"
- **UI Updates**: Interior lighting visualization shows color transition
- **Visual Feedback**: Brightness slider and color preview update immediately

### 9. Context Restoration
- **Voice Command**: "Resume route from earlier"
- **UI Updates**: Restores previous navigation context and view
- **Memory**: Recalls past routes, media preferences, and comfort settings

## Architecture

### Backend (FastAPI + OpenAI Agents SDK)

```
backend/
├── app/
│   ├── main.py              # FastAPI server with /mercedes/chatkit endpoint
│   ├── chat.py              # ChatKit server with 9 function tools
│   ├── vehicle_state.py     # Vehicle state management
│   ├── constants.py         # Agent instructions and configuration
│   ├── memory_store.py      # Thread/item persistence
│   └── __init__.py
└── pyproject.toml           # Python dependencies
```

**Key Technologies**:
- FastAPI for REST API and ChatKit endpoint
- OpenAI Agents SDK for function tools
- OpenAI ChatKit Python SDK for conversation management
- In-memory state management (production would use database)

### Frontend (React + TypeScript + ChatKit React)

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatKitPanel.tsx    # ChatKit integration with client tool handlers
│   │   ├── Dashboard.tsx       # Real-time vehicle metrics display
│   │   ├── Home.tsx            # Main layout
│   │   └── ThemeToggle.tsx     # Light/dark theme switcher
│   ├── hooks/
│   │   ├── useVehicleState.ts  # Vehicle state management and updates
│   │   └── useColorScheme.ts   # Theme persistence
│   ├── lib/
│   │   └── config.ts           # API URLs and UI configuration
│   ├── types/
│   │   └── vehicle.ts          # TypeScript interfaces
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── vite.config.ts              # Vite dev server with proxy
├── tailwind.config.ts
└── package.json
```

**Key Technologies**:
- React 19 with TypeScript
- @openai/chatkit-react for voice assistant UI
- Tailwind CSS for styling
- Vite for development and building

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.12+
- **uv** (Python package manager) - Install with: `pip install uv`
- **OpenAI API Key** with access to GPT-4o

## Installation

1. **Set up environment variables**:

   Create a `.env` file in the `backend` directory:

   ```bash
   OPENAI_API_KEY=sk-...
   ```

2. **Install dependencies** (both frontend and backend):

   From the `examples/mercedes_benz_automobile` directory:

   ```bash
   npm install
   ```

## Running the Application

From the `examples/mercedes_benz_automobile` directory:

```bash
npm start
```

This will start:
- **Backend**: http://localhost:8004
- **Frontend**: http://localhost:5174

The frontend will automatically proxy `/mercedes/*` requests to the backend.

## Usage

1. Open http://localhost:5174 in your browser
2. Click the microphone or type in the chat input
3. Try any of these example prompts:

   **Climate**:
   - "Set the temperature to 70 degrees"
   - "Turn on driver seat heating to level 2"
   - "Switch to cooling mode"

   **Navigation**:
   - "Navigate to LAX Airport"
   - "Take me home"
   - "What's my next turn?"

   **Vehicle Status**:
   - "What's my battery level?"
   - "Check tire pressure"
   - "Any warnings?"

   **Media**:
   - "Play some jazz music"
   - "Turn the volume up to 20"
   - "Pause the music"

   **Assistance**:
   - "I need roadside assistance"
   - "Schedule a service appointment"

   **Location Services**:
   - "Find nearby charging stations"
   - "Where's the closest parking?"

   **Comfort**:
   - "Set ambient lighting to purple"
   - "Dim the interior lights to 30%"

   **Context**:
   - "Resume the route from earlier"
   - "Go back to my last destination"

4. Watch the dashboard update in real-time as the AI makes changes

## How It Works

### Client Tool Calls (UI Synchronization)

When the AI needs to update the UI, it uses **client tool calls**:

1. **Backend**: Function tool sets `ctx.context.client_tool_call`
   ```python
   ctx.context.client_tool_call = ClientToolCall(
       name="update_climate_ui",
       arguments={"temperature": 72, "fan_speed": 3}
   )
   ```

2. **Frontend**: ChatKit `onClientTool` handler receives the call
   ```typescript
   onClientTool: async (invocation) => {
     if (invocation.name === "update_climate_ui") {
       updateVehicleState(invocation.params);
       return { success: true };
     }
   }
   ```

3. **React State**: `useVehicleState` hook updates local state
4. **Dashboard**: Components re-render with new values

### Function Tools

Each feature is implemented as a function tool:

- `adjust_climate()` - Temperature, fan, seat heating/ventilation
- `set_navigation()` - Routing and destination
- `get_vehicle_status()` - Battery, range, tire pressure, warnings
- `control_media()` - Play/pause, volume, source selection
- `request_assistance()` - Roadside, concierge, service
- `explain_warning()` - Warning details and recommended actions
- `find_nearby()` - Charging stations, parking, restaurants
- `set_ambient_lighting()` - Interior lighting color and brightness
- `restore_context()` - Previous routes, settings, preferences

## Project Structure Highlights

### Backend Agent Flow

```python
# 1. User message arrives
input = "Set temperature to 72"

# 2. Agent context created with vehicle state
context = VehicleAgentContext(thread=thread, store=store, ...)

# 3. Agent runs with function tools
async with agent.run_stream(input, context) as stream:
    # 4. Agent calls adjust_climate tool
    # 5. Tool updates vehicle state and triggers client tool call
    # 6. Client tool call streamed to frontend
    # 7. Agent responds with verbal confirmation
```

### Frontend State Flow

```typescript
// 1. User sends message via ChatKit
chatkit.control.send("Set temperature to 72")

// 2. Backend processes and streams events
// 3. Client tool call received
onClientTool: (invocation) => {
  // 4. Update React state
  performAction({ type: invocation.name, payload: invocation.params })
}

// 5. Dashboard re-renders with new state
<Dashboard vehicleState={vehicleState} />
```

## Customization

### Adding New Vehicle Features

1. **Backend**: Add function tool in `backend/app/chat.py`:
   ```python
   @function_tool(description_override="...")
   async def my_new_feature(ctx: RunContextWrapper[VehicleAgentContext], ...):
       # Update vehicle state
       # Trigger client tool call
       return {"success": True}
   ```

2. **Frontend**: Add handler in `ChatKitPanel.tsx`:
   ```typescript
   case "my_new_feature_ui":
     onVehicleAction({ type: invocation.name, payload: invocation.params });
     return { success: true };
   ```

3. **State**: Update `useVehicleState` hook to handle new state

4. **UI**: Add component to display the new feature

### Changing the Agent Behavior

Edit `backend/app/constants.py` to modify:
- `INSTRUCTIONS`: Agent personality and guidelines
- `MODEL`: Switch between GPT-4o, GPT-4o-mini, etc.

## Production Considerations

This is a demonstration example. For production:

1. **Authentication**: Add user authentication and session management
2. **Database**: Replace in-memory store with persistent database
3. **Real APIs**: Integrate with actual vehicle APIs, navigation services, and charging networks
4. **Security**: Validate inputs, sanitize outputs, implement rate limiting
5. **Monitoring**: Add logging, error tracking, and performance monitoring
6. **Scaling**: Use Redis for state, load balancing for multiple instances

## Troubleshooting

**Backend won't start**:
- Ensure `OPENAI_API_KEY` is set in `.env`
- Check Python version: `python --version` (should be 3.12+)
- Install uv: `pip install uv`

**Frontend won't connect**:
- Verify backend is running on port 8004
- Check browser console for errors
- Ensure vite proxy is configured correctly

**Client tools not working**:
- Check browser console for `onClientTool` logs
- Verify handler is registered in `ChatKitPanel.tsx`
- Ensure backend is setting `client_tool_call` correctly

## License

MIT

## Related Examples

- [Customer Support](../customer-support/) - Airline support agent
- [Marketing Assets](../marketing-assets/) - Creative asset generation
- [Knowledge Assistant](../knowledge-assistant/) - Document grounded answers
