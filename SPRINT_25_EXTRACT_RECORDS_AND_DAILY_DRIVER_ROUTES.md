# Sprint 25 — Extract Record Management and Daily Driver Routes

## Objective
Continue modularizing backend/main.py by extracting record management and daily driver routes into dedicated modules.

## Must Ship
- backend/routes/records.py
- backend/routes/daily_driver.py
- Preserve existing URLs
- Remove duplicate route blocks from backend/main.py after wiring
- Update route inventory
- Add route behavior tests

## Candidate Routes
- /api/command/records
- /api/command/records/archive
- /api/command/records/delete
- /command/records
- /api/command/daily-driver-state
- /command/daily-driver

## Constraint
No feature changes. Refactor only.
