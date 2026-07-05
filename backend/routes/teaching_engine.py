from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from backend.services.teaching_engine_service import (
    build_learning_profile,
    build_lesson,
    build_quiz,
    create_teaching_session,
    get_teaching_session,
    list_teaching_sessions,
    teaching_engine_status,
)


router = APIRouter(tags=["teaching-engine"])


@router.get("/api/teaching-engine/status")
async def teaching_engine_status_api() -> dict[str, Any]:
    return teaching_engine_status()


@router.post("/api/teaching-engine/profile")
async def teaching_engine_profile_api(payload: dict[str, Any]) -> dict[str, Any]:
    return build_learning_profile(payload)


@router.post("/api/teaching-engine/lesson")
async def teaching_engine_lesson_api(payload: dict[str, Any]) -> dict[str, Any]:
    return build_lesson(payload)


@router.post("/api/teaching-engine/quiz")
async def teaching_engine_quiz_api(payload: dict[str, Any]) -> dict[str, Any]:
    return build_quiz(payload)


@router.post("/api/teaching-engine/session")
async def teaching_engine_session_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        session = create_teaching_session(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "ok",
        "session": session,
    }


@router.get("/api/teaching-engine/sessions")
async def teaching_engine_sessions_api(
    topic: str | None = None,
    mode: str | None = None,
) -> dict[str, Any]:
    sessions = list_teaching_sessions(topic=topic, mode=mode)

    return {
        "status": "ok",
        "count": len(sessions),
        "sessions": sessions,
    }


@router.get("/api/teaching-engine/sessions/{session_id}")
async def teaching_engine_session_get_api(session_id: str) -> dict[str, Any]:
    session = get_teaching_session(session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="teaching session not found")

    return {
        "status": "ok",
        "session": session,
    }


@router.get("/command/teaching-engine", response_class=HTMLResponse)
async def teaching_engine_page() -> HTMLResponse:
    return HTMLResponse("""
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Teaching Engine</title>
      </head>
      <body>
        <h1>Project Salus — Teaching Engine v1.0</h1>
        <p>Mission: teach Kyle in a way that increases capability and reduces dependence on AI.</p>

        <a href="/command/kernel">Kernel</a>
        <a href="/command/core-identity">Core Identity</a>
        <a href="/command/knowledge">Knowledge</a>
        <a href="/command/memory">Memory</a>
        <a href="/command/judgment">Judgment</a>

        <h2>Create Teaching Session</h2>
        <input id="topic" value="cybersecurity risk management">
        <select id="level">
          <option>beginner</option>
          <option>intermediate</option>
          <option>advanced</option>
        </select>
        <select id="mode">
          <option>explain</option>
          <option>guided_practice</option>
          <option>quiz</option>
          <option>review</option>
          <option>mission_training</option>
        </select>
        <textarea id="goal">Understand and apply the topic to real decisions.</textarea>
        <button onclick="createSession()">Create Session</button>

        <h2>Status</h2>
        <pre id="status">Loading...</pre>

        <h2>Session Output</h2>
        <pre id="output">Waiting...</pre>

        <script>
          function pretty(data) { return JSON.stringify(data, null, 2); }

          async function loadStatus() {
            const response = await fetch("/api/teaching-engine/status");
            const data = await response.json();
            document.getElementById("status").textContent = pretty(data);
          }

          async function createSession() {
            const payload = {
              user: "Kyle",
              topic: document.getElementById("topic").value,
              level: document.getElementById("level").value,
              mode: document.getElementById("mode").value,
              goal: document.getElementById("goal").value
            };

            const response = await fetch("/api/teaching-engine/session", {
              method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify(payload)
            });

            const data = await response.json();
            document.getElementById("output").textContent = pretty(data);
            loadStatus();
          }

          loadStatus();
        </script>
      </body>
    </html>
    """)
