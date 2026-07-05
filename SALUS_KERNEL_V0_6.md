# Salus Kernel v0.6 — Learning Capture Loop

## Objective
Create a learning capture loop so Salus can record lessons from actions, decisions, and outcomes.

## Shipped
- backend/core/learning_capture.py
- /api/kernel/learning-capture/status
- /api/kernel/learning-capture
- /api/kernel/learning-capture/records
- /api/kernel/learning-capture/records/{record_id}
- Kernel status now includes learning capture status

## Learning Record Fields
- id
- input
- outcome
- lesson
- future_rule
- confidence
- source
- tags
- created_at
- updated_at

## Rule
Learning capture records lessons. It does not silently rewrite doctrine or permanent memory.
