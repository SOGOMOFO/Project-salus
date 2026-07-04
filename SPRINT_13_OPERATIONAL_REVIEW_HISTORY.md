# Sprint 13 — Operational Review and History Dashboard

## Objective
Create a browser-based review dashboard so Kyle can inspect stored Project Salus operational data without curl.

## Problem
Project Salus can create and persist important data, but Kyle needs a clean way to review what has been saved.

## Must Ship
- Review state endpoint
- Review dashboard page
- Mission review
- Daily brief review
- AAR review
- Schoolhouse course review
- Schoolhouse study-session review
- Schoolhouse wrong-answer review
- Schoolhouse writing-task review
- Charisma self-assessment review
- Charisma conversation AAR review
- Tests

## Proposed Endpoints
- GET /api/command/review-state
- GET /command/review

## Success Criteria
1. Kyle can open /command/review.
2. Review state endpoint returns stored data groups.
3. Schoolhouse persisted data is visible.
4. Charisma persisted data is visible.
5. Mission and AAR history is visible.
6. Tests pass.

## Do Not Build Yet
- Editing records
- Deleting individual records
- Authentication
- User accounts
- Database migration
- Cloud sync
