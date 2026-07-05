# Phase II Epic 1 — Knowledge Engine Plan

## Objective
Create the first version of the Project Salus Knowledge Engine.

## Purpose
Project Salus must convert information into organized knowledge that can support judgment, teaching, decision-making, and agent operations.

## Initial Data Model
Knowledge item fields:
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

## Initial Routes
- GET /api/knowledge/status
- POST /api/knowledge/item
- GET /api/knowledge/items
- GET /api/knowledge/item/{item_id}
- GET /command/knowledge

## Rules
- No external database yet
- Use existing local persistence pattern
- Add tests before merge
- Preserve all existing tests
- No breaking route changes

## Definition of Done
- All existing tests pass
- New knowledge tests pass
- Knowledge module has route file
- Knowledge service exists
- Knowledge docs exist
