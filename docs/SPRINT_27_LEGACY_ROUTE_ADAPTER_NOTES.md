# Sprint 27 Legacy Route Adapter Notes

## Status
The duplicated bridge implementation has been centralized.

## New Service
- backend/services/legacy_route_adapter.py

## Route Modules Updated
- backend/routes/records.py
- backend/routes/daily_driver.py

## Preserved URLs
- /api/command/records
- /api/command/records/archive
- /api/command/records/delete
- /command/records
- /api/command/daily-driver-state
- /command/daily-driver

## Remaining Technical Debt
backend/main.py still contains Sprint 26 legacy handler support. Sprint 28 should remove that support by moving behavior into explicit services.
