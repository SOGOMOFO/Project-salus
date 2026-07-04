# Sprint 17 — Daily Workflow Automation

## Objective
Reduce Kyle's daily manual steps by adding guided morning and evening workflows.

## Problem
Project Salus has pages and controls, but Kyle still has to decide the sequence every time.

## Must Ship
- Morning workflow endpoint
- Evening closeout endpoint
- Guided workflow page
- One-click generated morning checklist
- One-click generated evening checklist
- Tests

## Proposed Endpoints
- GET /api/workflows/morning
- GET /api/workflows/evening

## Proposed Page
- GET /command/workflows

## Success Criteria
1. Kyle can open one guided workflow page.
2. Morning workflow tells him what to do first.
3. Evening workflow tells him how to close the day.
4. Workflow links route to the correct dashboards.
5. Tests pass.

## Do Not Build Yet
- Calendar integrations
- Gmail integrations
- Push notifications
- Agent automation
- Cloud deployment
