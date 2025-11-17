# Metro Map

ChatKit-powered metro planner with a React Flow map of stations and colored lines. The left rail hosts ChatKit; the right panel centers the metro graph with a grid background and non-draggable stations.

## Quickstart

1. Export `OPENAI_API_KEY` and `VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_local_dev` (any non-empty string works locally).
2. Backend (FastAPI on port 8003):
   ```bash
   cd examples/metro-map/backend
   uv sync
   uv run uvicorn app.main:app --reload --port 8003
   ```
3. Frontend (Vite on port 5175):
   ```bash
   cd examples/metro-map/frontend
   npm install
   npm run dev
   ```
4. Open http://localhost:5175

## Notes

- The React Flow canvas renders only nodes and edges—no custom SVG canvas—using colored edges for lines and simple station nodes with badges.
- ChatKit runs against `/chatkit`; the map payload streams from `/map`, both provided by the FastAPI backend.
- Update `VITE_CHATKIT_API_DOMAIN_KEY` with a real domain key when deploying to an allowlisted host.
