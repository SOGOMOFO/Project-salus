# Sprint 31 — Extract Shared Storage and Store Helpers

## Objective
Move shared storage/helper access behind a dedicated storage registry service.

## Shipped
- backend/services/storage_registry.py
- Records service uses storage registry for shared store/helper sync
- Daily Driver service uses storage registry for shared store/helper sync
- Removed direct backend.main namespace sync from Records/Daily Driver services
- Existing URLs preserved

## Preserved URLs
- /api/command/records
- /api/command/records/archive
- /api/command/records/delete
- /command/records
- /api/command/daily-driver-state
- /command/daily-driver

## Remaining Technical Debt
storage_registry.py still reads backend.main as a transitional dependency. Sprint 32 should begin moving actual store ownership into the registry/service layer.

## Constraint
No feature changes. Refactor only.
