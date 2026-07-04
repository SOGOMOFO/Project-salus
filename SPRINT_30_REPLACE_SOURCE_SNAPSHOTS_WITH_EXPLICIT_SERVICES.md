# Sprint 30 — Replace Source Snapshots With Explicit Services

## Objective
Replace Records and Daily Driver source snapshots with explicit typed service functions.

## Problem
Sprint 29 moved behavior out of backend/main.py, but behavior is still preserved through source snapshots.

## Must Ship
- records_service explicit state/archive/delete/page functions
- daily_driver_service explicit state/page functions
- Remove legacy_source_executor dependency from records_service and daily_driver_service
- Preserve all existing URLs
- Preserve all existing tests
- Add explicit-service tests

## Constraint
No feature changes. Refactor only.
