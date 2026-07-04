# Sprint 13 — Operational Review and History Dashboard

## Objective
Create a browser-based review dashboard so Kyle can inspect stored Project Salus operational data without curl.

## Problem
Project Salus can now create and persist important data, but Kyle needs a clean way to review what has been saved.

## Must Ship
- Review dashboard page
- Stored Schoolhouse course review
- Stored Schoolhouse study-session review
- Stored Charisma self-assessment review
- Stored Charisma conversation AAR review
- Mission review
- Daily-use state review
- Tests

## Proposed Endpoints
- GET /api/command/review-state
- GET /command/review

## Review Sections
- Daily Use
- Missions
- Schoolhouse Courses
- Schoolhouse Study Sessions
- Schoolhouse Wrong-Answer Reviews
- Schoolhouse Writing Tasks
- Charisma Self-Assessments
- Charisma Conversation AARs

## Success Criteria
1. Kyle can open /command/review.
2. Page loads in browser.
3. Review state endpoint returns stored data groups.
4. Schoolhouse persisted data is visible.
5. Charisma persisted data is visible.
6. Tests pass.

## Do Not Build Yet
- Editing records
- Deleting individual records
- Authentication
- User accounts
- Database migration
- Cloud sync
