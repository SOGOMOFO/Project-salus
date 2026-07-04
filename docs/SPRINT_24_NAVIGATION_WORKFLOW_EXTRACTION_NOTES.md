# Sprint 24 Navigation and Workflow Extraction Notes

## Status
Navigation and workflow routes are now served by extracted route modules.

## Live Modules
- backend/routes/navigation.py
- backend/routes/workflows.py

## Removed From backend/main.py
- Sprint 17 direct workflow block
- Sprint 18 direct navigation block

## Preserved URLs
- /api/command/navigation
- /command/navigation
- /api/workflows/morning
- /api/workflows/evening
- /api/workflows/today
- /command/workflows

## Next Refactor Target
Extract record management and daily driver routes.
