# Sprint 14 — Command Launcher and Navigation System

## Objective
Make Project Salus easier and faster for Kyle to launch and use.

## Problem
Project Salus has strong backend and dashboard capability, but Kyle still needs to remember terminal commands and dashboard URLs.

## Must Ship
- Main Project Salus home page
- Command launcher page
- Health/status endpoint
- Navigation links to all major dashboards
- Local launch script
- Local stop script
- Tests

## Pages
- GET /
- GET /command/home

## Endpoint
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
4. Kyle can see system health.
5. Kyle can start Salus with one script.
6. Kyle can stop Salus with one script.
7. Tests pass.

## Do Not Build Yet
- Authentication
- Database migration
- Cloud deployment
- Multi-user accounts
- External connectors
