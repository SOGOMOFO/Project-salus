# Salus Kernel v0.8 — Full Orchestration Pipeline

## Objective
Create the first full Kernel orchestration pipeline.

## Shipped
- backend/core/orchestrator.py
- /api/kernel/orchestrate/status
- /api/kernel/orchestrate
- Kernel status now includes orchestrator status

## Pipeline
1. receive request
2. build context packet
3. classify intent
4. select subsystem
5. build response plan
6. run execution gate
7. run doctrine check
8. recommend learning capture
9. return orchestration packet

## Rule
The orchestrator plans and gates responses. It does not execute external actions.
