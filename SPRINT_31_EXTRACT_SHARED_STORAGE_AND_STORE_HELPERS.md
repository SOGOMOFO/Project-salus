# Sprint 31 — Extract Shared Storage and Store Helpers

## Objective
Move shared storage helpers and store registry behavior out of backend/main.py into dedicated service/storage modules.

## Problem
Records and Daily Driver services are explicit, but still sync shared stores/helpers from backend.main.

## Must Ship
- backend/services/storage_registry.py or backend/storage.py
- Shared count/list/archive/delete helper ownership outside backend/main.py
- Records service uses storage service directly
- Daily Driver service uses storage/count service directly
- Preserve all existing URLs
- Preserve all tests

## Constraint
No feature changes. Refactor only.
