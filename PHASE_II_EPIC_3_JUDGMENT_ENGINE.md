# Phase II Epic 3 — Judgment Engine

## Objective
Create the first Project Salus Judgment Engine.

## Purpose
The Judgment Engine captures decisions with context, options, evidence, risks, confidence, recommendation, and next action.

## Routes
- /api/judgment-engine/status
- /api/judgment-engine/score
- /api/judgment-engine/item
- /api/judgment-engine/items
- /api/judgment-engine/item/{item_id}
- /command/judgment

## Recommendation Values
- pursue
- pause
- delegate
- discard

## Constraint
No external model calls yet. Rule-based local scoring first.
