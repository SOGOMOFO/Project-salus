# Sprint 21 — Local MVP Hardening Plan

## Objective
Begin hardening Project Salus after the local MVP checkpoint.

## Problem
Project Salus works, but most sprint code currently lives in backend/main.py. The next phase should improve maintainability before adding major new capabilities.

## Must Ship
- Backend route inventory
- Refactor plan
- Module split plan
- Data storage plan
- Risk list
- Technical debt list
- Tests

## Candidate Hardening Work
- Split routes into modules
- Move Schoolhouse routes into dedicated file
- Move Charisma routes into dedicated file
- Move dashboard routes into dedicated file
- Move workflow/readiness/record routes into dedicated file
- Consolidate JSON persistence helpers
- Prepare future database migration
- Prepare auth strategy
- Prepare connector strategy

## Success Criteria
1. Project structure is assessed.
2. Technical debt is documented.
3. Refactor sequence is defined.
4. No existing tests break.
5. Next build phase is safer.
