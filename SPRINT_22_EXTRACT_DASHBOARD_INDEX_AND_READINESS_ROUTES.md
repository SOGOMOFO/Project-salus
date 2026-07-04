# Sprint 22 — Extract Dashboard Index and Readiness Routes

## Objective
Begin modularizing backend/main.py by extracting the lowest-risk dashboard routes into dedicated route modules.

## Problem
backend/main.py is too large. Refactoring must begin carefully without breaking local MVP behavior.

## Shipped
- backend/routes package
- backend/routes/dashboard_index.py
- backend/routes/readiness.py
- Extracted payload builders
- Extracted HTML renderers
- Route manifests
- Tests confirming extracted modules and existing URLs

## Important Note
This sprint performs a safe shadow extraction. Existing URLs remain served by backend/main.py until the next sprint wires the extracted routers into the live app and removes duplicated code.

## Constraint
No feature changes. Refactor only.
