# Sprint 23 Router Wiring Notes

## Status
Dashboard Index and Readiness routes are now served by extracted route modules.

## Live Modules
- backend/routes/dashboard_index.py
- backend/routes/readiness.py

## Removed From backend/main.py
- Sprint 19 direct readiness route block
- Sprint 20 direct dashboard index route block

## Preserved URLs
- /api/command/dashboard-index
- /command/dashboard-index
- /api/command/readiness
- /command/readiness

## Audit Update
scripts/salus_audit.py now scans backend/routes/*.py in addition to backend/main.py.

## Next Refactor Target
Extract navigation and workflow routes.
