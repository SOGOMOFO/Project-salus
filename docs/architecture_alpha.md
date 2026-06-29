# Project Salus Alpha Sprint Architecture

Project Salus Alpha is a modular Personal Intelligence Platform composed of six major subsystems.

## Subsystems

### 1. Core Runtime
- Agent Runtime: registration, discovery, execution, and optional memory persistence.
- Mission Planner: mission lifecycle and priority-aware mission queueing.
- Commander API: operational control surface under `/core`.
- Event Bus: in-process publish/subscribe event stream for mission and agent activity.
- Health Monitor: component health recording and degradation reporting.

### 2. Memory System
- Persistent Memory: SQLite-backed durable memory records.
- Session Memory: scoped key-value memory by session id.
- Semantic Search Interface: token-similarity matching over memory records.
- Memory Tagging: tag arrays persisted with each memory.
- Importance Scoring: normalized score in `[0.0, 1.0]` for prioritization.

### 3. Forge
- Complete CLI under `python3 -m backend.forge`.
- Directorate generation with API/service/agent/test/docs/manifests.
- Generator alias commands:
  - `generate-agent`
  - `generate-service`
  - `generate-api`
  - `generate-tests`
  - `generate-docs`
  - `update-registry`
- Registry and plugin metadata updates are automatic.

### 4. Plugin System
- Auto discovery from `backend/directorates/*`.
- Enable/disable controls.
- Plugin health payloads with required-file checks.
- Manifest validation for required shape and types.

### 5. Investor Intelligence Directorate
- Expert Panel synthesis.
- Scoring and confidence policy engine.
- Risk Engine and scenario engine.
- Portfolio model output.
- Recommendation engine with discipline constraints.

### 6. Mission Control API
- `/status`
- `/core`
- `/memory`
- `/missions`
- `/plugins`
- `/forge`
- `/investor-intelligence`

## Runtime Notes
- Memory writes from optional subsystems are best-effort and non-fatal.
- Recommendations remain decision support only.
- Brokerage integration remains disabled by design.
