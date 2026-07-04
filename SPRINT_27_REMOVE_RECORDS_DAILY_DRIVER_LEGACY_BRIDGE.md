# Sprint 27 — Remove Records/Daily Driver Legacy Bridge

## Objective
Remove the temporary Sprint 26 legacy handler bridge by moving data-store operations into explicit service/helper functions.

## Problem
Sprint 26 moved route ownership into backend/routes, but backend/main.py still contains legacy helper functions for behavior preservation.

## Must Ship
- Extract records data operations into a service/helper module
- Extract daily-driver state helper into a service/helper module
- Remove Sprint 26 legacy handler bridge from backend/main.py
- Preserve all existing URLs
- Preserve all existing tests
- Add bridge-removal tests

## Constraint
No feature changes. Refactor only.
