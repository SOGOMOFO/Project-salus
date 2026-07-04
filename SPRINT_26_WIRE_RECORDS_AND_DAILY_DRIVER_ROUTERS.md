# Sprint 26 — Wire Records and Daily Driver Routers

## Objective
Wire the extracted Record Management and Daily Driver routers into the live FastAPI app and remove duplicate blocks from backend/main.py.

## Problem
Sprint 25 created safe extracted route modules, but backend/main.py still serves the live records and daily driver routes.

## Must Ship
- Include extracted records router
- Include extracted daily_driver router
- Preserve existing URLs
- Remove duplicate Sprint 15 and Sprint 16 route blocks from backend/main.py
- Preserve all existing tests
- Add route behavior tests

## Candidate Route Blocks
- Sprint 15 Daily Driver Polish
- Sprint 16 Record Management Controls

## Constraint
No feature changes. Refactor only.
