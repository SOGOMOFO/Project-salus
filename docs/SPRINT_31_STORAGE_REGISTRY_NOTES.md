# Sprint 31 Storage Registry Notes

## Status
Records and Daily Driver services now use a central storage registry for shared legacy stores/helpers.

## New Service
- backend/services/storage_registry.py

## Updated Services
- backend/services/records_service.py
- backend/services/daily_driver_service.py

## Removed From Records/Daily Driver Services
- direct `import backend.main as legacy_main`
- direct `vars(legacy_main)` namespace sync

## Remaining Technical Debt
The storage registry still depends on backend.main. This is a controlled transition point for moving actual data ownership out of backend/main.py in the next sprint.
