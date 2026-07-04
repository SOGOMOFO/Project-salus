# Sprint 28 — Extract Records/Daily Driver Service Facades

## Objective
Move Records and Daily Driver route behavior behind explicit service facades.

## Shipped
- backend/services/records_service.py
- backend/services/daily_driver_service.py
- Records route module now calls records_service
- Daily Driver route module now calls daily_driver_service
- Existing URLs preserved
- Existing adapter preserved temporarily for behavior safety

## Important
This sprint intentionally does not remove the Sprint 26 backend/main.py legacy bridge yet. The safer sequence is:
1. Centralize adapter.
2. Add service facades.
3. Move behavior into services.
4. Remove backend/main.py legacy support.

## Next Step
Sprint 29 should move the actual handler logic into these services and remove the remaining backend/main.py bridge support.

## Constraint
No feature changes. Refactor only.
