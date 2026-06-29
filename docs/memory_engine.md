# Persistent Memory Engine v1

Project Salus now includes a lightweight SQLite-backed memory engine for mission control context.

## Supported memory types
- user
- project
- agent
- mission
- legacy

## Stored fields
- id
- memory_type
- title
- content
- tags
- source
- created_at
- updated_at

## API surface
- GET /memory
- POST /memory
- GET /memory/search?q=
- DELETE /memory/{id}

## Example payload
```json
{
  "memory_type": "mission",
  "title": "Mission briefing",
  "content": "Project Salus launch plan",
  "tags": ["launch", "mission"],
  "source": "mission-control"
}
```
