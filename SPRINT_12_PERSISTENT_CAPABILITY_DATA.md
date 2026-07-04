# Sprint 12 — Persistent Capability Data

## Objective
Make Project Salus preserve real Schoolhouse and Charisma data across server restarts.

## Problem
The operational dashboard works, but some new module data is still runtime-only.
That is acceptable for tests, but not acceptable for Kyle's real daily use.

## Must Ship
- Persistent Schoolhouse course storage
- Persistent Schoolhouse study-session storage
- Persistent Schoolhouse wrong-answer review storage
- Persistent Schoolhouse writing-task storage
- Persistent Charisma self-assessment storage
- Persistent Charisma conversation AAR storage
- Reset endpoint support for the new data files
- Tests proving data survives reload logic

## Data Files
- sprint12_schoolhouse_courses.json
- sprint12_schoolhouse_study_sessions.json
- sprint12_schoolhouse_wrong_answer_reviews.json
- sprint12_schoolhouse_writing_tasks.json
- sprint12_charisma_self_assessments.json
- sprint12_charisma_conversation_aars.json

## Success Criteria
1. Schoolhouse course data can be saved and reloaded.
2. Schoolhouse study sessions can be saved and reloaded.
3. Charisma assessments can be saved and reloaded.
4. Charisma conversation AARs can be saved and reloaded.
5. /api/dev/reset clears Sprint 12 data.
6. Tests pass.
7. /command/ops remains functional.

## Do Not Build Yet
- Database migration
- User accounts
- Cloud sync
- Authentication
- Multi-user role system
- External integrations
