# Sprint 26 — Wire Records and Daily Driver Routers

## Objective
Wire the extracted Record Management and Daily Driver routers into the live FastAPI app.

## Shipped
- Included extracted records router
- Included extracted daily_driver router
- Removed duplicate direct route registration blocks from backend/main.py
- Preserved existing URLs
- Preserved legacy behavior through a temporary handler bridge
- Updated route inventory
- Added wiring tests

## Preserved URLs
- /api/command/records
- /api/command/records/archive
- /api/command/records/delete
- /command/records
- /api/command/daily-driver-state
- /command/daily-driver

## Constraint
No feature changes. Refactor only.
