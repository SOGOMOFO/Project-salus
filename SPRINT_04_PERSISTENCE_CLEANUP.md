# Sprint 04 — Persistence Cleanup

## Objective
Make Project Salus data survive app restarts.

## Problem
Sprint 01–03 proved the local command loop works, but some data is still stored in memory.

## Required Persistence
- Daily Commander Briefs
- Missions
- Mission updates
- AAR entries

## Must Ship
- Simple local persistence layer
- Data saved after create/update actions
- Data loaded on app startup
- Existing endpoints preserved
- Existing /command UI preserved
- Tests proving data save/load behavior where practical

## Preferred MVP Storage
Use the simplest safe local-first option:
- JSON files under a local data directory, or
- Existing project storage pattern if already present

## Do Not Build Yet
- Supabase
- Vector database
- Multi-user accounts
- Login/auth
- Cloud deployment
- Agent orchestration
- MCP/A2A
- Enterprise features

## Success Criteria
1. Kyle can create a daily brief
2. Kyle can create/update a mission
3. Kyle can create an AAR
4. App can restart without losing saved Sprint 04 data
5. /command still works
6. Tests pass
