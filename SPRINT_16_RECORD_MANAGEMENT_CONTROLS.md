# Sprint 16 — Record Management Controls

## Objective
Give Kyle basic control over saved Project Salus records from the browser.

## Problem
Project Salus can create, persist, and review data, but individual records cannot yet be archived or deleted from the UI.

## Must Ship
- Record management state endpoint
- Archive endpoint
- Delete endpoint
- Browser record-management page
- Safer cleanup controls
- Tests

## New Endpoints
- GET /api/command/records
- POST /api/command/records/archive
- POST /api/command/records/delete

## New Page
- GET /command/records

## Record Groups
- missions
- daily_briefs
- aars
- schoolhouse_courses
- schoolhouse_study_sessions
- schoolhouse_wrong_answer_reviews
- schoolhouse_writing_tasks
- charisma_self_assessments
- charisma_conversation_aars

## Success Criteria
1. Kyle can view record groups.
2. Kyle can archive selected records.
3. Kyle can delete selected records.
4. Review dashboard remains usable.
5. Persistent data remains stable.
6. Tests pass.

## Do Not Build Yet
- Full edit forms
- User accounts
- Role-based permissions
- Database migration
- Cloud sync
