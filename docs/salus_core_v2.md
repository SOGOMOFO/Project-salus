# Salus Core v2

Salus Core v2 provides the coordination layer for Project Salus and turns separate services into a shared operating foundation.

## Components
- `agent_runtime.py`: agent registration, listing, and execution with structured outputs.
- `mission_planner.py`: mission lifecycle management (create, list, complete).
- `commander_api.py`: `/core/*` API endpoints for runtime and planner orchestration.
- `event_bus.py`: in-process event publication and subscriber fanout.
- `health_monitor.py`: service/component health checks with degradation reporting.
- `status.py`: shared system status payload builder.

## Core API
- `GET /core`
- `GET /core/status`
- `GET /core/agents`
- `POST /core/agents/{name}/run`
- `GET /core/missions`
- `POST /core/missions`
- `POST /core/missions/{id}/complete`
- `GET /core/events`
- `GET /core/health`

## Structured Agent Result
Each run returns:
- `status`
- `agent`
- `input`
- `output`
- `confidence`
- `timestamp`

## Mission Workflow
- Create missions with title, description, and priority.
- List missions ordered by priority and recency.
- Complete missions with immutable completion timestamps.

## Reliability Notes
- Optional memory writes for agent runs and mission events are best-effort.
- If memory persistence fails, API requests still succeed.
