# Salus Kernel v0.2 — Subsystem Registry

## Objective
Connect the Kernel to real Salus subsystems.

## Shipped
- backend/core/subsystem_registry.py
- Kernel status exposes subsystem registry
- Kernel routing selects subsystem by intent
- New subsystem registry routes

## Routes
- /api/kernel/subsystems
- /api/kernel/subsystems/{subsystem_id}
- /api/kernel/subsystem-registry/status

## Subsystems
- Core Identity
- Knowledge Engine
- Memory Engine
- Judgment Engine
- Salus Kernel
