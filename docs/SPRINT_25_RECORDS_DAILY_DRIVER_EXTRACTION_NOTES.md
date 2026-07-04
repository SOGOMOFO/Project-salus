# Sprint 25 Records and Daily Driver Extraction Notes

## Status
Record Management and Daily Driver logic has been shadow-extracted into dedicated route modules.

## New Modules
- backend/routes/records.py
- backend/routes/daily_driver.py

## Why Shadow Extraction
Record management touches local data mutation. A safe extraction first is lower risk than wiring and deleting backend/main.py blocks in the same sprint.

## Existing Live URLs Preserved
- /api/command/records
- /api/command/records/archive
- /api/command/records/delete
- /command/records
- /api/command/daily-driver-state
- /command/daily-driver

## Next Step
Sprint 26 should wire these extracted routers into the FastAPI app and remove duplicate route blocks only after tests confirm behavior.
