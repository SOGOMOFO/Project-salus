# Sprint 28 Service Facade Notes

## Status
Records and Daily Driver routes now depend on service facades instead of calling the generic legacy adapter directly.

## New Services
- backend/services/records_service.py
- backend/services/daily_driver_service.py

## Updated Route Modules
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
The service facades still call the central legacy adapter. Sprint 29 should move the real behavior into services and delete the backend/main.py legacy support section.
