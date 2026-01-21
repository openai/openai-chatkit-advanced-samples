# Customer Support Demo

Deliver airline-quality support with a ChatKit-powered workflow. This example pairs a scenario-specific FastAPI backend with a React UI so agents can chat with travelers while the right-hand panel surfaces live itinerary data, loyalty status, and recent service actions.

## What's Inside
- FastAPI service that streams responses from an OpenAI Agent trained on airline tooling.
- ChatKit Web Component embedded in a React app with a context-rich side panel.
- Chat composer dictation (speech-to-text) so you can talk your prompts instead of typing.
- Tools for seat changes, trip cancellations, and itinerary updates that sync with the UI in real time.

## Prerequisites
- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or `pip`
- OpenAI API key exported as `OPENAI_API_KEY`
- ChatKit domain key exported as `VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY` (use any non-empty placeholder while developing locally; supply the real key in production)

## Quickstart Overview
1. Install dependencies and start the customer support backend.
2. Configure the domain key and launch the React frontend.
3. Explore the support scenarios end to end.

Each step is detailed below.

### 1. Start the FastAPI backend

The backend for this demo lives in `examples/customer-support/backend` and ships with its own `pyproject.toml`.

```bash
cd examples/customer-support/backend
uv sync
export OPENAI_API_KEY="sk-proj-..."
uv run uvicorn app.main:app --reload --port 8001
```

The API exposes ChatKit at `http://127.0.0.1:8001/support/chatkit` and helper endpoints under `/support/*`.

### 2. Run the React frontend

```bash
cd examples/customer-support/frontend
npm install
npm run dev
```

The dev server runs at `http://127.0.0.1:5171` and proxies `/support` calls back to the API, which covers local iteration.

From the `examples/customer-support` directory you can also run `npm start` to launch the backend (`uv sync` + Uvicorn) and frontend together. Ensure `uv` is installed and required environment variables (for example `OPENAI_API_KEY` and `VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY`) are exported before using this shortcut.

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

You can also use dictation: click the mic button in the message composer, grant microphone permission when prompted, and speak your request (the app transcribes it before sending).
