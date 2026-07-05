# Sprint 32 Storage Helper Ownership Notes

## Status
The storage registry now owns common helper behavior instead of leaving it scattered in service modules.

## Updated Service
- backend/services/storage_registry.py

## Updated Callers
- backend/services/records_service.py
- backend/services/daily_driver_service.py

## New Registry Helpers
- sync_service_globals
- get_store
- store_count
- store_counts
- normalize_record_mutation_payload
- storage_registry_status

## Remaining Technical Debt
Store data still originates in backend.main. Next sprint should move one low-risk shared store/helper into the storage layer.
