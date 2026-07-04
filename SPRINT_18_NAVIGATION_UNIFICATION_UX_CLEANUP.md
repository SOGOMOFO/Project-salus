# Sprint 18 — Navigation Unification and UX Cleanup

## Objective
Unify Project Salus navigation so every major page links cleanly to the daily driver, workflows, ops, review, and records pages.

## Problem
Project Salus has strong pages now, but navigation is distributed and inconsistent.

## Must Ship
- Central navigation endpoint
- Navigation hub page
- Primary page list
- Daily workflow links
- Admin/records links
- Learning and communication links
- Tests

## New Endpoints
- GET /api/command/navigation

## New Page
- GET /command/navigation

## Primary Pages
- /command/workflows
- /command/daily-driver
- /command/home
- /command/ops
- /command/review
- /command/records
- /command/integrated
- /command/daily

## Success Criteria
1. Kyle can reach every major page from one navigation hub.
2. Workflow page is treated as the primary daily operating guide.
3. Navigation endpoint lists all current primary pages.
4. Tests pass.
