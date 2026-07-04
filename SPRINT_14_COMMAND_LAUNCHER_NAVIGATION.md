# Sprint 14 — Command Launcher and Navigation System

## Objective
Make Project Salus easier and faster for Kyle to launch and use.

## Problem
Project Salus has strong backend and dashboard capability, but Kyle still needs to remember terminal commands and specific URLs.

## Must Ship
- Main home dashboard page
- Navigation links to all major Salus dashboards
- Health/status endpoint
- Local launch script
- Local stop script
- Tests

## Proposed Pages
- GET /
- GET /command

## Proposed Endpoint
- GET /api/command/health

## Navigation Targets
- /command/ops
- /command/review
- /command/integrated
- /command/daily
- /api/command/integrated-state
- /api/command/review-state
- /api/schoolhouse/status
- /api/skills/charisma

## Success Criteria
1. Kyle can open http://127.0.0.1:8000 and see Project Salus.
2. Kyle can navigate to operational dashboard.
3. Kyle can navigate to review dashboard.
4. Kyle can navigate to Schoolhouse/Charisma status.
5. Kyle can start Salus with one script.
6. Kyle can stop Salus with one script.
7. Tests pass.

## Do Not Build Yet
- Authentication
- Database migration
- Cloud deployment
- Multi-user accounts
- External connectors
