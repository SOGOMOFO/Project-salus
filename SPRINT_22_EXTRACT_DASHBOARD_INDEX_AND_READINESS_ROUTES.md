# Sprint 22 — Extract Dashboard Index and Readiness Routes

## Objective
Begin modularizing backend/main.py by extracting the lowest-risk dashboard routes into dedicated route modules.

## Problem
backend/main.py is too large. Refactoring must begin carefully without breaking local MVP behavior.

## Must Ship
- backend/routes package if not present
- Extract dashboard index route logic
- Extract readiness route logic
- Preserve existing URLs
- Preserve existing tests
- Add tests confirming route availability

## Candidate New Files
- backend/routes/dashboard_index.py
- backend/routes/readiness.py

## Success Criteria
1. /api/command/dashboard-index still works.
2. /command/dashboard-index still works.
3. /api/command/readiness still works.
4. /command/readiness still works.
5. Existing tests pass.
6. backend/main.py is reduced or prepared for reduction.

## Constraint
No feature changes. Refactor only.
