# Sprint 30 — Replace Source Snapshots With Explicit Services

## Objective
Replace Records and Daily Driver source snapshots with explicit service modules.

## Shipped
- records_service no longer uses RECORDS_LEGACY_SOURCE
- daily_driver_service no longer uses DAILY_DRIVER_LEGACY_SOURCE
- records_service no longer depends on legacy_source_executor
- daily_driver_service no longer depends on legacy_source_executor
- Route modules still call service facades
- backend/main.py remains free of Sprint 26 legacy bridge support
- Existing URLs preserved

## Preserved URLs
- /api/command/records
- /api/command/records/archive
- /api/command/records/delete
- /command/records
- /api/command/daily-driver-state
- /command/daily-driver

## Remaining Technical Debt
The service modules still sync shared storage/helpers from backend.main. Sprint 31 should extract those shared stores/helpers into a dedicated storage/service layer.

## Constraint
No feature changes. Refactor only.
