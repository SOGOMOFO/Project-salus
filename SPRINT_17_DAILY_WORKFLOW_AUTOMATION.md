# Sprint 17 — Daily Workflow Automation

## Objective
Reduce Kyle's daily manual steps by adding guided morning and evening workflows.

## Problem
Project Salus has pages, controls, review, persistence, and record management, but Kyle still has to decide the operating sequence every time.

## Must Ship
- Morning workflow endpoint
- Evening workflow endpoint
- Combined today workflow endpoint
- Guided workflow page
- Links to correct dashboards
- Tests

## New Endpoints
- GET /api/workflows/morning
- GET /api/workflows/evening
- GET /api/workflows/today

## New Page
- GET /command/workflows

## Success Criteria
1. Kyle can open one guided workflow page.
2. Morning workflow tells him what to do first.
3. Evening workflow tells him how to close the day.
4. Workflow links route to correct dashboards.
5. Tests pass.
