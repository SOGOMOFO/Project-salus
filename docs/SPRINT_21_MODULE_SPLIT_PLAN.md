# Sprint 21 Module Split Plan

## Objective
Split backend/main.py into maintainable route and service modules without breaking current tests.

## Proposed Target Structure

backend/
├── main.py
├── routes/
│   ├── command.py
│   ├── daily.py
│   ├── schoolhouse.py
│   ├── charisma.py
│   ├── records.py
│   ├── workflows.py
│   ├── readiness.py
│   └── dashboard_index.py
├── services/
│   ├── persistence.py
│   ├── readiness_service.py
│   ├── workflow_service.py
│   └── audit_service.py
└── schemas/
    ├── command.py
    ├── schoolhouse.py
    ├── charisma.py
    └── records.py

## Refactor Sequence

### Phase 1 — Safety Harness
- Keep all behavior unchanged
- Add audit/inventory script
- Confirm tests green
- Create route inventory

### Phase 2 — Extract Low-Risk Routes
- Extract dashboard index routes
- Extract readiness routes
- Extract navigation routes

### Phase 3 — Extract Workflow and Record Routes
- Extract workflow routes
- Extract record management routes
- Confirm persistence still works

### Phase 4 — Extract Capability Modules
- Extract Schoolhouse routes
- Extract Charisma routes
- Extract daily-use routes

### Phase 5 — Consolidate Persistence
- Centralize JSON file loading/saving
- Add backup/export strategy
- Prepare database migration

## Rule
One module extraction per sprint. Tests must pass after each extraction.
