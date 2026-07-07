#!/bin/zsh
set -e

cd "$(dirname "$0")"

if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

HOST="${SALUS_HOST:-127.0.0.1}"
PORT="${SALUS_PORT:-8010}"

echo "Starting Project Salus on ${HOST}:${PORT}"
python -m uvicorn backend.main:app --reload --host "${HOST}" --port "${PORT}"
