# Sprint 29 — Move Records/Daily Driver Behavior Into Services

## Objective
Move Records and Daily Driver behavior out of backend/main.py legacy handlers and into service modules.

## Problem
Sprint 28 created service facades, but those facades still call the central legacy adapter.

## Must Ship
- records_service owns record state/archive/delete/page behavior
- daily_driver_service owns daily driver state/page behavior
- Route modules call services directly
- Remove Sprint 26 legacy handler support section from backend/main.py
- Preserve all existing URLs
- Preserve all tests

## Constraint
No feature changes. Refactor only.
