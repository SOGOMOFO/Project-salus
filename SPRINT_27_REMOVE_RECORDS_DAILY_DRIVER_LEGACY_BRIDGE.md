# Sprint 27 — Centralize Records/Daily Driver Legacy Route Adapter

## Objective
Reduce Sprint 26 bridge debt by moving duplicated bridge-calling logic from route modules into one service adapter.

## Shipped
- backend/services/legacy_route_adapter.py
- Removed duplicated `_call_legacy_handler` functions from:
  - backend/routes/records.py
  - backend/routes/daily_driver.py
- Preserved all existing URLs
- Preserved Sprint 26 live route ownership
- Added bridge centralization tests

## Important
The remaining legacy handlers still live in backend/main.py temporarily. They are now called through a single service adapter instead of duplicate route-local bridge functions.

## Next Step
Sprint 28 should move the remaining legacy handler behavior into service/helper modules and remove the Sprint 26 legacy handler support section from backend/main.py.

## Constraint
No feature changes. Refactor only.
