#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/examples/customer-support" && pwd)"
export PATH="$HOME/.local/bin:$PATH"

if [ -z "$OPENAI_API_KEY" ]; then
  echo "ERROR: OPENAI_API_KEY is not set."
  echo "Export it first:  export OPENAI_API_KEY=sk-proj-..."
  exit 1
fi

# Start backend in background
echo "Starting FastAPI backend on http://127.0.0.1:8001 ..."
cd "$ROOT/backend"
uv run uvicorn app.main:app --reload --port 8001 &
BACKEND_PID=$!

# Start frontend
echo "Starting React frontend on http://127.0.0.1:5171 ..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend PID: $BACKEND_PID  |  Frontend PID: $FRONTEND_PID"
echo "Open: http://127.0.0.1:5171"
echo "Press Ctrl+C to stop both."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
