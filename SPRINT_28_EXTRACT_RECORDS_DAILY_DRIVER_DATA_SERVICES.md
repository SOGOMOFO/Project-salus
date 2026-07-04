# Sprint 28 — Extract Records/Daily Driver Data Services

## Objective
Move remaining Records and Daily Driver legacy handler behavior out of backend/main.py and into explicit service/helper modules.

## Problem
Sprint 27 centralized the adapter, but backend/main.py still contains Sprint 26 legacy handler support.

## Must Ship
- backend/services/records_service.py
- backend/services/daily_driver_service.py
- Route modules call service functions directly
- Remove Sprint 26 legacy handler support from backend/main.py
- Preserve all existing URLs
- Preserve all existing tests

## Constraint
No feature changes. Refactor only.
