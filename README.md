# Project Salus

Project Salus is a modular Personal Intelligence Platform powered by a FastAPI backend and a SQLite persistence layer.

## Alpha Sprint Capabilities

- Core Runtime
	- Agent Runtime
	- Mission Planner
	- Commander API
	- Event Bus
	- Health Monitor
- Memory System
	- Persistent memory
	- Session memory
	- Semantic search interface
	- Memory tagging
	- Memory importance scoring
- Forge
	- Directorate generation
	- Agent/service/API/test/docs generators
	- Plugin metadata and registry updates
- Plugin System
	- Auto discovery
	- Enable/disable
	- Health checks
	- Manifest validation
- Security Core v1
	- Structured auth foundation
	- RBAC: commander, family, agent, readonly
	- Audit logging for protected actions
	- Emergency lockdown mode
	- Plugin permission model
- Investor Intelligence Directorate
	- Expert panel
	- Scoring and risk engine
	- Scenario engine
	- Portfolio model
	- Recommendation engine

## Mission Control API Surface

- `/status`
- `/core`
- `/memory`
- `/missions`
- `/plugins`
- `/forge`
- `/security`
- `/investor-intelligence`

## Validation

Run:

```bash
python3 -m compileall backend
python3 -m pytest -q
```

Both commands should pass before shipping changes.
