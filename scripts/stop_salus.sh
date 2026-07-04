#!/usr/bin/env bash
set -e

echo "=== STOPPING PROJECT SALUS ==="

if [ -f /tmp/salus_server.pid ]; then
  kill "$(cat /tmp/salus_server.pid)" 2>/dev/null || true
  rm -f /tmp/salus_server.pid
fi

lsof -ti:8000 | xargs kill -9 2>/dev/null || true

echo "Project Salus stopped."
