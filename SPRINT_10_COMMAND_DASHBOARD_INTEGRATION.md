# Sprint 10 — Command Dashboard Integration

## Objective
Bring Schoolhouse and Charisma into a visible Project Salus command dashboard so Kyle can use them without curl commands.

## Problem
Project Salus now has backend modules for:
- Daily use mode
- Schoolhouse Learning Coach
- Charisma and Communication Skill

But they are not yet integrated into one operational dashboard.

## Must Ship
- Integrated command state endpoint
- Visible dashboard page
- Schoolhouse panel
- Charisma panel
- Daily use panel
- Tests

## Proposed Endpoints
- GET /api/command/integrated-state
- GET /command/integrated

## Success Criteria
1. Kyle can open one dashboard page.
2. Dashboard shows daily-use status.
3. Dashboard shows Schoolhouse status.
4. Dashboard shows Charisma status.
5. Tests pass.
