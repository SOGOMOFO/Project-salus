#!/bin/zsh
set -e

cd "$(dirname "$0")"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

python -m uvicorn praevale_app.main:app --reload
