# Sprint 29 — Move Records/Daily Driver Behavior Into Services

## Objective
Move Records and Daily Driver behavior out of backend/main.py legacy handler support and into service-owned source snapshots.

## Shipped
- backend/services/legacy_source_executor.py
- records_service now owns the migrated Sprint 16 behavior source
- daily_driver_service now owns the migrated Sprint 15 behavior source
- Removed Sprint 26 legacy handler bridge support from backend/main.py
- Route modules continue calling service facades
- Existing URLs preserved

## Important
This sprint removes the main-file legacy support section while preserving behavior through service-owned snapshots. The next step is to replace source snapshots with explicit service logic.

## Constraint
No feature changes. Refactor only.
