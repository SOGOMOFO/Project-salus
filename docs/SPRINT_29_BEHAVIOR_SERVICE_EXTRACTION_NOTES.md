# Sprint 29 Behavior Service Extraction Notes

## Status
Records and Daily Driver behavior is no longer stored in backend/main.py legacy bridge sections.

## New Service
- backend/services/legacy_source_executor.py

## Updated Services
- backend/services/records_service.py
- backend/services/daily_driver_service.py

## Removed From backend/main.py
- Sprint 26 Legacy Handler Bridge — Daily Driver
- Sprint 26 Legacy Handler Bridge — Record Management

## Preserved URLs
- /api/command/records
- /api/command/records/archive
- /api/command/records/delete
- /command/records
- /api/command/daily-driver-state
- /command/daily-driver

## Remaining Technical Debt
The service behavior is preserved through source snapshots. Sprint 30 should replace those snapshots with explicit typed service functions.
