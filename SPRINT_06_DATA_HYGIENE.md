# Sprint 06 — Data Hygiene and Reset Controls

## Objective
Stop test, demo, and smoke-test data from polluting real local Project Salus data.

## Problem
Sprint 01–05 proved the backend, dashboard, mission API, AAR API, persistence, and data contract work.

However, tests and smoke tests now create many duplicate local records:
- demo missions
- test missions
- test AARs
- repeated smoke-test records

## Must Ship
- Dev-only reset endpoint
- Runtime data cleanup control
- Safer test isolation
- Cleaner local data behavior
- Smoke test that confirms reset works

## Endpoints
- POST /api/dev/reset

## Reset Behavior
The reset endpoint should clear:
- Sprint missions
- Sprint daily briefs
- Sprint AARs
- Runtime JSON files if present

## Guardrail
This is a local development tool only.

It should require:
- environment = local/dev/test
or
- explicit confirmation payload

## Do Not Build Yet
- Delete/archive mission UI
- Auth overhaul
- Database migration
- User accounts
- Cloud sync
- Multi-user support
- Production admin panel

## Success Criteria
1. Tests pass.
2. /api/dev/reset clears local Sprint data.
3. /api/dashboard returns clean counts after reset.
4. /api/missions returns status ok and count 0 after reset.
5. No secrets are committed.
