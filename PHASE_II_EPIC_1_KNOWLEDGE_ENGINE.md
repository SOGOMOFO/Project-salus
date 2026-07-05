# Phase II Epic 1 — Knowledge Engine

## Objective
Create the first Project Salus Knowledge Engine.

## Purpose
Project Salus must capture structured knowledge that supports judgment, teaching, decision-making, and agent operations.

## Shipped
- backend/services/knowledge_service.py
- backend/routes/knowledge.py
- /api/knowledge/status
- /api/knowledge/item
- /api/knowledge/items
- /api/knowledge/item/{item_id}
- /command/knowledge

## Knowledge Fields
- id
- title
- domain
- source
- summary
- content
- confidence
- tags
- created_at
- updated_at

## Constraint
Local persistence only. No external database yet.
