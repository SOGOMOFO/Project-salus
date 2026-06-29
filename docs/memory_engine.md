# Persistent Memory Engine v1

Project Salus includes a lightweight SQLite-backed persistent memory engine for storing mission, agent, project, user, and legacy context.

## Supported memory types
- user
- project
- agent
- mission
- legacy

## API surface
- GET /memory
- POST /memory
- GET /memory/search?q=
- DELETE /memory/{id}

## Example payload
```json
{
  "content": "Mission briefing",
  "memory_type": "mission",
  "metadata": {
    "owner": "salus"
  }
}
```
