# Sprint 32 — Move Core Store Ownership Into Storage Registry

## Objective
Move core store ownership and common store helper functions out of backend/main.py into backend/services/storage_registry.py.

## Problem
Sprint 31 centralized storage access, but the storage registry still reads store objects from backend.main.

## Must Ship
- storage_registry owns common store helper functions
- records_service uses storage_registry helpers directly
- daily_driver_service uses storage_registry count helpers directly
- Preserve all existing URLs
- Preserve all tests

## Constraint
No feature changes. Refactor only.
