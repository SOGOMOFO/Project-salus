# Sprint 24 — Extract Navigation and Workflow Routes

## Objective
Continue modularizing backend/main.py by extracting navigation and workflow routes into dedicated modules.

## Shipped
- backend/routes/navigation.py
- backend/routes/workflows.py
- Removed duplicate Sprint 17 workflow block from backend/main.py
- Removed duplicate Sprint 18 navigation block from backend/main.py
- Preserved existing URLs
- Updated route inventory
- Added route behavior tests

## Routes Extracted
- /api/command/navigation
- /command/navigation
- /api/workflows/morning
- /api/workflows/evening
- /api/workflows/today
- /command/workflows

## Constraint
No feature changes. Refactor only.
