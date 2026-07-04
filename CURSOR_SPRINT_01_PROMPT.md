# Cursor Prompt — Sprint 01 Core Loop

You are helping build Project Salus, a Human Judgment System for the Intelligence Age.

Current mission: Sprint 01 Core Loop.

Do not expand scope. Do not add unnecessary frameworks. Do not refactor unrelated code.

Inspect the existing FastAPI backend and implement or improve these MVP endpoints:

- GET /dashboard
- GET /daily-brief
- POST /daily-brief
- GET /missions
- POST /missions
- PATCH /missions/{id}
- POST /aar
- GET /aar
- POST /judgment

Doctrine:
- Improve judgment, not just information
- Keep the human in command
- Separate facts, assumptions, risks, and recommendations
- Support action and reflection
- Avoid unnecessary complexity

Required output:
1. Inspect the repo first.
2. Summarize current structure.
3. Propose the smallest safe implementation plan.
4. Implement only Sprint 01 endpoints.
5. Add tests for each endpoint.
6. Keep persistence simple using the current project pattern.
7. Do not add frontend work.
8. Do not add external AI integrations.
9. Run pytest.
10. Stop when tests pass.
