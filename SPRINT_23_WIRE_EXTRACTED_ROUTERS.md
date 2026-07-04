# Sprint 23 — Wire Extracted Routers and Remove Duplicate Blocks

## Objective
Wire the extracted Dashboard Index and Readiness routers into the live FastAPI app and remove duplicate route blocks from backend/main.py.

## Problem
Sprint 22 created safe extracted route modules, but backend/main.py still serves the live routes.

## Must Ship
- Include extracted dashboard_index router
- Include extracted readiness router
- Remove duplicate Sprint 19 and Sprint 20 route blocks from backend/main.py
- Preserve existing URLs
- Preserve tests
- Add route conflict checks

## Success Criteria
1. /api/command/dashboard-index still works.
2. /command/dashboard-index still works.
3. /api/command/readiness still works.
4. /command/readiness still works.
5. No duplicate active route handlers remain for these paths.
6. Existing tests pass.

## Constraint
No feature changes. Refactor only.
