#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "=== STARTING PROJECT SALUS ==="

lsof -ti:8000 | xargs kill -9 2>/dev/null || true

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

python3 -m uvicorn backend.main:app --reload > /tmp/salus_server.log 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > /tmp/salus_server.pid

echo "Project Salus started."
echo "PID: $SERVER_PID"
echo "Home: http://127.0.0.1:8000"
echo "Ops:  http://127.0.0.1:8000/command/ops"
echo "Log:  /tmp/salus_server.log"
