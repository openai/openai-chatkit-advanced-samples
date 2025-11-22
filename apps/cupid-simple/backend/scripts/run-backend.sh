#!/usr/bin/env bash
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${BACKEND_DIR}/.venv"
PORT="${PORT:-8003}"
UV_PROJECT_ENVIRONMENT="${VENV_DIR}" uv sync --directory "${BACKEND_DIR}"
exec "${VENV_DIR}/bin/python" -m uvicorn app.main:app --app-dir "${BACKEND_DIR}" --reload --port "${PORT}"
