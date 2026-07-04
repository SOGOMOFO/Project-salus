# Sprint 01 — Project Salus Core Loop

## Objective
Build the minimum usable Project Salus personal MVP.

## Core Loop
Observe → Understand → Evaluate → Decide → Execute → Reflect → Learn → Improve

## Must Ship
- Dashboard summary
- Daily Commander Brief
- Mission Tracker
- Mission Update
- AAR Log
- Judgment Matrix

## Endpoints
- GET /dashboard
- GET /daily-brief
- POST /daily-brief
- GET /missions
- POST /missions
- PATCH /missions/{id}
- POST /aar
- GET /aar
- POST /judgment

## Kill List
Do not build yet:
- Agent fleets
- Supabase
- Vector database
- Multi-user support
- Public product
- MCP/A2A
- Enterprise portal
- Payment system
- Full frontend polish

## Success Criteria
Project Salus can be used daily by Kyle to:
1. See today’s priorities
2. Track active missions
3. Update mission status
4. Record an AAR
5. Evaluate a decision using the judgment matrix
