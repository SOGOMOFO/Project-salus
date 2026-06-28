#!/bin/bash
cd "$(dirname "$0")/.."
source .venv/bin/activate
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
uvicorn backend.main:app --reload
