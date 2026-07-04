# Sprint 19 — System Status and Readiness Scoring

## Objective
Create a simple Project Salus readiness score so Kyle can quickly see whether the system and his daily loop are healthy.

## Problem
Project Salus now has navigation and workflows, but Kyle still needs a fast status/risk/readiness summary.

## Must Ship
- Readiness score endpoint
- Readiness page
- Score based on missions, briefs, AARs, Schoolhouse, Charisma, and record hygiene
- Clear recommendations
- Tests

## New Endpoint
- GET /api/command/readiness

## New Page
- GET /command/readiness

## Success Criteria
1. Kyle can see readiness score.
2. Score includes system status.
3. Score includes daily operations readiness.
4. Score includes Schoolhouse readiness.
5. Score includes Charisma readiness.
6. Score includes data hygiene signal.
7. Tests pass.

## Do Not Build Yet
- Advanced analytics
- Predictive modeling
- External integrations
- Cloud deployment
