# Salus Kernel v0.3 — Context Packet Builder

## Objective
Build a real context packet that combines identity, memory, knowledge, judgment, classification, and subsystem routing.

## Shipped
- backend/core/context_packet.py
- /api/kernel/context/status
- /api/kernel/context
- Kernel route responses now include context_packet

## Context Packet Includes
- user
- input
- classification
- selected subsystem
- core identity status
- memory status
- knowledge status
- judgment status
- operating rules

## Rule
Context packet informs routing and response generation. It does not execute actions.
