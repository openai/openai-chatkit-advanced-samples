# OpenSkies Customer Support - TypeScript/Hono Backend

This is a TypeScript reimplementation of the Python FastAPI backend using Hono and the openai-agents-js SDK.

## Architecture

The implementation consists of:

- **`src/airline-state.ts`** - State management for customer profiles and flight bookings
- **`src/support-agent.ts`** - AI agent configuration with tools for seat changes, cancellations, etc.
- **`src/index.ts`** - Hono server with HTTP endpoints

## API Endpoints

### `GET /support/health`

Health check endpoint

- Returns: `{ "status": "healthy" }`

### `GET /support/customer`

Get customer profile

- Query params: `thread_id` (optional)
- Returns: Customer profile with flight segments and timeline

### `POST /support/chatkit`

Main chat endpoint for interacting with the support agent

**ChatKit Protocol Requests:**

- `threads.list` - List all threads
  ```json
  {
    "type": "threads.list",
    "params": {
      "limit": 9999,
      "order": "desc"
    }
  }
  ```

**Legacy Chat Requests:**

- Body:
  ```json
  {
    "message": "Your message here",
    "thread_id": "optional_thread_id",
    "stream": true/false
  }
  ```
- Returns: Agent response (streamed or non-streamed)

## Available Tools

The support agent has access to the following tools:

- **`change_seat(flight_number, seat)`** - Change passenger seat
- **`cancel_trip()`** - Cancel the upcoming reservation
- **`add_checked_bag()`** - Add a checked bag
- **`set_meal_preference(meal)`** - Update meal preference
- **`request_assistance(note)`** - Record special assistance request

## Setup

1. Install dependencies:

   ```bash
   npm install
   ```

2. Create a `.env` file with your OpenAI API key:

   ```
   OPENAI_API_KEY=your_key_here
   ```

3. Build the project:

   ```bash
   npm run build
   ```

4. Run in development mode:

   ```bash
   npm run dev
   ```

5. Run in production:
   ```bash
   npm start
   ```

## Testing

Test the health endpoint:

```bash
curl http://localhost:4001/support/health
```

Test the customer profile:

```bash
curl http://localhost:4001/support/customer
```

Test the threads.list ChatKit protocol:

```bash
curl -X POST http://localhost:4001/support/chatkit \
  -H "Content-Type: application/json" \
  -d '{"type":"threads.list","params":{"limit":9999,"order":"desc"}}'
```

Test a chat message:

```bash
curl -X POST http://localhost:4001/support/chatkit \
  -H "Content-Type: application/json" \
  -d '{"message": "Can you change my seat on flight OA476 to 12C?", "stream": false}'
```

## Differences from Python Implementation

The TypeScript implementation maintains API compatibility with the Python FastAPI version but uses:

- **Hono** instead of FastAPI for the web framework
- **openai-agents-js** SDK instead of the Python agents SDK
- **TypeScript** for type safety
- Same endpoint structure and response formats
- Simplified in-memory state management (no separate MemoryStore class needed for this example)

## Port

The server runs on port **4001** by default.
