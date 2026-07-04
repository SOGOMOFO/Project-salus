# Sprint 25 — Extract Record Management and Daily Driver Routes

## Objective
Continue modularizing backend/main.py by extracting record management and daily driver routes into dedicated modules.

## Shipped
- backend/routes/records.py
- backend/routes/daily_driver.py
- Route manifests
- Extracted payload builders
- Extracted HTML renderers
- Route module tests
- Live route behavior checks

## Important Note
This sprint performs a safe shadow extraction. Existing URLs remain served by backend/main.py until the next sprint wires these extracted routers into the live app and removes duplicated code.

## Routes Shadow-Extracted
- /api/command/records
- /api/command/records/archive
- /api/command/records/delete
- /command/records
- /api/command/daily-driver-state
- /command/daily-driver

## Constraint
No feature changes. Refactor only.
