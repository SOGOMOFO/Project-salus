# Sprint 16 — Record Management Controls

## Objective
Give Kyle basic control over saved Project Salus records from the browser.

## Problem
Project Salus can create, persist, and review data, but individual records cannot yet be edited, archived, or deleted from the UI.

## Must Ship
- Record management state endpoint
- Basic archive/delete endpoint for selected record groups
- UI controls for cleaning test/demo data
- Safer dev reset placement
- Tests

## Candidate Record Groups
- Missions
- Daily briefs
- AARs
- Schoolhouse courses
- Schoolhouse study sessions
- Schoolhouse wrong-answer reviews
- Schoolhouse writing tasks
- Charisma self-assessments
- Charisma conversation AARs

## Success Criteria
1. Kyle can remove bad/demo entries.
2. Kyle can archive records instead of losing them.
3. Review dashboard remains usable.
4. Persistent data remains stable.
5. Tests pass.

## Do Not Build Yet
- User accounts
- Full database migration
- Cloud sync
- Role-based permissions
- Audit-grade compliance logs
