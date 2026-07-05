# Sprint 32 — Move Core Store Helper Ownership Into Storage Registry

## Objective
Move common storage helper responsibilities into `backend/services/storage_registry.py`.

## Shipped
- Added preferred storage helper API:
  - sync_service_globals
  - get_store
  - store_count
  - store_counts
  - normalize_record_mutation_payload
  - storage_registry_status
- Records service uses storage registry payload normalization and service sync
- Daily Driver service uses service sync from storage registry
- Existing URLs preserved

## Preserved URLs
- /api/command/records
- /api/command/records/archive
- /api/command/records/delete
- /command/records
- /api/command/daily-driver-state
- /command/daily-driver

## Remaining Technical Debt
The registry still reads backend.main during transition. Sprint 33 should move one low-risk store/helper out of backend.main entirely.

## Constraint
No feature changes. Refactor only.
