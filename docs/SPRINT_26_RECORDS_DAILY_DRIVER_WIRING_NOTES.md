# Sprint 26 Records and Daily Driver Router Wiring Notes

## Status
Record Management and Daily Driver routers are now wired into the live FastAPI app.

## Wired Modules
- backend/routes/records.py
- backend/routes/daily_driver.py

## Removed Direct Route Blocks
- Sprint 15 Daily Driver direct app route block
- Sprint 16 Record Management direct app route block

## Preserved URLs
- /api/command/records
- /api/command/records/archive
- /api/command/records/delete
- /command/records
- /api/command/daily-driver-state
- /command/daily-driver

## Safety Design
Sprint 26 uses a temporary legacy handler bridge to preserve behavior exactly while moving route ownership into backend/routes.

## Next Step
Sprint 27 should remove the legacy bridge by moving data-store operations behind explicit service/helper functions.
