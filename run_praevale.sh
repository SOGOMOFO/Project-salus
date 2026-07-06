#!/bin/zsh
set -e

cd "$(dirname "$0")"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

python -m uvicorn backend.main:app --reload --port 8010
