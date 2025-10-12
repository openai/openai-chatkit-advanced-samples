# Customer Support Demo

Deliver airline-quality support with a ChatKit-powered workflow. This example pairs a scenario-specific FastAPI backend with a React UI so agents can chat with travelers while the right-hand panel surfaces live itinerary data, loyalty status, and recent service actions.

## What's Inside

- **Python FastAPI backend** (`/backend`) - Reference implementation with full ChatKit protocol support
- **TypeScript/Hono backend** (`/backend-node`) - Alternative implementation using openai-agents-js
- ChatKit Web Component embedded in a React app with a context-rich side panel
- Tools for seat changes, trip cancellations, and itinerary updates that sync with the UI in real time

## Prerequisites

- Python 3.11+ (for Python backend)
- Node.js 20+ (for TypeScript backend and frontend)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or `pip` (for Python backend)
- OpenAI API key exported as `OPENAI_API_KEY`
- ChatKit domain key exported as `VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY` (use any non-empty placeholder while developing locally; supply the real key in production)

## Quickstart Overview

1. Choose and start either the Python or TypeScript backend.
2. Configure the domain key and launch the React frontend.
3. Explore the support scenarios end to end.

Each step is detailed below.

### 1. Start a backend

#### Option A: Python FastAPI backend (port 8001)

The Python backend lives in `examples/customer-support/backend` and ships with its own `pyproject.toml`.

```bash
cd examples/customer-support/backend
uv sync
export OPENAI_API_KEY="sk-proj-..."
uv run uvicorn app.main:app --reload --port 8001
```

The API exposes ChatKit at `http://127.0.0.1:8001/support/chatkit` and helper endpoints under `/support/*`.

#### Option B: TypeScript/Hono backend (port 4001)

The TypeScript backend lives in `examples/customer-support/backend-node` and uses the openai-agents-js SDK.

```bash
cd examples/customer-support/backend-node
npm install
export OPENAI_API_KEY="sk-proj-..."
npm run dev
```

The API exposes ChatKit at `http://127.0.0.1:4001/support/chatkit` and helper endpoints under `/support/*`.

### 2. Run the React frontend

```bash
cd examples/customer-support/frontend
npm install
npm run dev
```

The dev server runs at `http://127.0.0.1:5171` and proxies `/support` calls back to the API.

#### Switching between backends

The frontend defaults to the **TypeScript backend** on port `4001`. To switch to the Python backend on port `8001`, update `frontend/vite.config.ts`:

```typescript
// For TypeScript backend (default)
const backendTarget = process.env.BACKEND_URL ?? 'http://127.0.0.1:4001';

// For Python backend
const backendTarget = process.env.BACKEND_URL ?? 'http://127.0.0.1:8001';
```

Alternatively, set the `BACKEND_URL` environment variable:

```bash
BACKEND_URL=http://127.0.0.1:8001 npm run dev
```

From the `examples/customer-support` directory you can also run `npm start` to launch the Python backend (`uv sync` + Uvicorn) and frontend together. Ensure `uv` is installed and required environment variables (for example `OPENAI_API_KEY` and `VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY`) are exported before using this shortcut.

Regarding the domain public key, you can use any string during local development. However, for production deployments:

1. Host the frontend on infrastructure you control behind a managed domain.
2. Register that domain on the [domain allowlist page](https://platform.openai.com/settings/organization/security/domain-allowlist) and mirror it in `examples/customer-support/frontend/vite.config.ts` under `server.allowedHosts`.
3. Set `VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY` to the key returned by the allowlist page and verify it surfaces in `examples/customer-support/frontend/src/lib/config.ts`.

When you need to test remote-access scenarios ahead of launch, temporarily expose the app with a tunnel—e.g. `ngrok http 5171` or `cloudflared tunnel --url http://localhost:5171`—and allowlist that hostname first.

### 3. Try the workflow

Open the printed URL and experiment with prompts such as:

- `Can you move me to seat 14C on flight OA476?`
- `I need to cancel my trip and request a refund.`
- `Add one more checked bag to my reservation.`

The agent invokes the appropriate tools and the timeline updates automatically in the side panel.
