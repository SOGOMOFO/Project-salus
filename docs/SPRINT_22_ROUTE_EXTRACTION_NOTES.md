# Sprint 22 Route Extraction Notes

## Status
Dashboard Index and Readiness logic has been shadow-extracted into dedicated route modules.

## New Modules
- backend/routes/dashboard_index.py
- backend/routes/readiness.py

## Why Shadow Extraction
Directly removing code from backend/main.py in one step is risky because many sprint-built helpers still share global runtime state. This sprint creates tested route modules first.

## Current Behavior
Existing URLs remain unchanged:
- /api/command/dashboard-index
- /command/dashboard-index
- /api/command/readiness
- /command/readiness

## Next Step
Sprint 23 should wire extracted routers into the FastAPI app and then remove duplicate route blocks from backend/main.py only after tests confirm behavior.
