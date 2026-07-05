# Sprint 33 — Move First Low-Risk Store Helper Out Of backend/main.py

## Objective
Move one low-risk store/helper fully out of backend/main.py and into the storage/service layer.

## Problem
Sprint 32 moved helper ownership into storage_registry, but actual data still originates from backend.main.

## Must Ship
- Select one low-risk helper/store
- Move ownership into backend/services/storage_registry.py or a dedicated storage module
- Preserve all existing URLs
- Preserve all tests

## Constraint
No feature changes. Refactor only.
