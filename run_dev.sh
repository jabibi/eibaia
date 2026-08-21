#!/usr/bin/env bash
# Arranca backend (FastAPI/uvicorn) y frontend (Nuxt dev) en local, con el
# frontend apuntando al backend local sin tocar frontend/.env (ver CLAUDE.md).
# Ctrl+C detiene ambos.
set -euo pipefail
set -m # cada job en background arranca en su propio grupo de procesos

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -x "$ROOT_DIR/functions/venv/bin/uvicorn" ]]; then
  echo "No existe functions/venv. Crea el entorno primero (ver README.rst):" >&2
  echo "  cd functions && python3.12 -m venv venv && source venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

CLEANED_UP=0
cleanup() {
  [[ "$CLEANED_UP" -eq 1 ]] && return
  CLEANED_UP=1
  echo
  echo "Deteniendo backend y frontend..."
  [[ -n "${BACKEND_PID:-}" ]] && kill -TERM -- "-${BACKEND_PID}" 2>/dev/null
  [[ -n "${FRONTEND_PID:-}" ]] && kill -TERM -- "-${FRONTEND_PID}" 2>/dev/null
  wait 2>/dev/null
  echo "Servicios detenidos."
}
trap cleanup EXIT INT TERM

(
  cd "$ROOT_DIR/functions"
  source venv/bin/activate
  exec uvicorn app.main:app --port 8000 --reload
) &
BACKEND_PID=$!

(
  cd "$ROOT_DIR/frontend"
  exec env NUXT_PUBLIC_API_BASE=http://localhost:8000/api npm run dev
) &
FRONTEND_PID=$!

wait -n "$BACKEND_PID" "$FRONTEND_PID"
