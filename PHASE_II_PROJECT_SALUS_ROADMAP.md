# Project Salus Phase II Roadmap

## Phase I Status
Phase I local MVP is complete and stable.

Current verified baseline:
- Branch: forge-v2
- Tests: 208 passed, 1 warning
- Latest checkpoint: Sprint 32 complete
- Current architecture includes routes, services, storage registry, dashboards, records, Schoolhouse, Charisma, Daily Driver, navigation, readiness, and operational controls.

## Strategic Pivot
Stop micro-refactor sprints for now.

Project Salus now shifts from backend hardening to product capability development.

## Phase II Mission
Build Project Salus into a Human Judgment System for the Intelligence Age.

## Epic 1 — Knowledge Engine
Create the foundation for storing, organizing, retrieving, and reasoning over Project Salus knowledge.

## Epic 2 — Memory Engine
Separate working memory, long-term memory, user memory, mission memory, and knowledge memory.

## Epic 3 — Judgment Engine
Create decision-quality scoring, evidence tracking, confidence levels, risks, tradeoffs, and recommendation logic.

## Epic 4 — Teaching Engine
Improve the Schoolhouse module into a true adaptive learning coach for WGU, PSP, cybersecurity, business, and AI.

## Epic 5 — Agent Framework
Build specialized Salus agents:
- Commander
- Teacher
- Cyber
- Finance
- Health
- Family/Admin
- Intelligence
- Business
- Legacy

## Epic 6 — Real Database
Move from local in-memory/json persistence toward SQLite first, then Postgres.

## Epic 7 — Real Frontend
Move toward a clean mission-control UI with React/Next.js when backend foundations are ready.

## Epic 8 — Auth and User Profiles
Add authentication, user profiles, permissions, and multi-user capability.

## Epic 9 — Provider Layer
Create model/provider abstraction:
- OpenAI
- Claude
- Gemini
- Local models
- Fallback logic

## Epic 10 — Deployment
Docker, GitHub Actions, cloud deployment, backup, and production readiness.

## Immediate Next Step
Start Phase II Epic 1: Knowledge Engine.

First build:
- knowledge item model
- knowledge capture route
- knowledge list/search route
- knowledge source field
- confidence field
- domain field
- tests
